# CIPP Compatibility Matrix

This document compares the original CIPP (PowerShell Azure Functions backend) with this fork (FastAPI + direct Graph API backend). It covers feature parity, implementation status, and known limitations.

---

## Architecture Differences

| Aspect | Original CIPP | This Fork |
|--------|--------------|-----------|
| Backend | Azure Functions (PowerShell) | FastAPI (Python) |
| Database | Azure Table Storage | PostgreSQL (async SQLAlchemy) |
| Graph API access | Via PowerShell modules | Direct `httpx` calls via `GraphClient` |
| Exchange cmdlets | Native PowerShell | PS-Runner container (optional) |
| Auth | Azure Static Web Apps (SWA) | MSAL OAuth2 + cookie sessions |
| Hosting | Azure (SWA + Functions) | Any server (Docker, XAMPP, etc.) |
| MCP integration | None | Built-in MCP server (21 tools) |

---

## Feature Status by Area

### Legend

| Status | Meaning |
|--------|---------|
| Full | Fully implemented with real Graph API calls |
| Partial | Core functionality works, some sub-features missing |
| PS-Runner | Requires the PS-Runner container for Exchange PowerShell cmdlets |
| Placeholder | Endpoint exists for frontend compatibility but returns static/empty data |

---

### Dashboard

| Feature | Status | Notes |
|---------|--------|-------|
| Tenant overview | Full | `/api/ListTests` aggregates user/group/device counts, secure score |
| User counts | Full | Total, licensed, guests, enabled, disabled |
| Secure score display | Full | Current score, max score, percentage |
| Standards test results | Full | 11 real checks (MFA, CA policies, password, licenses, etc.) |
| Recent alerts | Full | Via `/api/GetCippAlerts` (empty) + security alerts via Graph |
| CIPP version info | Full | `/api/GetVersion`, `/version.json` |

### Tenant Management

| Feature | Status | Notes |
|---------|--------|-------|
| List tenants | Full | DB-backed, both `/api/ListTenants` and `/api/listTenants` |
| Onboard tenant | Full | Verifies Graph access, saves org info and domains |
| Offboard/remove tenant | Full | Deactivate or permanently remove from DB |
| Tenant details | Full | Organization, domains, subscribed SKUs |
| Tenant alignment | Full | Compares org info + CA policies |
| Tenant groups | Placeholder | Returns empty; grouping logic not implemented |
| External tenant info | Full | Organization details via Graph |

### User Management

| Feature | Status | Notes |
|---------|--------|-------|
| List users | Full | With full property selection, single-user lookup |
| Create user | Full | Via Graph `/users` POST |
| Edit user | Full | Via Graph PATCH |
| Delete user | Full | Via Graph DELETE |
| Bulk user creation | Full | Iterates and creates via Graph |
| Guest invitations | Full | Via Graph `/invitations` |
| Reset password | Full | With optional auto-generate |
| Disable/enable user | Full | Via Graph PATCH `accountEnabled` |
| Revoke sessions | Full | Via Graph `revokeSignInSessions` |
| User offboarding | Full | Disable + revoke + remove licenses + reset password + hide from GAL |
| MFA status | Full | Batch checks auth methods per user |
| MFA reset | Full | Deletes non-password auth methods |
| Temporary Access Pass | Full | Via Graph TAP methods |
| JIT Admin (PIM) | Full | Role activation via `roleAssignmentScheduleRequests` |
| Sign-in logs (per user) | Full | Via Graph audit logs |
| User groups | Full | Via Graph `memberOf` |
| User photo | Partial | GET works; SET requires PS-Runner for binary upload |
| Proxy addresses / aliases | Full | Via Graph PATCH |
| Mailbox details | PS-Runner | Exchange-specific mailbox properties |
| Mailbox rules | Full | Via Graph `messageRules` |
| Per-user MFA (legacy) | PS-Runner | Legacy MFA API not available in Graph |
| Password never expires | Full | Via Graph `passwordPolicies` |
| Clear ImmutableId | Full | Via Graph PATCH |
| License reprocessing | Full | Via Graph `reprocessLicenseAssignment` |
| Contact permissions | PS-Runner | Exchange-specific |
| User trusted/blocked senders | Placeholder | Returns empty |

### Group Management

| Feature | Status | Notes |
|---------|--------|-------|
| List groups | Full | With type detection (M365, Security, Distribution) |
| Create group | Full | Security and M365 groups |
| Edit group | Full | Via Graph PATCH |
| Delete group | Full | Via Graph DELETE |
| Create Team from group | Full | Creates M365 group + provisions Team |
| Group templates | Full | DB-backed CRUD |
| Hide from GAL | Full | Via Graph `hideFromAddressLists` |
| Delivery management | PS-Runner | Exchange `AcceptMessagesOnlyFromSendersOrMembers` |
| Default security groups | Full | Creates CIPP-Admins, CIPP-Editors, CIPP-Readers |

### License Management

| Feature | Status | Notes |
|---------|--------|-------|
| List licenses | Full | Subscribed SKUs with usage counts |
| Assign/remove licenses | Full | Bulk license operations via Graph |
| License search | Full | Search SKUs by name |
| License utilization check | Full | Standards check for underutilized licenses |
| CSP license management | Placeholder | Requires Partner Center API |

### Security

| Feature | Status | Notes |
|---------|--------|-------|
| Conditional Access policies | Full | Full CRUD + state labels |
| Named locations | Full | List + create/update |
| CA templates | Full | DB-backed CRUD |
| CA exclusions | Full | Add user exclusions to policies |
| Security alerts (Defender) | Full | List + update status/classification |
| Security incidents | Full | List + update |
| Secure score | Full | Score + control scores + improvement actions |
| Risky users | Full | List + detail + history + dismiss/confirm |
| Risky sign-ins | Full | Risk detections from Identity Protection |
| Risky service principals | Full | Identity Protection |
| Sign-in logs | Full | With OData filter support |
| Audit logs | Full | With OData filter support |
| Sign-in summary | Full | Success/failure counts, legacy auth detection |
| Directory roles | Full | With member counts (batch) |
| Role members | Full | Members of specific roles |
| Auth methods policy | Full | Authentication methods configuration |
| Auth methods activity | Full | User registration details |
| Threat intelligence | Full | TI indicators (if tenant supports it) |
| Breach search (HIBP) | Placeholder | Requires external HIBP API key |
| GeoIP lookup | Placeholder | Requires external GeoIP service |
| BitLocker key search | Full | Via Graph `recoveryKeys` |
| LAPS passwords | Full | Via Graph `deviceLocalCredentials` |
| BEC remediation | Full | Disable + revoke sessions |

### Exchange / Email

| Feature | Status | Notes |
|---------|--------|-------|
| Mailbox rules | Full | List + create + delete via Graph |
| Hide from GAL | Full | Via Graph `showInAddressList` |
| Mailbox locale | Full | Via Graph `mailboxSettings` |
| Out of Office | Full | Get + set via Graph `automaticRepliesSetting` |
| Calendar permissions | Full | List + update via Graph |
| Mailbox forwarding detection | Full | Checks `mailboxSettings` |
| Remove mailbox rule | Full | Via Graph DELETE |
| Mailbox list | PS-Runner | `Get-Mailbox` |
| Mailbox permissions | PS-Runner | `Get-MailboxPermission` |
| Transport rules | PS-Runner | `Get-TransportRule` |
| Spam filter | PS-Runner | `Get-HostedContentFilterPolicy` |
| Convert mailbox type | PS-Runner | `Set-Mailbox -Type` |
| Email forwarding config | PS-Runner | `Set-Mailbox -ForwardingSmtpAddress` |
| Archive mailbox | PS-Runner | `Enable-Mailbox -Archive` |
| Mailbox quota | PS-Runner | `Set-Mailbox -ProhibitSendReceiveQuota` |
| Litigation hold | PS-Runner | `Set-Mailbox -LitigationHoldEnabled` |
| Shared mailbox creation | Partial | Creates user via Graph; needs PS-Runner to convert type |
| Equipment/room mailboxes | PS-Runner | Exchange-specific resource types |
| Exchange connectors | PS-Runner | `Get-InboundConnector` / `Get-OutboundConnector` |
| CAS mailbox settings | PS-Runner | `Get-CASMailbox` |

### Email Security (EOP/MDO)

| Feature | Status | Notes |
|---------|--------|-------|
| Safe Links policies | PS-Runner | `Get-SafeLinksPolicy` |
| Anti-phishing filters | PS-Runner | `Get-AntiPhishPolicy` |
| Malware filters | PS-Runner | `Get-MalwareFilterPolicy` |
| Safe Attachments | PS-Runner | `Get-SafeAttachmentPolicy` |
| Spam filters | PS-Runner | `Get-HostedContentFilterPolicy` |
| Connection filters | PS-Runner | `Get-HostedConnectionFilterPolicy` |
| Quarantine management | PS-Runner | `Get-QuarantineMessage` |
| Message trace | PS-Runner | `Get-MessageTrace` |
| Tenant allow/block list | PS-Runner | `Get-TenantAllowBlockListItems` |
| Restricted users | PS-Runner | `Get-BlockedSenderAddress` |
| Defender state | Full | Inferred from secure score controls |
| Defender TVM alerts | Full | Via Graph security alerts with filter |
| MDO alerts | Full | Via Graph `alerts_v2` with service filter |

### Intune / Device Management

| Feature | Status | Notes |
|---------|--------|-------|
| List managed devices | Full | All device properties |
| Device actions | Full | Sync, reboot, retire, wipe, lock, reset passcode, Defender scan |
| Delete device | Full | Via Graph DELETE |
| Compliance policies | Full | List via Graph |
| Device configuration profiles | Full | Full CRUD + clone |
| Intune apps | Full | List via Graph |
| App deployment (Choco/WinGet/Office/Store) | Full | Create via Graph `mobileApps` |
| App assignment | Full | Assign to groups via Graph |
| App deletion | Full | Via Graph DELETE |
| Autopilot devices | Full | List + register + remove + assign + rename |
| Autopilot profiles | Full | Create + delete deployment profiles |
| Autopilot sync | Full | Trigger sync via Graph |
| Assignment filters | Full | CRUD via Graph |
| Policy assignment | Full | Assign policies to groups |
| BitLocker recovery keys | Full | Search + retrieve via Graph |
| Intune scripts | Full | List + edit + delete |
| Reusable policy settings | Full | CRUD via Graph |
| Apple DEP sync | Full | Trigger DEP sync |
| Apple VPP sync | Full | Trigger VPP license sync |
| App protection policies | Full | List via Graph |

### SharePoint and Teams

| Feature | Status | Notes |
|---------|--------|-------|
| List SharePoint sites | Full | Via Graph search |
| Site members | Full | Via Graph permissions |
| Create site (via group) | Full | Creates M365 group |
| Delete site | Full | Deletes associated group |
| SharePoint quota | Full | Root site quota info |
| SharePoint admin URL | Full | Derived from tenant domain |
| List Teams | Full | M365 groups with Team provisioning |
| Teams activity | Full | User activity report |
| Teams voice | Partial | Call records (limited data) |
| SharePoint permissions mgmt | Placeholder | Complex SP permissions not implemented |
| Bulk site creation | Placeholder | Returns success message |

### Contacts and Resources

| Feature | Status | Notes |
|---------|--------|-------|
| List contacts | Full | Org contacts via Graph |
| Create/edit/delete contact | Full | Full CRUD |
| Contact templates | Full | DB-backed CRUD + deployment |
| Room resources | Full | Via Graph `places` |
| Room lists | Full | Via Graph `places` |
| Equipment | Full | Via Graph `places` |

### GDAP

| Feature | Status | Notes |
|---------|--------|-------|
| List GDAP relationships | Full | Via Graph `delegatedAdminRelationships` |
| Create relationship | Full | Via Graph POST |
| Delete relationship | Full | Via Graph DELETE |
| Access assignments | Full | List + create + delete |
| Role templates | Placeholder | Returns static message |
| Auto-extend | Placeholder | Returns static message |

### Standards and Compliance

| Feature | Status | Notes |
|---------|--------|-------|
| Standards checks (11 checks) | Full | Real Graph API checks for MFA, CA, passwords, licenses, etc. |
| Standard templates | Full | DB-backed CRUD |
| Run checks against tenant | Full | Executes all checks and saves results |
| BPA (Best Practice Analyzer) | Full | Same engine as standards |
| BPA templates | Full | DB-backed CRUD |
| Standards comparison | Full | Latest results per tenant |
| Tenant drift detection | Full | Compares last two check runs |
| Access verification | Full | Tests Graph + Exchange connectivity |
| AD Connect status | Full | Sync status from organization data |
| Inactive accounts | Full | Users with no sign-in activity |
| Deleted items | Full | List + restore soft-deleted objects |

### Settings and Admin

| Feature | Status | Notes |
|---------|--------|-------|
| Extension config | Full | DB-backed CRUD |
| Feature flags | Full | DB-backed (all enabled by default) |
| User settings (theme, bookmarks) | Full | DB-backed |
| Custom roles | Full | DB-backed |
| Scheduled items | Full | DB-backed task scheduling |
| Notification config | Full | DB-backed |
| IP whitelist | Full | DB-backed |
| Custom variables | Full | DB-backed |
| Logs | Full | DB-backed application logs |
| Domain health (DNS) | Full | Real DNS checks via Google DNS API (MX, SPF, DMARC) |
| GitHub release notes | Full | Fetches from upstream CIPP repo |
| Backup/restore | Partial | Backup creates DB snapshot of CA + groups + SKUs; restore is manual |
| Alert queue | Full | DB-backed CRUD |
| Community repos | Full | DB-backed |
| Diagnostics presets | Partial | DB-backed storage; execution is placeholder |

### SAM / Partner

| Feature | Status | Notes |
|---------|--------|-------|
| SAM setup | Placeholder | Returns guidance to configure via Azure Portal |
| CPV permissions | Placeholder | Requires Partner Center integration |
| Multi-tenant app registration | Full | Via Graph `servicePrincipals` |
| API client (Graph proxy) | Full | Supports all HTTP methods |
| API permission list | Full | Returns required permissions |

### Authentication

| Feature | Status | Notes |
|---------|--------|-------|
| Azure AD OAuth2 login | Full | MSAL code flow |
| Dev mode auto-login | Full | Bypasses Azure AD when no credentials configured |
| Demo mode | Full | Synthetic data without real Azure credentials |
| Session management | Full | JWT cookies with roles/permissions |
| SWA-compatible `/.auth/me` | Full | Returns `clientPrincipal` in expected format |
| Role-based access | Full | First user gets admin; subsequent users get readonly |

---

## Known Limitations

1. **Exchange PowerShell cmdlets** -- Features requiring Exchange Online PowerShell (mailbox management, transport rules, EOP policies, quarantine, message trace) need the PS-Runner container running. Without it, these endpoints return helpful guidance messages instead of failing silently.

2. **Partner Center API** -- CSP license management, CPV operations, and partner-specific features are placeholders. They require Partner Center SDK integration which is not yet implemented.

3. **Binary file uploads** -- User photo upload and Intune app package upload require binary handling that is not yet implemented via the REST API.

4. **Legacy MFA API** -- Per-user MFA settings use a legacy Microsoft API not available through Graph. Requires PS-Runner with the MSOnline module.

5. **SharePoint advanced permissions** -- Fine-grained SharePoint site permissions management is complex and only partially implemented. Basic site CRUD works via the associated M365 group.

6. **No Azure Table Storage** -- The original CIPP uses Azure Table Storage extensively. This fork replaces all storage with PostgreSQL, which means existing CIPP data cannot be migrated directly.

7. **Webhook/event subscriptions** -- Real-time event subscriptions (Graph webhooks for alerts, sign-ins, etc.) are not yet implemented. The system uses polling via the frontend.

8. **Multi-region** -- The backend runs as a single instance. No Azure-native scaling or multi-region deployment is configured by default.

9. **Audit logging** -- While the DB stores logs, comprehensive audit logging of admin actions (who changed what, when) is minimal compared to the original CIPP's Azure Functions logging.

10. **Rate limiting** -- No built-in rate limiting for Graph API calls. High-volume operations (bulk user creation, full tenant scans) may hit Microsoft's throttling limits.
