from fastapi import APIRouter, Query

from app.core.graph import GraphClient
from app.services.ps_runner import run_ps_action

router = APIRouter(prefix="/api", tags=["mailbox"])


@router.get("/ListMailboxes")
async def list_mailboxes(tenantFilter: str = Query(...)):
    """List mailboxes via Exchange PS Runner."""
    return await run_ps_action("get_mailbox", tenantFilter, identity="*")


@router.get("/ListMailboxPermissions")
async def list_mailbox_permissions(
    tenantFilter: str = Query(...),
    userId: str = Query(...),
):
    """Get mailbox permissions via PS Runner."""
    return await run_ps_action("get_mailbox_permissions", tenantFilter, identity=userId)


@router.get("/ListMailboxRules")
async def list_mailbox_rules(
    tenantFilter: str = Query(...),
    userId: str = Query(...),
):
    """Get mailbox rules via Graph API."""
    graph = GraphClient(tenantFilter)
    data = await graph.get(f"/users/{userId}/mailFolders/inbox/messageRules")
    return data.get("value", [])


@router.get("/ListTransportRules")
async def list_transport_rules(tenantFilter: str = Query(...)):
    """Get transport rules via PS Runner."""
    return await run_ps_action("get_transport_rules", tenantFilter)


@router.get("/ListSpamfilter")
async def list_spam_filter(tenantFilter: str = Query(...)):
    """Get spam filter policies via PS Runner."""
    return await run_ps_action("get_spam_filter", tenantFilter)
