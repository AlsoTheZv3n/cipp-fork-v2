from fastapi import APIRouter, Query

from app.core.graph import GraphClient

router = APIRouter(prefix="/api", tags=["licenses"])


@router.get("/ListLicenses")
async def list_licenses(tenantFilter: str = Query(...)):
    """List all subscribed SKUs for a tenant."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/subscribedSkus")
    return data.get("value", [])


@router.get("/ListCSPsku")
async def list_csp_sku(tenantFilter: str = Query(...)):
    """List CSP SKUs (same as subscribed SKUs)."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/subscribedSkus")
    return data.get("value", [])


@router.post("/ExecBulkLicense")
async def bulk_license(body: dict):
    """Assign or remove licenses in bulk."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    add_licenses = body.get("addLicenses", [])
    remove_licenses = body.get("removeLicenses", [])
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId are required."}
    graph = GraphClient(tenant_filter)
    await graph.post(f"/users/{user_id}/assignLicense", {
        "addLicenses": add_licenses,
        "removeLicenses": remove_licenses,
    })
    return {"Results": f"Licenses updated for {user_id}."}
