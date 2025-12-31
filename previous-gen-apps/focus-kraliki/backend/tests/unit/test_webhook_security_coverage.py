"""
Targeted tests to improve coverage for Webhook Security Module
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException, status
import json
import hmac
import hashlib
from datetime import datetime

from app.core.webhook_security import WebhookSignatureVerifier, GoogleCalendarWebhookVerifier

@pytest.fixture
def verifier():
    return WebhookSignatureVerifier()

@pytest.fixture
def google_verifier():
    return GoogleCalendarWebhookVerifier()

@pytest.mark.asyncio
async def test_verify_ii_agent_webhook_hmac_success(verifier):
    """Test HMAC signature verification success"""
    body = {"test": "data"}
    body_bytes = json.dumps(body).encode('utf-8')
    timestamp = str(int(datetime.utcnow().timestamp()))
    secret = "test-secret"
    
    # Compute HMAC
    message = f"{timestamp}.".encode('utf-8') + body_bytes
    signature = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()
    
    # Mock Request
    mock_request = MagicMock()
    mock_request.body = AsyncMock(return_value=body_bytes)
    
    with patch("app.core.webhook_security.settings") as mock_settings:
        mock_settings.II_AGENT_WEBHOOK_SECRET = secret
        
        result = await verifier.verify_ii_agent_webhook(
            mock_request,
            x_signature=signature,
            x_timestamp=timestamp,
            x_signature_type="hmac-sha256"
        )
        
        assert result == body

@pytest.mark.asyncio
async def test_verify_ii_agent_webhook_missing_headers(verifier):
    """Test missing headers raises 401"""
    mock_request = MagicMock()
    with pytest.raises(HTTPException) as exc:
        await verifier.verify_ii_agent_webhook(mock_request, x_signature=None, x_timestamp=None)
    assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_verify_ii_agent_webhook_old_timestamp(verifier):
    """Test old timestamp raises 401"""
    timestamp = str(int(datetime.utcnow().timestamp()) - 600) # 10 mins old
    mock_request = MagicMock()
    with patch("app.core.webhook_security.settings"):
        with pytest.raises(HTTPException) as exc:
            await verifier.verify_ii_agent_webhook(mock_request, x_signature="sig", x_timestamp=timestamp)
        assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_verify_ii_agent_webhook_invalid_json(verifier):
    """Test invalid JSON body raises 400"""
    body_bytes = b"not json"
    timestamp = str(int(datetime.utcnow().timestamp()))
    secret = "secret"
    
    # Compute HMAC for "not json"
    message = f"{timestamp}.".encode('utf-8') + body_bytes
    signature = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()
    
    mock_request = MagicMock()
    mock_request.body = AsyncMock(return_value=body_bytes)
    
    with patch("app.core.webhook_security.settings") as mock_settings:
        mock_settings.II_AGENT_WEBHOOK_SECRET = secret
        with pytest.raises(HTTPException) as exc:
            await verifier.verify_ii_agent_webhook(mock_request, x_signature=signature, x_timestamp=timestamp)
        assert exc.value.status_code == 400

def test_verify_google_calendar_webhook_success(google_verifier):
    """Test Google Calendar webhook verification success"""
    result = google_verifier.verify_google_calendar_webhook(
        x_goog_channel_id="chan1",
        x_goog_resource_state="exists",
        x_goog_resource_id="res1",
        x_goog_message_number="5"
    )
    
    assert result["channel_id"] == "chan1"
    assert result["message_number"] == 5

def test_verify_google_calendar_webhook_missing_headers(google_verifier):
    """Test missing Google headers raises 401"""
    with pytest.raises(HTTPException) as exc:
        google_verifier.verify_google_calendar_webhook(x_goog_channel_id=None)
    assert exc.value.status_code == 401

def test_verify_google_calendar_webhook_invalid_token(google_verifier):
    """Test invalid token raises 401"""
    with patch("app.core.webhook_security.settings") as mock_settings:
        mock_settings.GOOGLE_CALENDAR_WEBHOOK_TOKEN = "expected"
        with pytest.raises(HTTPException) as exc:
            google_verifier.verify_google_calendar_webhook(
                x_goog_channel_id="c", 
                x_goog_resource_state="s",
                x_goog_channel_token="wrong"
            )
        assert exc.value.status_code == 401
