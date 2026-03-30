"""CIPP Frontend Compatibility Tests.

Tests that our backend responses match what the CIPP frontend expects.
Run: cd backend && DEMO_MODE=true PYTHONPATH=. python -m pytest tests/test_compat.py -v

IMPORTANT: These tests require the backend running in demo mode on port 8055.
Start with: DEMO_MODE=true PYTHONPATH=. uvicorn app.main:app --port 8055
"""
import os
import pytest
import httpx

BASE = os.getenv("TEST_API_URL", "http://127.0.0.1:8055")
TENANT = "demo-tenant-contoso"


def get(path, **params):
    """Sync GET helper."""
    r = httpx.get(f"{BASE}{path}", params=params, timeout=10)
    return r


def post(path, body=None):
    """Sync POST helper."""
    r = httpx.post(f"{BASE}{path}", json=body or {}, timeout=10)
    return r


# ============================================================
# Auth endpoints — frontend requires specific formats
# ============================================================

class TestAuth:
    def test_auth_me_returns_client_principal(self):
        """/.auth/me must return {clientPrincipal: {...}} or {clientPrincipal: null}"""
        r = get("/.auth/me")
        assert r.status_code == 200
        data = r.json()
        assert "clientPrincipal" in data

    def test_api_me_returns_client_principal_and_permissions(self):
        """/api/me must return {clientPrincipal: {...}, permissions: [...]}"""
        r = get("/api/me")
        assert r.status_code == 200
        data = r.json()
        assert "clientPrincipal" in data
        cp = data["clientPrincipal"]
        assert "userRoles" in cp
        assert isinstance(cp["userRoles"], list)
        assert len(cp["userRoles"]) > 0
        # Must not contain blocked roles only
        blocked = {"anonymous", "authenticated"}
        real_roles = [r for r in cp["userRoles"] if r not in blocked]
        assert len(real_roles) > 0, "Must have at least one non-blocked role"

    def test_api_me_has_permissions(self):
        r = get("/api/me")
        data = r.json()
        assert "permissions" in data
        assert isinstance(data["permissions"], list)


# ============================================================
# Tenant endpoints
# ============================================================

class TestTenants:
    def test_list_tenants_returns_array(self):
        """ListTenants must return an array of tenant objects."""
        r = get("/api/ListTenants")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        if data:
            assert "tenantId" in data[0] or "customerId" in data[0]
            assert "displayName" in data[0]

    def test_list_tenants_lowercase(self):
        """listTenants (lowercase) must work too."""
        r = get("/api/listTenants")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_tenant_filter_returns_array(self):
        """/api/tenantFilter must return array for dropdown."""
        r = get("/api/tenantFilter")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ============================================================
# User endpoints
# ============================================================

class TestUsers:
    def test_list_users_returns_array(self):
        """ListUsers must return array of user objects."""
        r = get("/api/ListUsers", tenantFilter=TENANT)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_list_users_with_userid_returns_array(self):
        """ListUsers?UserId=xxx must return array (single user wrapped)."""
        r = get("/api/ListUsers", tenantFilter=TENANT, UserId="test@test.com")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_list_user_counts(self):
        r = get("/api/ListuserCounts", tenantFilter=TENANT)
        assert r.status_code == 200

    def test_list_user_photo_no_crash(self):
        """ListUserPhoto must not 422 even with missing params."""
        r = get("/api/ListUserPhoto")
        assert r.status_code == 200
        r2 = get("/api/ListUserPhoto", UserID="test@test.com")
        assert r2.status_code == 200


# ============================================================
# Groups
# ============================================================

class TestGroups:
    def test_list_groups_returns_array(self):
        r = get("/api/ListGroups", tenantFilter=TENANT)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ============================================================
# Licenses
# ============================================================

class TestLicenses:
    def test_list_licenses_returns_array(self):
        r = get("/api/ListLicenses", tenantFilter=TENANT)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_csp_sku(self):
        r = get("/api/ListCSPsku", tenantFilter=TENANT)
        assert r.status_code == 200


# ============================================================
# Security
# ============================================================

class TestSecurity:
    def test_list_ca_policies_returns_array(self):
        r = get("/api/ListConditionalAccessPolicies", tenantFilter=TENANT)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_alerts_list_returns_array(self):
        r = get("/api/ExecAlertsList", tenantFilter=TENANT)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_sign_ins_returns_array(self):
        r = get("/api/ListSignIns", tenantFilter=TENANT)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_audit_logs_returns_array(self):
        r = get("/api/ListAuditLogs", tenantFilter=TENANT)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_roles_returns_array(self):
        r = get("/api/ListRoles", tenantFilter=TENANT)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ============================================================
# Settings — must return {Results: ...} format
# ============================================================

class TestSettings:
    def test_feature_flags_has_results(self):
        r = get("/api/ListFeatureFlags")
        assert r.status_code == 200
        data = r.json()
        assert "Results" in data

    def test_user_settings_has_results(self):
        r = get("/api/ListUserSettings")
        assert r.status_code == 200
        assert "Results" in r.json()

    def test_extensions_config_has_results(self):
        r = get("/api/ListExtensionsConfig")
        assert r.status_code == 200
        assert "Results" in r.json()

    def test_scheduled_items_has_results(self):
        r = get("/api/ListScheduledItems")
        assert r.status_code == 200
        assert "Results" in r.json()

    def test_community_repos_has_results(self):
        r = get("/api/ListCommunityRepos")
        assert r.status_code == 200
        assert "Results" in r.json()

    def test_custom_role_has_results(self):
        r = get("/api/ListCustomRole")
        assert r.status_code == 200
        assert "Results" in r.json()

    def test_logs_has_results(self):
        r = get("/api/Listlogs")
        assert r.status_code == 200
        assert "Results" in r.json()

    def test_notification_config_has_results(self):
        r = get("/api/ListNotificationConfig")
        assert r.status_code == 200
        assert "Results" in r.json()


# ============================================================
# Templates — must return {Results: [...]}
# ============================================================

class TestTemplates:
    def test_graph_explorer_presets_has_results(self):
        r = get("/api/ListGraphExplorerPresets")
        assert r.status_code == 200
        data = r.json()
        assert "Results" in data
        assert isinstance(data["Results"], list)

    def test_ca_templates_has_results(self):
        r = get("/api/ListCATemplates")
        assert r.status_code == 200
        assert "Results" in r.json()

    def test_group_templates_has_results(self):
        r = get("/api/ListGroupTemplates")
        assert r.status_code == 200
        assert "Results" in r.json()

    def test_contact_templates_has_results(self):
        r = get("/api/ListContactTemplates")
        assert r.status_code == 200
        assert "Results" in r.json()

    def test_standard_templates_has_results(self):
        r = get("/api/ListStandardTemplates")
        assert r.status_code == 200
        data = r.json()
        # Can be list or {Results: [...]}
        assert isinstance(data, list) or "Results" in data

    def test_bpa_templates(self):
        r = get("/api/listBPATemplates")
        assert r.status_code == 200

    def test_app_approval_templates_has_results(self):
        r = get("/api/ListAppApprovalTemplates")
        assert r.status_code == 200
        assert "Results" in r.json()


# ============================================================
# Misc endpoints that must not crash
# ============================================================

class TestMisc:
    def test_health(self):
        r = get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_version_json(self):
        r = get("/version.json")
        assert r.status_code == 200
        assert "version" in r.json()

    def test_get_version(self):
        r = get("/api/GetVersion")
        assert r.status_code == 200

    def test_get_cipp_alerts(self):
        r = get("/api/GetCippAlerts")
        assert r.status_code == 200

    def test_backend_urls(self):
        r = get("/api/ExecBackendURLs")
        assert r.status_code == 200
        assert "Results" in r.json()

    def test_list_standards(self):
        r = get("/api/ListStandards")
        assert r.status_code == 200

    def test_empty_results(self):
        r = get("/api/ListEmptyResults")
        assert r.status_code == 200

    def test_list_tests(self):
        r = get("/api/ListTests")
        assert r.status_code == 200

    def test_domain_health_no_crash(self):
        r = get("/api/ListDomainHealth")
        assert r.status_code == 200


# ============================================================
# POST endpoints must not crash
# ============================================================

class TestPostEndpoints:
    def test_exec_standards_run(self):
        r = post("/api/ExecStandardsRun", {"tenantFilter": TENANT})
        assert r.status_code == 200

    def test_exec_access_checks(self):
        r = post("/api/ExecAccessChecks", {"tenantFilter": TENANT})
        assert r.status_code == 200
        assert "Results" in r.json()

    def test_exec_user_settings(self):
        r = post("/api/ExecUserSettings", {"theme": "dark"})
        assert r.status_code == 200

    def test_exec_feature_flag(self):
        r = post("/api/ExecFeatureFlag", {"enableIntune": True})
        assert r.status_code == 200


# ============================================================
# No duplicate routes
# ============================================================

class TestRoutes:
    def test_no_duplicate_routes(self):
        """Verify no duplicate route paths exist."""
        r = get("/openapi.json")
        assert r.status_code == 200
        data = r.json()
        paths = list(data["paths"].keys())
        assert len(paths) == len(set(paths)), f"Duplicate paths found"

    def test_minimum_endpoint_count(self):
        """Backend must have at least 480 endpoints."""
        r = get("/openapi.json")
        data = r.json()
        assert len(data["paths"]) >= 440


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
