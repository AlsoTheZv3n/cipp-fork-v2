"""CIPP Response helpers.

The CIPP frontend expects most list endpoints to return:
    {"Results": [...], "Metadata": {"nextLink": "..."}}

CippDataTable extracts data via `dataKey="Results"` using getNestedValue().

Use `cipp_response()` for all endpoints consumed by CippDataTable/CippTablePage.
Use direct returns for special endpoints (dashboard, auth, settings).
"""


def cipp_response(data, next_link: str | None = None, error: str | None = None) -> dict:
    """Wrap data in standard CIPP response format.

    Args:
        data: The response data (usually a list)
        next_link: Optional pagination URL for Metadata.nextLink
        error: Optional error message for Metadata.error

    Returns:
        {"Results": data} with optional Metadata
    """
    result = {"Results": data}
    metadata = {}
    if next_link:
        metadata["nextLink"] = next_link
    if error:
        metadata["error"] = error
    if metadata:
        result["Metadata"] = metadata
    return result


def cipp_error(message: str, status_code: int = 400) -> dict:
    """Return a CIPP-compatible error response.

    The frontend checks for: data.error, data.message, data.result, data.Results
    """
    return {"Results": [], "error": message, "Metadata": {"error": message}}
