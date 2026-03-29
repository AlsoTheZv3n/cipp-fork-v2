"""PowerShell Runner client — communicates with the PS-Runner sidecar container.

The PS-Runner handles Exchange Online cmdlets that have no Graph API equivalent.
All commands are executed via predefined action handlers (no raw command execution).
"""
import httpx

from app.core.config import settings

# Timeout: Exchange cmdlets can be slow (especially Get-Mailbox -ResultSize Unlimited)
PS_RUNNER_TIMEOUT = 60.0
PS_RUNNER_CONNECT_TIMEOUT = 10.0


async def run_ps_action(action: str, tenant_id: str, **params) -> dict:
    """Execute a predefined PowerShell action via the PS-Runner sidecar.

    Args:
        action: The action name (e.g., "get_mailbox", "set_mailbox")
        tenant_id: The customer tenant ID to connect to
        **params: Action-specific parameters (e.g., identity="user@domain.com")

    Returns:
        dict with Results key containing the action output
    """
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(PS_RUNNER_TIMEOUT, connect=PS_RUNNER_CONNECT_TIMEOUT)
        ) as client:
            response = await client.post(
                f"{settings.ps_runner_url}/run",
                json={
                    "action": action,
                    "tenant_id": tenant_id,
                    "params": params,
                },
            )

            if response.status_code == 404:
                return {"Results": f"PS-Runner not available. Action '{action}' requires Exchange Online PowerShell."}
            if response.status_code == 400:
                data = response.json()
                return {"Results": f"PS-Runner error: {data.get('error', 'Bad request')}"}
            if response.status_code == 500:
                data = response.json()
                return {"Results": f"PS-Runner execution error: {data.get('error', 'Unknown error')}"}

            response.raise_for_status()
            return response.json()

    except httpx.ConnectError:
        return {"Results": f"PS-Runner is not running. Start it with 'docker compose up ps-runner'. Action '{action}' requires Exchange Online PowerShell."}
    except httpx.TimeoutException:
        return {"Results": f"PS-Runner timeout after {PS_RUNNER_TIMEOUT}s for action '{action}'."}
    except Exception as e:
        return {"Results": f"PS-Runner error: {str(e)}"}


async def ps_runner_health() -> dict:
    """Check if the PS-Runner sidecar is healthy."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ps_runner_url}/health")
            return response.json()
    except Exception:
        return {"status": "unavailable"}


async def ps_runner_actions() -> list:
    """List available PS-Runner actions."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ps_runner_url}/actions")
            data = response.json()
            return data.get("actions", [])
    except Exception:
        return []
