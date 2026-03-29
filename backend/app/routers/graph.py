from fastapi import APIRouter, Query

from app.core.graph import GraphClient

router = APIRouter(prefix="/api", tags=["graph"])


@router.get("/ListGraphRequest")
async def list_graph_request(
    tenantFilter: str = Query(...),
    Endpoint: str = Query(...),
    type: str = Query("GET"),
    NoPagination: bool = Query(False),
):
    """Generic Graph API proxy — used by CIPP for flexible Graph queries.

    This is the catch-all endpoint that CIPP uses for dynamic Graph requests.
    The frontend passes the Graph endpoint path and this proxies it.
    """
    graph = GraphClient(tenantFilter)

    if NoPagination:
        data = await graph.get(Endpoint)
        return data
    else:
        results = await graph.get_all_pages(Endpoint)
        return {"Results": results}


@router.post("/ListGraphRequest")
async def post_graph_request(body: dict):
    """Generic Graph API proxy for POST requests."""
    tenant_filter = body.get("tenantFilter")
    endpoint = body.get("Endpoint", body.get("endpoint"))
    if not tenant_filter or not endpoint:
        return {"Results": "tenantFilter and Endpoint are required."}

    graph = GraphClient(tenant_filter)
    method = body.get("type", "GET").upper()

    if method == "GET":
        params = body.get("params", {})
        data = await graph.get(endpoint, params=params)
        return data
    elif method == "POST":
        request_body = body.get("body", {})
        return await graph.post(endpoint, request_body)
    elif method == "PATCH":
        request_body = body.get("body", {})
        return await graph.patch(endpoint, request_body)
    elif method == "DELETE":
        await graph.delete(endpoint)
        return {"Results": "Deleted successfully."}
    else:
        return {"Results": f"Unsupported method: {method}"}
