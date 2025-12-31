"""Tests for provider discovery endpoints."""

import os

import pytest
from fastapi.testclient import TestClient

from datetime import datetime, timezone

from app.main import create_app
from app.config.settings import get_settings
from app.settings import provider as provider_settings


@pytest.fixture
def client(monkeypatch) -> TestClient:
    """Provide FastAPI test client with provider credentials configured."""

    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    provider_settings._IN_MEMORY_STORE.clear()  # type: ignore[attr-defined]
    provider_settings._IN_MEMORY_STORE[provider_settings.SETTINGS_KEY] = {  # type: ignore[attr-defined]
        "value": provider_settings.DEFAULT_PROVIDER_SETTINGS,  # type: ignore[attr-defined]
        "updated_at": datetime.now(timezone.utc),
    }
    provider_settings._DB_AVAILABLE = False  # type: ignore[attr-defined]
    get_settings.cache_clear()
    app = create_app()
    return TestClient(app)


def test_list_providers(client: TestClient) -> None:
    """Ensure /api/v1/providers returns AI and telephony metadata."""

    response = client.get('/api/v1/providers')
    assert response.status_code == 200

    data = response.json()
    assert 'providers' in data
    assert 'telephony' in data

    provider_ids = {item['id'] for item in data['providers']}
    assert 'openai' in provider_ids
    assert 'gemini' in provider_ids

    telephony_ids = {item['id'] for item in data['telephony']}
    assert 'twilio' in telephony_ids
    assert 'telnyx' in telephony_ids
