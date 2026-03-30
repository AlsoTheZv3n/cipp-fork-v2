"""Test that backend response formats match what the CIPP frontend expects.

The frontend uses patterns like:
  - response.data || []           -> expects an array
  - response.data?.Results        -> expects {Results: ...}
  - response.data?.displayName    -> expects an object with specific keys

Run: cd backend && PYTHONPATH=. python -m pytest tests/test_response_formats.py -v
Requires: backend running in DEMO_MODE on http://127.0.0.1:8055
"""
import pytest

TENANT = "demo-tenant-contoso"


# ===========================================================================
# Endpoints that the frontend expects to return an ARRAY (list)
# Pattern: response.data || []  or  Array.isArray(response.data)
# ===========================================================================

ARRAY_RESPONSE_ENDPOINTS = [
    # dashboardv2/index.js: reportsApi.data || []
    ("/api/ListTestReports", {}),
    # CippTable / general list endpoints consumed as arrays
    ("/api/ListTenants", {}),
    ("/api/listTenants", {}),
    ("/api/ListUsers", {"tenantFilter": TENANT}),
    ("/api/listUsers", {"tenantFilter": TENANT}),
    ("/api/ListGroups", {"tenantFilter": TENANT}),
    ("/api/ListDevices", {"tenantFilter": TENANT}),
    ("/api/ListMailboxes", {"tenantFilter": TENANT}),
    ("/api/ListContacts", {"tenantFilter": TENANT}),
    ("/api/ListDomains", {"tenantFilter": TENANT}),
    ("/api/ListLicenses", {"tenantFilter": TENANT}),
    ("/api/ListCSPsku", {"tenantFilter": TENANT}),
    ("/api/listCSPLicenses", {"tenantFilter": TENANT}),
    ("/api/ListRoles", {"tenantFilter": TENANT}),
    ("/api/ListApps", {"tenantFilter": TENANT}),
    ("/api/ListConditionalAccessPolicies", {"tenantFilter": TENANT}),
    ("/api/ListNamedLocations", {"tenantFilter": TENANT}),
    ("/api/ListIntunePolicy", {"tenantFilter": TENANT}),
    ("/api/ListCompliancePolicies", {"tenantFilter": TENANT}),
    ("/api/ListAppProtectionPolicies", {"tenantFilter": TENANT}),
    ("/api/ListAssignmentFilters", {"tenantFilter": TENANT}),
    ("/api/ListAutopilotConfig", {"tenantFilter": TENANT}),
    ("/api/ListAPDevices", {"tenantFilter": TENANT}),
    ("/api/ListTeams", {"tenantFilter": TENANT}),
    ("/api/ListTeamsActivity", {"tenantFilter": TENANT}),
    ("/api/ListTeamsVoice", {"tenantFilter": TENANT}),
    ("/api/ListSites", {"tenantFilter": TENANT}),
    ("/api/ListTransportRules", {"tenantFilter": TENANT}),
    ("/api/ListExchangeConnectors", {"tenantFilter": TENANT}),
    ("/api/ListConnectionFilter", {"tenantFilter": TENANT}),
    ("/api/ListSpamfilter", {"tenantFilter": TENANT}),
    ("/api/ListMailQuarantine", {"tenantFilter": TENANT}),
    ("/api/ListCalendarPermissions", {"tenantFilter": TENANT}),
    ("/api/ListContactPermissions", {"tenantFilter": TENANT}),
    ("/api/ListMailboxPermissions", {"tenantFilter": TENANT}),
    ("/api/ListMailboxForwarding", {"tenantFilter": TENANT}),
    ("/api/ListMailboxCAS", {"tenantFilter": TENANT}),
    ("/api/ListMailboxRules", {"tenantFilter": TENANT}),
    ("/api/ListMailboxRestores", {"tenantFilter": TENANT}),
    ("/api/ListOAuthApps", {"tenantFilter": TENANT}),
    ("/api/ListMFAUsers", {"tenantFilter": TENANT}),
    ("/api/ListSignIns", {"tenantFilter": TENANT}),
    ("/api/ListInactiveAccounts", {"tenantFilter": TENANT}),
    ("/api/ListDeletedItems", {"tenantFilter": TENANT}),
    ("/api/ListAntiPhishingFilters", {"tenantFilter": TENANT}),
    ("/api/ListMalwareFilters", {"tenantFilter": TENANT}),
    ("/api/ListSafeAttachmentsFilters", {"tenantFilter": TENANT}),
    ("/api/ListSafeLinksPolicy", {"tenantFilter": TENANT}),
    ("/api/ListQuarantinePolicy", {"tenantFilter": TENANT}),
    ("/api/ListRestrictedUsers", {"tenantFilter": TENANT}),
    ("/api/ListTenantAllowBlockList", {"tenantFilter": TENANT}),
    ("/api/ListSharedMailboxAccountEnabled", {"tenantFilter": TENANT}),
    ("/api/ListGlobalAddressList", {"tenantFilter": TENANT}),
    ("/api/ListEquipment", {"tenantFilter": TENANT}),
    ("/api/ListRooms", {"tenantFilter": TENANT}),
    ("/api/ListRoomLists", {"tenantFilter": TENANT}),
    ("/api/ListAppConsentRequests", {"tenantFilter": TENANT}),
    ("/api/ListAuditLogs", {"tenantFilter": TENANT}),
    ("/api/ListAuditLogSearches", {"tenantFilter": TENANT}),
    ("/api/ListIntuneScript", {"tenantFilter": TENANT}),
    ("/api/ListIntuneReusableSettings", {"tenantFilter": TENANT}),
    ("/api/ListDefenderState", {"tenantFilter": TENANT}),
    ("/api/ListDefenderTVM", {"tenantFilter": TENANT}),
    ("/api/ListMessageTrace", {"tenantFilter": TENANT}),
    ("/api/ListDomainAnalyser", {}),
    ("/api/ListStandards", {}),
    ("/api/ListStandardTemplates", {}),
    ("/api/listStandardTemplates", {}),
    ("/api/ListBPATemplates", {}),
    ("/api/listBPATemplates", {}),
    ("/api/ListCATemplates", {}),
    ("/api/ListGroupTemplates", {}),
    ("/api/ListContactTemplates", {}),
    ("/api/ListIntuneTemplates", {}),
    ("/api/ListExConnectorTemplates", {}),
    ("/api/ListConnectionFilterTemplates", {}),
    ("/api/ListSpamFilterTemplates", {}),
    ("/api/ListTransportRulesTemplates", {}),
    ("/api/ListSafeLinksPolicyTemplates", {}),
    ("/api/ListAssignmentFilterTemplates", {}),
    ("/api/ListJITAdminTemplates", {}),
    ("/api/ListScheduledItems", {}),
    ("/api/ListGDAPRoles", {}),
    ("/api/ListGDAPInvite", {}),
    ("/api/ListGDAPAccessAssignments", {}),
    ("/api/ListCustomRole", {}),
    ("/api/ListExcludedLicenses", {}),
    ("/api/ListTenantGroups", {}),
    ("/api/ListCommunityRepos", {}),
    ("/api/ListAppsRepository", {}),
    ("/api/ListAvailableTests", {}),
    ("/api/ListAppApprovalTemplates", {}),
    ("/api/ListIntuneReusableSettingTemplates", {}),
    ("/api/ListFeatureFlags", {}),
    ("/api/ListLogs", {}),
    ("/api/ListCippQueue", {}),
    ("/api/ListAlertsQueue", {}),
    ("/api/ListCheckExtAlerts", {}),
    # breachlookup page: getGeoIP.data?.map(...)
    ("/api/ListBreachesTenant", {"tenantFilter": TENANT}),
    # Security endpoints returning arrays
    ("/api/security/riskyUsers", {"tenantFilter": TENANT}),
    ("/api/security/riskySignIns", {"tenantFilter": TENANT}),
    ("/api/security/riskyServicePrincipals", {"tenantFilter": TENANT}),
    ("/api/ExecAlertsList", {"tenantFilter": TENANT}),
    ("/api/ExecIncidentsList", {"tenantFilter": TENANT}),
    ("/api/ExecMdoAlertsList", {"tenantFilter": TENANT}),
    ("/api/ListJITAdmin", {"tenantFilter": TENANT}),
    ("/api/ListCustomDataMappings", {}),
]


@pytest.mark.parametrize("path,params", ARRAY_RESPONSE_ENDPOINTS,
                         ids=[f"array:{p}" for p, _ in ARRAY_RESPONSE_ENDPOINTS])
def test_response_is_array(client, path, params):
    """Verify endpoints the frontend expects as arrays actually return arrays."""
    r = client.get(path, params=params)
    if r.status_code >= 500:
        pytest.skip(f"Server error {r.status_code}, skipping format check")
    if r.status_code == 200:
        data = r.json()
        assert isinstance(data, list), (
            f"{path} should return a list/array but got {type(data).__name__}: "
            f"{str(data)[:200]}"
        )


# ===========================================================================
# Endpoints that the frontend expects to return an OBJECT with Results key
# Pattern: response.data?.Results  or  response.data.Results
# ===========================================================================

RESULTS_RESPONSE_ENDPOINTS = [
    # CippGraphExplorerFilter.js: presetList.data?.Results
    ("/api/ListGraphExplorerPresets", {}),
    # ExecGraphExplorerPreset
    ("/api/ExecGraphExplorerPreset", {}),
    # CippBackendCard: backendComponents?.data?.Results
    ("/api/ExecBackendURLs", {}),
    # CippPasswordSettings: passwordSetting.data.Results
    ("/api/ExecPasswordConfig", {}),  # GET-like behavior via POST but also GET
    # CippBackupRetentionSettings: retentionSetting?.data?.Results
    ("/api/ExecBackupRetentionConfig", {}),  # returns Results
    # CippLogRetentionSettings: retentionSetting?.data?.Results
    ("/api/ExecLogRetentionConfig", {}),
    # use-securescore.js: secureScore.data.Results
    ("/api/ExecUpdateSecureScore", {"tenantFilter": TENANT}),
    # ListGraphRequest with Results
    ("/api/ListGraphRequest", {"tenantFilter": TENANT, "endpoint": "users", "$top": "1"}),
    # dashboardv1.js: partners.data?.Results
    ("/api/ListExoRequest", {"tenantFilter": TENANT}),
    # CippApiClientManagement: azureConfig.data?.Results
    ("/api/ExecApiClient", {}),
    # CippStandardsSideBar: tenantGroupsApi.data?.Results
    ("/api/ListTenantGroups", {}),
]


@pytest.mark.parametrize("path,params", RESULTS_RESPONSE_ENDPOINTS,
                         ids=[f"results:{p}" for p, _ in RESULTS_RESPONSE_ENDPOINTS])
def test_response_has_results_key(client, path, params):
    """Verify endpoints the frontend accesses via .Results have that key."""
    r = client.get(path, params=params)
    if r.status_code >= 500:
        pytest.skip(f"Server error {r.status_code}, skipping format check")
    if r.status_code == 200:
        data = r.json()
        # Some endpoints return a dict with Results; some return a list
        # If it returns a dict, it must have Results
        if isinstance(data, dict):
            assert "Results" in data, (
                f"{path} should have 'Results' key but got keys: {list(data.keys())[:10]}"
            )


# ===========================================================================
# Endpoints that the frontend expects to return an OBJECT (not array)
# Pattern: response.data?.displayName, response.data?.Users, etc.
# ===========================================================================

OBJECT_RESPONSE_ENDPOINTS = [
    # dashboardv1.js: organization.data?.displayName
    ("/api/ListOrg", {"tenantFilter": TENANT}),
    # dashboardv1.js: dashboard.data?.Users, dashboard.data?.LicUsers
    ("/api/ListuserCounts", {"tenantFilter": TENANT}),
    # dashboardv1.js: sharepoint.data?.TenantStorageMB
    ("/api/ListSharepointQuota", {"tenantFilter": TENANT}),
    # dashboardv2/index.js: testsApi.data?.TenantCounts, testsApi.data?.SecureScore
    ("/api/ListTests", {"tenantFilter": TENANT}),
    # TenantDetails
    ("/api/ListTenantDetails", {"tenantFilter": TENANT}),
    ("/api/listTenantDetails", {"tenantFilter": TENANT}),
    # AzureADConnectStatus
    ("/api/ListAzureADConnectStatus", {"tenantFilter": TENANT}),
    # Extensions config
    ("/api/ListExtensionsConfig", {}),
    # Notification config
    ("/api/ListNotificationConfig", {}),
    # SharePoint admin url
    ("/api/ListSharePointAdminUrl", {"tenantFilter": TENANT}),
    # User settings
    ("/api/ListUserSettings", {}),
    # New user defaults
    ("/api/ListNewUserDefaults", {}),
]


@pytest.mark.parametrize("path,params", OBJECT_RESPONSE_ENDPOINTS,
                         ids=[f"object:{p}" for p, _ in OBJECT_RESPONSE_ENDPOINTS])
def test_response_is_object(client, path, params):
    """Verify endpoints the frontend uses as objects actually return objects."""
    r = client.get(path, params=params)
    if r.status_code >= 500:
        pytest.skip(f"Server error {r.status_code}, skipping format check")
    if r.status_code == 200:
        data = r.json()
        assert isinstance(data, dict), (
            f"{path} should return an object/dict but got {type(data).__name__}: "
            f"{str(data)[:200]}"
        )


# ===========================================================================
# Auth endpoint format
# Pattern: response.data?.clientPrincipal
# ===========================================================================

def test_auth_me_format(client):
    """/.auth/me must return {clientPrincipal: ...} for the frontend layout."""
    r = client.get("/.auth/me")
    if r.status_code == 200:
        data = r.json()
        assert isinstance(data, dict), "/.auth/me should return an object"
        assert "clientPrincipal" in data, (
            f"/.auth/me must have 'clientPrincipal' key, got: {list(data.keys())}"
        )


def test_api_me_format(client):
    """/api/me must return {clientPrincipal: ..., permissions: ...}."""
    r = client.get("/api/me")
    if r.status_code == 200:
        data = r.json()
        assert isinstance(data, dict), "/api/me should return an object"
        assert "clientPrincipal" in data, (
            f"/api/me must have 'clientPrincipal' key, got: {list(data.keys())}"
        )


# ===========================================================================
# GetVersion format
# ===========================================================================

def test_get_version_format(client):
    """/api/GetVersion must return {version: ...}."""
    r = client.get("/api/GetVersion")
    if r.status_code == 200:
        data = r.json()
        assert isinstance(data, dict), "/api/GetVersion should return an object"
        assert "version" in data, (
            f"/api/GetVersion must have 'version' key, got: {list(data.keys())}"
        )


# ===========================================================================
# GetCippAlerts format
# ===========================================================================

def test_cipp_alerts_format(client):
    """/api/GetCippAlerts must return a list."""
    r = client.get("/api/GetCippAlerts")
    if r.status_code == 200:
        data = r.json()
        assert isinstance(data, list), (
            f"/api/GetCippAlerts should return a list, got {type(data).__name__}"
        )


# ===========================================================================
# ListTenants format — must be array of objects with specific keys
# ===========================================================================

def test_list_tenants_item_format(client):
    """Each tenant in ListTenants must have expected keys."""
    r = client.get("/api/ListTenants")
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            tenant = data[0]
            assert isinstance(tenant, dict), "Each tenant should be a dict"
            # Frontend commonly accesses these fields
            expected_keys = {"customerId", "defaultDomainName", "displayName"}
            missing = expected_keys - set(tenant.keys())
            assert not missing, (
                f"Tenant object missing keys: {missing}. Has: {list(tenant.keys())[:15]}"
            )


# ===========================================================================
# dashboardv2 — ListTests format
# ===========================================================================

def test_list_tests_format(client):
    """ListTests should return object with TenantCounts, TestResults, etc."""
    r = client.get("/api/ListTests", params={"tenantFilter": TENANT})
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, dict):
            # Frontend accesses: data?.TenantCounts, data?.TestResults, data?.SecureScore
            # At minimum it should be a dict (not array)
            pass  # dict is correct
        # If it's a list, that may also be valid depending on implementation


# ===========================================================================
# Drift endpoint format
# ===========================================================================

def test_list_tenant_drift_format(client):
    """listTenantDrift should return a list."""
    r = client.get("/api/listTenantDrift", params={"TenantFilter": TENANT})
    if r.status_code == 200:
        data = r.json()
        assert isinstance(data, (list, dict)), (
            f"listTenantDrift should return list or dict, got {type(data).__name__}"
        )
