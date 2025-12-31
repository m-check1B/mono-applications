"""
VD-398: Telnyx Webhook Signature Validation Tests

Tests Ed25519 signature validation for Telnyx webhooks.
SECURITY: All Telnyx webhooks must be cryptographically validated.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.services.voice_streaming import voice_streaming_service

client = TestClient(app)


@pytest.mark.asyncio
async def test_telnyx_webhook_signature_validation_called():
    """Test that Telnyx-Signature-Ed25519 and Telnyx-Timestamp headers are passed to validation."""
    payload = {"data": {"event_type": "call.initiated", "payload": {"call_control_id": "test-call-id"}}}
    signature = "test-signature"
    timestamp = "1735161600"  # A valid Unix timestamp

    with patch("app.routers.telephony.voice_streaming_service.validate_webhook", new_callable=AsyncMock) as mock_validate:
        mock_validate.return_value = True

        response = client.post(
            "/api/speak/telephony/webhook",
            json=payload,
            headers={
                "Telnyx-Signature-Ed25519": signature,
                "Telnyx-Timestamp": timestamp
            }
        )

        assert response.status_code == 200
        # Check if validate_webhook was called with signature, body, and timestamp
        mock_validate.assert_called_once()
        args, kwargs = mock_validate.call_args
        assert args[0] == signature
        # args[1] should be the raw bytes of the payload
        assert args[2] == timestamp  # Now includes timestamp for replay attack prevention


@pytest.mark.asyncio
async def test_telnyx_webhook_invalid_signature():
    """Test that invalid signature returns 401."""
    payload = {"data": {"event_type": "call.initiated", "payload": {"call_control_id": "test-call-id"}}}

    with patch("app.routers.telephony.voice_streaming_service.validate_webhook", new_callable=AsyncMock) as mock_validate:
        mock_validate.return_value = False

        response = client.post(
            "/api/speak/telephony/webhook",
            json=payload,
            headers={"Telnyx-Signature-Ed25519": "wrong-signature"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid webhook signature"


@pytest.mark.asyncio
async def test_telnyx_webhook_missing_signature_rejected():
    """Test that missing signature is rejected (fails secure)."""
    payload = {"data": {"event_type": "call.initiated", "payload": {"call_control_id": "test-call-id"}}}

    # Don't mock - let the real validation run (it should fail without signature)
    response = client.post(
        "/api/speak/telephony/webhook",
        json=payload,
        headers={}  # No signature header
    )

    # Should be rejected with 401
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid webhook signature"


@pytest.mark.asyncio
async def test_telnyx_webhook_no_public_key_rejected():
    """Test that webhook is rejected when TELNYX_PUBLIC_KEY is not configured."""
    payload = {"data": {"event_type": "call.initiated", "payload": {"call_control_id": "test-call-id"}}}

    # Mock settings to return no public key
    with patch("app.services.voice_streaming.settings") as mock_settings:
        mock_settings.telnyx_public_key = ""

        response = client.post(
            "/api/speak/telephony/webhook",
            json=payload,
            headers={"Telnyx-Signature-Ed25519": "some-signature"}
        )

        # Should be rejected - fail secure
        assert response.status_code == 401
