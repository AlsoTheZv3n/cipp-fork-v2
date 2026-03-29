"""Security endpoints with comprehensive Graph API coverage."""
from fastapi import APIRouter, Query

from app.core.graph import GraphClient

router = APIRouter(prefix="/api", tags=["security"])


# ============================================================
# Conditional Access
# ============================================================

@router.get("/ListConditionalAccessPolicies")
async def list_ca_policies(tenantFilter: str = Query(...)):
    """List all Conditional Access policies with full details."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/identity/conditionalAccess/policies")
    policies = data.get("value", [])
    # Enrich with state summary
    for p in policies:
        p["_stateLabel"] = {"enabled": "On", "disabled": "Off", "enabledForReportingButNotEnforced": "Report-only"}.get(p.get("state"), p.get("state"))
    return policies


@router.post("/AddCAPolicy")
async def add_ca_policy(body: dict):
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter is required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/identity/conditionalAccess/policies", body)
    return {"Results": f"CA Policy {result.get('displayName', '')} created."}


@router.post("/EditCAPolicy")
async def edit_ca_policy(body: dict):
    tenant_filter = body.pop("tenantFilter", None)
    policy_id = body.pop("policyId", None)
    if not tenant_filter or not policy_id:
        return {"Results": "tenantFilter and policyId are required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/identity/conditionalAccess/policies/{policy_id}", body)
    return {"Results": f"CA Policy {policy_id} updated."}


@router.post("/RemoveCAPolicy")
async def remove_ca_policy(body: dict):
    tenant_filter = body.get("tenantFilter")
    policy_id = body.get("policyId")
    if not tenant_filter or not policy_id:
        return {"Results": "tenantFilter and policyId are required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/identity/conditionalAccess/policies/{policy_id}")
    return {"Results": f"CA Policy {policy_id} deleted."}


# ============================================================
# Named Locations
# ============================================================

@router.get("/ListNamedLocations")
async def list_named_locations(tenantFilter: str = Query(...)):
    graph = GraphClient(tenantFilter)
    data = await graph.get("/identity/conditionalAccess/namedLocations")
    return data.get("value", [])


# ============================================================
# Defender / Security Alerts & Incidents
# ============================================================

@router.get("/ExecAlertsList")
async def list_alerts(tenantFilter: str = Query(...), top: int = 50):
    """List security alerts with severity and status."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/security/alerts_v2", params={
        "$top": top,
        "$orderby": "createdDateTime desc",
    })
    return data.get("value", [])


@router.get("/ExecIncidentsList")
async def list_incidents(tenantFilter: str = Query(...), top: int = 50):
    """List security incidents."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/security/incidents", params={
        "$top": top,
        "$orderby": "createdDateTime desc",
    })
    return data.get("value", [])


@router.post("/ExecSetSecurityAlert")
async def set_security_alert(body: dict):
    """Update a security alert status/classification."""
    tenant_filter = body.get("tenantFilter")
    alert_id = body.get("alertId")
    if not tenant_filter or not alert_id:
        return {"Results": "tenantFilter and alertId are required."}
    graph = GraphClient(tenant_filter)
    update = {}
    if "status" in body:
        update["status"] = body["status"]
    if "classification" in body:
        update["classification"] = body["classification"]
    if "determination" in body:
        update["determination"] = body["determination"]
    if "assignedTo" in body:
        update["assignedTo"] = body["assignedTo"]
    await graph.patch(f"/security/alerts_v2/{alert_id}", update)
    return {"Results": f"Alert {alert_id} updated."}


@router.post("/ExecSetSecurityIncident")
async def set_security_incident(body: dict):
    """Update a security incident status/classification."""
    tenant_filter = body.get("tenantFilter")
    incident_id = body.get("incidentId")
    if not tenant_filter or not incident_id:
        return {"Results": "tenantFilter and incidentId are required."}
    graph = GraphClient(tenant_filter)
    update = {}
    if "status" in body:
        update["status"] = body["status"]
    if "classification" in body:
        update["classification"] = body["classification"]
    if "assignedTo" in body:
        update["assignedTo"] = body["assignedTo"]
    await graph.patch(f"/security/incidents/{incident_id}", update)
    return {"Results": f"Incident {incident_id} updated."}


# ============================================================
# Secure Score (detailed)
# ============================================================

@router.get("/ExecUpdateSecureScore")
async def get_secure_score(tenantFilter: str = Query(...)):
    """Get latest secure score with control scores breakdown."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/security/secureScores", params={"$top": 1})
    scores = data.get("value", [])
    if not scores:
        return {}
    score = scores[0]
    # Add percentage
    current = score.get("currentScore", 0)
    maximum = score.get("maxScore", 1)
    score["_percentage"] = round(current / maximum * 100) if maximum else 0
    return score


@router.get("/security/secureScoreControlProfiles")
async def list_secure_score_profiles(tenantFilter: str = Query(...)):
    """Get secure score improvement actions."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/security/secureScoreControlProfiles")
    return data.get("value", [])


# ============================================================
# Identity Protection — Risky Users
# ============================================================

@router.get("/security/riskyUsers")
async def list_risky_users(tenantFilter: str = Query(...), top: int = 100):
    """List all risky users from Identity Protection."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/identityProtection/riskyUsers", params={
        "$top": top,
        "$orderby": "riskLastUpdatedDateTime desc",
    })
    users = data.get("value", [])
    # Enrich with risk summary
    for u in users:
        u["_riskSummary"] = f"{u.get('riskLevel', 'none')} / {u.get('riskState', 'none')}"
    return users


@router.get("/security/riskyUser/{user_id}")
async def get_risky_user(tenantFilter: str = Query(...), user_id: str = ""):
    """Get detailed risk info for a specific user."""
    graph = GraphClient(tenantFilter)
    user = await graph.get(f"/identityProtection/riskyUsers/{user_id}")
    # Get risk history
    history = await graph.get(f"/identityProtection/riskyUsers/{user_id}/history")
    user["_riskHistory"] = history.get("value", [])
    return user


@router.post("/ExecDismissRiskyUser")
async def dismiss_risky_user(body: dict):
    """Dismiss risky users (mark as safe)."""
    tenant_filter = body.get("tenantFilter")
    user_ids = body.get("userIds", [])
    if not tenant_filter or not user_ids:
        return {"Results": "tenantFilter and userIds are required."}
    graph = GraphClient(tenant_filter)
    await graph.post("/identityProtection/riskyUsers/dismiss", {"userIds": user_ids})
    return {"Results": f"Dismissed {len(user_ids)} risky user(s)."}


@router.post("/security/confirmCompromised")
async def confirm_compromised(body: dict):
    """Confirm users as compromised."""
    tenant_filter = body.get("tenantFilter")
    user_ids = body.get("userIds", [])
    if not tenant_filter or not user_ids:
        return {"Results": "tenantFilter and userIds are required."}
    graph = GraphClient(tenant_filter)
    await graph.post("/identityProtection/riskyUsers/confirmCompromised", {"userIds": user_ids})
    return {"Results": f"Confirmed {len(user_ids)} user(s) as compromised."}


# ============================================================
# Identity Protection — Risky Sign-ins & Service Principals
# ============================================================

@router.get("/security/riskySignIns")
async def list_risky_signins(tenantFilter: str = Query(...), top: int = 100):
    """List risky sign-in events."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/identityProtection/riskDetections", params={
        "$top": top,
        "$orderby": "activityDateTime desc",
    })
    return data.get("value", [])


@router.get("/security/riskyServicePrincipals")
async def list_risky_service_principals(tenantFilter: str = Query(...)):
    """List risky service principals."""
    graph = GraphClient(tenantFilter)
    try:
        data = await graph.get("/identityProtection/riskyServicePrincipals")
        return data.get("value", [])
    except Exception:
        return []


# ============================================================
# Sign-in & Audit Logs (enhanced with filters)
# ============================================================

@router.get("/ListSignIns")
async def list_sign_ins(
    tenantFilter: str = Query(...),
    top: int = 100,
    filter: str = Query(None, alias="$filter"),
):
    """Get sign-in logs with optional OData filter."""
    graph = GraphClient(tenantFilter)
    params = {"$top": top, "$orderby": "createdDateTime desc"}
    if filter:
        params["$filter"] = filter
    data = await graph.get("/auditLogs/signIns", params=params)
    return data.get("value", [])


@router.get("/ListAuditLogs")
async def list_audit_logs(
    tenantFilter: str = Query(...),
    top: int = 100,
    filter: str = Query(None, alias="$filter"),
):
    """Get directory audit logs with optional OData filter."""
    graph = GraphClient(tenantFilter)
    params = {"$top": top, "$orderby": "activityDateTime desc"}
    if filter:
        params["$filter"] = filter
    data = await graph.get("/auditLogs/directoryAudits", params=params)
    return data.get("value", [])


@router.get("/security/signInSummary")
async def sign_in_summary(tenantFilter: str = Query(...)):
    """Get sign-in summary: success/failure counts, top failure reasons."""
    graph = GraphClient(tenantFilter)
    # Get recent sign-ins
    data = await graph.get("/auditLogs/signIns", params={
        "$top": 500,
        "$select": "status,createdDateTime,userPrincipalName,ipAddress,location,clientAppUsed",
        "$orderby": "createdDateTime desc",
    })
    signins = data.get("value", [])

    success = sum(1 for s in signins if s.get("status", {}).get("errorCode") == 0)
    failure = len(signins) - success

    # Top failure reasons
    failure_reasons = {}
    for s in signins:
        code = s.get("status", {}).get("errorCode", 0)
        if code != 0:
            reason = s.get("status", {}).get("failureReason", f"Error {code}")
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

    top_failures = sorted(failure_reasons.items(), key=lambda x: -x[1])[:10]

    # Unique users with failures
    failed_users = set()
    for s in signins:
        if s.get("status", {}).get("errorCode", 0) != 0:
            failed_users.add(s.get("userPrincipalName", ""))

    # Legacy auth detection
    legacy_apps = {"Exchange ActiveSync", "IMAP4", "POP3", "SMTP", "Other clients"}
    legacy_count = sum(1 for s in signins if s.get("clientAppUsed", "") in legacy_apps)

    return {
        "total": len(signins),
        "success": success,
        "failure": failure,
        "topFailureReasons": [{"reason": r, "count": c} for r, c in top_failures],
        "failedUserCount": len(failed_users),
        "legacyAuthCount": legacy_count,
    }


# ============================================================
# Roles (enhanced with member details)
# ============================================================

@router.get("/ListRoles")
async def list_roles(tenantFilter: str = Query(...)):
    """List directory roles with member counts."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/directoryRoles")
    roles = data.get("value", [])

    # Get member counts via batch
    if roles:
        batch_requests = [
            {"id": str(i), "method": "GET", "url": f"/directoryRoles/{r['id']}/members/$count", "headers": {"ConsistencyLevel": "eventual"}}
            for i, r in enumerate(roles[:20])
        ]
        try:
            batch_result = await graph.batch(batch_requests)
            for resp in batch_result.get("responses", []):
                idx = int(resp.get("id", 0))
                if idx < len(roles):
                    roles[idx]["_memberCount"] = resp.get("body", 0)
        except Exception:
            pass

    return roles


@router.get("/security/roleMembers/{role_id}")
async def get_role_members(tenantFilter: str = Query(...), role_id: str = ""):
    """Get members of a specific directory role."""
    graph = GraphClient(tenantFilter)
    data = await graph.get(f"/directoryRoles/{role_id}/members")
    return data.get("value", [])


# ============================================================
# Threat Intelligence
# ============================================================

@router.get("/security/threatIntelligence")
async def list_threat_intelligence(tenantFilter: str = Query(...)):
    """Get threat intelligence indicators."""
    graph = GraphClient(tenantFilter)
    try:
        data = await graph.get("/security/tiIndicators", params={"$top": 50})
        return data.get("value", [])
    except Exception:
        return []


# ============================================================
# Authentication Methods Policy
# ============================================================

@router.get("/security/authMethodsPolicy")
async def get_auth_methods_policy(tenantFilter: str = Query(...)):
    """Get authentication methods policy (which methods are enabled)."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/policies/authenticationMethodsPolicy")
    return data


@router.get("/security/authMethodsActivity")
async def get_auth_methods_activity(tenantFilter: str = Query(...)):
    """Get authentication methods registration activity."""
    graph = GraphClient(tenantFilter)
    try:
        data = await graph.get("/reports/authenticationMethods/userRegistrationDetails")
        return data.get("value", [])
    except Exception:
        return []
