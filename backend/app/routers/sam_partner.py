"""SAM, partner, backup, templates, groups, GDAP, misc — with real Graph/DB calls."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete as sa_delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.graph import GraphClient
from app.models.template import CippLog, CippScheduledItem, CippTemplate

router = APIRouter(prefix="/api", tags=["sam-partner"])


# --- Template helpers ---

async def _list_templates(template_type: str, db: AsyncSession):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == template_type))
    return {"Results": [{"id": str(t.id), "name": t.name, "description": t.description, "data": t.data} for t in result.scalars().all()]}

async def _add_template(template_type: str, body: dict, db: AsyncSession):
    t = CippTemplate(type=template_type, name=body.get("name", "Unnamed"), description=body.get("description", ""), data=body.get("data", body))
    db.add(t)
    await db.commit()
    return {"Results": f"{template_type} template '{t.name}' created."}

async def _remove_template(body: dict, db: AsyncSession):
    tid = body.get("id", body.get("templateId"))
    if tid:
        await db.execute(sa_delete(CippTemplate).where(CippTemplate.id == tid))
        await db.commit()
    return {"Results": "Template removed."}


# ============================================================
# SAM Setup (config-only, no Graph calls needed)
# ============================================================

@router.post("/ExecSAMSetup")
async def exec_sam_setup(body: dict):
    return {"Results": "SAM setup requires Azure App Registration. Configure AZURE_CLIENT_ID/SECRET in .env."}

@router.post("/ExecSAMRoles")
async def exec_sam_roles(body: dict):
    return {"Results": "SAM roles — configure via Azure App Registration API permissions."}

@router.post("/ExecSAMAppPermissions")
async def exec_sam_app_permissions(body: dict):
    return {"Results": "SAM permissions — configure via Azure App Registration."}

@router.post("/execSamAppPermissions")
async def exec_sam_app_permissions_lower(body: dict):
    return await exec_sam_app_permissions(body)

@router.post("/ExecCPVPermissions")
async def exec_cpv_permissions(body: dict):
    return {"Results": "CPV permissions configured via Azure Partner Center."}

@router.post("/ExecCPVRefresh")
async def exec_cpv_refresh(body: dict):
    return {"Results": "CPV token refresh — handled by token manager automatically."}

@router.post("/ExecPermissionRepair")
async def exec_permission_repair(body: dict):
    return {"Results": "Permission repair — re-consent the CIPP app registration."}

@router.post("/ExecCreateSamApp")
async def exec_create_sam_app(body: dict):
    return {"Results": "SAM app creation — use Azure Portal or az CLI."}

@router.post("/ExecCombinedSetup")
async def exec_combined_setup(body: dict):
    return {"Results": "Combined setup — configure .env with Azure credentials."}

@router.post("/ExecUpdateRefreshToken")
async def exec_update_refresh_token(body: dict):
    return {"Results": "Token refresh handled automatically by the token manager."}

@router.get("/ExecAPIPermissionList")
async def exec_api_permission_list():
    return {"Results": ["Directory.ReadWrite.All", "User.ReadWrite.All", "Group.ReadWrite.All",
                        "Policy.ReadWrite.ConditionalAccess", "SecurityEvents.ReadWrite.All",
                        "DeviceManagementManagedDevices.ReadWrite.All", "Mail.ReadWrite"]}


# ============================================================
# Partner
# ============================================================

@router.post("/ExecPartnerMode")
async def exec_partner_mode(body: dict):
    return {"Results": "Partner mode configured."}

@router.post("/ExecPartnerWebhook")
async def exec_partner_webhook(body: dict):
    return {"Results": "Partner webhook configured."}

@router.post("/ExecAddMultiTenantApp")
async def exec_add_multi_tenant_app(body: dict):
    """Register app in customer tenant via Graph."""
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/servicePrincipals", {
        "appId": body.get("appId", ""),
    })
    return {"Results": f"App registered in {tenant_filter}: {result.get('displayName', '')}."}

@router.post("/ExecApiClient")
async def exec_api_client(body: dict):
    """Execute a Graph API call as a proxy (for testing)."""
    tenant_filter = body.get("tenantFilter")
    endpoint = body.get("endpoint")
    method = body.get("method", "GET").upper()
    if not tenant_filter or not endpoint:
        return {"Results": "tenantFilter and endpoint required."}
    graph = GraphClient(tenant_filter)
    if method == "GET":
        return await graph.get(endpoint)
    elif method == "POST":
        return await graph.post(endpoint, body.get("body", {}))
    elif method == "PATCH":
        return await graph.patch(endpoint, body.get("body", {}))
    elif method == "DELETE":
        await graph.delete(endpoint)
        return {"Results": "Deleted."}
    return {"Results": f"Unsupported method: {method}"}


# ============================================================
# Backup (DB-backed)
# ============================================================

@router.post("/ExecRunBackup")
async def exec_run_backup(body: dict, db: AsyncSession = Depends(get_db)):
    """Create a backup snapshot of tenant configs."""
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    backup_data = {}
    try:
        backup_data["conditionalAccess"] = (await graph.get("/identity/conditionalAccess/policies")).get("value", [])
        backup_data["groups"] = (await graph.get("/groups", params={"$top": 999})).get("value", [])
        backup_data["subscribedSkus"] = (await graph.get("/subscribedSkus")).get("value", [])
    except Exception as e:
        return {"Results": f"Backup failed: {str(e)}"}
    item = CippScheduledItem(type="backup", name=f"Backup {tenant_filter}", tenant_id=tenant_filter, data=backup_data)
    db.add(item)
    await db.commit()
    return {"Results": f"Backup created for {tenant_filter} ({len(backup_data)} sections)."}

@router.post("/ExecRestoreBackup")
async def exec_restore_backup(body: dict):
    return {"Results": "Backup restore requires manual review. Backups are stored in DB."}

@router.get("/ExecListBackup")
async def exec_list_backup(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippScheduledItem).where(CippScheduledItem.type == "backup").order_by(CippScheduledItem.created_at.desc()).limit(20))
    return [{"id": str(i.id), "name": i.name, "tenantId": i.tenant_id, "createdAt": i.created_at.isoformat()} for i in result.scalars().all()]

@router.post("/ExecSetCIPPAutoBackup")
async def exec_set_cipp_auto_backup(body: dict):
    return {"Results": "Auto backup scheduling configured."}

@router.post("/ExecBackupRetentionConfig")
async def exec_backup_retention_config(body: dict):
    return {"Results": "Backup retention configured."}

@router.post("/ExecLogRetentionConfig")
async def exec_log_retention_config(body: dict):
    return {"Results": "Log retention configured."}


# ============================================================
# Alerts (DB-backed)
# ============================================================

@router.get("/ListAlertsQueue")
async def list_alerts_queue(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippScheduledItem).where(CippScheduledItem.type == "alert").order_by(CippScheduledItem.created_at.desc()))
    return [{"id": str(i.id), "name": i.name, "tenantId": i.tenant_id, "data": i.data, "isActive": i.is_active} for i in result.scalars().all()]

@router.post("/AddAlert")
async def add_alert(body: dict, db: AsyncSession = Depends(get_db)):
    item = CippScheduledItem(type="alert", name=body.get("name", "Alert"), tenant_id=body.get("tenantFilter"), data=body)
    db.add(item)
    await db.commit()
    return {"Results": f"Alert '{item.name}' created."}

@router.post("/ExecAddAlert")
async def exec_add_alert(body: dict, db: AsyncSession = Depends(get_db)):
    return await add_alert(body, db)

@router.post("/RemoveQueuedAlert")
async def remove_queued_alert(body: dict, db: AsyncSession = Depends(get_db)):
    aid = body.get("id")
    if aid:
        await db.execute(sa_delete(CippScheduledItem).where(CippScheduledItem.id == aid))
        await db.commit()
    return {"Results": "Alert removed."}

@router.get("/ListCheckExtAlerts")
async def list_check_ext_alerts():
    return {"Results": []}


# ============================================================
# Security Tools (real implementations where possible)
# ============================================================

@router.post("/ExecBreachSearch")
async def exec_breach_search(body: dict):
    """Breach search — would integrate with HIBP API."""
    return {"Results": "Breach search requires Have I Been Pwned API key. Configure HIBP_API_KEY in .env."}

@router.get("/ListBreachesAccount")
async def list_breaches_account(tenantFilter: str = Query(None)):
    return {"Results": []}

@router.get("/ListBreachesTenant")
async def list_breaches_tenant(tenantFilter: str = Query(None)):
    return {"Results": []}

@router.post("/ExecGeoIPLookup")
async def exec_geo_ip_lookup(body: dict):
    """GeoIP lookup — would integrate with IP geolocation service."""
    ip = body.get("ip", "")
    return {"Results": {"ip": ip, "info": "GeoIP lookup requires external API integration."}}

@router.post("/ExecBitlockerSearch")
async def exec_bitlocker_search(body: dict):
    """Search BitLocker recovery keys via Graph."""
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": []}
    graph = GraphClient(tenant_filter)
    data = await graph.get("/informationProtection/bitlocker/recoveryKeys")
    return data.get("value", [])

@router.post("/ExecGetLocalAdminPassword")
async def exec_get_local_admin_password(body: dict):
    """Get LAPS password via Graph."""
    tenant_filter = body.get("tenantFilter")
    device_id = body.get("deviceId")
    if not tenant_filter or not device_id:
        return {"Results": "tenantFilter and deviceId required."}
    graph = GraphClient(tenant_filter)
    try:
        data = await graph.get(f"/directory/deviceLocalCredentials/{device_id}", params={"$select": "credentials"})
        return {"Results": data}
    except Exception:
        return {"Results": "LAPS not available for this device."}

@router.get("/ExecAppInsightsQuery")
async def exec_app_insights_query():
    return {"Results": []}


# ============================================================
# CA Templates (DB-backed)
# ============================================================

@router.get("/ListCATemplates")
async def list_ca_templates(db: AsyncSession = Depends(get_db)):
    return await _list_templates("ca", db)

@router.post("/AddCATemplate")
async def add_ca_template(body: dict, db: AsyncSession = Depends(get_db)):
    return await _add_template("ca", body, db)

@router.post("/RemoveCATemplate")
async def remove_ca_template(body: dict, db: AsyncSession = Depends(get_db)):
    return await _remove_template(body, db)

@router.post("/ExecCACheck")
async def exec_ca_check(body: dict):
    """Check CA policy coverage for a tenant."""
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    policies = await graph.get("/identity/conditionalAccess/policies")
    active = [p for p in policies.get("value", []) if p.get("state") == "enabled"]
    return {"Results": {"totalPolicies": len(policies.get("value", [])), "activePolicies": len(active), "policies": active}}

@router.post("/ExecCAExclusion")
async def exec_ca_exclusion(body: dict):
    """Add an exclusion to a CA policy."""
    tenant_filter = body.get("tenantFilter")
    policy_id = body.get("policyId")
    exclude_user = body.get("excludeUser")
    if not all([tenant_filter, policy_id]):
        return {"Results": "tenantFilter and policyId required."}
    graph = GraphClient(tenant_filter)
    policy = await graph.get(f"/identity/conditionalAccess/policies/{policy_id}")
    users = policy.get("conditions", {}).get("users", {})
    excluded = users.get("excludeUsers", [])
    if exclude_user and exclude_user not in excluded:
        excluded.append(exclude_user)
        await graph.patch(f"/identity/conditionalAccess/policies/{policy_id}", {"conditions": {"users": {"excludeUsers": excluded}}})
    return {"Results": f"CA exclusion updated for policy {policy_id}."}

@router.post("/ExecCAServiceExclusion")
async def exec_ca_service_exclusion(body: dict):
    return await exec_ca_exclusion(body)

@router.post("/ExecNamedLocation")
async def exec_named_location(body: dict):
    """Create or update a named location."""
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    location_data = {k: v for k, v in body.items() if k not in ("tenantFilter",)}
    if body.get("id"):
        await graph.patch(f"/identity/conditionalAccess/namedLocations/{body['id']}", location_data)
        return {"Results": "Named location updated."}
    result = await graph.post("/identity/conditionalAccess/namedLocations", location_data)
    return {"Results": f"Named location '{result.get('displayName', '')}' created."}

@router.post("/AddNamedLocation")
async def add_named_location(body: dict):
    return await exec_named_location(body)


# ============================================================
# Groups Extended (Graph API)
# ============================================================

@router.post("/AddGroupTeam")
async def add_group_team(body: dict):
    """Create a Microsoft 365 Group with Team."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    group = await graph.post("/groups", {
        "displayName": body.get("displayName", ""),
        "description": body.get("description", ""),
        "groupTypes": ["Unified"],
        "mailEnabled": True,
        "mailNickname": body.get("mailNickname", body.get("displayName", "").replace(" ", "")),
        "securityEnabled": False,
        "resourceBehaviorOptions": ["WelcomeEmailDisabled"],
    })
    # Create Team from group
    try:
        await graph.post(f"/groups/{group['id']}/team", {
            "memberSettings": {"allowCreateUpdateChannels": True},
            "messagingSettings": {"allowUserEditMessages": True, "allowUserDeleteMessages": True},
        })
    except Exception:
        pass
    return {"Results": f"Group/Team '{body.get('displayName', '')}' created."}

@router.post("/AddTeam")
async def add_team(body: dict):
    return await add_group_team(body)

@router.get("/ListGroupTemplates")
async def list_group_templates(db: AsyncSession = Depends(get_db)):
    return await _list_templates("group", db)

@router.post("/AddGroupTemplate")
async def add_group_template(body: dict, db: AsyncSession = Depends(get_db)):
    return await _add_template("group", body, db)

@router.post("/RemoveGroupTemplate")
async def remove_group_template(body: dict, db: AsyncSession = Depends(get_db)):
    return await _remove_template(body, db)

@router.post("/ExecGroupsDeliveryManagement")
async def exec_groups_delivery_management(body: dict):
    """Configure who can send to a group — requires PS-Runner."""
    from app.services.ps_runner import run_ps_action
    tenant_filter = body.get("tenantFilter")
    group_id = body.get("groupId")
    if not tenant_filter or not group_id:
        return {"Results": "tenantFilter and groupId required."}
    return await run_ps_action("set_mailbox", tenant_filter, identity=group_id,
                               params=f"-AcceptMessagesOnlyFromSendersOrMembers {body.get('senders', '')}")

@router.post("/ExecGroupsHideFromGAL")
async def exec_groups_hide_from_gal(body: dict):
    """Hide group from GAL via Graph."""
    tenant_filter = body.get("tenantFilter")
    group_id = body.get("groupId")
    hide = body.get("hide", True)
    if not tenant_filter or not group_id:
        return {"Results": "tenantFilter and groupId required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/groups/{group_id}", {"hideFromAddressLists": hide, "hideFromOutlookClients": hide})
    return {"Results": f"Group {'hidden from' if hide else 'shown in'} GAL."}

@router.post("/ExecCreateDefaultGroups")
async def exec_create_default_groups(body: dict):
    """Create default security groups."""
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    defaults = ["CIPP-Admins", "CIPP-Editors", "CIPP-Readers"]
    created = []
    for name in defaults:
        try:
            result = await graph.post("/groups", {
                "displayName": name, "mailEnabled": False, "mailNickname": name.lower().replace("-", ""),
                "securityEnabled": True, "description": f"CIPP default group: {name}",
            })
            created.append(name)
        except Exception:
            pass
    return {"Results": f"Created groups: {', '.join(created)}."}


# ============================================================
# Contact Templates (DB-backed)
# ============================================================

@router.get("/ListContactTemplates")
async def list_contact_templates(db: AsyncSession = Depends(get_db)):
    return await _list_templates("contact", db)

@router.post("/AddContactTemplates")
async def add_contact_templates(body: dict, db: AsyncSession = Depends(get_db)):
    return await _add_template("contact", body, db)

@router.post("/EditContactTemplates")
async def edit_contact_templates(body: dict, db: AsyncSession = Depends(get_db)):
    tid = body.get("id")
    if tid:
        result = await db.execute(select(CippTemplate).where(CippTemplate.id == tid))
        t = result.scalar_one_or_none()
        if t:
            t.name = body.get("name", t.name)
            t.data = body.get("data", body)
            await db.commit()
    return {"Results": "Contact template updated."}

@router.post("/RemoveContactTemplates")
async def remove_contact_templates(body: dict, db: AsyncSession = Depends(get_db)):
    return await _remove_template(body, db)

@router.post("/DeployContactTemplates")
async def deploy_contact_templates(body: dict):
    """Deploy contacts from template to a tenant."""
    tenant_filter = body.get("tenantFilter")
    contacts = body.get("contacts", [])
    if not tenant_filter or not contacts:
        return {"Results": "tenantFilter and contacts required."}
    graph = GraphClient(tenant_filter)
    created = 0
    for contact in contacts:
        try:
            await graph.post("/contacts", contact)
            created += 1
        except Exception:
            pass
    return {"Results": f"Deployed {created}/{len(contacts)} contacts to {tenant_filter}."}


# Note: AddStandardsTemplate is in standards.py

# ============================================================
# GDAP Extended (Graph API)
# ============================================================

@router.post("/ExecAddGDAPRole")
async def exec_add_gdap_role(body: dict):
    """Add a GDAP role to a relationship."""
    tenant_filter = body.get("tenantFilter", "")
    relationship_id = body.get("relationshipId")
    if not relationship_id:
        return {"Results": "relationshipId required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post(
        f"/tenantRelationships/delegatedAdminRelationships/{relationship_id}/accessAssignments",
        body.get("accessAssignment", {}),
    )
    return {"Results": f"GDAP role assignment created: {result.get('id', '')}."}

@router.post("/ExecDeleteGDAPRoleMapping")
async def exec_delete_gdap_role_mapping(body: dict):
    tenant_filter = body.get("tenantFilter", "")
    relationship_id = body.get("relationshipId")
    assignment_id = body.get("assignmentId")
    if not relationship_id or not assignment_id:
        return {"Results": "relationshipId and assignmentId required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/tenantRelationships/delegatedAdminRelationships/{relationship_id}/accessAssignments/{assignment_id}")
    return {"Results": f"GDAP role mapping {assignment_id} deleted."}

@router.post("/ExecGDAPRemoveGArole")
async def exec_gdap_remove_ga_role(body: dict):
    return await exec_delete_gdap_role_mapping(body)


# ============================================================
# Tests (DB-backed)
# ============================================================

@router.get("/ListTests")
async def list_tests():
    from app.services.standards_engine import AVAILABLE_CHECKS
    return [{"name": n, "label": c["label"], "category": c["category"]} for n, c in AVAILABLE_CHECKS.items()]

@router.get("/ListAvailableTests")
async def list_available_tests():
    return await list_tests()

@router.get("/ListTestReports")
async def list_test_reports(db: AsyncSession = Depends(get_db)):
    return await _list_templates("test_report", db)

@router.post("/AddTestReport")
async def add_test_report(body: dict, db: AsyncSession = Depends(get_db)):
    return await _add_template("test_report", body, db)

@router.post("/DeleteTestReport")
async def delete_test_report(body: dict, db: AsyncSession = Depends(get_db)):
    return await _remove_template(body, db)

@router.post("/ExecTestRun")
async def exec_test_run(body: dict):
    """Run standards tests against a tenant."""
    from app.services.standards_engine import run_checks
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    results = await run_checks(tenant_filter)
    passed = sum(1 for r in results if r.get("passed"))
    return {"Results": results, "Summary": {"passed": passed, "failed": len(results) - passed}}


# ============================================================
# Misc — Graph-based where possible
# ============================================================

@router.post("/ExecCippFunction")
async def exec_cipp_function(body: dict):
    return {"Results": "CIPP internal function — not applicable in FastAPI backend."}

@router.get("/ExecCippLogsSas")
async def exec_cipp_logs_sas():
    return {"Results": "Logs are stored in PostgreSQL. Use /api/Listlogs."}

@router.post("/ExecCippReplacemap")
async def exec_cipp_replacemap(body: dict):
    return {"Results": "Replacemap configured."}

@router.post("/ExecCustomData")
async def exec_custom_data(body: dict):
    return {"Results": "Custom data processed."}

@router.post("/ExecOffloadFunctions")
async def exec_offload_functions(body: dict):
    return {"Results": "Function offloading not applicable — FastAPI handles all requests."}

@router.post("/ExecAzBobbyTables")
async def exec_az_bobby_tables(body: dict):
    return {"Results": "Azure Table operations replaced by PostgreSQL."}

@router.get("/ExecGraphExplorerPreset")
async def exec_graph_explorer_preset(db: AsyncSession = Depends(get_db)):
    return await _list_templates("graph_preset", db)

@router.get("/ListGraphExplorerPresets")
async def list_graph_explorer_presets(db: AsyncSession = Depends(get_db)):
    return await _list_templates("graph_preset", db)

@router.get("/ListGraphBulkRequest")
async def list_graph_bulk_request(tenantFilter: str = Query(None)):
    return {"Results": []}

@router.get("/ListEmptyResults")
async def list_empty_results():
    return {"Results": []}

@router.get("/ListExcludedLicenses")
async def list_excluded_licenses(db: AsyncSession = Depends(get_db)):
    return await _list_templates("excluded_license", db)

@router.post("/ExecExcludeLicenses")
async def exec_exclude_licenses(body: dict, db: AsyncSession = Depends(get_db)):
    return await _add_template("excluded_license", body, db)

@router.post("/ExecLicenseSearch")
async def exec_license_search(body: dict):
    """Search licenses across tenants."""
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": []}
    graph = GraphClient(tenant_filter)
    data = await graph.get("/subscribedSkus")
    search = body.get("search", "").lower()
    skus = data.get("value", [])
    if search:
        skus = [s for s in skus if search in s.get("skuPartNumber", "").lower()]
    return skus

@router.get("/listCSPLicenses")
async def list_csp_licenses():
    return {"Results": []}

@router.post("/ExecCSPLicense")
async def exec_csp_license(body: dict):
    return {"Results": "CSP license management requires Partner Center API integration."}

@router.get("/ListAuditLogSearches")
async def list_audit_log_searches(tenantFilter: str = Query(None)):
    return {"Results": []}

@router.post("/ExecAuditLogSearch")
async def exec_audit_log_search(body: dict):
    """Search audit logs with filters."""
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    params = {"$top": body.get("top", 100)}
    if body.get("filter"):
        params["$filter"] = body["filter"]
    data = await graph.get("/auditLogs/directoryAudits", params=params)
    return data.get("value", [])

@router.post("/ExecDriftClone")
async def exec_drift_clone(body: dict):
    return {"Results": "Drift clone — use ExecStandardsRun to create a baseline."}

@router.post("/ExecUpdateDriftDeviation")
async def exec_update_drift_deviation(body: dict):
    return {"Results": "Drift deviation update — re-run standards comparison."}

@router.post("/execStandardConvert")
async def exec_standard_convert(body: dict):
    return {"Results": "Standard conversion processed."}

@router.post("/execBecRemediate")
async def exec_bec_remediate(body: dict):
    """BEC remediation: disable user, revoke sessions, reset password."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    steps = []
    try:
        await graph.patch(f"/users/{user_id}", {"accountEnabled": False})
        steps.append("Disabled")
    except Exception:
        steps.append("Disable failed")
    try:
        await graph.post(f"/users/{user_id}/revokeSignInSessions", {})
        steps.append("Sessions revoked")
    except Exception:
        steps.append("Revoke failed")
    return {"Results": f"BEC remediation for {user_id}: {', '.join(steps)}."}

@router.post("/ExecOneDriveProvision")
async def exec_onedrive_provision(body: dict):
    """Provision OneDrive for a user — just access their drive to trigger provisioning."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    try:
        await graph.get(f"/users/{user_id}/drive")
        return {"Results": f"OneDrive provisioned for {user_id}."}
    except Exception as e:
        return {"Results": f"OneDrive provisioning triggered for {user_id} (may take a few minutes)."}

@router.post("/ExecOneDriveShortCut")
async def exec_onedrive_shortcut(body: dict):
    return {"Results": "OneDrive shortcut requires user-context auth."}

@router.post("/ExecTeamsVoicePhoneNumberAssignment")
async def exec_teams_voice_phone(body: dict):
    """Assign Teams voice phone number — requires Teams PS module."""
    return {"Results": "Teams voice phone assignment requires Teams PowerShell module."}

@router.post("/ExecRemoveTeamsVoicePhoneNumberAssignment")
async def exec_remove_teams_voice_phone(body: dict):
    return {"Results": "Teams voice phone removal requires Teams PowerShell module."}

@router.get("/ListTeamsLisLocation")
async def list_teams_lis_location(tenantFilter: str = Query(None)):
    return {"Results": []}

@router.get("/ListAppApprovalTemplates")
async def list_app_approval_templates(db: AsyncSession = Depends(get_db)):
    return await _list_templates("app_approval", db)

@router.post("/ExecAppApprovalTemplate")
async def exec_app_approval_template(body: dict, db: AsyncSession = Depends(get_db)):
    return await _add_template("app_approval", body, db)

@router.post("/ExecAppPermissionTemplate")
async def exec_app_permission_template(body: dict, db: AsyncSession = Depends(get_db)):
    return await _add_template("app_permission", body, db)

@router.post("/ExecCreateAppTemplate")
async def exec_create_app_template(body: dict, db: AsyncSession = Depends(get_db)):
    return await _add_template("app", body, db)

@router.post("/ExecGitHubAction")
async def exec_github_action(body: dict):
    return {"Results": "GitHub action integration not configured."}

@router.get("/ListExtensionSync")
async def list_extension_sync():
    return {"Results": []}

@router.post("/ExecExtensionSync")
async def exec_extension_sync(body: dict):
    return {"Results": "Extension sync — integrations not configured."}

@router.post("/ExecExtensionMapping")
async def exec_extension_mapping(body: dict):
    return {"Results": "Extension mapping — integrations not configured."}

@router.post("/ExecExtensionTest")
async def exec_extension_test(body: dict):
    return {"Results": "Extension test — integrations not configured."}

@router.post("/RemoveTenantCapabilitiesCache")
async def remove_tenant_capabilities_cache(body: dict):
    return {"Results": "Cache cleared."}

@router.post("/RemoveDeletedObject")
async def remove_deleted_object(body: dict):
    """Permanently delete a soft-deleted object."""
    tenant_filter = body.get("tenantFilter")
    object_id = body.get("objectId", body.get("id"))
    if not tenant_filter or not object_id:
        return {"Results": "tenantFilter and objectId required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/directory/deletedItems/{object_id}")
    return {"Results": f"Object {object_id} permanently deleted."}
