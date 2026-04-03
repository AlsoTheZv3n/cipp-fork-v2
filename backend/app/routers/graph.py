from fastapi import APIRouter, Query, Request

from app.core.graph import GraphClient

router = APIRouter(prefix="/api", tags=["graph"])


@router.get("/ListGraphRequest")
async def list_graph_request(
    request: Request,
    Endpoint: str = Query(...),
    tenantFilter: str = Query(None),
    TenantFilter: str = Query(None),
    NoPagination: bool = Query(False),
    noPagination: bool = Query(False),
):
    """Generic Graph API proxy — the most-used CIPP endpoint (~79 calls in frontend).

    Forwards all extra query params ($select, $filter, $top, $count, etc.) to Graph API.
    Returns {Results: [...]} for paginated, or raw data for NoPagination.
    """
    tenant = tenantFilter or TenantFilter
    if not tenant:
        return {"Results": [], "Metadata": {"error": "tenantFilter is required"}}
    graph = GraphClient(tenant)
    no_page = NoPagination or noPagination

    # Collect Graph query params (everything except our known params)
    our_params = {"tenantFilter", "TenantFilter", "Endpoint", "NoPagination", "noPagination", "type",
                  "ReverseTenantLookup", "manualPagination", "IgnoreErrors", "ListProperties"}
    graph_params = {k: v for k, v in request.query_params.items() if k not in our_params}

    # Ensure endpoint starts with /
    endpoint = Endpoint if Endpoint.startswith("/") else f"/{Endpoint}"

    try:
        if no_page:
            data = await graph.get(endpoint, params=graph_params or None)
            return data
        else:
            if graph_params:
                data = await graph.get(endpoint, params=graph_params)
                results = data.get("value", []) if isinstance(data, dict) else data
                next_link = data.get("@odata.nextLink") if isinstance(data, dict) else None
                resp = {"Results": results}
                if next_link:
                    resp["Metadata"] = {"nextLink": next_link}
                return resp
            else:
                results = await graph.get_all_pages(endpoint)
                return {"Results": results}
    except Exception as e:
        error_msg = str(e)
        # Extract HTTP status from httpx error
        if "403" in error_msg:
            return {"Results": [], "Metadata": {"error": "Insufficient permissions for this Graph API endpoint."}}
        elif "404" in error_msg:
            return {"Results": [], "Metadata": {"error": "Graph API endpoint not found."}}
        else:
            return {"Results": [], "Metadata": {"error": error_msg[:200]}}


@router.post("/ListGraphRequest")
async def post_graph_request(body: dict):
    """Generic Graph API proxy for POST requests."""
    tenant_filter = body.get("tenantFilter")
    endpoint = body.get("Endpoint", body.get("endpoint"))
    if not tenant_filter or not endpoint:
        return {"Results": "tenantFilter and Endpoint are required."}

    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"

    graph = GraphClient(tenant_filter)
    method = body.get("type", "GET").upper()

    try:
        if method == "GET":
            params = body.get("params", {})
            data = await graph.get(endpoint, params=params)
            results = data.get("value", []) if isinstance(data, dict) else data
            return {"Results": results}
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
    except Exception as e:
        return {"Results": [], "Metadata": {"error": str(e)[:200]}}
