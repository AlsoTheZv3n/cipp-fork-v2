# CIPP Fork v2 — Roadmap zur Production-Readiness

> Von Proof-of-Concept zu einem vollstaendig funktionalen CIPP-Ersatz.
> Priorisiert nach Frontend-Nutzung und Impact.

---

## Aktueller Stand

| Metrik | Wert |
|--------|------|
| Endpoints gesamt | 485 |
| Echte Graph Calls | 257 (53%) |
| PS-Runner Calls | 39 (8%) |
| DB Calls | 31 (6%) |
| **Placeholder Stubs** | **151 (31%)** |
| Auth + Proxy | 7 (2%) |
| Agent Audit | 33/33 |
| Frontend Pages ohne 500 | 25/25 |
| MCP Tools getestet | 6/6 |

---

## Iterationsplan

Jede Iteration hat:
1. **Ziel** — was wird verbessert
2. **Tasks** — konkrete Aufgaben
3. **Abgleich** — Vergleich mit Original-CIPP
4. **Tests** — wie wird verifiziert
5. **Commit** — was wird gepusht

---

## Iteration 1: Response-Formate 1:1 korrigieren
**Prioritaet: KRITISCH | Geschaetzte Dauer: 4-6h**

### Problem
Die CippResultsWrapperMiddleware ist ein Hack. Sie wrapped Arrays automatisch in `{Results: [...]}`, aber:
- Manche Endpoints brauchen `{Results: {MSResults: [...]}}` (nested)
- Manche POST-Responses brauchen `{Results: "string"}` als Message
- Die Middleware schluckt Error-Details
- Response-Headers gehen verloren

### Tasks
- [ ] Original CIPP-API Response-Formate dokumentieren (PowerShell Functions lesen)
- [ ] Middleware entfernen
- [ ] Jeden Router einzeln korrigieren mit `cipp_response()` Helper
- [ ] Spezialformate implementieren:
  - ExecAlertsList → `{Results: {MSResults: [...]}}`
  - ListGraphRequest → `{Results: [...], Metadata: {nextLink: "..."}}`
  - POST-Endpoints → `{Results: "Success message"}`
- [ ] Agent Audit auf 50+ Endpoints erweitern

### Abgleich mit Original
- Original: Jeder PowerShell Function Return ist spezifisch
- Wir: Middleware-Hack → muss weg

### Tests
```bash
python agents/cipp_agents.py --quick  # Erweitert auf 50+ Checks
```

### Dateien
- `backend/app/main.py` — Middleware entfernen
- `backend/app/routers/*.py` — Jeder Router einzeln
- `backend/app/core/response.py` — Helper erweitern

---

## Iteration 2: Pagination implementieren
**Prioritaet: HOCH | Geschaetzte Dauer: 3-4h**

### Problem
CippDataTable nutzt `ApiGetCallWithPagination` mit `Metadata.nextLink`. Bei Tenants mit >999 Items fehlen Daten.

### Tasks
- [ ] `Metadata.nextLink` in Graph Client durchreichen
- [ ] `cipp_response(data, next_link=graph_next_link)` nutzen
- [ ] ListGraphRequest: `nextLink` Query-Parameter akzeptieren und weiterleiten
- [ ] ListUsers, ListGroups, ListDevices: Pagination Support
- [ ] `AllTenants` Modus: Pagination deaktivieren

### Abgleich mit Original
- Original: Volle Pagination mit `@odata.nextLink`
- Wir: Kein Pagination → fehlt komplett

### Tests
```bash
# Test mit Tenant der >100 Users hat
curl "/api/ListUsers?tenantFilter=xxx&$top=10"
# Response muss Metadata.nextLink enthalten
```

### Dateien
- `backend/app/core/graph.py` — nextLink Support
- `backend/app/core/response.py` — Metadata Support
- `backend/app/routers/graph.py` — nextLink Parameter
- `backend/app/routers/users.py`, `groups.py`, etc.

---

## Iteration 3: Error-Handling verbessern
**Prioritaet: HOCH | Geschaetzte Dauer: 3-4h**

### Problem
`graph.get()` gibt bei jedem Fehler `{value: []}` zurueck. Das schluckt:
- 403 Forbidden (fehlende Permissions) → User sieht nichts statt Fehlermeldung
- 400 Bad Request (falsche Parameter) → stille Fehler
- 404 Not Found → keine Info

### Tasks
- [ ] GraphClient: Fehler-Details zurueckgeben statt leere Arrays
- [ ] Structured Error Response: `{Results: [], error: "Insufficient permissions", errorCode: 403}`
- [ ] Frontend-kompatibles Error-Format (getCippError Utility nutzt `data.error`, `data.message`)
- [ ] PS-Runner: Error-Details zurueckgeben statt `[]`
- [ ] Logging: Alle Graph-Fehler in `cipp_logs` Tabelle schreiben

### Abgleich mit Original
- Original: Detaillierte Fehlermeldungen in `Results`
- Wir: Stille Fehler, leere Arrays

### Tests
```bash
# Endpoint ohne Permission aufrufen
curl "/api/ListSignIns?tenantFilter=xxx"
# Muss Error-Message zurueckgeben, nicht leeres Array
```

### Dateien
- `backend/app/core/graph.py` — Error-Detail Handling
- `backend/app/services/ps_runner.py` — Error-Details
- `backend/app/routers/*.py` — Error-Responses

---

## Iteration 4: Placeholder durch echte Graph Calls ersetzen (Runde 1)
**Prioritaet: HOCH | Geschaetzte Dauer: 8-10h**

### Problem
151 Placeholder-Endpoints geben nur `{Results: "..."}` oder `[]` zurueck.

### Tasks — Die 50 meistgenutzten zuerst

**Templates (CRUD in DB — 20 Endpoints):**
- [ ] ListGroupTemplates, AddGroupTemplate, RemoveGroupTemplate
- [ ] ListCATemplates, AddCATemplate, RemoveCATemplate
- [ ] ListContactTemplates, AddContactTemplates, EditContactTemplates, RemoveContactTemplates
- [ ] ListSpamFilterTemplates, AddSpamfilterTemplate, RemoveSpamfilterTemplate
- [ ] ListTransportRulesTemplates, AddTransportTemplate, RemoveTransportRuleTemplate
- [ ] ListExConnectorTemplates, AddExConnectorTemplate, RemoveExConnectorTemplate
- [ ] ListSafeLinksPolicyTemplates, AddSafeLinksPolicyTemplate
- [ ] ListAssignmentFilterTemplates, AddAssignmentFilterTemplate

**Exchange Connectors (PS-Runner — 6 Endpoints):**
- [ ] ListExchangeConnectors → `get_inbound_connector` + `get_outbound_connector`
- [ ] AddExConnector, EditExConnector, RemoveExConnector

**Domain Health (DNS — 3 Endpoints):**
- [ ] ListDomainHealth → Echte DNS Checks (MX, SPF, DKIM, DMARC)
- [ ] ListDomainAnalyser → Batch-Analyse ueber alle Domains
- [ ] ExecDomainAnalyser → Analyse starten

**JIT Admin (PIM via Graph — 5 Endpoints):**
- [ ] ListJITAdmin → roleManagement/directory/roleEligibilityScheduleInstances
- [ ] ListJITAdminTemplates → DB CRUD
- [ ] ExecJitAdmin → PIM Role Activation
- [ ] ExecJITAdminSettings

**Misc haeufig genutzt:**
- [ ] ListDiagnosticsPresets → DB CRUD
- [ ] ListCustomVariables → DB CRUD
- [ ] ListIPWhitelist → DB CRUD
- [ ] ExecDomainAction → Graph Domain Verify/Delete
- [ ] ListMailboxRestores → PS-Runner
- [ ] ExecMailboxRestore → PS-Runner

### Abgleich mit Original
- Fuer jeden implementierten Endpoint: Response-Format mit Original vergleichen
- PowerShell Function in CIPP-API Repo lesen → gleichen Output generieren

### Tests
```bash
# Vorher: 151 Placeholder
# Nachher: <100 Placeholder
python agents/cipp_agents.py --quick  # Erweitert
```

---

## Iteration 5: Placeholder ersetzen (Runde 2) — Exchange/EOP
**Prioritaet: MITTEL | Geschaetzte Dauer: 6-8h**

### Problem
Exchange/EOP Features brauchen den PS-Runner der nie getestet wurde.

### Tasks
- [ ] PS-Runner Container starten und testen
- [ ] Exchange Online Connection mit echtem Tenant verifizieren
- [ ] Alle 39 PS-Runner Endpoints real testen:
  - Get-Mailbox, Get-MailboxPermission
  - Get-TransportRule, Get-HostedContentFilterPolicy
  - Get-AntiPhishPolicy, Get-MalwareFilterPolicy
  - Get-SafeLinksPolicy, Get-SafeAttachmentPolicy
  - Get-QuarantineMessage, Get-MessageTrace
- [ ] Fehlende PS-Runner Actions hinzufuegen
- [ ] Error-Handling fuer PS-Runner Timeouts

### Abgleich mit Original
- Original: Volle Exchange Integration
- Wir: PS-Runner gebaut, 0 getestet

### Voraussetzungen
- Exchange Online License im Test-Tenant
- PS-Runner Docker Container laeuft

### Tests
```bash
docker compose up ps-runner
curl "/api/ListMailboxes?tenantFilter=xxx"
curl "/api/ListTransportRules?tenantFilter=xxx"
```

---

## Iteration 6: Multi-Tenant GDAP Testing
**Prioritaet: MITTEL | Geschaetzte Dauer: 4-6h**

### Problem
Nur mit 1 eigenem Tenant getestet. GDAP (delegated admin) ist ungetestet.

### Tasks
- [ ] Zweiten Test-Tenant anlegen (Microsoft 365 Developer Program)
- [ ] GDAP Relationship zwischen Tenants aufbauen
- [ ] Token Manager fuer Multi-Tenant testen
- [ ] Tenant Onboarding Flow testen
- [ ] Tenant Switching im Frontend testen
- [ ] AllTenants Modus testen

### Abgleich mit Original
- Original: Hunderte MSPs nutzen GDAP mit dutzenden Kunden
- Wir: 1 Tenant

### Tests
- Tenant A → Tenant B Daten abrufen
- Tenant Dropdown wechseln → Daten aktualisieren

---

## Iteration 7: Frontend-Kompatibilitaet verbessern
**Prioritaet: MITTEL | Geschaetzte Dauer: 6-8h**

### Problem
Viele Seiten laden, aber zeigen falsche/keine Daten wegen Response-Format-Mismatches.

### Tasks
- [ ] CIPP Search reparieren (Navigation-Index)
- [ ] Jede CippTablePage Seite manuell testen (131 Seiten)
- [ ] Fehlende apiDataKey Formate:
  - `Results.MSResults` (Alerts)
  - `Results.0.authenticationMethodConfigurations` (Auth Methods)
- [ ] Offboarding Wizard testen
- [ ] User Edit/Create Flow testen
- [ ] Group Create/Edit Flow testen
- [ ] Conditional Access Policy Create/Edit Flow testen

### Abgleich mit Original
- Jede Seite im Original oeffnen, Screenshot machen
- Gleiche Seite in unserem Fork oeffnen, vergleichen

### Tests
- Browser-Tests fuer 20 kritische Seiten
- Screenshot-Vergleich

---

## Iteration 8: Placeholder ersetzen (Runde 3) — Admin/Settings
**Prioritaet: NIEDRIG | Geschaetzte Dauer: 4-6h**

### Tasks
- [ ] SAM Setup Flow (ExecSAMSetup, ExecCPVPermissions, etc.)
- [ ] Backup/Restore (ExecRunBackup mit echtem Tenant-Snapshot)
- [ ] Scheduled Items mit echtem Cron
- [ ] Extension Integrations Stubs (Halo, NinjaOne, Hudu Placeholders)
- [ ] Custom Roles mit echtem RBAC
- [ ] Notification Config mit echtem Email/Webhook

### Abgleich
- Original: Voll funktionale Admin-Seiten
- Wir: Placeholder

---

## Iteration 9: Performance & Optimization
**Prioritaet: NIEDRIG | Geschaetzte Dauer: 4-6h**

### Tasks
- [ ] Graph API Batch Requests nutzen (bis 20 Calls in 1 Request)
- [ ] Connection Pooling fuer httpx (nicht fuer jeden Call neuen Client)
- [ ] Redis Cache statt PostgreSQL fuer Token Cache
- [ ] Background Tasks fuer langlaufende Operations (Standards Check, BPA)
- [ ] Rate Limiting implementieren
- [ ] Response Compression (gzip)

### Abgleich
- Original: Azure Functions skalieren automatisch
- Wir: Single uvicorn Process

---

## Iteration 10: Production Deployment
**Prioritaet: NIEDRIG | Geschaetzte Dauer: 2-3h**

### Tasks
- [ ] Railway/Docker Deployment testen
- [ ] HTTPS mit Let's Encrypt
- [ ] Production .env Template finalisieren
- [ ] CI/CD Pipeline mit echten Tests
- [ ] Monitoring (Health Check Dashboard)
- [ ] Logging (strukturiert, JSON)
- [ ] Backup-Strategie fuer PostgreSQL

---

## Tracking-Tabelle

| Iteration | Prioritaet | Status | Placeholder vorher | Placeholder nachher | Dauer |
|-----------|-----------|--------|-------------------|-------------------|-------|
| 1. Response-Formate | KRITISCH | Offen | 151 | 151 | 4-6h |
| 2. Pagination | HOCH | Offen | 151 | 151 | 3-4h |
| 3. Error-Handling | HOCH | Offen | 151 | 151 | 3-4h |
| 4. Placeholder Runde 1 | HOCH | Offen | 151 | ~100 | 8-10h |
| 5. Exchange/EOP | MITTEL | Offen | ~100 | ~80 | 6-8h |
| 6. Multi-Tenant GDAP | MITTEL | Offen | ~80 | ~80 | 4-6h |
| 7. Frontend-Compat | MITTEL | Offen | ~80 | ~80 | 6-8h |
| 8. Admin/Settings | NIEDRIG | Offen | ~80 | ~40 | 4-6h |
| 9. Performance | NIEDRIG | Offen | ~40 | ~40 | 4-6h |
| 10. Production Deploy | NIEDRIG | Offen | ~40 | ~40 | 2-3h |

**Gesamt: ~45-60 Stunden ueber mehrere Sessions**

---

## Wie eine Iteration ablaeuft

```
1. Branch erstellen: git checkout -b iteration-X
2. Agent Audit (vorher): python agents/cipp_agents.py --quick
3. Tasks abarbeiten
4. Agent Audit (nachher): python agents/cipp_agents.py --quick
5. Tests: python -m pytest tests/ -v
6. Frontend testen: Browser-Check der betroffenen Seiten
7. Abgleich: Betroffene Endpoints mit Original-CIPP vergleichen
8. Commit + Push
9. PR erstellen mit Vorher/Nachher Vergleich
10. Merge nach main
```

## Original CIPP als Referenz

```bash
# Original CIPP-API klonen fuer Referenz
git clone https://github.com/KelvinTegelaar/CIPP-API.git ../CIPP-API-Reference
# PowerShell Functions lesen fuer Response-Format Referenz
ls ../CIPP-API-Reference/Modules/CIPPCore/Public/
```
