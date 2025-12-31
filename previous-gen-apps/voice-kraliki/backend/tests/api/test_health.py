"""Tests for health check endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the application.

    Returns:
        TestClient: FastAPI test client
    """
    app = create_app()
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint.

    Args:
        client: FastAPI test client
    """
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    assert "environment" in data


def test_root_endpoint(client: TestClient) -> None:
    """Test the root endpoint.

    Args:
        client: FastAPI test client
    """
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


def test_health_check_response_structure(client: TestClient) -> None:
    """Test that health check returns correct response structure.

    Args:
        client: FastAPI test client
    """
    response = client.get("/health")
    data = response.json()

    # Check all required fields are present
    required_fields = ["status", "service", "version", "environment"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Check field types
    assert isinstance(data["status"], str)
    assert isinstance(data["service"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["environment"], str)
