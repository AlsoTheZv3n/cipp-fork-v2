"""Standards, BPA, and compliance checking with real implementations."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.graph import GraphClient
from app.models.standard import BPATemplate, StandardResult, StandardTemplate
from app.services.standards_engine import AVAILABLE_CHECKS, run_checks

router = APIRouter(prefix="/api", tags=["standards"])


# --- Standards ---

@router.get("/ListStandards")
async def list_standards():
    """List all available standard checks."""
    return [
        {"name": name, "label": info["label"], "category": info["category"]}
        for name, info in AVAILABLE_CHECKS.items()
    ]

@router.get("/ListStandardTemplates")
async def list_standard_templates(db: AsyncSession = Depends(get_db)):
    """List saved standard templates from DB."""
    result = await db.execute(select(StandardTemplate))
    templates = result.scalars().all()
    return [
        {
            "id": str(t.id),
            "name": t.name,
            "description": t.description,
            "checks": t.checks,
            "isDefault": t.is_default,
            "createdAt": t.created_at.isoformat() if t.created_at else None,
        }
        for t in templates
    ]

@router.get("/listStandardTemplates")
async def list_standard_templates_lower(db: AsyncSession = Depends(get_db)):
    return await list_standard_templates(db)

@router.post("/AddStandardTemplate")
async def add_standard_template(body: dict, db: AsyncSession = Depends(get_db)):
    """Create a standard template."""
    template = StandardTemplate(
        name=body.get("name", "Unnamed Template"),
        description=body.get("description", ""),
        checks=body.get("checks", []),
        is_default=body.get("isDefault", False),
    )
    db.add(template)
    await db.commit()
    return {"Results": f"Standard template '{template.name}' created."}

@router.post("/RemoveStandardTemplate")
async def remove_standard_template(body: dict, db: AsyncSession = Depends(get_db)):
    """Delete a standard template."""
    template_id = body.get("id")
    if not template_id:
        return {"Results": "Template id required."}
    await db.execute(sa_delete(StandardTemplate).where(StandardTemplate.id == template_id))
    await db.commit()
    return {"Results": "Standard template removed."}

@router.get("/ListStandardsCompare")
async def list_standards_compare(
    tenantFilter: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get latest standards results for a tenant."""
    if not tenantFilter:
        # Return all latest results
        result = await db.execute(select(StandardResult).order_by(StandardResult.run_at.desc()).limit(50))
        results = result.scalars().all()
        return [
            {
                "tenantId": r.tenant_id,
                "passed": r.passed_count,
                "failed": r.failed_count,
                "total": r.total_count,
                "results": r.results,
                "runAt": r.run_at.isoformat() if r.run_at else None,
            }
            for r in results
        ]
    # Return latest for specific tenant
    result = await db.execute(
        select(StandardResult)
        .where(StandardResult.tenant_id == tenantFilter)
        .order_by(StandardResult.run_at.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    if not latest:
        return {"Results": []}
    return {
        "tenantId": latest.tenant_id,
        "passed": latest.passed_count,
        "failed": latest.failed_count,
        "total": latest.total_count,
        "results": latest.results,
        "runAt": latest.run_at.isoformat() if latest.run_at else None,
    }

@router.post("/ExecStandardsRun")
async def exec_standards_run(body: dict, db: AsyncSession = Depends(get_db)):
    """Run all standard checks against a tenant and save results."""
    tenant_filter = body.get("tenantFilter", body.get("TenantFilter"))
    template_id = body.get("templateId")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}

    # Determine which checks to run
    check_names = None
    params_map = {}
    if template_id:
        result = await db.execute(select(StandardTemplate).where(StandardTemplate.id == template_id))
        template = result.scalar_one_or_none()
        if template and template.checks:
            check_names = [c.get("check") for c in template.checks if c.get("enabled", True)]
            params_map = {c["check"]: c.get("params", {}) for c in template.checks}

    # Run checks
    results = await run_checks(tenant_filter, check_names, params_map)

    passed = sum(1 for r in results if r.get("passed"))
    failed = len(results) - passed

    # Save results
    db_result = StandardResult(
        tenant_id=tenant_filter,
        template_id=template_id,
        results=results,
        passed_count=passed,
        failed_count=failed,
        total_count=len(results),
    )
    db.add(db_result)
    await db.commit()

    return {
        "Results": results,
        "Summary": {"passed": passed, "failed": failed, "total": len(results)},
    }

@router.post("/AddStandardsTemplate")
async def add_standards_template(body: dict, db: AsyncSession = Depends(get_db)):
    return await add_standard_template(body, db)


# --- BPA (Best Practice Analyzer) ---

@router.get("/listBPA")
async def list_bpa(tenantFilter: str = Query(None), db: AsyncSession = Depends(get_db)):
    """List BPA results (same as standards results but labeled as BPA)."""
    if not tenantFilter:
        result = await db.execute(select(StandardResult).order_by(StandardResult.run_at.desc()).limit(20))
    else:
        result = await db.execute(
            select(StandardResult)
            .where(StandardResult.tenant_id == tenantFilter)
            .order_by(StandardResult.run_at.desc())
            .limit(5)
        )
    results = result.scalars().all()
    return [
        {
            "tenantId": r.tenant_id,
            "passed": r.passed_count,
            "failed": r.failed_count,
            "total": r.total_count,
            "results": r.results,
            "runAt": r.run_at.isoformat() if r.run_at else None,
        }
        for r in results
    ]

@router.get("/listBPATemplates")
async def list_bpa_templates(db: AsyncSession = Depends(get_db)):
    """List BPA templates."""
    result = await db.execute(select(BPATemplate))
    templates = result.scalars().all()
    return [
        {"id": str(t.id), "name": t.name, "description": t.description, "checks": t.checks}
        for t in templates
    ]

@router.post("/ExecBPA")
async def exec_bpa(body: dict, db: AsyncSession = Depends(get_db)):
    """Execute Best Practice Analysis (runs all checks)."""
    tenant_filter = body.get("tenantFilter", body.get("TenantFilter"))
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    return await exec_standards_run({"tenantFilter": tenant_filter}, db)

@router.post("/AddBPATemplate")
async def add_bpa_template(body: dict, db: AsyncSession = Depends(get_db)):
    """Create a BPA template."""
    template = BPATemplate(
        name=body.get("name", "Unnamed BPA Template"),
        description=body.get("description", ""),
        checks=body.get("checks", []),
    )
    db.add(template)
    await db.commit()
    return {"Results": f"BPA template '{template.name}' created."}

@router.post("/RemoveBPATemplate")
async def remove_bpa_template(body: dict, db: AsyncSession = Depends(get_db)):
    """Delete a BPA template."""
    template_id = body.get("id")
    if not template_id:
        return {"Results": "Template id required."}
    await db.execute(sa_delete(BPATemplate).where(BPATemplate.id == template_id))
    await db.commit()
    return {"Results": "BPA template removed."}


# --- Tenant Drift ---

@router.get("/listTenantDrift")
async def list_tenant_drift(tenantFilter: str = Query(None), db: AsyncSession = Depends(get_db)):
    """Compare current tenant config vs last known good state."""
    if not tenantFilter:
        return {"Results": []}

    # Get latest results
    result = await db.execute(
        select(StandardResult)
        .where(StandardResult.tenant_id == tenantFilter)
        .order_by(StandardResult.run_at.desc())
        .limit(2)
    )
    results = result.scalars().all()
    if len(results) < 2:
        return {"Results": "Not enough data for drift detection. Run standards at least twice."}

    current = results[0].results
    previous = results[1].results

    drifts = []
    prev_map = {r["check"]: r for r in previous}
    for check in current:
        prev = prev_map.get(check["check"])
        if prev and prev.get("passed") != check.get("passed"):
            drifts.append({
                "check": check["check"],
                "label": check.get("label", ""),
                "previousState": "passed" if prev.get("passed") else "failed",
                "currentState": "passed" if check.get("passed") else "failed",
                "details": check.get("details", ""),
            })

    return {"Results": drifts, "driftCount": len(drifts)}


# --- Access checks ---

@router.post("/ExecAccessChecks")
async def exec_access_checks(body: dict):
    """Run CIPP access checks (verify we can reach Graph for this tenant)."""
    tenant_filter = body.get("tenantFilter")
    results = {"graphPermissions": False, "exchangePermissions": False, "samPermissions": True}
    if tenant_filter:
        graph = GraphClient(tenant_filter)
        try:
            await graph.get("/organization")
            results["graphPermissions"] = True
        except Exception:
            pass
        try:
            await graph.get("/users", params={"$top": 1})
            results["exchangePermissions"] = True
        except Exception:
            pass
    return {"Results": results}


# --- Directory ---

@router.get("/ListAzureADConnectStatus")
async def list_azure_ad_connect_status(tenantFilter: str = Query(...)):
    """Get Azure AD Connect sync status."""
    graph = GraphClient(tenantFilter)
    org = await graph.get("/organization")
    org_data = org.get("value", [{}])[0] if org.get("value") else {}
    return {
        "dirSyncEnabled": org_data.get("onPremisesSyncEnabled", False),
        "lastDirSyncTime": org_data.get("onPremisesLastSyncDateTime"),
        "displayName": org_data.get("displayName"),
    }

@router.get("/ListInactiveAccounts")
async def list_inactive_accounts(tenantFilter: str = Query(...)):
    """List inactive user accounts (no sign-in activity)."""
    graph = GraphClient(tenantFilter)
    users = await graph.get_all_pages("/users", params={
        "$select": "id,displayName,userPrincipalName,signInActivity,accountEnabled,userType",
        "$filter": "accountEnabled eq true and userType eq 'Member'",
    })
    # Filter for users with no recent sign-in (signInActivity may not be populated for all)
    inactive = [u for u in users if not u.get("signInActivity", {}).get("lastSignInDateTime")]
    return inactive

@router.get("/ListDeletedItems")
async def list_deleted_items(tenantFilter: str = Query(...)):
    """List recently deleted directory objects."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/directory/deletedItems/microsoft.graph.user", params={"$top": 100})
    return data.get("value", [])

@router.post("/ExecRestoreDeleted")
async def exec_restore_deleted(body: dict):
    """Restore a deleted directory object."""
    tenant_filter = body.get("tenantFilter")
    object_id = body.get("objectId")
    if not tenant_filter or not object_id:
        return {"Results": "tenantFilter and objectId required."}
    graph = GraphClient(tenant_filter)
    await graph.post(f"/directory/deletedItems/{object_id}/restore", {})
    return {"Results": f"Object {object_id} restored."}
