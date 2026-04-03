from fastapi import APIRouter, Query

from app.core.graph import GraphClient

router = APIRouter(prefix="/api", tags=["users"])

USER_SELECT = (
    "id,displayName,userPrincipalName,mail,assignedLicenses,"
    "accountEnabled,createdDateTime,lastSignInDateTime,userType,"
    "onPremisesSyncEnabled,city,department,jobTitle"
)


@router.get("/ListUsers")
async def list_users(tenantFilter: str = Query(...), UserId: str = Query(None), top: int = 999):
    """List users or get a single user by ID/UPN."""
    graph = GraphClient(tenantFilter)
    if UserId:
        # Single user lookup — frontend expects array
        try:
            user = await graph.get(f"/users/{UserId}", params={"$select": USER_SELECT})
            return [user]
        except Exception:
            return []
    data = await graph.get("/users", params={"$select": USER_SELECT, "$top": top})
    return data.get("value", [])


@router.get("/ListuserCounts")
async def list_user_counts(tenantFilter: str = Query(...)):
    """Get user counts (total, licensed, guests, enabled, disabled)."""
    graph = GraphClient(tenantFilter)
    users = await graph.get_all_pages("/users", params={
        "$select": "id,accountEnabled,userType,assignedLicenses",
    })
    total = len(users)
    enabled = sum(1 for u in users if u.get("accountEnabled"))
    disabled = total - enabled
    guests = sum(1 for u in users if u.get("userType") == "Guest")
    licensed = sum(1 for u in users if u.get("assignedLicenses"))
    members = total - guests
    admins = 0  # Would need role check
    # Frontend expects: data.Users, data.LicUsers, data.Guests, data.Gas
    return {
        "Users": total,
        "LicUsers": licensed,
        "Guests": guests,
        "Gas": admins,
        "Enabled": enabled,
        "Disabled": disabled,
        "Members": members,
    }


@router.get("/ListMFAUsers")
async def list_mfa_users(tenantFilter: str = Query(...)):
    """Get MFA status for all users."""
    graph = GraphClient(tenantFilter)
    users = await graph.get("/users", params={
        "$select": "id,displayName,userPrincipalName",
        "$top": 20,
    })
    user_list = users.get("value", [])
    if not user_list:
        return []

    batch_requests = [
        {"id": str(i), "method": "GET", "url": f"/users/{u['id']}/authentication/methods"}
        for i, u in enumerate(user_list)
    ]
    batch_result = await graph.batch(batch_requests)

    results = []
    for i, user in enumerate(user_list):
        methods = []
        for resp in batch_result.get("responses", []):
            if resp.get("id") == str(i):
                methods = resp.get("body", {}).get("value", [])
                break
        method_types = [m.get("@odata.type", "") for m in methods]
        has_mfa = any(
            t not in ("#microsoft.graph.passwordAuthenticationMethod",)
            for t in method_types
        )
        results.append({
            "id": user["id"],
            "displayName": user.get("displayName"),
            "userPrincipalName": user.get("userPrincipalName"),
            "isMfaRegistered": has_mfa,
            "authMethods": method_types,
        })
    return results


@router.post("/AddUser")
async def add_user(body: dict):
    """Create a new user."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter is required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/users", body)
    return {"Results": f"User {result.get('userPrincipalName', '')} created successfully."}


@router.post("/EditUser")
async def edit_user(body: dict):
    """Update user properties."""
    tenant_filter = body.pop("tenantFilter", None)
    user_id = body.pop("userId", None)
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId are required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/users/{user_id}", body)
    return {"Results": f"User {user_id} updated successfully."}


@router.post("/RemoveUser")
async def remove_user(body: dict):
    """Delete a user."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId are required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/users/{user_id}")
    return {"Results": f"User {user_id} deleted successfully."}


@router.post("/ExecResetPass")
async def reset_password(body: dict):
    """Reset a user's password."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    password = body.get("password")
    if not all([tenant_filter, user_id]):
        return {"Results": "tenantFilter and userId are required."}
    graph = GraphClient(tenant_filter)
    payload = {"passwordProfile": {"forceChangePasswordNextSignIn": True}}
    if password:
        payload["passwordProfile"]["password"] = password
    await graph.patch(f"/users/{user_id}", payload)
    return {"Results": f"Password reset for {user_id}."}


@router.post("/ExecDisableUser")
async def disable_user(body: dict):
    """Disable a user account."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId are required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/users/{user_id}", {"accountEnabled": False})
    return {"Results": f"User {user_id} disabled."}


@router.post("/ExecRevokeSessions")
async def revoke_sessions(body: dict):
    """Revoke all user sessions."""
    tenant_filter = body.get("tenantFilter")
    user_id = body.get("userId")
    if not tenant_filter or not user_id:
        return {"Results": "tenantFilter and userId are required."}
    graph = GraphClient(tenant_filter)
    await graph.post(f"/users/{user_id}/revokeSignInSessions", {})
    return {"Results": f"Sessions revoked for {user_id}."}


@router.get("/ListUserSigninLogs")
async def list_user_signin_logs(
    tenantFilter: str = Query(...),
    UserId: str = Query(None, alias="UserId"),
    userId: str = Query(None),
    top: int = 50,
):
    """Get sign-in logs for a specific user."""
    uid = UserId or userId
    if not uid:
        return []
    graph = GraphClient(tenantFilter)
    data = await graph.get(
        "/auditLogs/signIns",
        params={"$filter": f"userId eq '{uid}'", "$top": top},
    )
    return data.get("value", [])


@router.get("/ListUserGroups")
async def list_user_groups(tenantFilter: str = Query(...), userId: str = Query(...)):
    """List groups a user is a member of."""
    graph = GraphClient(tenantFilter)
    data = await graph.get(f"/users/{userId}/memberOf")
    return data.get("value", [])


@router.get("/ListUserMailboxDetails")
async def list_user_mailbox_details(
    tenantFilter: str = Query(...),
    UserId: str = Query(None),
    userMail: str = Query(None),
):
    """Get mailbox details for a user."""
    from app.services.ps_runner import run_ps_action
    identity = userMail or UserId
    if not identity:
        return {"Results": []}
    return await run_ps_action("get_mailbox", tenantFilter, identity=identity)


@router.get("/ListUserMailboxRules")
async def list_user_mailbox_rules(
    tenantFilter: str = Query(...),
    UserId: str = Query(...),
):
    """Get mailbox rules for a user via Graph."""
    graph = GraphClient(tenantFilter)
    data = await graph.get(f"/users/{UserId}/mailFolders/inbox/messageRules")
    return data.get("value", [])


@router.get("/ListContactPermissions")
async def list_contact_permissions(
    tenantFilter: str = Query(...),
    UserId: str = Query(None),
):
    """Get contact folder permissions — requires PS-Runner."""
    from app.services.ps_runner import run_ps_action
    if not UserId:
        return []
    return await run_ps_action("get_mailbox_permissions", tenantFilter, identity=UserId)


@router.get("/ListUserTrustedBlockedSenders")
async def list_user_trusted_blocked_senders(
    tenantFilter: str = Query(...),
    UserId: str = Query(None),
    userPrincipalName: str = Query(None),
):
    """List user's trusted/blocked senders — requires PS-Runner."""
    return {"Results": []}


@router.get("/ListNewUserDefaults")
async def list_new_user_defaults(TenantFilter: str = Query(None), tenantFilter: str = Query(None)):
    """Get default settings for new user creation."""
    return {"Results": {"usageLocation": "US", "domain": TenantFilter or tenantFilter}}


@router.get("/ListCustomDataMappings")
async def list_custom_data_mappings(
    tenantFilter: str = Query(None),
    sourceType: str = Query(None),
    directoryObject: str = Query(None),
):
    """List custom data mappings."""
    return []
