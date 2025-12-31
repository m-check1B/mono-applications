"""Tests for telephony outbound and webhook endpoints."""

import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.config.settings import get_settings
from app.main import create_app
from app.telephony import state as telephony_state


class StubDefaults:
    def __init__(self):
        self.default_provider = type('Enum', (), {'value': 'openai'})()
        self.openai_model = 'gpt-4o-mini-realtime-preview-2024-12-17'
        self.strategy = 'realtime'
        self.telephony_provider = type('Enum', (), {'value': 'telnyx'})()
        self.telephony_from_number = '+15550000000'


class StubSession:
    def __init__(self, request):
        self.id = uuid4()
        self.provider_type = request.provider or request.provider_type or 'openai'
        self.provider_model = request.provider_model or 'gpt-4o-mini-realtime-preview-2024-12-17'
        self.strategy = request.strategy or 'realtime'
        self.telephony_provider = request.telephony_provider
        self.system_prompt = request.system_prompt
        self.temperature = request.temperature
        self.metadata = request.metadata


class StubSessionManager:
    def __init__(self):
        self.sessions = {}
        self.ended = []

    async def create_session(self, request):
        session = StubSession(request)
        self.sessions[session.id] = session
        return session

    async def start_session(self, session_id):
        return

    async def end_session(self, session_id):
        self.ended.append(session_id)
        self.sessions.pop(session_id, None)

    def get_session(self, session_id):
        return self.sessions.get(session_id)


class StubAdapter:
    def __init__(self, registry, telephony_type):
        self.registry = registry
        self.telephony_type = telephony_type
        self.last_params = None
        self.last_stream_url = None

    async def setup_call(self, params):
        self.last_params = params
        return {"call_id": "CAstub"}

    def generate_answer_twiml(self, stream_url, stream_name="audio-stream"):
        self.last_stream_url = stream_url
        return f"<Response>{stream_url}</Response>"

    async def close(self):
        return


class StubRegistry:
    def __init__(self):
        self.adapters = []

    def create_telephony_adapter(self, telephony_type):
        adapter = StubAdapter(self, telephony_type)
        self.adapters.append(adapter)
        return adapter


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv('TWILIO_ACCOUNT_SID', 'AC1234567890')
    monkeypatch.setenv('TWILIO_AUTH_TOKEN', 'test-token')
    monkeypatch.setenv('PUBLIC_URL', 'https://api.test')
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')

    stub_defaults = StubDefaults()
    monkeypatch.setattr('app.telephony.routes.fetch_provider_defaults', lambda: (stub_defaults, datetime.now(timezone.utc)))

    stub_registry = StubRegistry()
    monkeypatch.setattr('app.telephony.routes.get_provider_registry', lambda: stub_registry)

    stub_manager = StubSessionManager()
    monkeypatch.setattr('app.telephony.routes.get_session_manager', lambda: stub_manager)

    telephony_state._CALL_TO_SESSION.clear()
    telephony_state._SESSION_TO_CALL.clear()

    get_settings.cache_clear()

    app = create_app()
    client = TestClient(app)

    yield client, stub_registry, stub_manager

    client.close()
    get_settings.cache_clear()


def test_outbound_call_initializes_session(env) -> None:
    client, registry, session_manager = env

    response = client.post(
        "/api/v1/telephony/outbound",
        json={
            "to_number": "+15551239999",
        },
    )

    assert response.status_code == 202, response.text
    data = response.json()

    assert data["status"] == "accepted"
    assert data["telephony_provider"] == "telnyx"
    expected_prefix = f"wss://api.test/ws/sessions/{data['session_id']}"
    assert data["stream_url"] == expected_prefix
    assert registry.adapters[0].last_stream_url == expected_prefix
    assert data["call_sid"] == "CAstub"
    assert data["from_number"] == "+15550000000"
    assert data["to_number"] == "+15551239999"
    assert registry.adapters[0].last_params["from_number"] == "+15550000000"
    assert telephony_state.get_session_for_call("CAstub")


def test_outbound_call_respects_explicit_from(env) -> None:
    client, registry, session_manager = env

    response = client.post(
        "/api/v1/telephony/outbound",
        json={
            "from_number": "+15551230000",
            "to_number": "+15551235555",
        },
    )

    assert response.status_code == 202
    data = response.json()
    assert data["from_number"] == "+15551230000"
    assert data["to_number"] == "+15551235555"
    assert registry.adapters[-1].last_params["from_number"] == "+15551230000"


def test_incoming_call_webhook_creates_session(env) -> None:
    client, registry, session_manager = env

    response = client.post(
        "/api/v1/telephony/webhooks/twilio",
        json={
            "CallSid": "CA1234567890",
            "From": "+15551110000",
            "To": "+15552220000",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["telephony_provider"] == "twilio"
    assert data["session_id"]
    assert data["twiML"].startswith("<Response>")


def test_webhook_acknowledges_followup_event(env) -> None:
    client, registry, session_manager = env

    start_response = client.post(
        "/api/v1/telephony/webhooks/twilio",
        json={
            "CallSid": "CAfollowup",
            "From": "+15550001111",
            "To": "+15550002222",
        },
    )

    session_id = start_response.json()["session_id"]

    response = client.post(
        "/api/v1/telephony/webhooks/twilio",
        json={
            "CallSid": "CAfollowup",
            "EventType": "completed",
        },
    )

    assert response.status_code == 202
    assert telephony_state.get_session_for_call("CAfollowup") is None
    assert any(str(sid) == session_id for sid in session_manager.ended)
