import httpx

from app.core.config import settings


def _is_demo_mode() -> bool:
    """Check if demo mode is active (no Azure credentials configured)."""
    return settings.demo_mode or not settings.azure_client_id


class GraphClient:
    """Async client for Microsoft Graph API with batch support.

    In demo mode (DEMO_MODE=true or no AZURE_CLIENT_ID), returns realistic
    fake data instead of making real Graph API calls.
    """

    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.demo = _is_demo_mode()

    async def _headers(self) -> dict[str, str]:
        if self.demo:
            return {"Content-Type": "application/json"}
        from app.core.auth import get_token_for_tenant
        token = await get_token_for_tenant(self.tenant_id)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def get(self, endpoint: str, params: dict | None = None) -> dict:
        if self.demo:
            from app.core.demo_data import get_demo_response
            result = get_demo_response(endpoint, params)
            return result if result is not None else {"value": []}

        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}{endpoint}",
                headers=await self._headers(),
                params=params,
            )
            if r.status_code >= 400:
                return {"value": []}
            return r.json()

    async def get_page(self, endpoint: str, params: dict | None = None) -> tuple[list, str | None]:
        """Get a single page of results. Returns (items, next_link).

        Use this instead of get() when you need pagination support.
        The next_link can be passed to cipp_response() for Metadata.nextLink.
        """
        data = await self.get(endpoint, params)
        items = data.get("value", []) if isinstance(data, dict) else []
        next_link = data.get("@odata.nextLink") if isinstance(data, dict) else None
        return items, next_link

    async def get_next_page(self, next_link_url: str) -> tuple[list, str | None]:
        """Follow a nextLink URL to get the next page of results."""
        if self.demo:
            return [], None

        async with httpx.AsyncClient() as client:
            r = await client.get(next_link_url, headers=await self._headers())
            if r.status_code >= 400:
                return [], None
            data = r.json()
            items = data.get("value", []) if isinstance(data, dict) else []
            next_link = data.get("@odata.nextLink") if isinstance(data, dict) else None
            return items, next_link

    async def post(self, endpoint: str, body: dict) -> dict:
        if self.demo:
            return {"id": "demo-created", "status": "success", **body}

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.BASE_URL}{endpoint}",
                headers=await self._headers(),
                json=body,
            )
            r.raise_for_status()
            return r.json()

    async def patch(self, endpoint: str, body: dict) -> dict:
        if self.demo:
            return {"id": "demo-updated", "status": "success"}

        async with httpx.AsyncClient() as client:
            r = await client.patch(
                f"{self.BASE_URL}{endpoint}",
                headers=await self._headers(),
                json=body,
            )
            r.raise_for_status()
            return r.json()

    async def delete(self, endpoint: str) -> None:
        if self.demo:
            return

        async with httpx.AsyncClient() as client:
            r = await client.delete(
                f"{self.BASE_URL}{endpoint}",
                headers=await self._headers(),
            )
            r.raise_for_status()

    async def batch(self, requests: list[dict]) -> dict:
        """Graph Batch API — up to 20 requests in a single HTTP call."""
        if self.demo:
            from app.core.demo_data import get_demo_response
            responses = []
            for req in requests:
                url = req.get("url", "")
                result = get_demo_response(url)
                responses.append({"id": req.get("id", "0"), "status": 200, "body": result or {"value": []}})
            return {"responses": responses}

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.BASE_URL}/$batch",
                headers=await self._headers(),
                json={"requests": requests},
            )
            r.raise_for_status()
            return r.json()

    async def get_all_pages(self, endpoint: str, params: dict | None = None) -> list:
        """Auto-paginate through @odata.nextLink responses. Returns all items."""
        data = await self.get(endpoint, params)
        results = data.get("value", []) if isinstance(data, dict) else []

        if not self.demo:
            while next_link := data.get("@odata.nextLink"):
                async with httpx.AsyncClient() as client:
                    r = await client.get(next_link, headers=await self._headers())
                    if r.status_code >= 400:
                        break
                    data = r.json()
                    results.extend(data.get("value", []))

        return results
