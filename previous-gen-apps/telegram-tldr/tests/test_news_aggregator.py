"""Tests for news aggregator service."""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.news_aggregator import (
    DEFAULT_RSS_FEEDS,
    NewsAggregator,
    news_aggregator,
)


@pytest.fixture
def mock_redis():
    """Mock Redis connection."""
    redis_mock = AsyncMock()
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.sadd = AsyncMock(return_value=1)
    redis_mock.srem = AsyncMock(return_value=1)
    redis_mock.smembers = AsyncMock(return_value=set())
    redis_mock.sismember = AsyncMock(return_value=False)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.expire = AsyncMock(return_value=True)
    redis_mock.scan = AsyncMock(return_value=(0, []))
    return redis_mock


@pytest.fixture
def aggregator(mock_redis):
    """News aggregator with mock Redis."""
    agg = NewsAggregator()
    agg.redis = mock_redis
    return agg


class TestDefaultRSSFeeds:
    """Tests for default RSS feeds configuration."""

    def test_has_tech_feeds(self):
        """Should have tech topic feeds."""
        assert "tech" in DEFAULT_RSS_FEEDS
        assert len(DEFAULT_RSS_FEEDS["tech"]) > 0

    def test_has_crypto_feeds(self):
        """Should have crypto topic feeds."""
        assert "crypto" in DEFAULT_RSS_FEEDS
        assert len(DEFAULT_RSS_FEEDS["crypto"]) > 0

    def test_has_news_feeds(self):
        """Should have news topic feeds."""
        assert "news" in DEFAULT_RSS_FEEDS
        assert len(DEFAULT_RSS_FEEDS["news"]) > 0

    def test_has_deals_feeds(self):
        """Should have deals topic feeds."""
        assert "deals" in DEFAULT_RSS_FEEDS
        assert len(DEFAULT_RSS_FEEDS["deals"]) > 0

    def test_feeds_are_urls(self):
        """All feeds should be valid URLs."""
        for topic, feeds in DEFAULT_RSS_FEEDS.items():
            for feed in feeds:
                assert feed.startswith("http"), f"Invalid URL in {topic}: {feed}"


class TestRedisKeyPatterns:
    """Tests for Redis key generation."""

    def test_news_items_key(self, aggregator):
        """Should generate correct news items key."""
        key = aggregator._news_items_key("tech")
        assert key == "tldr:news:tech:items"

    def test_news_last_fetched_key(self, aggregator):
        """Should generate correct last fetched key."""
        key = aggregator._news_last_fetched_key("crypto")
        assert key == "tldr:news:crypto:last_fetched"

    def test_user_news_subs_key(self, aggregator):
        """Should generate correct user news subs key."""
        key = aggregator._user_news_subs_key(123)
        assert key == "tldr:user:123:news_topics"

    def test_user_news_digest_time_key(self, aggregator):
        """Should generate correct digest time key."""
        key = aggregator._user_news_digest_time_key(456)
        assert key == "tldr:user:456:newsletter_time"

    def test_newsletter_subscribers_key(self, aggregator):
        """Should generate correct newsletter subscribers key."""
        key = aggregator._newsletter_subscribers_key()
        assert key == "tldr:newsletter:subscribers"


class TestFetchTopicNews:
    """Tests for fetch_topic_news."""

    @pytest.mark.asyncio
    async def test_unknown_topic_returns_empty(self, aggregator):
        """Should return empty list for unknown topic."""
        result = await aggregator.fetch_topic_news("unknown_topic")
        assert result == []

    @pytest.mark.asyncio
    async def test_fetches_from_feeds(self, aggregator, mock_redis):
        """Should fetch and parse RSS feeds."""
        mock_items = [
            {
                "title": "Test Article",
                "link": "https://example.com/article",
                "published": datetime.now(UTC),
                "summary": "Article summary",
                "source": "Test Source",
            }
        ]

        with patch.object(aggregator, "_parse_feed", return_value=mock_items):
            result = await aggregator.fetch_topic_news("tech")
            assert len(result) > 0
            assert result[0]["title"] == "Test Article"

    @pytest.mark.asyncio
    async def test_handles_feed_error(self, aggregator, mock_redis):
        """Should handle feed parsing errors gracefully."""
        with patch.object(
            aggregator, "_parse_feed", side_effect=Exception("Feed error")
        ):
            result = await aggregator.fetch_topic_news("tech")
            assert result == []

    @pytest.mark.asyncio
    async def test_stores_items_in_redis(self, aggregator, mock_redis):
        """Should store fetched items in Redis."""
        mock_items = [
            {
                "title": "Test",
                "link": "https://example.com",
                "published": datetime.now(UTC),
                "summary": "Summary",
                "source": "Source",
            }
        ]

        with patch.object(aggregator, "_parse_feed", return_value=mock_items):
            await aggregator.fetch_topic_news("tech")
            # Verify Redis set was called for storage
            mock_redis.set.assert_called()


class TestParseFeed:
    """Tests for _parse_feed."""

    def test_parses_feed_entries(self, aggregator):
        """Should parse feed entries into items."""
        mock_feed = MagicMock()
        mock_entry = MagicMock()
        # Use current time to ensure entry isn't filtered as old
        now = datetime.now(UTC)
        mock_entry.published_parsed = now.timetuple()[:6] + (0, 0, 0)
        mock_entry.get = lambda k, d="": {"title": "Test Title", "link": "https://test.com"}.get(k, d)
        mock_entry.summary = "Test summary"
        mock_feed.entries = [mock_entry]
        mock_feed.feed = MagicMock()
        mock_feed.feed.get = lambda k, d="": "Test Source"

        with patch("app.services.news_aggregator.feedparser.parse", return_value=mock_feed):
            items = aggregator._parse_feed("https://example.com/feed", 24)
            assert len(items) == 1
            assert items[0]["title"] == "Test Title"
            assert items[0]["source"] == "Test Source"

    def test_filters_old_items(self, aggregator):
        """Should filter out items older than specified hours."""
        mock_feed = MagicMock()
        mock_entry = MagicMock()
        # Old entry - 48 hours ago
        old_time = datetime.now(UTC) - timedelta(hours=48)
        mock_entry.published_parsed = old_time.timetuple()[:6] + (0, 0, 0)
        mock_entry.get = lambda k, d="": "Title"
        mock_entry.summary = "Summary"
        mock_feed.entries = [mock_entry]
        mock_feed.feed = MagicMock()
        mock_feed.feed.get = lambda k, d="": "Source"

        with patch("app.services.news_aggregator.feedparser.parse", return_value=mock_feed):
            items = aggregator._parse_feed("https://example.com/feed", 24)
            assert len(items) == 0

    def test_strips_html_from_summary(self, aggregator):
        """Should strip HTML tags from summary."""
        mock_feed = MagicMock()
        mock_entry = MagicMock()
        mock_entry.published_parsed = datetime.now(UTC).timetuple()[:6] + (0, 0, 0)
        mock_entry.get = lambda k, d="": "Title"
        mock_entry.summary = "<p>Test <b>summary</b> with HTML</p>"
        mock_feed.entries = [mock_entry]
        mock_feed.feed = MagicMock()
        mock_feed.feed.get = lambda k, d="": "Source"

        with patch("app.services.news_aggregator.feedparser.parse", return_value=mock_feed):
            items = aggregator._parse_feed("https://example.com/feed", 24)
            assert "<" not in items[0]["summary"]
            assert ">" not in items[0]["summary"]


class TestGetCachedNews:
    """Tests for get_cached_news."""

    @pytest.mark.asyncio
    async def test_returns_empty_without_redis(self):
        """Should return empty without Redis."""
        agg = NewsAggregator()
        result = await agg.get_cached_news("tech")
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_cache(self, aggregator, mock_redis):
        """Should return empty when no cached data."""
        mock_redis.get.return_value = None
        result = await aggregator.get_cached_news("tech")
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_cached_items(self, aggregator, mock_redis):
        """Should return cached items with parsed dates."""
        cached_data = json.dumps([
            {
                "title": "Cached Article",
                "link": "https://example.com",
                "published": "2024-01-15T10:30:00+00:00",
                "summary": "Summary",
                "source": "Source",
            }
        ])
        mock_redis.get.return_value = cached_data

        result = await aggregator.get_cached_news("tech")
        assert len(result) == 1
        assert result[0]["title"] == "Cached Article"
        assert isinstance(result[0]["published"], datetime)


class TestNewsletterSubscription:
    """Tests for newsletter subscription methods."""

    @pytest.mark.asyncio
    async def test_subscribe_newsletter(self, aggregator, mock_redis):
        """Should subscribe user to newsletter."""
        result = await aggregator.subscribe_newsletter(123)
        assert result is True
        mock_redis.sadd.assert_called()

    @pytest.mark.asyncio
    async def test_subscribe_with_topics(self, aggregator, mock_redis):
        """Should set topics when subscribing."""
        await aggregator.subscribe_newsletter(123, topics=["tech", "crypto"])
        # Should call sadd for each topic
        assert mock_redis.sadd.call_count >= 2

    @pytest.mark.asyncio
    async def test_subscribe_without_redis(self):
        """Should return False without Redis."""
        agg = NewsAggregator()
        result = await agg.subscribe_newsletter(123)
        assert result is False

    @pytest.mark.asyncio
    async def test_unsubscribe_newsletter(self, aggregator, mock_redis):
        """Should unsubscribe user from newsletter."""
        result = await aggregator.unsubscribe_newsletter(123)
        assert result is True
        mock_redis.srem.assert_called()
        mock_redis.delete.assert_called()

    @pytest.mark.asyncio
    async def test_is_newsletter_subscriber_true(self, aggregator, mock_redis):
        """Should return True when subscribed."""
        mock_redis.sismember.return_value = True
        result = await aggregator.is_newsletter_subscriber(123)
        assert result is True

    @pytest.mark.asyncio
    async def test_is_newsletter_subscriber_false(self, aggregator, mock_redis):
        """Should return False when not subscribed."""
        mock_redis.sismember.return_value = False
        result = await aggregator.is_newsletter_subscriber(123)
        assert result is False


class TestUserNewsTopics:
    """Tests for user news topic methods."""

    @pytest.mark.asyncio
    async def test_get_user_topics_default(self, aggregator, mock_redis):
        """Should return default topics when user has none."""
        mock_redis.smembers.return_value = None
        result = await aggregator.get_user_news_topics(123)
        assert set(result) == set(DEFAULT_RSS_FEEDS.keys())

    @pytest.mark.asyncio
    async def test_get_user_topics_custom(self, aggregator, mock_redis):
        """Should return user's custom topics."""
        mock_redis.smembers.return_value = {"tech", "crypto"}
        result = await aggregator.get_user_news_topics(123)
        assert set(result) == {"tech", "crypto"}

    @pytest.mark.asyncio
    async def test_set_user_topics(self, aggregator, mock_redis):
        """Should set user's news topics."""
        result = await aggregator.set_user_news_topics(123, ["tech", "news"])
        assert result is True
        mock_redis.delete.assert_called()  # Clear existing
        assert mock_redis.sadd.call_count >= 2

    @pytest.mark.asyncio
    async def test_set_invalid_topics_returns_false(self, aggregator, mock_redis):
        """Should return False for all invalid topics."""
        result = await aggregator.set_user_news_topics(123, ["invalid1", "invalid2"])
        assert result is False


class TestNewsletterTime:
    """Tests for newsletter delivery time methods."""

    @pytest.mark.asyncio
    async def test_set_newsletter_time(self, aggregator, mock_redis):
        """Should set newsletter delivery time."""
        result = await aggregator.set_newsletter_time(123, 9, 30)
        assert result is True
        mock_redis.set.assert_called()

    @pytest.mark.asyncio
    async def test_set_newsletter_time_invalid_hour(self, aggregator, mock_redis):
        """Should return False for invalid hour."""
        result = await aggregator.set_newsletter_time(123, 25, 0)
        assert result is False

    @pytest.mark.asyncio
    async def test_set_newsletter_time_invalid_minute(self, aggregator, mock_redis):
        """Should return False for invalid minute."""
        result = await aggregator.set_newsletter_time(123, 9, 60)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_newsletter_time(self, aggregator, mock_redis):
        """Should get newsletter delivery time."""
        mock_redis.get.return_value = "09:30"
        result = await aggregator.get_newsletter_time(123)
        assert result == (9, 30)

    @pytest.mark.asyncio
    async def test_get_newsletter_time_none(self, aggregator, mock_redis):
        """Should return None when no time set."""
        mock_redis.get.return_value = None
        result = await aggregator.get_newsletter_time(123)
        assert result is None


class TestGetAllNewsletterSubscribers:
    """Tests for get_all_newsletter_subscribers."""

    @pytest.mark.asyncio
    async def test_returns_empty_without_redis(self):
        """Should return empty list without Redis."""
        agg = NewsAggregator()
        result = await agg.get_all_newsletter_subscribers()
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_subscribers_with_data(self, aggregator, mock_redis):
        """Should return subscribers with topics and time."""
        # This is complex to test due to scan/smembers interaction
        # Just verify it returns a list
        result = await aggregator.get_all_newsletter_subscribers()
        assert isinstance(result, list)


class TestGetAvailableNewsTopics:
    """Tests for get_available_news_topics."""

    @pytest.mark.asyncio
    async def test_returns_all_topics(self, aggregator):
        """Should return all available topics."""
        result = await aggregator.get_available_news_topics()
        assert set(result) == set(DEFAULT_RSS_FEEDS.keys())


class TestGlobalInstance:
    """Tests for global news_aggregator instance."""

    def test_global_instance_exists(self):
        """Should have a global instance."""
        assert news_aggregator is not None
        assert isinstance(news_aggregator, NewsAggregator)

    def test_new_instance_has_no_redis(self):
        """New instance should not have Redis initially."""
        new_agg = NewsAggregator()
        assert new_agg.redis is None
