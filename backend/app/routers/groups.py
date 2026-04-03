from fastapi import APIRouter, Query

from app.core.graph import GraphClient
from app.core.response import cipp_response

router = APIRouter(prefix="/api", tags=["groups"])

GROUP_SELECT = (
    "id,displayName,groupTypes,mailEnabled,securityEnabled,"
    "membershipRule,mail,proxyAddresses,description"
)


@router.get("/ListGroups")
async def list_groups(tenantFilter: str = Query(...), top: int = 999):
    """List all groups in a tenant."""
    graph = GraphClient(tenantFilter)
    items, next_link = await graph.get_page("/groups", params={"$select": GROUP_SELECT, "$top": top})
    return cipp_response(items, next_link=next_link)


@router.post("/AddGroup")
async def add_group(body: dict):
    """Create a new group."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter is required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/groups", body)
    return {"Results": f"Group {result.get('displayName', '')} created successfully."}


@router.post("/EditGroup")
async def edit_group(body: dict):
    """Update group properties."""
    tenant_filter = body.pop("tenantFilter", None)
    group_id = body.pop("groupId", None)
    if not tenant_filter or not group_id:
        return {"Results": "tenantFilter and groupId are required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/groups/{group_id}", body)
    return {"Results": f"Group {group_id} updated."}


@router.post("/ExecGroupsDelete")
async def delete_group(body: dict):
    """Delete a group."""
    tenant_filter = body.get("tenantFilter")
    group_id = body.get("groupId")
    if not tenant_filter or not group_id:
        return {"Results": "tenantFilter and groupId are required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/groups/{group_id}")
    return {"Results": f"Group {group_id} deleted."}
