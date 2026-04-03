#!/bin/bash
# CIPP App Registration Setup Script (Bash/az cli)
# Creates the Azure AD App Registration with all required Graph permissions.
#
# Usage: ./setup-app-registration.sh [display-name] [redirect-uri]
# Requirements: az cli (logged in as Global Admin)

set -e

DISPLAY_NAME="${1:-cipp2}"
REDIRECT_URI="${2:-http://localhost:3001/.auth/callback}"

echo "=== CIPP App Registration Setup ==="
echo ""

# Required permissions JSON
PERMISSIONS='[
  {"resourceAppId":"00000003-0000-0000-c000-000000000000","resourceAccess":[
    {"id":"498476ce-e0fe-48b0-b801-37ba7e2685c6","type":"Role"},
    {"id":"df021288-bdef-4463-88db-98f22de89214","type":"Role"},
    {"id":"5b567255-7703-4780-807c-7be8301ae99b","type":"Role"},
    {"id":"7ab1d382-f21e-4acd-a863-ba3e13f7da61","type":"Role"},
    {"id":"dbb9058a-0e50-45d7-ae91-66909b5d4664","type":"Role"},
    {"id":"c79f8feb-a9db-4090-85f9-90d820caa0eb","type":"Role"},
    {"id":"b0afded3-3588-46d8-8b3d-9842eff778da","type":"Role"},
    {"id":"dc377aa6-52d8-4e23-b271-b3b753e16f74","type":"Role"},
    {"id":"246dd0d5-5bd0-4def-940b-0421030a5b68","type":"Role"},
    {"id":"bf394140-e372-4bf9-a898-299cfc7564e5","type":"Role"},
    {"id":"dc5007c0-2d7d-4c42-879c-2dab87571379","type":"Role"},
    {"id":"230c1aed-a721-4c5d-9cb4-a90514e508ef","type":"Role"},
    {"id":"5e0edab9-c148-49d0-b423-ac253e121825","type":"Role"},
    {"id":"810c84a8-4a9e-49e6-bf7d-12d183f40d01","type":"Role"},
    {"id":"332a536c-c7ef-4017-ab91-336970924f0d","type":"Role"},
    {"id":"242607bd-1d2c-432c-82eb-bdb27baa23ab","type":"Role"}
  ]}
]'

# Step 1: Create App
echo "[1/4] Creating app registration '$DISPLAY_NAME'..."
APP_ID=$(az ad app create \
  --display-name "$DISPLAY_NAME" \
  --sign-in-audience "AzureADMyOrg" \
  --web-redirect-uris "$REDIRECT_URI" \
  --required-resource-accesses "$PERMISSIONS" \
  --query appId -o tsv)
echo "  App ID: $APP_ID"

OBJECT_ID=$(az ad app show --id "$APP_ID" --query id -o tsv)
echo "  Object ID: $OBJECT_ID"

# Step 2: Create Secret
echo "[2/4] Creating client secret..."
SECRET=$(az ad app credential reset --id "$OBJECT_ID" --display-name "CIPP Secret" --years 2 --query password -o tsv)
echo "  Secret created"

# Step 3: Create Service Principal
echo "[3/4] Creating service principal..."
az ad sp create --id "$APP_ID" -o none 2>/dev/null || true
echo "  Service principal created"

# Step 4: Grant Admin Consent
echo "[4/4] Granting admin consent..."
sleep 5
az ad app permission admin-consent --id "$APP_ID" 2>/dev/null || echo "  (Run admin consent manually in Azure Portal if this fails)"
echo "  Admin consent granted"

# Output
TENANT_ID=$(az account show --query tenantId -o tsv)

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Add these to your backend/.env:"
echo ""
echo "AZURE_TENANT_ID=$TENANT_ID"
echo "AZURE_CLIENT_ID=$APP_ID"
echo "AZURE_CLIENT_SECRET=$SECRET"
echo "AUTH_TENANT_ID=$TENANT_ID"
echo "AUTH_CLIENT_ID=$APP_ID"
echo "AUTH_CLIENT_SECRET=$SECRET"
echo "AUTH_REDIRECT_URI=$REDIRECT_URI"
echo ""
echo "Permissions: Organization.Read.All, User.Read.All, Group.Read.All,"
echo "Directory.Read.All, Domain.Read.All, Application.Read.All,"
echo "DeviceManagementManagedDevices.Read.All, DeviceManagementConfiguration.Read.All,"
echo "Policy.Read.All, SecurityEvents.Read.All, IdentityRiskyUser.Read.All,"
echo "Reports.Read.All, SecurityActions.Read.All, Mail.Read,"
echo "Sites.Read.All, TeamSettings.Read.All"
