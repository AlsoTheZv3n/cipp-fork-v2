import httpx

from app.core.auth import get_token_for_tenant


class GraphClient:
    """Async client for Microsoft Graph API with batch support."""

    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    async def _headers(self) -> dict[str, str]:
        token = await get_token_for_tenant(self.tenant_id)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def get(self, endpoint: str, params: dict | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}{endpoint}",
                headers=await self._headers(),
                params=params,
            )
            r.raise_for_status()
            return r.json()

    async def post(self, endpoint: str, body: dict) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.BASE_URL}{endpoint}",
                headers=await self._headers(),
                json=body,
            )
            r.raise_for_status()
            return r.json()

    async def patch(self, endpoint: str, body: dict) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.patch(
                f"{self.BASE_URL}{endpoint}",
                headers=await self._headers(),
                json=body,
            )
            r.raise_for_status()
            return r.json()

    async def delete(self, endpoint: str) -> None:
        async with httpx.AsyncClient() as client:
            r = await client.delete(
                f"{self.BASE_URL}{endpoint}",
                headers=await self._headers(),
            )
            r.raise_for_status()

    async def batch(self, requests: list[dict]) -> dict:
        """Graph Batch API — up to 20 requests in a single HTTP call."""
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.BASE_URL}/$batch",
                headers=await self._headers(),
                json={"requests": requests},
            )
            r.raise_for_status()
            return r.json()

    async def get_all_pages(self, endpoint: str, params: dict | None = None) -> list:
        """Auto-paginate through @odata.nextLink responses."""
        results = []
        data = await self.get(endpoint, params)
        results.extend(data.get("value", []))

        while next_link := data.get("@odata.nextLink"):
            async with httpx.AsyncClient() as client:
                r = await client.get(next_link, headers=await self._headers())
                r.raise_for_status()
                data = r.json()
                results.extend(data.get("value", []))

        return results
