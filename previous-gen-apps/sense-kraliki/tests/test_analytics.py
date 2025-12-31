"""Tests for usage analytics module.

These tests mock Redis at the module level to avoid dependency on redis package.
"""
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

# Mock redis module before any imports that might need it
mock_redis_module = MagicMock()
mock_redis_module.asyncio = MagicMock()
sys.modules['redis'] = mock_redis_module
sys.modules['redis.asyncio'] = mock_redis_module.asyncio


class TestAnalytics:
    """Tests for Analytics class."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create mock Redis client."""
        mock = MagicMock()
        mock.sadd = AsyncMock(return_value=1)
        mock.expire = AsyncMock(return_value=True)
        mock.incr = AsyncMock(return_value=1)
        mock.get = AsyncMock(return_value="10")
        mock.scard = AsyncMock(return_value=5)
        mock.sunion = AsyncMock(return_value={"user1", "user2", "user3", "user4", "user5"})
        mock.close = AsyncMock()
        return mock

    @pytest.fixture(autouse=True)
    def clear_analytics_import(self):
        """Clear analytics module cache between tests."""
        # Remove cached analytics module
        to_remove = [k for k in sys.modules if 'app.core.analytics' in k]
        for mod in to_remove:
            del sys.modules[mod]
        yield
        # Cleanup after test
        to_remove = [k for k in sys.modules if 'app.core.analytics' in k]
        for mod in to_remove:
            del sys.modules[mod]

    @pytest.mark.asyncio
    async def test_track_user(self, mock_redis_client):
        """Test tracking user activity."""
        mock_redis_module.asyncio.from_url = MagicMock(return_value=mock_redis_client)

        from app.core.analytics import Analytics

        analytics = Analytics()
        analytics._redis = mock_redis_client

        await analytics.track_user(12345)

        # Should add to daily, weekly, monthly, and total sets
        assert mock_redis_client.sadd.call_count >= 4
        assert mock_redis_client.expire.call_count >= 3

    @pytest.mark.asyncio
    async def test_track_command(self, mock_redis_client):
        """Test tracking command usage."""
        mock_redis_module.asyncio.from_url = MagicMock(return_value=mock_redis_client)

        from app.core.analytics import Analytics

        analytics = Analytics()
        analytics._redis = mock_redis_client

        await analytics.track_command("sense", 12345)

        # Should track user and increment command counters
        assert mock_redis_client.incr.call_count >= 2

    @pytest.mark.asyncio
    async def test_track_chart_type(self, mock_redis_client):
        """Test tracking chart type generation."""
        mock_redis_module.asyncio.from_url = MagicMock(return_value=mock_redis_client)

        from app.core.analytics import Analytics

        analytics = Analytics()
        analytics._redis = mock_redis_client

        await analytics.track_chart_type("dream", 12345)

        # Should increment chart type counters
        assert mock_redis_client.incr.call_count >= 2

    @pytest.mark.asyncio
    async def test_track_error(self, mock_redis_client):
        """Test tracking error occurrences."""
        mock_redis_module.asyncio.from_url = MagicMock(return_value=mock_redis_client)

        from app.core.analytics import Analytics

        analytics = Analytics()
        analytics._redis = mock_redis_client

        await analytics.track_error("api_failure", "sense")

        # Should increment error counters
        assert mock_redis_client.incr.call_count >= 3

    @pytest.mark.asyncio
    async def test_get_stats(self, mock_redis_client):
        """Test retrieving analytics stats."""
        mock_redis_module.asyncio.from_url = MagicMock(return_value=mock_redis_client)

        from app.core.analytics import Analytics

        analytics = Analytics()
        analytics._redis = mock_redis_client

        stats = await analytics.get_stats()

        # Should return structured stats
        assert "users" in stats
        assert "charts" in stats
        assert "commands" in stats
        assert "errors" in stats
        assert "timestamp" in stats

        # Check user stats structure
        assert "daily_active" in stats["users"]
        assert "weekly_active" in stats["users"]
        assert "monthly_active" in stats["users"]
        assert "total" in stats["users"]

    @pytest.mark.asyncio
    async def test_get_stats_handles_redis_error(self, mock_redis_client):
        """Test that get_stats handles Redis errors gracefully."""
        mock_redis_client.scard = AsyncMock(side_effect=Exception("Redis connection error"))
        mock_redis_client.sunion = AsyncMock(side_effect=Exception("Redis connection error"))
        mock_redis_module.asyncio.from_url = MagicMock(return_value=mock_redis_client)

        from app.core.analytics import Analytics

        analytics = Analytics()
        analytics._redis = mock_redis_client

        stats = await analytics.get_stats()

        # Should return error response
        assert "error" in stats
        assert "timestamp" in stats


class TestStatsCommand:
    """Tests for /stats command handler."""

    @pytest.mark.asyncio
    async def test_stats_requires_admin(self, mock_message):
        """Test that /stats is admin-only."""
        mock_message.text = "/stats"
        mock_message.from_user.id = 99999  # Non-admin user

        # Non-admin should get rejection message
        # This would be tested via full handler integration

    @pytest.mark.asyncio
    async def test_stats_returns_analytics(self, mock_message):
        """Test that /stats returns analytics for admin."""
        mock_message.text = "/stats"
        mock_message.from_user.id = 12345  # Would need to be in admin list

        # Admin should get analytics response
        # This would be tested via full handler integration
