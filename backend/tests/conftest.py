"""Shared pytest fixtures for CIPP backend tests.

Usage: cd backend && PYTHONPATH=. python -m pytest tests/ -v
Requires the backend running in DEMO_MODE on port 8055.
"""
import os
import pytest
import httpx

BASE_URL = os.getenv("TEST_API_URL", "http://127.0.0.1:8055")
TENANT = "demo-tenant-contoso"
FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3001")


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def tenant():
    return TENANT


@pytest.fixture(scope="session")
def frontend_url():
    return FRONTEND_URL


@pytest.fixture(scope="session")
def client():
    """Reusable httpx client for the whole test session."""
    with httpx.Client(base_url=BASE_URL, timeout=15) as c:
        yield c


@pytest.fixture(scope="session")
def frontend_client():
    """Reusable httpx client for frontend tests."""
    with httpx.Client(base_url=FRONTEND_URL, timeout=15, follow_redirects=False) as c:
        yield c
