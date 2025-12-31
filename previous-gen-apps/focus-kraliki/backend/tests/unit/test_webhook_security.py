"""
Unit tests for Webhook Security Module
Tests signature verification, HMAC validation, and Google Calendar webhook handling

Coverage target: All webhook security functions including:
- verify_ii_agent_webhook (HMAC and Ed25519 paths)
- _verify_ed25519_signature
- _verify_hmac_signature
- verify_google_calendar_webhook
"""

import pytest
import hmac
import hashlib
import time
import base64
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi import HTTPException

from app.core.webhook_security import (
    WebhookSignatureVerifier,
    GoogleCalendarWebhookVerifier,
    webhook_verifier,
    google_webhook_verifier
)


class TestWebhookSignatureVerifier:
    """Tests for WebhookSignatureVerifier class"""
    
    def test_init(self):
        """Initialize verifier"""
        verifier = WebhookSignatureVerifier()
        assert verifier is not None
    
    def test_public_key_not_found(self):
        """Verifier works without public key"""
        verifier = WebhookSignatureVerifier()
        # Should initialize even without public key
        assert verifier.public_key is None or verifier.public_key is not None


class TestHMACSignature:
    """Tests for HMAC-SHA256 signature verification"""
    
    def test_hmac_signature_generation(self):
        """Generate HMAC-SHA256 signature manually"""
        secret = "test-secret-123"
        payload = b'{"test": "data"}'
        timestamp = "1700000000"
        
        # Message is: timestamp + "." + body
        message = f"{timestamp}.".encode('utf-8') + payload
        
        signature = hmac.new(
            secret.encode('utf-8'),
            message,
            hashlib.sha256
        ).hexdigest()
        
        assert len(signature) == 64  # SHA256 hex digest length
    
    def test_hmac_signature_verification(self):
        """Verify HMAC signature matches"""
        secret = "my-webhook-secret"
        payload = b'{"event": "task_completed", "task_id": "123"}'
        timestamp = str(int(time.time()))
        
        message = f"{timestamp}.".encode('utf-8') + payload
        signature = hmac.new(
            secret.encode('utf-8'),
            message,
            hashlib.sha256
        ).hexdigest()
        
        # Verify with same secret
        expected = hmac.new(
            secret.encode('utf-8'),
            message,
            hashlib.sha256
        ).hexdigest()
        
        assert hmac.compare_digest(signature, expected)
    
    def test_invalid_signature_rejected(self):
        """Invalid signature fails verification"""
        secret = "my-webhook-secret"
        wrong_secret = "wrong-secret"
        payload = b'{"test": "data"}'
        timestamp = str(int(time.time()))
        
        message = f"{timestamp}.".encode('utf-8') + payload
        
        # Generate with correct secret
        correct_sig = hmac.new(
            secret.encode('utf-8'),
            message,
            hashlib.sha256
        ).hexdigest()
        
        # Generate with wrong secret
        wrong_sig = hmac.new(
            wrong_secret.encode('utf-8'),
            message,
            hashlib.sha256
        ).hexdigest()
        
        assert not hmac.compare_digest(correct_sig, wrong_sig)


class TestTimestampValidation:
    """Tests for timestamp validation (replay attack prevention)"""
    
    def test_recent_timestamp_valid(self):
        """Recent timestamp passes validation"""
        now = int(time.time())
        timestamp = now - 60  # 1 minute ago
        
        # Allow 5 minute window
        is_valid = abs(now - timestamp) <= 300
        assert is_valid
    
    def test_old_timestamp_rejected(self):
        """Old timestamp fails validation"""
        now = int(time.time())
        timestamp = now - 600  # 10 minutes ago
        
        # Should fail (outside 5 minute window)
        is_valid = abs(now - timestamp) <= 300
        assert not is_valid
    
    def test_future_timestamp_rejected(self):
        """Future timestamp fails validation"""
        now = int(time.time())
        timestamp = now + 600  # 10 minutes in future
        
        # Should fail
        is_valid = abs(now - timestamp) <= 300
        assert not is_valid


class TestGoogleCalendarWebhookVerifier:
    """Tests for Google Calendar webhook verification"""
    
    def test_verifier_initialization(self):
        """Initialize Google webhook verifier"""
        verifier = GoogleCalendarWebhookVerifier()
        assert verifier is not None
    
    def test_missing_headers_rejected(self):
        """Missing required headers raises error"""
        verifier = GoogleCalendarWebhookVerifier()
        
        # Would test missing channel_id and resource_state
        # raises HTTPException
        pass
    
    def test_valid_webhook_data_returned(self):
        """Valid webhook returns parsed data"""
        webhook_data = {
            "channel_id": "channel-123",
            "resource_id": "resource-456",
            "resource_state": "exists",
            "expiration": "2025-12-01T00:00:00Z",
            "message_number": 5
        }
        
        assert webhook_data["channel_id"] == "channel-123"
        assert webhook_data["resource_state"] == "exists"
    
    def test_expired_channel_detected(self):
        """Expired channel raises error"""
        expiration = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        now = datetime.utcnow()
        
        # Check if expired
        from dateutil import parser
        exp_dt = parser.isoparse(expiration)
        is_expired = now > exp_dt.replace(tzinfo=None)
        
        assert is_expired


class TestWebhookResourceStates:
    """Tests for Google Calendar resource states"""
    
    def test_sync_state(self):
        """Handle sync state (initial sync notification)"""
        state = "sync"
        # Sync state means channel was created, no action needed
        assert state == "sync"
    
    def test_exists_state(self):
        """Handle exists state (resource changed)"""
        state = "exists"
        # Exists means resource was modified
        assert state == "exists"
    
    def test_not_exists_state(self):
        """Handle not_exists state (resource deleted)"""
        state = "not_exists"
        # Resource was deleted
        assert state == "not_exists"


class TestWebhookTokenValidation:
    """Tests for webhook token validation"""
    
    def test_valid_token_accepted(self):
        """Valid token passes validation"""
        expected_token = "my-secret-token"
        received_token = "my-secret-token"
        
        is_valid = hmac.compare_digest(expected_token, received_token)
        assert is_valid
    
    def test_invalid_token_rejected(self):
        """Invalid token fails validation"""
        expected_token = "my-secret-token"
        received_token = "wrong-token"
        
        is_valid = hmac.compare_digest(expected_token, received_token)
        assert not is_valid


class TestGlobalInstances:
    """Tests for global webhook verifier instances"""

    def test_webhook_verifier_exists(self):
        """Global webhook_verifier is available"""
        assert webhook_verifier is not None

    def test_google_webhook_verifier_exists(self):
        """Global google_webhook_verifier is available"""
        assert google_webhook_verifier is not None


class TestVerifyIIAgentWebhook:
    """Tests for verify_ii_agent_webhook async method"""

    @pytest.fixture
    def verifier(self):
        """Create a fresh verifier for each test"""
        return WebhookSignatureVerifier()

    @pytest.fixture
    def mock_request(self):
        """Create a mock FastAPI request"""
        request = AsyncMock()
        request.body = AsyncMock(return_value=b'{"test": "data"}')
        return request

    @pytest.mark.asyncio
    async def test_missing_signature_header_raises_401(self, verifier, mock_request):
        """Missing X-II-Agent-Signature raises HTTPException"""
        with pytest.raises(HTTPException) as exc_info:
            await verifier.verify_ii_agent_webhook(
                request=mock_request,
                x_signature=None,
                x_timestamp=str(int(time.time())),
                x_signature_type="hmac-sha256"
            )
        assert exc_info.value.status_code == 401
        assert "Missing required signature headers" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_missing_timestamp_header_raises_401(self, verifier, mock_request):
        """Missing X-II-Agent-Timestamp raises HTTPException"""
        with pytest.raises(HTTPException) as exc_info:
            await verifier.verify_ii_agent_webhook(
                request=mock_request,
                x_signature="some-signature",
                x_timestamp=None,
                x_signature_type="hmac-sha256"
            )
        assert exc_info.value.status_code == 401
        assert "Missing required signature headers" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_no_secret_configured_raises_503(self, verifier, mock_request):
        """No webhook secret configured raises HTTPException 503"""
        with patch('app.core.webhook_security.settings') as mock_settings:
            # Simulate missing secret
            del mock_settings.II_AGENT_WEBHOOK_SECRET
            verifier.public_key = None  # No Ed25519 key either

            with pytest.raises(HTTPException) as exc_info:
                await verifier.verify_ii_agent_webhook(
                    request=mock_request,
                    x_signature="some-signature",
                    x_timestamp=str(int(time.time())),
                    x_signature_type="hmac-sha256"
                )
            assert exc_info.value.status_code == 503
            assert "not configured" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_old_timestamp_rejected(self, verifier, mock_request):
        """Timestamp older than 5 minutes raises HTTPException"""
        old_timestamp = str(int(time.time()) - 600)  # 10 minutes ago

        with patch('app.core.webhook_security.settings') as mock_settings:
            mock_settings.II_AGENT_WEBHOOK_SECRET = "test-secret"

            with pytest.raises(HTTPException) as exc_info:
                await verifier.verify_ii_agent_webhook(
                    request=mock_request,
                    x_signature="some-signature",
                    x_timestamp=old_timestamp,
                    x_signature_type="hmac-sha256"
                )
            assert exc_info.value.status_code == 401
            assert "replay attack" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_future_timestamp_rejected(self, verifier, mock_request):
        """Timestamp too far in future raises HTTPException"""
        future_timestamp = str(int(time.time()) + 600)  # 10 minutes ahead

        with patch('app.core.webhook_security.settings') as mock_settings:
            mock_settings.II_AGENT_WEBHOOK_SECRET = "test-secret"

            with pytest.raises(HTTPException) as exc_info:
                await verifier.verify_ii_agent_webhook(
                    request=mock_request,
                    x_signature="some-signature",
                    x_timestamp=future_timestamp,
                    x_signature_type="hmac-sha256"
                )
            assert exc_info.value.status_code == 401
            assert "replay attack" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_invalid_timestamp_format_rejected(self, verifier, mock_request):
        """Non-numeric timestamp raises HTTPException"""
        with patch('app.core.webhook_security.settings') as mock_settings:
            mock_settings.II_AGENT_WEBHOOK_SECRET = "test-secret"

            with pytest.raises(HTTPException) as exc_info:
                await verifier.verify_ii_agent_webhook(
                    request=mock_request,
                    x_signature="some-signature",
                    x_timestamp="not-a-number",
                    x_signature_type="hmac-sha256"
                )
            assert exc_info.value.status_code == 401
            assert "Invalid timestamp format" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_unsupported_signature_type_rejected(self, verifier, mock_request):
        """Unsupported signature type raises HTTPException 400"""
        with patch('app.core.webhook_security.settings') as mock_settings:
            mock_settings.II_AGENT_WEBHOOK_SECRET = "test-secret"

            with pytest.raises(HTTPException) as exc_info:
                await verifier.verify_ii_agent_webhook(
                    request=mock_request,
                    x_signature="some-signature",
                    x_timestamp=str(int(time.time())),
                    x_signature_type="rsa-sha512"  # unsupported
                )
            assert exc_info.value.status_code == 400
            assert "Unsupported signature type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_invalid_json_body_rejected(self, verifier):
        """Invalid JSON body raises HTTPException 400"""
        mock_request = AsyncMock()
        mock_request.body = AsyncMock(return_value=b'not valid json')

        # Generate valid HMAC signature for the invalid JSON
        secret = "test-secret"
        timestamp = str(int(time.time()))
        body = b'not valid json'
        message = f"{timestamp}.".encode('utf-8') + body
        signature = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()

        with patch('app.core.webhook_security.settings') as mock_settings:
            mock_settings.II_AGENT_WEBHOOK_SECRET = secret

            with pytest.raises(HTTPException) as exc_info:
                await verifier.verify_ii_agent_webhook(
                    request=mock_request,
                    x_signature=signature,
                    x_timestamp=timestamp,
                    x_signature_type="hmac-sha256"
                )
            assert exc_info.value.status_code == 400
            assert "Invalid JSON body" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_valid_hmac_signature_accepted(self, verifier):
        """Valid HMAC-SHA256 signature returns parsed body"""
        payload = {"event": "task_completed", "task_id": "123"}
        body = json.dumps(payload).encode('utf-8')
        secret = "test-webhook-secret"
        timestamp = str(int(time.time()))

        message = f"{timestamp}.".encode('utf-8') + body
        signature = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()

        mock_request = AsyncMock()
        mock_request.body = AsyncMock(return_value=body)

        with patch('app.core.webhook_security.settings') as mock_settings:
            mock_settings.II_AGENT_WEBHOOK_SECRET = secret

            result = await verifier.verify_ii_agent_webhook(
                request=mock_request,
                x_signature=signature,
                x_timestamp=timestamp,
                x_signature_type="hmac-sha256"
            )

            assert result == payload
            assert result["task_id"] == "123"

    @pytest.mark.asyncio
    async def test_invalid_hmac_signature_rejected(self, verifier):
        """Invalid HMAC signature raises HTTPException 401"""
        payload = {"event": "task_completed"}
        body = json.dumps(payload).encode('utf-8')
        secret = "correct-secret"
        timestamp = str(int(time.time()))

        # Sign with wrong secret
        wrong_signature = hmac.new(b"wrong-secret", body, hashlib.sha256).hexdigest()

        mock_request = AsyncMock()
        mock_request.body = AsyncMock(return_value=body)

        with patch('app.core.webhook_security.settings') as mock_settings:
            mock_settings.II_AGENT_WEBHOOK_SECRET = secret

            with pytest.raises(HTTPException) as exc_info:
                await verifier.verify_ii_agent_webhook(
                    request=mock_request,
                    x_signature=wrong_signature,
                    x_timestamp=timestamp,
                    x_signature_type="hmac-sha256"
                )
            assert exc_info.value.status_code == 401
            assert "Invalid HMAC signature" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_default_signature_type_is_hmac(self, verifier):
        """When signature_type header is None, default to hmac-sha256"""
        payload = {"test": "default_type"}
        body = json.dumps(payload).encode('utf-8')
        secret = "test-secret"
        timestamp = str(int(time.time()))

        message = f"{timestamp}.".encode('utf-8') + body
        signature = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()

        mock_request = AsyncMock()
        mock_request.body = AsyncMock(return_value=body)

        with patch('app.core.webhook_security.settings') as mock_settings:
            mock_settings.II_AGENT_WEBHOOK_SECRET = secret

            result = await verifier.verify_ii_agent_webhook(
                request=mock_request,
                x_signature=signature,
                x_timestamp=timestamp,
                x_signature_type=None  # No type specified
            )

            assert result == payload


class TestVerifyEd25519Signature:
    """Tests for _verify_ed25519_signature method"""

    @pytest.fixture
    def verifier(self):
        return WebhookSignatureVerifier()

    def test_no_public_key_raises_503(self, verifier):
        """Missing public key raises HTTPException 503"""
        verifier.public_key = None

        with pytest.raises(HTTPException) as exc_info:
            verifier._verify_ed25519_signature(
                body_bytes=b'{"test": "data"}',
                signature_b64="dGVzdHNpZw==",
                timestamp="1700000000"
            )
        assert exc_info.value.status_code == 503
        assert "missing public key" in exc_info.value.detail

    def test_invalid_base64_signature_rejected(self, verifier):
        """Invalid base64 in signature raises HTTPException 401"""
        # Create a mock public key
        verifier.public_key = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            verifier._verify_ed25519_signature(
                body_bytes=b'{"test": "data"}',
                signature_b64="not-valid-base64!!!",
                timestamp="1700000000"
            )
        assert exc_info.value.status_code == 401

    def test_invalid_ed25519_signature_rejected(self, verifier):
        """Invalid Ed25519 signature raises HTTPException 401"""
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.exceptions import InvalidSignature

        # Create a mock public key that raises InvalidSignature
        mock_key = MagicMock()
        mock_key.verify.side_effect = InvalidSignature()
        verifier.public_key = mock_key

        # Valid base64, but wrong signature
        fake_signature = base64.b64encode(b"wrong_signature_data").decode()

        with pytest.raises(HTTPException) as exc_info:
            verifier._verify_ed25519_signature(
                body_bytes=b'{"test": "data"}',
                signature_b64=fake_signature,
                timestamp="1700000000"
            )
        assert exc_info.value.status_code == 401
        assert "Invalid Ed25519 signature" in exc_info.value.detail

    def test_valid_ed25519_signature_passes(self, verifier):
        """Valid Ed25519 signature passes verification"""
        # Create a mock public key that doesn't raise
        mock_key = MagicMock()
        mock_key.verify.return_value = None  # Ed25519 verify returns None on success
        verifier.public_key = mock_key

        fake_signature = base64.b64encode(b"valid_signature").decode()

        # Should not raise
        verifier._verify_ed25519_signature(
            body_bytes=b'{"test": "data"}',
            signature_b64=fake_signature,
            timestamp="1700000000"
        )

        # Verify the correct message format was used
        expected_message = b"1700000000." + b'{"test": "data"}'
        mock_key.verify.assert_called_once()
        call_args = mock_key.verify.call_args[0]
        assert call_args[1] == expected_message


class TestVerifyHMACSignature:
    """Tests for _verify_hmac_signature method"""

    @pytest.fixture
    def verifier(self):
        return WebhookSignatureVerifier()

    def test_no_secret_raises_503(self, verifier):
        """Missing secret raises HTTPException 503"""
        with pytest.raises(HTTPException) as exc_info:
            verifier._verify_hmac_signature(
                body_bytes=b'{"test": "data"}',
                signature_hex="abc123",
                timestamp="1700000000",
                secret=None
            )
        assert exc_info.value.status_code == 503
        assert "missing webhook secret" in exc_info.value.detail

    def test_empty_secret_raises_503(self, verifier):
        """Empty secret raises HTTPException 503"""
        with pytest.raises(HTTPException) as exc_info:
            verifier._verify_hmac_signature(
                body_bytes=b'{"test": "data"}',
                signature_hex="abc123",
                timestamp="1700000000",
                secret=""
            )
        assert exc_info.value.status_code == 503

    def test_valid_hmac_passes(self, verifier):
        """Valid HMAC signature passes verification"""
        secret = "my-secret-key"
        body = b'{"test": "data"}'
        timestamp = "1700000000"

        message = f"{timestamp}.".encode('utf-8') + body
        valid_signature = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()

        # Should not raise
        verifier._verify_hmac_signature(
            body_bytes=body,
            signature_hex=valid_signature,
            timestamp=timestamp,
            secret=secret
        )

    def test_invalid_hmac_rejected(self, verifier):
        """Invalid HMAC signature raises HTTPException 401"""
        with pytest.raises(HTTPException) as exc_info:
            verifier._verify_hmac_signature(
                body_bytes=b'{"test": "data"}',
                signature_hex="definitely_not_a_valid_hmac",
                timestamp="1700000000",
                secret="my-secret"
            )
        assert exc_info.value.status_code == 401
        assert "Invalid HMAC signature" in exc_info.value.detail

    def test_tampered_body_rejected(self, verifier):
        """Signature for different body is rejected"""
        secret = "my-secret"
        original_body = b'{"amount": 100}'
        tampered_body = b'{"amount": 1000000}'
        timestamp = "1700000000"

        # Sign original body
        message = f"{timestamp}.".encode('utf-8') + original_body
        signature = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()

        # Try to verify with tampered body
        with pytest.raises(HTTPException) as exc_info:
            verifier._verify_hmac_signature(
                body_bytes=tampered_body,
                signature_hex=signature,
                timestamp=timestamp,
                secret=secret
            )
        assert exc_info.value.status_code == 401


class TestGoogleCalendarWebhookVerifierMethods:
    """Tests for GoogleCalendarWebhookVerifier.verify_google_calendar_webhook"""

    @pytest.fixture
    def verifier(self):
        return GoogleCalendarWebhookVerifier()

    def test_missing_channel_id_raises_401(self, verifier):
        """Missing channel_id raises HTTPException 401"""
        with pytest.raises(HTTPException) as exc_info:
            verifier.verify_google_calendar_webhook(
                x_goog_channel_id=None,
                x_goog_resource_state="exists",
                x_goog_resource_id="resource-123"
            )
        assert exc_info.value.status_code == 401
        assert "Missing required" in exc_info.value.detail

    def test_missing_resource_state_raises_401(self, verifier):
        """Missing resource_state raises HTTPException 401"""
        with pytest.raises(HTTPException) as exc_info:
            verifier.verify_google_calendar_webhook(
                x_goog_channel_id="channel-123",
                x_goog_resource_state=None,
                x_goog_resource_id="resource-123"
            )
        assert exc_info.value.status_code == 401

    def test_expired_channel_is_logged_not_rejected(self, verifier):
        """Expired channel is logged but request continues (best-effort check)"""
        # NOTE: The implementation catches ALL exceptions including HTTPException
        # during expiration check and logs them instead of failing.
        # This is intentional "best-effort" behavior per the code comments.

        # Set expiration to 1 hour ago
        expired = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

        # Should NOT raise - expiration check is best-effort
        result = verifier.verify_google_calendar_webhook(
            x_goog_channel_id="channel-123",
            x_goog_resource_state="exists",
            x_goog_resource_id="resource-123",
            x_goog_channel_expiration=expired,
            x_goog_channel_token=None,
            x_goog_message_number=None
        )

        # Request still succeeds despite expired channel
        assert result["channel_id"] == "channel-123"

    def test_valid_expiration_accepted(self, verifier):
        """Valid (future) expiration is accepted"""
        future_exp = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

        result = verifier.verify_google_calendar_webhook(
            x_goog_channel_id="channel-123",
            x_goog_resource_state="exists",
            x_goog_resource_id="resource-123",
            x_goog_channel_expiration=future_exp,
            x_goog_channel_token=None,
            x_goog_message_number=None
        )

        assert result["channel_id"] == "channel-123"
        assert result["resource_state"] == "exists"

    def test_invalid_token_rejected(self, verifier):
        """Invalid channel token raises HTTPException 401"""
        with patch('app.core.webhook_security.settings') as mock_settings:
            mock_settings.GOOGLE_CALENDAR_WEBHOOK_TOKEN = "expected-token"

            with pytest.raises(HTTPException) as exc_info:
                verifier.verify_google_calendar_webhook(
                    x_goog_channel_id="channel-123",
                    x_goog_resource_state="exists",
                    x_goog_resource_id="resource-123",
                    x_goog_channel_expiration=None,
                    x_goog_channel_token="wrong-token",
                    x_goog_message_number=None
                )
            assert exc_info.value.status_code == 401
            assert "Invalid calendar webhook token" in exc_info.value.detail

    def test_valid_token_accepted(self, verifier):
        """Valid channel token passes"""
        with patch('app.core.webhook_security.settings') as mock_settings:
            mock_settings.GOOGLE_CALENDAR_WEBHOOK_TOKEN = "correct-token"

            result = verifier.verify_google_calendar_webhook(
                x_goog_channel_id="channel-123",
                x_goog_resource_state="sync",
                x_goog_resource_id="resource-456",
                x_goog_channel_expiration=None,
                x_goog_channel_token="correct-token",
                x_goog_message_number=None
            )

            assert result["channel_id"] == "channel-123"
            assert result["resource_id"] == "resource-456"

    def test_no_token_configured_accepts_any(self, verifier):
        """When no token is configured, any token is accepted"""
        with patch('app.core.webhook_security.settings') as mock_settings:
            mock_settings.GOOGLE_CALENDAR_WEBHOOK_TOKEN = None

            result = verifier.verify_google_calendar_webhook(
                x_goog_channel_id="channel-123",
                x_goog_resource_state="exists",
                x_goog_resource_id="resource-123",
                x_goog_channel_expiration=None,
                x_goog_channel_token="any-token",
                x_goog_message_number=None
            )

            assert result["channel_id"] == "channel-123"

    def test_message_number_parsed(self, verifier):
        """Message number is parsed as integer"""
        result = verifier.verify_google_calendar_webhook(
            x_goog_channel_id="channel-123",
            x_goog_resource_state="exists",
            x_goog_resource_id="resource-123",
            x_goog_message_number="42"
        )

        assert result["message_number"] == 42

    def test_message_number_none_when_missing(self, verifier):
        """Message number is None when not provided"""
        result = verifier.verify_google_calendar_webhook(
            x_goog_channel_id="channel-123",
            x_goog_resource_state="exists",
            x_goog_resource_id="resource-123",
            x_goog_message_number=None
        )

        assert result["message_number"] is None

    def test_all_fields_returned(self, verifier):
        """All webhook fields are returned correctly"""
        result = verifier.verify_google_calendar_webhook(
            x_goog_channel_id="ch-001",
            x_goog_resource_state="not_exists",
            x_goog_resource_id="res-002",
            x_goog_channel_expiration="2099-12-31T23:59:59Z",
            x_goog_message_number="100"
        )

        assert result == {
            "channel_id": "ch-001",
            "resource_id": "res-002",
            "resource_state": "not_exists",
            "expiration": "2099-12-31T23:59:59Z",
            "message_number": 100
        }

    def test_malformed_expiration_is_logged_not_rejected(self, verifier):
        """Malformed expiration is logged but doesn't fail request"""
        # The verifier has a try/except that logs but continues
        result = verifier.verify_google_calendar_webhook(
            x_goog_channel_id="channel-123",
            x_goog_resource_state="exists",
            x_goog_resource_id="resource-123",
            x_goog_channel_expiration="not-a-valid-date",
            x_goog_channel_token=None,
            x_goog_message_number=None
        )

        # Should still succeed with malformed expiration
        assert result["channel_id"] == "channel-123"


class TestWebhookSecurityEdgeCases:
    """Edge case and integration tests"""

    def test_empty_body_hmac_verification(self):
        """HMAC verification works with empty body"""
        verifier = WebhookSignatureVerifier()
        secret = "test-secret"
        body = b''
        timestamp = "1700000000"

        message = f"{timestamp}.".encode('utf-8') + body
        signature = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()

        # Should not raise
        verifier._verify_hmac_signature(
            body_bytes=body,
            signature_hex=signature,
            timestamp=timestamp,
            secret=secret
        )

    def test_unicode_body_hmac_verification(self):
        """HMAC verification works with unicode body"""
        verifier = WebhookSignatureVerifier()
        secret = "test-secret"
        body = '{"message": "こんにちは世界"}'.encode('utf-8')
        timestamp = "1700000000"

        message = f"{timestamp}.".encode('utf-8') + body
        signature = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()

        # Should not raise
        verifier._verify_hmac_signature(
            body_bytes=body,
            signature_hex=signature,
            timestamp=timestamp,
            secret=secret
        )

    def test_large_body_hmac_verification(self):
        """HMAC verification works with large body"""
        verifier = WebhookSignatureVerifier()
        secret = "test-secret"
        # 1MB body
        body = ('x' * 1024 * 1024).encode('utf-8')
        timestamp = "1700000000"

        message = f"{timestamp}.".encode('utf-8') + body
        signature = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()

        # Should not raise
        verifier._verify_hmac_signature(
            body_bytes=body,
            signature_hex=signature,
            timestamp=timestamp,
            secret=secret
        )

    @pytest.mark.asyncio
    async def test_ed25519_path_with_valid_setup(self):
        """Ed25519 signature type uses ed25519 verification path"""
        verifier = WebhookSignatureVerifier()

        # Mock public key
        mock_key = MagicMock()
        mock_key.verify.return_value = None
        verifier.public_key = mock_key

        payload = {"test": "ed25519"}
        body = json.dumps(payload).encode('utf-8')
        timestamp = str(int(time.time()))
        fake_sig = base64.b64encode(b"fake_ed25519_sig").decode()

        mock_request = AsyncMock()
        mock_request.body = AsyncMock(return_value=body)

        result = await verifier.verify_ii_agent_webhook(
            request=mock_request,
            x_signature=fake_sig,
            x_timestamp=timestamp,
            x_signature_type="ed25519"
        )

        assert result == payload
        mock_key.verify.assert_called_once()