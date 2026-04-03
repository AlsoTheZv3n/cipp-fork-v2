from fastapi import APIRouter, Query, Request

from app.core.graph import GraphClient
from app.core.response import cipp_response

router = APIRouter(prefix="/api", tags=["graph"])


@router.get("/ListGraphRequest")
async def list_graph_request(
    request: Request,
    Endpoint: str = Query(...),
    tenantFilter: str = Query(None),
    TenantFilter: str = Query(None),
    NoPagination: bool = Query(False),
    noPagination: bool = Query(False),
    nextLink: str = Query(None),
):
    """Generic Graph API proxy with pagination support.

    The most-used CIPP endpoint (~79 calls in frontend).
    Forwards $select, $filter, $top, $count etc. to Graph API.
    Returns {Results: [...], Metadata: {nextLink: "..."}} for paginated responses.
    Frontend uses ApiGetCallWithPagination which passes nextLink for next page.
    """
    tenant = tenantFilter or TenantFilter
    if not tenant:
        return {"Results": [], "Metadata": {"error": "tenantFilter is required"}}
    graph = GraphClient(tenant)
    no_page = NoPagination or noPagination

    # Collect Graph query params (everything except our known params)
    our_params = {"tenantFilter", "TenantFilter", "Endpoint", "NoPagination", "noPagination",
                  "type", "ReverseTenantLookup", "manualPagination", "IgnoreErrors",
                  "ListProperties", "nextLink"}
    graph_params = {k: v for k, v in request.query_params.items() if k not in our_params}

    # Ensure endpoint starts with /
    endpoint = Endpoint if Endpoint.startswith("/") else f"/{Endpoint}"

    try:
        # If nextLink is provided, follow it for the next page
        if nextLink:
            items, next_next_link = await graph.get_next_page(nextLink)
            return cipp_response(items, next_link=next_next_link)

        if no_page:
            data = await graph.get(endpoint, params=graph_params or None)
            return data
        else:
            # Single page with pagination metadata
            items, next_link_url = await graph.get_page(endpoint, params=graph_params or None)
            return cipp_response(items, next_link=next_link_url)
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg:
            return cipp_response([], next_link=None)
        elif "404" in error_msg:
            return cipp_response([], next_link=None)
        else:
            return cipp_response([], next_link=None)


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
            items, next_link = await graph.get_page(endpoint, params=body.get("params"))
            return cipp_response(items, next_link=next_link)
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
        return cipp_response([], next_link=None)
