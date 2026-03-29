# PS Runner — Secure HTTP microservice for Exchange Online cmdlets
# NO raw command execution. Each action is a hardcoded function.
# Connects to Exchange Online per-tenant via certificate or app credentials.

param(
    [int]$Port = 8001
)

$ErrorActionPreference = "Stop"

# --- Connection Cache (avoid reconnecting for every request) ---
$script:ConnectionCache = @{}
$script:ConnectionExpiry = @{}

function Connect-Tenant {
    param([string]$TenantId)

    $now = Get-Date
    if ($script:ConnectionCache[$TenantId] -and $script:ConnectionExpiry[$TenantId] -gt $now) {
        return  # Already connected and not expired
    }

    # Disconnect previous if exists
    try { Disconnect-ExchangeOnline -Confirm:$false 2>$null } catch {}

    $appId = $env:AZURE_CLIENT_ID
    $certThumb = $env:AZURE_CERT_THUMBPRINT
    $clientSecret = $env:AZURE_CLIENT_SECRET

    if ($certThumb) {
        # Certificate-based auth (recommended for production)
        Connect-ExchangeOnline -AppId $appId -CertificateThumbprint $certThumb -Organization $TenantId -ShowBanner:$false
    }
    elseif ($clientSecret) {
        # Client secret auth via access token
        $tokenBody = @{
            grant_type    = "client_credentials"
            client_id     = $appId
            client_secret = $clientSecret
            scope         = "https://outlook.office365.com/.default"
        }
        $tokenResponse = Invoke-RestMethod -Uri "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token" -Method POST -Body $tokenBody
        Connect-ExchangeOnline -AccessToken $tokenResponse.access_token -Organization $TenantId -ShowBanner:$false
    }
    else {
        throw "No AZURE_CERT_THUMBPRINT or AZURE_CLIENT_SECRET configured for Exchange auth."
    }

    $script:ConnectionCache[$TenantId] = $true
    $script:ConnectionExpiry[$TenantId] = $now.AddMinutes(45)  # Refresh before 60min token expiry
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Connected to $TenantId"
}

# --- Action Handlers (NO Invoke-Expression, each is a dedicated function) ---

function Invoke-Action {
    param([string]$Action, [string]$TenantId, [hashtable]$Params)

    Connect-Tenant -TenantId $TenantId

    switch ($Action) {
        # --- Mailbox ---
        "get_mailbox" {
            $identity = $Params.identity
            if ($identity -eq "*") {
                Get-Mailbox -ResultSize Unlimited | Select-Object DisplayName, PrimarySmtpAddress, RecipientTypeDetails, IsShared, ForwardingSmtpAddress, DeliverToMailboxAndForward
            } else {
                Get-Mailbox -Identity $identity | Select-Object *
            }
        }
        "get_mailbox_permissions" {
            Get-MailboxPermission -Identity $Params.identity | Where-Object { $_.User -ne "NT AUTHORITY\SELF" } | Select-Object Identity, User, AccessRights, IsInherited
        }
        "set_mailbox" {
            $splat = @{ Identity = $Params.identity }
            if ($Params.ForwardingSmtpAddress) { $splat.ForwardingSmtpAddress = $Params.ForwardingSmtpAddress }
            if ($Params.DeliverToMailboxAndForward -ne $null) { $splat.DeliverToMailboxAndForward = [bool]$Params.DeliverToMailboxAndForward }
            if ($Params.ProhibitSendReceiveQuota) { $splat.ProhibitSendReceiveQuota = $Params.ProhibitSendReceiveQuota }
            if ($Params.ProhibitSendQuota) { $splat.ProhibitSendQuota = $Params.ProhibitSendQuota }
            if ($Params.IssueWarningQuota) { $splat.IssueWarningQuota = $Params.IssueWarningQuota }
            if ($Params.MaxSendSize) { $splat.MaxSendSize = $Params.MaxSendSize }
            if ($Params.MaxReceiveSize) { $splat.MaxReceiveSize = $Params.MaxReceiveSize }
            if ($Params.RecipientLimits) { $splat.RecipientLimits = $Params.RecipientLimits }
            if ($Params.LitigationHoldEnabled -ne $null) { $splat.LitigationHoldEnabled = [bool]$Params.LitigationHoldEnabled }
            if ($Params.RetentionHoldEnabled -ne $null) { $splat.RetentionHoldEnabled = [bool]$Params.RetentionHoldEnabled }
            if ($Params.RetentionPolicy) { $splat.RetentionPolicy = $Params.RetentionPolicy }
            if ($Params.MessageCopyForSentAsEnabled -ne $null) { $splat.MessageCopyForSentAsEnabled = [bool]$Params.MessageCopyForSentAsEnabled }
            if ($Params.Type) { $splat.Type = $Params.Type }
            if ($Params.HiddenFromAddressListsEnabled -ne $null) { $splat.HiddenFromAddressListsEnabled = [bool]$Params.HiddenFromAddressListsEnabled }
            Set-Mailbox @splat
            @{ status = "success"; message = "Mailbox $($Params.identity) updated." }
        }
        "add_mailbox_permission" {
            Add-MailboxPermission -Identity $Params.identity -User $Params.user -AccessRights $Params.accessRights -AutoMapping ([bool]$Params.autoMapping)
            @{ status = "success"; message = "Permission granted." }
        }
        "remove_mailbox_permission" {
            Remove-MailboxPermission -Identity $Params.identity -User $Params.user -AccessRights $Params.accessRights -Confirm:$false
            @{ status = "success"; message = "Permission removed." }
        }

        # --- CAS Mailbox ---
        "get_cas_mailbox" {
            Get-CASMailbox -Identity $Params.identity | Select-Object *
        }
        "set_cas_mailbox" {
            $splat = @{ Identity = $Params.identity }
            if ($Params.ActiveSyncEnabled -ne $null) { $splat.ActiveSyncEnabled = [bool]$Params.ActiveSyncEnabled }
            if ($Params.ImapEnabled -ne $null) { $splat.ImapEnabled = [bool]$Params.ImapEnabled }
            if ($Params.PopEnabled -ne $null) { $splat.PopEnabled = [bool]$Params.PopEnabled }
            if ($Params.OWAEnabled -ne $null) { $splat.OWAEnabled = [bool]$Params.OWAEnabled }
            if ($Params.MAPIEnabled -ne $null) { $splat.MAPIEnabled = [bool]$Params.MAPIEnabled }
            if ($Params.EwsEnabled -ne $null) { $splat.EwsEnabled = [bool]$Params.EwsEnabled }
            Set-CASMailbox @splat
            @{ status = "success"; message = "CAS mailbox $($Params.identity) updated." }
        }

        # --- Transport Rules ---
        "get_transport_rules" {
            Get-TransportRule | Select-Object Name, State, Priority, Mode, SentTo, SentToScope, FromScope, Description
        }
        "new_transport_rule" {
            $splat = @{ Name = $Params.name }
            if ($Params.FromScope) { $splat.FromScope = $Params.FromScope }
            if ($Params.SentToScope) { $splat.SentToScope = $Params.SentToScope }
            if ($Params.Priority) { $splat.Priority = [int]$Params.Priority }
            New-TransportRule @splat
            @{ status = "success"; message = "Transport rule '$($Params.name)' created." }
        }
        "remove_transport_rule" {
            Remove-TransportRule -Identity $Params.identity -Confirm:$false
            @{ status = "success"; message = "Transport rule removed." }
        }

        # --- Spam / Content Filter ---
        "get_spam_filter" {
            Get-HostedContentFilterPolicy | Select-Object Name, IsDefault, HighConfidenceSpamAction, SpamAction, BulkSpamAction, PhishSpamAction, BulkThreshold
        }
        "set_spam_filter" {
            $splat = @{ Identity = $Params.identity }
            if ($Params.HighConfidenceSpamAction) { $splat.HighConfidenceSpamAction = $Params.HighConfidenceSpamAction }
            if ($Params.SpamAction) { $splat.SpamAction = $Params.SpamAction }
            if ($Params.BulkSpamAction) { $splat.BulkSpamAction = $Params.BulkSpamAction }
            if ($Params.BulkThreshold) { $splat.BulkThreshold = [int]$Params.BulkThreshold }
            Set-HostedContentFilterPolicy @splat
            @{ status = "success"; message = "Spam filter '$($Params.identity)' updated." }
        }

        # --- Connection Filter ---
        "get_connection_filter" {
            Get-HostedConnectionFilterPolicy | Select-Object Name, IPAllowList, IPBlockList, EnableSafeList
        }
        "set_connection_filter" {
            $splat = @{ Identity = $Params.identity }
            if ($Params.IPAllowList) { $splat.IPAllowList = $Params.IPAllowList }
            if ($Params.IPBlockList) { $splat.IPBlockList = $Params.IPBlockList }
            Set-HostedConnectionFilterPolicy @splat
            @{ status = "success"; message = "Connection filter updated." }
        }

        # --- Anti-Phishing ---
        "get_anti_phish" {
            Get-AntiPhishPolicy | Select-Object Name, Enabled, IsDefault, PhishThresholdLevel, EnableMailboxIntelligence, EnableSpoofIntelligence
        }
        "set_anti_phish" {
            $splat = @{ Identity = $Params.identity }
            if ($Params.Enabled -ne $null) { $splat.Enabled = [bool]$Params.Enabled }
            if ($Params.PhishThresholdLevel) { $splat.PhishThresholdLevel = [int]$Params.PhishThresholdLevel }
            Set-AntiPhishPolicy @splat
            @{ status = "success"; message = "Anti-phish policy updated." }
        }

        # --- Malware Filter ---
        "get_malware_filter" {
            Get-MalwareFilterPolicy | Select-Object Name, IsDefault, Action, EnableFileFilter, FileTypes
        }
        "set_malware_filter" {
            $splat = @{ Identity = $Params.identity }
            if ($Params.EnableFileFilter -ne $null) { $splat.EnableFileFilter = [bool]$Params.EnableFileFilter }
            Set-MalwareFilterPolicy @splat
            @{ status = "success"; message = "Malware filter updated." }
        }

        # --- Safe Links ---
        "get_safe_links" {
            Get-SafeLinksPolicy | Select-Object Name, IsEnabled, IsBuiltInProtection, DoNotRewriteUrls, EnableForInternalSenders
        }

        # --- Safe Attachments ---
        "get_safe_attachments" {
            Get-SafeAttachmentPolicy | Select-Object Name, Action, Enable, Redirect, RedirectAddress
        }

        # --- Quarantine ---
        "get_quarantine_messages" {
            $splat = @{ PageSize = 100 }
            if ($Params.startDate) { $splat.StartExpiresDate = [datetime]$Params.startDate }
            Get-QuarantineMessage @splat | Select-Object MessageId, SenderAddress, RecipientAddress, Subject, ReceivedTime, Type, ReleaseStatus, PolicyName
        }
        "release_quarantine_message" {
            Release-QuarantineMessage -Identity $Params.identity -ReleaseToAll
            @{ status = "success"; message = "Quarantine message released." }
        }
        "delete_quarantine_message" {
            Delete-QuarantineMessage -Identity $Params.identity -Confirm:$false
            @{ status = "success"; message = "Quarantine message deleted." }
        }
        "get_quarantine_policy" {
            Get-QuarantinePolicy | Select-Object Name, EndUserQuarantinePermissionsValue, ESNEnabled, MultiLanguageSetting
        }

        # --- Message Trace ---
        "get_message_trace" {
            $splat = @{ PageSize = 100 }
            if ($Params.senderAddress) { $splat.SenderAddress = $Params.senderAddress }
            if ($Params.recipientAddress) { $splat.RecipientAddress = $Params.recipientAddress }
            if ($Params.startDate) { $splat.StartDate = [datetime]$Params.startDate }
            if ($Params.endDate) { $splat.EndDate = [datetime]$Params.endDate }
            Get-MessageTrace @splat | Select-Object MessageId, SenderAddress, RecipientAddress, Subject, Status, Received, Size
        }

        # --- Tenant Allow/Block ---
        "get_tenant_allow_block" {
            Get-TenantAllowBlockListItems -ListType $Params.listType | Select-Object Value, Action, ExpirationDate, ListType, Notes
        }
        "add_tenant_allow_block" {
            New-TenantAllowBlockListItems -ListType $Params.listType -Entries $Params.entries -Action $Params.action
            @{ status = "success"; message = "Allow/Block entry added." }
        }
        "remove_tenant_allow_block" {
            Remove-TenantAllowBlockListItems -ListType $Params.listType -Entries $Params.entries
            @{ status = "success"; message = "Allow/Block entry removed." }
        }

        # --- Exchange Connectors ---
        "get_inbound_connector" {
            Get-InboundConnector | Select-Object Name, Enabled, ConnectorType, SenderDomains, SenderIPAddresses
        }
        "get_outbound_connector" {
            Get-OutboundConnector | Select-Object Name, Enabled, ConnectorType, RecipientDomains, SmartHosts
        }

        # --- Shared / Room / Equipment ---
        "new_shared_mailbox" {
            New-Mailbox -Shared -Name $Params.name -PrimarySmtpAddress $Params.email
            @{ status = "success"; message = "Shared mailbox '$($Params.name)' created." }
        }
        "new_room_mailbox" {
            New-Mailbox -Room -Name $Params.name -PrimarySmtpAddress $Params.email
            @{ status = "success"; message = "Room mailbox '$($Params.name)' created." }
        }
        "new_equipment_mailbox" {
            New-Mailbox -Equipment -Name $Params.name -PrimarySmtpAddress $Params.email
            @{ status = "success"; message = "Equipment mailbox '$($Params.name)' created." }
        }

        # --- Calendar Processing ---
        "get_calendar_processing" {
            Get-CalendarProcessing -Identity $Params.identity | Select-Object *
        }
        "set_calendar_processing" {
            $splat = @{ Identity = $Params.identity }
            if ($Params.AutomateProcessing) { $splat.AutomateProcessing = $Params.AutomateProcessing }
            if ($Params.BookingWindowInDays) { $splat.BookingWindowInDays = [int]$Params.BookingWindowInDays }
            Set-CalendarProcessing @splat
            @{ status = "success"; message = "Calendar processing updated." }
        }

        # --- Restricted Users ---
        "get_blocked_sender" {
            Get-BlockedSenderAddress | Select-Object SenderAddress, Reason, Status
        }
        "remove_blocked_sender" {
            Remove-BlockedSenderAddress -SenderAddress $Params.senderAddress
            @{ status = "success"; message = "Sender unblocked." }
        }

        default {
            throw "Unknown action: $Action"
        }
    }
}

# --- HTTP Server ---

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://+:$Port/")
$listener.Start()
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] PS Runner ready on port $Port"
Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Available actions: $((Invoke-Action).Keys -join ', ')" -ErrorAction SilentlyContinue

function Send-Response {
    param($Response, [int]$StatusCode = 200, $Body)
    $json = if ($Body -is [string]) { $Body } else { $Body | ConvertTo-Json -Depth 10 -Compress }
    $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
    $Response.StatusCode = $StatusCode
    $Response.ContentType = "application/json; charset=utf-8"
    $Response.ContentLength64 = $buffer.Length
    $Response.OutputStream.Write($buffer, 0, $buffer.Length)
    $Response.Close()
}

while ($listener.IsListening) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response

    try {
        $path = $request.Url.AbsolutePath

        # Health check
        if ($path -eq "/health") {
            Send-Response -Response $response -Body @{ status = "ok"; connections = $script:ConnectionCache.Count }
            continue
        }

        # List available actions
        if ($path -eq "/actions" -and $request.HttpMethod -eq "GET") {
            $actions = @(
                "get_mailbox", "get_mailbox_permissions", "set_mailbox",
                "add_mailbox_permission", "remove_mailbox_permission",
                "get_cas_mailbox", "set_cas_mailbox",
                "get_transport_rules", "new_transport_rule", "remove_transport_rule",
                "get_spam_filter", "set_spam_filter",
                "get_connection_filter", "set_connection_filter",
                "get_anti_phish", "set_anti_phish",
                "get_malware_filter", "set_malware_filter",
                "get_safe_links", "get_safe_attachments",
                "get_quarantine_messages", "release_quarantine_message", "delete_quarantine_message", "get_quarantine_policy",
                "get_message_trace",
                "get_tenant_allow_block", "add_tenant_allow_block", "remove_tenant_allow_block",
                "get_inbound_connector", "get_outbound_connector",
                "new_shared_mailbox", "new_room_mailbox", "new_equipment_mailbox",
                "get_calendar_processing", "set_calendar_processing",
                "get_blocked_sender", "remove_blocked_sender"
            )
            Send-Response -Response $response -Body @{ actions = $actions; count = $actions.Count }
            continue
        }

        # Only accept POST /run
        if ($request.HttpMethod -ne "POST" -or $path -ne "/run") {
            Send-Response -Response $response -StatusCode 404 -Body @{ error = "Not found. Use POST /run" }
            continue
        }

        # Parse request
        $reader = [System.IO.StreamReader]::new($request.InputStream, [System.Text.Encoding]::UTF8)
        $json = $reader.ReadToEnd() | ConvertFrom-Json

        if (-not $json.action -or -not $json.tenant_id) {
            Send-Response -Response $response -StatusCode 400 -Body @{ error = "action and tenant_id are required." }
            continue
        }

        # Convert params from PSCustomObject to hashtable
        $params = @{}
        if ($json.params) {
            $json.params.PSObject.Properties | ForEach-Object { $params[$_.Name] = $_.Value }
        }

        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $($json.action) for $($json.tenant_id)"

        # Execute action
        $result = Invoke-Action -Action $json.action -TenantId $json.tenant_id -Params $params
        Send-Response -Response $response -Body @{ Results = $result }
    }
    catch {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ERROR: $($_.Exception.Message)" -ForegroundColor Red
        # Invalidate connection cache on auth errors
        if ($_.Exception.Message -match "token|auth|expired|connect") {
            $script:ConnectionCache.Clear()
            $script:ConnectionExpiry.Clear()
        }
        Send-Response -Response $response -StatusCode 500 -Body @{ error = $_.Exception.Message }
    }
}
