# Ungetestete Features — Lizenz-/Tenant-Mangel

> Diese Features konnten nicht getestet werden weil der Test-Tenant
> keine Exchange Online Lizenz hat und kein zweiter Tenant fuer GDAP verfuegbar ist.

---

## 1. Exchange Online / EOP (PS-Runner)

**Voraussetzung:** Exchange Online Plan 1/2 oder Microsoft 365 Business/Enterprise Lizenz

### PS-Runner Container
- Container gebaut (`docker compose build ps-runner`) — startet, aber Exchange-Auth schlaegt fehl
- 36 Exchange Actions definiert in `ps_runner/runner.ps1` — keine davon real getestet
- Connection-Caching pro Tenant implementiert aber ungetestet

### Ungetestete Endpoints (39 PS-Runner Endpoints)

**Mailbox Management:**
- `GET /api/ListMailboxes` — Get-Mailbox
- `GET /api/ListMailboxPermissions` — Get-MailboxPermission
- `POST /api/ExecConvertMailbox` — Set-Mailbox -Type
- `POST /api/ExecEmailForward` — Set-Mailbox -ForwardingSmtpAddress
- `POST /api/ExecSetMailboxQuota` — Set-Mailbox -ProhibitSendReceiveQuota
- `POST /api/ExecSetMailboxEmailSize` — Set-Mailbox -MaxSendSize
- `POST /api/ExecSetLitigationHold` — Set-Mailbox -LitigationHoldEnabled
- `POST /api/ExecSetRetentionHold` — Set-Mailbox -RetentionHoldEnabled
- `POST /api/ExecCopyForSent` — Set-Mailbox -MessageCopyForSentAsEnabled
- `POST /api/ExecEnableArchive` — Enable-Mailbox -Archive
- `POST /api/ExecSetRecipientLimits` — Set-Mailbox -RecipientLimits
- `POST /api/ExecSetMailboxRetentionPolicies` — Set-Mailbox -RetentionPolicy

**CAS Mailbox:**
- `GET /api/ListMailboxCAS` — Get-CASMailbox (Protokoll-Settings)

**Transport Rules:**
- `GET /api/ListTransportRules` — Get-TransportRule
- `POST /api/AddTransportRule` — New-TransportRule
- `POST /api/RemoveTransportRule` — Remove-TransportRule

**Spam / Content Filter:**
- `GET /api/ListSpamfilter` — Get-HostedContentFilterPolicy
- `POST /api/EditSpamfilter` — Set-HostedContentFilterPolicy

**Anti-Phishing:**
- `GET /api/ListAntiPhishingFilters` — Get-AntiPhishPolicy
- `POST /api/EditAntiPhishingFilter` — Set-AntiPhishPolicy

**Malware Filter:**
- `GET /api/ListMalwareFilters` — Get-MalwareFilterPolicy
- `POST /api/EditMalwareFilter` — Set-MalwareFilterPolicy

**Safe Links / Safe Attachments:**
- `GET /api/ListSafeLinksPolicy` — Get-SafeLinksPolicy
- `GET /api/ListSafeAttachmentsFilters` — Get-SafeAttachmentPolicy

**Quarantine:**
- `GET /api/ListMailQuarantine` — Get-QuarantineMessage
- `GET /api/ListQuarantinePolicy` — Get-QuarantinePolicy
- `POST /api/ExecQuarantineManagement` — Release/Delete-QuarantineMessage

**Connection Filter:**
- `GET /api/ListConnectionFilter` — Get-HostedConnectionFilterPolicy
- `POST /api/AddConnectionFilter` — Set-HostedConnectionFilterPolicy

**Message Trace:**
- `GET /api/ListMessageTrace` — Get-MessageTrace

**Tenant Allow/Block:**
- `GET /api/ListTenantAllowBlockList` — Get-TenantAllowBlockListItems
- `POST /api/AddTenantAllowBlockList` — New-TenantAllowBlockListItems
- `POST /api/RemoveTenantAllowBlockList` — Remove-TenantAllowBlockListItems

**Restricted Users:**
- `GET /api/ListRestrictedUsers` — Get-BlockedSenderAddress
- `POST /api/ExecRemoveRestrictedUser` — Remove-BlockedSenderAddress

**Shared/Room/Equipment Mailboxes:**
- `POST /api/AddSharedMailbox` — New-Mailbox -Shared
- `POST /api/AddRoomMailbox` — New-Mailbox -Room
- `POST /api/AddEquipmentMailbox` — New-Mailbox -Equipment

### Was zum Testen benoetigt wird
1. M365 Business Basic oder hoeher Lizenz im Test-Tenant
2. Mindestens 1 User mit Mailbox
3. PS-Runner Container: `docker compose up ps-runner`
4. Exchange Online Management PowerShell Module (im Container vorinstalliert)

---

## 2. Multi-Tenant GDAP

**Voraussetzung:** Zweiter M365 Tenant + GDAP Relationship

### Ungetestete Features

**Tenant Onboarding via GDAP:**
- `POST /api/ExecOnboardTenant` — Mit GDAP-Berechtigung auf Kunden-Tenant zugreifen
- Token Manager fuer Cross-Tenant Calls (app/core/auth.py)
- Tenant-Wechsel im Frontend (Dropdown → anderer Tenant → neue Daten)

**GDAP Relationship Management:**
- `GET /api/ListGDAPRoles` — GDAP Rollen auflisten
- `GET /api/ListGDAPInvite` — GDAP Invites auflisten
- `POST /api/ExecGDAPInvite` — GDAP Invite erstellen
- `POST /api/ExecDeleteGDAPRelationship` — GDAP Relationship loeschen
- `POST /api/ExecGDAPAccessAssignment` — Access Assignment erstellen
- `POST /api/ExecAddGDAPRole` — Rolle zuweisen
- `POST /api/ExecDeleteGDAPRoleMapping` — Rolle-Mapping loeschen
- `GET /api/ListGDAPAccessAssignments` — Assignments auflisten

**AllTenants Modus:**
- `tenantFilter=AllTenants` — Daten von allen Tenants aggregieren
- Pagination deaktiviert im AllTenants-Modus
- `Tenant` Feld wird automatisch an jede Row angehaengt

### Was zum Testen benoetigt wird
1. Microsoft Partner Center Account
2. Zweiter M365 Tenant (z.B. Microsoft 365 Developer Program)
3. GDAP Relationship zwischen den Tenants
4. Azure App Registration mit GDAP Delegated Admin Permissions

---

## 3. Features die Graph Permissions brauchen die fehlen

Einige Graph API Endpoints geben 403 zurueck weil die App Registration
nicht alle Permissions hat. Diese Endpoints funktionieren technisch,
liefern aber leere Daten.

**Fehlende Permissions (aus cipp_logs DB):**
- `AuditLog.Read.All` — Sign-in Logs, Audit Logs
- `SecurityActions.ReadWrite.All` — Secure Score Write
- `Sites.Read.All` — SharePoint (Tenant hat keine SPO Lizenz)
- `DeviceManagement*` — Intune (Tenant hat keine Intune Lizenz)

---

## Wie man diese Features spaeter testet

### Exchange testen
```bash
# 1. M365 Lizenz kaufen/Trial aktivieren
# 2. PS-Runner starten
cd backend && docker compose up -d ps-runner

# 3. Testen
curl "http://localhost:8055/api/ListMailboxes?tenantFilter=YOUR_TENANT"
curl "http://localhost:8055/api/ListTransportRules?tenantFilter=YOUR_TENANT"
```

### Multi-Tenant testen
```bash
# 1. Zweiten Tenant erstellen (developer.microsoft.com/microsoft-365/dev-program)
# 2. GDAP Relationship aufbauen
# 3. Zweiten Tenant onboarden
curl -X POST "http://localhost:8055/api/ExecOnboardTenant" \
  -H "Content-Type: application/json" \
  -d '{"tenantId": "SECOND_TENANT_ID"}'

# 4. Tenant wechseln im Frontend
# → Dashboard zeigt Daten des zweiten Tenants
```
