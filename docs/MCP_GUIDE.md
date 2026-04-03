# CIPP MCP Server Guide

The CIPP MCP (Model Context Protocol) server allows AI assistants like Claude to manage Microsoft 365 tenants through CIPP. It exposes 21 tools that cover tenant management, user lifecycle, security monitoring, compliance checking, device management, and raw Graph API access.

## Overview

The MCP server (`backend/mcp_server.py`) is built with [FastMCP](https://github.com/jlowin/fastmcp) and provides a structured interface to the same Graph API and database operations that the CIPP web frontend uses. All tools return Markdown-formatted text for readability in AI conversations.

**Server name:** `CIPP`
**Description:** M365 Multi-Tenant Management -- manage users, tenants, security, devices, and compliance via Microsoft Graph API.

---

## Setup

### Prerequisites

- CIPP backend configured with valid Azure credentials (`.env` file)
- Python 3.10+ with backend dependencies installed
- For real tenant access: Azure App Registration with appropriate Graph API permissions

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "cipp": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "D:/dev/xampp/htdocs/cipp-fork-v2/CIPP/backend"
    }
  }
}
```

### Claude Code

Add to `.claude/settings.json` in your project or user config:

```json
{
  "mcpServers": {
    "cipp": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "D:/dev/xampp/htdocs/cipp-fork-v2/CIPP/backend"
    }
  }
}
```

### Standalone

```bash
cd backend
PYTHONPATH=. python mcp_server.py
```

---

## Tools Reference

### 1. list_tenants

List all onboarded M365 tenants from the CIPP database.

**Parameters:** None

**Example usage:**
```
List all my tenants
```

**Example output:**
```markdown
# Onboarded Tenants (2)

- **Contoso GmbH** (contoso.onmicrosoft.com) -- ID: `abc-123`
- **Fabrikam Inc** (fabrikam.onmicrosoft.com) -- ID: `def-456`
```

---

### 2. onboard_tenant

Onboard a new M365 tenant by verifying Graph API access and saving to the database.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Azure AD tenant ID or primary domain (e.g. `contoso.onmicrosoft.com`) |

**Example usage:**
```
Onboard the tenant contoso.onmicrosoft.com
```

**Example output:**
```
Tenant **Contoso GmbH** (contoso.onmicrosoft.com) onboarded successfully.
```

---

### 3. get_tenant_details

Get detailed information about a tenant: organization info, domains, and licenses.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |

**Example usage:**
```
Show me details for contoso.onmicrosoft.com
```

**Example output:**
```markdown
# Tenant: Contoso GmbH

**Tenant ID:** abc-123-def
**Created:** 2020-01-15T00:00:00Z
**AD Sync:** No

## Domains (2)
- contoso.onmicrosoft.com (default)
- contoso.com

## Licenses (3)
- **ENTERPRISEPACK**: 45/50 used
- **EMS**: 20/50 used
- **POWER_BI_STANDARD**: 5/25 used
```

---

### 4. list_users

List users in a tenant with key details.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |
| `top` | int | No | Max users to return (default 50) |

**Example usage:**
```
List the first 10 users in contoso.onmicrosoft.com
```

**Example output:**
```markdown
# Users in contoso.onmicrosoft.com (10)

| Name | UPN | Enabled | Licensed | Type |
|------|-----|---------|----------|------|
| John Doe | john@contoso.com | Yes | Yes | Member |
| Jane Smith | jane@contoso.com | Yes | Yes | Member |
| Guest User | guest@external.com | Yes | No | Guest |
```

---

### 5. get_user

Get detailed information about a specific user.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |
| `user_id` | string | Yes | User ID or UPN (e.g. `user@domain.com`) |

**Example usage:**
```
Get details for john@contoso.com in contoso.onmicrosoft.com
```

**Example output:**
```markdown
# User: John Doe

**UPN:** john@contoso.com
**Email:** john@contoso.com
**Enabled:** True
**Type:** Member
**Job Title:** IT Manager
**Department:** IT
**Created:** 2021-03-10T00:00:00Z
**Last Sign-in:** 2026-04-02T14:30:00Z
**AD Sync:** No
**Licenses:** 2
```

---

### 6. create_user

Create a new user in a tenant.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |
| `display_name` | string | Yes | Display name |
| `user_principal_name` | string | Yes | UPN (e.g. `john@contoso.com`) |
| `password` | string | Yes | Initial password |
| `mail_nickname` | string | No | Mail nickname (defaults to part before @) |

**Example usage:**
```
Create user "Max Mueller" with UPN max@contoso.com and password TempPass123!
```

**Example output:**
```
User **Max Mueller** (max@contoso.com) created successfully. ID: `guid-here`
```

---

### 7. disable_user

Disable a user account (block sign-in).

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |
| `user_id` | string | Yes | User ID or UPN |

**Example output:**
```
User john@contoso.com has been disabled.
```

---

### 8. reset_password

Reset a user's password. Generates a random password if none provided.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |
| `user_id` | string | Yes | User ID or UPN |
| `new_password` | string | No | New password (random if empty) |

**Example output:**
```
Password reset for john@contoso.com. New password: `aB3dEf7GhI9jK!1` (must change on next sign-in).
```

---

### 9. offboard_user

Full user offboarding: disable account, revoke sessions, optionally remove licenses.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |
| `user_id` | string | Yes | User ID or UPN |
| `remove_licenses` | bool | No | Remove all licenses (default True) |

**Example output:**
```
User john@contoso.com offboarded. Steps: Account disabled, Sessions revoked, Removed 2 license(s).
```

---

### 10. get_security_alerts

Get recent security alerts for a tenant.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |
| `top` | int | No | Max alerts (default 20) |

**Example output:**
```markdown
# Security Alerts (3)

- **[HIGH]** Suspicious sign-in activity -- Status: new (2026-04-01)
- **[MEDIUM]** Impossible travel -- Status: inProgress (2026-03-30)
- **[LOW]** Risky sign-in detected -- Status: resolved (2026-03-28)
```

---

### 11. get_risky_users

List risky users from Identity Protection.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |

**Example output:**
```markdown
# Risky Users (2)

| User | Risk Level | Risk State | Last Updated |
|------|-----------|-----------|--------------|
| John Doe | high | atRisk | 2026-04-01 |
| Jane Smith | medium | confirmedCompromised | 2026-03-28 |
```

---

### 12. get_secure_score

Get the current Microsoft Secure Score for a tenant.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |

**Example output:**
```markdown
# Secure Score: 45/80 (56%)

## Top Improvement Actions
- **AdminMFAV2**: 0% -- Enable MFA for admin roles
- **BlockLegacyAuthentication**: 0% -- Block legacy auth protocols
- **OneAdmin**: 50% -- Designate more than one global admin
```

---

### 13. list_conditional_access_policies

List all Conditional Access policies in a tenant.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |

**Example output:**
```markdown
# Conditional Access Policies (3)

- **Require MFA for Admins** -- [ON] (ID: `policy-id-1`)
- **Block Legacy Auth** -- [ON] (ID: `policy-id-2`)
- **Require Compliant Device** -- [Report-only] (ID: `policy-id-3`)
```

---

### 14. get_sign_in_summary

Get a sign-in activity summary: success/failure counts and top failure reasons.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |

**Example output:**
```markdown
# Sign-in Summary (last 500 events)

- **Success:** 420
- **Failure:** 80

## Top Failure Reasons
- Invalid password: 35x
- MFA denied: 25x
- Account locked: 12x
```

---

### 15. run_standards_check

Run all compliance/security standards checks against a tenant.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |

**Available checks:** MFAForAdmins, MFAForAllUsers, SecurityDefaults, PasswordExpiry, SSPR, AdminAccountsLicensed, GlobalAdminCount, UnusedLicenses, LegacyAuthBlocked, GuestAccessRestricted, SecureScore.

**Example output:**
```markdown
# Standards Check: 7/11 passed

- **[PASS]** MFA for Admin Roles
  CA Policy 'Require MFA for Admins' enforces MFA for admin roles.
- **[FAIL]** MFA for All Users
  No CA policy enforces MFA for all users.
- **[PASS]** Legacy Auth Blocked
  CA Policy 'Block Legacy Auth' blocks legacy auth.
- **[FAIL]** Secure Score Threshold
  Secure Score: 45/80 (56%) -- below 50% threshold.
```

---

### 16. list_available_checks

List all available standards/compliance checks that can be run.

**Parameters:** None

**Example output:**
```markdown
# Available Standards Checks

- **MFAForAdmins** (Identity): MFA for Admin Roles
- **MFAForAllUsers** (Identity): MFA for All Users
- **SecurityDefaults** (Identity): Security Defaults / CA Policies
- **PasswordExpiry** (Identity): Password Expiry Policy
- **SSPR** (Identity): Self-Service Password Reset
- **AdminAccountsLicensed** (Identity): Admin Accounts Licensed
- **GlobalAdminCount** (Identity): Global Admin Count (2-5)
- **UnusedLicenses** (Licensing): License Utilization
- **LegacyAuthBlocked** (Identity): Legacy Auth Blocked
- **GuestAccessRestricted** (Identity): Guest Access Restricted
- **SecureScore** (Security): Secure Score Threshold
```

---

### 17. list_groups

List groups in a tenant.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |
| `top` | int | No | Max groups (default 50) |

**Example output:**
```markdown
# Groups (15)

- **All Employees** [M365] -- allemployees@contoso.com
- **IT Department** [Security] -- no email
- **Sales Team** [M365] -- sales@contoso.com
```

---

### 18. list_devices

List Intune managed devices in a tenant.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |
| `top` | int | No | Max devices (default 50) |

**Example output:**
```markdown
# Managed Devices (25)

| Name | OS | Compliance | Last Sync | User |
|------|----|-----------|-----------|------|
| DESKTOP-ABC | Windows | compliant | 2026-04-02 | john@contoso.com |
| iPhone-Jane | iOS | compliant | 2026-04-01 | jane@contoso.com |
| LAPTOP-DEF | Windows | noncompliant | 2026-03-25 | bob@contoso.com |
```

---

### 19. device_action

Execute a remote action on a managed device.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |
| `device_id` | string | Yes | Intune device ID |
| `action` | string | Yes | One of: `syncDevice`, `rebootNow`, `retire`, `wipe`, `remoteLock`, `resetPasscode`, `windowsDefenderScan` |

**Example output:**
```
Action **syncDevice** executed on device `device-id-123`.
```

---

### 20. list_licenses

List all subscribed license SKUs for a tenant with usage info.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |

**Example output:**
```markdown
# Licenses

| SKU | Used | Total | Available |
|-----|------|-------|-----------|
| ENTERPRISEPACK | 45 | 50 | 5 |
| EMS | 20 | 50 | 30 |
| POWER_BI_STANDARD | 5 | 25 | 20 |
```

---

### 21. graph_query

Execute a raw Microsoft Graph API query. Use for anything not covered by the other tools.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `tenant_id` | string | Yes | Tenant ID or domain |
| `endpoint` | string | Yes | Graph API path (e.g. `/users`, `/groups`, `/security/alerts_v2`) |
| `method` | string | No | HTTP method: GET, POST, PATCH, DELETE (default GET) |
| `body` | string | No | JSON body for POST/PATCH |

**Example usage:**
```
Query Graph API for contoso.onmicrosoft.com: GET /users?$select=displayName,userPrincipalName&$top=5
```

**Example output:**
```json
{
  "value": [
    {"displayName": "John Doe", "userPrincipalName": "john@contoso.com"},
    {"displayName": "Jane Smith", "userPrincipalName": "jane@contoso.com"}
  ]
}
```

Note: Output is truncated to 4000 characters for large responses.

---

## Troubleshooting

### MCP server fails to start

- Verify the backend dependencies are installed: `pip install -r requirements.txt`
- Ensure `PYTHONPATH` includes the backend directory or run from the `backend/` directory
- Check that `.env` exists with valid Azure credentials (or `DEMO_MODE=true` for testing)

### "No tenants onboarded yet"

- Onboard a tenant first using `onboard_tenant` with a valid tenant ID
- In demo mode, a demo tenant (`Contoso GmbH`) is auto-seeded on startup

### Graph API permission errors

- The Azure App Registration needs the following permissions:
  - `Directory.ReadWrite.All`, `User.ReadWrite.All`, `Group.ReadWrite.All`
  - `Policy.ReadWrite.ConditionalAccess`, `SecurityEvents.ReadWrite.All`
  - `DeviceManagementManagedDevices.ReadWrite.All`
- Ensure admin consent has been granted for all permissions

### Tools return empty data

- Verify the tenant ID is correct and accessible
- Check that the Azure App Registration has delegated admin access to the target tenant
- Use `graph_query` to test raw Graph API access: `GET /organization`

### Timeout errors

- Graph API calls may time out for large tenants. Use the `top` parameter to limit results
- Some endpoints (like `list_users` with `top=999`) may be slow on large directories

### Claude Desktop not showing CIPP tools

- Restart Claude Desktop after editing `claude_desktop_config.json`
- Check the MCP server logs in Claude Desktop's developer console
- Verify the `cwd` path points to the correct backend directory
- On Windows, use forward slashes in paths or escape backslashes

### Demo mode

Set `DEMO_MODE=true` in `.env` to use synthetic demo data without real Azure credentials. This is useful for testing the MCP integration without a live tenant.
