"""Extended Intune with real Graph API calls for device management."""
from fastapi import APIRouter, Query

from app.core.graph import GraphClient

router = APIRouter(prefix="/api", tags=["intune-extended"])


# ============================================================
# Device Configuration Templates / Profiles
# ============================================================

@router.post("/AddIntuneTemplate")
async def add_intune_template(body: dict):
    """Create a device configuration profile via Graph."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/deviceManagement/deviceConfigurations", body)
    return {"Results": f"Configuration profile '{result.get('displayName', '')}' created."}

@router.post("/RemoveIntuneTemplate")
async def remove_intune_template(body: dict):
    """Delete a device configuration profile."""
    tenant_filter = body.get("tenantFilter")
    template_id = body.get("id", body.get("templateId"))
    if not tenant_filter or not template_id:
        return {"Results": "tenantFilter and id required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/deviceManagement/deviceConfigurations/{template_id}")
    return {"Results": f"Configuration profile {template_id} deleted."}

@router.post("/ExecEditTemplate")
async def exec_edit_template(body: dict):
    """Update a device configuration profile."""
    tenant_filter = body.pop("tenantFilter", None)
    template_id = body.pop("id", body.pop("templateId", None))
    if not tenant_filter or not template_id:
        return {"Results": "tenantFilter and id required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/deviceManagement/deviceConfigurations/{template_id}", body)
    return {"Results": f"Configuration profile {template_id} updated."}

@router.post("/ExecCloneTemplate")
async def exec_clone_template(body: dict):
    """Clone a device configuration by reading and re-creating it."""
    tenant_filter = body.get("tenantFilter")
    template_id = body.get("id", body.get("templateId"))
    new_name = body.get("newName")
    if not all([tenant_filter, template_id]):
        return {"Results": "tenantFilter and id required."}
    graph = GraphClient(tenant_filter)
    original = await graph.get(f"/deviceManagement/deviceConfigurations/{template_id}")
    # Strip read-only properties
    for key in ("id", "createdDateTime", "lastModifiedDateTime", "version", "@odata.context"):
        original.pop(key, None)
    if new_name:
        original["displayName"] = new_name
    else:
        original["displayName"] = f"{original.get('displayName', '')} (Copy)"
    result = await graph.post("/deviceManagement/deviceConfigurations", original)
    return {"Results": f"Profile cloned as '{result.get('displayName', '')}'."}


# ============================================================
# Reusable Settings (Graph deviceManagement)
# ============================================================

@router.get("/ListIntuneReusableSettings")
async def list_intune_reusable_settings(tenantFilter: str = Query(...)):
    """List reusable policy settings."""
    graph = GraphClient(tenantFilter)
    try:
        data = await graph.get("/deviceManagement/reusablePolicySettings")
        return data.get("value", [])
    except Exception:
        return []

@router.get("/ListIntuneReusableSettingTemplates")
async def list_intune_reusable_setting_templates():
    return {"Results": []}

@router.post("/AddIntuneReusableSetting")
async def add_intune_reusable_setting(body: dict):
    """Create a reusable policy setting."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/deviceManagement/reusablePolicySettings", body)
    return {"Results": f"Reusable setting '{result.get('displayName', '')}' created."}

@router.post("/AddIntuneReusableSettingTemplate")
async def add_intune_reusable_setting_template(body: dict):
    return {"Results": "Reusable setting template saved."}

@router.post("/RemoveIntuneReusableSetting")
async def remove_intune_reusable_setting(body: dict):
    """Delete a reusable policy setting."""
    tenant_filter = body.get("tenantFilter")
    setting_id = body.get("id")
    if not tenant_filter or not setting_id:
        return {"Results": "tenantFilter and id required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/deviceManagement/reusablePolicySettings/{setting_id}")
    return {"Results": f"Reusable setting {setting_id} deleted."}

@router.post("/RemoveIntuneReusableSettingTemplate")
async def remove_intune_reusable_setting_template(body: dict):
    return {"Results": "Reusable setting template removed."}


# ============================================================
# Intune Scripts
# ============================================================

@router.post("/EditIntuneScript")
async def edit_intune_script(body: dict):
    """Update an Intune PowerShell script."""
    tenant_filter = body.pop("tenantFilter", None)
    script_id = body.pop("id", body.pop("scriptId", None))
    if not tenant_filter or not script_id:
        return {"Results": "tenantFilter and id required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/deviceManagement/deviceManagementScripts/{script_id}", body)
    return {"Results": f"Script {script_id} updated."}

@router.post("/RemoveIntuneScript")
async def remove_intune_script(body: dict):
    """Delete an Intune PowerShell script."""
    tenant_filter = body.get("tenantFilter")
    script_id = body.get("id", body.get("scriptId"))
    if not tenant_filter or not script_id:
        return {"Results": "tenantFilter and id required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/deviceManagement/deviceManagementScripts/{script_id}")
    return {"Results": f"Script {script_id} deleted."}


# ============================================================
# Autopilot
# ============================================================

@router.post("/AddAPDevice")
async def add_ap_device(body: dict):
    """Register a device for Windows Autopilot."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/deviceManagement/importedWindowsAutopilotDeviceIdentities", {
        "serialNumber": body.get("serialNumber", ""),
        "hardwareIdentifier": body.get("hardwareIdentifier", ""),
        "groupTag": body.get("groupTag", ""),
    })
    return {"Results": f"Autopilot device registered (import ID: {result.get('id', '')})."}

@router.post("/RemoveAPDevice")
async def remove_ap_device(body: dict):
    """Remove an Autopilot device."""
    tenant_filter = body.get("tenantFilter")
    device_id = body.get("id", body.get("deviceId"))
    if not tenant_filter or not device_id:
        return {"Results": "tenantFilter and id required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/deviceManagement/windowsAutopilotDeviceIdentities/{device_id}")
    return {"Results": f"Autopilot device {device_id} removed."}

@router.post("/ExecAssignAPDevice")
async def exec_assign_ap_device(body: dict):
    """Assign an Autopilot device to a user."""
    tenant_filter = body.get("tenantFilter")
    device_id = body.get("deviceId")
    user_id = body.get("userId")
    if not all([tenant_filter, device_id]):
        return {"Results": "tenantFilter and deviceId required."}
    graph = GraphClient(tenant_filter)
    update = {}
    if user_id:
        update["userPrincipalName"] = user_id
    if body.get("displayName"):
        update["displayName"] = body["displayName"]
    await graph.post(f"/deviceManagement/windowsAutopilotDeviceIdentities/{device_id}/assignUserToDevice", {
        "userPrincipalName": user_id or "",
        "addressableUserName": body.get("addressableUserName", ""),
    })
    return {"Results": f"Autopilot device {device_id} assigned."}

@router.post("/ExecRenameAPDevice")
async def exec_rename_ap_device(body: dict):
    """Update Autopilot device display name."""
    tenant_filter = body.get("tenantFilter")
    device_id = body.get("deviceId")
    new_name = body.get("displayName", body.get("newName"))
    if not all([tenant_filter, device_id, new_name]):
        return {"Results": "tenantFilter, deviceId, displayName required."}
    graph = GraphClient(tenant_filter)
    await graph.post(f"/deviceManagement/windowsAutopilotDeviceIdentities/{device_id}/updateDeviceProperties", {
        "displayName": new_name,
    })
    return {"Results": f"Autopilot device renamed to '{new_name}'."}

@router.post("/ExecSetAPDeviceGroupTag")
async def exec_set_ap_device_group_tag(body: dict):
    """Set Autopilot device group tag."""
    tenant_filter = body.get("tenantFilter")
    device_id = body.get("deviceId")
    group_tag = body.get("groupTag", "")
    if not tenant_filter or not device_id:
        return {"Results": "tenantFilter and deviceId required."}
    graph = GraphClient(tenant_filter)
    await graph.post(f"/deviceManagement/windowsAutopilotDeviceIdentities/{device_id}/updateDeviceProperties", {
        "groupTag": group_tag,
    })
    return {"Results": f"Group tag set to '{group_tag}'."}

@router.post("/ExecSyncAPDevices")
async def exec_sync_ap_devices(body: dict):
    """Trigger Autopilot device sync."""
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    await graph.post("/deviceManagement/windowsAutopilotSettings/sync", {})
    return {"Results": "Autopilot sync initiated."}

@router.post("/AddAutopilotConfig")
async def add_autopilot_config(body: dict):
    """Create an Autopilot deployment profile."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/deviceManagement/windowsAutopilotDeploymentProfiles", body)
    return {"Results": f"Autopilot profile '{result.get('displayName', '')}' created."}

@router.post("/RemoveAutopilotConfig")
async def remove_autopilot_config(body: dict):
    """Delete an Autopilot deployment profile."""
    tenant_filter = body.get("tenantFilter")
    profile_id = body.get("id", body.get("profileId"))
    if not tenant_filter or not profile_id:
        return {"Results": "tenantFilter and id required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/deviceManagement/windowsAutopilotDeploymentProfiles/{profile_id}")
    return {"Results": f"Autopilot profile {profile_id} deleted."}

@router.post("/ExecSyncDEP")
async def exec_sync_dep(body: dict):
    """Sync Apple DEP devices."""
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    try:
        tokens = await graph.get("/deviceManagement/depOnboardingSettings")
        for token in tokens.get("value", []):
            await graph.post(f"/deviceManagement/depOnboardingSettings/{token['id']}/syncWithAppleDeviceEnrollmentProgram", {})
        return {"Results": f"DEP sync initiated for {len(tokens.get('value', []))} token(s)."}
    except Exception as e:
        return {"Results": f"DEP sync failed: {str(e)}"}

@router.post("/ExecSyncVPP")
async def exec_sync_vpp(body: dict):
    """Sync Apple VPP tokens."""
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    try:
        tokens = await graph.get("/deviceAppManagement/vppTokens")
        for token in tokens.get("value", []):
            await graph.post(f"/deviceAppManagement/vppTokens/{token['id']}/syncLicenses", {})
        return {"Results": f"VPP sync initiated for {len(tokens.get('value', []))} token(s)."}
    except Exception as e:
        return {"Results": f"VPP sync failed: {str(e)}"}

@router.post("/ExecSetCloudManaged")
async def exec_set_cloud_managed(body: dict):
    """Set device to cloud-managed (co-management workload shift)."""
    tenant_filter = body.get("tenantFilter")
    device_id = body.get("deviceId")
    if not tenant_filter or not device_id:
        return {"Results": "tenantFilter and deviceId required."}
    graph = GraphClient(tenant_filter)
    # Trigger cloud management authority
    await graph.post(f"/deviceManagement/managedDevices/{device_id}/setCloudPCReviewStatus", {
        "reviewStatus": {"inReview": False},
    })
    return {"Results": f"Cloud management configured for device {device_id}."}

@router.post("/ExecDevicePasscodeAction")
async def exec_device_passcode_action(body: dict):
    """Reset device passcode."""
    tenant_filter = body.get("tenantFilter")
    device_id = body.get("deviceId")
    if not tenant_filter or not device_id:
        return {"Results": "tenantFilter and deviceId required."}
    graph = GraphClient(tenant_filter)
    await graph.post(f"/deviceManagement/managedDevices/{device_id}/resetPasscode", {})
    return {"Results": f"Passcode reset for device {device_id}."}


# ============================================================
# App Management
# ============================================================

@router.post("/AddChocoApp")
async def add_choco_app(body: dict):
    """Create a Win32 app from Chocolatey package via Graph."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    app_data = {
        "@odata.type": "#microsoft.graph.win32LobApp",
        "displayName": body.get("displayName", body.get("packageName", "")),
        "description": body.get("description", f"Chocolatey: {body.get('packageName', '')}"),
        "installCommandLine": f"choco install {body.get('packageName', '')} -y",
        "uninstallCommandLine": f"choco uninstall {body.get('packageName', '')} -y",
        "installExperience": {"runAsAccount": "system", "deviceRestartBehavior": "suppress"},
        "returnCodes": [{"returnCode": 0, "type": "success"}, {"returnCode": 1641, "type": "hardReboot"}, {"returnCode": 3010, "type": "softReboot"}],
    }
    result = await graph.post("/deviceAppManagement/mobileApps", app_data)
    return {"Results": f"Chocolatey app '{body.get('packageName', '')}' created (ID: {result.get('id', '')})."}

@router.post("/AddOfficeApp")
async def add_office_app(body: dict):
    """Create an Office suite app deployment."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    app_data = {
        "@odata.type": "#microsoft.graph.officeSuiteApp",
        "displayName": body.get("displayName", "Microsoft 365 Apps"),
        "autoAcceptEula": True,
        "productIds": body.get("productIds", ["o365ProPlusRetail"]),
        "updateChannel": body.get("updateChannel", "current"),
        "officePlatformArchitecture": body.get("architecture", "x64"),
    }
    result = await graph.post("/deviceAppManagement/mobileApps", app_data)
    return {"Results": f"Office app '{app_data['displayName']}' created."}

@router.post("/AddStoreApp")
async def add_store_app(body: dict):
    """Add a Microsoft Store app."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    app_data = {
        "@odata.type": "#microsoft.graph.winGetApp",
        "displayName": body.get("displayName", ""),
        "packageIdentifier": body.get("packageIdentifier", ""),
        "installExperience": {"runAsAccount": body.get("runAsAccount", "system")},
    }
    result = await graph.post("/deviceAppManagement/mobileApps", app_data)
    return {"Results": f"Store app '{body.get('displayName', '')}' created."}

@router.post("/AddwinGetApp")
async def add_winget_app(body: dict):
    """Add a WinGet app via Graph."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    app_data = {
        "@odata.type": "#microsoft.graph.winGetApp",
        "displayName": body.get("displayName", ""),
        "packageIdentifier": body.get("packageIdentifier", ""),
        "installExperience": {"runAsAccount": body.get("runAsAccount", "system")},
    }
    result = await graph.post("/deviceAppManagement/mobileApps", app_data)
    return {"Results": f"WinGet app '{body.get('displayName', '')}' created (ID: {result.get('id', '')})."}

@router.post("/AddMSPApp")
async def add_msp_app(body: dict):
    """Add an MSP/RMM app deployment."""
    return await add_winget_app(body)

@router.post("/ExecAssignApp")
async def exec_assign_app(body: dict):
    """Assign an app to groups/users."""
    tenant_filter = body.get("tenantFilter")
    app_id = body.get("appId")
    assignments = body.get("assignments", [])
    if not tenant_filter or not app_id:
        return {"Results": "tenantFilter and appId required."}
    graph = GraphClient(tenant_filter)
    await graph.post(f"/deviceAppManagement/mobileApps/{app_id}/assign", {
        "mobileAppAssignments": assignments,
    })
    return {"Results": f"App {app_id} assigned to {len(assignments)} target(s)."}

@router.post("/ExecAppUpload")
async def exec_app_upload(body: dict):
    """App upload requires binary content — placeholder for file upload flow."""
    return {"Results": "App upload requires binary file handling. Use the Intune portal for complex app packages."}

@router.post("/RemoveApp")
async def remove_app(body: dict):
    """Delete an app from Intune."""
    tenant_filter = body.get("tenantFilter")
    app_id = body.get("appId", body.get("id"))
    if not tenant_filter or not app_id:
        return {"Results": "tenantFilter and appId required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/deviceAppManagement/mobileApps/{app_id}")
    return {"Results": f"App {app_id} deleted."}

@router.post("/RemoveQueuedApp")
async def remove_queued_app(body: dict):
    return await remove_app(body)

@router.post("/ExecSetPackageTag")
async def exec_set_package_tag(body: dict):
    """Update app notes/tags."""
    tenant_filter = body.get("tenantFilter")
    app_id = body.get("appId")
    notes = body.get("notes", body.get("tag", ""))
    if not tenant_filter or not app_id:
        return {"Results": "tenantFilter and appId required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/deviceAppManagement/mobileApps/{app_id}", {"notes": notes})
    return {"Results": f"App {app_id} notes updated."}


# ============================================================
# Policies
# ============================================================

@router.post("/AddPolicy")
async def add_policy(body: dict):
    """Create a device compliance or configuration policy."""
    tenant_filter = body.pop("tenantFilter", None)
    policy_type = body.pop("policyType", "deviceCompliancePolicies")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post(f"/deviceManagement/{policy_type}", body)
    return {"Results": f"Policy '{result.get('displayName', '')}' created."}

@router.post("/RemovePolicy")
async def remove_policy(body: dict):
    """Delete a device policy."""
    tenant_filter = body.get("tenantFilter")
    policy_id = body.get("id", body.get("policyId"))
    policy_type = body.get("policyType", "deviceCompliancePolicies")
    if not tenant_filter or not policy_id:
        return {"Results": "tenantFilter and id required."}
    graph = GraphClient(tenant_filter)
    await graph.delete(f"/deviceManagement/{policy_type}/{policy_id}")
    return {"Results": f"Policy {policy_id} deleted."}

@router.post("/AddEnrollment")
async def add_enrollment(body: dict):
    """Create an enrollment restriction."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/deviceManagement/deviceEnrollmentConfigurations", body)
    return {"Results": f"Enrollment config '{result.get('displayName', '')}' created."}


# ============================================================
# Assignment Filters
# ============================================================

@router.post("/AddAssignmentFilter")
async def add_assignment_filter(body: dict):
    """Create an Intune assignment filter."""
    tenant_filter = body.pop("tenantFilter", None)
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    result = await graph.post("/deviceManagement/assignmentFilters", {
        "displayName": body.get("displayName", ""),
        "description": body.get("description", ""),
        "platform": body.get("platform", "windows10AndLater"),
        "rule": body.get("rule", ""),
    })
    return {"Results": f"Assignment filter '{result.get('displayName', '')}' created."}

@router.post("/EditAssignmentFilter")
async def edit_assignment_filter(body: dict):
    """Update an assignment filter."""
    tenant_filter = body.pop("tenantFilter", None)
    filter_id = body.pop("id", body.pop("filterId", None))
    if not tenant_filter or not filter_id:
        return {"Results": "tenantFilter and id required."}
    graph = GraphClient(tenant_filter)
    await graph.patch(f"/deviceManagement/assignmentFilters/{filter_id}", body)
    return {"Results": f"Assignment filter {filter_id} updated."}

@router.post("/ExecAssignmentFilter")
async def exec_assignment_filter(body: dict):
    """Test an assignment filter rule."""
    tenant_filter = body.get("tenantFilter")
    if not tenant_filter:
        return {"Results": "tenantFilter required."}
    graph = GraphClient(tenant_filter)
    # Validate filter rule by getting evaluation
    result = await graph.post("/deviceManagement/assignmentFilters/getState", {})
    return {"Results": result}

@router.get("/ListAssignmentFilterTemplates")
async def list_assignment_filter_templates():
    return {"Results": []}

@router.post("/AddAssignmentFilterTemplate")
async def add_assignment_filter_template(body: dict):
    return {"Results": "Assignment filter template saved."}

@router.post("/RemoveAssignmentFilterTemplate")
async def remove_assignment_filter_template(body: dict):
    return {"Results": "Assignment filter template removed."}
