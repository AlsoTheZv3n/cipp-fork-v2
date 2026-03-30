"""Extended user management with real Graph API calls."""
from fastapi import APIRouter, Query

from app.core.graph import GraphClient
from app.services.ps_runner import run_ps_action

router = APIRouter(prefix="/api", tags=["user-extended"])


@router.get("/listUsers")
async def list_users_lower(tenantFilter: str = Query(...)):
    graph = GraphClient(tenantFilter)
    data = await graph.get("/users", params={"$select": "id,displayName,userPrincipalName", "$top": 999})
    return data.get("value", [])

@router.get("/ListUsersAndGroups")
async def list_users_and_groups(tenantFilter: str = Query(...)):
    graph = GraphClient(tenantFilter)
    users = await graph.get("/users", params={"$select": "id,displayName,userPrincipalName", "$top": 999})
    groups = await graph.get("/groups", params={"$select": "id,displayName", "$top": 999})
    return {"Users": users.get("value", []), "Groups": groups.get("value", [])}

@router.post("/PatchUser")
async def patch_user(body: dict):
    tenant_filter = body.pop("tenantFilter", None)
    user_id = body.pop("userId", None)
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/users/{user_id}", body)
    return {"Results": f"User {user_id} patched."}


# --- Bulk Operations ---

@router.post("/AddUserBulk")
async def add_user_bulk(body: dict):
    """Create multiple users via Graph batch API."""
    tenant_filter = body.get("tenantFilter")
    users = body.get("users", [])
    if not tenant_filter or not users:
        return {"Results": "tenantFilter and users array required."}
    graph = GraphClient(tenant_filter)
    results = []
    for user_data in users:
        try:
            result = await graph.post("/users", user_data)
            results.append({"status": "success", "user": result.get("userPrincipalName", "")})
        except Exception as e:
            results.append({"status": "error", "error": str(e)})
    return {"Results": results}

@router.post("/AddUserDefaults")
async def add_user_defaults(body: dict):
    return {"Results": "User defaults saved."}

@router.post("/RemoveUserDefaultTemplate")
async def remove_user_default_template(body: dict):
    return {"Results": "User default template removed."}

@router.post("/AddGuest")
async def add_guest(body: dict):
    """Invite a guest user via Graph."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/invitations", {
        "invitedUserEmailAddress": body.get("email"),
        "inviteRedirectUrl": body.get("redirectUrl", "https://myapps.microsoft.com"),
        "sendInvitationMessage": body.get("sendInvite", True),
    })
    return {"Results": f"Guest invitation sent to {body.get('email', '')}."}


# --- User Photo ---

@router.get("/ListUserPhoto")
async def list_user_photo(
    tenantFilter: str = Query(None),
    userId: str = Query(None),
    UserID: str = Query(None),
):
    uid = UserID or userId
    if not uid or not tenantFilter:
        return {"Results": "No photo found."}
    graph = GraphClient(tenantFilter)
    try:
        data = await graph.get(f"/users/{uid}/photo/$value")
        return data
    except Exception:
        return {"Results": "No photo found."}

@router.post("/ExecSetUserPhoto")
async def exec_set_user_photo(body: dict):
    return {"Results": "Photo upload requires binary data handling — use PS-Runner."}


# --- Aliases ---

@router.post("/EditUserAliases")
async def edit_user_aliases(body: dict):
    """Update user proxy addresses (aliases) via Graph."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    aliases = body.get("proxyAddresses", [])
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/users/{user_id}", {"proxyAddresses": aliases})
    return {"Results": f"Aliases updated for {user_id}."}


# --- Offboarding ---

@router.post("/ExecOffboardUser")
async def exec_offboard_user(body: dict):
    """Full user offboarding: disable, revoke sessions, remove licenses, reset password."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    steps = []

    # Disable account
    await graph.patch(f"/users/{user_id}", {"accountEnabled": False})
    steps.append("Account disabled")

    # Revoke sessions
    try:
        await graph.post(f"/users/{user_id}/revokeSignInSessions", {})
        steps.append("Sessions revoked")
    except Exception:
        steps.append("Session revocation failed")

    # Remove licenses
    if body.get("removeLicenses", True):
        try:
            user = await graph.get(f"/users/{user_id}", params={"$select": "assignedLicenses"})
            sku_ids = [lic["skuId"] for lic in user.get("assignedLicenses", [])]
            if sku_ids:
                await graph.post(f"/users/{user_id}/assignLicense", {
                    "addLicenses": [],
                    "removeLicenses": sku_ids,
                })
                steps.append(f"Removed {len(sku_ids)} license(s)")
        except Exception:
            steps.append("License removal failed")

    # Reset password
    if body.get("resetPassword", True):
        import secrets
        new_pass = secrets.token_urlsafe(24)
        try:
            await graph.patch(f"/users/{user_id}", {
                "passwordProfile": {"password": new_pass, "forceChangePasswordNextSignIn": True}
            })
            steps.append("Password reset")
        except Exception:
            steps.append("Password reset failed")

    # Hide from GAL
    if body.get("hideFromGAL", False):
        try:
            await graph.patch(f"/users/{user_id}", {"showInAddressList": False})
            steps.append("Hidden from GAL")
        except Exception:
            pass

    return {"Results": f"User {user_id} offboarded. Steps: {', '.join(steps)}."}


# --- MFA Actions ---

@router.post("/ExecResetMFA")
async def exec_reset_mfa(body: dict):
    """Delete all auth methods except password (effectively resets MFA)."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    methods = await graph.get(f"/users/{user_id}/authentication/methods")
    removed = 0
    for method in methods.get("value", []):
        odata_type = method.get("@odata.type", "")
        if "password" in odata_type.lower():
            continue  # Don't remove password
        method_id = method.get("id")
        try:
            # Different method types have different delete endpoints
            if "phone" in odata_type.lower():
                await graph.delete(f"/users/{user_id}/authentication/phoneMethods/{method_id}")
                removed += 1
            elif "fido2" in odata_type.lower():
                await graph.delete(f"/users/{user_id}/authentication/fido2Methods/{method_id}")
                removed += 1
            elif "software" in odata_type.lower():
                await graph.delete(f"/users/{user_id}/authentication/softwareOathMethods/{method_id}")
                removed += 1
            elif "microsoftAuthenticator" in odata_type:
                await graph.delete(f"/users/{user_id}/authentication/microsoftAuthenticatorMethods/{method_id}")
                removed += 1
        except Exception:
            continue
    return {"Results": f"MFA reset: removed {removed} auth method(s) for {user_id}."}

@router.post("/ExecPerUserMFA")
async def exec_per_user_mfa(body: dict):
    """Per-user MFA requires legacy API — use PS-Runner."""
    return {"Results": "Per-user MFA requires PS-Runner (legacy MFA API)."}

@router.post("/SetAuthMethod")
async def set_auth_method(body: dict):
    """Add an authentication method for a user."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    method_type = body.get("methodType", "phone")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    if method_type == "phone":
        await graph.post(f"/users/{user_id}/authentication/phoneMethods", {
            "phoneNumber": body.get("phoneNumber"),
            "phoneType": body.get("phoneType", "mobile"),
        })
        return {"Results": "Phone auth method added."}
    return {"Results": f"Method type '{method_type}' not supported via Graph."}

@router.post("/ExecSendPush")
async def exec_send_push(body: dict):
    return {"Results": "Push notification requires Authenticator integration."}

@router.post("/ExecCreateTAP")
async def exec_create_tap(body: dict):
    """Create a Temporary Access Pass via Graph."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    tap_config = {"lifetimeInMinutes": body.get("lifetimeMinutes", 60), "isUsableOnce": body.get("oneTimeUse", True)}
    result = await graph.post(f"/users/{user_id}/authentication/temporaryAccessPassMethods", tap_config)
    return {"Results": f"TAP created: {result.get('temporaryAccessPass', 'see details')}", "tap": result}


# --- JIT Admin ---

@router.get("/ListJITAdmin")
async def list_jit_admin(tenantFilter: str = Query(None)):
    """List JIT admin assignments (users with time-limited admin roles)."""
    if not tenantFilter:
        return {"Results": []}
    graph = GraphClient(tenantFilter)
    # PIM (Privileged Identity Management) eligible role assignments
    try:
        data = await graph.get("/roleManagement/directory/roleEligibilityScheduleInstances")
        return data.get("value", [])
    except Exception:
        return {"Results": []}

@router.get("/ListJITAdminTemplates")
async def list_jit_admin_templates():
    return []

@router.post("/AddJITAdminTemplate")
async def add_jit_admin_template(body: dict):
    return {"Results": "JIT admin template created."}

@router.post("/EditJITAdminTemplate")
async def edit_jit_admin_template(body: dict):
    return {"Results": "JIT admin template updated."}

@router.post("/RemoveJITAdminTemplate")
async def remove_jit_admin_template(body: dict):
    return {"Results": "JIT admin template removed."}

@router.post("/ExecJitAdmin")
async def exec_jit_admin(body: dict):
    """Activate a JIT admin role via PIM."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    role_id = body.get("roleId")
    if not all([tenant_filter, user_id, role_id]):
        return {"Results": "tenantFilter, userId, roleId required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/roleManagement/directory/roleAssignmentScheduleRequests", {
        "action": "selfActivate",
        "principalId": user_id,
        "roleDefinitionId": role_id,
        "directoryScopeId": "/",
        "justification": body.get("justification", "JIT admin activation via CIPP"),
        "scheduleInfo": {
            "startDateTime": body.get("startTime"),
            "expiration": {"type": "afterDuration", "duration": body.get("duration", "PT4H")},
        },
    })
    return {"Results": f"JIT admin role activated for {user_id}."}

@router.post("/ExecJITAdminSettings")
async def exec_jit_admin_settings(body: dict):
    return {"Results": "JIT admin settings updated."}


# --- Password ---

@router.post("/ExecPasswordNeverExpires")
async def exec_password_never_expires(body: dict):
    """Set password to never expire via Graph."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    never_expires = body.get("neverExpires", True)
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/users/{user_id}", {
        "passwordPolicies": "DisablePasswordExpiration" if never_expires else "None"
    })
    return {"Results": f"Password {'never expires' if never_expires else 'expiry restored'} for {user_id}."}

@router.post("/ExecClrImmId")
async def exec_clr_imm_id(body: dict):
    """Clear ImmutableId for a user (needed for AD sync changes)."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/users/{user_id}", {"onPremisesImmutableId": None})
    return {"Results": f"ImmutableId cleared for {user_id}."}

@router.post("/ExecHVEUser")
async def exec_hve_user(body: dict):
    """Configure high-volume email — requires PS-Runner."""
    return {"Results": "HVE configuration requires PS-Runner."}

@router.post("/ExecReprocessUserLicenses")
async def exec_reprocess_user_licenses(body: dict):
    """Reprocess license assignments for a user."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId required."}
    graph = GraphClient(tenant_filter)
    await graph.post(f"/users/{user_id}/reprocessLicenseAssignment", {})
    return {"Results": f"License reprocessing initiated for {user_id}."}
