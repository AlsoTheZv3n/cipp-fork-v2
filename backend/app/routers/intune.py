from fastapi import APIRouter, Query

from app.core.graph import GraphClient

router = APIRouter(prefix="/api", tags=["intune"])


@router.get("/ListDevices")
async def list_devices(tenantFilter: str = Query(...), top: int = 999):
    """List managed devices."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/deviceManagement/managedDevices", params={"$top": top})
    return data.get("value", [])


@router.post("/ExecDeviceAction")
async def exec_device_action(body: dict):
    """Execute device action (wipe, retire, sync, restart, etc.)."""
    tenant_filter = body.get("tenantFilter")
    device_id = body.get("deviceId")
    action = body.get("action")
    if not all([tenant_filter, device_id, action]):
        return {"Results": "tenantFilter, deviceId, and action are required."}

    graph = GraphClient(tenant_filter)
    action_map = {
        "syncDevice": f"/deviceManagement/managedDevices/{device_id}/syncDevice",
        "rebootNow": f"/deviceManagement/managedDevices/{device_id}/rebootNow",
        "retire": f"/deviceManagement/managedDevices/{device_id}/retire",
        "wipe": f"/deviceManagement/managedDevices/{device_id}/wipe",
        "resetPasscode": f"/deviceManagement/managedDevices/{device_id}/resetPasscode",
        "remoteLock": f"/deviceManagement/managedDevices/{device_id}/remoteLock",
        "windowsDefenderScan": f"/deviceManagement/managedDevices/{device_id}/windowsDefenderScan",
        "windowsDefenderUpdateSignatures": f"/deviceManagement/managedDevices/{device_id}/windowsDefenderUpdateSignatures",
    }
    endpoint = action_map.get(action)
    if not endpoint:
        return {"Results": f"Unknown action: {action}"}

    action_body = body.get("body", {})
    await graph.post(endpoint, action_body)
    return {"Results": f"Action '{action}' executed on device {device_id}."}


@router.post("/ExecDeviceDelete")
async def exec_device_delete(body: dict):
    """Delete a managed device."""
    tenant_filter = body.get("tenantFilter")
    device_id = body.get("deviceId")
    if not tenant_filter or not device_id:
        return {"Results": "tenantFilter and deviceId are required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/deviceManagement/managedDevices/{device_id}")
    return {"Results": f"Device {device_id} deleted."}


@router.get("/ListCompliancePolicies")
async def list_compliance_policies(tenantFilter: str = Query(...)):
    """List device compliance policies."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/deviceManagement/deviceCompliancePolicies")
    return data.get("value", [])


@router.get("/ListApps")
async def list_apps(tenantFilter: str = Query(...)):
    """List Intune managed apps."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/deviceAppManagement/mobileApps")
    return data.get("value", [])


@router.get("/ListAPDevices")
async def list_autopilot_devices(tenantFilter: str = Query(...)):
    """List Windows Autopilot devices."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/deviceManagement/windowsAutopilotDeviceIdentities")
    return data.get("value", [])


@router.get("/ListIntuneTemplates")
async def list_intune_templates(tenantFilter: str = Query(...)):
    """List Intune configuration templates."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/deviceManagement/deviceConfigurations")
    return data.get("value", [])


@router.get("/ListIntuneScript")
async def list_intune_scripts(tenantFilter: str = Query(...)):
    """List Intune PowerShell scripts."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/deviceManagement/deviceManagementScripts")
    return data.get("value", [])


@router.get("/ListAssignmentFilters")
async def list_assignment_filters(tenantFilter: str = Query(...)):
    """List Intune assignment filters."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/deviceManagement/assignmentFilters")
    return data.get("value", [])


@router.get("/ListAppProtectionPolicies")
async def list_app_protection_policies(tenantFilter: str = Query(...)):
    """List app protection policies."""
    graph = GraphClient(tenantFilter)
    data = await graph.get("/deviceAppManagement/managedAppPolicies")
    return data.get("value", [])


@router.post("/ExecAssignPolicy")
async def exec_assign_policy(body: dict):
    """Assign a policy to groups."""
    tenant_filter = body.get("tenantFilter")
    policy_id = body.get("policyId")
    policy_type = body.get("policyType", "deviceConfigurations")
    assignments = body.get("assignments", [])
    if not tenant_filter or not policy_id:
        return {"Results": "tenantFilter and policyId are required."}
    graph = GraphClient(tenant_filter)
    await graph.post(
        f"/deviceManagement/{policy_type}/{policy_id}/assign",
        {"assignments": assignments},
    )
    return {"Results": f"Policy {policy_id} assigned."}


@router.post("/ExecGetRecoveryKey")
async def exec_get_recovery_key(body: dict):
    """Get BitLocker recovery key for a device."""
    tenant_filter = body.get("tenantFilter")
    device_id = body.get("deviceId")
    if not tenant_filter or not device_id:
        return {"Results": "tenantFilter and deviceId are required."}
    graph = GraphClient(tenant_filter)
    data = await graph.get(
        f"/informationProtection/bitlocker/recoveryKeys",
        params={"$filter": f"deviceId eq '{device_id}'"},
    )
    keys = data.get("value", [])
    if keys:
        key_id = keys[0]["id"]
        full_key = await graph.get(
            f"/informationProtection/bitlocker/recoveryKeys/{key_id}",
            params={"$select": "key"},
        )
        return {"Results": full_key}
    return {"Results": "No recovery key found."}
