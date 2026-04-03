"""CIPP Response helpers.

The CIPP frontend expects most list endpoints to return:
    {"Results": [...], "Metadata": {"nextLink": "..."}}

CippDataTable extracts data via `dataKey="Results"` using getNestedValue().

Use `cipp_response()` for all endpoints consumed by CippDataTable/CippTablePage.
Use direct returns for special endpoints (dashboard, auth, settings).
"""


def cipp_response(data, next_link: str | None = None) -> dict:
    """Wrap data in standard CIPP response format.

    Args:
        data: The response data (usually a list)
        next_link: Optional pagination URL for Metadata.nextLink

    Returns:
        {"Results": data, "Metadata": {"nextLink": next_link}} if next_link
        {"Results": data} otherwise
    """
    result = {"Results": data}
    if next_link:
        result["Metadata"] = {"nextLink": next_link}
    return result
