"""CIPP MCP Server — allows AI assistants to manage M365 tenants via CIPP.

Run: python mcp_server.py
Or configure in claude_desktop_config.json / .claude/settings.json
"""
import asyncio
import os
import sys

# Add backend to path so we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP

# Initialize the CIPP backend modules
from app.core.config import settings
from app.core.graph import GraphClient
from app.services.standards_engine import AVAILABLE_CHECKS, run_checks

mcp = FastMCP(
    "CIPP",
    instructions="M365 Multi-Tenant Management — manage users, tenants, security, devices, and compliance via Microsoft Graph API.",
)


# ============================================================
# Tenant Management
# ============================================================

@mcp.tool()
async def list_tenants() -> str:
    """List all onboarded M365 tenants from the CIPP database."""
    from sqlalchemy import select
    from app.core.database import async_session
    from app.models.tenant import Tenant

    async with async_session() as session:
        result = await session.execute(select(Tenant).where(Tenant.is_active.is_(True)))
        tenants = result.scalars().all()
        if not tenants:
            return "No tenants onboarded yet. Use onboard_tenant to add one."
        lines = [f"# Onboarded Tenants ({len(tenants)})\n"]
        for t in tenants:
            lines.append(f"- **{t.display_name}** ({t.default_domain}) — ID: `{t.tenant_id}`")
        return "\n".join(lines)


@mcp.tool()
async def onboard_tenant(tenant_id: str) -> str:
    """Onboard a new M365 tenant by verifying Graph API access and saving to DB.

    Args:
        tenant_id: The Azure AD tenant ID or primary domain (e.g. contoso.onmicrosoft.com)
    """
    from sqlalchemy import select
    from app.core.database import async_session
    from app.models.tenant import Tenant

    graph = GraphClient(tenant_id)
    try:
        org = await graph.get("/organization")
        org_data = org.get("value", [{}])[0]
        display_name = org_data.get("displayName", tenant_id)
        domains = await graph.get("/domains")
        default_domain = next(
            (d["id"] for d in domains.get("value", []) if d.get("isDefault")), tenant_id
        )
    except Exception as e:
        return f"Failed to access tenant {tenant_id}: {str(e)}"

    async with async_session() as session:
        result = await session.execute(select(Tenant).where(Tenant.tenant_id == tenant_id))
        existing = result.scalar_one_or_none()
        if existing:
            existing.display_name = display_name
            existing.default_domain = default_domain
            existing.is_active = True
        else:
            session.add(Tenant(tenant_id=tenant_id, display_name=display_name, default_domain=default_domain))
        await session.commit()

    return f"Tenant **{display_name}** ({default_domain}) onboarded successfully."


@mcp.tool()
async def get_tenant_details(tenant_id: str) -> str:
    """Get detailed information about a tenant: organization, domains, licenses.

    Args:
        tenant_id: The tenant ID or domain
    """
    graph = GraphClient(tenant_id)
    org = await graph.get("/organization")
    org_data = org.get("value", [{}])[0] if org.get("value") else {}
    domains = await graph.get("/domains")
    skus = await graph.get("/subscribedSkus")

    lines = [f"# Tenant: {org_data.get('displayName', tenant_id)}\n"]
    lines.append(f"**Tenant ID:** {org_data.get('id', 'N/A')}")
    lines.append(f"**Created:** {org_data.get('createdDateTime', 'N/A')}")
    lines.append(f"**AD Sync:** {'Yes' if org_data.get('onPremisesSyncEnabled') else 'No'}")

    lines.append(f"\n## Domains ({len(domains.get('value', []))})")
    for d in domains.get("value", []):
        default = " (default)" if d.get("isDefault") else ""
        lines.append(f"- {d['id']}{default}")

    lines.append(f"\n## Licenses ({len(skus.get('value', []))})")
    for sku in skus.get("value", []):
        total = sku.get("prepaidUnits", {}).get("enabled", 0)
        consumed = sku.get("consumedUnits", 0)
        lines.append(f"- **{sku.get('skuPartNumber', 'Unknown')}**: {consumed}/{total} used")

    return "\n".join(lines)


# ============================================================
# User Management
# ============================================================

@mcp.tool()
async def list_users(tenant_id: str, top: int = 50) -> str:
    """List users in a tenant with key details.

    Args:
        tenant_id: The tenant ID or domain
        top: Maximum number of users to return (default 50)
    """
    graph = GraphClient(tenant_id)
    data = await graph.get("/users", params={
        "$select": "id,displayName,userPrincipalName,accountEnabled,assignedLicenses,userType",
        "$top": top,
    })
    users = data.get("value", [])
    lines = [f"# Users in {tenant_id} ({len(users)})\n"]
    lines.append("| Name | UPN | Enabled | Licensed | Type |")
    lines.append("|------|-----|---------|----------|------|")
    for u in users:
        enabled = "Yes" if u.get("accountEnabled") else "No"
        licensed = "Yes" if u.get("assignedLicenses") else "No"
        utype = u.get("userType", "Member")
        lines.append(f"| {u.get('displayName', '')} | {u.get('userPrincipalName', '')} | {enabled} | {licensed} | {utype} |")
    return "\n".join(lines)


@mcp.tool()
async def get_user(tenant_id: str, user_id: str) -> str:
    """Get detailed information about a specific user.

    Args:
        tenant_id: The tenant ID or domain
        user_id: The user ID or UPN (e.g. user@domain.com)
    """
    graph = GraphClient(tenant_id)
    user = await graph.get(f"/users/{user_id}", params={
        "$select": "id,displayName,userPrincipalName,mail,accountEnabled,assignedLicenses,userType,createdDateTime,lastSignInDateTime,jobTitle,department,city,onPremisesSyncEnabled"
    })
    lines = [f"# User: {user.get('displayName', 'Unknown')}\n"]
    lines.append(f"**UPN:** {user.get('userPrincipalName', 'N/A')}")
    lines.append(f"**Email:** {user.get('mail', 'N/A')}")
    lines.append(f"**Enabled:** {user.get('accountEnabled', 'N/A')}")
    lines.append(f"**Type:** {user.get('userType', 'N/A')}")
    lines.append(f"**Job Title:** {user.get('jobTitle', 'N/A')}")
    lines.append(f"**Department:** {user.get('department', 'N/A')}")
    lines.append(f"**Created:** {user.get('createdDateTime', 'N/A')}")
    lines.append(f"**Last Sign-in:** {user.get('lastSignInDateTime', 'N/A')}")
    lines.append(f"**AD Sync:** {'Yes' if user.get('onPremisesSyncEnabled') else 'No'}")
    lines.append(f"**Licenses:** {len(user.get('assignedLicenses', []))}")
    return "\n".join(lines)


@mcp.tool()
async def create_user(
    tenant_id: str,
    display_name: str,
    user_principal_name: str,
    password: str,
    mail_nickname: str = "",
) -> str:
    """Create a new user in a tenant.

    Args:
        tenant_id: The tenant ID or domain
        display_name: The user's display name
        user_principal_name: The UPN (e.g. john@contoso.com)
        password: Initial password
        mail_nickname: Mail nickname (defaults to part before @)
    """
    graph = GraphClient(tenant_id)
    if not mail_nickname:
        mail_nickname = user_principal_name.split("@")[0]
    result = await graph.post("/users", {
        "displayName": display_name,
        "userPrincipalName": user_principal_name,
        "mailNickname": mail_nickname,
        "passwordProfile": {"password": password, "forceChangePasswordNextSignIn": True},
        "accountEnabled": True,
    })
    return f"User **{display_name}** ({user_principal_name}) created successfully. ID: `{result.get('id', '')}`"


@mcp.tool()
async def disable_user(tenant_id: str, user_id: str) -> str:
    """Disable a user account (block sign-in).

    Args:
        tenant_id: The tenant ID or domain
        user_id: The user ID or UPN
    """
    graph = GraphClient(tenant_id)
    await graph.patch(f"/users/{user_id}", {"accountEnabled": False})
    return f"User {user_id} has been disabled."


@mcp.tool()
async def reset_password(tenant_id: str, user_id: str, new_password: str = "") -> str:
    """Reset a user's password. Generates a random password if none provided.

    Args:
        tenant_id: The tenant ID or domain
        user_id: The user ID or UPN
        new_password: New password (optional, random if empty)
    """
    import secrets
    if not new_password:
        new_password = secrets.token_urlsafe(16) + "!1"
    graph = GraphClient(tenant_id)
    await graph.patch(f"/users/{user_id}", {
        "passwordProfile": {"password": new_password, "forceChangePasswordNextSignIn": True}
    })
    return f"Password reset for {user_id}. New password: `{new_password}` (must change on next sign-in)."


@mcp.tool()
async def offboard_user(tenant_id: str, user_id: str, remove_licenses: bool = True) -> str:
    """Full user offboarding: disable, revoke sessions, optionally remove licenses.

    Args:
        tenant_id: The tenant ID or domain
        user_id: The user ID or UPN
        remove_licenses: Whether to remove all licenses (default True)
    """
    graph = GraphClient(tenant_id)
    steps = []

    await graph.patch(f"/users/{user_id}", {"accountEnabled": False})
    steps.append("Account disabled")

    try:
        await graph.post(f"/users/{user_id}/revokeSignInSessions", {})
        steps.append("Sessions revoked")
    except Exception:
        steps.append("Session revocation failed")

    if remove_licenses:
        try:
            user = await graph.get(f"/users/{user_id}", params={"$select": "assignedLicenses"})
            sku_ids = [lic["skuId"] for lic in user.get("assignedLicenses", [])]
            if sku_ids:
                await graph.post(f"/users/{user_id}/assignLicense", {"addLicenses": [], "removeLicenses": sku_ids})
                steps.append(f"Removed {len(sku_ids)} license(s)")
        except Exception:
            steps.append("License removal failed")

    return f"User {user_id} offboarded. Steps: {', '.join(steps)}."


# ============================================================
# Security
# ============================================================

@mcp.tool()
async def get_security_alerts(tenant_id: str, top: int = 20) -> str:
    """Get recent security alerts for a tenant.

    Args:
        tenant_id: The tenant ID or domain
        top: Maximum number of alerts (default 20)
    """
    graph = GraphClient(tenant_id)
    data = await graph.get("/security/alerts_v2", params={"$top": top, "$orderby": "createdDateTime desc"})
    alerts = data.get("value", [])
    if not alerts:
        return f"No security alerts found for {tenant_id}."
    lines = [f"# Security Alerts ({len(alerts)})\n"]
    for a in alerts:
        severity = a.get("severity", "unknown")
        status = a.get("status", "unknown")
        lines.append(f"- **[{severity.upper()}]** {a.get('title', 'Untitled')} — Status: {status} ({a.get('createdDateTime', '')[:10]})")
    return "\n".join(lines)


@mcp.tool()
async def get_risky_users(tenant_id: str) -> str:
    """List risky users from Identity Protection.

    Args:
        tenant_id: The tenant ID or domain
    """
    graph = GraphClient(tenant_id)
    data = await graph.get("/identityProtection/riskyUsers", params={"$top": 50})
    users = data.get("value", [])
    if not users:
        return f"No risky users found for {tenant_id}."
    lines = [f"# Risky Users ({len(users)})\n"]
    lines.append("| User | Risk Level | Risk State | Last Updated |")
    lines.append("|------|-----------|-----------|--------------|")
    for u in users:
        lines.append(f"| {u.get('userDisplayName', 'Unknown')} | {u.get('riskLevel', 'none')} | {u.get('riskState', 'none')} | {str(u.get('riskLastUpdatedDateTime', ''))[:10]} |")
    return "\n".join(lines)


@mcp.tool()
async def get_secure_score(tenant_id: str) -> str:
    """Get the current Microsoft Secure Score for a tenant.

    Args:
        tenant_id: The tenant ID or domain
    """
    graph = GraphClient(tenant_id)
    data = await graph.get("/security/secureScores", params={"$top": 1})
    scores = data.get("value", [])
    if not scores:
        return "No secure score data available."
    score = scores[0]
    current = score.get("currentScore", 0)
    maximum = score.get("maxScore", 1)
    pct = round(current / maximum * 100) if maximum else 0
    lines = [f"# Secure Score: {current}/{maximum} ({pct}%)\n"]
    controls = score.get("controlScores", [])
    if controls:
        lines.append("## Top Improvement Actions")
        not_achieved = [c for c in controls if c.get("scoreInPercentage", 100) < 100]
        not_achieved.sort(key=lambda c: c.get("scoreInPercentage", 0))
        for c in not_achieved[:10]:
            lines.append(f"- **{c.get('controlName', '')}**: {c.get('scoreInPercentage', 0)}% — {c.get('description', '')[:80]}")
    return "\n".join(lines)


@mcp.tool()
async def list_conditional_access_policies(tenant_id: str) -> str:
    """List all Conditional Access policies in a tenant.

    Args:
        tenant_id: The tenant ID or domain
    """
    graph = GraphClient(tenant_id)
    data = await graph.get("/identity/conditionalAccess/policies")
    policies = data.get("value", [])
    if not policies:
        return "No Conditional Access policies found."
    lines = [f"# Conditional Access Policies ({len(policies)})\n"]
    for p in policies:
        state_map = {"enabled": "ON", "disabled": "OFF", "enabledForReportingButNotEnforced": "Report-only"}
        state = state_map.get(p.get("state"), p.get("state"))
        lines.append(f"- **{p.get('displayName', 'Unnamed')}** — [{state}] (ID: `{p.get('id', '')}`)")
    return "\n".join(lines)


@mcp.tool()
async def get_sign_in_summary(tenant_id: str) -> str:
    """Get a sign-in activity summary: success/failure counts, top failure reasons.

    Args:
        tenant_id: The tenant ID or domain
    """
    graph = GraphClient(tenant_id)
    data = await graph.get("/auditLogs/signIns", params={
        "$top": 500, "$select": "status,userPrincipalName,clientAppUsed", "$orderby": "createdDateTime desc",
    })
    signins = data.get("value", [])
    success = sum(1 for s in signins if s.get("status", {}).get("errorCode") == 0)
    failure = len(signins) - success
    reasons = {}
    for s in signins:
        code = s.get("status", {}).get("errorCode", 0)
        if code != 0:
            reason = s.get("status", {}).get("failureReason", f"Error {code}")
            reasons[reason] = reasons.get(reason, 0) + 1
    lines = [f"# Sign-in Summary (last {len(signins)} events)\n"]
    lines.append(f"- **Success:** {success}")
    lines.append(f"- **Failure:** {failure}")
    if reasons:
        lines.append("\n## Top Failure Reasons")
        for reason, count in sorted(reasons.items(), key=lambda x: -x[1])[:5]:
            lines.append(f"- {reason}: {count}x")
    return "\n".join(lines)


# ============================================================
# Standards & Compliance
# ============================================================

@mcp.tool()
async def run_standards_check(tenant_id: str) -> str:
    """Run all compliance/security standards checks against a tenant (MFA, CA policies, password, licenses, etc.).

    Args:
        tenant_id: The tenant ID or domain
    """
    results = await run_checks(tenant_id)
    passed = sum(1 for r in results if r.get("passed"))
    failed = len(results) - passed
    lines = [f"# Standards Check: {passed}/{len(results)} passed\n"]
    for r in results:
        icon = "PASS" if r.get("passed") else "FAIL"
        lines.append(f"- **[{icon}]** {r.get('label', r.get('check', 'Unknown'))}")
        lines.append(f"  {r.get('details', '')}")
    return "\n".join(lines)


@mcp.tool()
async def list_available_checks() -> str:
    """List all available standards/compliance checks that can be run."""
    lines = ["# Available Standards Checks\n"]
    for name, info in AVAILABLE_CHECKS.items():
        lines.append(f"- **{name}** ({info['category']}): {info['label']}")
    return "\n".join(lines)


# ============================================================
# Groups
# ============================================================

@mcp.tool()
async def list_groups(tenant_id: str, top: int = 50) -> str:
    """List groups in a tenant.

    Args:
        tenant_id: The tenant ID or domain
        top: Maximum number of groups (default 50)
    """
    graph = GraphClient(tenant_id)
    data = await graph.get("/groups", params={
        "$select": "id,displayName,groupTypes,mailEnabled,securityEnabled,mail", "$top": top,
    })
    groups = data.get("value", [])
    lines = [f"# Groups ({len(groups)})\n"]
    for g in groups:
        gtype = "M365" if "Unified" in g.get("groupTypes", []) else ("Security" if g.get("securityEnabled") else "Distribution")
        lines.append(f"- **{g.get('displayName', '')}** [{gtype}] — {g.get('mail', 'no email')}")
    return "\n".join(lines)


# ============================================================
# Devices / Intune
# ============================================================

@mcp.tool()
async def list_devices(tenant_id: str, top: int = 50) -> str:
    """List Intune managed devices in a tenant.

    Args:
        tenant_id: The tenant ID or domain
        top: Maximum number of devices (default 50)
    """
    graph = GraphClient(tenant_id)
    data = await graph.get("/deviceManagement/managedDevices", params={"$top": top})
    devices = data.get("value", [])
    if not devices:
        return "No managed devices found."
    lines = [f"# Managed Devices ({len(devices)})\n"]
    lines.append("| Name | OS | Compliance | Last Sync | User |")
    lines.append("|------|----|-----------|-----------|------|")
    for d in devices:
        lines.append(f"| {d.get('deviceName', '')} | {d.get('operatingSystem', '')} | {d.get('complianceState', '')} | {str(d.get('lastSyncDateTime', ''))[:10]} | {d.get('userPrincipalName', '')} |")
    return "\n".join(lines)


@mcp.tool()
async def device_action(tenant_id: str, device_id: str, action: str) -> str:
    """Execute a remote action on a managed device.

    Args:
        tenant_id: The tenant ID or domain
        device_id: The Intune device ID
        action: Action to perform: syncDevice, rebootNow, retire, wipe, remoteLock, resetPasscode, windowsDefenderScan
    """
    graph = GraphClient(tenant_id)
    valid_actions = ["syncDevice", "rebootNow", "retire", "wipe", "remoteLock", "resetPasscode", "windowsDefenderScan"]
    if action not in valid_actions:
        return f"Invalid action. Valid actions: {', '.join(valid_actions)}"
    await graph.post(f"/deviceManagement/managedDevices/{device_id}/{action}", {})
    return f"Action **{action}** executed on device `{device_id}`."


# ============================================================
# Licenses
# ============================================================

@mcp.tool()
async def list_licenses(tenant_id: str) -> str:
    """List all subscribed license SKUs for a tenant with usage info.

    Args:
        tenant_id: The tenant ID or domain
    """
    graph = GraphClient(tenant_id)
    data = await graph.get("/subscribedSkus")
    skus = data.get("value", [])
    if not skus:
        return "No licenses found."
    lines = ["# Licenses\n"]
    lines.append("| SKU | Used | Total | Available |")
    lines.append("|-----|------|-------|-----------|")
    for s in skus:
        total = s.get("prepaidUnits", {}).get("enabled", 0)
        consumed = s.get("consumedUnits", 0)
        available = total - consumed
        lines.append(f"| {s.get('skuPartNumber', 'Unknown')} | {consumed} | {total} | {available} |")
    return "\n".join(lines)


# ============================================================
# Graph API Proxy (for advanced queries)
# ============================================================

@mcp.tool()
async def graph_query(tenant_id: str, endpoint: str, method: str = "GET", body: str = "") -> str:
    """Execute a raw Microsoft Graph API query. Use for anything not covered by other tools.

    Args:
        tenant_id: The tenant ID or domain
        endpoint: The Graph API endpoint path (e.g. /users, /groups, /security/alerts_v2)
        method: HTTP method (GET, POST, PATCH, DELETE)
        body: JSON body for POST/PATCH (optional)
    """
    import json
    graph = GraphClient(tenant_id)
    method = method.upper()
    if method == "GET":
        result = await graph.get(endpoint)
    elif method == "POST":
        result = await graph.post(endpoint, json.loads(body) if body else {})
    elif method == "PATCH":
        result = await graph.patch(endpoint, json.loads(body) if body else {})
    elif method == "DELETE":
        await graph.delete(endpoint)
        return f"DELETE {endpoint} completed."
    else:
        return f"Unsupported method: {method}"
    return json.dumps(result, indent=2, default=str)[:4000]


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    mcp.run()
