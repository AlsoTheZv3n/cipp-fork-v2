# CIPP App Registration Setup Script
# Creates the Azure AD App Registration with all required Graph permissions
# and grants admin consent.
#
# Usage: .\setup-app-registration.ps1 -DisplayName "cipp2" -RedirectUri "http://localhost:3001/.auth/callback"
# Requirements: az cli (logged in as Global Admin)

param(
    [string]$DisplayName = "cipp2",
    [string]$RedirectUri = "http://localhost:3001/.auth/callback"
)

$ErrorActionPreference = "Stop"

Write-Host "=== CIPP App Registration Setup ===" -ForegroundColor Cyan
Write-Host ""

# Microsoft Graph App ID (constant)
$graphApiId = "00000003-0000-0000-c000-000000000000"

# Required permissions with their Graph API IDs
$permissions = @(
    @{ Id = "498476ce-e0fe-48b0-b801-37ba7e2685c6"; Name = "Organization.Read.All" }
    @{ Id = "df021288-bdef-4463-88db-98f22de89214"; Name = "User.Read.All" }
    @{ Id = "5b567255-7703-4780-807c-7be8301ae99b"; Name = "Group.Read.All" }
    @{ Id = "7ab1d382-f21e-4acd-a863-ba3e13f7da61"; Name = "Directory.Read.All" }
    @{ Id = "dbb9058a-0e50-45d7-ae91-66909b5d4664"; Name = "Domain.Read.All" }
    @{ Id = "c79f8feb-a9db-4090-85f9-90d820caa0eb"; Name = "Application.Read.All" }
    @{ Id = "b0afded3-3588-46d8-8b3d-9842eff778da"; Name = "DeviceManagementManagedDevices.Read.All" }
    @{ Id = "dc377aa6-52d8-4e23-b271-b3b753e16f74"; Name = "DeviceManagementConfiguration.Read.All" }
    @{ Id = "246dd0d5-5bd0-4def-940b-0421030a5b68"; Name = "Policy.Read.All" }
    @{ Id = "bf394140-e372-4bf9-a898-299cfc7564e5"; Name = "SecurityEvents.Read.All" }
    @{ Id = "dc5007c0-2d7d-4c42-879c-2dab87571379"; Name = "IdentityRiskyUser.Read.All" }
    @{ Id = "b0afded3-3588-46d8-8b3d-9842eff778da"; Name = "AuditLog.Read.All" }
    @{ Id = "230c1aed-a721-4c5d-9cb4-a90514e508ef"; Name = "Reports.Read.All" }
    @{ Id = "5e0edab9-c148-49d0-b423-ac253e121825"; Name = "SecurityActions.Read.All" }
    @{ Id = "810c84a8-4a9e-49e6-bf7d-12d183f40d01"; Name = "Mail.Read" }
    @{ Id = "332a536c-c7ef-4017-ab91-336970924f0d"; Name = "Sites.Read.All" }
    @{ Id = "242607bd-1d2c-432c-82eb-bdb27baa23ab"; Name = "TeamSettings.Read.All" }
)

# Build resource access JSON
$resourceAccess = $permissions | ForEach-Object {
    @{ id = $_.Id; type = "Role" }
}
$requiredResourceAccess = @(
    @{
        resourceAppId = $graphApiId
        resourceAccess = $resourceAccess
    }
)

# Step 1: Create App Registration
Write-Host "[1/4] Creating app registration '$DisplayName'..." -ForegroundColor Yellow
$app = az ad app create `
    --display-name $DisplayName `
    --sign-in-audience "AzureADMyOrg" `
    --web-redirect-uris $RedirectUri `
    --required-resource-accesses ($requiredResourceAccess | ConvertTo-Json -Depth 5 -Compress) `
    2>&1 | ConvertFrom-Json

if (-not $app.appId) {
    Write-Host "ERROR: Failed to create app registration." -ForegroundColor Red
    Write-Host $app
    exit 1
}

$appId = $app.appId
$objectId = $app.id
Write-Host "  App ID: $appId" -ForegroundColor Green
Write-Host "  Object ID: $objectId" -ForegroundColor Green

# Step 2: Create Client Secret
Write-Host "[2/4] Creating client secret..." -ForegroundColor Yellow
$secret = az ad app credential reset `
    --id $objectId `
    --display-name "CIPP Secret" `
    --years 2 `
    2>&1 | ConvertFrom-Json

$clientSecret = $secret.password
Write-Host "  Secret created (save this!)" -ForegroundColor Green

# Step 3: Create Service Principal
Write-Host "[3/4] Creating service principal..." -ForegroundColor Yellow
az ad sp create --id $appId 2>&1 | Out-Null
Write-Host "  Service principal created" -ForegroundColor Green

# Step 4: Grant Admin Consent
Write-Host "[4/4] Granting admin consent..." -ForegroundColor Yellow
Start-Sleep -Seconds 5  # Wait for propagation
az ad app permission admin-consent --id $appId 2>&1 | Out-Null
Write-Host "  Admin consent granted" -ForegroundColor Green

# Output
Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Add these to your backend/.env:" -ForegroundColor Yellow
Write-Host ""
Write-Host "AZURE_TENANT_ID=$(az account show --query tenantId -o tsv)"
Write-Host "AZURE_CLIENT_ID=$appId"
Write-Host "AZURE_CLIENT_SECRET=$clientSecret"
Write-Host "AUTH_TENANT_ID=$(az account show --query tenantId -o tsv)"
Write-Host "AUTH_CLIENT_ID=$appId"
Write-Host "AUTH_CLIENT_SECRET=$clientSecret"
Write-Host ""
Write-Host "Permissions granted:" -ForegroundColor Yellow
$permissions | ForEach-Object { Write-Host "  - $($_.Name)" }
