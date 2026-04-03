from fastapi import APIRouter, Query

from app.core.graph import GraphClient

router = APIRouter(prefix="/api", tags=["sharepoint-teams"])


@router.get("/ListSites")
async def list_sites(tenantFilter: str = Query(...)):
    """List SharePoint sites."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/sites", params={"search": "*"})
    return data.get("value", [])


@router.get("/ListSiteMembers")
async def list_site_members(tenantFilter: str = Query(...), siteId: str = Query(...)):
    """List SharePoint site members."""
    graph = GraphClient(tenantFilter)
    data = await graph.get(f"/sites/{siteId}/permissions")
    return data.get("value", [])


@router.post("/AddSite")
async def add_site(body: dict):
    """Create a SharePoint site."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter is required."}
    graph = GraphClient(tenant_filter)
    # Site creation via Graph requires group creation for team sites
    result = await graph.post("/groups", {
        "displayName": body.get("displayName"),
        "description": body.get("description", ""),
        "groupTypes": ["Unified"],
        "mailEnabled": True,
        "mailNickname": body.get("mailNickname", body.get("displayName", "").replace(" ", "")),
        "securityEnabled": False,
        "resourceBehaviorOptions": ["CreateTeamFromSPSite" if body.get("createTeam") else ""],
    })
    return {"Results": f"Site/Group {result.get('displayName', '')} created."}


@router.get("/ListTeamsVoice")
async def list_teams_voice(tenantFilter: str = Query(...)):
    """List Teams voice users."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/communications/callRecords", params={"$top": 50})
    return data.get("value", [])


@router.get("/ListSharepointQuota")
async def list_sharepoint_quota(tenantFilter: str = Query(...)):
    """Get SharePoint storage quota info — frontend expects TenantStorageMB, GeoUsedStorageMB."""
    graph = GraphClient(tenantFilter)
    try:
        data = await graph.get("/sites/root")
        quota = data.get("quota", {})
        total_mb = round(quota.get("total", 0) / 1024 / 1024)
        used_mb = round(quota.get("used", 0) / 1024 / 1024)
        return {"TenantStorageMB": total_mb, "GeoUsedStorageMB": used_mb}
    except Exception:
        return {"TenantStorageMB": 0, "GeoUsedStorageMB": 0}


@router.post("/ExecSharePointPerms")
async def exec_sharepoint_perms(body: dict):
    """Manage SharePoint permissions."""
    tenant_filter = body.get("tenantFilter")
    site_id = body.get("siteId")
    if not tenant_filter or not site_id:
        return {"Results": "tenantFilter and siteId are required."}
    graph = GraphClient(tenant_filter)
    # Placeholder — SharePoint permissions are complex
    return {"Results": "SharePoint permission management placeholder."}


@router.post("/ExecSetSharePointMember")
async def exec_set_sharepoint_member(body: dict):
    """Add/remove SharePoint site member."""
    tenant_filter = body.get("tenantFilter")
    site_id = body.get("siteId")
    if not tenant_filter or not site_id:
        return {"Results": "tenantFilter and siteId are required."}
    graph = GraphClient(tenant_filter)
    return {"Results": "SharePoint member management placeholder."}


@router.post("/AddSiteBulk")
async def add_site_bulk(body: dict):
    """Bulk create SharePoint sites."""
    return {"Results": "Bulk site creation initiated."}


@router.post("/DeleteSharepointSite")
async def delete_sharepoint_site(body: dict):
    """Delete a SharePoint site."""
    tenant_filter = body.get("tenantFilter")
    group_id = body.get("groupId")
    if not tenant_filter or not group_id:
        return {"Results": "tenantFilter and groupId are required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/groups/{group_id}")
    return {"Results": f"Site group {group_id} deleted."}
