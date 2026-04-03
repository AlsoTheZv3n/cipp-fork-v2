"""PowerShell Runner client — communicates with the PS-Runner sidecar container.

The PS-Runner handles Exchange Online cmdlets that have no Graph API equivalent.
All commands are executed via predefined action handlers (no raw command execution).
"""
import httpx

from app.core.config import settings
from app.core.response import cipp_response

# Timeout: Exchange cmdlets can be slow (especially Get-Mailbox -ResultSize Unlimited)
PS_RUNNER_TIMEOUT = 60.0
PS_RUNNER_CONNECT_TIMEOUT = 10.0


async def run_ps_action(action: str, tenant_id: str, **params) -> dict:
    """Execute a predefined PowerShell action via the PS-Runner sidecar.

    Returns cipp_response() format: {Results: [...]} or {Results: [], Metadata: {error: ...}}
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
                return cipp_response([], error=f"PS-Runner not available. Action '{action}' requires Exchange Online PowerShell.")
            if response.status_code == 400:
                try:
                    err = response.json()
                    return cipp_response([], error=f"PS-Runner: {err.get('error', 'Bad request')}")
                except Exception:
                    return cipp_response([], error="PS-Runner: Bad request")
            if response.status_code == 500:
                try:
                    err = response.json()
                    return cipp_response([], error=f"PS-Runner: {err.get('error', 'Internal error')}")
                except Exception:
                    return cipp_response([], error="PS-Runner: Internal error")

            response.raise_for_status()
            data = response.json()
            # PS-Runner returns {Results: ...} — pass through
            if isinstance(data, dict) and "Results" in data:
                return data
            # If it returns a list, wrap it
            if isinstance(data, list):
                return cipp_response(data)
            return cipp_response([data] if data else [])

    except httpx.ConnectError:
        return cipp_response([], error="PS-Runner is not running. Start with: docker compose up ps-runner")
    except httpx.TimeoutException:
        return cipp_response([], error=f"PS-Runner timeout ({PS_RUNNER_TIMEOUT}s) for action '{action}'")
    except Exception as e:
        return cipp_response([], error=str(e)[:200])


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
