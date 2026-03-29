from datetime import datetime, timedelta

import httpx
from sqlalchemy import select, text

from app.core.config import settings
from app.core.database import async_session
from app.models.token_cache import TenantToken


async def get_token_for_tenant(tenant_id: str) -> str:
    """Get a valid Graph API token for a customer tenant via GDAP.

    Checks PostgreSQL cache first, requests a new token if expired.
    """
    async with async_session() as session:
        # 1. Cache check
        result = await session.execute(
            select(TenantToken).where(
                TenantToken.tenant_id == tenant_id,
                TenantToken.expires_at > datetime.utcnow(),
            )
        )
        cached = result.scalar_one_or_none()

        if cached:
            return cached.access_token

        # 2. Request new token via GDAP client credentials
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.azure_client_id,
                    "client_secret": settings.azure_client_secret,
                    "scope": "https://graph.microsoft.com/.default",
                },
            )
            response.raise_for_status()
            token_data = response.json()

        access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)

        # 3. Upsert into PostgreSQL cache
        await session.execute(
            text("""
                INSERT INTO tenant_tokens (tenant_id, access_token, expires_at, updated_at)
                VALUES (:tid, :token, :exp, NOW())
                ON CONFLICT (tenant_id)
                DO UPDATE SET access_token = :token, expires_at = :exp, updated_at = NOW()
            """),
            {"tid": tenant_id, "token": access_token, "exp": expires_at},
        )
        await session.commit()

        return access_token
