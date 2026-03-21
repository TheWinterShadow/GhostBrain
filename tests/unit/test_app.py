"""Unit tests for ghost_brain.app."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from ghost_brain.app import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client."""
    return TestClient(app)


def test_health(client: TestClient) -> None:
    """Health endpoint should return 200 and status ok."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_openapi_schema(client: TestClient) -> None:
    """OpenAPI schema should list /health."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    data = r.json()
    assert "/health" in data.get("paths", {})
