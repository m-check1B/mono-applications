"""Tests for token revocation."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from auth_core.revocation import TokenBlacklist, RevocationStats


class MockRedis:
    """Mock Redis client for testing."""

    def __init__(self):
        self._data = {}

    async def setex(self, name: str, time: int, value: str) -> None:
        self._data[name] = value

    async def exists(self, name: str) -> int:
        return 1 if name in self._data else 0

    async def keys(self, pattern: str) -> list:
        import fnmatch
        return [k for k in self._data.keys() if fnmatch.fnmatch(k, pattern)]

    async def close(self) -> None:
        pass


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    return MockRedis()


@pytest.fixture
def blacklist(mock_redis):
    """Create a TokenBlacklist with mock Redis."""
    return TokenBlacklist(redis_client=mock_redis)


class TestTokenRevocation:
    """Test individual token revocation."""

    @pytest.mark.asyncio
    async def test_revoke_token(self, blacklist):
        """Should revoke a token."""
        future_exp = int(datetime.utcnow().timestamp()) + 3600  # 1 hour

        result = await blacklist.revoke_token("test-token", future_exp)
        assert result is True

    @pytest.mark.asyncio
    async def test_is_revoked_true(self, blacklist):
        """Should return True for revoked token."""
        future_exp = int(datetime.utcnow().timestamp()) + 3600

        await blacklist.revoke_token("test-token", future_exp)
        is_revoked = await blacklist.is_revoked("test-token")

        assert is_revoked is True

    @pytest.mark.asyncio
    async def test_is_revoked_false(self, blacklist):
        """Should return False for non-revoked token."""
        is_revoked = await blacklist.is_revoked("unknown-token")
        assert is_revoked is False

    @pytest.mark.asyncio
    async def test_already_expired_token(self, blacklist):
        """Should not blacklist already expired tokens."""
        past_exp = int(datetime.utcnow().timestamp()) - 3600  # 1 hour ago

        result = await blacklist.revoke_token("expired-token", past_exp)
        assert result is True  # Success, but no-op

        # Token should not be in blacklist (no need to track expired tokens)
        is_revoked = await blacklist.is_revoked("expired-token")
        assert is_revoked is False


class TestUserRevocation:
    """Test user-level revocation."""

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens(self, blacklist):
        """Should revoke all tokens for a user."""
        result = await blacklist.revoke_all_user_tokens("user123")
        assert result is True

    @pytest.mark.asyncio
    async def test_is_user_revoked_true(self, blacklist):
        """Should return True for revoked user."""
        await blacklist.revoke_all_user_tokens("user123")
        is_revoked = await blacklist.is_user_revoked("user123")

        assert is_revoked is True

    @pytest.mark.asyncio
    async def test_is_user_revoked_false(self, blacklist):
        """Should return False for non-revoked user."""
        is_revoked = await blacklist.is_user_revoked("unknown-user")
        assert is_revoked is False


class TestCombinedRevocationCheck:
    """Test combined token and user revocation."""

    @pytest.mark.asyncio
    async def test_token_revoked(self, blacklist):
        """Should detect revoked token."""
        future_exp = int(datetime.utcnow().timestamp()) + 3600
        await blacklist.revoke_token("test-token", future_exp)

        is_revoked = await blacklist.is_token_or_user_revoked(
            "test-token", "user123"
        )
        assert is_revoked is True

    @pytest.mark.asyncio
    async def test_user_revoked(self, blacklist):
        """Should detect revoked user."""
        await blacklist.revoke_all_user_tokens("user123")

        is_revoked = await blacklist.is_token_or_user_revoked(
            "some-token", "user123"
        )
        assert is_revoked is True

    @pytest.mark.asyncio
    async def test_neither_revoked(self, blacklist):
        """Should return False when neither token nor user revoked."""
        is_revoked = await blacklist.is_token_or_user_revoked(
            "valid-token", "valid-user"
        )
        assert is_revoked is False


class TestRevocationStats:
    """Test revocation statistics."""

    @pytest.mark.asyncio
    async def test_get_stats_empty(self, blacklist):
        """Should return zero stats when empty."""
        stats = await blacklist.get_revocation_stats()

        assert stats.revoked_tokens == 0
        assert stats.revoked_users == 0
        assert stats.total_revocations == 0

    @pytest.mark.asyncio
    async def test_get_stats_with_data(self, blacklist):
        """Should return correct stats."""
        future_exp = int(datetime.utcnow().timestamp()) + 3600

        await blacklist.revoke_token("token1", future_exp)
        await blacklist.revoke_token("token2", future_exp)
        await blacklist.revoke_all_user_tokens("user1")

        stats = await blacklist.get_revocation_stats()

        assert stats.revoked_tokens == 2
        assert stats.revoked_users == 1
        assert stats.total_revocations == 3


class TestGracefulDegradation:
    """Test behavior when Redis is unavailable."""

    @pytest.mark.asyncio
    async def test_no_redis_revoke(self):
        """Should not fail when Redis unavailable."""
        blacklist = TokenBlacklist()  # No Redis URL or client

        future_exp = int(datetime.utcnow().timestamp()) + 3600
        result = await blacklist.revoke_token("test", future_exp)

        assert result is False  # Failed but didn't raise

    @pytest.mark.asyncio
    async def test_no_redis_is_revoked(self):
        """Should return False when Redis unavailable."""
        blacklist = TokenBlacklist()

        is_revoked = await blacklist.is_revoked("test")
        assert is_revoked is False  # Assume valid when can't check

    @pytest.mark.asyncio
    async def test_no_redis_stats(self):
        """Should return zero stats when Redis unavailable."""
        blacklist = TokenBlacklist()

        stats = await blacklist.get_revocation_stats()

        assert stats.revoked_tokens == 0
        assert stats.revoked_users == 0


class TestKeyPrefixing:
    """Test Redis key namespacing."""

    @pytest.mark.asyncio
    async def test_custom_key_prefix(self):
        """Should use custom key prefix."""
        mock_redis = MockRedis()
        blacklist = TokenBlacklist(
            redis_client=mock_redis,
            key_prefix="myapp:auth",
        )

        future_exp = int(datetime.utcnow().timestamp()) + 3600
        await blacklist.revoke_token("test-token", future_exp)

        assert "myapp:auth:token:test-token" in mock_redis._data
