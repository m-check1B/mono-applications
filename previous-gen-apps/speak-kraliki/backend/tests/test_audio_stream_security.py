"""
VD-398: Audio Stream Security Tests

Tests Ed25519 signature validation for Telnyx audio stream endpoint.
SECURITY: All audio data must be cryptographically validated to prevent injection.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_audio_stream_signature_validation_called():
    """Test that /audio-stream validates Telnyx-Signature-Ed25519 and Telnyx-Timestamp headers."""
    audio_data = b"fake-audio-data"
    call_id = "test-call-id"
    signature = "test-signature"
    timestamp = "1735161600"

    with patch("app.routers.telephony.voice_streaming_service.validate_webhook", new_callable=AsyncMock) as mock_validate:
        mock_validate.return_value = True

        # We also need to mock handle_incoming_audio to avoid errors
        with patch("app.routers.telephony.voice_streaming_service.handle_incoming_audio", new_callable=AsyncMock) as mock_handle:
            response = client.post(
                "/api/speak/telephony/audio-stream",
                content=audio_data,
                headers={
                    "Telnyx-Signature-Ed25519": signature,
                    "Telnyx-Timestamp": timestamp,
                    "X-Call-Control-Id": call_id
                }
            )

            assert response.status_code == 200
            # Now validate_webhook takes 3 args: signature, body, timestamp
            mock_validate.assert_called_once_with(signature, audio_data, timestamp)
            mock_handle.assert_called_once_with(call_id, audio_data)


@pytest.mark.asyncio
async def test_audio_stream_invalid_signature():
    """Test that /audio-stream rejects invalid signatures."""
    audio_data = b"fake-audio-data"

    with patch("app.routers.telephony.voice_streaming_service.validate_webhook", new_callable=AsyncMock) as mock_validate:
        mock_validate.return_value = False

        response = client.post(
            "/api/speak/telephony/audio-stream",
            content=audio_data,
            headers={
                "Telnyx-Signature-Ed25519": "wrong-signature",
                "X-Call-Control-Id": "test-call-id"
            }
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid webhook signature"


@pytest.mark.asyncio
async def test_audio_stream_missing_signature_rejected():
    """Test that /audio-stream rejects requests without signature (fails secure)."""
    audio_data = b"fake-audio-data"

    # Don't mock - let the real validation run (it should fail without signature)
    response = client.post(
        "/api/speak/telephony/audio-stream",
        content=audio_data,
        headers={
            "X-Call-Control-Id": "test-call-id"
            # No Telnyx-Signature-Ed25519 header
        }
    )

    # Should be rejected with 401
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid webhook signature"


@pytest.mark.asyncio
async def test_audio_stream_no_public_key_rejected():
    """Test that audio stream is rejected when TELNYX_PUBLIC_KEY is not configured."""
    audio_data = b"fake-audio-data"

    # Mock settings to return no public key
    with patch("app.services.voice_streaming.settings") as mock_settings:
        mock_settings.telnyx_public_key = ""

        response = client.post(
            "/api/speak/telephony/audio-stream",
            content=audio_data,
            headers={
                "Telnyx-Signature-Ed25519": "some-signature",
                "X-Call-Control-Id": "test-call-id"
            }
        )

        # Should be rejected - fail secure
        assert response.status_code == 401
