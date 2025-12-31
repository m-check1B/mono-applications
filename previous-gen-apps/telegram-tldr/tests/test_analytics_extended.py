"""Extended tests for analytics service.

These tests provide comprehensive coverage for the Analytics class.
"""
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, UTC
import json

import pytest


class MockRedis:
    """Mock Redis client for testing."""

    def __init__(self):
        self.data = {}
        self.sets = {}
        self.lists = {}
        self.expiry = {}

    def pipeline(self):
        return MockPipeline(self)

    async def get(self, key):
        return self.data.get(key)

    async def set(self, key, value, ex=None):
        self.data[key] = value
        if ex:
            self.expiry[key] = ex

    async def incr(self, key):
        val = int(self.data.get(key, 0)) + 1
        self.data[key] = str(val)
        return val

    async def incrby(self, key, amount):
        val = int(self.data.get(key, 0)) + amount
        self.data[key] = str(val)
        return val

    async def sadd(self, key, value):
        if key not in self.sets:
            self.sets[key] = set()
        self.sets[key].add(value)
        return 1

    async def scard(self, key):
        return len(self.sets.get(key, set()))

    async def lpush(self, key, value):
        if key not in self.lists:
            self.lists[key] = []
        self.lists[key].insert(0, value)
        return len(self.lists[key])

    async def ltrim(self, key, start, end):
        if key in self.lists:
            self.lists[key] = self.lists[key][start:end + 1]

    async def lrange(self, key, start, end):
        if key not in self.lists:
            return []
        return self.lists[key][start:end + 1]

    async def expire(self, key, seconds):
        self.expiry[key] = seconds

    async def close(self):
        pass


class MockPipeline:
    """Mock pipeline for batch operations."""

    def __init__(self, redis):
        self.redis = redis
        self.operations = []
        self.results = []

    def get(self, key):
        self.operations.append(("get", key))
        return self

    def set(self, key, value, ex=None):
        self.operations.append(("set", key, value, ex))
        return self

    def incr(self, key):
        self.operations.append(("incr", key))
        return self

    def incrby(self, key, amount):
        self.operations.append(("incrby", key, amount))
        return self

    def sadd(self, key, value):
        self.operations.append(("sadd", key, value))
        return self

    def scard(self, key):
        self.operations.append(("scard", key))
        return self

    def lpush(self, key, value):
        self.operations.append(("lpush", key, value))
        return self

    def ltrim(self, key, start, end):
        self.operations.append(("ltrim", key, start, end))
        return self

    def expire(self, key, seconds):
        self.operations.append(("expire", key, seconds))
        return self

    async def execute(self):
        results = []
        for op in self.operations:
            if op[0] == "get":
                results.append(self.redis.data.get(op[1]))
            elif op[0] == "set":
                self.redis.data[op[1]] = op[2]
                if op[3]:
                    self.redis.expiry[op[1]] = op[3]
                results.append(True)
            elif op[0] == "incr":
                val = int(self.redis.data.get(op[1], 0)) + 1
                self.redis.data[op[1]] = str(val)
                results.append(val)
            elif op[0] == "incrby":
                val = int(self.redis.data.get(op[1], 0)) + op[2]
                self.redis.data[op[1]] = str(val)
                results.append(val)
            elif op[0] == "sadd":
                if op[1] not in self.redis.sets:
                    self.redis.sets[op[1]] = set()
                self.redis.sets[op[1]].add(op[2])
                results.append(1)
            elif op[0] == "scard":
                results.append(len(self.redis.sets.get(op[1], set())))
            elif op[0] == "lpush":
                if op[1] not in self.redis.lists:
                    self.redis.lists[op[1]] = []
                self.redis.lists[op[1]].insert(0, op[2])
                results.append(len(self.redis.lists[op[1]]))
            elif op[0] == "ltrim":
                if op[1] in self.redis.lists:
                    self.redis.lists[op[1]] = self.redis.lists[op[1]][op[2]:op[3] + 1]
                results.append(True)
            elif op[0] == "expire":
                self.redis.expiry[op[1]] = op[2]
                results.append(True)
            else:
                results.append(None)
        return results


@pytest.fixture
def mock_redis():
    return MockRedis()


class TestAnalyticsInit:
    """Tests for Analytics initialization."""

    def test_init_creates_none_redis(self):
        """Analytics initializes with no Redis connection."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        assert analytics.redis is None


class TestAnalyticsConnect:
    """Tests for Analytics.connect()."""

    @pytest.mark.asyncio
    async def test_connect_creates_redis(self):
        """connect() creates Redis connection."""
        from app.services.analytics import Analytics

        analytics = Analytics()

        with patch("app.services.analytics.redis") as redis_mock:
            mock_redis_instance = MagicMock()
            redis_mock.from_url = MagicMock(return_value=mock_redis_instance)

            await analytics.connect()

        assert analytics.redis is not None
        redis_mock.from_url.assert_called_once()


class TestAnalyticsClose:
    """Tests for Analytics.close()."""

    @pytest.mark.asyncio
    async def test_close_closes_redis(self):
        """close() closes Redis connection."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = MagicMock()
        analytics.redis.close = AsyncMock()

        await analytics.close()

        analytics.redis.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_handles_none_redis(self):
        """close() handles None Redis gracefully."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = None

        # Should not raise
        await analytics.close()


class TestKeyGeneration:
    """Tests for key generation methods."""

    def test_key_generates_correct_format(self):
        """_key() generates correct key format."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        key = analytics._key("test:metric")
        assert key == "tldr:analytics:test:metric"

    def test_daily_key_generates_correct_format(self):
        """_daily_key() generates correct key format with date."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        test_date = datetime(2025, 12, 25, 12, 0, 0, tzinfo=UTC)
        key = analytics._daily_key("messages", test_date)
        assert key == "tldr:analytics:daily:2025-12-25:messages"

    def test_daily_key_uses_current_date_if_none(self):
        """_daily_key() uses current date if none provided."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        key = analytics._daily_key("messages")
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        assert today in key


class TestTrackMessage:
    """Tests for track_message()."""

    @pytest.mark.asyncio
    async def test_track_message_increments_counters(self, mock_redis):
        """track_message() increments various counters."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        await analytics.track_message(chat_id=-100123456, user_id=12345)

        # Check total messages incremented
        assert "tldr:analytics:messages:total" in mock_redis.data

        # Check unique user tracked
        assert any("users:all" in key for key in mock_redis.sets.keys())

        # Check unique chat tracked
        assert any("chats:all" in key for key in mock_redis.sets.keys())

    @pytest.mark.asyncio
    async def test_track_message_without_redis(self):
        """track_message() handles missing Redis gracefully."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = None

        # Should not raise
        await analytics.track_message(chat_id=-100123456, user_id=12345)


class TestTrackSummary:
    """Tests for track_summary()."""

    @pytest.mark.asyncio
    async def test_track_summary_increments_counters(self, mock_redis):
        """track_summary() increments summary counters."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        await analytics.track_summary(chat_id=-100123456, user_id=12345, message_count=50)

        # Check summaries incremented
        assert "tldr:analytics:summaries:total" in mock_redis.data

        # Check messages summarized tracked
        assert "tldr:analytics:messages:summarized" in mock_redis.data
        assert int(mock_redis.data["tldr:analytics:messages:summarized"]) == 50

    @pytest.mark.asyncio
    async def test_track_summary_without_redis(self):
        """track_summary() handles missing Redis gracefully."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = None

        # Should not raise
        await analytics.track_summary(chat_id=-100123456, user_id=12345, message_count=50)


class TestTrackError:
    """Tests for track_error()."""

    @pytest.mark.asyncio
    async def test_track_error_increments_counters(self, mock_redis):
        """track_error() increments error counters."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        await analytics.track_error("api_error", "Connection timeout")

        # Check errors incremented
        assert "tldr:analytics:errors:total" in mock_redis.data

        # Check error type tracked
        assert "tldr:analytics:errors:type:api_error" in mock_redis.data

        # Check error log added
        assert any("errors:log" in key for key in mock_redis.lists.keys())

    @pytest.mark.asyncio
    async def test_track_error_truncates_long_details(self, mock_redis):
        """track_error() truncates long error details."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        long_details = "x" * 1000  # 1000 character string
        await analytics.track_error("test_error", long_details)

        # Get the logged error
        log_key = "tldr:analytics:errors:log"
        assert log_key in mock_redis.lists
        error_log = json.loads(mock_redis.lists[log_key][0])
        assert len(error_log["details"]) <= 500

    @pytest.mark.asyncio
    async def test_track_error_without_redis(self):
        """track_error() handles missing Redis gracefully."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = None

        # Should not raise
        await analytics.track_error("test_error", "details")


class TestTrackSubscription:
    """Tests for track_subscription()."""

    @pytest.mark.asyncio
    async def test_track_subscription_increments_counters(self, mock_redis):
        """track_subscription() increments subscription counters."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        await analytics.track_subscription(chat_id=-100123456)

        # Check subscriptions incremented
        assert "tldr:analytics:subscriptions:total" in mock_redis.data

    @pytest.mark.asyncio
    async def test_track_subscription_without_redis(self):
        """track_subscription() handles missing Redis gracefully."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = None

        # Should not raise
        await analytics.track_subscription(chat_id=-100123456)


class TestTrackCommand:
    """Tests for track_command()."""

    @pytest.mark.asyncio
    async def test_track_command_increments_counter(self, mock_redis):
        """track_command() increments command counter."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        await analytics.track_command("summary")

        # Check command counter incremented
        assert "tldr:analytics:commands:summary" in mock_redis.data

    @pytest.mark.asyncio
    async def test_track_command_without_redis(self):
        """track_command() handles missing Redis gracefully."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = None

        # Should not raise
        await analytics.track_command("summary")


class TestGetStats:
    """Tests for get_stats()."""

    @pytest.mark.asyncio
    async def test_get_stats_returns_empty_without_redis(self):
        """get_stats() returns empty dict without Redis."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = None

        result = await analytics.get_stats()
        assert result == {}

    @pytest.mark.asyncio
    async def test_get_stats_returns_all_metrics(self, mock_redis):
        """get_stats() returns all expected metrics."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        # Set up some test data
        mock_redis.data["tldr:analytics:messages:total"] = "100"
        mock_redis.data["tldr:analytics:summaries:total"] = "10"
        mock_redis.sets["tldr:analytics:users:all"] = {"1", "2", "3"}
        mock_redis.sets["tldr:analytics:chats:all"] = {"c1", "c2"}

        result = await analytics.get_stats()

        assert result["messages_processed"] == 100
        assert result["summaries_generated"] == 10
        assert result["unique_users"] == 3
        assert result["unique_chats"] == 2


class TestGetDailyStats:
    """Tests for get_daily_stats()."""

    @pytest.mark.asyncio
    async def test_get_daily_stats_returns_empty_without_redis(self):
        """get_daily_stats() returns empty dict without Redis."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = None

        result = await analytics.get_daily_stats()
        assert result == {}

    @pytest.mark.asyncio
    async def test_get_daily_stats_returns_date_formatted(self, mock_redis):
        """get_daily_stats() returns date in correct format."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        result = await analytics.get_daily_stats()

        assert "date" in result
        # Should be in YYYY-MM-DD format
        assert len(result["date"]) == 10
        assert result["date"].count("-") == 2


class TestGetRecentErrors:
    """Tests for get_recent_errors()."""

    @pytest.mark.asyncio
    async def test_get_recent_errors_returns_empty_without_redis(self):
        """get_recent_errors() returns empty list without Redis."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = None

        result = await analytics.get_recent_errors()
        assert result == []

    @pytest.mark.asyncio
    async def test_get_recent_errors_returns_parsed_errors(self, mock_redis):
        """get_recent_errors() returns parsed error objects."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        # Add some test errors
        error = {"type": "test_error", "details": "test", "ts": "2025-12-25T00:00:00"}
        mock_redis.lists["tldr:analytics:errors:log"] = [json.dumps(error)]

        result = await analytics.get_recent_errors()

        assert len(result) == 1
        assert result[0]["type"] == "test_error"


class TestGetCommandStats:
    """Tests for get_command_stats()."""

    @pytest.mark.asyncio
    async def test_get_command_stats_returns_empty_without_redis(self):
        """get_command_stats() returns empty dict without Redis."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = None

        result = await analytics.get_command_stats()
        assert result == {}

    @pytest.mark.asyncio
    async def test_get_command_stats_returns_all_commands(self, mock_redis):
        """get_command_stats() returns all expected commands."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        mock_redis.data["tldr:analytics:commands:start"] = "50"
        mock_redis.data["tldr:analytics:commands:summary"] = "100"

        result = await analytics.get_command_stats()

        assert "start" in result
        assert "summary" in result
        assert result["start"] == 50
        assert result["summary"] == 100


class TestGetTrendData:
    """Tests for get_trend_data()."""

    @pytest.mark.asyncio
    async def test_get_trend_data_returns_empty_without_redis(self):
        """get_trend_data() returns empty list without Redis."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = None

        result = await analytics.get_trend_data(7)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_trend_data_returns_correct_days(self, mock_redis):
        """get_trend_data() returns correct number of days."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        result = await analytics.get_trend_data(7)

        assert len(result) == 7


class TestGetDashboardData:
    """Tests for get_dashboard_data()."""

    @pytest.mark.asyncio
    async def test_get_dashboard_data_returns_empty_without_redis(self):
        """get_dashboard_data() returns empty dict without Redis."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = None

        result = await analytics.get_dashboard_data()
        assert result == {}

    @pytest.mark.asyncio
    async def test_get_dashboard_data_includes_all_sections(self, mock_redis):
        """get_dashboard_data() includes all expected sections."""
        from app.services.analytics import Analytics

        analytics = Analytics()
        analytics.redis = mock_redis

        result = await analytics.get_dashboard_data()

        assert "generated_at" in result
        assert "all_time" in result
        assert "today" in result
        assert "commands" in result
        assert "trends_7d" in result
        assert "trends_30d" in result
        assert "recent_errors" in result


class TestFormatStatsMessage:
    """Tests for format_stats_message()."""

    def test_format_stats_message_includes_all_sections(self):
        """format_stats_message() includes all expected sections."""
        from app.services.analytics import Analytics

        analytics = Analytics()

        all_time = {
            "messages_processed": 1000,
            "summaries_generated": 100,
            "messages_summarized": 5000,
            "unique_users": 50,
            "unique_chats": 20,
            "subscriptions_total": 5,
            "errors_total": 2,
        }
        daily = {
            "date": "2025-12-25",
            "messages_processed": 100,
            "summaries_generated": 10,
            "active_users": 15,
            "active_chats": 8,
            "errors": 0,
        }
        commands = {
            "start": 50,
            "summary": 100,
            "help": 30,
            "status": 20,
            "subscribe": 10,
        }

        result = analytics.format_stats_message(all_time, daily, commands)

        assert "All-Time" in result
        assert "Today" in result
        assert "Command Usage" in result
        assert "1,000" in result  # messages_processed formatted
        assert "2025-12-25" in result

    def test_format_stats_message_handles_missing_values(self):
        """format_stats_message() handles missing values gracefully."""
        from app.services.analytics import Analytics

        analytics = Analytics()

        result = analytics.format_stats_message({}, {}, {})

        # Should contain section headers even with empty data
        assert "All-Time" in result
        assert "Today" in result
        assert "0" in result  # Default values should be 0


class TestGlobalInstance:
    """Tests for global analytics instance."""

    def test_global_instance_exists(self):
        """Global analytics instance should exist."""
        from app.services.analytics import analytics

        assert analytics is not None

    def test_global_instance_is_analytics(self):
        """Global instance should be Analytics type."""
        from app.services.analytics import analytics, Analytics

        assert isinstance(analytics, Analytics)
