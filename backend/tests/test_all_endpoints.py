"""Test ALL backend endpoints return non-500 responses.

Run: cd backend && PYTHONPATH=. python -m pytest tests/test_all_endpoints.py -v
Requires: backend running in DEMO_MODE on http://127.0.0.1:8055
"""
import pytest
import httpx

TENANT = "demo-tenant-contoso"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def assert_not_500(response, label=""):
    """Assert the server did not return a 500-class error."""
    assert response.status_code < 500, (
        f"{label} returned {response.status_code}: {response.text[:300]}"
    )


# ===========================================================================
# GET endpoints — no tenant required
# ===========================================================================

GET_NO_TENANT = [
    "/api/health",
    "/api/GetVersion",
    "/api/GetCippAlerts",
    "/api/me",
    "/api/ListTenants",
    "/api/listTenants",
    "/api/ListFeatureFlags",
    "/api/ListCippQueue",
    "/api/ListLogs",
    "/api/Listlogs",
    "/api/ListStandards",
    "/api/ListStandardTemplates",
    "/api/listStandardTemplates",
    "/api/ListBPATemplates",
    "/api/listBPATemplates",
    "/api/ListCATemplates",
    "/api/ListGroupTemplates",
    "/api/ListContactTemplates",
    "/api/ListIntuneTemplates",
    "/api/ListExConnectorTemplates",
    "/api/ListExconnectorTemplates",
    "/api/ListConnectionFilterTemplates",
    "/api/ListConnectionfilterTemplates",
    "/api/ListSpamFilterTemplates",
    "/api/ListSpamfilterTemplates",
    "/api/ListTransportRulesTemplates",
    "/api/ListSafeLinksPolicyTemplates",
    "/api/ListAssignmentFilterTemplates",
    "/api/ListJITAdminTemplates",
    "/api/ListDiagnosticsPresets",
    "/api/ListGraphExplorerPresets",
    "/api/ListCustomRole",
    "/api/ListIPWhitelist",
    "/api/ListExcludedLicenses",
    "/api/ListExtensionsConfig",
    "/api/ListExtensionSync",
    "/api/ListNotificationConfig",
    "/api/ListScheduledItems",
    "/api/ListCommunityRepos",
    "/api/ListGDAPRoles",
    "/api/ListGDAPInvite",
    "/api/ListAppsRepository",
    "/api/ListNewUserDefaults",
    "/api/ListCustomVariables",
    "/api/ListTestReports",
    "/api/ListAvailableTests",
    "/api/ListTenantGroups",
    "/api/ListTenantOnboarding",
    "/api/ListAppApprovalTemplates",
    "/api/ListIntuneReusableSettingTemplates",
    "/api/ListStandardsCompare",
    "/api/ListUserSettings",
    "/api/ListGitHubReleaseNotes",
    "/api/ExecBackendURLs",
    "/api/ExecListAppId",
    "/api/ExecListBackup",
    "/api/ExecGraphExplorerPreset",
    "/api/tenantFilter",
    "/api/ps-runner/actions",
]


@pytest.mark.parametrize("path", GET_NO_TENANT)
def test_get_no_tenant(client, path):
    """GET endpoints that do not require tenantFilter should not return 500."""
    r = client.get(path)
    assert_not_500(r, f"GET {path}")


# ===========================================================================
# GET endpoints — tenant required (via query param tenantFilter)
# ===========================================================================

GET_WITH_TENANT = [
    "/api/ListUsers",
    "/api/listUsers",
    "/api/ListGroups",
    "/api/ListDevices",
    "/api/ListMailboxes",
    "/api/ListContacts",
    "/api/ListDomains",
    "/api/ListOrg",
    "/api/ListLicenses",
    "/api/ListCSPsku",
    "/api/listCSPLicenses",
    "/api/ListRoles",
    "/api/ListApps",
    "/api/ListConditionalAccessPolicies",
    "/api/ListNamedLocations",
    "/api/ListIntunePolicy",
    "/api/ListCompliancePolicies",
    "/api/ListAppProtectionPolicies",
    "/api/ListAssignmentFilters",
    "/api/ListAutopilotConfig",
    "/api/ListAPDevices",
    "/api/ListTeams",
    "/api/ListTeamsActivity",
    "/api/ListTeamsVoice",
    "/api/ListTeamsLisLocation",
    "/api/ListSites",
    "/api/ListSharepointQuota",
    "/api/ListSharePointAdminUrl",
    "/api/ListTransportRules",
    "/api/ListExchangeConnectors",
    "/api/ListConnectionFilter",
    "/api/ListSpamfilter",
    "/api/ListMailQuarantine",
    "/api/ListCalendarPermissions",
    "/api/ListContactPermissions",
    "/api/ListMailboxPermissions",
    "/api/ListMailboxForwarding",
    "/api/ListMailboxCAS",
    "/api/ListMailboxRules",
    "/api/ListMailboxRestores",
    "/api/ListOoO",
    "/api/ListOAuthApps",
    "/api/ListMFAUsers",
    "/api/ListSignIns",
    "/api/ListInactiveAccounts",
    "/api/ListAzureADConnectStatus",
    "/api/ListDefenderState",
    "/api/ListDefenderTVM",
    "/api/ListDeletedItems",
    "/api/ListAntiPhishingFilters",
    "/api/ListMalwareFilters",
    "/api/ListSafeAttachmentsFilters",
    "/api/ListSafeLinksPolicy",
    "/api/ListQuarantinePolicy",
    "/api/ListRestrictedUsers",
    "/api/ListTenantAllowBlockList",
    "/api/ListSharedMailboxAccountEnabled",
    "/api/ListGlobalAddressList",
    "/api/ListEquipment",
    "/api/ListRooms",
    "/api/ListRoomLists",
    "/api/ListAppConsentRequests",
    "/api/ListAuditLogs",
    "/api/ListAuditLogSearches",
    "/api/ListDirectoryObjects",
    "/api/ListIntuneScript",
    "/api/ListIntuneReusableSettings",
    "/api/ListApplicationQueue",
    "/api/ListPotentialApps",
    "/api/ListMessageTrace",
    "/api/ListTenantDetails",
    "/api/listTenantDetails",
    "/api/ListuserCounts",
    "/api/ListTenantAlignment",
    "/api/listBPA",
    "/api/listTenantDrift",
    "/api/ListDomainAnalyser",
    "/api/ListCustomDataMappings",
    "/api/ListJITAdmin",
]


@pytest.mark.parametrize("path", GET_WITH_TENANT)
def test_get_with_tenant(client, path):
    """GET endpoints requiring tenantFilter should not return 500."""
    r = client.get(path, params={"tenantFilter": TENANT})
    assert_not_500(r, f"GET {path}?tenantFilter={TENANT}")


# ===========================================================================
# GET endpoints — special query parameters
# ===========================================================================

def test_get_graph_request(client):
    r = client.get("/api/ListGraphRequest", params={
        "tenantFilter": TENANT,
        "endpoint": "users",
        "$top": "1",
    })
    assert_not_500(r, "GET /api/ListGraphRequest")


def test_get_graph_bulk_request(client):
    r = client.get("/api/ListGraphBulkRequest", params={
        "tenantFilter": TENANT,
        "endpoint": "users",
    })
    assert_not_500(r, "GET /api/ListGraphBulkRequest")


def test_get_exo_request(client):
    r = client.get("/api/ListExoRequest", params={
        "tenantFilter": TENANT,
    })
    assert_not_500(r, "GET /api/ListExoRequest")


def test_get_domain_health(client):
    r = client.get("/api/ListDomainHealth", params={
        "Domain": "contoso.com",
    })
    assert_not_500(r, "GET /api/ListDomainHealth")


def test_get_external_tenant_info(client):
    r = client.get("/api/ListExternalTenantInfo", params={
        "tenantFilter": "contoso.com",
    })
    assert_not_500(r, "GET /api/ListExternalTenantInfo")


def test_get_breaches_account(client):
    r = client.get("/api/ListBreachesAccount", params={
        "account": "test@contoso.com",
    })
    assert_not_500(r, "GET /api/ListBreachesAccount")


def test_get_breaches_tenant(client):
    r = client.get("/api/ListBreachesTenant", params={
        "tenantFilter": TENANT,
    })
    assert_not_500(r, "GET /api/ListBreachesTenant")


def test_get_user_groups(client):
    r = client.get("/api/ListUserGroups", params={
        "tenantFilter": TENANT,
        "userId": "demo-user-id",
    })
    assert_not_500(r, "GET /api/ListUserGroups")


def test_get_user_mailbox_details(client):
    r = client.get("/api/ListUserMailboxDetails", params={
        "tenantFilter": TENANT,
        "userId": "demo-user@contoso.com",
    })
    assert_not_500(r, "GET /api/ListUserMailboxDetails")


def test_get_user_mailbox_rules(client):
    r = client.get("/api/ListUserMailboxRules", params={
        "tenantFilter": TENANT,
        "userId": "demo-user@contoso.com",
    })
    assert_not_500(r, "GET /api/ListUserMailboxRules")


def test_get_user_signin_logs(client):
    r = client.get("/api/ListUserSigninLogs", params={
        "tenantFilter": TENANT,
        "userId": "demo-user-id",
    })
    assert_not_500(r, "GET /api/ListUserSigninLogs")


def test_get_user_photo(client):
    r = client.get("/api/ListUserPhoto", params={
        "tenantFilter": TENANT,
        "userId": "demo-user-id",
    })
    assert_not_500(r, "GET /api/ListUserPhoto")


def test_get_user_trusted_blocked_senders(client):
    r = client.get("/api/ListUserTrustedBlockedSenders", params={
        "tenantFilter": TENANT,
        "userId": "demo-user@contoso.com",
    })
    assert_not_500(r, "GET /api/ListUserTrustedBlockedSenders")


def test_get_site_members(client):
    r = client.get("/api/ListSiteMembers", params={
        "tenantFilter": TENANT,
        "siteUrl": "https://contoso.sharepoint.com",
    })
    assert_not_500(r, "GET /api/ListSiteMembers")


def test_get_mailbox_quarantine_message(client):
    r = client.get("/api/ListMailQuarantineMessage", params={
        "tenantFilter": TENANT,
        "Identity": "test-id",
    })
    assert_not_500(r, "GET /api/ListMailQuarantineMessage")


def test_get_safelinks_policy_details(client):
    r = client.get("/api/ListSafeLinksPolicyDetails", params={
        "tenantFilter": TENANT,
    })
    assert_not_500(r, "GET /api/ListSafeLinksPolicyDetails")


def test_get_safelinks_policy_template_details(client):
    r = client.get("/api/ListSafeLinksPolicyTemplateDetails", params={
        "templateId": "test",
    })
    assert_not_500(r, "GET /api/ListSafeLinksPolicyTemplateDetails")


def test_get_scheduled_item_details(client):
    r = client.get("/api/ListScheduledItemDetails", params={
        "id": "test",
    })
    assert_not_500(r, "GET /api/ListScheduledItemDetails")


def test_get_function_parameters(client):
    r = client.get("/api/ListFunctionParameters", params={
        "Function": "ExecTest",
    })
    assert_not_500(r, "GET /api/ListFunctionParameters")


def test_get_users_and_groups(client):
    r = client.get("/api/ListUsersAndGroups", params={
        "tenantFilter": TENANT,
    })
    assert_not_500(r, "GET /api/ListUsersAndGroups")


def test_get_empty_results(client):
    r = client.get("/api/ListEmptyResults")
    assert_not_500(r, "GET /api/ListEmptyResults")


def test_get_check_ext_alerts(client):
    r = client.get("/api/ListCheckExtAlerts")
    assert_not_500(r, "GET /api/ListCheckExtAlerts")


def test_get_alerts_queue(client):
    r = client.get("/api/ListAlertsQueue")
    assert_not_500(r, "GET /api/ListAlertsQueue")


def test_get_gdap_access_assignments(client):
    r = client.get("/api/ListGDAPAccessAssignments")
    assert_not_500(r, "GET /api/ListGDAPAccessAssignments")


# ===========================================================================
# GET endpoints — security router
# ===========================================================================

SECURITY_GET_ENDPOINTS = [
    "/api/security/secureScoreControlProfiles",
    "/api/security/threatIntelligence",
]

SECURITY_GET_TENANT_ENDPOINTS = [
    "/api/security/riskyUsers",
    "/api/security/riskySignIns",
    "/api/security/riskyServicePrincipals",
    "/api/security/signInSummary",
    "/api/security/authMethodsActivity",
    "/api/security/authMethodsPolicy",
]


@pytest.mark.parametrize("path", SECURITY_GET_ENDPOINTS)
def test_security_get_no_tenant(client, path):
    r = client.get(path)
    assert_not_500(r, f"GET {path}")


@pytest.mark.parametrize("path", SECURITY_GET_TENANT_ENDPOINTS)
def test_security_get_with_tenant(client, path):
    r = client.get(path, params={"tenantFilter": TENANT})
    assert_not_500(r, f"GET {path}")


def test_security_risky_user(client):
    r = client.get("/api/security/riskyUser/demo-user-id", params={"tenantFilter": TENANT})
    assert_not_500(r, "GET /api/security/riskyUser/{user_id}")


def test_security_role_members(client):
    r = client.get("/api/security/roleMembers/demo-role-id", params={"tenantFilter": TENANT})
    assert_not_500(r, "GET /api/security/roleMembers/{role_id}")


# ===========================================================================
# GET endpoints — exec/alert endpoints
# ===========================================================================

EXEC_GET_ENDPOINTS = [
    "/api/ExecAlertsList",
    "/api/ExecIncidentsList",
    "/api/ExecMdoAlertsList",
    "/api/ExecAPIPermissionList",
]


@pytest.mark.parametrize("path", EXEC_GET_ENDPOINTS)
def test_exec_get_endpoints(client, path):
    r = client.get(path, params={"tenantFilter": TENANT})
    assert_not_500(r, f"GET {path}")


def test_exec_update_secure_score(client):
    r = client.get("/api/ExecUpdateSecureScore", params={"tenantFilter": TENANT})
    assert_not_500(r, "GET /api/ExecUpdateSecureScore")


def test_exec_app_insights_query(client):
    r = client.get("/api/ExecAppInsightsQuery")
    assert_not_500(r, "GET /api/ExecAppInsightsQuery")


def test_exec_cipp_logs_sas(client):
    r = client.get("/api/ExecCippLogsSas")
    assert_not_500(r, "GET /api/ExecCippLogsSas")


# ===========================================================================
# GET endpoints — auth endpoints
# ===========================================================================

def test_auth_me(client):
    r = client.get("/.auth/me")
    assert_not_500(r, "GET /.auth/me")


def test_auth_login(client):
    """Auth login may redirect, just verify not 500."""
    r = httpx.get(f"{client.base_url}/.auth/login/aad", follow_redirects=False, timeout=10)
    assert_not_500(r, "GET /.auth/login/aad")


def test_auth_logout(client):
    r = httpx.get(f"{client.base_url}/.auth/logout", follow_redirects=False, timeout=10)
    assert_not_500(r, "GET /.auth/logout")


def test_auth_callback(client):
    r = httpx.get(f"{client.base_url}/.auth/callback", follow_redirects=False, timeout=10)
    assert_not_500(r, "GET /.auth/callback")


# ===========================================================================
# GET endpoints — docs / openapi
# ===========================================================================

def test_openapi_json(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200, f"openapi.json returned {r.status_code}"


def test_docs(client):
    r = client.get("/docs")
    assert r.status_code == 200


def test_redoc(client):
    r = client.get("/redoc")
    assert r.status_code == 200


def test_version_json(client):
    r = client.get("/version.json")
    assert_not_500(r, "GET /version.json")


# ===========================================================================
# POST endpoints — safe in demo mode (empty body)
# ===========================================================================

POST_SAFE_ENDPOINTS = [
    "/api/ExecUniversalSearch",
    "/api/ExecGeoIPLookup",
    "/api/ExecBreachSearch",
    "/api/ExecCACheck",
    "/api/ExecBPA",
    "/api/ExecStandardsRun",
    "/api/ExecDomainAnalyser",
    "/api/ExecAccessChecks",
    "/api/ExecCPVPermissions",
    "/api/ExecCPVRefresh",
    "/api/ExecPermissionRepair",
    "/api/ExecExtensionTest",
    "/api/ExecLicenseSearch",
    "/api/ExecBitlockerSearch",
    "/api/ExecTestRun",
    "/api/ExecCIPPDBCache",
    "/api/ListGraphRequest",
    "/api/ExecTokenExchange",
]


@pytest.mark.parametrize("path", POST_SAFE_ENDPOINTS)
def test_post_safe_empty_body(client, path):
    """POST endpoints with empty body should not return 500."""
    r = client.post(path, json={})
    assert_not_500(r, f"POST {path}")


# ===========================================================================
# POST endpoints — with tenantFilter in body
# ===========================================================================

POST_WITH_TENANT_BODY = [
    "/api/ExecConvertMailbox",
    "/api/ExecHideFromGAL",
    "/api/ExecCopyForSent",
    "/api/ExecEnableArchive",
    "/api/ExecEnableAutoExpandingArchive",
    "/api/ExecSetLitigationHold",
    "/api/ExecOneDriveProvision",
    "/api/ExecDisableUser",
    "/api/ExecResetPass",
    "/api/ExecResetMFA",
    "/api/ExecRevokeSessions",
    "/api/ExecCreateTAP",
    "/api/ExecSendPush",
    "/api/ExecClrImmId",
    "/api/ExecPerUserMFA",
    "/api/ExecPasswordNeverExpires",
    "/api/ExecHVEUser",
    "/api/ExecDismissRiskyUser",
    "/api/ExecEmailForward",
    "/api/ExecSetOoO",
    "/api/ExecModifyCalPerms",
    "/api/ExecModifyContactPerms",
    "/api/ExecModifyMBPerms",
    "/api/ExecRemoveMailboxRule",
    "/api/ExecSetMailboxRule",
    "/api/ExecSetMailboxQuota",
    "/api/ExecSetMailboxLocale",
    "/api/ExecSetMailboxEmailSize",
    "/api/ExecSetRecipientLimits",
    "/api/ExecScheduleMailboxVacation",
    "/api/ExecScheduleOOOVacation",
    "/api/ExecStartManagedFolderAssistant",
    "/api/ExecSetRetentionHold",
    "/api/ExecSetMailboxRetentionPolicies",
    "/api/ExecMailboxRestore",
    "/api/ExecSetCalendarProcessing",
    "/api/ExecQuarantineManagement",
    "/api/ExecRemoveRestrictedUser",
    "/api/ExecDeviceAction",
    "/api/ExecDeviceDelete",
    "/api/ExecDevicePasscodeAction",
    "/api/ExecSetCloudManaged",
    "/api/ExecAssignPolicy",
    "/api/ExecAssignApp",
    "/api/ExecSyncAPDevices",
    "/api/ExecSyncDEP",
    "/api/ExecSyncVPP",
    "/api/ExecAssignAPDevice",
    "/api/ExecRenameAPDevice",
    "/api/ExecSetAPDeviceGroupTag",
    "/api/ExecSharePointPerms",
    "/api/ExecSetSharePointMember",
    "/api/ExecTeamsVoicePhoneNumberAssignment",
    "/api/ExecRemoveTeamsVoicePhoneNumberAssignment",
    "/api/ExecSetSecurityAlert",
    "/api/ExecSetSecurityIncident",
    "/api/ExecSetMdoAlert",
    "/api/ExecDomainAction",
    "/api/ExecEditCalendarPermissions",
    "/api/ExecCSPLicense",
    "/api/ExecBulkLicense",
    "/api/ExecGetRecoveryKey",
    "/api/ExecGetLocalAdminPassword",
    "/api/ExecReprocessUserLicenses",
]


@pytest.mark.parametrize("path", POST_WITH_TENANT_BODY)
def test_post_with_tenant_body(client, path):
    """POST endpoints with tenantFilter in body should not return 500."""
    r = client.post(path, json={"tenantFilter": TENANT})
    assert_not_500(r, f"POST {path}")


# ===========================================================================
# POST endpoints — configuration / settings (empty or minimal body)
# ===========================================================================

POST_CONFIG_ENDPOINTS = [
    "/api/ExecNotificationConfig",
    "/api/ExecExtensionsConfig",
    "/api/ExecExtensionMapping",
    "/api/ExecExtensionSync",
    "/api/ExecFeatureFlag",
    "/api/ExecUserSettings",
    "/api/ExecUserBookmarks",
    "/api/ExecCustomRole",
    "/api/ExecCustomData",
    "/api/ExecDiagnosticsPresets",
    "/api/ExecPartnerMode",
    "/api/ExecPartnerWebhook",
    "/api/ExecPasswordConfig",
    "/api/ExecTimeSettings",
    "/api/ExecBackupRetentionConfig",
    "/api/ExecLogRetentionConfig",
    "/api/ExecSetCIPPAutoBackup",
    "/api/ExecJITAdminSettings",
    "/api/ExecCombinedSetup",
    "/api/ExecSAMSetup",
    "/api/ExecSAMRoles",
    "/api/ExecSAMAppPermissions",
    "/api/execSamAppPermissions",
    "/api/ExecServicePrincipals",
    "/api/ExecAddTrustedIP",
    "/api/ExecOffloadFunctions",
    "/api/ExecStandardsRun",
    "/api/ExecDnsConfig",
    "/api/ExecCippReplacemap",
    "/api/ExecCippFunction",
    "/api/ExecApiClient",
    "/api/ExecRunBackup",
    "/api/ExecRestoreBackup",
    "/api/ExecExcludeLicenses",
    "/api/ExecExchangeRoleRepair",
    "/api/ExecManageRetentionPolicies",
    "/api/ExecManageRetentionTags",
    "/api/ExecUpdateRefreshToken",
    "/api/ExecDeviceCodeLogon",
    "/api/ExecGitHubAction",
    "/api/ExecCommunityRepo",
    "/api/ExecUpdateDriftDeviation",
    "/api/execStandardConvert",
    "/api/execBecRemediate",
    "/api/security/confirmCompromised",
]


@pytest.mark.parametrize("path", POST_CONFIG_ENDPOINTS)
def test_post_config_empty_body(client, path):
    """POST config/settings endpoints with empty body should not return 500."""
    r = client.post(path, json={})
    assert_not_500(r, f"POST {path}")


# ===========================================================================
# POST endpoints — Add* (create resources)
# ===========================================================================

POST_ADD_ENDPOINTS = [
    "/api/AddUser",
    "/api/AddUserBulk",
    "/api/AddUserDefaults",
    "/api/AddGroup",
    "/api/AddGroupTeam",
    "/api/AddGroupTemplate",
    "/api/AddGuest",
    "/api/AddContact",
    "/api/AddContactTemplates",
    "/api/AddDomain",
    "/api/AddSharedMailbox",
    "/api/AddEquipmentMailbox",
    "/api/AddRoomMailbox",
    "/api/AddRoomList",
    "/api/AddSite",
    "/api/AddSiteBulk",
    "/api/AddTeam",
    "/api/AddAlert",
    "/api/AddAPDevice",
    "/api/AddAutopilotConfig",
    "/api/AddCAPolicy",
    "/api/AddCATemplate",
    "/api/AddNamedLocation",
    "/api/AddPolicy",
    "/api/AddEnrollment",
    "/api/AddIntuneTemplate",
    "/api/AddIntuneReusableSetting",
    "/api/AddIntuneReusableSettingTemplate",
    "/api/AddExConnector",
    "/api/AddExConnectorTemplate",
    "/api/AddConnectionFilter",
    "/api/AddConnectionfilterTemplate",
    "/api/AddSpamFilter",
    "/api/AddSpamfilterTemplate",
    "/api/AddEditTransportRule",
    "/api/AddTransportRule",
    "/api/AddTransportTemplate",
    "/api/AddDefenderDeployment",
    "/api/AddQuarantinePolicy",
    "/api/AddSafeLinksPolicyFromTemplate",
    "/api/AddSafeLinksPolicyTemplate",
    "/api/CreateSafeLinksPolicyTemplate",
    "/api/AddTenantAllowBlockList",
    "/api/AddBPATemplate",
    "/api/AddStandardTemplate",
    "/api/AddStandardsTemplate",
    "/api/AddScheduledItem",
    "/api/AddJITAdminTemplate",
    "/api/AddAssignmentFilter",
    "/api/AddAssignmentFilterTemplate",
    "/api/AddTenant",
    "/api/AddChocoApp",
    "/api/AddOfficeApp",
    "/api/AddStoreApp",
    "/api/AddwinGetApp",
    "/api/AddMSPApp",
    "/api/AddTestReport",
]


@pytest.mark.parametrize("path", POST_ADD_ENDPOINTS)
def test_post_add_empty_body(client, path):
    """POST Add* endpoints with empty body should not return 500."""
    r = client.post(path, json={})
    assert_not_500(r, f"POST {path}")


# ===========================================================================
# POST endpoints — Edit* (modify resources)
# ===========================================================================

POST_EDIT_ENDPOINTS = [
    "/api/EditUser",
    "/api/EditGroup",
    "/api/EditContact",
    "/api/EditContactTemplates",
    "/api/EditEquipmentMailbox",
    "/api/EditRoomMailbox",
    "/api/EditRoomList",
    "/api/EditCAPolicy",
    "/api/EditAntiPhishingFilter",
    "/api/EditMalwareFilter",
    "/api/EditSafeAttachmentsFilter",
    "/api/EditSafeLinksPolicy",
    "/api/EditSafeLinkspolicy",
    "/api/EditSafeLinksPolicyTemplate",
    "/api/EditSpamfilter",
    "/api/EditExConnector",
    "/api/EditQuarantinePolicy",
    "/api/EditIntuneScript",
    "/api/EditJITAdminTemplate",
    "/api/EditAssignmentFilter",
    "/api/EditTenant",
    "/api/EditTenantOffboardingDefaults",
    "/api/EditUserAliases",
    "/api/PatchUser",
    "/api/SetAuthMethod",
]


@pytest.mark.parametrize("path", POST_EDIT_ENDPOINTS)
def test_post_edit_empty_body(client, path):
    """POST Edit* endpoints with empty body should not return 500."""
    r = client.post(path, json={})
    assert_not_500(r, f"POST {path}")


# ===========================================================================
# POST endpoints — Remove* (delete resources)
# ===========================================================================

POST_REMOVE_ENDPOINTS = [
    "/api/RemoveUser",
    "/api/RemoveContact",
    "/api/RemoveContactTemplates",
    "/api/RemoveApp",
    "/api/RemovePolicy",
    "/api/RemoveCAPolicy",
    "/api/RemoveCATemplate",
    "/api/RemoveBPATemplate",
    "/api/RemoveGroupTemplate",
    "/api/RemoveIntuneTemplate",
    "/api/RemoveIntuneScript",
    "/api/RemoveIntuneReusableSetting",
    "/api/RemoveIntuneReusableSettingTemplate",
    "/api/RemoveExConnector",
    "/api/RemoveExConnectorTemplate",
    "/api/RemoveConnectionfilterTemplate",
    "/api/RemoveSpamFilter",
    "/api/RemoveSpamfilterTemplate",
    "/api/RemoveAntiPhishingFilter",
    "/api/RemoveMalwareFilter",
    "/api/RemoveSafeAttachmentsFilter",
    "/api/RemoveSafeLinksPolicyTemplate",
    "/api/RemoveTransportRule",
    "/api/RemoveTransportRuleTemplate",
    "/api/RemoveQuarantinePolicy",
    "/api/RemoveTenantAllowBlockList",
    "/api/RemoveAutopilotConfig",
    "/api/RemoveAPDevice",
    "/api/RemoveAssignmentFilterTemplate",
    "/api/RemoveJITAdminTemplate",
    "/api/RemoveStandardTemplate",
    "/api/RemoveScheduledItem",
    "/api/RemoveDeletedObject",
    "/api/RemoveQueuedAlert",
    "/api/RemoveQueuedApp",
    "/api/RemoveTenantCapabilitiesCache",
    "/api/RemoveTrustedBlockedSender",
    "/api/RemoveUserDefaultTemplate",
    "/api/DeleteSharepointSite",
    "/api/DeleteTestReport",
]


@pytest.mark.parametrize("path", POST_REMOVE_ENDPOINTS)
def test_post_remove_empty_body(client, path):
    """POST Remove* endpoints with empty body should not return 500."""
    r = client.post(path, json={})
    assert_not_500(r, f"POST {path}")


# ===========================================================================
# POST endpoints — Exec* (actions with specific body shapes)
# ===========================================================================

POST_EXEC_SPECIAL = [
    "/api/ExecAddAlert",
    "/api/ExecAddGDAPRole",
    "/api/ExecAddMultiTenantApp",
    "/api/ExecAddTenant",
    "/api/ExecApplication",
    "/api/ExecAppUpload",
    "/api/ExecAppPermissionTemplate",
    "/api/ExecAppApprovalTemplate",
    "/api/ExecAuditLogSearch",
    "/api/ExecAutoExtendGDAP",
    "/api/ExecAzBobbyTables",
    "/api/ExecBrandingSettings",
    "/api/ExecCAExclusion",
    "/api/ExecCAServiceExclusion",
    "/api/ExecCloneTemplate",
    "/api/ExecCreateAppTemplate",
    "/api/ExecCreateDefaultGroups",
    "/api/ExecCreateSamApp",
    "/api/ExecDeleteGDAPRelationship",
    "/api/ExecDeleteGDAPRoleMapping",
    "/api/ExecDeleteSafeLinksPolicy",
    "/api/ExecDriftClone",
    "/api/ExecEditTemplate",
    "/api/ExecExcludeTenant",
    "/api/ExecGDAPAccessAssignment",
    "/api/ExecGDAPInvite",
    "/api/ExecGDAPRemoveGArole",
    "/api/ExecGDAPRoleTemplate",
    "/api/ExecGDAPTrace",
    "/api/ExecGroupsDelete",
    "/api/ExecGroupsDeliveryManagement",
    "/api/ExecGroupsHideFromGAL",
    "/api/ExecJitAdmin",
    "/api/ExecNamedLocation",
    "/api/ExecNewSafeLinkspolicy",
    "/api/ExecOffboardTenant",
    "/api/ExecOffboardUser",
    "/api/ExecOnboardTenant",
    "/api/ExecOneDriveShortCut",
    "/api/ExecRemoveTenant",
    "/api/ExecRunTenantGroupRule",
    "/api/ExecSetPackageTag",
    "/api/ExecSetUserPhoto",
    "/api/ExecTenantGroup",
    "/api/DeployContactTemplates",
    "/api/AddAssignmentFilter",
]


@pytest.mark.parametrize("path", POST_EXEC_SPECIAL)
def test_post_exec_special_empty_body(client, path):
    """POST Exec* special endpoints with empty body should not return 500."""
    r = client.post(path, json={})
    assert_not_500(r, f"POST {path}")
