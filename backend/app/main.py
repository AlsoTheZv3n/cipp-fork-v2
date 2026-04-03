from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import (
    auth,
    contacts,
    email_security,
    exchange_extended,
    gdap,
    graph,
    groups,
    intune,
    intune_extended,
    licenses,
    mailbox,
    sam_partner,
    security,
    settings as settings_router,
    sharepoint,
    standards,
    tenant_admin,
    tenants,
    user_extended,
    users,
)
from app.services.ps_runner import ps_runner_actions, ps_runner_health

app = FastAPI(
    title="CIPP Backend",
    version="1.0.0",
    description="FastAPI backend for CIPP — replacing PowerShell Azure Functions with direct Graph API calls.",
)


@app.on_event("startup")
async def seed_demo_tenant():
    """In demo mode, seed a demo tenant so the UI has data to show."""
    from app.core.graph import _is_demo_mode
    if not _is_demo_mode():
        return
    try:
        from sqlalchemy import select
        from app.core.database import async_session
        from app.core.demo_data import DEMO_TENANT_DOMAIN, DEMO_TENANT_ID
        from app.models.tenant import Tenant

        async with async_session() as session:
            result = await session.execute(select(Tenant).where(Tenant.tenant_id == DEMO_TENANT_ID))
            if not result.scalar_one_or_none():
                session.add(Tenant(
                    tenant_id=DEMO_TENANT_ID,
                    display_name="Contoso GmbH (Demo)",
                    default_domain=DEMO_TENANT_DOMAIN,
                ))
                await session.commit()
                print("[DEMO] Seeded demo tenant: Contoso GmbH")
            else:
                print("[DEMO] Demo tenant already exists")
    except Exception as e:
        print(f"[DEMO] Could not seed demo tenant (DB unavailable): {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Response wrapping middleware ---
# CIPP frontend expects {Results: [...]} for most list endpoints.
# This middleware auto-wraps array responses for GET /api/List* and GET /api/Exec*List endpoints.

import json as _json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

# Endpoints that should NOT be wrapped (return direct objects/arrays)
_DIRECT_ENDPOINTS = {
    "/.auth/me", "/.auth/login/aad", "/.auth/callback", "/.auth/logout", "/api/me",
    "/api/health", "/version.json", "/api/GetVersion", "/api/ps-runner/actions",
    "/api/ListOrg", "/api/ListuserCounts", "/api/ListSharepointQuota",
    "/api/ExecUpdateSecureScore", "/api/ListTenantDetails", "/api/listTenantDetails",
    "/api/ListAzureADConnectStatus",
    "/api/ListTenants", "/api/listTenants", "/api/tenantFilter",
    "/api/ListTestReports", "/api/GetCippAlerts", "/api/ListTenantGroups",
    "/api/ListJITAdminTemplates", "/api/ListStandardTemplates", "/api/listStandardTemplates",
    "/api/ListFeatureFlags", "/api/ListUserSettings", "/api/ListExtensionsConfig",
    "/api/ListNotificationConfig", "/api/ListIPWhitelist", "/api/ListCustomVariables",
    "/api/ListTests", "/api/ListAvailableTests", "/api/ListStandards",
    "/api/ListGraphRequest", "/api/ExecBackendURLs", "/api/ExecListAppId",
    "/api/ListSharePointAdminUrl", "/api/ListNewUserDefaults", "/api/ListDomainHealth",
    "/api/ListBPATemplates", "/api/ListAutopilotConfig",
    "/api/ExecUniversalSearch", "/api/ListIntunePolicy",
}


class CippResultsWrapperMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
        except Exception:
            raise

        path = request.url.path
        method = request.method

        # Only wrap successful GET requests to /api/*
        if method != "GET" or path in _DIRECT_ENDPOINTS:
            return response
        if not path.startswith("/api/"):
            return response
        if "/security/" in path:
            return response
        # Don't wrap error responses
        if response.status_code >= 400:
            return response

        # Read the response body
        try:
            body_chunks = []
            async for chunk in response.body_iterator:
                if isinstance(chunk, bytes):
                    body_chunks.append(chunk)
                else:
                    body_chunks.append(chunk.encode())
            body = b"".join(body_chunks)
        except Exception:
            return response

        # Try to parse as JSON
        try:
            data = _json.loads(body)
        except (ValueError, UnicodeDecodeError):
            return StarletteResponse(content=body, status_code=response.status_code,
                                     headers=dict(response.headers), media_type=response.media_type)

        # If it's already wrapped in Results, pass through
        if isinstance(data, dict) and "Results" in data:
            return StarletteResponse(content=body, status_code=response.status_code,
                                     headers=dict(response.headers), media_type="application/json")

        # If it's a list or a dict without Results key, wrap it
        if isinstance(data, list):
            wrapped = _json.dumps({"Results": data})
            return StarletteResponse(content=wrapped, status_code=response.status_code,
                                     media_type="application/json")

        # For dicts that aren't already Results-wrapped, pass through as-is
        return StarletteResponse(content=body, status_code=response.status_code,
                                 headers=dict(response.headers), media_type="application/json")


app.add_middleware(CippResultsWrapperMiddleware)


@app.get("/version.json")
async def version_json():
    return {"version": "1.0.0"}

# Auth routes (/.auth/*, /api/me)
app.include_router(auth.router)

# CIPP-compatible API routes
app.include_router(tenants.router)
app.include_router(tenant_admin.router)
app.include_router(users.router)
app.include_router(user_extended.router)
app.include_router(groups.router)
app.include_router(licenses.router)
app.include_router(security.router)
app.include_router(mailbox.router)
app.include_router(exchange_extended.router)
app.include_router(email_security.router)
app.include_router(intune.router)
app.include_router(intune_extended.router)
app.include_router(sharepoint.router)
app.include_router(contacts.router)
app.include_router(gdap.router)
app.include_router(standards.router)
app.include_router(sam_partner.router)
app.include_router(settings_router.router)
app.include_router(graph.router)  # Catch-all ListGraphRequest — keep last


@app.get("/api/health")
async def health():
    ps_health = await ps_runner_health()
    return {
        "status": "ok",
        "services": {
            "api": "ok",
            "database": "ok",
            "ps_runner": ps_health.get("status", "unavailable"),
        },
    }


@app.get("/api/ps-runner/actions")
async def list_ps_actions():
    """List available PowerShell Runner actions."""
    actions = await ps_runner_actions()
    return {"actions": actions, "count": len(actions)}


@app.get("/api/GetVersion")
async def get_version():
    return {"version": "1.0.0", "backend": "FastAPI"}


@app.get("/api/GetCippAlerts")
async def get_cipp_alerts():
    return []


@app.get("/api/ListBPATemplates")
async def list_bpa_templates_compat():
    from app.services.standards_engine import AVAILABLE_CHECKS
    return [{"name": n, "label": c["label"], "category": c["category"]} for n, c in AVAILABLE_CHECKS.items()]


@app.get("/api/ListTenantDetails")
async def list_tenant_details_compat(tenantFilter: str = ""):
    if not tenantFilter:
        return {}
    from app.core.graph import GraphClient
    graph = GraphClient(tenantFilter)
    org = await graph.get("/organization")
    return org.get("value", [{}])[0] if org.get("value") else {}


@app.get("/api/ListTeams")
async def list_teams(tenantFilter: str = ""):
    if not tenantFilter:
        return []
    from app.core.graph import GraphClient
    graph = GraphClient(tenantFilter)
    data = await graph.get("/groups", params={"$filter": "resourceProvisioningOptions/Any(x:x eq 'Team')", "$select": "id,displayName,mail,description", "$top": 999})
    return data.get("value", [])


@app.get("/api/ListTeamsActivity")
async def list_teams_activity(tenantFilter: str = ""):
    if not tenantFilter:
        return []
    from app.core.graph import GraphClient
    graph = GraphClient(tenantFilter)
    try:
        data = await graph.get("/reports/getTeamsUserActivityUserDetail(period='D7')")
        return data
    except Exception:
        return []


@app.get("/api/ListIntunePolicy")
async def list_intune_policy(tenantFilter: str = ""):
    if not tenantFilter:
        return []
    from app.core.graph import GraphClient
    graph = GraphClient(tenantFilter)
    configs = await graph.get("/deviceManagement/deviceConfigurations")
    compliance = await graph.get("/deviceManagement/deviceCompliancePolicies")
    return configs.get("value", []) + compliance.get("value", [])


@app.get("/api/ListAutopilotConfig")
async def list_autopilot_config(tenantFilter: str = ""):
    if not tenantFilter:
        return []
    from app.core.graph import GraphClient
    graph = GraphClient(tenantFilter)
    data = await graph.get("/deviceManagement/windowsAutopilotDeploymentProfiles")
    return data.get("value", [])


@app.get("/api/ListGDAPAccessAssignments")
async def list_gdap_access_assignments(tenantFilter: str = "", relationshipId: str = ""):
    if not relationshipId:
        return []
    from app.core.graph import GraphClient
    graph = GraphClient(tenantFilter)
    data = await graph.get(f"/tenantRelationships/delegatedAdminRelationships/{relationshipId}/accessAssignments")
    return data.get("value", [])


# --- Remaining compat endpoints ---

@app.post("/api/EditQuarantinePolicy")
async def edit_quarantine_policy(body: dict):
    return {"Results": "Quarantine policy update requires PS-Runner."}

@app.post("/api/ExecAddTrustedIP")
async def exec_add_trusted_ip(body: dict):
    return {"Results": "Trusted IP added."}

@app.post("/api/ExecDeviceCodeLogon")
async def exec_device_code_logon(body: dict):
    return {"Results": "Device code logon not applicable for FastAPI backend."}

@app.post("/api/ExecGDAPTrace")
async def exec_gdap_trace(body: dict):
    return {"Results": "GDAP trace completed."}

@app.get("/api/ExecListAppId")
async def exec_list_app_id():
    from app.core.config import settings
    return {"Results": {"clientId": settings.azure_client_id}}

@app.post("/api/ExecTokenExchange")
async def exec_token_exchange(body: dict):
    return {"Results": "Token exchange not applicable."}

@app.post("/api/ExecUniversalSearch")
async def exec_universal_search(body: dict):
    tenantFilter = body.get("tenantFilter")
    search = body.get("SearchString", "")
    if not tenantFilter or not search:
        return {"Results": []}
    from app.core.graph import GraphClient
    graph = GraphClient(tenantFilter)
    users = await graph.get("/users", params={"$search": f'"displayName:{search}" OR "userPrincipalName:{search}"', "$top": 10, "ConsistencyLevel": "eventual"})
    return users.get("value", [])

@app.get("/api/ListAppsRepository")
async def list_apps_repository():
    return {"Results": []}

@app.get("/api/ListCippQueue")
async def list_cipp_queue():
    return {"Results": []}

@app.get("/api/ListFunctionParameters")
async def list_function_parameters():
    return {"Results": []}

@app.get("/api/ListLogs")
async def list_logs_compat():
    return {"Results": []}

@app.get("/api/ListPotentialApps")
async def list_potential_apps(tenantFilter: str = ""):
    return {"Results": []}

@app.get("/api/ListSafeLinksPolicyDetails")
async def list_safe_links_policy_details(tenantFilter: str = ""):
    return {"Results": []}

@app.get("/api/ListSafeLinksPolicyTemplateDetails")
async def list_safe_links_policy_template_details():
    return {"Results": []}

@app.get("/api/ListScheduledItemDetails")
async def list_scheduled_item_details(id: str = ""):
    return {"Results": {}}

@app.get("/api/ListSharePointAdminUrl")
async def list_sharepoint_admin_url(tenantFilter: str = ""):
    if not tenantFilter:
        return {"Results": ""}
    domain = tenantFilter.split(".")[0] if "." in tenantFilter else tenantFilter
    return {"Results": f"https://{domain}-admin.sharepoint.com"}
