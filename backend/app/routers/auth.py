"""Auth routes — replaces Azure Static Web Apps /.auth/* endpoints.

Implements MSAL OAuth2 flow for Azure AD login.
"""
from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.session import (
    clear_session_cookie,
    create_session_token,
    get_current_user,
    set_session_cookie,
)
from app.models.user import CippUser

router = APIRouter(tags=["auth"])

AUTHORITY = f"https://login.microsoftonline.com/{settings.auth_tenant_id or settings.azure_tenant_id}"
SCOPES = ["openid", "profile", "email"]


@router.get("/.auth/login/aad")
async def login_aad(post_login_redirect_uri: str = "/"):
    """Redirect to Azure AD login page."""
    tenant_id = settings.auth_tenant_id or settings.azure_tenant_id
    if not tenant_id or not settings.auth_client_id:
        # Dev mode — auto-login without Azure AD
        return RedirectResponse(url=f"/.auth/callback?code=dev-mode&state={post_login_redirect_uri}")

    params = {
        "client_id": settings.auth_client_id,
        "response_type": "code",
        "redirect_uri": settings.auth_redirect_uri,
        "scope": " ".join(SCOPES),
        "state": post_login_redirect_uri,
        "response_mode": "query",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url=f"{AUTHORITY}/oauth2/v2.0/authorize?{query}")


@router.get("/.auth/callback")
async def auth_callback(
    request: Request,
    code: str = "",
    state: str = "/",
    db: AsyncSession = Depends(get_db),
):
    """Handle OAuth2 callback from Azure AD."""
    tenant_id = settings.auth_tenant_id or settings.azure_tenant_id

    if code == "dev-mode" or not tenant_id or not settings.auth_client_id:
        # Dev mode — create local admin session
        user_data = {
            "azure_oid": "dev-local-admin",
            "email": "admin@localhost",
            "display_name": "Local Admin",
            "roles": ["admin", "editor", "readonly"],
            "permissions": ["*"],
        }
    else:
        # Exchange auth code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                f"{AUTHORITY}/oauth2/v2.0/token",
                data={
                    "client_id": settings.auth_client_id,
                    "client_secret": settings.auth_client_secret,
                    "code": code,
                    "redirect_uri": settings.auth_redirect_uri,
                    "grant_type": "authorization_code",
                    "scope": " ".join(SCOPES),
                },
            )
            token_response.raise_for_status()
            token_data = token_response.json()

        # Decode ID token to get user info (without full validation for now)
        import jwt as pyjwt

        id_token = token_data.get("id_token", "")
        claims = pyjwt.decode(id_token, options={"verify_signature": False})

        user_data = {
            "azure_oid": claims.get("oid", claims.get("sub", "")),
            "email": claims.get("preferred_username", claims.get("email", "")),
            "display_name": claims.get("name", ""),
        }

        # Look up or create user in DB
        result = await db.execute(
            select(CippUser).where(CippUser.azure_oid == user_data["azure_oid"])
        )
        db_user = result.scalar_one_or_none()

        if db_user:
            db_user.last_login = datetime.utcnow()
            db_user.email = user_data["email"]
            db_user.display_name = user_data["display_name"]
            user_data["roles"] = db_user.roles or ["readonly"]
            user_data["permissions"] = db_user.permissions or []
        else:
            # First user gets admin, rest get readonly
            existing_count = await db.execute(select(CippUser.id).limit(1))
            is_first_user = existing_count.scalar_one_or_none() is None

            new_user = CippUser(
                azure_oid=user_data["azure_oid"],
                email=user_data["email"],
                display_name=user_data["display_name"],
                roles=["admin", "editor", "readonly"] if is_first_user else ["readonly"],
                permissions=["*"] if is_first_user else [],
                last_login=datetime.utcnow(),
            )
            db.add(new_user)
            user_data["roles"] = new_user.roles
            user_data["permissions"] = new_user.permissions

        await db.commit()

    # Create session and redirect
    token = create_session_token(user_data)
    redirect_url = state if state and state != "/" else settings.frontend_url
    response = RedirectResponse(url=redirect_url)
    set_session_cookie(response, token)
    return response


@router.get("/.auth/me")
async def auth_me(request: Request):
    """Return current user session — replaces Azure SWA /.auth/me."""
    user = get_current_user(request)
    if not user:
        return {"clientPrincipal": None}

    return {
        "clientPrincipal": {
            "identityProvider": "aad",
            "userId": user.get("sub", ""),
            "userDetails": user.get("email", ""),
            "userRoles": user.get("roles", []),
        }
    }


@router.get("/.auth/logout")
async def logout(post_logout_redirect_uri: str = "/"):
    """Clear session and redirect."""
    response = RedirectResponse(url=post_logout_redirect_uri)
    clear_session_cookie(response)
    return response


@router.get("/api/me")
async def api_me(request: Request):
    """CIPP user info endpoint — returns roles and permissions."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"error": "Not authenticated"},
        )

    return {
        "clientPrincipal": {
            "identityProvider": "aad",
            "userId": user.get("sub", ""),
            "userDetails": user.get("email", ""),
            "userRoles": user.get("roles", []),
        },
        "permissions": user.get("permissions", []),
    }
