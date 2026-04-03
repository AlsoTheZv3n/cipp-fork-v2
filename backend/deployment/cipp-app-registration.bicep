// CIPP App Registration with all required Microsoft Graph permissions
// Deploy: az deployment group create --resource-group <rg> --template-file cipp-app-registration.bicep --parameters displayName=cipp2
// Or: az deployment sub create --location westeurope --template-file cipp-app-registration.bicep

@description('Display name for the CIPP app registration')
param displayName string = 'cipp2'

@description('Redirect URI for the CIPP frontend (dev: http://localhost:3001/.auth/callback)')
param redirectUri string = 'http://localhost:3001/.auth/callback'

// Microsoft Graph App ID (constant across all tenants)
var graphApiId = '00000003-0000-0000-c000-000000000000'

// Microsoft Graph Application Permission IDs
// Reference: https://learn.microsoft.com/en-us/graph/permissions-reference
var graphPermissions = [
  // Organization
  { id: '498476ce-e0fe-48b0-b801-37ba7e2685c6', name: 'Organization.Read.All' }
  // Users
  { id: 'df021288-bdef-4463-88db-98f22de89214', name: 'User.Read.All' }
  // Groups
  { id: '5b567255-7703-4780-807c-7be8301ae99b', name: 'Group.Read.All' }
  // Directory
  { id: '7ab1d382-f21e-4acd-a863-ba3e13f7da61', name: 'Directory.Read.All' }
  // Domains
  { id: 'dbb9058a-0e50-45d7-ae91-66909b5d4664', name: 'Domain.Read.All' }
  // Applications
  { id: 'c79f8feb-a9db-4090-85f9-90d820caa0eb', name: 'Application.Read.All' }
  // Intune Devices
  { id: 'b0afded3-3588-46d8-8b3d-9842eff778da', name: 'DeviceManagementManagedDevices.Read.All' }
  // Intune Configuration
  { id: 'dc377aa6-52d8-4e23-b271-b3b753e16f74', name: 'DeviceManagementConfiguration.Read.All' }
  // Policies (Conditional Access)
  { id: '246dd0d5-5bd0-4def-940b-0421030a5b68', name: 'Policy.Read.All' }
  // Security Events
  { id: 'bf394140-e372-4bf9-a898-299cfc7564e5', name: 'SecurityEvents.Read.All' }
  // Identity Protection - Risky Users
  { id: 'dc5007c0-2d7d-4c42-879c-2dab87571379', name: 'IdentityRiskyUser.Read.All' }
  // Audit Logs
  { id: 'b0afded3-3588-46d8-8b3d-9842eff778da', name: 'AuditLog.Read.All' }
  // Reports
  { id: '230c1aed-a721-4c5d-9cb4-a90514e508ef', name: 'Reports.Read.All' }
  // Security Actions (Secure Score)
  { id: '5e0edab9-c148-49d0-b423-ac253e121825', name: 'SecurityActions.Read.All' }
  // Mail
  { id: '810c84a8-4a9e-49e6-bf7d-12d183f40d01', name: 'Mail.Read' }
  // SharePoint Sites
  { id: '332a536c-c7ef-4017-ab91-336970924f0d', name: 'Sites.Read.All' }
  // Teams
  { id: '242607bd-1d2c-432c-82eb-bdb27baa23ab', name: 'TeamSettings.Read.All' }
]

resource cippApp 'Microsoft.Graph/applications@v1.0' = {
  displayName: displayName
  signInAudience: 'AzureADMyOrg'
  web: {
    redirectUris: [
      redirectUri
    ]
  }
  requiredResourceAccess: [
    {
      resourceAppId: graphApiId
      resourceAccess: [for perm in graphPermissions: {
        id: perm.id
        type: 'Role' // Application permission
      }]
    }
  ]
}

resource cippSp 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: cippApp.appId
}

output appId string = cippApp.appId
output objectId string = cippApp.id
output displayName string = cippApp.displayName
