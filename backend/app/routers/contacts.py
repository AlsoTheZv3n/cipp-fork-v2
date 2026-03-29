from fastapi import APIRouter, Query

from app.core.graph import GraphClient

router = APIRouter(prefix="/api", tags=["contacts"])


@router.get("/ListContacts")
async def list_contacts(tenantFilter: str = Query(...), id: str = Query(None)):
    """List contacts or get a specific contact."""
    graph = GraphClient(tenantFilter)
    if id:
        return await graph.get(f"/contacts/{id}")
    data = await graph.get("/contacts")
    return data.get("value", [])


@router.post("/AddContact")
async def add_contact(body: dict):
    """Create a new contact."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter is required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/contacts", body)
    return {"Results": f"Contact {result.get('displayName', '')} created."}


@router.post("/EditContact")
async def edit_contact(body: dict):
    """Update a contact."""
    tenant_filter = body.pop("tenantFilter", None)
    contact_id = body.pop("contactId", None)
    if not tenant_filter or not contact_id:
        return {"Results": "tenantFilter and contactId are required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/contacts/{contact_id}", body)
    return {"Results": f"Contact {contact_id} updated."}


@router.post("/RemoveContact")
async def remove_contact(body: dict):
    """Delete a contact."""
    tenant_filter = body.get("tenantFilter")
    contact_id = body.get("contactId")
    if not tenant_filter or not contact_id:
        return {"Results": "tenantFilter and contactId are required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/contacts/{contact_id}")
    return {"Results": f"Contact {contact_id} deleted."}


# --- Equipment & Room Mailboxes ---

@router.get("/ListEquipment")
async def list_equipment(tenantFilter: str = Query(...)):
    """List equipment mailboxes (via Graph groups/resources)."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/places/microsoft.graph.room")
    return data.get("value", [])


@router.get("/ListRooms")
async def list_rooms(tenantFilter: str = Query(...)):
    """List room resources."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/places/microsoft.graph.room")
    return data.get("value", [])


@router.get("/ListRoomLists")
async def list_room_lists(tenantFilter: str = Query(...)):
    """List room lists."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/places/microsoft.graph.roomList")
    return data.get("value", [])
