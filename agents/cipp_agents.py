"""CIPP AI Agent Team — automated testing, fixing, and compatibility checking.

Usage:
    python agents/cipp_agents.py                    # Quick audit (no AI)
    python agents/cipp_agents.py --quick            # Quick format check
    python agents/cipp_agents.py --full             # Full AI-powered audit
    python agents/cipp_agents.py --fix              # AI audit + auto-fix
    python agents/cipp_agents.py --test-only        # Just run pytest
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.tools import (
    api_get,
    api_post,
    check_frontend_page,
    check_response_format,
    list_endpoints,
    read_file,
    run_test_suite,
    search_files,
    write_file,
)


def create_tester_agent():
    """Create the API Tester agent."""
    from agno.agent import Agent
    from agno.models.anthropic import Claude

    return Agent(
        name="CIPP API Tester",
        model=Claude(id="claude-sonnet-4-20250514"),
        description="Tests CIPP API endpoints for health and response format compatibility.",
        instructions="""You are the CIPP API Tester. Test endpoints and report issues.

The CIPP frontend expects:
- CippTablePage endpoints (90%): {Results: [...], Metadata: {nextLink?}}
- Dashboard (ListOrg, ListuserCounts): direct objects
- Auth (/.auth/me, /api/me): {clientPrincipal: {...}}
- Dropdowns (ListTenants): direct arrays
- ExecAlertsList: {Results: {MSResults: [...]}} (nested!)
- ListFeatureFlags: [{Enabled: bool, Pages: [...]}] (array of flag objects)

Use tenantFilter=demo-tenant-contoso for testing.""",
        tools=[api_get, api_post, check_response_format, list_endpoints, run_test_suite],
        markdown=True,
    )


def create_checker_agent():
    """Create the Compatibility Checker agent."""
    from agno.agent import Agent
    from agno.models.anthropic import Claude

    return Agent(
        name="CIPP Compatibility Checker",
        model=Claude(id="claude-sonnet-4-20250514"),
        description="Checks frontend-backend compatibility by reading source code.",
        instructions="""You check CIPP frontend-backend compatibility.

Read frontend files to see what format they expect.
Read backend files to see what format they return.
Report mismatches with file:line references.

Key patterns:
- CippTablePage: apiDataKey="Results" → needs {Results: [...]}
- .data?.Results → needs {Results: ...}
- .data || [] → needs direct array
- .data?.displayName → needs direct object""",
        tools=[read_file, search_files, api_get, check_response_format],
        markdown=True,
    )


def create_fixer_agent():
    """Create the Auto Fixer agent."""
    from agno.agent import Agent
    from agno.models.anthropic import Claude

    return Agent(
        name="CIPP Auto Fixer",
        model=Claude(id="claude-sonnet-4-20250514"),
        description="Fixes backend code to match frontend expectations.",
        instructions="""You fix CIPP backend response format issues.

Rules:
- Only modify backend/app/routers/ and backend/app/core/
- Keep changes minimal
- Test after fixing
- Common fixes: wrap arrays in {Results: [...]}, add error handling""",
        tools=[read_file, write_file, api_get, check_response_format, search_files],
        markdown=True,
    )


# --- Quick Audit (no AI needed) ---

def run_quick_audit():
    """Run a quick audit of critical endpoints."""
    print("=" * 60)
    print("  CIPP Quick Compatibility Audit")
    print("=" * 60)

    T = os.getenv("CIPP_TEST_TENANT", "demo-tenant-contoso")

    checks = [
        # (path, expected_format, params, description)
        ("/api/health", "direct_object", None, "Health check"),
        ("/.auth/me", "direct_object", None, "Auth session"),

        # Dashboard — direct objects
        ("/api/ListOrg", "direct_object", {"tenantFilter": T}, "Dashboard: Org info"),
        ("/api/ListuserCounts", "direct_object", {"tenantFilter": T}, "Dashboard: User counts"),
        ("/api/ListTests", "direct_object", {"tenantFilter": T}, "Dashboard V2: Test results"),

        # Dropdowns — direct arrays
        ("/api/ListTenants", "direct_array", None, "Tenant dropdown"),
        ("/api/tenantFilter", "direct_array", None, "Tenant filter dropdown"),
        ("/api/ListTestReports", "direct_array", None, "Report dropdown"),
        ("/api/ListTenantGroups", "direct_array", None, "Tenant groups dropdown"),

        # Settings — direct objects/arrays
        ("/api/ListFeatureFlags", "direct_object", None, "Feature flags"),
        ("/api/ListUserSettings", "direct_object", None, "User settings"),

        # CippTablePage endpoints — must be {Results: [...]}
        ("/api/ListUsers", "results_array", {"tenantFilter": T}, "Users table"),
        ("/api/ListGroups", "results_array", {"tenantFilter": T}, "Groups table"),
        ("/api/ListDevices", "results_array", {"tenantFilter": T}, "Devices table"),
        ("/api/ListConditionalAccessPolicies", "results_array", {"tenantFilter": T}, "CA Policies table"),
        ("/api/ListRoles", "results_array", {"tenantFilter": T}, "Roles table"),
        ("/api/ListLicenses", "results_array", {"tenantFilter": T}, "Licenses table"),
        ("/api/ListDomains", "results_array", {"tenantFilter": T}, "Domains table"),
        ("/api/ListContacts", "results_array", {"tenantFilter": T}, "Contacts table"),
        ("/api/ListMFAUsers", "results_array", {"tenantFilter": T}, "MFA Users table"),
        ("/api/ListSignIns", "results_array", {"tenantFilter": T}, "Sign-ins table"),
        ("/api/ListAuditLogs", "results_array", {"tenantFilter": T}, "Audit logs table"),
        ("/api/ListNamedLocations", "results_array", {"tenantFilter": T}, "Named locations table"),
        ("/api/ExecAlertsList", "results_array", {"tenantFilter": T}, "Alerts table"),
        ("/api/ExecIncidentsList", "results_array", {"tenantFilter": T}, "Incidents table"),
        ("/api/ListOAuthApps", "results_array", {"tenantFilter": T}, "OAuth apps table"),
        ("/api/ListAPDevices", "results_array", {"tenantFilter": T}, "Autopilot devices"),
        ("/api/ListApps", "results_array", {"tenantFilter": T}, "Intune apps"),
        ("/api/ListCompliancePolicies", "results_array", {"tenantFilter": T}, "Compliance policies"),
        ("/api/ListSites", "results_array", {"tenantFilter": T}, "SharePoint sites"),

        # Graph proxy
        ("/api/ListGraphRequest", "results_array", {"tenantFilter": T, "Endpoint": "users", "$top": "1"}, "Graph proxy"),

        # Standards
        ("/api/ListStandards", "direct_array", None, "Standards list"),
        ("/api/ListStandardTemplates", "direct_array", None, "Standard templates"),
    ]

    passed = 0
    failed = 0
    errors = []

    for path, expected, params, desc in checks:
        result = check_response_format(path, expected, params)
        status = "PASS" if result["ok"] else "FAIL"
        symbol = "OK" if result["ok"] else "!!"

        if result["ok"]:
            passed += 1
            print(f"  {symbol} {desc:40s} {path}")
        else:
            failed += 1
            errors.append({**result, "desc": desc})
            print(f"  {symbol} {desc:40s} {path}")
            print(f"    Expected: {result['expected']}, Got: {result['actual']}")

    print()
    print("=" * 60)
    print(f"  Results: {passed} passed, {failed} failed out of {passed+failed}")
    print("=" * 60)

    if errors:
        print("\n  Issues to fix:")
        for e in errors:
            print(f"    - {e['desc']}: {e['path']} (expected {e['expected']}, got {e['actual']})")

    return {"passed": passed, "failed": failed, "errors": errors}


def run_full_audit():
    """Run AI-powered full audit."""
    agent = create_tester_agent()
    agent.print_response(
        "Run a comprehensive audit of the CIPP API. "
        "Test these critical endpoint categories:\n"
        "1. Dashboard endpoints (ListOrg, ListuserCounts, ListTests)\n"
        "2. CippTablePage endpoints (ListUsers, ListGroups, etc.) — need {Results: [...]}\n"
        "3. Auth endpoints (/.auth/me, /api/me)\n"
        "4. ListGraphRequest with various Endpoints\n"
        "5. Feature flags and settings\n"
        "Report all issues with specific details.",
        stream=True,
    )


def run_with_fixes():
    """Run audit then fix issues."""
    # First audit
    print("Phase 1: Running quick audit...")
    audit = run_quick_audit()

    if not audit["errors"]:
        print("\nNo issues found!")
        return

    print(f"\nPhase 2: Fixing {len(audit['errors'])} issues with AI agent...")
    fixer = create_fixer_agent()
    issues = "\n".join(f"- {e['desc']}: {e['path']} expected {e['expected']}, got {e['actual']}" for e in audit["errors"])
    fixer.print_response(
        f"Fix these CIPP API compatibility issues:\n{issues}\n\n"
        "Read the affected backend router files, make minimal fixes, and test each endpoint after.",
        stream=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CIPP AI Agent Team")
    parser.add_argument("--fix", action="store_true", help="Audit + auto-fix issues")
    parser.add_argument("--test-only", action="store_true", help="Just run pytest suite")
    parser.add_argument("--quick", action="store_true", help="Quick format check (no AI)")
    parser.add_argument("--full", action="store_true", help="Full AI-powered audit")
    args = parser.parse_args()

    if args.test_only:
        result = run_test_suite()
        print(json.dumps(result, indent=2))
    elif args.full:
        run_full_audit()
    elif args.fix:
        run_with_fixes()
    else:
        run_quick_audit()
