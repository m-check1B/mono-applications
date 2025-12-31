"""Tests for Ed25519 JWT authentication."""

import pytest
from datetime import timedelta

from auth_core import (
    Ed25519Auth,
    TokenConfig,
    TokenType,
    TokenExpiredError,
    TokenInvalidError,
    TokenTypeMismatchError,
    generate_ed25519_keypair,
)


@pytest.fixture
def keypair():
    """Generate a fresh key pair for testing."""
    return generate_ed25519_keypair()


@pytest.fixture
def auth(keypair):
    """Create an Ed25519Auth instance with test keys."""
    private_key, public_key = keypair
    return Ed25519Auth(
        private_key=private_key,
        public_key=public_key,
        config=TokenConfig(
            access_token_expire_minutes=15,
            refresh_token_expire_days=7,
        ),
    )


class TestTokenCreation:
    """Test token creation."""

    def test_create_access_token(self, auth):
        """Should create a valid access token."""
        token = auth.create_access_token({"sub": "user123"})
        assert token
        assert isinstance(token, str)
        assert len(token) > 50

    def test_create_refresh_token(self, auth):
        """Should create a valid refresh token."""
        token = auth.create_refresh_token({"sub": "user123"})
        assert token
        assert isinstance(token, str)

    def test_tokens_are_different(self, auth):
        """Access and refresh tokens should be different."""
        access = auth.create_access_token({"sub": "user123"})
        refresh = auth.create_refresh_token({"sub": "user123"})
        assert access != refresh

    def test_custom_expiration(self, auth):
        """Should accept custom expiration delta."""
        token = auth.create_access_token(
            {"sub": "user123"},
            expires_delta=timedelta(hours=1),
        )
        payload = auth.verify_token(token)
        assert payload.sub == "user123"


class TestTokenVerification:
    """Test token verification."""

    def test_verify_valid_access_token(self, auth):
        """Should verify a valid access token."""
        token = auth.create_access_token({"sub": "user123"})
        payload = auth.verify_token(token, TokenType.ACCESS)

        assert payload.sub == "user123"
        assert payload.type == TokenType.ACCESS
        assert payload.jti

    def test_verify_valid_refresh_token(self, auth):
        """Should verify a valid refresh token."""
        token = auth.create_refresh_token({"sub": "user123"})
        payload = auth.verify_token(token, TokenType.REFRESH)

        assert payload.sub == "user123"
        assert payload.type == TokenType.REFRESH

    def test_type_mismatch_access_as_refresh(self, auth):
        """Should reject access token when refresh expected."""
        token = auth.create_access_token({"sub": "user123"})

        with pytest.raises(TokenTypeMismatchError) as exc:
            auth.verify_token(token, TokenType.REFRESH)

        assert exc.value.expected == "refresh"
        assert exc.value.got == "access"

    def test_type_mismatch_refresh_as_access(self, auth):
        """Should reject refresh token when access expected."""
        token = auth.create_refresh_token({"sub": "user123"})

        with pytest.raises(TokenTypeMismatchError):
            auth.verify_token(token, TokenType.ACCESS)

    def test_invalid_token_format(self, auth):
        """Should reject malformed tokens."""
        with pytest.raises(TokenInvalidError):
            auth.verify_token("not-a-valid-token")

    def test_invalid_signature(self, auth):
        """Should reject tokens with invalid signature."""
        # Create token with different keys
        other_private, other_public = generate_ed25519_keypair()
        other_auth = Ed25519Auth(
            private_key=other_private,
            public_key=other_public,
        )
        token = other_auth.create_access_token({"sub": "user123"})

        with pytest.raises(TokenInvalidError):
            auth.verify_token(token)

    def test_expired_token(self, auth):
        """Should reject expired tokens."""
        token = auth.create_access_token(
            {"sub": "user123"},
            expires_delta=timedelta(seconds=-1),  # Already expired
        )

        with pytest.raises(TokenExpiredError):
            auth.verify_token(token)


class TestTokenPayload:
    """Test token payload handling."""

    def test_extra_claims(self, auth):
        """Should preserve extra claims in payload."""
        token = auth.create_access_token({
            "sub": "user123",
            "role": "admin",
            "org_id": "org456",
        })
        payload = auth.verify_token(token)

        assert payload.sub == "user123"
        assert payload.extra["role"] == "admin"
        assert payload.extra["org_id"] == "org456"

    def test_jti_uniqueness(self, auth):
        """Each token should have a unique JTI."""
        token1 = auth.create_access_token({"sub": "user123"})
        token2 = auth.create_access_token({"sub": "user123"})

        payload1 = auth.verify_token(token1)
        payload2 = auth.verify_token(token2)

        assert payload1.jti != payload2.jti


class TestDecodeWithoutVerification:
    """Test unverified decoding."""

    def test_decode_without_verification(self, auth):
        """Should decode token without verifying signature."""
        token = auth.create_access_token({"sub": "user123"})
        payload = auth.decode_without_verification(token)

        assert payload["sub"] == "user123"
        assert payload["type"] == "access"

    def test_get_token_jti(self, auth):
        """Should extract JTI from token."""
        token = auth.create_access_token({"sub": "user123"})
        jti = auth.get_token_jti(token)

        assert jti
        assert len(jti) > 0

    def test_get_token_exp(self, auth):
        """Should extract expiration from token."""
        token = auth.create_access_token({"sub": "user123"})
        exp = auth.get_token_exp(token)

        assert exp
        assert exp > 0
