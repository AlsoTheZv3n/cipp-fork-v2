# CIPP Fork v2

> Experimenteller Fork von [KelvinTegelaar/CIPP](https://github.com/KelvinTegelaar/CIPP) mit einem komplett neuen FastAPI-Backend als Ersatz fuer die PowerShell Azure Functions.

## Hinweis

Dieses Projekt basiert auf dem grossartigen [CIPP (CyberDrain Improved Partner Portal)](https://github.com/KelvinTegelaar/CIPP) von **Kelvin Tegelaar** und der CIPP-Community. Alle Credits fuer das originale Frontend und die Idee dahinter gehoeren dem urspruenglichen Projekt.

Ich habe diesen Fork **rein aus Lerngruenden und Interesse** erstellt — keine kommerziellen Absichten, kein Unternehmen dahinter. Das einzige Ziel ist es, das Problem mit den langsamen PowerShell-Modul-Downloads beim Backend-Start zu loesen und dabei moderne Technologien zu lernen.

**Was hier anders ist:**
- Backend: FastAPI (Python) statt PowerShell Azure Functions
- Datenbank: PostgreSQL statt Azure Table Storage
- Graph API: Direkte async HTTP Calls statt serielle PS-Cmdlets
- Exchange: Isolierter PS-Runner Container (Module nur einmal beim Build geladen)
- Auth: MSAL OAuth2 mit JWT Sessions statt Azure Static Web Apps
- MCP Server: AI-Anbindung fuer Tenant-Verwaltung via Model Context Protocol

## Original-Projekt

- **CIPP Frontend**: [KelvinTegelaar/CIPP](https://github.com/KelvinTegelaar/CIPP)
- **CIPP Backend (Original)**: [KelvinTegelaar/CIPP-API](https://github.com/KelvinTegelaar/CIPP-API)
- **Dokumentation**: [docs.cipp.app](https://docs.cipp.app)
- **Website**: [cipp.app](https://cipp.app)

---

## Architektur

```
Frontend (Next.js 16 / React 19)
    |
    | REST API (482 Endpoints, CIPP-kompatibel)
    v
FastAPI Backend (Python)
    |--- PostgreSQL 16 (Tenants, Tokens, Users, Standards, Templates, Logs)
    |--- Microsoft Graph API (async httpx, Batch API, Auto-Pagination)
    |--- PS-Runner Container (Exchange Online Cmdlets)
    |--- MCP Server (AI-Anbindung)
```

## Tech Stack

| Layer | Technologie |
|-------|-------------|
| Frontend | Next.js 16, React 19, MUI, Redux Toolkit, React Query |
| Backend | FastAPI, Python 3.12+, uvicorn |
| Datenbank | PostgreSQL 16, SQLAlchemy 2.0 (async), Alembic |
| Graph Client | httpx (async), Batch API, Token Caching |
| Auth | MSAL OAuth2, Azure AD, JWT Session Cookies, RBAC |
| Exchange | PowerShell Runner Container (36 sichere Actions) |
| MCP | Model Context Protocol Server (21 Tools) |
| Deployment | Docker Compose (lokal), Railway (Produktion) |

---

## Schnellstart

### Voraussetzungen

- Python 3.12+
- Docker + Docker Compose
- Node.js 22+ (fuer Frontend)
- Azure AD App Registration (fuer Graph API Zugang)

### 1. Backend starten

```bash
cd backend

# .env aus Vorlage erstellen
cp .env.example .env
# → Azure Credentials in .env eintragen

# PostgreSQL starten
docker compose up -d db

# Python Dependencies installieren
pip install -r requirements.txt

# Datenbank-Migrationen ausfuehren
PYTHONPATH=. alembic upgrade head

# API starten
PYTHONPATH=. uvicorn app.main:app --host 127.0.0.1 --port 8055 --reload
```

Die API ist dann erreichbar unter `http://localhost:8055`. Swagger-Docs: `http://localhost:8055/docs`.

Im Dev-Modus (ohne Azure Credentials) gibt es einen Auto-Login als Admin unter `/.auth/callback?code=dev-mode`.

### 2. Frontend starten

```bash
# Im Root-Verzeichnis
yarn install
yarn dev
```

Das Frontend laeuft auf `http://localhost:3000` und verbindet sich ueber `NEXT_PUBLIC_API_URL` zum Backend.

### 3. PS-Runner starten (optional, fuer Exchange)

```bash
cd backend
docker compose up -d ps-runner
```

Der PS-Runner laedt die Exchange Module einmalig beim Docker-Build und stellt sie dann als HTTP-Microservice bereit. Ohne PS-Runner funktionieren alle Graph-basierten Features, nur Exchange-spezifische Cmdlets (Mailbox-Permissions, Transport Rules, Spam Filter etc.) sind nicht verfuegbar.

### 4. Alles zusammen (Docker Compose)

```bash
cd backend
docker compose up -d
```

Startet PostgreSQL + FastAPI + PS-Runner. Die API ist dann auf Port 8055 erreichbar.

---

## Backend-Struktur

```
backend/
├── app/
│   ├── main.py                 # FastAPI App (482 Endpoints)
│   ├── core/
│   │   ├── config.py           # Pydantic Settings
│   │   ├── database.py         # SQLAlchemy async Engine
│   │   ├── auth.py             # GDAP Token Manager (Graph API)
│   │   ├── graph.py            # Graph Client (GET/POST/PATCH/DELETE/Batch)
│   │   ├── session.py          # JWT Cookie Sessions
│   │   └── rbac.py             # Role-Based Access Control
│   ├── models/                 # SQLAlchemy Models (11 Tabellen)
│   │   ├── tenant.py           # Tenants
│   │   ├── token_cache.py      # Graph API Token Cache
│   │   ├── user.py             # CIPP Dashboard Users
│   │   ├── audit.py            # Audit Logs
│   │   ├── standard.py         # Standards + BPA Templates + Results
│   │   └── template.py         # Generic Templates, Scheduled Items, Logs
│   ├── routers/                # API Router (CIPP-kompatible Endpoints)
│   │   ├── auth.py             # /.auth/login, /.auth/me, /api/me
│   │   ├── tenants.py          # ListTenants, ListOrg, ListDomains
│   │   ├── tenant_admin.py     # Onboarding, Offboarding, Domains, OAuth
│   │   ├── users.py            # ListUsers, AddUser, EditUser, MFA
│   │   ├── user_extended.py    # Offboard, JIT Admin, TAP, Bulk Ops
│   │   ├── groups.py           # ListGroups, AddGroup, EditGroup
│   │   ├── licenses.py         # ListLicenses, BulkLicense
│   │   ├── security.py         # CA Policies, Alerts, Secure Score, Risky Users
│   │   ├── mailbox.py          # Mailboxes, Permissions, Rules (PS-Runner)
│   │   ├── exchange_extended.py # Calendar, OoO, Forwarding, Connectors
│   │   ├── email_security.py   # SafeLinks, AntiPhish, Spam, Quarantine (PS-Runner)
│   │   ├── intune.py           # Devices, Compliance, Apps, Autopilot
│   │   ├── intune_extended.py  # Templates, Reusable Settings, App Mgmt
│   │   ├── sharepoint.py       # Sites, Teams, OneDrive
│   │   ├── contacts.py         # Contacts, Rooms, Equipment
│   │   ├── gdap.py             # GDAP Relationships, Invites
│   │   ├── standards.py        # Standards Engine, BPA, Drift Detection
│   │   ├── settings.py         # Feature Flags, User Settings, Logs, DNS
│   │   ├── sam_partner.py      # SAM Setup, Backup, Templates, Misc
│   │   └── graph.py            # ListGraphRequest (Catch-All Proxy)
│   └── services/
│       ├── ps_runner.py        # PowerShell Runner HTTP Client
│       └── standards_engine.py # 11 Compliance Checks
├── migrations/                 # Alembic (4 Migrationen)
├── ps_runner/                  # PowerShell Sidecar Container
│   ├── Dockerfile
│   └── runner.ps1              # 36 sichere Exchange Actions
├── mcp_server.py               # MCP Server (21 AI Tools)
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Datenbank (PostgreSQL)

11 Tabellen, verwaltet via Alembic Migrationen:

| Tabelle | Zweck |
|---------|-------|
| `tenants` | Onboarded M365 Tenants |
| `tenant_tokens` | Graph API Token Cache (pro Tenant) |
| `cipp_users` | Dashboard-User mit Rollen + Permissions |
| `audit_logs` | API Audit Trail |
| `standard_templates` | Gespeicherte Standards-Vorlagen |
| `standard_results` | Ergebnisse von Standards-Checks |
| `bpa_templates` | Best Practice Analyzer Vorlagen |
| `cipp_templates` | Generische Templates (CA, Group, Contact, Filter etc.) |
| `cipp_scheduled_items` | Geplante Tasks, Alerts, Backups |
| `cipp_logs` | Applikations-Logs |
| `alembic_version` | Migrations-Tracking |

---

## Auth-System

Das Auth-System ersetzt Azure Static Web Apps komplett:

| Endpoint | Funktion |
|----------|----------|
| `GET /.auth/login/aad` | Redirect zu Azure AD Login |
| `GET /.auth/callback` | OAuth2 Callback, setzt JWT Cookie |
| `GET /.auth/me` | Session-Check (clientPrincipal) |
| `GET /.auth/logout` | Cookie loeschen + Redirect |
| `GET /api/me` | User-Daten + Rollen + Permissions |

**Dev-Modus:** Wenn `AUTH_TENANT_ID` leer ist, wird automatisch ein Admin-Login ohne Azure AD erstellt.

**Rollen:** `admin`, `editor`, `readonly` — konfigurierbar pro User in der Datenbank. Erster User bekommt automatisch Admin.

**RBAC:** `require_role("editor")` und `require_permission("tenant.write.*")` als FastAPI Dependencies verfuegbar.

---

## Standards Engine

11 automatisierte Compliance-Checks gegen die Microsoft Graph API:

| Check | Kategorie | Was geprueft wird |
|-------|-----------|-------------------|
| MFAForAdmins | Identity | CA Policy erzwingt MFA fuer Admin-Rollen |
| MFAForAllUsers | Identity | CA Policy erzwingt MFA fuer alle User |
| SecurityDefaults | Identity | Aktive CA Policies vorhanden |
| PasswordExpiry | Identity | Passwort-Ablauf < 365 Tage |
| SSPR | Identity | Self-Service Password Reset aktiviert |
| AdminAccountsLicensed | Identity | Alle Admins haben Lizenzen |
| GlobalAdminCount | Identity | 2-5 Global Admins |
| UnusedLicenses | Licensing | Lizenz-Auslastung > 50% |
| LegacyAuthBlocked | Identity | Legacy Auth via CA blockiert |
| GuestAccessRestricted | Identity | Gast-Zugriff eingeschraenkt |
| SecureScore | Security | Secure Score ueber Schwellenwert |

Ergebnisse werden in PostgreSQL gespeichert. Drift Detection vergleicht die letzten zwei Runs.

---

## PowerShell Runner

Isolierter Docker-Container fuer Exchange Online Cmdlets die kein Graph API Equivalent haben.

**Sicherheit:** Kein `Invoke-Expression` — jede Action ist eine dedizierte PowerShell-Funktion mit parametrisiertem Splatting.

**36 Actions** in Kategorien:
- Mailbox: get/set, Permissions, CAS
- Transport: Rules CRUD
- EOP: Spam, AntiPhish, Malware, SafeLinks, SafeAttachments
- Quarantine: Messages, Policies
- Message Trace
- Tenant Allow/Block Lists
- Exchange Connectors
- Shared/Room/Equipment Mailboxes
- Calendar Processing
- Restricted Users

**Connection Management:** Pro-Tenant Connection Cache mit 45 Min Expiry. Unterstuetzt Certificate-basierte und Client-Secret-basierte Auth.

---

## MCP Server (AI-Anbindung)

Der MCP Server ermoeglicht es AI-Assistenten (Claude, etc.) direkt mit der CIPP API zu interagieren.

### 21 Tools

| Kategorie | Tools |
|-----------|-------|
| **Tenants** | `list_tenants`, `onboard_tenant`, `get_tenant_details` |
| **Users** | `list_users`, `get_user`, `create_user`, `disable_user`, `reset_password`, `offboard_user` |
| **Security** | `get_security_alerts`, `get_risky_users`, `get_secure_score`, `list_conditional_access_policies`, `get_sign_in_summary` |
| **Standards** | `run_standards_check`, `list_available_checks` |
| **Groups** | `list_groups` |
| **Devices** | `list_devices`, `device_action` |
| **Licenses** | `list_licenses` |
| **Graph Proxy** | `graph_query` |

### Einrichtung

**Claude Code** (automatisch, wenn dieses Repo geoeffnet ist):
Die Config liegt in `.claude/settings.json`.

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "cipp": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/pfad/zu/CIPP/backend",
      "env": { "PYTHONPATH": "." }
    }
  }
}
```

**Standalone:**
```bash
cd backend
PYTHONPATH=. python mcp_server.py
```

### Beispiel-Interaktion

> "Zeig mir alle Tenants und pruefe die Compliance fuer contoso.onmicrosoft.com"

Die AI nutzt `list_tenants` → `run_standards_check("contoso.onmicrosoft.com")` und liefert einen Compliance-Bericht.

---

## Environment Variables

```env
# Datenbank
DATABASE_URL=postgresql+asyncpg://cipp:changeme@localhost:5433/cipp

# Azure AD / GDAP (fuer Graph API Calls zu Kunden-Tenants)
AZURE_TENANT_ID=your-partner-tenant-id
AZURE_CLIENT_ID=your-app-registration-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Azure AD / Auth (fuer CIPP Dashboard Login, leer = Dev-Mode Auto-Login)
AUTH_TENANT_ID=
AUTH_CLIENT_ID=
AUTH_CLIENT_SECRET=
JWT_SECRET=change-me-in-production

# PowerShell Runner
PS_RUNNER_URL=http://localhost:8001

# App
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
FRONTEND_URL=http://localhost:3000
```

---

## Lizenz

Dieses Projekt steht unter der gleichen [AGPL-3.0 Lizenz](LICENSE.md) wie das Original.
