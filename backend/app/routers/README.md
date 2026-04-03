# Router-Uebersicht

## Struktur nach Bereich

### Identity & Users
| Datei | Endpoints | Beschreibung |
|-------|-----------|--------------|
| `users.py` | 12 | ListUsers, AddUser, EditUser, MFA, SigninLogs |
| `user_extended.py` | 27 | Offboard, JIT Admin, TAP, Bulk Ops, Photo, Aliases |
| `groups.py` | 4 | ListGroups, AddGroup, EditGroup, Delete |

### Tenant Administration
| Datei | Endpoints | Beschreibung |
|-------|-----------|--------------|
| `tenants.py` | 6 | ListTenants, ListOrg, ListDomains, AddTenant |
| `tenant_admin.py` | 15 | Onboarding, Offboarding, Domains, OAuth Apps, Branding |

### Security & Compliance
| Datei | Endpoints | Beschreibung |
|-------|-----------|--------------|
| `security.py` | 16 | CA Policies, Alerts, Secure Score, Risky Users, Sign-ins, Roles |
| `standards.py` | 11 | Standards Engine, BPA, Drift Detection |

### Exchange & Email
| Datei | Endpoints | Beschreibung |
|-------|-----------|--------------|
| `mailbox.py` | 5 | ListMailboxes, Permissions, Rules (PS-Runner) |
| `exchange_extended.py` | 36 | Calendar, OoO, Forwarding, Connectors, Transport |
| `email_security.py` | 33 | SafeLinks, AntiPhish, Spam, Quarantine, Defender |

### Intune & Endpoint
| Datei | Endpoints | Beschreibung |
|-------|-----------|--------------|
| `intune.py` | 10 | Devices, Compliance, Apps, Autopilot, Recovery Keys |
| `intune_extended.py` | 35 | Templates, Reusable Settings, Apps, Policies |

### SharePoint & Teams
| Datei | Endpoints | Beschreibung |
|-------|-----------|--------------|
| `sharepoint.py` | 10 | Sites, Teams, OneDrive, Quota |

### GDAP & Partner
| Datei | Endpoints | Beschreibung |
|-------|-----------|--------------|
| `gdap.py` | 6 | GDAP Relationships, Invites, Access Assignments |

### Contacts & Resources
| Datei | Endpoints | Beschreibung |
|-------|-----------|--------------|
| `contacts.py` | 7 | Contacts CRUD, Rooms, Equipment |

### Settings & Admin
| Datei | Endpoints | Beschreibung |
|-------|-----------|--------------|
| `settings.py` | 18 | Feature Flags, User Settings, Logs, DNS, Community Repos |
| `sam_partner.py` | 62 | SAM Setup, Backup, Templates, Groups, CA, Tests, Misc |

### Auth & Proxy
| Datei | Endpoints | Beschreibung |
|-------|-----------|--------------|
| `auth.py` | 5 | /.auth/login, /.auth/me, /api/me, Logout |
| `graph.py` | 2 | ListGraphRequest (Catch-All Graph Proxy) |

---

## Gesamt: 485 Endpoints in 20 Router-Dateien

### Nach Implementierungsstatus
- **Echte Graph API Calls:** 257 (53%)
- **PS-Runner (Exchange):** 39 (8%)
- **DB Operationen:** 31 (6%)
- **Auth + Proxy:** 7 (2%)
- **POST Stubs (korrekte Messages):** 109 (22%)
- **GET Stubs (leer):** 13 (3%)
- **cipp_response([]) Wrapper:** 29 (6%)
