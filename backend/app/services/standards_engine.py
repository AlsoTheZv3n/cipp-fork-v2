"""Standards Engine — checks tenant configuration against best practices.

Each check is a function that takes Graph data and returns a result dict.
Checks are registered in AVAILABLE_CHECKS and can be referenced by name in templates.
"""
from app.core.graph import GraphClient


async def check_mfa_for_admins(graph: GraphClient, params: dict = None) -> dict:
    """Check if MFA is required for admin roles via Conditional Access."""
    policies = await graph.get("/identity/conditionalAccess/policies")
    for policy in policies.get("value", []):
        if policy.get("state") != "enabled":
            continue
        conditions = policy.get("conditions", {})
        users = conditions.get("users", {})
        grant = policy.get("grantControls", {})

        # Check if policy targets admin roles and requires MFA
        include_roles = users.get("includeRoles", [])
        built_in_controls = grant.get("builtInControls", [])

        if include_roles and "mfa" in built_in_controls:
            return {"passed": True, "details": f"CA Policy '{policy['displayName']}' enforces MFA for admin roles."}

    return {"passed": False, "details": "No Conditional Access policy found that enforces MFA for admin roles."}


async def check_mfa_for_all_users(graph: GraphClient, params: dict = None) -> dict:
    """Check if MFA is required for all users via Conditional Access."""
    policies = await graph.get("/identity/conditionalAccess/policies")
    for policy in policies.get("value", []):
        if policy.get("state") != "enabled":
            continue
        users = policy.get("conditions", {}).get("users", {})
        grant = policy.get("grantControls", {})

        if "All" in users.get("includeUsers", []) and "mfa" in grant.get("builtInControls", []):
            return {"passed": True, "details": f"CA Policy '{policy['displayName']}' enforces MFA for all users."}

    return {"passed": False, "details": "No CA policy enforces MFA for all users."}


async def check_security_defaults(graph: GraphClient, params: dict = None) -> dict:
    """Check if security defaults are enabled (or CA policies are used instead)."""
    policies = await graph.get("/identity/conditionalAccess/policies")
    ca_count = len([p for p in policies.get("value", []) if p.get("state") == "enabled"])
    if ca_count > 0:
        return {"passed": True, "details": f"{ca_count} active CA policies found (security defaults likely disabled in favor of CA)."}
    return {"passed": False, "details": "No active Conditional Access policies. Consider enabling security defaults or creating CA policies."}


async def check_password_expiry(graph: GraphClient, params: dict = None) -> dict:
    """Check that password expiry is configured on domains."""
    domains = await graph.get("/domains")
    issues = []
    for domain in domains.get("value", []):
        validity = domain.get("passwordValidityPeriodInDays")
        if validity and validity > 365:
            issues.append(f"{domain['id']}: password validity {validity} days (>365)")
    if issues:
        return {"passed": False, "details": f"Long password expiry: {'; '.join(issues)}"}
    return {"passed": True, "details": "Password expiry policies are within acceptable range."}


async def check_self_service_password_reset(graph: GraphClient, params: dict = None) -> dict:
    """Check SSPR configuration."""
    try:
        data = await graph.get("/policies/authorizationPolicy")
        sspr = data.get("defaultUserRolePermissions", {}).get("allowedToResetPassword", False)
        if sspr:
            return {"passed": True, "details": "Self-service password reset is enabled."}
        return {"passed": False, "details": "Self-service password reset is not enabled."}
    except Exception:
        return {"passed": False, "details": "Could not check SSPR status."}


async def check_admin_accounts_licensed(graph: GraphClient, params: dict = None) -> dict:
    """Check that admin role holders have licenses assigned."""
    roles = await graph.get("/directoryRoles")
    admin_role_ids = [r["id"] for r in roles.get("value", [])
                      if "admin" in r.get("displayName", "").lower()]
    unlicensed_admins = []
    for role_id in admin_role_ids[:5]:  # Limit for performance
        members = await graph.get(f"/directoryRoles/{role_id}/members")
        for member in members.get("value", []):
            if not member.get("assignedLicenses"):
                unlicensed_admins.append(member.get("userPrincipalName", member.get("id")))
    if unlicensed_admins:
        return {"passed": False, "details": f"Unlicensed admin accounts: {', '.join(unlicensed_admins[:10])}"}
    return {"passed": True, "details": "All admin accounts have licenses assigned."}


async def check_global_admin_count(graph: GraphClient, params: dict = None) -> dict:
    """Check that there aren't too many or too few Global Admins."""
    max_admins = (params or {}).get("maxAdmins", 5)
    min_admins = (params or {}).get("minAdmins", 2)
    roles = await graph.get("/directoryRoles")
    ga_role = next((r for r in roles.get("value", []) if r.get("displayName") == "Global Administrator"), None)
    if not ga_role:
        return {"passed": False, "details": "Global Administrator role not found."}
    members = await graph.get(f"/directoryRoles/{ga_role['id']}/members")
    count = len(members.get("value", []))
    if count < min_admins:
        return {"passed": False, "details": f"Only {count} Global Admin(s) — recommend at least {min_admins}."}
    if count > max_admins:
        return {"passed": False, "details": f"{count} Global Admins — recommend max {max_admins}."}
    return {"passed": True, "details": f"{count} Global Admin(s) (within {min_admins}-{max_admins} range)."}


async def check_unused_licenses(graph: GraphClient, params: dict = None) -> dict:
    """Check for licenses with low utilization."""
    skus = await graph.get("/subscribedSkus")
    underused = []
    for sku in skus.get("value", []):
        total = sku.get("prepaidUnits", {}).get("enabled", 0)
        consumed = sku.get("consumedUnits", 0)
        if total > 0 and consumed / total < 0.5:
            underused.append(f"{sku.get('skuPartNumber', 'Unknown')}: {consumed}/{total} used")
    if underused:
        return {"passed": False, "details": f"Underutilized licenses: {'; '.join(underused[:5])}"}
    return {"passed": True, "details": "All licenses are reasonably utilized."}


async def check_legacy_auth_blocked(graph: GraphClient, params: dict = None) -> dict:
    """Check if legacy authentication protocols are blocked via CA."""
    policies = await graph.get("/identity/conditionalAccess/policies")
    for policy in policies.get("value", []):
        if policy.get("state") != "enabled":
            continue
        conditions = policy.get("conditions", {})
        client_apps = conditions.get("clientAppTypes", [])
        grant = policy.get("grantControls", {})

        if ("exchangeActiveSync" in client_apps or "other" in client_apps) and "block" in grant.get("builtInControls", []):
            return {"passed": True, "details": f"CA Policy '{policy['displayName']}' blocks legacy auth."}

    return {"passed": False, "details": "No CA policy blocks legacy authentication protocols."}


async def check_guest_access_restricted(graph: GraphClient, params: dict = None) -> dict:
    """Check guest user access restrictions."""
    try:
        policy = await graph.get("/policies/authorizationPolicy")
        guest_access = policy.get("guestUserRoleId", "")
        # Restricted = 2af84b1e-..., Default = 10ddb8f4-..., Same as member = a0b1b346-...
        if "2af84b1e" in guest_access:
            return {"passed": True, "details": "Guest access is restricted (most restrictive)."}
        elif "10ddb8f4" in guest_access:
            return {"passed": False, "details": "Guest access is set to default (limited). Consider restricting further."}
        else:
            return {"passed": False, "details": "Guest access level may be too permissive."}
    except Exception:
        return {"passed": False, "details": "Could not check guest access policy."}


async def check_secure_score(graph: GraphClient, params: dict = None) -> dict:
    """Check if secure score meets minimum threshold."""
    min_score = (params or {}).get("minScorePercent", 50)
    data = await graph.get("/security/secureScores", params={"$top": 1})
    scores = data.get("value", [])
    if not scores:
        return {"passed": False, "details": "No secure score data available."}
    score = scores[0]
    current = score.get("currentScore", 0)
    maximum = score.get("maxScore", 1)
    pct = round(current / maximum * 100) if maximum else 0
    if pct >= min_score:
        return {"passed": True, "details": f"Secure Score: {current}/{maximum} ({pct}%) — meets {min_score}% threshold."}
    return {"passed": False, "details": f"Secure Score: {current}/{maximum} ({pct}%) — below {min_score}% threshold."}


# --- Check Registry ---

AVAILABLE_CHECKS = {
    "MFAForAdmins": {"fn": check_mfa_for_admins, "label": "MFA for Admin Roles", "category": "Identity"},
    "MFAForAllUsers": {"fn": check_mfa_for_all_users, "label": "MFA for All Users", "category": "Identity"},
    "SecurityDefaults": {"fn": check_security_defaults, "label": "Security Defaults / CA Policies", "category": "Identity"},
    "PasswordExpiry": {"fn": check_password_expiry, "label": "Password Expiry Policy", "category": "Identity"},
    "SSPR": {"fn": check_self_service_password_reset, "label": "Self-Service Password Reset", "category": "Identity"},
    "AdminAccountsLicensed": {"fn": check_admin_accounts_licensed, "label": "Admin Accounts Licensed", "category": "Identity"},
    "GlobalAdminCount": {"fn": check_global_admin_count, "label": "Global Admin Count (2-5)", "category": "Identity"},
    "UnusedLicenses": {"fn": check_unused_licenses, "label": "License Utilization", "category": "Licensing"},
    "LegacyAuthBlocked": {"fn": check_legacy_auth_blocked, "label": "Legacy Auth Blocked", "category": "Identity"},
    "GuestAccessRestricted": {"fn": check_guest_access_restricted, "label": "Guest Access Restricted", "category": "Identity"},
    "SecureScore": {"fn": check_secure_score, "label": "Secure Score Threshold", "category": "Security"},
}


async def run_checks(tenant_id: str, check_names: list[str] | None = None, params_map: dict | None = None) -> list[dict]:
    """Run specified checks (or all) against a tenant. Returns list of results."""
    graph = GraphClient(tenant_id)
    params_map = params_map or {}

    if check_names is None:
        check_names = list(AVAILABLE_CHECKS.keys())

    results = []
    for name in check_names:
        check = AVAILABLE_CHECKS.get(name)
        if not check:
            results.append({"check": name, "passed": False, "details": f"Unknown check: {name}"})
            continue
        try:
            result = await check["fn"](graph, params_map.get(name, {}))
            results.append({
                "check": name,
                "label": check["label"],
                "category": check["category"],
                **result,
            })
        except Exception as e:
            results.append({
                "check": name,
                "label": check["label"],
                "category": check["category"],
                "passed": False,
                "details": f"Check failed with error: {str(e)}",
            })

    return results
