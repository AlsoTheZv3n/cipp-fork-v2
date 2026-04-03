"""Shared tools for CIPP AI Agents."""
import json
import os
import re
import subprocess

import httpx

BACKEND_URL = os.getenv("CIPP_BACKEND_URL", "http://127.0.0.1:8055")
FRONTEND_URL = os.getenv("CIPP_FRONTEND_URL", "http://localhost:3001")
PROJECT_ROOT = os.getenv("CIPP_PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
TENANT = os.getenv("CIPP_TEST_TENANT", "demo-tenant-contoso")


def api_get(path: str, params: dict = None) -> dict:
    """Make a GET request to the backend API. Returns {status, data, error}."""
    try:
        r = httpx.get(f"{BACKEND_URL}{path}", params=params, timeout=15)
        return {"status": r.status_code, "data": r.json() if r.status_code == 200 else None, "error": r.text if r.status_code >= 400 else None}
    except Exception as e:
        return {"status": 0, "data": None, "error": str(e)}


def api_post(path: str, body: dict = None) -> dict:
    """Make a POST request to the backend API."""
    try:
        r = httpx.post(f"{BACKEND_URL}{path}", json=body or {}, timeout=15)
        return {"status": r.status_code, "data": r.json() if r.status_code < 500 else None, "error": r.text if r.status_code >= 400 else None}
    except Exception as e:
        return {"status": 0, "data": None, "error": str(e)}


def check_response_format(path: str, expected_format: str, params: dict = None) -> dict:
    """Check if an endpoint returns the expected format.

    expected_format: 'results_array' | 'results_nested' | 'direct_array' | 'direct_object'
    Returns {ok, path, expected, actual, details}
    """
    result = api_get(path, params)
    if result["status"] != 200:
        return {"ok": False, "path": path, "expected": expected_format, "actual": f"HTTP {result['status']}", "details": result["error"][:200] if result["error"] else ""}

    data = result["data"]
    actual = "unknown"

    if isinstance(data, list):
        actual = "direct_array"
    elif isinstance(data, dict):
        if "Results" in data:
            if isinstance(data["Results"], list):
                actual = "results_array"
            elif isinstance(data["Results"], dict):
                actual = "results_nested"
            else:
                actual = "results_other"
        else:
            actual = "direct_object"

    ok = actual == expected_format
    return {"ok": ok, "path": path, "expected": expected_format, "actual": actual, "details": str(list(data.keys()) if isinstance(data, dict) else f"len={len(data)}")[:100]}


def read_file(filepath: str) -> str:
    """Read a file from the project."""
    full_path = os.path.join(PROJECT_ROOT, filepath) if not os.path.isabs(filepath) else filepath
    try:
        with open(full_path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"ERROR: {e}"


def write_file(filepath: str, content: str) -> str:
    """Write content to a file."""
    full_path = os.path.join(PROJECT_ROOT, filepath) if not os.path.isabs(filepath) else filepath
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"OK: wrote {len(content)} bytes to {filepath}"
    except Exception as e:
        return f"ERROR: {e}"


def search_files(pattern: str, directory: str = "src", file_glob: str = "*.js,*.jsx") -> list:
    """Search for a pattern in files. Returns list of {file, line, text}."""
    search_dir = os.path.join(PROJECT_ROOT, directory)
    results = []
    extensions = [ext.replace("*", "") for ext in file_glob.split(",")]

    for root, dirs, files in os.walk(search_dir):
        for f in files:
            if not any(f.endswith(ext) for ext in extensions):
                continue
            filepath = os.path.join(root, f)
            try:
                with open(filepath, encoding="utf-8") as fh:
                    for i, line in enumerate(fh, 1):
                        if pattern in line:
                            rel = os.path.relpath(filepath, PROJECT_ROOT)
                            results.append({"file": rel, "line": i, "text": line.strip()[:150]})
            except Exception:
                continue
    return results[:50]  # Limit results


def list_endpoints() -> list:
    """List all backend endpoints with their methods and response formats."""
    import sys
    sys.path.insert(0, BACKEND_ROOT)
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://cipp:changeme@localhost:5433/cipp")

    from app.main import app
    import inspect

    endpoints = []
    for route in app.routes:
        if not hasattr(route, "path") or not hasattr(route, "methods"):
            continue
        src = inspect.getsource(route.endpoint)
        for method in route.methods:
            if method in ("GET", "POST"):
                endpoints.append({
                    "method": method,
                    "path": route.path,
                    "has_graph": "GraphClient" in src,
                    "has_db": "db." in src or "session" in src,
                    "has_ps_runner": "run_ps_action" in src,
                    "returns_results": '"Results"' in src,
                })
    return endpoints


def run_test_suite() -> dict:
    """Run the pytest test suite and return results."""
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=line", "-q"],
            capture_output=True, text=True, cwd=BACKEND_ROOT, timeout=120,
            env={**os.environ, "PYTHONPATH": ".", "DEMO_MODE": "true",
                 "DATABASE_URL": "postgresql+asyncpg://cipp:changeme@localhost:5433/cipp"}
        )
        lines = result.stdout.split("\n")
        summary = [l for l in lines if "passed" in l or "failed" in l or "error" in l]
        failures = [l for l in lines if "FAILED" in l]
        return {"returncode": result.returncode, "summary": summary, "failures": failures, "total_lines": len(lines)}
    except Exception as e:
        return {"returncode": -1, "summary": [], "failures": [], "error": str(e)}


def check_frontend_page(path: str) -> dict:
    """Check if a frontend page loads without 500 errors."""
    try:
        r = httpx.get(f"{FRONTEND_URL}{path}", timeout=10, follow_redirects=True)
        return {"status": r.status_code, "path": path, "ok": r.status_code < 500}
    except Exception as e:
        return {"status": 0, "path": path, "ok": False, "error": str(e)}
