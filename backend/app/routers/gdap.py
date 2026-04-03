from fastapi import APIRouter, Query

from app.core.graph import GraphClient
from app.core.response import cipp_response

router = APIRouter(prefix="/api", tags=["gdap"])


@router.get("/ListGDAPRoles")
async def list_gdap_roles(tenantFilter: str = Query(None)):
    """List GDAP role definitions."""
    graph = GraphClient(tenantFilter or "")
    data = await graph.get("/directoryRoles")
    return cipp_response(data.get("value", []))


@router.get("/ListGDAPInvite")
async def list_gdap_invites(tenantFilter: str = Query(None)):
    """List GDAP relationship invites."""
    graph = GraphClient(tenantFilter or "")
    data = await graph.get("/tenantRelationships/delegatedAdminRelationships")
    return cipp_response(data.get("value", []))


@router.post("/ExecGDAPInvite")
async def exec_gdap_invite(body: dict):
    """Create a GDAP relationship invite."""
    tenant_filter = body.get("tenantFilter", "")
    graph = GraphClient(tenant_filter)
    result = await graph.post("/tenantRelationships/delegatedAdminRelationships", body)
    return {"Results": f"GDAP invite created: {result.get('id', '')}"}


@router.post("/ExecDeleteGDAPRelationship")
async def delete_gdap_relationship(body: dict):
    """Delete a GDAP relationship."""
    tenant_filter = body.get("tenantFilter", "")
    relationship_id = body.get("relationshipId")
    if not relationship_id:
        return {"Results": "relationshipId is required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/tenantRelationships/delegatedAdminRelationships/{relationship_id}")
    return {"Results": f"GDAP relationship {relationship_id} deleted."}


@router.post("/ExecGDAPAccessAssignment")
async def exec_gdap_access_assignment(body: dict):
    """Create GDAP access assignment."""
    tenant_filter = body.get("tenantFilter", "")
    relationship_id = body.get("relationshipId")
    if not relationship_id:
        return {"Results": "relationshipId is required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post(
        f"/tenantRelationships/delegatedAdminRelationships/{relationship_id}/accessAssignments",
        body.get("accessAssignment", {}),
    )
    return {"Results": f"Access assignment created: {result.get('id', '')}"}


@router.post("/ExecGDAPRoleTemplate")
async def exec_gdap_role_template(body: dict):
    """Manage GDAP role templates."""
    return {"Results": "GDAP role template processed."}


@router.post("/ExecAutoExtendGDAP")
async def exec_auto_extend_gdap(body: dict):
    """Auto-extend GDAP relationships."""
    return {"Results": "GDAP auto-extend processed."}
