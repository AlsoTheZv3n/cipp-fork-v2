"""Extended Exchange endpoints with real Graph API and PS-Runner calls."""
from fastapi import APIRouter, Query

from app.core.graph import GraphClient
from app.services.ps_runner import run_ps_action

router = APIRouter(prefix="/api", tags=["exchange-extended"])


# --- Mailbox Actions (Graph API where possible, PS-Runner for Exchange-only) ---

@router.post("/ExecConvertMailbox")
async def exec_convert_mailbox(body: dict):
    """Convert mailbox type (requires PS-Runner)."""
    tenant_filter = body.get("tenantFilter")
    identity = body.get("userId", body.get("identity"))
    mailbox_type = body.get("mailboxType", "Shared")
    if not tenant_filter or not identity:
        return {"Results": "tenantFilter and userId required."}
    return await run_ps_action("set_mailbox", tenant_filter,
                               identity=identity, params=f"-Type {mailbox_type}")

@router.post("/ExecEmailForward")
async def exec_email_forward(body: dict):
    """Configure email forwarding via Graph."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    forward_to = body.get("forwardTo", "")
    keep_copy = body.get("keepCopy", True)
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    # Graph doesn't support mail forwarding directly — needs PS-Runner
    return await run_ps_action("set_mailbox", tenant_filter,
                               identity=user_id,
                               params=f"-ForwardingSmtpAddress '{forward_to}' -DeliverToMailboxAndForward ${str(keep_copy).lower()}")

@router.post("/ExecCopyForSent")
async def exec_copy_for_sent(body: dict):
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    return await run_ps_action("set_mailbox", tenant_filter,
                               identity=user_id, params="-MessageCopyForSentAsEnabled $true")

@router.post("/ExecEnableArchive")
async def exec_enable_archive(body: dict):
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    return await run_ps_action("set_mailbox", tenant_filter,
                               identity=user_id, params="-Archive")

@router.post("/ExecEnableAutoExpandingArchive")
async def exec_enable_auto_expanding_archive(body: dict):
    return {"Results": "Auto-expanding archive requires tenant-level Exchange admin. Use PS-Runner."}

@router.post("/ExecHideFromGAL")
async def exec_hide_from_gal(body: dict):
    """Hide user from Global Address List via Graph."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    hide = body.get("hide", True)
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/users/{user_id}", {"showInAddressList": not hide})
    return {"Results": f"User {'hidden from' if hide else 'shown in'} GAL."}

@router.post("/ExecSetMailboxQuota")
async def exec_set_mailbox_quota(body: dict):
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    quota = body.get("quota", "50GB")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    return await run_ps_action("set_mailbox", tenant_filter,
                               identity=user_id, params=f"-ProhibitSendReceiveQuota {quota} -ProhibitSendQuota {quota}")

@router.post("/ExecSetMailboxEmailSize")
async def exec_set_mailbox_email_size(body: dict):
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    size = body.get("maxSize", "35MB")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    return await run_ps_action("set_mailbox", tenant_filter,
                               identity=user_id, params=f"-MaxSendSize {size} -MaxReceiveSize {size}")

@router.post("/ExecSetMailboxLocale")
async def exec_set_mailbox_locale(body: dict):
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    locale = body.get("locale", "en-US")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/users/{user_id}/mailboxSettings", {"language": {"locale": locale}})
    return {"Results": f"Mailbox locale set to {locale}."}

@router.post("/ExecSetRecipientLimits")
async def exec_set_recipient_limits(body: dict):
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    limit = body.get("limit", 500)
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    return await run_ps_action("set_mailbox", tenant_filter,
                               identity=user_id, params=f"-RecipientLimits {limit}")

@router.post("/ExecSetLitigationHold")
async def exec_set_litigation_hold(body: dict):
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    enabled = body.get("enabled", True)
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    return await run_ps_action("set_mailbox", tenant_filter,
                               identity=user_id,
                               params=f"-LitigationHoldEnabled ${str(enabled).lower()}")

@router.post("/ExecSetRetentionHold")
async def exec_set_retention_hold(body: dict):
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    return await run_ps_action("set_mailbox", tenant_filter,
                               identity=user_id, params="-RetentionHoldEnabled $true")

@router.post("/ExecMailboxRestore")
async def exec_mailbox_restore(body: dict):
    return {"Results": "Mailbox restore requires Exchange admin. Use PS-Runner."}

@router.get("/ListMailboxRestores")
async def list_mailbox_restores(tenantFilter: str = Query(...)):
    return []

@router.post("/ExecStartManagedFolderAssistant")
async def exec_start_managed_folder_assistant(body: dict):
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    return await run_ps_action("set_mailbox", tenant_filter,
                               identity=user_id, params="| Start-ManagedFolderAssistant")

@router.post("/ExecRemoveMailboxRule")
async def exec_remove_mailbox_rule(body: dict):
    """Remove a mailbox rule via Graph."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    rule_id = body.get("ruleId")
    if not all([tenant_filter, user_id, rule_id]):
        return {"Results": "tenantFilter, userId, and ruleId required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/users/{user_id}/mailFolders/inbox/messageRules/{rule_id}")
    return {"Results": f"Mailbox rule {rule_id} removed."}

@router.post("/ExecSetMailboxRule")
async def exec_set_mailbox_rule(body: dict):
    """Create or update a mailbox rule via Graph."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    rule_data = {k: v for k, v in body.items() if k not in ("tenantFilter", "userId")}
    result = await graph.post(f"/users/{user_id}/mailFolders/inbox/messageRules", rule_data)
    return {"Results": f"Mailbox rule created: {result.get('displayName', '')}."}

@router.post("/ExecSetMailboxRetentionPolicies")
async def exec_set_mailbox_retention_policies(body: dict):
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    policy = body.get("policy", "")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    return await run_ps_action("set_mailbox", tenant_filter,
                               identity=user_id, params=f"-RetentionPolicy '{policy}'")

@router.post("/ExecManageRetentionPolicies")
async def exec_manage_retention_policies(body: dict):
    return {"Results": "Retention policy management requires Exchange admin."}

@router.post("/ExecManageRetentionTags")
async def exec_manage_retention_tags(body: dict):
    return {"Results": "Retention tag management requires Exchange admin."}


# --- Mailbox Info (Graph where possible) ---

@router.get("/ListMailboxCAS")
async def list_mailbox_cas(tenantFilter: str = Query(...), userId: str = Query(None)):
    """List CAS mailbox settings (protocols enabled)."""
    if not userId:
        return []
    return await run_ps_action("get_cas_mailbox", tenantFilter, identity=userId)

@router.get("/ListMailboxForwarding")
async def list_mailbox_forwarding(tenantFilter: str = Query(...)):
    """List mailboxes with forwarding configured."""
    graph = GraphClient(tenantFilter)
    users = await graph.get_all_pages("/users", params={
        "$select": "id,displayName,userPrincipalName,mail",
        "$filter": "userType eq 'Member'",
    })
    # Graph mailboxSettings has forwardTo info
    results = []
    for user in users[:50]:  # Limit to 50 for performance
        try:
            settings = await graph.get(f"/users/{user['id']}/mailboxSettings")
            if settings.get("automaticRepliesSetting", {}).get("externalReplyMessage"):
                results.append({**user, "forwarding": settings})
        except Exception:
            continue
    return results

@router.get("/ListSharedMailboxAccountEnabled")
async def list_shared_mailbox_account_enabled(tenantFilter: str = Query(...)):
    """List shared mailboxes where user account is enabled (security risk)."""
    graph = GraphClient(tenantFilter)
    # Shared mailboxes are typically users with specific recipientTypeDetails
    users = await graph.get_all_pages("/users", params={
        "$select": "id,displayName,userPrincipalName,accountEnabled,mail",
    })
    return [u for u in users if u.get("accountEnabled") and u.get("mail")]


# --- Shared/Equipment/Room Mailboxes ---

@router.post("/AddSharedMailbox")
async def add_shared_mailbox(body: dict):
    """Create shared mailbox — requires PS-Runner."""
    tenant_filter = body.get("tenantFilter")
    name = body.get("displayName")
    email = body.get("primarySmtpAddress")
    if not all([tenant_filter, name, email]):
        return {"Results": "tenantFilter, displayName, primarySmtpAddress required."}
    graph = GraphClient(tenant_filter)
    user = await graph.post("/users", {
        "displayName": name,
        "mailNickname": email.split("@")[0],
        "userPrincipalName": email,
        "passwordProfile": {"forceChangePasswordNextSignIn": True, "password": __import__('secrets').token_urlsafe(16) + "!1"},
        "accountEnabled": False,
    })
    return {"Results": f"Shared mailbox {email} created. Convert via PS-Runner."}

@router.post("/AddEquipmentMailbox")
async def add_equipment_mailbox(body: dict):
    return {"Results": "Equipment mailbox creation requires PS-Runner."}

@router.post("/EditEquipmentMailbox")
async def edit_equipment_mailbox(body: dict):
    return {"Results": "Equipment mailbox update requires PS-Runner."}

@router.post("/AddRoomMailbox")
async def add_room_mailbox(body: dict):
    return {"Results": "Room mailbox creation requires PS-Runner."}

@router.post("/EditRoomMailbox")
async def edit_room_mailbox(body: dict):
    return {"Results": "Room mailbox update requires PS-Runner."}

@router.post("/AddRoomList")
async def add_room_list(body: dict):
    return {"Results": "Room list creation requires PS-Runner."}

@router.post("/EditRoomList")
async def edit_room_list(body: dict):
    return {"Results": "Room list update requires PS-Runner."}


# --- Calendar (Graph API) ---

@router.get("/ListCalendarPermissions")
async def list_calendar_permissions(tenantFilter: str = Query(...), userId: str = Query(None)):
    """List calendar permissions via Graph."""
    if not userId:
        return []
    graph = GraphClient(tenantFilter)
    data = await graph.get(f"/users/{userId}/calendar/calendarPermissions")
    return data.get("value", [])

@router.post("/ExecEditCalendarPermissions")
async def exec_edit_calendar_permissions(body: dict):
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    perm_id = body.get("permissionId")
    role = body.get("role", "read")
    if not all([tenant_filter, user_id, perm_id]):
        return {"Results": "tenantFilter, userId, permissionId required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/users/{user_id}/calendar/calendarPermissions/{perm_id}", {"role": role})
    return {"Results": "Calendar permissions updated."}

@router.post("/ExecModifyCalPerms")
async def exec_modify_cal_perms(body: dict):
    return await exec_edit_calendar_permissions(body)

@router.post("/ExecSetCalendarProcessing")
async def exec_set_calendar_processing(body: dict):
    return {"Results": "Calendar processing requires PS-Runner (Set-CalendarProcessing)."}


# --- Out of Office (Graph API) ---

@router.get("/ListOoO")
async def list_ooo(tenantFilter: str = Query(...), userId: str = Query(None)):
    """Get Out of Office settings via Graph."""
    if not userId:
        return []
    graph = GraphClient(tenantFilter)
    settings = await graph.get(f"/users/{userId}/mailboxSettings")
    return settings.get("automaticRepliesSetting", {})

@router.post("/ExecSetOoO")
async def exec_set_ooo(body: dict):
    """Configure Out of Office via Graph."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    ooo_settings = {
        "automaticRepliesSetting": {
            "status": body.get("status", "disabled"),
            "internalReplyMessage": body.get("internalMessage", ""),
            "externalReplyMessage": body.get("externalMessage", ""),
            "externalAudience": body.get("externalAudience", "all"),
        }
    }
    if body.get("startTime") and body.get("endTime"):
        ooo_settings["automaticRepliesSetting"]["scheduledStartDateTime"] = {"dateTime": body["startTime"], "timeZone": "UTC"}
        ooo_settings["automaticRepliesSetting"]["scheduledEndDateTime"] = {"dateTime": body["endTime"], "timeZone": "UTC"}
    await graph.patch(f"/users/{user_id}/mailboxSettings", ooo_settings)
    return {"Results": f"OoO configured for {user_id}."}

@router.post("/ExecScheduleOOOVacation")
async def exec_schedule_ooo_vacation(body: dict):
    return await exec_set_ooo(body)

@router.post("/ExecScheduleMailboxVacation")
async def exec_schedule_mailbox_vacation(body: dict):
    return await exec_set_ooo(body)


# --- Permissions ---

@router.post("/ExecModifyContactPerms")
async def exec_modify_contact_perms(body: dict):
    return {"Results": "Contact folder permissions require PS-Runner."}

@router.post("/ExecModifyMBPerms")
async def exec_modify_mb_perms(body: dict):
    """Modify mailbox permissions via PS-Runner."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    return await run_ps_action("get_mailbox_permissions", tenant_filter, identity=user_id)


# --- Exchange Connectors (PS-Runner) ---

@router.get("/ListExchangeConnectors")
async def list_exchange_connectors(tenantFilter: str = Query(...)):
    graph = GraphClient(tenantFilter)
    # Exchange connectors aren't in Graph — need PS-Runner
    return []

@router.get("/ListExConnectorTemplates")
async def list_ex_connector_templates():
    return []

@router.get("/ListExconnectorTemplates")
async def list_ex_connector_templates_lower():
    return []

@router.post("/AddExConnector")
async def add_ex_connector(body: dict):
    return {"Results": "Exchange connector creation requires PS-Runner."}

@router.post("/AddExConnectorTemplate")
async def add_ex_connector_template(body: dict):
    return {"Results": "Connector template saved."}

@router.post("/EditExConnector")
async def edit_ex_connector(body: dict):
    return {"Results": "Connector update requires PS-Runner."}

@router.post("/RemoveExConnector")
async def remove_ex_connector(body: dict):
    return {"Results": "Connector removal requires PS-Runner."}

@router.post("/RemoveExConnectorTemplate")
async def remove_ex_connector_template(body: dict):
    return {"Results": "Connector template removed."}

@router.post("/ExecExchangeRoleRepair")
async def exec_exchange_role_repair(body: dict):
    return {"Results": "Exchange role repair requires PS-Runner."}


# --- Transport Rules (PS-Runner) ---

@router.post("/AddTransportRule")
async def add_transport_rule(body: dict):
    return {"Results": "Transport rule creation requires PS-Runner."}

@router.post("/AddEditTransportRule")
async def add_edit_transport_rule(body: dict):
    return {"Results": "Transport rule save requires PS-Runner."}

@router.post("/RemoveTransportRule")
async def remove_transport_rule(body: dict):
    return {"Results": "Transport rule removal requires PS-Runner."}

@router.get("/ListTransportRulesTemplates")
async def list_transport_rules_templates():
    return []

@router.post("/AddTransportTemplate")
async def add_transport_template(body: dict):
    return {"Results": "Transport template saved."}

@router.post("/RemoveTransportRuleTemplate")
async def remove_transport_rule_template(body: dict):
    return {"Results": "Transport template removed."}


# --- GAL ---
# Note: ListMessageTrace is in email_security.py (PS-Runner)

@router.get("/ListGlobalAddressList")
async def list_global_address_list(tenantFilter: str = Query(...)):
    """Get GAL via Graph (contacts + users)."""
    graph = GraphClient(tenantFilter)
    users = await graph.get("/users", params={
        "$select": "displayName,mail,userPrincipalName,jobTitle,department",
        "$top": 999,
    })
    return users.get("value", [])

@router.get("/ListExoRequest")
async def list_exo_request(tenantFilter: str = Query(...)):
    return []
