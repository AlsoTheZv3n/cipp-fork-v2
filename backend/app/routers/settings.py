"""Settings, config, utility endpoints — DB-backed."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete as sa_delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.graph import GraphClient
from app.models.template import CippLog, CippScheduledItem, CippTemplate

router = APIRouter(prefix="/api", tags=["settings"])


# ============================================================
# Extensions Config (DB-backed)
# ============================================================

@router.get("/ListExtensionsConfig")
async def list_extensions_config(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "extension_config"))
    configs = result.scalars().all()
    return [{"id": str(c.id), "name": c.name, "data": c.data} for c in configs]

@router.post("/ExecExtensionsConfig")
async def exec_extensions_config(body: dict, db: AsyncSession = Depends(get_db)):
    name = body.get("name", body.get("extension", "default"))
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "extension_config", CippTemplate.name == name))
    existing = result.scalar_one_or_none()
    if existing:
        existing.data = body
        await db.commit()
        return {"Results": f"Extension config '{name}' updated."}
    t = CippTemplate(type="extension_config", name=name, data=body)
    db.add(t)
    await db.commit()
    return {"Results": f"Extension config '{name}' created."}


# ============================================================
# Feature Flags (DB-backed with defaults)
# ============================================================

DEFAULT_FEATURE_FLAGS = {
    "enableIntune": True, "enableSharePoint": True, "enableTeams": True,
    "enableExchange": True, "enableSecurity": True, "enableGDAP": True,
}

@router.get("/ListFeatureFlags")
async def list_feature_flags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "feature_flags").limit(1))
    config = result.scalar_one_or_none()
    return {"Results": config.data if config else DEFAULT_FEATURE_FLAGS}

@router.post("/ExecFeatureFlag")
async def exec_feature_flag(body: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "feature_flags").limit(1))
    config = result.scalar_one_or_none()
    if config:
        config.data = {**config.data, **body}
        await db.commit()
    else:
        t = CippTemplate(type="feature_flags", name="flags", data={**DEFAULT_FEATURE_FLAGS, **body})
        db.add(t)
        await db.commit()
    return {"Results": "Feature flags updated."}


# ============================================================
# User Settings (DB-backed per user)
# ============================================================

@router.get("/ListUserSettings")
async def list_user_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "user_settings").limit(1))
    config = result.scalar_one_or_none()
    return {"Results": config.data if config else {"bookmarks": [], "theme": "light"}}

@router.post("/ExecUserSettings")
async def exec_user_settings(body: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "user_settings").limit(1))
    config = result.scalar_one_or_none()
    if config:
        config.data = {**config.data, **body}
        await db.commit()
    else:
        t = CippTemplate(type="user_settings", name="settings", data=body)
        db.add(t)
        await db.commit()
    return {"Results": "Settings updated."}

@router.post("/ExecUserBookmarks")
async def exec_user_bookmarks(body: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "user_settings").limit(1))
    config = result.scalar_one_or_none()
    if config:
        config.data["bookmarks"] = body.get("bookmarks", [])
        await db.commit()
    else:
        t = CippTemplate(type="user_settings", name="settings", data={"bookmarks": body.get("bookmarks", [])})
        db.add(t)
        await db.commit()
    return {"Results": "Bookmarks updated."}


# ============================================================
# Custom Roles (DB-backed)
# ============================================================

@router.get("/ListCustomRole")
async def list_custom_roles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "custom_role"))
    return [{"id": str(r.id), "name": r.name, "data": r.data} for r in result.scalars().all()]

@router.post("/ExecCustomRole")
async def exec_custom_role(body: dict, db: AsyncSession = Depends(get_db)):
    t = CippTemplate(type="custom_role", name=body.get("name", "Custom Role"), data=body)
    db.add(t)
    await db.commit()
    return {"Results": f"Custom role '{t.name}' created."}


# ============================================================
# Scheduled Items (DB-backed)
# ============================================================

@router.get("/ListScheduledItems")
async def list_scheduled_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippScheduledItem).where(CippScheduledItem.type == "task").order_by(CippScheduledItem.created_at.desc()))
    return [{"id": str(i.id), "name": i.name, "tenantId": i.tenant_id, "schedule": i.schedule, "data": i.data, "isActive": i.is_active} for i in result.scalars().all()]

@router.post("/AddScheduledItem")
async def add_scheduled_item(body: dict, db: AsyncSession = Depends(get_db)):
    item = CippScheduledItem(type="task", name=body.get("name", "Task"), tenant_id=body.get("tenantFilter"), schedule=body.get("schedule"), data=body)
    db.add(item)
    await db.commit()
    return {"Results": f"Scheduled item '{item.name}' created."}

@router.post("/RemoveScheduledItem")
async def remove_scheduled_item(body: dict, db: AsyncSession = Depends(get_db)):
    sid = body.get("id")
    if sid:
        await db.execute(sa_delete(CippScheduledItem).where(CippScheduledItem.id == sid))
        await db.commit()
    return {"Results": "Scheduled item removed."}


# ============================================================
# Community Repos
# ============================================================

@router.get("/ListCommunityRepos")
async def list_community_repos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "community_repo"))
    return [{"id": str(r.id), "name": r.name, "data": r.data} for r in result.scalars().all()]

@router.post("/ExecCommunityRepo")
async def exec_community_repo(body: dict, db: AsyncSession = Depends(get_db)):
    t = CippTemplate(type="community_repo", name=body.get("name", body.get("url", "Repo")), data=body)
    db.add(t)
    await db.commit()
    return {"Results": f"Community repo '{t.name}' added."}


# ============================================================
# Notifications
# ============================================================

@router.get("/ListNotificationConfig")
async def list_notification_config(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "notification_config").limit(1))
    config = result.scalar_one_or_none()
    return {"Results": config.data if config else {}}

@router.post("/ExecNotificationConfig")
async def exec_notification_config(body: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "notification_config").limit(1))
    config = result.scalar_one_or_none()
    if config:
        config.data = body
        await db.commit()
    else:
        t = CippTemplate(type="notification_config", name="notifications", data=body)
        db.add(t)
        await db.commit()
    return {"Results": "Notification config updated."}


# ============================================================
# Misc Settings
# ============================================================

@router.get("/ListIPWhitelist")
async def list_ip_whitelist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "ip_whitelist").limit(1))
    config = result.scalar_one_or_none()
    return {"Results": config.data.get("ips", []) if config else []}

@router.get("/ListCustomVariables")
async def list_custom_variables(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "custom_variables").limit(1))
    config = result.scalar_one_or_none()
    return {"Results": config.data if config else {}}

@router.post("/ExecCIPPDBCache")
async def exec_cipp_db_cache(body: dict):
    return {"Results": "PostgreSQL handles caching natively."}

@router.get("/ExecBackendURLs")
async def exec_backend_urls():
    from app.core.config import settings
    return {"Results": {"apiUrl": "/api", "version": "1.0.0", "psRunnerUrl": settings.ps_runner_url}}

@router.get("/ListGitHubReleaseNotes")
async def list_github_release_notes():
    """Fetch release notes from GitHub."""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.github.com/repos/KelvinTegelaar/CIPP/releases", params={"per_page": 5})
            return [{"name": rel.get("name"), "tag": rel.get("tag_name"), "body": rel.get("body", "")[:500], "date": rel.get("published_at")} for rel in r.json()]
    except Exception:
        return []


# ============================================================
# Logs (DB-backed)
# ============================================================

@router.get("/Listlogs")
async def list_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippLog).order_by(CippLog.created_at.desc()).limit(200))
    return [{"id": str(l.id), "level": l.level, "message": l.message, "tenantId": l.tenant_id, "source": l.source, "createdAt": l.created_at.isoformat()} for l in result.scalars().all()]


# ============================================================
# Diagnostics
# ============================================================

@router.get("/ListDiagnosticsPresets")
async def list_diagnostics_presets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CippTemplate).where(CippTemplate.type == "diagnostics_preset"))
    return [{"id": str(p.id), "name": p.name, "data": p.data} for p in result.scalars().all()]

@router.post("/ExecDiagnosticsPresets")
async def exec_diagnostics_presets(body: dict):
    return {"Results": "Diagnostic preset executed."}


# ============================================================
# Domain Analysis
# ============================================================

@router.get("/ListDomainHealth")
async def list_domain_health(tenantFilter: str = Query(None), Domain: str = Query(None)):
    """Domain health check — basic DNS-based analysis."""
    if not Domain:
        return []
    import httpx
    results = {"domain": Domain, "checks": {}}
    # Basic check: resolve the domain
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://dns.google/resolve?name={Domain}&type=MX")
            mx = r.json()
            results["checks"]["mx"] = {"status": "found" if mx.get("Answer") else "missing", "records": mx.get("Answer", [])}

            r = await client.get(f"https://dns.google/resolve?name={Domain}&type=TXT")
            txt = r.json()
            txt_records = [a.get("data", "") for a in txt.get("Answer", [])]
            results["checks"]["spf"] = {"status": "found" if any("v=spf1" in t for t in txt_records) else "missing"}
            results["checks"]["dmarc"] = {"status": "checking"}

            r = await client.get(f"https://dns.google/resolve?name=_dmarc.{Domain}&type=TXT")
            dmarc = r.json()
            results["checks"]["dmarc"] = {"status": "found" if dmarc.get("Answer") else "missing", "records": [a.get("data", "") for a in dmarc.get("Answer", [])]}
    except Exception:
        pass
    return {"Results": results}

@router.get("/ListDomainAnalyser")
async def list_domain_analyser(tenantFilter: str = Query(None)):
    return []

@router.post("/ExecDomainAnalyser")
async def exec_domain_analyser(body: dict):
    return {"Results": "Domain analysis — use ListDomainHealth for individual domains."}


# ============================================================
# Directory Objects
# ============================================================

@router.get("/ListDirectoryObjects")
async def list_directory_objects(tenantFilter: str = Query(...), id: str = Query(None), type: str = Query(None)):
    graph = GraphClient(tenantFilter)
    if id:
        return await graph.get(f"/directoryObjects/{id}")
    data = await graph.get("/directoryObjects", params={"$top": 100})
    return data.get("value", [])


# ============================================================
# Tenant filter dropdown
# ============================================================

@router.get("/tenantFilter")
async def tenant_filter_options(db: AsyncSession = Depends(get_db)):
    from app.models.tenant import Tenant
    result = await db.execute(select(Tenant).where(Tenant.is_active.is_(True)))
    return [{"customerId": str(t.id), "defaultDomainName": t.default_domain, "displayName": t.display_name} for t in result.scalars().all()]
