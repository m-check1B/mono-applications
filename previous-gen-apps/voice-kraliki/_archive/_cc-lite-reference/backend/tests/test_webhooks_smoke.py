"""Smoke tests for webhooks routes"""
from fastapi.testclient import TestClient
from app.module import CommsModule
from app.core.database import get_db
from tests.utils import override_db


def test_webhook_call_status():
    """Test POST /api/webhooks/twilio/call-status endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.post("/api/webhooks/twilio/call-status", json={
        "CallSid": "CA123456",
        "CallStatus": "completed",
        "CallDuration": "120"
    })
    # 200 = success, 422 = validation error
    assert resp.status_code in (200, 422)


def test_webhook_recording():
    """Test POST /api/webhooks/twilio/recording endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.post("/api/webhooks/twilio/recording", json={
        "CallSid": "CA123456",
        "RecordingSid": "RE123456",
        "RecordingUrl": "https://api.twilio.com/recording.mp3"
    })
    # 200 = success, 422 = validation error
    assert resp.status_code in (200, 422)


def test_webhook_transcription():
    """Test POST /api/webhooks/twilio/transcription endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.post("/api/webhooks/twilio/transcription", json={
        "CallSid": "CA123456",
        "TranscriptionSid": "TR123456",
        "TranscriptionText": "Hello, this is a test call",
        "RecordingSid": "RE123456"
    })
    # 200 = success, 422 = validation error
    assert resp.status_code in (200, 422)


def test_webhook_ivr():
    """Test POST /api/webhooks/twilio/ivr endpoint exists"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.post("/api/webhooks/twilio/ivr", json={
        "CallSid": "CA123456",
        "Digits": "1"
    })
    # 200 = success, 422 = validation error
    assert resp.status_code in (200, 422)


def test_webhook_health():
    """Test GET /api/webhooks/health returns health status"""
    module = CommsModule(platform_mode=False)
    app = module.get_app()
    client = TestClient(app)

    resp = client.get("/api/webhooks/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
