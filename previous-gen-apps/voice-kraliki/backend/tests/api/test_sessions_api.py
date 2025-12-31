"""Tests for session management API."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.config.settings import get_settings
from app.providers.registry import get_provider_registry


@pytest.fixture
def client(monkeypatch) -> TestClient:
    """FastAPI client with provider credentials set."""

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC1234567890")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "test-token")
    from app.settings import provider as provider_settings

    provider_settings._IN_MEMORY_STORE.clear()  # type: ignore[attr-defined]
    provider_settings._DB_AVAILABLE = False  # type: ignore[attr-defined]
    get_settings.cache_clear()
    get_provider_registry.cache_clear()
    app = create_app()
    return TestClient(app)


def test_create_session(client: TestClient) -> None:
    """Session creation should return session metadata."""

    payload = {
        "provider": "openai",
        "strategy": "realtime",
        "telephony_provider": "twilio",
        "phone_number": "+15550000000",
        "metadata": {"test": "value"},
    }

    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["provider_type"] == "openai"
    assert data["strategy"] == "realtime"
    assert data["telephony_provider"] == "twilio"
    assert data["metadata"]["test"] == "value"
