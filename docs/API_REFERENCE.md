# CIPP API Reference

FastAPI backend for CIPP -- replacing PowerShell Azure Functions with direct Graph API calls.

**Base URL:** `/api/`
**Auth:** All endpoints except `/.auth/*` and `/api/health` require an authenticated session (cookie-based or dev-mode).

---

## Response Format

Most GET endpoints under `/api/` return arrays that are automatically wrapped by middleware:

```json
{"Results": [...]}
```

**Endpoints that return data directly (NOT wrapped):** `/.auth/me`, `/api/me`, `/api/health`, `/api/GetVersion`, `/api/ListTenants`, `/api/listTenants`, `/api/tenantFilter`, `/api/ListOrg`, `/api/ListuserCounts`, `/api/ListSharepointQuota`, `/api/ListTenantDetails`, `/api/listTenantDetails`, `/api/ListAzureADConnectStatus`, `/api/ExecUpdateSecureScore`, `/api/ListGraphRequest`, `/api/ExecBackendURLs`, `/api/ExecListAppId`, `/api/ListIntunePolicy`, `/api/ListAutopilotConfig`, `/api/ExecUniversalSearch`, `/api/ListNewUserDefaults`, `/api/ListDomainHealth`, `/api/ListBPATemplates`, `/api/ListSharePointAdminUrl`.

POST endpoints typically return `{"Results": "message"}` or `{"Results": {...}}`.

Endpoints under `/api/security/*` are also passed through unwrapped.

---

## Authentication

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/.auth/login/aad` | Redirect to Azure AD login (or dev-mode auto-login) | No |
| GET | `/.auth/callback` | OAuth2 callback -- exchanges code for session | No |
| GET | `/.auth/me` | Current user session (SWA-compatible format) | No |
| GET | `/.auth/logout` | Clear session and redirect | No |
| GET | `/api/me` | User info with roles and permissions | Yes |

---

## Tenants

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListTenants` | List all onboarded tenants from DB | Yes |
| GET | `/api/listTenants` | Same as ListTenants (case variant) | Yes |
| GET | `/api/tenantFilter` | Tenant dropdown options | Yes |
| GET | `/api/ListOrg` | Tenant organization details (Graph) | Yes |
| GET | `/api/ListDomains` | Tenant domains (Graph) | Yes |
| GET | `/api/listTenantDetails` | Detailed tenant info: org, domains, SKUs | Yes |
| GET | `/api/ListTenantDetails` | Org details for a single tenant | Yes |
| POST | `/api/AddTenant` | Onboard a new tenant to DB | Yes |
| POST | `/api/EditTenant` | Update tenant display name / domain | Yes |

---

## Tenant Administration

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/ExecOnboardTenant` | Verify Graph access and save tenant to DB | Yes |
| POST | `/api/ExecOffboardTenant` | Deactivate a tenant | Yes |
| POST | `/api/ExecRemoveTenant` | Permanently remove tenant from DB | Yes |
| POST | `/api/ExecExcludeTenant` | Exclude (deactivate) a tenant | Yes |
| POST | `/api/ExecAddTenant` | Alias for ExecOnboardTenant | Yes |
| GET | `/api/ListTenantOnboarding` | List tenants in onboarding state | Yes |
| POST | `/api/EditTenantOffboardingDefaults` | Update offboarding defaults (placeholder) | Yes |
| GET | `/api/ListTenantGroups` | List tenant groups (placeholder) | Yes |
| POST | `/api/ExecTenantGroup` | Process tenant group (placeholder) | Yes |
| POST | `/api/ExecRunTenantGroupRule` | Execute tenant group rule (placeholder) | Yes |
| GET | `/api/ListTenantAlignment` | Compare tenant config against baseline | Yes |
| GET | `/api/ListExternalTenantInfo` | External tenant organization info | Yes |
| POST | `/api/AddDomain` | Add a domain to tenant | Yes |
| POST | `/api/ExecDomainAction` | Verify or remove a domain | Yes |
| POST | `/api/ExecDnsConfig` | Get DNS records for a domain | Yes |
| GET | `/api/ListOAuthApps` | List service principals | Yes |
| GET | `/api/ListAppConsentRequests` | List pending consent requests | Yes |
| POST | `/api/ExecApplication` | Enable/disable/delete a service principal | Yes |
| GET | `/api/ListApplicationQueue` | Application queue (placeholder) | Yes |
| POST | `/api/ExecServicePrincipals` | List service principals (POST variant) | Yes |
| POST | `/api/ExecBrandingSettings` | Update organization branding | Yes |
| POST | `/api/ExecTimeSettings` | Time settings (requires PS-Runner) | Yes |
| POST | `/api/ExecPasswordConfig` | Update domain password policy | Yes |

---

## Users

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListUsers` | List users or get single user by UserId | Yes |
| GET | `/api/listUsers` | Simplified user list (id, displayName, UPN) | Yes |
| GET | `/api/ListuserCounts` | User counts: total, licensed, guests, enabled/disabled | Yes |
| GET | `/api/ListMFAUsers` | MFA registration status for users (batch) | Yes |
| GET | `/api/ListUsersAndGroups` | Combined users and groups listing | Yes |
| POST | `/api/AddUser` | Create a new user | Yes |
| POST | `/api/AddUserBulk` | Bulk create users | Yes |
| POST | `/api/AddGuest` | Invite a guest user | Yes |
| POST | `/api/EditUser` | Update user properties | Yes |
| POST | `/api/PatchUser` | Patch user properties (alternate) | Yes |
| POST | `/api/RemoveUser` | Delete a user | Yes |
| POST | `/api/ExecResetPass` | Reset user password | Yes |
| POST | `/api/ExecDisableUser` | Disable user account | Yes |
| POST | `/api/ExecRevokeSessions` | Revoke all user sessions | Yes |
| POST | `/api/ExecOffboardUser` | Full offboarding: disable, revoke, remove licenses, reset password | Yes |
| GET | `/api/ListUserSigninLogs` | Sign-in logs for a specific user | Yes |
| GET | `/api/ListUserGroups` | Groups a user belongs to | Yes |
| GET | `/api/ListUserMailboxDetails` | Mailbox details (PS-Runner) | Yes |
| GET | `/api/ListUserMailboxRules` | Mailbox inbox rules (Graph) | Yes |
| GET | `/api/ListContactPermissions` | Contact folder permissions (PS-Runner) | Yes |
| GET | `/api/ListUserTrustedBlockedSenders` | Trusted/blocked senders (placeholder) | Yes |
| GET | `/api/ListNewUserDefaults` | Default settings for new user creation | Yes |
| GET | `/api/ListCustomDataMappings` | Custom data mappings (placeholder) | Yes |
| GET | `/api/ListUserPhoto` | Get user profile photo | Yes |
| POST | `/api/ExecSetUserPhoto` | Set user photo (requires PS-Runner) | Yes |
| POST | `/api/EditUserAliases` | Update user proxy addresses | Yes |
| POST | `/api/AddUserDefaults` | Save user defaults (placeholder) | Yes |
| POST | `/api/RemoveUserDefaultTemplate` | Remove user default template (placeholder) | Yes |

### MFA and Authentication Methods

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/ExecResetMFA` | Delete all auth methods except password | Yes |
| POST | `/api/ExecPerUserMFA` | Per-user MFA (requires PS-Runner) | Yes |
| POST | `/api/SetAuthMethod` | Add phone auth method for user | Yes |
| POST | `/api/ExecSendPush` | Push notification (placeholder) | Yes |
| POST | `/api/ExecCreateTAP` | Create Temporary Access Pass | Yes |

### JIT Admin

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListJITAdmin` | List PIM eligible role assignments | Yes |
| GET | `/api/ListJITAdminTemplates` | JIT admin templates (placeholder) | Yes |
| POST | `/api/AddJITAdminTemplate` | Create JIT admin template | Yes |
| POST | `/api/EditJITAdminTemplate` | Update JIT admin template | Yes |
| POST | `/api/RemoveJITAdminTemplate` | Remove JIT admin template | Yes |
| POST | `/api/ExecJitAdmin` | Activate JIT admin role via PIM | Yes |
| POST | `/api/ExecJITAdminSettings` | Update JIT admin settings | Yes |

### Password and Account

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/ExecPasswordNeverExpires` | Set password to never expire | Yes |
| POST | `/api/ExecClrImmId` | Clear ImmutableId (AD sync) | Yes |
| POST | `/api/ExecHVEUser` | High-volume email (requires PS-Runner) | Yes |
| POST | `/api/ExecReprocessUserLicenses` | Reprocess license assignments | Yes |

---

## Groups

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListGroups` | List all groups in a tenant | Yes |
| POST | `/api/AddGroup` | Create a new group | Yes |
| POST | `/api/EditGroup` | Update group properties | Yes |
| POST | `/api/ExecGroupsDelete` | Delete a group | Yes |
| POST | `/api/AddGroupTeam` | Create M365 Group with Team | Yes |
| POST | `/api/AddTeam` | Alias for AddGroupTeam | Yes |
| GET | `/api/ListGroupTemplates` | List group templates (DB) | Yes |
| POST | `/api/AddGroupTemplate` | Create group template | Yes |
| POST | `/api/RemoveGroupTemplate` | Delete group template | Yes |
| POST | `/api/ExecGroupsDeliveryManagement` | Configure who can send to group (PS-Runner) | Yes |
| POST | `/api/ExecGroupsHideFromGAL` | Hide/show group in GAL | Yes |
| POST | `/api/ExecCreateDefaultGroups` | Create default CIPP security groups | Yes |

---

## Licenses

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListLicenses` | List subscribed SKUs for a tenant | Yes |
| GET | `/api/ListCSPsku` | List CSP SKUs (same as subscribed) | Yes |
| POST | `/api/ExecBulkLicense` | Assign/remove licenses for a user | Yes |
| GET | `/api/ListExcludedLicenses` | List excluded licenses (DB) | Yes |
| POST | `/api/ExecExcludeLicenses` | Exclude licenses | Yes |
| POST | `/api/ExecLicenseSearch` | Search licenses across tenants | Yes |
| GET | `/api/listCSPLicenses` | CSP licenses (placeholder) | Yes |
| POST | `/api/ExecCSPLicense` | CSP license management (placeholder) | Yes |

---

## Security

### Conditional Access

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListConditionalAccessPolicies` | List all CA policies with state labels | Yes |
| POST | `/api/AddCAPolicy` | Create a CA policy | Yes |
| POST | `/api/EditCAPolicy` | Update a CA policy | Yes |
| POST | `/api/RemoveCAPolicy` | Delete a CA policy | Yes |
| GET | `/api/ListNamedLocations` | List named locations | Yes |
| GET | `/api/ListCATemplates` | List CA templates (DB) | Yes |
| POST | `/api/AddCATemplate` | Create CA template | Yes |
| POST | `/api/RemoveCATemplate` | Delete CA template | Yes |
| POST | `/api/ExecCACheck` | Check CA policy coverage | Yes |
| POST | `/api/ExecCAExclusion` | Add exclusion to CA policy | Yes |
| POST | `/api/ExecCAServiceExclusion` | Service exclusion (alias) | Yes |
| POST | `/api/ExecNamedLocation` | Create/update named location | Yes |
| POST | `/api/AddNamedLocation` | Alias for ExecNamedLocation | Yes |

### Alerts and Incidents

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ExecAlertsList` | List security alerts (Defender) | Yes |
| GET | `/api/ExecIncidentsList` | List security incidents | Yes |
| POST | `/api/ExecSetSecurityAlert` | Update alert status/classification | Yes |
| POST | `/api/ExecSetSecurityIncident` | Update incident status/classification | Yes |

### Secure Score

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ExecUpdateSecureScore` | Get latest secure score with controls | Yes |
| GET | `/api/security/secureScoreControlProfiles` | Secure score improvement actions | Yes |

### Identity Protection

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/security/riskyUsers` | List risky users | Yes |
| GET | `/api/security/riskyUser/{user_id}` | Detailed risk info + history | Yes |
| POST | `/api/ExecDismissRiskyUser` | Dismiss risky users | Yes |
| POST | `/api/security/confirmCompromised` | Confirm users as compromised | Yes |
| GET | `/api/security/riskySignIns` | List risky sign-in events | Yes |
| GET | `/api/security/riskyServicePrincipals` | List risky service principals | Yes |

### Sign-in and Audit Logs

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListSignIns` | Sign-in logs with optional OData filter | Yes |
| GET | `/api/ListAuditLogs` | Directory audit logs with filter | Yes |
| GET | `/api/security/signInSummary` | Sign-in summary: success/failure, legacy auth | Yes |

### Roles

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListRoles` | Directory roles with member counts | Yes |
| GET | `/api/security/roleMembers/{role_id}` | Members of a specific role | Yes |

### Other Security

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/security/threatIntelligence` | Threat intelligence indicators | Yes |
| GET | `/api/security/authMethodsPolicy` | Authentication methods policy | Yes |
| GET | `/api/security/authMethodsActivity` | Auth methods registration activity | Yes |

---

## Exchange / Mailbox

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListMailboxes` | List mailboxes (PS-Runner) | Yes |
| GET | `/api/ListMailboxPermissions` | Mailbox permissions (PS-Runner) | Yes |
| GET | `/api/ListMailboxRules` | Mailbox inbox rules (Graph) | Yes |
| GET | `/api/ListTransportRules` | Transport rules (PS-Runner) | Yes |
| GET | `/api/ListSpamfilter` | Spam filter policies (PS-Runner) | Yes |
| GET | `/api/ListMailboxCAS` | CAS mailbox settings (PS-Runner) | Yes |
| GET | `/api/ListMailboxForwarding` | Mailboxes with forwarding configured | Yes |
| GET | `/api/ListSharedMailboxAccountEnabled` | Shared mailboxes with enabled accounts | Yes |
| POST | `/api/ExecConvertMailbox` | Convert mailbox type (PS-Runner) | Yes |
| POST | `/api/ExecEmailForward` | Configure forwarding (PS-Runner) | Yes |
| POST | `/api/ExecCopyForSent` | Enable copy for sent (PS-Runner) | Yes |
| POST | `/api/ExecEnableArchive` | Enable archive mailbox (PS-Runner) | Yes |
| POST | `/api/ExecEnableAutoExpandingArchive` | Auto-expanding archive (PS-Runner) | Yes |
| POST | `/api/ExecHideFromGAL` | Hide from GAL (Graph) | Yes |
| POST | `/api/ExecSetMailboxQuota` | Set mailbox quota (PS-Runner) | Yes |
| POST | `/api/ExecSetMailboxEmailSize` | Set max email size (PS-Runner) | Yes |
| POST | `/api/ExecSetMailboxLocale` | Set mailbox locale (Graph) | Yes |
| POST | `/api/ExecSetRecipientLimits` | Set recipient limits (PS-Runner) | Yes |
| POST | `/api/ExecSetLitigationHold` | Enable/disable litigation hold (PS-Runner) | Yes |
| POST | `/api/ExecSetRetentionHold` | Enable retention hold (PS-Runner) | Yes |
| POST | `/api/ExecMailboxRestore` | Mailbox restore (placeholder) | Yes |
| GET | `/api/ListMailboxRestores` | List mailbox restores (placeholder) | Yes |
| POST | `/api/ExecStartManagedFolderAssistant` | Start MFA (PS-Runner) | Yes |
| POST | `/api/ExecRemoveMailboxRule` | Remove mailbox rule (Graph) | Yes |
| POST | `/api/ExecSetMailboxRule` | Create mailbox rule (Graph) | Yes |
| POST | `/api/ExecSetMailboxRetentionPolicies` | Set retention policy (PS-Runner) | Yes |
| POST | `/api/ExecManageRetentionPolicies` | Manage retention policies (placeholder) | Yes |
| POST | `/api/ExecManageRetentionTags` | Manage retention tags (placeholder) | Yes |
| POST | `/api/AddSharedMailbox` | Create shared mailbox (Graph + PS-Runner) | Yes |
| POST | `/api/AddEquipmentMailbox` | Equipment mailbox (PS-Runner) | Yes |
| POST | `/api/EditEquipmentMailbox` | Edit equipment mailbox (PS-Runner) | Yes |
| POST | `/api/AddRoomMailbox` | Room mailbox (PS-Runner) | Yes |
| POST | `/api/EditRoomMailbox` | Edit room mailbox (PS-Runner) | Yes |
| POST | `/api/AddRoomList` | Room list (PS-Runner) | Yes |
| POST | `/api/EditRoomList` | Edit room list (PS-Runner) | Yes |

### Calendar

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListCalendarPermissions` | Calendar permissions (Graph) | Yes |
| POST | `/api/ExecEditCalendarPermissions` | Update calendar permissions | Yes |
| POST | `/api/ExecModifyCalPerms` | Alias for edit calendar permissions | Yes |
| POST | `/api/ExecSetCalendarProcessing` | Calendar processing (PS-Runner) | Yes |

### Out of Office

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListOoO` | Out of Office settings (Graph) | Yes |
| POST | `/api/ExecSetOoO` | Configure Out of Office (Graph) | Yes |
| POST | `/api/ExecScheduleOOOVacation` | Schedule OoO vacation | Yes |
| POST | `/api/ExecScheduleMailboxVacation` | Schedule mailbox vacation | Yes |

### Permissions and Connectors

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/ExecModifyContactPerms` | Contact folder permissions (PS-Runner) | Yes |
| POST | `/api/ExecModifyMBPerms` | Mailbox permissions (PS-Runner) | Yes |
| GET | `/api/ListExchangeConnectors` | Exchange connectors (placeholder) | Yes |
| GET | `/api/ListExConnectorTemplates` | Connector templates (placeholder) | Yes |
| POST | `/api/AddExConnector` | Create connector (PS-Runner) | Yes |
| POST | `/api/EditExConnector` | Update connector (PS-Runner) | Yes |
| POST | `/api/RemoveExConnector` | Remove connector (PS-Runner) | Yes |

### Transport Rules

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/AddTransportRule` | Create transport rule (PS-Runner) | Yes |
| POST | `/api/AddEditTransportRule` | Save transport rule (PS-Runner) | Yes |
| POST | `/api/RemoveTransportRule` | Remove transport rule (PS-Runner) | Yes |
| GET | `/api/ListTransportRulesTemplates` | Transport rule templates (placeholder) | Yes |

### GAL

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListGlobalAddressList` | Global Address List (Graph users) | Yes |

---

## Email Security

### Safe Links

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListSafeLinksPolicy` | Safe Links policies (PS-Runner) | Yes |
| POST | `/api/EditSafeLinksPolicy` | Edit Safe Links (PS-Runner) | Yes |
| POST | `/api/ExecNewSafeLinkspolicy` | Create Safe Links (PS-Runner) | Yes |
| POST | `/api/ExecDeleteSafeLinksPolicy` | Delete Safe Links (PS-Runner) | Yes |

### Anti-Phishing

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListAntiPhishingFilters` | Anti-phishing policies (PS-Runner) | Yes |
| POST | `/api/EditAntiPhishingFilter` | Edit anti-phishing (PS-Runner) | Yes |
| POST | `/api/RemoveAntiPhishingFilter` | Remove anti-phishing (PS-Runner) | Yes |

### Malware Filters

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListMalwareFilters` | Malware filter policies (PS-Runner) | Yes |
| POST | `/api/EditMalwareFilter` | Edit malware filter (PS-Runner) | Yes |

### Safe Attachments

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListSafeAttachmentsFilters` | Safe Attachments policies (PS-Runner) | Yes |
| POST | `/api/EditSafeAttachmentsFilter` | Edit Safe Attachments (PS-Runner) | Yes |

### Spam Filters

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/AddSpamFilter` | Create spam filter (PS-Runner) | Yes |
| POST | `/api/EditSpamfilter` | Edit spam filter (PS-Runner) | Yes |
| POST | `/api/RemoveSpamFilter` | Remove spam filter (PS-Runner) | Yes |

### Connection Filters

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListConnectionFilter` | Connection filter policies (PS-Runner) | Yes |
| POST | `/api/AddConnectionFilter` | Update connection filter (PS-Runner) | Yes |

### Quarantine

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListMailQuarantine` | Quarantined messages (PS-Runner) | Yes |
| GET | `/api/ListMailQuarantineMessage` | Specific quarantine message (PS-Runner) | Yes |
| GET | `/api/ListQuarantinePolicy` | Quarantine policies (PS-Runner) | Yes |
| POST | `/api/ExecQuarantineManagement` | Release/delete quarantined messages | Yes |

### Defender for Office 365

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListDefenderState` | Defender state from secure score | Yes |
| GET | `/api/ListDefenderTVM` | Defender TVM alerts | Yes |
| GET | `/api/ExecMdoAlertsList` | MDO-specific alerts | Yes |
| POST | `/api/ExecSetMdoAlert` | Update MDO alert | Yes |

### Tenant Allow/Block List

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListTenantAllowBlockList` | Tenant allow/block entries (PS-Runner) | Yes |
| POST | `/api/AddTenantAllowBlockList` | Add entries (PS-Runner) | Yes |
| POST | `/api/RemoveTenantAllowBlockList` | Remove entries (PS-Runner) | Yes |

### Message Trace

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListMessageTrace` | Message trace (PS-Runner) | Yes |

### Restricted Users

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListRestrictedUsers` | Restricted users (PS-Runner) | Yes |
| POST | `/api/ExecRemoveRestrictedUser` | Unblock restricted user (PS-Runner) | Yes |

---

## Intune / Device Management

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListDevices` | List managed devices | Yes |
| POST | `/api/ExecDeviceAction` | Remote device action (sync, reboot, wipe, etc.) | Yes |
| POST | `/api/ExecDeviceDelete` | Delete a managed device | Yes |
| GET | `/api/ListCompliancePolicies` | Device compliance policies | Yes |
| GET | `/api/ListApps` | Intune managed apps | Yes |
| GET | `/api/ListAPDevices` | Autopilot device identities | Yes |
| GET | `/api/ListIntuneTemplates` | Device configuration profiles | Yes |
| GET | `/api/ListIntuneScript` | Intune PowerShell scripts | Yes |
| GET | `/api/ListAssignmentFilters` | Intune assignment filters | Yes |
| GET | `/api/ListAppProtectionPolicies` | App protection policies | Yes |
| GET | `/api/ListIntunePolicy` | Combined device configs + compliance | Yes |
| GET | `/api/ListAutopilotConfig` | Autopilot deployment profiles | Yes |
| POST | `/api/ExecAssignPolicy` | Assign a policy to groups | Yes |
| POST | `/api/ExecGetRecoveryKey` | Get BitLocker recovery key | Yes |

### Configuration Templates

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/AddIntuneTemplate` | Create device config profile | Yes |
| POST | `/api/RemoveIntuneTemplate` | Delete device config profile | Yes |
| POST | `/api/ExecEditTemplate` | Update device config profile | Yes |
| POST | `/api/ExecCloneTemplate` | Clone a config profile | Yes |

### Reusable Settings

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListIntuneReusableSettings` | List reusable policy settings | Yes |
| POST | `/api/AddIntuneReusableSetting` | Create reusable setting | Yes |
| POST | `/api/RemoveIntuneReusableSetting` | Delete reusable setting | Yes |

### Scripts

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/EditIntuneScript` | Update Intune script | Yes |
| POST | `/api/RemoveIntuneScript` | Delete Intune script | Yes |

### Autopilot

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/AddAPDevice` | Register Autopilot device | Yes |
| POST | `/api/RemoveAPDevice` | Remove Autopilot device | Yes |
| POST | `/api/ExecAssignAPDevice` | Assign Autopilot device to user | Yes |
| POST | `/api/ExecRenameAPDevice` | Rename Autopilot device | Yes |
| POST | `/api/ExecSetAPDeviceGroupTag` | Set Autopilot group tag | Yes |
| POST | `/api/ExecSyncAPDevices` | Trigger Autopilot sync | Yes |
| POST | `/api/AddAutopilotConfig` | Create deployment profile | Yes |
| POST | `/api/RemoveAutopilotConfig` | Delete deployment profile | Yes |
| POST | `/api/ExecSyncDEP` | Sync Apple DEP devices | Yes |
| POST | `/api/ExecSyncVPP` | Sync Apple VPP tokens | Yes |

### App Management

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/AddChocoApp` | Create Win32 app from Chocolatey | Yes |
| POST | `/api/AddOfficeApp` | Create Office suite deployment | Yes |
| POST | `/api/AddStoreApp` | Add Microsoft Store app | Yes |
| POST | `/api/AddwinGetApp` | Add WinGet app | Yes |
| POST | `/api/ExecAssignApp` | Assign app to groups | Yes |
| POST | `/api/RemoveApp` | Delete an app | Yes |
| POST | `/api/ExecSetPackageTag` | Update app notes/tags | Yes |

### Policies

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/AddPolicy` | Create compliance/config policy | Yes |
| POST | `/api/RemovePolicy` | Delete a device policy | Yes |
| POST | `/api/AddEnrollment` | Create enrollment restriction | Yes |

### Assignment Filters

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/AddAssignmentFilter` | Create assignment filter | Yes |
| POST | `/api/EditAssignmentFilter` | Update assignment filter | Yes |
| POST | `/api/ExecAssignmentFilter` | Test assignment filter rule | Yes |

### Device Actions

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/ExecSetCloudManaged` | Set cloud management authority | Yes |
| POST | `/api/ExecDevicePasscodeAction` | Reset device passcode | Yes |

---

## SharePoint and Teams

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListSites` | List SharePoint sites | Yes |
| GET | `/api/ListSiteMembers` | Site members/permissions | Yes |
| POST | `/api/AddSite` | Create SharePoint site (via group) | Yes |
| POST | `/api/AddSiteBulk` | Bulk create sites (placeholder) | Yes |
| POST | `/api/DeleteSharepointSite` | Delete site group | Yes |
| GET | `/api/ListSharepointQuota` | SharePoint storage quota | Yes |
| GET | `/api/ListSharePointAdminUrl` | SharePoint admin URL | Yes |
| POST | `/api/ExecSharePointPerms` | Manage SP permissions (placeholder) | Yes |
| POST | `/api/ExecSetSharePointMember` | Add/remove SP member (placeholder) | Yes |
| GET | `/api/ListTeams` | List Teams (M365 groups with Team) | Yes |
| GET | `/api/ListTeamsActivity` | Teams user activity report | Yes |
| GET | `/api/ListTeamsVoice` | Teams voice (call records) | Yes |

---

## Contacts

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListContacts` | List org contacts or get by ID | Yes |
| POST | `/api/AddContact` | Create a new contact | Yes |
| POST | `/api/EditContact` | Update a contact | Yes |
| POST | `/api/RemoveContact` | Delete a contact | Yes |
| GET | `/api/ListEquipment` | List room resources (equipment) | Yes |
| GET | `/api/ListRooms` | List rooms | Yes |
| GET | `/api/ListRoomLists` | List room lists | Yes |
| GET | `/api/ListContactTemplates` | Contact templates (DB) | Yes |
| POST | `/api/AddContactTemplates` | Create contact template | Yes |
| POST | `/api/EditContactTemplates` | Update contact template | Yes |
| POST | `/api/RemoveContactTemplates` | Delete contact template | Yes |
| POST | `/api/DeployContactTemplates` | Deploy contacts from template | Yes |

---

## GDAP (Granular Delegated Admin Privileges)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListGDAPRoles` | List GDAP role definitions | Yes |
| GET | `/api/ListGDAPInvite` | List GDAP relationship invites | Yes |
| GET | `/api/ListGDAPAccessAssignments` | List access assignments for a relationship | Yes |
| POST | `/api/ExecGDAPInvite` | Create GDAP relationship | Yes |
| POST | `/api/ExecDeleteGDAPRelationship` | Delete GDAP relationship | Yes |
| POST | `/api/ExecGDAPAccessAssignment` | Create access assignment | Yes |
| POST | `/api/ExecGDAPRoleTemplate` | Manage role templates (placeholder) | Yes |
| POST | `/api/ExecAutoExtendGDAP` | Auto-extend relationships (placeholder) | Yes |
| POST | `/api/ExecAddGDAPRole` | Add GDAP role to relationship | Yes |
| POST | `/api/ExecDeleteGDAPRoleMapping` | Delete GDAP role mapping | Yes |
| POST | `/api/ExecGDAPRemoveGArole` | Remove GA role (alias) | Yes |

---

## Standards and Compliance

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListStandards` | List all available standard checks | Yes |
| GET | `/api/ListStandardTemplates` | List saved standard templates (DB) | Yes |
| POST | `/api/AddStandardTemplate` | Create standard template | Yes |
| POST | `/api/RemoveStandardTemplate` | Delete standard template | Yes |
| GET | `/api/ListStandardsCompare` | Get standards results for tenant | Yes |
| POST | `/api/ExecStandardsRun` | Run standard checks and save results | Yes |
| POST | `/api/ExecAccessChecks` | Verify Graph/Exchange permissions | Yes |
| GET | `/api/ListAzureADConnectStatus` | AD Connect sync status | Yes |
| GET | `/api/ListInactiveAccounts` | Inactive user accounts | Yes |
| GET | `/api/ListDeletedItems` | Deleted directory objects | Yes |
| POST | `/api/ExecRestoreDeleted` | Restore deleted object | Yes |

### BPA (Best Practice Analyzer)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/listBPA` | List BPA results | Yes |
| GET | `/api/listBPATemplates` | List BPA templates (DB) | Yes |
| GET | `/api/ListBPATemplates` | BPA templates (standards-based) | Yes |
| POST | `/api/ExecBPA` | Run Best Practice Analysis | Yes |
| POST | `/api/AddBPATemplate` | Create BPA template | Yes |
| POST | `/api/RemoveBPATemplate` | Delete BPA template | Yes |

### Tenant Drift

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/listTenantDrift` | Compare current vs previous standards | Yes |

---

## Settings and Configuration

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListExtensionsConfig` | Extension configurations (DB) | Yes |
| POST | `/api/ExecExtensionsConfig` | Save extension config | Yes |
| GET | `/api/ListFeatureFlags` | Feature flags (all enabled by default) | Yes |
| POST | `/api/ExecFeatureFlag` | Update feature flags | Yes |
| GET | `/api/ListUserSettings` | User settings (bookmarks, theme) | Yes |
| POST | `/api/ExecUserSettings` | Update user settings | Yes |
| POST | `/api/ExecUserBookmarks` | Update bookmarks | Yes |
| GET | `/api/ListCustomRole` | Custom roles (DB) | Yes |
| POST | `/api/ExecCustomRole` | Create custom role | Yes |
| GET | `/api/ListScheduledItems` | Scheduled tasks (DB) | Yes |
| POST | `/api/AddScheduledItem` | Create scheduled item | Yes |
| POST | `/api/RemoveScheduledItem` | Delete scheduled item | Yes |
| GET | `/api/ListCommunityRepos` | Community repos (DB) | Yes |
| POST | `/api/ExecCommunityRepo` | Add community repo | Yes |
| GET | `/api/ListNotificationConfig` | Notification config (DB) | Yes |
| POST | `/api/ExecNotificationConfig` | Update notification config | Yes |
| GET | `/api/ListIPWhitelist` | IP whitelist (DB) | Yes |
| GET | `/api/ListCustomVariables` | Custom variables (DB) | Yes |
| POST | `/api/ExecCIPPDBCache` | DB cache (no-op, PostgreSQL native) | Yes |
| GET | `/api/ExecBackendURLs` | Backend URL configuration | Yes |
| GET | `/api/ListGitHubReleaseNotes` | Upstream CIPP release notes | Yes |
| GET | `/api/Listlogs` | Application logs (DB) | Yes |
| GET | `/api/ListDiagnosticsPresets` | Diagnostics presets (DB) | Yes |
| POST | `/api/ExecDiagnosticsPresets` | Execute diagnostics (placeholder) | Yes |

### Domain Analysis

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListDomainHealth` | DNS-based domain health check (MX, SPF, DMARC) | Yes |
| GET | `/api/ListDomainAnalyser` | Domain analyser (placeholder) | Yes |
| POST | `/api/ExecDomainAnalyser` | Domain analysis (placeholder) | Yes |

### Directory Objects

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListDirectoryObjects` | List/get directory objects | Yes |

---

## SAM and Partner

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/ExecSAMSetup` | SAM setup guidance | Yes |
| POST | `/api/ExecSAMRoles` | SAM role configuration guidance | Yes |
| POST | `/api/ExecSAMAppPermissions` | SAM app permissions guidance | Yes |
| POST | `/api/ExecCPVPermissions` | CPV permissions (placeholder) | Yes |
| POST | `/api/ExecCPVRefresh` | CPV token refresh (automatic) | Yes |
| POST | `/api/ExecPermissionRepair` | Permission repair guidance | Yes |
| POST | `/api/ExecCreateSamApp` | SAM app creation guidance | Yes |
| POST | `/api/ExecCombinedSetup` | Combined setup guidance | Yes |
| POST | `/api/ExecUpdateRefreshToken` | Token refresh (automatic) | Yes |
| GET | `/api/ExecAPIPermissionList` | Required Graph API permissions | Yes |
| POST | `/api/ExecPartnerMode` | Configure partner mode | Yes |
| POST | `/api/ExecPartnerWebhook` | Configure partner webhook | Yes |
| POST | `/api/ExecAddMultiTenantApp` | Register app in customer tenant | Yes |
| POST | `/api/ExecApiClient` | Graph API proxy for testing | Yes |

### Backup

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/ExecRunBackup` | Create tenant config backup | Yes |
| POST | `/api/ExecRestoreBackup` | Restore backup (manual review) | Yes |
| GET | `/api/ExecListBackup` | List backups (DB) | Yes |
| POST | `/api/ExecSetCIPPAutoBackup` | Configure auto-backup (placeholder) | Yes |

### Alerts

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListAlertsQueue` | Alert queue (DB) | Yes |
| POST | `/api/AddAlert` | Create alert | Yes |
| POST | `/api/ExecAddAlert` | Create alert (alias) | Yes |
| POST | `/api/RemoveQueuedAlert` | Delete alert | Yes |

### Security Tools

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/ExecBreachSearch` | Breach search (requires HIBP key) | Yes |
| POST | `/api/ExecGeoIPLookup` | GeoIP lookup (placeholder) | Yes |
| POST | `/api/ExecBitlockerSearch` | Search BitLocker recovery keys | Yes |
| POST | `/api/ExecGetLocalAdminPassword` | Get LAPS password | Yes |
| POST | `/api/execBecRemediate` | BEC remediation: disable + revoke | Yes |
| POST | `/api/ExecOneDriveProvision` | Provision OneDrive for a user | Yes |

---

## Tests and Dashboard

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListTests` | Dashboard V2: tenant counts, test results, secure score | Yes |
| GET | `/api/ListAvailableTests` | Available standards checks | Yes |
| GET | `/api/ListTestReports` | Test report templates (DB) | Yes |
| POST | `/api/AddTestReport` | Create test report | Yes |
| POST | `/api/DeleteTestReport` | Delete test report | Yes |
| POST | `/api/ExecTestRun` | Run standards tests | Yes |

---

## Graph API Proxy (ListGraphRequest)

The most heavily used CIPP endpoint (~79 calls from the frontend). Acts as a catch-all proxy to Microsoft Graph API.

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/ListGraphRequest` | Generic Graph API GET proxy | Yes |
| POST | `/api/ListGraphRequest` | Generic Graph API proxy (any method) | Yes |

### GET Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `Endpoint` | string (required) | Graph API path, e.g. `/users`, `/groups` |
| `tenantFilter` | string (required) | Tenant ID or domain |
| `NoPagination` | bool | If true, return raw Graph response without pagination |
| `$select` | string | OData select fields |
| `$filter` | string | OData filter expression |
| `$top` | int | Max results per page |
| `$count` | bool | Include count |
| Any other query param | string | Forwarded directly to Graph API |

### POST Body

```json
{
  "tenantFilter": "contoso.onmicrosoft.com",
  "Endpoint": "/users",
  "type": "GET|POST|PATCH|DELETE",
  "params": {},
  "body": {}
}
```

### Response Format

```json
{
  "Results": [...],
  "Metadata": {"nextLink": "..."}
}
```

On error:
```json
{
  "Results": [],
  "Metadata": {"error": "error message"}
}
```

---

## System

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/version.json` | Version info | No |
| GET | `/api/health` | Health check (API, DB, PS-Runner) | No |
| GET | `/api/GetVersion` | Version and backend type | No |
| GET | `/api/GetCippAlerts` | CIPP alerts (empty) | No |
| GET | `/api/ps-runner/actions` | Available PS-Runner actions | No |
| GET | `/api/ExecListAppId` | Configured Azure client ID | Yes |
