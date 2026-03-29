from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.graph import GraphClient
from app.models.tenant import Tenant

router = APIRouter(prefix="/api", tags=["tenants"])


@router.get("/ListTenants")
async def list_tenants(db: AsyncSession = Depends(get_db)):
    """List all onboarded tenants from local database."""
    result = await db.execute(select(Tenant).where(Tenant.is_active.is_(True)))
    tenants = result.scalars().all()
    return [
        {
            "customerId": str(t.id),
            "defaultDomainName": t.default_domain,
            "displayName": t.display_name,
            "tenantId": t.tenant_id,
        }
        for t in tenants
    ]


@router.get("/ListOrg")
async def list_org(tenantFilter: str = Query(...)):
    """Get tenant organization details."""
    graph = GraphClient(tenantFilter)
    return await graph.get("/organization")


@router.get("/ListDomains")
async def list_domains(tenantFilter: str = Query(...)):
    """Get tenant domains."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/domains")
    return data.get("value", [])


@router.get("/listTenantDetails")
async def list_tenant_details(tenantFilter: str = Query(...)):
    """Get detailed tenant info from Graph."""
    graph = GraphClient(tenantFilter)
    org = await graph.get("/organization")
    domains = await graph.get("/domains")
    skus = await graph.get("/subscribedSkus")
    return {
        "organization": org.get("value", []),
        "domains": domains.get("value", []),
        "subscribedSkus": skus.get("value", []),
    }


@router.post("/AddTenant")
async def add_tenant(body: dict, db: AsyncSession = Depends(get_db)):
    """Onboard a new tenant."""
    tenant = Tenant(
        tenant_id=body["tenantId"],
        display_name=body.get("displayName"),
        default_domain=body.get("defaultDomainName"),
    )
    db.add(tenant)
    await db.commit()
    return {"Results": f"Tenant {body['tenantId']} onboarded successfully."}


@router.post("/EditTenant")
async def edit_tenant(body: dict, db: AsyncSession = Depends(get_db)):
    """Update tenant properties."""
    result = await db.execute(
        select(Tenant).where(Tenant.tenant_id == body["tenantId"])
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        return {"Results": "Tenant not found."}
    if "displayName" in body:
        tenant.display_name = body["displayName"]
    if "defaultDomainName" in body:
        tenant.default_domain = body["defaultDomainName"]
    await db.commit()
    return {"Results": f"Tenant {body['tenantId']} updated."}
