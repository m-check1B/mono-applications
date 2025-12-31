"""
Test Ed25519 JWT Authentication
Tests asymmetric cryptography (EdDSA) token creation and verification
"""

import pytest
import jwt
from datetime import datetime, timedelta
from pathlib import Path

from app.core.ed25519_auth import Ed25519Auth, ed25519_auth


class TestEd25519Auth:
    """Test Ed25519 JWT authentication system."""

    def test_keys_loaded(self):
        """Test that Ed25519 keys are loaded successfully."""
        auth = Ed25519Auth(keys_dir="keys")
        assert auth.private_key is not None
        assert auth.public_key is not None

    def test_create_access_token(self):
        """Test access token creation with Ed25519."""
        auth = Ed25519Auth(keys_dir="keys")

        data = {
            "sub": "user-123",
            "email": "test@example.com",
            "role": "user"
        }

        token = auth.create_access_token(data)

        # Verify token is a string
        assert isinstance(token, str)

        # Verify token has 3 parts (header.payload.signature)
        parts = token.split(".")
        assert len(parts) == 3

    def test_create_refresh_token(self):
        """Test refresh token creation with Ed25519."""
        auth = Ed25519Auth(keys_dir="keys")

        data = {
            "sub": "user-123",
            "email": "test@example.com"
        }

        token = auth.create_refresh_token(data)

        # Verify token is a string
        assert isinstance(token, str)

        # Verify token has 3 parts
        parts = token.split(".")
        assert len(parts) == 3

    def test_verify_access_token(self):
        """Test access token verification with Ed25519."""
        auth = Ed25519Auth(keys_dir="keys")

        data = {
            "sub": "user-456",
            "email": "verify@example.com"
        }

        token = auth.create_access_token(data)
        payload = auth.verify_token(token, expected_type="access")

        # Verify payload contains expected data
        assert payload["sub"] == "user-456"
        assert payload["email"] == "verify@example.com"
        assert payload["type"] == "access"
        assert payload["alg"] == "EdDSA"
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_refresh_token(self):
        """Test refresh token verification with Ed25519."""
        auth = Ed25519Auth(keys_dir="keys")

        data = {
            "sub": "user-789",
            "email": "refresh@example.com"
        }

        token = auth.create_refresh_token(data)
        payload = auth.verify_token(token, expected_type="refresh")

        # Verify payload
        assert payload["sub"] == "user-789"
        assert payload["type"] == "refresh"
        assert payload["alg"] == "EdDSA"

    def test_token_algorithm_is_eddsa(self):
        """Test that tokens use EdDSA algorithm (not HS256)."""
        auth = Ed25519Auth(keys_dir="keys")

        token = auth.create_access_token({"sub": "test"})

        # Decode header without verification
        header = jwt.get_unverified_header(token)

        # Verify algorithm is EdDSA (Ed25519)
        assert header["alg"] == "EdDSA"

    def test_token_type_validation(self):
        """Test that token type validation works."""
        auth = Ed25519Auth(keys_dir="keys")

        # Create access token
        access_token = auth.create_access_token({"sub": "test"})

        # Try to verify as refresh token (should fail)
        with pytest.raises(Exception) as exc_info:
            auth.verify_token(access_token, expected_type="refresh")

        assert "Invalid token type" in str(exc_info.value)

    def test_expired_token_rejected(self):
        """Test that expired tokens are rejected."""
        auth = Ed25519Auth(keys_dir="keys")

        # Create token that expires immediately
        data = {"sub": "test-expired"}
        token = auth.create_access_token(
            data,
            expires_delta=timedelta(seconds=-1)  # Already expired
        )

        # Verify token is rejected
        with pytest.raises(Exception) as exc_info:
            auth.verify_token(token)

        assert "expired" in str(exc_info.value).lower()

    def test_invalid_signature_rejected(self):
        """Test that tokens with invalid signatures are rejected."""
        auth = Ed25519Auth(keys_dir="keys")

        # Create valid token
        token = auth.create_access_token({"sub": "test"})

        # Tamper with token aggressively - replace multiple signature bytes
        # The signature is the last part after the final '.'
        parts = token.rsplit(".", 1)
        original_sig = parts[1]
        # Flip several characters to ensure signature is truly invalid
        tampered_sig = "X" * 10 + original_sig[10:]
        tampered_token = parts[0] + "." + tampered_sig

        # Verify tampered token is rejected
        with pytest.raises(Exception) as exc_info:
            auth.verify_token(tampered_token)

        assert "Invalid token" in str(exc_info.value) or "verification failed" in str(exc_info.value).lower()

    def test_decode_without_verification(self):
        """Test decoding token without signature verification."""
        auth = Ed25519Auth(keys_dir="keys")

        data = {
            "sub": "user-999",
            "email": "decode@example.com"
        }

        token = auth.create_access_token(data)
        payload = auth.decode_without_verification(token)

        # Verify payload is decoded
        assert payload["sub"] == "user-999"
        assert payload["email"] == "decode@example.com"

    def test_access_token_expiration_time(self):
        """Test that access tokens have correct expiration (15 minutes)."""
        auth = Ed25519Auth(keys_dir="keys")

        before = datetime.utcnow()
        token = auth.create_access_token({"sub": "test"})
        after = datetime.utcnow()

        payload = auth.verify_token(token)
        exp = datetime.fromtimestamp(payload["exp"])

        # Token should expire ~15 minutes from now
        expected_exp = before + timedelta(minutes=15)

        # Allow 5 second variance for test execution time
        assert abs((exp - expected_exp).total_seconds()) < 5

    def test_refresh_token_expiration_time(self):
        """Test that refresh tokens have correct expiration (7 days)."""
        auth = Ed25519Auth(keys_dir="keys")

        before = datetime.utcnow()
        token = auth.create_refresh_token({"sub": "test"})
        after = datetime.utcnow()

        payload = auth.verify_token(token, expected_type="refresh")
        exp = datetime.fromtimestamp(payload["exp"])

        # Token should expire ~7 days from now
        expected_exp = before + timedelta(days=7)

        # Allow 5 second variance
        assert abs((exp - expected_exp).total_seconds()) < 5

    def test_global_instance(self):
        """Test that global ed25519_auth instance works."""
        # This should not raise an error
        token = ed25519_auth.create_access_token({"sub": "global-test"})
        payload = ed25519_auth.verify_token(token)

        assert payload["sub"] == "global-test"

    def test_custom_expiration_delta(self):
        """Test creating tokens with custom expiration."""
        auth = Ed25519Auth(keys_dir="keys")

        # Create token with 1 hour expiration
        custom_delta = timedelta(hours=1)
        token = auth.create_access_token(
            {"sub": "custom"},
            expires_delta=custom_delta
        )

        payload = auth.verify_token(token)
        exp = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + custom_delta

        # Allow 5 second variance
        assert abs((exp - expected_exp).total_seconds()) < 5


class TestEd25519SecurityProperties:
    """Test security properties of Ed25519 implementation."""

    def test_different_tokens_for_same_data(self):
        """Test that creating tokens with same data produces different signatures."""
        auth = Ed25519Auth(keys_dir="keys")

        data = {"sub": "test-user"}

        # Create two tokens with same data
        token1 = auth.create_access_token(data)
        token2 = auth.create_access_token(data)

        # Tokens should be different (due to different 'iat' timestamps)
        assert token1 != token2

    def test_public_key_cannot_sign(self):
        """Test that public key alone cannot create valid tokens."""
        auth = Ed25519Auth(keys_dir="keys")

        # Try to create token with just public key (should fail)
        # This test verifies asymmetric nature of Ed25519
        with pytest.raises(AttributeError):
            jwt.encode(
                {"sub": "test"},
                auth.public_key,  # Wrong key type
                algorithm="EdDSA"
            )

    def test_tampering_detection(self):
        """Test that any tampering with token is detected."""
        auth = Ed25519Auth(keys_dir="keys")

        token = auth.create_access_token({"sub": "test", "role": "user"})

        # Try to tamper with payload by changing 'user' to 'admin'
        parts = token.split(".")

        # Decode payload
        import base64
        import json

        # Add padding if needed
        payload_b64 = parts[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding

        payload_json = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_json)

        # Tamper with payload
        payload["role"] = "admin"

        # Re-encode
        tampered_payload = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).decode().rstrip("=")

        # Create tampered token
        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

        # Verify tampered token is rejected
        with pytest.raises(Exception):
            auth.verify_token(tampered_token)
