"""Tests for provider settings endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import provider as provider_settings


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client fixture."""

    app = create_app()
    return TestClient(app)


def reset_in_memory_store() -> None:
    provider_settings._IN_MEMORY_STORE.clear()  # type: ignore[attr-defined]
    provider_settings._DB_AVAILABLE = False  # type: ignore[attr-defined]


def test_provider_settings_defaults(client: TestClient) -> None:
    """GET should return default settings when none are stored."""

    reset_in_memory_store()

    response = client.get("/api/v1/settings/provider")
    assert response.status_code == 200

    data = response.json()
    settings = data["settings"]

    assert settings["default_provider"] == provider_settings.DEFAULT_PROVIDER_SETTINGS["default_provider"]
    assert settings["telephony_provider"] == provider_settings.DEFAULT_PROVIDER_SETTINGS["telephony_provider"]
    assert settings["telephony_from_number"] in (None, "", provider_settings._DEFAULT_TELEPHONY_FROM)  # type: ignore[attr-defined]
    assert data["updated_at"]


def test_provider_settings_update(client: TestClient) -> None:
    """PUT should persist settings and return stored values."""

    reset_in_memory_store()

    payload = {
        "default_provider": "gemini",
        "strategy": "realtime",
        "openai_model": "gpt-4o-realtime-preview-2024-12-17",
        "telephony_provider": "telnyx",
        "telephony_from_number": "+15551234567",
        "fallback_enabled": True,
        "fallback_order": ["gemini", "openai"],
        "latency_preference": "low",
    }

    put_response = client.put("/api/v1/settings/provider", json=payload)
    assert put_response.status_code == 200
    assert put_response.json()["settings"]["telephony_provider"] == "telnyx"

    get_response = client.get("/api/v1/settings/provider")
    assert get_response.status_code == 200
    assert get_response.json()["settings"]["telephony_provider"] == "telnyx"
