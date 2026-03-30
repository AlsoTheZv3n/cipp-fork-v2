"""Test that ALL frontend pages return non-500 responses.

Run: cd backend && PYTHONPATH=. python -m pytest tests/test_frontend_pages.py -v
Requires: frontend running on http://localhost:3001
"""
import pytest

# ===========================================================================
# All page paths derived from src/pages/ directory structure
# Excludes _app, _document, and other Next.js internal files
# ===========================================================================

FRONTEND_PAGES = [
    # Root pages
    "/",
    "/dashboardv1",
    "/dashboardv2",
    "/dashboardv2/devices",
    "/dashboardv2/identity",
    "/license",
    "/onboarding",
    "/onboardingv2",
    "/unauthenticated",

    # Identity - Administration
    "/identity/administration",
    "/identity/administration/users",
    "/identity/administration/users/add",
    "/identity/administration/users/bulk-add",
    "/identity/administration/users/patch-wizard",
    "/identity/administration/groups",
    "/identity/administration/groups/add",
    "/identity/administration/groups/edit",
    "/identity/administration/devices",
    "/identity/administration/deleted-items",
    "/identity/administration/roles",
    "/identity/administration/offboarding-wizard",
    "/identity/administration/risky-users",
    "/identity/administration/deploy-group-template",
    "/identity/administration/group-templates",
    "/identity/administration/group-templates/add",
    "/identity/administration/group-templates/deploy",
    "/identity/administration/group-templates/edit",
    "/identity/administration/jit-admin",
    "/identity/administration/jit-admin/add",
    "/identity/administration/jit-admin-templates",
    "/identity/administration/jit-admin-templates/add",
    "/identity/administration/jit-admin-templates/edit",
    "/identity/administration/vacation-mode",
    "/identity/administration/vacation-mode/add",

    # Identity - Reports
    "/identity/reports",
    "/identity/reports/mfa-report",
    "/identity/reports/inactive-users-report",
    "/identity/reports/signin-report",
    "/identity/reports/azure-ad-connect-report",
    "/identity/reports/risk-detections",

    # Tenant - Administration
    "/tenant/administration",
    "/tenant/administration/tenants",
    "/tenant/administration/tenants/add",
    "/tenant/administration/tenants/edit",
    "/tenant/administration/tenants/global-variables",
    "/tenant/administration/tenants/groups",
    "/tenant/administration/tenants/groups/edit",
    "/tenant/administration/domains",
    "/tenant/administration/applications/app-registrations",
    "/tenant/administration/applications/enterprise-apps",
    "/tenant/administration/applications/permission-sets",
    "/tenant/administration/applications/permission-sets/add",
    "/tenant/administration/applications/permission-sets/edit",
    "/tenant/administration/applications/templates",
    "/tenant/administration/applications/templates/add",
    "/tenant/administration/applications/templates/edit",
    "/tenant/administration/alert-configuration",
    "/tenant/administration/alert-configuration/alert",
    "/tenant/administration/add-subscription",
    "/tenant/administration/securescore",
    "/tenant/administration/securescore/table",
    "/tenant/administration/tenantlookup",
    "/tenant/administration/partner-relationships",
    "/tenant/administration/audit-logs",
    "/tenant/administration/audit-logs/directory-audits",
    "/tenant/administration/audit-logs/log",
    "/tenant/administration/audit-logs/searches",
    "/tenant/administration/audit-logs/search-results",
    "/tenant/administration/authentication-methods",
    "/tenant/administration/app-consent-requests",

    # Tenant - Manage
    "/tenant/manage/applied-standards",
    "/tenant/manage/configuration-backup",
    "/tenant/manage/drift",
    "/tenant/manage/driftManagementActions",
    "/tenant/manage/edit",
    "/tenant/manage/history",
    "/tenant/manage/policies-deployed",
    "/tenant/manage/user-defaults",

    # Tenant - Conditional
    "/tenant/conditional/list-policies",
    "/tenant/conditional/list-template",
    "/tenant/conditional/list-template/edit",
    "/tenant/conditional/list-named-locations",
    "/tenant/conditional/list-named-locations/add",
    "/tenant/conditional/deploy-vacation",
    "/tenant/conditional/deploy-vacation/add",

    # Tenant - Backup
    "/tenant/backup/backup-wizard",
    "/tenant/backup/backup-wizard/add",
    "/tenant/backup/backup-wizard/restore",

    # Tenant - GDAP Management
    "/tenant/gdap-management",
    "/tenant/gdap-management/relationships",
    "/tenant/gdap-management/invites",
    "/tenant/gdap-management/invites/add",
    "/tenant/gdap-management/roles",
    "/tenant/gdap-management/roles/add",
    "/tenant/gdap-management/role-templates",
    "/tenant/gdap-management/role-templates/add",
    "/tenant/gdap-management/role-templates/edit",
    "/tenant/gdap-management/onboarding",
    "/tenant/gdap-management/onboarding/start",
    "/tenant/gdap-management/offboarding",

    # Tenant - Standards
    "/tenant/standards/alignment",
    "/tenant/standards/bpa-report",
    "/tenant/standards/bpa-report/builder",
    "/tenant/standards/bpa-report/view",
    "/tenant/standards/domains-analyser",
    "/tenant/standards/templates",
    "/tenant/standards/templates/template",

    # Tenant - Reports
    "/tenant/reports",
    "/tenant/reports/list-licenses",
    "/tenant/reports/list-csp-licenses",
    "/tenant/reports/application-consent",

    # Tenant - Tools
    "/tenant/tools/graph-explorer",
    "/tenant/tools/tenantlookup",
    "/tenant/tools/geoiplookup",
    "/tenant/tools/individual-domains",
    "/tenant/tools/bpa-report-builder",
    "/tenant/tools/appapproval",

    # Email - Administration
    "/email/administration/mailboxes",
    "/email/administration/mailboxes/addshared",
    "/email/administration/contacts",
    "/email/administration/contacts/edit",
    "/email/administration/contacts-template",
    "/email/administration/contacts-template/add",
    "/email/administration/contacts-template/edit",
    "/email/administration/quarantine",
    "/email/administration/deleted-mailboxes",
    "/email/administration/mailbox-rules",
    "/email/administration/restricted-users",
    "/email/administration/tenant-allow-block-lists",
    "/email/administration/exchange-retention/policies",
    "/email/administration/exchange-retention/policies/policy",
    "/email/administration/exchange-retention/tags",
    "/email/administration/exchange-retention/tags/tag",

    # Email - Reports
    "/email/reports/mailbox-statistics",
    "/email/reports/mailbox-cas-settings",
    "/email/reports/mailbox-permissions",
    "/email/reports/mailbox-forwarding",
    "/email/reports/mailbox-activity",
    "/email/reports/calendar-permissions",
    "/email/reports/global-address-list",
    "/email/reports/SharedMailboxEnabledAccount",
    "/email/reports/antiphishing-filters",
    "/email/reports/malware-filters",
    "/email/reports/safeattachments-filters",

    # Email - Resources
    "/email/resources/management/equipment",
    "/email/resources/management/equipment/edit",
    "/email/resources/management/list-rooms",
    "/email/resources/management/list-rooms/edit",
    "/email/resources/management/room-lists",
    "/email/resources/management/room-lists/edit",

    # Email - Spam filter
    "/email/spamfilter/list-spamfilter",
    "/email/spamfilter/list-spamfilter/add",
    "/email/spamfilter/list-connectionfilter",
    "/email/spamfilter/list-connectionfilter/add",
    "/email/spamfilter/list-connectionfilter-templates",
    "/email/spamfilter/list-quarantine-policies",
    "/email/spamfilter/list-quarantine-policies/add",
    "/email/spamfilter/list-templates",

    # Email - Transport
    "/email/transport/list-rules",
    "/email/transport/list-connectors",
    "/email/transport/list-templates",
    "/email/transport/list-connector-templates",

    # Email - Tools
    "/email/tools/message-trace",
    "/email/tools/message-viewer",
    "/email/tools/mail-test",
    "/email/tools/mailbox-restores",
    "/email/tools/mailbox-restores/add",
    "/email/tools/mailbox-restore-wizard",

    # Security
    "/security/defender/list-defender",
    "/security/defender/list-defender-tvm",
    "/security/defender/deployment",
    "/security/incidents/list-alerts",
    "/security/incidents/list-incidents",
    "/security/incidents/list-check-alerts",
    "/security/incidents/list-mdo-alerts",
    "/security/reports/list-device-compliance",
    "/security/safelinks/safelinks",
    "/security/safelinks/safelinks/add",
    "/security/safelinks/safelinks/edit",
    "/security/safelinks/safelinks-template",
    "/security/safelinks/safelinks-template/add",
    "/security/safelinks/safelinks-template/create",
    "/security/safelinks/safelinks-template/edit",

    # Endpoint - MEM
    "/endpoint/MEM/devices",
    "/endpoint/MEM/list-policies",
    "/endpoint/MEM/list-compliance-policies",
    "/endpoint/MEM/list-appprotection-policies",
    "/endpoint/MEM/list-scripts",
    "/endpoint/MEM/list-templates",
    "/endpoint/MEM/list-templates/edit",
    "/endpoint/MEM/assignment-filters",
    "/endpoint/MEM/assignment-filters/add",
    "/endpoint/MEM/assignment-filters/edit",
    "/endpoint/MEM/assignment-filter-templates",
    "/endpoint/MEM/assignment-filter-templates/add",
    "/endpoint/MEM/assignment-filter-templates/deploy",
    "/endpoint/MEM/assignment-filter-templates/edit",
    "/endpoint/MEM/reusable-settings",
    "/endpoint/MEM/reusable-settings/edit",
    "/endpoint/MEM/reusable-settings-templates",
    "/endpoint/MEM/reusable-settings-templates/add",
    "/endpoint/MEM/reusable-settings-templates/edit",

    # Endpoint - Applications
    "/endpoint/applications/list",
    "/endpoint/applications/queue",

    # Endpoint - Autopilot
    "/endpoint/autopilot/add-device",
    "/endpoint/autopilot/list-devices",
    "/endpoint/autopilot/list-profiles",
    "/endpoint/autopilot/list-status-pages",

    # Endpoint - Reports
    "/endpoint/reports/analyticsdevicescore",
    "/endpoint/reports/autopilot-deployment",
    "/endpoint/reports/detected-apps",
    "/endpoint/reports/workfromanywhere",

    # Teams & SharePoint
    "/teams-share/onedrive",
    "/teams-share/sharepoint",
    "/teams-share/sharepoint/add-site",
    "/teams-share/sharepoint/bulk-add-site",
    "/teams-share/teams/list-team",
    "/teams-share/teams/list-team/add",
    "/teams-share/teams/teams-activity",
    "/teams-share/teams/business-voice",

    # CIPP Settings
    "/cipp/settings",
    "/cipp/settings/backend",
    "/cipp/settings/backup",
    "/cipp/settings/features",
    "/cipp/settings/licenses",
    "/cipp/settings/notifications",
    "/cipp/settings/partner-webhooks",
    "/cipp/settings/password-config",
    "/cipp/settings/permissions",
    "/cipp/settings/siem",
    "/cipp/settings/tenants",

    # CIPP Advanced
    "/cipp/advanced/diagnostics",
    "/cipp/advanced/exchange-cmdlets",
    "/cipp/advanced/table-maintenance",
    "/cipp/advanced/timers",

    # CIPP Logs / Scheduler
    "/cipp/logs",
    "/cipp/scheduler",

    # CIPP Super Admin
    "/cipp/super-admin/cipp-roles",
    "/cipp/super-admin/cipp-roles/add",
    "/cipp/super-admin/cipp-roles/edit",
    "/cipp/super-admin/sam-app-permissions",
    "/cipp/super-admin/sam-app-roles",
    "/cipp/super-admin/function-offloading",
    "/cipp/super-admin/jit-admin-settings",
    "/cipp/super-admin/tenant-mode",
    "/cipp/super-admin/time-settings",

    # CIPP Other
    "/cipp/preferences",
    "/cipp/statistics",
    "/cipp/integrations",
    "/cipp/integrations/configure",
    "/cipp/integrations/sync",
    "/cipp/extension-sync",
    "/cipp/custom-data/directory-extensions",
    "/cipp/custom-data/directory-extensions/add",
    "/cipp/custom-data/mappings",
    "/cipp/custom-data/mappings/add",
    "/cipp/custom-data/mappings/edit",
    "/cipp/custom-data/schema-extensions",
    "/cipp/custom-data/schema-extensions/add",

    # Tools
    "/tools/breachlookup",
    "/tools/tenantbreachlookup",
    "/tools/community-repos",
    "/tools/templatelib",
]


@pytest.mark.parametrize("page_path", FRONTEND_PAGES)
def test_frontend_page(frontend_client, page_path):
    """Every frontend page should return 200 or 302 (redirect), never 500."""
    try:
        r = frontend_client.get(page_path)
    except Exception as e:
        pytest.skip(f"Could not connect to frontend: {e}")
    assert r.status_code < 500, (
        f"Frontend page {page_path} returned {r.status_code}"
    )
