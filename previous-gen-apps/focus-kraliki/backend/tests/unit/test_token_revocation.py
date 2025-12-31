"""
Test Redis Token Revocation System
Tests logout mechanism and token blacklisting with mocked Redis
"""

import pytest
from datetime import datetime, timedelta
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.token_revocation import TokenBlacklist
from app.core.ed25519_auth import Ed25519Auth


class MockRedis:
    """In-memory mock of Redis for testing."""

    def __init__(self):
        self._store = {}
        self._ttl = {}

    async def setex(self, key: str, ttl: int, value: str):
        """Set key with expiration."""
        self._store[key] = value
        self._ttl[key] = ttl

    async def exists(self, key: str) -> int:
        """Check if key exists."""
        return 1 if key in self._store else 0

    async def keys(self, pattern: str) -> list:
        """Get keys matching pattern (simple prefix matching)."""
        prefix = pattern.replace("*", "")
        return [k for k in self._store.keys() if k.startswith(prefix)]

    async def flushdb(self):
        """Clear all data."""
        self._store.clear()
        self._ttl.clear()

    async def close(self):
        """Close connection (no-op for mock)."""
        pass


@pytest.fixture
async def mock_redis():
    """Create mock Redis instance."""
    return MockRedis()


@pytest.fixture
async def blacklist(mock_redis):
    """Create a TokenBlacklist instance with mock Redis."""
    bl = TokenBlacklist(redis_url="redis://localhost:6379/15")
    bl._redis = mock_redis
    yield bl


@pytest.fixture
def auth():
    """Create Ed25519Auth instance for generating test tokens."""
    return Ed25519Auth(keys_dir="keys")


class TestTokenBlacklist:
    """Test Redis-based token blacklist functionality."""

    @pytest.mark.asyncio
    async def test_revoke_token(self, blacklist, auth):
        """Test revoking a single token."""
        # Create a test token
        token = auth.create_access_token({"sub": "user-123"})

        # Decode to get expiration
        payload = auth.decode_without_verification(token)
        exp = payload["exp"]

        # Revoke token
        await blacklist.revoke_token(token, exp)

        # Check if token is revoked
        is_revoked = await blacklist.is_revoked(token)
        assert is_revoked is True

    @pytest.mark.asyncio
    async def test_non_revoked_token(self, blacklist, auth):
        """Test that non-revoked tokens are not in blacklist."""
        # Create a token but don't revoke it
        token = auth.create_access_token({"sub": "user-456"})

        # Check if token is revoked
        is_revoked = await blacklist.is_revoked(token)
        assert is_revoked is False

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens(self, blacklist):
        """Test revoking all tokens for a user."""
        user_id = "user-789"

        # Revoke all user tokens
        await blacklist.revoke_all_user_tokens(user_id)

        # Check if user tokens are revoked
        is_revoked = await blacklist.is_user_revoked(user_id)
        assert is_revoked is True

    @pytest.mark.asyncio
    async def test_different_user_not_revoked(self, blacklist):
        """Test that revoking one user doesn't affect others."""
        user1 = "user-aaa"
        user2 = "user-bbb"

        # Revoke user1 tokens
        await blacklist.revoke_all_user_tokens(user1)

        # Check user1 is revoked
        assert await blacklist.is_user_revoked(user1) is True

        # Check user2 is NOT revoked
        assert await blacklist.is_user_revoked(user2) is False

    @pytest.mark.asyncio
    async def test_token_ttl_handling(self, blacklist, auth):
        """Test that tokens are stored with proper TTL."""
        # Create token with short expiration
        token = auth.create_access_token(
            {"sub": "user-ttl"},
            expires_delta=timedelta(seconds=60)
        )

        # Get expiration time
        payload = auth.decode_without_verification(token)
        exp = payload["exp"]

        # Revoke token
        await blacklist.revoke_token(token, exp)

        # Verify token is revoked
        assert await blacklist.is_revoked(token) is True

        # Verify TTL was stored (in mock, we can check the _ttl dict)
        if hasattr(blacklist._redis, '_ttl'):
            key = f"blacklist:token:{token}"
            assert key in blacklist._redis._ttl

    @pytest.mark.asyncio
    async def test_expired_token_zero_ttl(self, blacklist, auth):
        """Test that already-expired tokens get zero TTL (not stored)."""
        # Create an already-expired token
        token = auth.create_access_token(
            {"sub": "user-expired"},
            expires_delta=timedelta(seconds=-10)  # Expired 10 seconds ago
        )

        # Get expiration time (in the past)
        payload = auth.decode_without_verification(token)
        exp = payload["exp"]

        # Revoke token (should handle negative TTL gracefully)
        await blacklist.revoke_token(token, exp)

        # Token should NOT be in blacklist (TTL was 0 or negative)
        is_revoked = await blacklist.is_revoked(token)
        # Should be False since TTL was 0
        assert is_revoked is False

    @pytest.mark.asyncio
    async def test_revocation_stats(self, blacklist, auth):
        """Test getting revocation statistics."""
        # Revoke some tokens
        token1 = auth.create_access_token({"sub": "user-1"})
        token2 = auth.create_access_token({"sub": "user-2"})

        payload1 = auth.decode_without_verification(token1)
        payload2 = auth.decode_without_verification(token2)

        await blacklist.revoke_token(token1, payload1["exp"])
        await blacklist.revoke_token(token2, payload2["exp"])

        # Revoke all tokens for a user
        await blacklist.revoke_all_user_tokens("user-global")

        # Get stats
        stats = await blacklist.get_revocation_stats()

        assert stats["revoked_tokens"] == 2
        assert stats["revoked_users"] == 1
        assert stats["total_revocations"] == 3

    @pytest.mark.asyncio
    async def test_multiple_tokens_per_user(self, blacklist, auth):
        """Test that user-wide revocation affects all user tokens."""
        user_id = "user-multi"

        # Create multiple tokens for the same user
        token1 = auth.create_access_token({"sub": user_id})
        token2 = auth.create_access_token({"sub": user_id})
        token3 = auth.create_access_token({"sub": user_id})

        # Revoke all user tokens
        await blacklist.revoke_all_user_tokens(user_id)

        # All tokens should be considered revoked via user revocation
        assert await blacklist.is_user_revoked(user_id) is True


class TestTokenRevocationIntegration:
    """Integration tests for token revocation with Ed25519 auth."""

    @pytest.mark.asyncio
    async def test_complete_logout_flow(self, blacklist, auth):
        """Test complete logout flow: create token, revoke, verify rejected."""
        # 1. User logs in (gets token)
        user_id = "user-logout-test"
        token = auth.create_access_token({"sub": user_id, "email": "test@example.com"})

        # 2. Verify token is valid
        payload = auth.verify_token(token)
        assert payload["sub"] == user_id

        # 3. Token is NOT revoked yet
        assert await blacklist.is_revoked(token) is False

        # 4. User logs out (revoke token)
        payload = auth.decode_without_verification(token)
        await blacklist.revoke_token(token, payload["exp"])

        # 5. Token is now revoked
        assert await blacklist.is_revoked(token) is True

    @pytest.mark.asyncio
    async def test_password_change_flow(self, blacklist, auth):
        """Test password change flow: revoke all user tokens."""
        user_id = "user-password-change"

        # User has multiple active sessions (tokens)
        token1 = auth.create_access_token({"sub": user_id})
        token2 = auth.create_access_token({"sub": user_id})
        token3 = auth.create_access_token({"sub": user_id})

        # All tokens are valid
        assert await blacklist.is_user_revoked(user_id) is False

        # User changes password (revoke all tokens)
        await blacklist.revoke_all_user_tokens(user_id)

        # All tokens are now invalid
        assert await blacklist.is_user_revoked(user_id) is True

    @pytest.mark.asyncio
    async def test_refresh_token_revocation(self, blacklist, auth):
        """Test that refresh tokens can be revoked."""
        user_id = "user-refresh"

        # Create refresh token
        refresh_token = auth.create_refresh_token({"sub": user_id})

        # Verify it's valid
        payload = auth.verify_token(refresh_token, expected_type="refresh")
        assert payload["sub"] == user_id

        # Revoke refresh token
        payload = auth.decode_without_verification(refresh_token)
        await blacklist.revoke_token(refresh_token, payload["exp"])

        # Token is revoked
        assert await blacklist.is_revoked(refresh_token) is True

    @pytest.mark.asyncio
    async def test_concurrent_revocations(self, blacklist, auth):
        """Test concurrent token revocations don't conflict."""
        # Create multiple tokens
        tokens = [
            auth.create_access_token({"sub": f"user-{i}"})
            for i in range(10)
        ]

        # Revoke all tokens concurrently
        async def revoke_token_async(token):
            payload = auth.decode_without_verification(token)
            await blacklist.revoke_token(token, payload["exp"])

        await asyncio.gather(*[revoke_token_async(t) for t in tokens])

        # All tokens should be revoked
        for token in tokens:
            assert await blacklist.is_revoked(token) is True

    @pytest.mark.asyncio
    async def test_redis_connection_handling(self):
        """Test Redis connection initialization and cleanup."""
        bl = TokenBlacklist(redis_url="redis://localhost:6379/15")

        # Before connect, _redis should be None
        assert bl._redis is None

    @pytest.mark.asyncio
    async def test_ensure_connection_failure(self):
        """Test graceful degradation when Redis is unavailable."""
        bl = TokenBlacklist(redis_url="redis://invalid-host:6379/15")

        # Mock connect to fail
        async def failing_connect():
            raise ConnectionError("Cannot connect to Redis")

        bl.connect = failing_connect

        # Should return False gracefully
        result = await bl._ensure_connection()
        assert result is False

        # Operations should return safe defaults
        assert await bl.is_revoked("any-token") is False
        assert await bl.is_user_revoked("any-user") is False


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.mark.asyncio
    async def test_empty_token_revocation(self, blacklist):
        """Test revoking empty or invalid token strings."""
        # This should not crash
        future_exp = int(datetime.utcnow().timestamp()) + 3600
        await blacklist.revoke_token("", future_exp)

        # Empty token is "revoked" (in blacklist)
        assert await blacklist.is_revoked("") is True

    @pytest.mark.asyncio
    async def test_empty_user_id_revocation(self, blacklist):
        """Test revoking with empty user ID."""
        # This should not crash
        await blacklist.revoke_all_user_tokens("")

        # Empty user ID is "revoked"
        assert await blacklist.is_user_revoked("") is True

    @pytest.mark.asyncio
    async def test_very_long_user_id(self, blacklist):
        """Test with very long user ID."""
        long_user_id = "user-" + ("x" * 1000)

        await blacklist.revoke_all_user_tokens(long_user_id)
        assert await blacklist.is_user_revoked(long_user_id) is True

    @pytest.mark.asyncio
    async def test_special_characters_in_user_id(self, blacklist):
        """Test user IDs with special characters."""
        special_user_id = "user:123@domain.com/test#query"

        await blacklist.revoke_all_user_tokens(special_user_id)
        assert await blacklist.is_user_revoked(special_user_id) is True


class TestWithoutRedis:
    """Test behavior when Redis is not available."""

    @pytest.mark.asyncio
    async def test_graceful_degradation_revoke(self):
        """Test revoke gracefully handles missing Redis."""
        bl = TokenBlacklist(redis_url="redis://invalid-host:6379/15")
        # Mock connect to always fail
        async def failing_connect():
            raise ConnectionError("Cannot connect to Redis")
        bl.connect = failing_connect

        # Should not raise, just return silently
        await bl.revoke_token("test-token", int(datetime.utcnow().timestamp()) + 3600)

    @pytest.mark.asyncio
    async def test_graceful_degradation_is_revoked(self):
        """Test is_revoked returns False when Redis unavailable."""
        bl = TokenBlacklist(redis_url="redis://invalid-host:6379/15")
        # Mock connect to always fail
        async def failing_connect():
            raise ConnectionError("Cannot connect to Redis")
        bl.connect = failing_connect

        # Should return False (not revoked) when Redis unavailable
        result = await bl.is_revoked("test-token")
        assert result is False

    @pytest.mark.asyncio
    async def test_graceful_degradation_stats(self):
        """Test stats return zeros when Redis unavailable."""
        bl = TokenBlacklist(redis_url="redis://invalid-host:6379/15")
        # Mock connect to always fail
        async def failing_connect():
            raise ConnectionError("Cannot connect to Redis")
        bl.connect = failing_connect

        stats = await bl.get_revocation_stats()
        assert stats["revoked_tokens"] == 0
        assert stats["revoked_users"] == 0
        assert stats["total_revocations"] == 0
