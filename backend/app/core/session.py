"""Session management using signed JWT cookies.

Replaces Azure Static Web Apps /.auth/* endpoints with our own auth flow.
"""
import uuid
from datetime import datetime, timedelta

import jwt
from fastapi import Request, Response

from app.core.config import settings

COOKIE_NAME = "cipp_session"


def create_session_token(user_data: dict) -> str:
    """Create a signed JWT session token."""
    payload = {
        "sub": user_data["azure_oid"],
        "email": user_data["email"],
        "name": user_data.get("display_name", ""),
        "roles": user_data.get("roles", ["readonly"]),
        "permissions": user_data.get("permissions", []),
        "jti": str(uuid.uuid4()),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=settings.session_expiry_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_session_token(token: str) -> dict | None:
    """Decode and validate a session token. Returns None if invalid."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_current_user(request: Request) -> dict | None:
    """Extract current user from session cookie."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    return decode_session_token(token)


def set_session_cookie(response: Response, token: str) -> None:
    """Set the session cookie on the response."""
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
        max_age=settings.session_expiry_hours * 3600,
    )


def clear_session_cookie(response: Response) -> None:
    """Clear the session cookie."""
    response.delete_cookie(key=COOKIE_NAME)
