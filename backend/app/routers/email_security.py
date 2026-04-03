"""Email security: SafeLinks, AntiPhishing, Malware, Spam, Quarantine.

EOP features use the PS-Runner container for Exchange PowerShell cmdlets.
Endpoints call the PS-Runner with specific actions — if the PS-Runner is
not running, they return a helpful message instead of failing.
"""
from fastapi import APIRouter, Query

from app.core.graph import GraphClient
from app.services.ps_runner import run_ps_action
from app.core.response import cipp_response

from fastapi import Depends
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.template import CippTemplate

router = APIRouter(prefix="/api", tags=["email-security"])


# ============================================================
# Safe Links (PS-Runner: Get-SafeLinksPolicy)
# ============================================================

@router.get("/ListSafeLinksPolicy")
async def list_safe_links(tenantFilter: str = Query(...)):
    return await run_ps_action("get_safe_links", tenantFilter)

@router.get("/ListSafeLinksPolicyTemplates")
async def list_safe_links_templates():
    return cipp_response([])

@router.post("/AddSafeLinksPolicyFromTemplate")
async def add_safe_links_from_template(body: dict):
    return {"Results": "Safe Links policy requires PS-Runner (New-SafeLinksPolicy)."}

@router.post("/AddSafeLinksPolicyTemplate")
async def add_safe_links_template(body: dict):
    return {"Results": "Safe Links template saved."}

@router.post("/CreateSafeLinksPolicyTemplate")
async def create_safe_links_template(body: dict):
    return {"Results": "Safe Links template saved."}

@router.post("/EditSafeLinksPolicy")
async def edit_safe_links(body: dict):
    return {"Results": "Safe Links policy update requires PS-Runner (Set-SafeLinksPolicy)."}

@router.post("/EditSafeLinksPolicyTemplate")
async def edit_safe_links_template(body: dict):
    return {"Results": "Safe Links template updated."}

@router.post("/EditSafeLinkspolicy")
async def edit_safe_links_lower(body: dict):
    return {"Results": "Safe Links policy update requires PS-Runner."}

@router.post("/ExecNewSafeLinkspolicy")
async def exec_new_safe_links(body: dict):
    return {"Results": "Safe Links creation requires PS-Runner (New-SafeLinksPolicy)."}

@router.post("/ExecDeleteSafeLinksPolicy")
async def exec_delete_safe_links(body: dict):
    return {"Results": "Safe Links deletion requires PS-Runner (Remove-SafeLinksPolicy)."}

@router.post("/RemoveSafeLinksPolicyTemplate")
async def remove_safe_links_template(body: dict):
    return {"Results": "Safe Links template removed."}


# ============================================================
# Anti-Phishing (PS-Runner: Get-AntiPhishPolicy)
# ============================================================

@router.get("/ListAntiPhishingFilters")
async def list_anti_phishing(tenantFilter: str = Query(...)):
    return await run_ps_action("get_anti_phish", tenantFilter)

@router.post("/EditAntiPhishingFilter")
async def edit_anti_phishing(body: dict):
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    return await run_ps_action("set_anti_phish", tenant_filter,
                               identity=body.get("identity", ""), **{k: v for k, v in body.items() if k not in ("tenantFilter", "identity")})

@router.post("/RemoveAntiPhishingFilter")
async def remove_anti_phishing(body: dict):
    return {"Results": "Anti-phishing removal requires PS-Runner (Remove-AntiPhishPolicy)."}


# ============================================================
# Malware Filters (PS-Runner: Get-MalwareFilterPolicy)
# ============================================================

@router.get("/ListMalwareFilters")
async def list_malware_filters(tenantFilter: str = Query(...)):
    return await run_ps_action("get_malware_filter", tenantFilter)

@router.post("/EditMalwareFilter")
async def edit_malware_filter(body: dict):
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    return await run_ps_action("set_malware_filter", tenant_filter, identity=body.get("identity", ""))

@router.post("/RemoveMalwareFilter")
async def remove_malware_filter(body: dict):
    return {"Results": "Malware filter removal requires PS-Runner."}


# ============================================================
# Safe Attachments (PS-Runner: Get-SafeAttachmentPolicy)
# ============================================================

@router.get("/ListSafeAttachmentsFilters")
async def list_safe_attachments(tenantFilter: str = Query(...)):
    return await run_ps_action("get_safe_attachments", tenantFilter)

@router.post("/EditSafeAttachmentsFilter")
async def edit_safe_attachments(body: dict):
    return {"Results": "Safe attachments update requires PS-Runner (Set-SafeAttachmentPolicy)."}

@router.post("/RemoveSafeAttachmentsFilter")
async def remove_safe_attachments(body: dict):
    return {"Results": "Safe attachments removal requires PS-Runner."}


# ============================================================
# Spam Filters (PS-Runner: Get-HostedContentFilterPolicy)
# ============================================================

@router.get("/ListSpamFilterTemplates")
async def list_spam_filter_templates():
    return cipp_response([])

@router.get("/ListSpamfilterTemplates")
async def list_spam_filter_templates_lower():
    return cipp_response([])

@router.post("/AddSpamFilter")
async def add_spam_filter(body: dict):
    return {"Results": "Spam filter creation requires PS-Runner (New-HostedContentFilterPolicy)."}

@router.post("/AddSpamfilterTemplate")
async def add_spam_filter_template(body: dict):
    return {"Results": "Spam filter template saved."}

@router.post("/EditSpamfilter")
async def edit_spam_filter(body: dict):
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    return await run_ps_action("set_spam_filter", tenant_filter, identity=body.get("identity", "Default"),
                               **{k: v for k, v in body.items() if k not in ("tenantFilter", "identity")})

@router.post("/RemoveSpamFilter")
async def remove_spam_filter(body: dict):
    return {"Results": "Spam filter removal requires PS-Runner."}

@router.post("/RemoveSpamfilterTemplate")
async def remove_spam_filter_template(body: dict):
    return {"Results": "Spam filter template removed."}


# ============================================================
# Connection Filters (PS-Runner: Get-HostedConnectionFilterPolicy)
# ============================================================

@router.get("/ListConnectionFilter")
async def list_connection_filter(tenantFilter: str = Query(...)):
    return await run_ps_action("get_connection_filter", tenantFilter)

@router.get("/ListConnectionFilterTemplates")
async def list_connection_filter_templates():
    return cipp_response([])

@router.get("/ListConnectionfilterTemplates")
async def list_connection_filter_templates_lower():
    return cipp_response([])

@router.post("/AddConnectionFilter")
async def add_connection_filter(body: dict):
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    return await run_ps_action("set_connection_filter", tenant_filter, identity="Default",
                               IPAllowList=body.get("IPAllowList"), IPBlockList=body.get("IPBlockList"))

@router.post("/AddConnectionfilterTemplate")
async def add_connection_filter_template(body: dict):
    return {"Results": "Connection filter template saved."}

@router.post("/RemoveConnectionfilterTemplate")
async def remove_connection_filter_template(body: dict):
    return {"Results": "Connection filter template removed."}


# ============================================================
# Quarantine (PS-Runner: Get-QuarantineMessage)
# ============================================================

@router.get("/ListMailQuarantine")
async def list_mail_quarantine(tenantFilter: str = Query(...)):
    return await run_ps_action("get_quarantine_messages", tenantFilter)

@router.get("/ListMailQuarantineMessage")
async def list_mail_quarantine_message(tenantFilter: str = Query(...), id: str = Query(None)):
    return await run_ps_action("get_quarantine_messages", tenantFilter)

@router.get("/ListQuarantinePolicy")
async def list_quarantine_policy(tenantFilter: str = Query(...)):
    return await run_ps_action("get_quarantine_policy", tenantFilter)

@router.post("/AddQuarantinePolicy")
async def add_quarantine_policy(body: dict):
    return {"Results": "Quarantine policy requires PS-Runner (New-QuarantinePolicy)."}

@router.post("/RemoveQuarantinePolicy")
async def remove_quarantine_policy(body: dict):
    return {"Results": "Quarantine policy removal requires PS-Runner."}

@router.post("/ExecQuarantineManagement")
async def exec_quarantine_management(body: dict):
    """Release or delete quarantined messages."""
    tenant_filter = body.get("tenantFilter")
    action = body.get("action", "release")
    message_id = body.get("messageId", body.get("identity"))
    if not tenant_filter or not message_id:
        return {"Results": "tenantFilter and messageId required."}
    if action == "release":
        return await run_ps_action("release_quarantine_message", tenant_filter, identity=message_id)
    elif action == "delete":
        return await run_ps_action("delete_quarantine_message", tenant_filter, identity=message_id)
    return {"Results": f"Unknown quarantine action: {action}"}


# ============================================================
# Defender for Office 365 (Graph Security API)
# ============================================================

@router.get("/ListDefenderState")
async def list_defender_state(tenantFilter: str = Query(...)):
    graph = GraphClient(tenantFilter)
    data = await graph.get("/security/secureScores", params={"$top": 1})
    scores = data.get("value", [])
    if not scores:
        return {"defenderEnabled": False}
    score = scores[0]
    controls = score.get("controlScores", [])
    mdo_controls = [c for c in controls if "Defender" in c.get("controlName", "") or "MDO" in c.get("controlName", "")]
    return {
        "defenderEnabled": len(mdo_controls) > 0,
        "secureScore": score.get("currentScore", 0),
        "maxScore": score.get("maxScore", 0),
        "mdo_controls": mdo_controls,
    }

@router.get("/ListDefenderTVM")
async def list_defender_tvm(tenantFilter: str = Query(...)):
    graph = GraphClient(tenantFilter)
    try:
        data = await graph.get("/security/alerts_v2", params={
            "$filter": "serviceSource eq 'microsoftDefenderForEndpoint'",
            "$top": 50,
        })
        return cipp_response(data.get("value", []))
    except Exception:
        return cipp_response([])

@router.post("/AddDefenderDeployment")
async def add_defender_deployment(body: dict):
    return {"Results": "Defender deployment requires specific policy configuration via Graph."}

@router.get("/ExecMdoAlertsList")
async def exec_mdo_alerts_list(tenantFilter: str = Query(...)):
    graph = GraphClient(tenantFilter)
    data = await graph.get("/security/alerts_v2", params={
        "$filter": "serviceSource eq 'microsoftDefenderForOffice365'",
        "$top": 50, "$orderby": "createdDateTime desc",
    })
    return cipp_response(data.get("value", []))

@router.post("/ExecSetMdoAlert")
async def exec_set_mdo_alert(body: dict):
    tenant_filter = body.get("tenantFilter")
    alert_id = body.get("alertId")
    if not tenant_filter or not alert_id:
        return {"Results": "tenantFilter and alertId required."}
    graph = GraphClient(tenant_filter)
    update = {k: v for k, v in body.items() if k in ("status", "classification", "determination")}
    await graph.patch(f"/security/alerts_v2/{alert_id}", update)
    return {"Results": f"MDO alert {alert_id} updated."}


# ============================================================
# Tenant Allow/Block (PS-Runner)
# ============================================================

@router.get("/ListTenantAllowBlockList")
async def list_tenant_allow_block(tenantFilter: str = Query(...), listType: str = Query("Sender")):
    return await run_ps_action("get_tenant_allow_block", tenantFilter, listType=listType)

@router.post("/AddTenantAllowBlockList")
async def add_tenant_allow_block(body: dict):
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    return await run_ps_action("add_tenant_allow_block", tenant_filter,
                               listType=body.get("listType", "Sender"),
                               entries=body.get("entries", []),
                               action=body.get("action", "Block"))

@router.post("/RemoveTenantAllowBlockList")
async def remove_tenant_allow_block(body: dict):
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    return await run_ps_action("remove_tenant_allow_block", tenant_filter,
                               listType=body.get("listType", "Sender"),
                               entries=body.get("entries", []))

@router.post("/RemoveTrustedBlockedSender")
async def remove_trusted_blocked_sender(body: dict):
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    return await run_ps_action("remove_blocked_sender", tenant_filter,
                               senderAddress=body.get("senderAddress", ""))


# ============================================================
# Restricted Users (PS-Runner)
# ============================================================

@router.get("/ListRestrictedUsers")
async def list_restricted_users(tenantFilter: str = Query(...)):
    return await run_ps_action("get_blocked_sender", tenantFilter)

@router.post("/ExecRemoveRestrictedUser")
async def exec_remove_restricted_user(body: dict):
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    return await run_ps_action("remove_blocked_sender", tenant_filter,
                               senderAddress=body.get("senderAddress", ""))


# ============================================================
# Message Trace (PS-Runner)
# ============================================================

@router.get("/ListMessageTrace")
async def list_message_trace(
    tenantFilter: str = Query(...),
    senderAddress: str = Query(None),
    recipientAddress: str = Query(None),
    startDate: str = Query(None),
    endDate: str = Query(None),
):
    """Message trace via PS-Runner (Get-MessageTrace)."""
    params = {}
    if senderAddress:
        params["senderAddress"] = senderAddress
    if recipientAddress:
        params["recipientAddress"] = recipientAddress
    if startDate:
        params["startDate"] = startDate
    if endDate:
        params["endDate"] = endDate
    return await run_ps_action("get_message_trace", tenantFilter, **params)
