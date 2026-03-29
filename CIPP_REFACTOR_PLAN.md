# CIPP Refactor Plan
> Eigener M365 Multi-Tenant Management Stack — schneller, moderner, selbst kontrolliert.
> Open-Source-Verbesserung von CIPP. Nicht kommerziell.

---

## Ziel

CIPP (CyberDrain Improved Partner Portal) ist ein gutes Tool, aber mit einem massiven Problem: Das Backend basiert auf PowerShell Azure Functions, die beim Start hunderte PS1-Module herunterladen. Das macht es langsam, schwer wartbar und abhängig von Microsofts PS-Modul-Ökosystem.

**Unser Ansatz:**
- Frontend: CIPP forken (Next.js 16 / React 19), MUI schrittweise gegen eigenes Design System tauschen
- Backend: Kompletter Neubau in FastAPI mit direkten Graph API Calls
- PS1 nur noch für Exchange-Cmdlets die kein Graph Equivalent haben (isolierter PS-Runner Container)
- PostgreSQL als Datenbank (Token Cache, Tenant-Daten, Audit Logs)
- Deployment auf Railway statt Azure Functions

---

## Architektur

```
┌─────────────────────────────────────────────────────┐
│              Next.js Frontend (Fork von CIPP)        │
│       Next.js 16 / React 19 / MUI → eigenes DS      │
└───────────────────────┬─────────────────────────────┘
                        │ REST API
┌───────────────────────▼─────────────────────────────┐
│                  FastAPI Backend                     │
│         Direkte Graph API Calls + Batch API          │
│         Multi-Tenant Token Manager (PostgreSQL)      │
└──────┬────────────────────────────────┬─────────────┘
       │                                │
┌──────▼──────┐                ┌────────▼────────┐
│ PostgreSQL  │                │   PS-Runner     │
│ Token Cache │                │   Container     │
│ Tenant Data │                │ (Exchange only) │
│ Audit Logs  │                └─────────────────┘
└─────────────┘
```

---

## Tech Stack

| Layer | Technologie |
|-------|-------------|
| Frontend | Next.js 16 (CIPP Fork) |
| UI | MUI v6 → schrittweise eigenes System |
| State | Redux Toolkit + React Query (bereits in CIPP) |
| Backend | FastAPI (Python 3.12+) |
| ORM / DB | SQLAlchemy 2.0 (async) + asyncpg |
| Datenbank | PostgreSQL 16 |
| Migrations | Alembic |
| Auth | MSAL / Azure AD, GDAP Client Credentials |
| Graph Client | httpx (async) |
| Exchange Fallback | PowerShell Runner Container |
| Deployment | Railway (Backend + DB + PS-Runner), Vercel/Railway (Frontend) |
| CI/CD | GitHub Actions |

---

## Ordnerstruktur

### Frontend (Fork von CIPP)
```
CIPP/
├── src/
│   ├── api/           # API-Aufrufe → auf unser Backend umbiegen
│   ├── components/    # Wiederverwendbare UI-Komponenten
│   ├── contexts/      # React Context Provider
│   ├── data/          # Statische Daten/Konfigurationen
│   ├── hooks/         # Custom React Hooks
│   ├── layouts/       # Seitenlayouts
│   ├── pages/         # Next.js Pages (Routing)
│   ├── sections/      # Feature-Abschnitte
│   ├── store/         # Redux Store
│   ├── theme/         # MUI-Theme
│   └── utils/         # Hilfsfunktionen
├── public/
├── next.config.js
└── package.json
```

### Backend (Neubau)
```
cipp-backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py       # Settings (Pydantic BaseSettings)
│   │   ├── auth.py         # GDAP Token Manager
│   │   ├── graph.py        # Graph API Client + Batch
│   │   └── database.py     # SQLAlchemy async engine + session
│   ├── models/
│   │   ├── tenant.py       # Tenant SQLAlchemy model
│   │   ├── token_cache.py  # Token Cache model
│   │   └── audit.py        # Audit Log model
│   ├── schemas/
│   │   └── *.py            # Pydantic request/response schemas
│   ├── routers/
│   │   ├── tenants.py      # Tenant Management
│   │   ├── users.py        # User Management
│   │   ├── groups.py       # Gruppen
│   │   ├── licenses.py     # Lizenz Management
│   │   ├── security.py     # MFA, CA Policies, Defender
│   │   ├── mailbox.py      # Exchange (→ PS Runner)
│   │   ├── intune.py       # Endpoint/Intune Management
│   │   └── standards.py    # Standards Deployment
│   └── services/
│       ├── graph_service.py   # Business Logic für Graph
│       └── ps_runner.py       # PowerShell Sidecar Client
├── migrations/                # Alembic
│   ├── env.py
│   └── versions/
├── ps_runner/
│   ├── Dockerfile
│   └── runner.ps1
├── alembic.ini
├── Dockerfile
├── requirements.txt
├── docker-compose.yml         # Lokale Entwicklung
└── railway.toml
```

---

## Feature-Priorisierung

CIPP hat einen riesigen Feature-Umfang. Statt alles auf einmal anzugehen, priorisieren wir nach Nutzungshäufigkeit und Komplexität:

### Priorität 1 — Kern (muss funktionieren)
- Tenant Management (Liste, Onboarding, Config)
- User Management (CRUD, Liste, Details)
- Lizenzen (Zuweisung, Übersicht, SKUs)
- MFA Status & Auth Methods
- Conditional Access Policies
- Gruppen (CRUD, Mitglieder)
- Sign-in Logs & Audit Logs

### Priorität 2 — Security & Compliance
- Defender Alerts & Incidents
- Secure Score
- Risky Users & Sign-ins
- Standards / Best Practice Analyzer

### Priorität 3 — Exchange (PS-Runner nötig)
- Mailbox Management
- Transport Rules
- Spam Filter / Quarantine
- Mailbox Permissions

### Priorität 4 — Endpoint / Intune
- Device Management
- Compliance Policies
- App Deployment (Store, Choco, Office)
- Autopilot

### Priorität 5 — Erweitert
- GDAP Management (Relationships, Invites)
- Teams & SharePoint
- Integrationen (Halo, NinjaOne, Hudu)
- Tools (Graph Explorer, Message Trace, Breach Lookup)

---

## Phase 1 — Repo Setup & Infrastruktur

**Dauer: ~2 Tage**

### Schritte

```bash
# 1. CIPP Frontend forken
gh repo fork KelvinTegelaar/CIPP --clone --remote
cd CIPP
git remote add upstream https://github.com/KelvinTegelaar/CIPP.git

# 2. Backend Repo erstellen
mkdir cipp-backend && cd cipp-backend
git init
```

### PostgreSQL Setup

```sql
-- Datenbank erstellen
CREATE DATABASE cipp;

-- Tabellen werden via Alembic Migrations erstellt
-- Hier das Schema als Referenz:

-- Token Cache
CREATE TABLE tenant_tokens (
    tenant_id     TEXT PRIMARY KEY,
    access_token  TEXT NOT NULL,
    expires_at    TIMESTAMPTZ NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Tenant Liste
CREATE TABLE tenants (
    id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id     TEXT UNIQUE NOT NULL,
    display_name  TEXT,
    default_domain TEXT,
    onboarded_at  TIMESTAMPTZ DEFAULT NOW(),
    is_active     BOOLEAN DEFAULT TRUE
);

-- Audit Log
CREATE TABLE audit_logs (
    id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id     TEXT REFERENCES tenants(tenant_id),
    action        TEXT NOT NULL,
    endpoint      TEXT,
    user_agent    TEXT,
    request_body  JSONB,
    response_code INT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
```

### Azure App Registration
- Neue App Registration im Partner Tenant anlegen
- Permissions: `https://graph.microsoft.com/.default` (Application)
- GDAP: Granular Delegated Admin Privileges für Kunden-Tenants
- Client Secret generieren und sicher speichern

### Docker Compose (lokale Entwicklung)

```yaml
version: "3.8"
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: cipp
      POSTGRES_USER: cipp
      POSTGRES_PASSWORD: cipp_dev
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://cipp:cipp_dev@db:5432/cipp
      AZURE_TENANT_ID: ${AZURE_TENANT_ID}
      AZURE_CLIENT_ID: ${AZURE_CLIENT_ID}
      AZURE_CLIENT_SECRET: ${AZURE_CLIENT_SECRET}
      PS_RUNNER_URL: http://ps-runner:8001
    depends_on:
      - db

  ps-runner:
    build: ./ps_runner
    ports:
      - "8001:8001"

volumes:
  pgdata:
```

---

## Phase 2 — Database Layer & Auth

**Dauer: ~3–5 Tage**

### Database Setup (`app/core/database.py`)

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session
```

### Token Manager (`app/core/auth.py`)

```python
import httpx
from datetime import datetime, timedelta
from sqlalchemy import select, text
from app.core.database import async_session
from app.models.token_cache import TenantToken
from app.core.config import settings

async def get_token_for_tenant(tenant_id: str) -> str:
    async with async_session() as session:
        # 1. Cache check
        result = await session.execute(
            select(TenantToken).where(
                TenantToken.tenant_id == tenant_id,
                TenantToken.expires_at > datetime.utcnow()
            )
        )
        cached = result.scalar_one_or_none()

        if cached:
            return cached.access_token

        # 2. Neuen Token via GDAP holen
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.azure_client_id,
                    "client_secret": settings.azure_client_secret,
                    "scope": "https://graph.microsoft.com/.default"
                }
            )
            token_data = response.json()

        access_token = token_data["access_token"]
        expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"] - 60)

        # 3. In PostgreSQL cachen (upsert)
        await session.execute(
            text("""
                INSERT INTO tenant_tokens (tenant_id, access_token, expires_at, updated_at)
                VALUES (:tid, :token, :exp, NOW())
                ON CONFLICT (tenant_id)
                DO UPDATE SET access_token = :token, expires_at = :exp, updated_at = NOW()
            """),
            {"tid": tenant_id, "token": access_token, "exp": expires_at}
        )
        await session.commit()

        return access_token
```

---

## Phase 3 — FastAPI Grundgerüst + Graph Client

**Dauer: ~3–5 Tage**

### Graph Client (`app/core/graph.py`)

```python
import httpx
from app.core.auth import get_token_for_tenant

class GraphClient:
    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    async def _headers(self):
        token = await get_token_for_tenant(self.tenant_id)
        return {"Authorization": f"Bearer {token}"}

    async def get(self, endpoint: str, params: dict = None):
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE_URL}{endpoint}",
                headers=await self._headers(),
                params=params
            )
            r.raise_for_status()
            return r.json()

    async def post(self, endpoint: str, body: dict):
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.BASE_URL}{endpoint}",
                headers=await self._headers(),
                json=body
            )
            r.raise_for_status()
            return r.json()

    async def patch(self, endpoint: str, body: dict):
        async with httpx.AsyncClient() as client:
            r = await client.patch(
                f"{self.BASE_URL}{endpoint}",
                headers=await self._headers(),
                json=body
            )
            r.raise_for_status()
            return r.json()

    async def delete(self, endpoint: str):
        async with httpx.AsyncClient() as client:
            r = await client.delete(
                f"{self.BASE_URL}{endpoint}",
                headers=await self._headers()
            )
            r.raise_for_status()

    async def batch(self, requests: list[dict]):
        """Graph Batch API — bis 20 Requests in 1 HTTP Call."""
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.BASE_URL}/$batch",
                headers=await self._headers(),
                json={"requests": requests}
            )
            return r.json()
```

### Erste Prio-1-Endpoints

```python
# app/routers/users.py
from fastapi import APIRouter
from app.core.graph import GraphClient

router = APIRouter(prefix="/api/tenants/{tenant_id}/users", tags=["users"])

@router.get("")
async def list_users(tenant_id: str):
    graph = GraphClient(tenant_id)
    return await graph.get("/users", params={
        "$select": "id,displayName,userPrincipalName,assignedLicenses,accountEnabled",
        "$top": 999
    })

@router.get("/{user_id}")
async def get_user(tenant_id: str, user_id: str):
    graph = GraphClient(tenant_id)
    return await graph.get(f"/users/{user_id}")

@router.get("/mfa-status")
async def mfa_status(tenant_id: str):
    graph = GraphClient(tenant_id)
    users = await graph.get("/users", params={"$select": "id,displayName", "$top": 20})
    batch_requests = [
        {"id": str(i), "method": "GET", "url": f"/users/{u['id']}/authentication/methods"}
        for i, u in enumerate(users["value"])
    ]
    return await graph.batch(batch_requests)
```

### Main (`app/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, tenants, groups, licenses, security

app = FastAPI(title="CIPP Backend", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(tenants.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(licenses.router)
app.include_router(security.router)
```

---

## Phase 4 — Prio-1 Features komplett

**Dauer: ~3–4 Wochen**

Alle Kern-Endpoints implementieren:

| Feature | Graph Endpoint | Status |
|---------|---------------|--------|
| Tenant Liste | `GET /contracts` + `GET /domains` | |
| User Liste | `GET /users` | |
| User erstellen | `POST /users` | |
| User bearbeiten | `PATCH /users/{id}` | |
| User löschen | `DELETE /users/{id}` | |
| Lizenzen anzeigen | `GET /users/{id}/licenseDetails` | |
| Lizenzen zuweisen | `POST /users/{id}/assignLicense` | |
| Subscribed SKUs | `GET /subscribedSkus` | |
| MFA Status | `GET /users/{id}/authentication/methods` | |
| CA Policies | `GET /identity/conditionalAccess/policies` | |
| CA Policy CRUD | `POST/PATCH/DELETE .../policies` | |
| Gruppen | `GET /groups` | |
| Gruppen CRUD | `POST/PATCH/DELETE /groups` | |
| Gruppenmitglieder | `GET /groups/{id}/members` | |
| Sign-in Logs | `GET /auditLogs/signIns` | |
| Audit Logs | `GET /auditLogs/directoryAudits` | |

**Parallel: Frontend `src/api/` Layer auf unser Backend umbiegen.**

---

## Phase 5 — Prio-2: Security & Standards

**Dauer: ~2–3 Wochen**

| Feature | Graph Endpoint |
|---------|---------------|
| Defender Alerts | `GET /security/alerts_v2` |
| Incidents | `GET /security/incidents` |
| Secure Score | `GET /security/secureScores` |
| Risky Users | `GET /identityProtection/riskyUsers` |
| Risky Sign-ins | `GET /identityProtection/riskyServicePrincipals` |

Standards/Best Practice Analyzer: Eigene Logik die Graph-Daten gegen definierte Regeln prüft.

---

## Phase 6 — PowerShell Runner (Exchange)

**Dauer: ~1–2 Wochen**

Für Exchange-Cmdlets ohne Graph-Equivalent:
- `Get-MailboxPermission`
- `Set-Mailbox`
- `Get-TransportRule` / `Set-TransportRule`
- `Set-CASMailbox`
- `Get-/Set-HostedContentFilterPolicy`

### PS-Runner Container

```dockerfile
FROM mcr.microsoft.com/powershell:latest
WORKDIR /app
COPY runner.ps1 .
# Module EINMALIG beim Build — nicht beim Start
RUN pwsh -Command "Install-Module ExchangeOnlineManagement -Force -AllowClobber"
EXPOSE 8001
CMD ["pwsh", "-File", "runner.ps1"]
```

**Wichtig:** Der PS-Runner akzeptiert keine rohen Befehle (Sicherheitsrisiko). Stattdessen vordefinierte Actions mit parametrisierten Cmdlets.

---

## Phase 7 — Prio-4: Intune / Endpoint

**Dauer: ~2–3 Wochen**

| Feature | Graph Endpoint |
|---------|---------------|
| Devices | `GET /deviceManagement/managedDevices` |
| Compliance Policies | `GET /deviceManagement/deviceCompliancePolicies` |
| Config Profiles | `GET /deviceManagement/deviceConfigurations` |
| Apps | `GET /deviceAppManagement/mobileApps` |
| Autopilot | `GET /deviceManagement/windowsAutopilotDeviceIdentities` |

---

## Phase 8 — Prio-5: Erweiterungen & Integrationen

**Dauer: ~4+ Wochen (laufend)**

- GDAP Management
- Teams & SharePoint Administration
- Integrationen (Halo PSA, NinjaOne, Hudu)
- Tools (Message Trace, Breach Lookup, DNS Analyse)
- Custom Reporting

---

## Phase 9 — Deployment

**Dauer: ~2–3 Tage**

### Railway Setup

```toml
# railway.toml
[build]
builder = "dockerfile"

[[services]]
name = "cipp-api"
source = "."

[[services]]
name = "ps-runner"
source = "./ps_runner"
```

### Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/cipp
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
PS_RUNNER_URL=http://ps-runner:8001
```

### Frontend

```env
NEXT_PUBLIC_API_URL=https://cipp-api.railway.app
```

---

## Gesamtübersicht

| Phase | Inhalt | Dauer |
|-------|--------|-------|
| 1 | Repo Setup, Azure App, PostgreSQL, Docker Compose | ~2 Tage |
| 2 | Database Layer, Auth & Token Manager | ~3–5 Tage |
| 3 | FastAPI Grundgerüst + Graph Client | ~3–5 Tage |
| 4 | Prio-1: Identity, Tenants, Lizenzen, CA, Gruppen, Logs | ~3–4 Wochen |
| 5 | Prio-2: Security, Defender, Standards | ~2–3 Wochen |
| 6 | PS-Runner Container (Exchange) | ~1–2 Wochen |
| 7 | Prio-4: Intune / Endpoint Management | ~2–3 Wochen |
| 8 | Prio-5: GDAP, Teams, SharePoint, Integrationen | ~4+ Wochen |
| 9 | Deployment Railway + Frontend | ~2–3 Tage |

**Gesamt: ~14–18 Wochen für vollständige Feature Parity**
**Bis MVP (Phase 1–4): ~5–6 Wochen**

---

## Warum das besser ist als CIPP

| | CIPP | Unser Stack |
|--|------|-------------|
| Startup Zeit | 30–60s (PS Module Download) | <1s |
| Backend | PowerShell Azure Functions | FastAPI (Python) |
| Datenbank | Azure Table Storage / limitiert | PostgreSQL (vollwertig) |
| Kosten | Azure Functions (teuer bei Scale) | Railway (günstiger) |
| Graph Calls | Seriell via PS Cmdlets | Batch API (bis 20x schneller) |
| Wartbarkeit | PS1 Module, Azure-spezifisch | Standard Python, portabel |
| Self-hosted | Kompliziert (Azure-Abhängigkeit) | Docker Compose, einfach |
| Token Caching | Limitiert | PostgreSQL, persistent + queryable |
| Exchange | PS Module bei jedem Start laden | Vorinstalliert im Container |
