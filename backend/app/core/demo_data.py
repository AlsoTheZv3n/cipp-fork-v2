"""Demo data for testing without a real M365 tenant.

Provides realistic fake Graph API responses for all major endpoints.
Activated when DEMO_MODE=true or when no AZURE_CLIENT_ID is configured.
"""
import uuid
from datetime import datetime, timedelta

DEMO_TENANT_ID = "demo-tenant-contoso"
DEMO_TENANT_DOMAIN = "contoso.onmicrosoft.com"

# --- Users ---
DEMO_USERS = [
    {"id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"user{i}")), "displayName": name, "userPrincipalName": f"{upn}@contoso.onmicrosoft.com",
     "mail": f"{upn}@contoso.com", "accountEnabled": enabled, "userType": utype, "jobTitle": title, "department": dept,
     "city": city, "assignedLicenses": [{"skuId": "c7df2760-2c81-4ef7-b578-5b5392b571df"}] if licensed else [],
     "createdDateTime": "2024-01-15T10:00:00Z", "onPremisesSyncEnabled": False,
     "lastSignInDateTime": (datetime.utcnow() - timedelta(days=days_ago)).isoformat() + "Z"}
    for i, (name, upn, enabled, utype, title, dept, city, licensed, days_ago) in enumerate([
        ("Alex Mueller", "alex.mueller", True, "Member", "IT Admin", "IT", "Berlin", True, 0),
        ("Sarah Schmidt", "sarah.schmidt", True, "Member", "CFO", "Finance", "Munich", True, 1),
        ("Max Weber", "max.weber", True, "Member", "Developer", "Engineering", "Hamburg", True, 0),
        ("Lisa Fischer", "lisa.fischer", True, "Member", "HR Manager", "Human Resources", "Berlin", True, 2),
        ("Tom Braun", "tom.braun", True, "Member", "Sales Lead", "Sales", "Frankfurt", True, 0),
        ("Anna Koch", "anna.koch", True, "Member", "Marketing", "Marketing", "Munich", True, 3),
        ("Felix Richter", "felix.richter", False, "Member", "Former Employee", "IT", "Berlin", True, 90),
        ("Emma Wagner", "emma.wagner", True, "Member", "Support", "Support", "Hamburg", True, 1),
        ("David Becker", "david.becker", True, "Member", "Intern", "Engineering", "Berlin", False, 5),
        ("Sophie Hoffmann", "sophie.hoffmann", True, "Guest", "External Consultant", "Consulting", "Vienna", False, 10),
        ("Admin Account", "admin", True, "Member", "Global Admin", "IT", "Berlin", True, 0),
        ("Break Glass", "breakglass", True, "Member", "Emergency Admin", "IT", "Berlin", True, 30),
    ])
]

# --- Groups ---
DEMO_GROUPS = [
    {"id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"group{i}")), "displayName": name, "groupTypes": gtypes,
     "mailEnabled": mail, "securityEnabled": sec, "mail": email, "description": desc}
    for i, (name, gtypes, mail, sec, email, desc) in enumerate([
        ("All Employees", ["Unified"], True, False, "allemployees@contoso.com", "All company employees"),
        ("IT Department", [], False, True, None, "IT security group"),
        ("Engineering Team", ["Unified"], True, False, "engineering@contoso.com", "Engineering M365 group"),
        ("Management", [], False, True, None, "Management security group"),
        ("External Partners", [], False, True, None, "External partner access"),
        ("MFA Excluded Users", [], False, True, None, "Users excluded from MFA (should be empty)"),
    ])
]

# --- Licenses ---
DEMO_SKUS = [
    {"id": "sku1", "skuId": "c7df2760-2c81-4ef7-b578-5b5392b571df", "skuPartNumber": "ENTERPRISEPREMIUM",
     "prepaidUnits": {"enabled": 25, "suspended": 0, "warning": 0}, "consumedUnits": 10},
    {"id": "sku2", "skuId": "05e9a617-0261-4cee-bb36-b42a6b1acc38", "skuPartNumber": "SPE_E3",
     "prepaidUnits": {"enabled": 50, "suspended": 0, "warning": 0}, "consumedUnits": 8},
    {"id": "sku3", "skuId": "f30db892-07e9-47e9-837c-80727f46fd3d", "skuPartNumber": "POWER_BI_PRO",
     "prepaidUnits": {"enabled": 10, "suspended": 0, "warning": 0}, "consumedUnits": 3},
    {"id": "sku4", "skuId": "1f2f344a-700d-42c9-9427-5cea45d8b441", "skuPartNumber": "STREAM",
     "prepaidUnits": {"enabled": 25, "suspended": 0, "warning": 0}, "consumedUnits": 0},
]

# --- Conditional Access Policies ---
DEMO_CA_POLICIES = [
    {"id": "ca1", "displayName": "Require MFA for Admins", "state": "enabled",
     "conditions": {"users": {"includeRoles": ["62e90394-69f5-4237-9190-012177145e10"]}, "clientAppTypes": ["all"]},
     "grantControls": {"operator": "OR", "builtInControls": ["mfa"]}},
    {"id": "ca2", "displayName": "Block Legacy Authentication", "state": "enabled",
     "conditions": {"users": {"includeUsers": ["All"]}, "clientAppTypes": ["exchangeActiveSync", "other"]},
     "grantControls": {"operator": "OR", "builtInControls": ["block"]}},
    {"id": "ca3", "displayName": "Require MFA for All Users", "state": "enabledForReportingButNotEnforced",
     "conditions": {"users": {"includeUsers": ["All"]}, "clientAppTypes": ["all"]},
     "grantControls": {"operator": "OR", "builtInControls": ["mfa"]}},
    {"id": "ca4", "displayName": "Require Compliant Device", "state": "disabled",
     "conditions": {"users": {"includeUsers": ["All"]}, "clientAppTypes": ["all"]},
     "grantControls": {"operator": "OR", "builtInControls": ["compliantDevice"]}},
]

# --- Security Alerts ---
DEMO_ALERTS = [
    {"id": "alert1", "title": "Suspicious sign-in from unfamiliar location", "severity": "medium",
     "status": "new", "createdDateTime": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z",
     "serviceSource": "microsoftDefenderForOffice365"},
    {"id": "alert2", "title": "Impossible travel activity", "severity": "high",
     "status": "inProgress", "createdDateTime": (datetime.utcnow() - timedelta(hours=8)).isoformat() + "Z",
     "serviceSource": "azureAdIdentityProtection"},
    {"id": "alert3", "title": "Malware detected in email attachment", "severity": "high",
     "status": "new", "createdDateTime": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
     "serviceSource": "microsoftDefenderForOffice365"},
]

# --- Secure Score ---
DEMO_SECURE_SCORE = {
    "id": "score1", "currentScore": 47.5, "maxScore": 78.0,
    "createdDateTime": datetime.utcnow().isoformat() + "Z",
    "controlScores": [
        {"controlName": "MFARegistrationV2", "scoreInPercentage": 80.0, "description": "Ensure all users register for MFA"},
        {"controlName": "BlockLegacyAuthentication", "scoreInPercentage": 100.0, "description": "Block legacy auth protocols"},
        {"controlName": "AdminMFAV2", "scoreInPercentage": 100.0, "description": "Require MFA for admins"},
        {"controlName": "OneAdmin", "scoreInPercentage": 0.0, "description": "Designate more than one global admin"},
        {"controlName": "SigninRiskPolicy", "scoreInPercentage": 0.0, "description": "Enable sign-in risk policy"},
        {"controlName": "SelfServicePasswordReset", "scoreInPercentage": 50.0, "description": "Enable SSPR"},
        {"controlName": "IntegratedApps", "scoreInPercentage": 0.0, "description": "Do not allow users to grant consent to unmanaged apps"},
    ],
}

# --- Risky Users ---
DEMO_RISKY_USERS = [
    {"id": DEMO_USERS[6]["id"], "userDisplayName": "Felix Richter", "userPrincipalName": "felix.richter@contoso.onmicrosoft.com",
     "riskLevel": "high", "riskState": "atRisk", "riskLastUpdatedDateTime": (datetime.utcnow() - timedelta(hours=3)).isoformat() + "Z"},
    {"id": DEMO_USERS[9]["id"], "userDisplayName": "Sophie Hoffmann", "userPrincipalName": "sophie.hoffmann@contoso.onmicrosoft.com",
     "riskLevel": "medium", "riskState": "atRisk", "riskLastUpdatedDateTime": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"},
]

# --- Sign-in Logs ---
DEMO_SIGNINS = [
    {"id": f"signin{i}", "userPrincipalName": user["userPrincipalName"], "userDisplayName": user["displayName"],
     "createdDateTime": (datetime.utcnow() - timedelta(hours=i)).isoformat() + "Z",
     "status": {"errorCode": code, "failureReason": reason},
     "ipAddress": ip, "clientAppUsed": app,
     "location": {"city": user["city"], "countryOrRegion": "DE"}}
    for i, (user, code, reason, ip, app) in enumerate([
        (DEMO_USERS[0], 0, "", "203.0.113.10", "Browser"),
        (DEMO_USERS[2], 0, "", "198.51.100.22", "Mobile Apps and Desktop clients"),
        (DEMO_USERS[1], 0, "", "192.0.2.50", "Browser"),
        (DEMO_USERS[4], 50126, "Invalid username or password", "203.0.113.99", "Browser"),
        (DEMO_USERS[6], 50053, "Account is locked", "198.51.100.77", "Exchange ActiveSync"),
        (DEMO_USERS[3], 0, "", "192.0.2.30", "Browser"),
        (DEMO_USERS[0], 0, "", "203.0.113.10", "Browser"),
        (DEMO_USERS[7], 0, "", "198.51.100.15", "Mobile Apps and Desktop clients"),
        (DEMO_USERS[9], 50074, "MFA required", "10.0.0.1", "Other clients"),
        (DEMO_USERS[2], 0, "", "198.51.100.22", "Browser"),
    ])
]

# --- Devices ---
DEMO_DEVICES = [
    {"id": f"device{i}", "deviceName": name, "operatingSystem": os_name, "osVersion": os_ver,
     "complianceState": comp, "managedDeviceOwnerType": "company",
     "userPrincipalName": DEMO_USERS[user_idx]["userPrincipalName"],
     "lastSyncDateTime": (datetime.utcnow() - timedelta(hours=hours)).isoformat() + "Z"}
    for i, (name, os_name, os_ver, comp, user_idx, hours) in enumerate([
        ("DESKTOP-AM01", "Windows", "11.0.22631", "compliant", 0, 1),
        ("DESKTOP-SS02", "Windows", "11.0.22631", "compliant", 1, 3),
        ("MACBOOK-MW03", "macOS", "14.2", "compliant", 2, 2),
        ("DESKTOP-LF04", "Windows", "10.0.19045", "noncompliant", 3, 24),
        ("IPHONE-TB05", "iOS", "17.2", "compliant", 4, 0),
        ("PIXEL-AK06", "Android", "14", "noncompliant", 5, 48),
    ])
]

# --- Organization ---
DEMO_ORG = {
    "id": DEMO_TENANT_ID, "displayName": "Contoso GmbH (Demo)",
    "verifiedDomains": [{"name": DEMO_TENANT_DOMAIN, "isDefault": True}],
    "onPremisesSyncEnabled": False, "createdDateTime": "2023-06-15T08:00:00Z",
    "onPremisesLastSyncDateTime": None,
}

# --- Domains ---
DEMO_DOMAINS = [
    {"id": "contoso.onmicrosoft.com", "isDefault": True, "isVerified": True, "authenticationType": "Managed"},
    {"id": "contoso.com", "isDefault": False, "isVerified": True, "authenticationType": "Managed"},
    {"id": "contoso.de", "isDefault": False, "isVerified": False, "authenticationType": "Managed"},
]

# --- Directory Roles ---
DEMO_ROLES = [
    {"id": "role1", "displayName": "Global Administrator", "description": "Can manage all aspects of Azure AD"},
    {"id": "role2", "displayName": "User Administrator", "description": "Can manage users and groups"},
    {"id": "role3", "displayName": "Exchange Administrator", "description": "Can manage Exchange Online"},
    {"id": "role4", "displayName": "Security Administrator", "description": "Can manage security features"},
]

# --- Named Locations ---
DEMO_NAMED_LOCATIONS = [
    {"id": "loc1", "displayName": "Corporate Office Berlin", "@odata.type": "#microsoft.graph.ipNamedLocation",
     "ipRanges": [{"cidrAddress": "203.0.113.0/24"}], "isTrusted": True},
    {"id": "loc2", "displayName": "Blocked Countries", "@odata.type": "#microsoft.graph.countryNamedLocation",
     "countriesAndRegions": ["RU", "CN", "KP"], "isTrusted": False},
]

# --- Auth Methods Policy ---
DEMO_AUTH_POLICY = {
    "id": "authMethodsPolicy",
    "registrationEnforcement": {"authenticationMethodsRegistrationCampaign": {"state": "enabled"}},
    "authenticationMethodConfigurations": [
        {"id": "MicrosoftAuthenticator", "state": "enabled"},
        {"id": "Fido2", "state": "enabled"},
        {"id": "Sms", "state": "disabled"},
    ],
}


# --- Route mapping: Graph endpoint → demo data ---

def get_demo_response(endpoint: str, params: dict | None = None) -> dict | list | None:
    """Map a Graph API endpoint to demo data. Returns None if no mapping exists."""
    ep = endpoint.rstrip("/")

    if ep == "/organization":
        return {"value": [DEMO_ORG]}
    if ep == "/domains":
        return {"value": DEMO_DOMAINS}
    if ep == "/subscribedSkus":
        return {"value": DEMO_SKUS}
    if ep == "/users":
        user_id_filter = params.get("$filter", "") if params else ""
        return {"value": DEMO_USERS}
    if ep.startswith("/users/") and ep.count("/") == 2:
        user_id = ep.split("/")[2]
        user = next((u for u in DEMO_USERS if u["id"] == user_id or u["userPrincipalName"] == user_id or user_id in u.get("userPrincipalName", "")), None)
        return user or DEMO_USERS[0]
    if ep == "/groups":
        return {"value": DEMO_GROUPS}
    if ep == "/directoryRoles":
        return {"value": DEMO_ROLES}
    if ep == "/identity/conditionalAccess/policies":
        return {"value": DEMO_CA_POLICIES}
    if ep == "/identity/conditionalAccess/namedLocations":
        return {"value": DEMO_NAMED_LOCATIONS}
    if ep == "/security/alerts_v2":
        return {"value": DEMO_ALERTS}
    if ep == "/security/incidents":
        return {"value": []}
    if ep == "/security/secureScores":
        return {"value": [DEMO_SECURE_SCORE]}
    if ep == "/identityProtection/riskyUsers":
        return {"value": DEMO_RISKY_USERS}
    if ep == "/identityProtection/riskDetections":
        return {"value": []}
    if ep == "/auditLogs/signIns":
        return {"value": DEMO_SIGNINS}
    if ep == "/auditLogs/directoryAudits":
        return {"value": []}
    if ep == "/deviceManagement/managedDevices":
        return {"value": DEMO_DEVICES}
    if ep == "/deviceManagement/deviceCompliancePolicies":
        return {"value": []}
    if ep == "/deviceManagement/deviceConfigurations":
        return {"value": []}
    if ep == "/deviceAppManagement/mobileApps":
        return {"value": []}
    if ep == "/deviceManagement/windowsAutopilotDeviceIdentities":
        return {"value": []}
    if ep == "/servicePrincipals":
        return {"value": []}
    if ep == "/policies/authenticationMethodsPolicy":
        return DEMO_AUTH_POLICY
    if ep == "/policies/authorizationPolicy":
        return {"guestUserRoleId": "2af84b1e-32c8-42b7-82bc-daa742cc7555", "defaultUserRolePermissions": {"allowedToResetPassword": True}}
    if ep == "/contacts":
        return {"value": []}
    if ep.startswith("/places/"):
        return {"value": []}
    if ep.startswith("/tenantRelationships/"):
        return {"value": []}
    if "/mailboxSettings" in ep:
        return {"automaticRepliesSetting": {"status": "disabled", "internalReplyMessage": "", "externalReplyMessage": ""}}
    if "/calendarPermissions" in ep:
        return {"value": []}
    if "/messageRules" in ep:
        return {"value": []}
    if "/memberOf" in ep:
        return {"value": DEMO_GROUPS[:2]}
    if "/members" in ep:
        return {"value": DEMO_USERS[:3]}
    if "/authentication/methods" in ep:
        return {"value": [
            {"@odata.type": "#microsoft.graph.passwordAuthenticationMethod", "id": "pwd1"},
            {"@odata.type": "#microsoft.graph.microsoftAuthenticatorAuthenticationMethod", "id": "auth1"},
        ]}
    if "/licenseDetails" in ep:
        return {"value": [{"skuId": "c7df2760-2c81-4ef7-b578-5b5392b571df", "skuPartNumber": "ENTERPRISEPREMIUM"}]}
    if "/drive" in ep:
        return {"id": "drive1", "driveType": "business", "quota": {"total": 1099511627776, "used": 524288000}}
    if "/sites" in ep:
        return {"value": []}

    # Default: return empty value
    return {"value": []}
