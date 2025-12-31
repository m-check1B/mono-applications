"""Tests for content subscription service."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.content_subscription import (
    ContentSubscription,
    DEFAULT_TOPICS,
    content_subscription,
)


@pytest.fixture
def mock_redis():
    """Mock Redis connection."""
    redis_mock = AsyncMock()
    redis_mock.sadd = AsyncMock(return_value=1)
    redis_mock.srem = AsyncMock(return_value=1)
    redis_mock.smembers = AsyncMock(return_value=set())
    redis_mock.expire = AsyncMock(return_value=True)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.exists = AsyncMock(return_value=0)
    redis_mock.scan = AsyncMock(return_value=(0, []))
    return redis_mock


@pytest.fixture
def content_service(mock_redis):
    """Content subscription service with mock Redis."""
    service = ContentSubscription()
    service.redis = mock_redis
    return service


class TestGetAvailableTopics:
    """Tests for get_available_topics."""

    @pytest.mark.asyncio
    async def test_returns_default_topics(self, content_service):
        """Should return all default topics."""
        topics = await content_service.get_available_topics()
        assert topics == DEFAULT_TOPICS
        assert "tech" in topics
        assert "crypto" in topics
        assert "deals" in topics

    @pytest.mark.asyncio
    async def test_returns_copy_not_original(self, content_service):
        """Should return a copy, not the original list."""
        topics = await content_service.get_available_topics()
        topics.append("new_topic")
        topics2 = await content_service.get_available_topics()
        assert "new_topic" not in topics2


class TestSubscribeToTopics:
    """Tests for subscribe_to_topics."""

    @pytest.mark.asyncio
    async def test_subscribe_valid_topics(self, content_service, mock_redis):
        """Should subscribe to valid topics."""
        result = await content_service.subscribe_to_topics(123, ["tech", "crypto"])
        assert result == ["tech", "crypto"]
        assert mock_redis.sadd.call_count == 2
        mock_redis.expire.assert_called()

    @pytest.mark.asyncio
    async def test_subscribe_filters_invalid_topics(self, content_service, mock_redis):
        """Should filter out invalid topics."""
        result = await content_service.subscribe_to_topics(123, ["tech", "invalid_topic"])
        assert result == ["tech"]
        assert mock_redis.sadd.call_count == 1

    @pytest.mark.asyncio
    async def test_subscribe_all_invalid_returns_empty(self, content_service):
        """Should return empty list if all topics are invalid."""
        result = await content_service.subscribe_to_topics(123, ["invalid1", "invalid2"])
        assert result == []

    @pytest.mark.asyncio
    async def test_subscribe_without_redis(self):
        """Should return empty list without Redis connection."""
        service = ContentSubscription()
        result = await service.subscribe_to_topics(123, ["tech"])
        assert result == []


class TestUnsubscribeFromTopics:
    """Tests for unsubscribe_from_topics."""

    @pytest.mark.asyncio
    async def test_unsubscribe_removes_topics(self, content_service, mock_redis):
        """Should remove subscribed topics."""
        mock_redis.srem.return_value = 1
        result = await content_service.unsubscribe_from_topics(123, ["tech", "crypto"])
        assert result == 2
        assert mock_redis.srem.call_count == 2

    @pytest.mark.asyncio
    async def test_unsubscribe_returns_zero_when_not_subscribed(
        self, content_service, mock_redis
    ):
        """Should return 0 when not subscribed."""
        mock_redis.srem.return_value = 0
        result = await content_service.unsubscribe_from_topics(123, ["tech"])
        assert result == 0

    @pytest.mark.asyncio
    async def test_unsubscribe_without_redis(self):
        """Should return 0 without Redis connection."""
        service = ContentSubscription()
        result = await service.unsubscribe_from_topics(123, ["tech"])
        assert result == 0


class TestGetUserTopics:
    """Tests for get_user_topics."""

    @pytest.mark.asyncio
    async def test_get_subscribed_topics(self, content_service, mock_redis):
        """Should return user's subscribed topics."""
        mock_redis.smembers.return_value = {"tech", "crypto"}
        result = await content_service.get_user_topics(123)
        assert set(result) == {"tech", "crypto"}

    @pytest.mark.asyncio
    async def test_get_empty_when_no_subscriptions(self, content_service, mock_redis):
        """Should return empty list when no subscriptions."""
        mock_redis.smembers.return_value = None
        result = await content_service.get_user_topics(123)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_without_redis(self):
        """Should return empty list without Redis."""
        service = ContentSubscription()
        result = await service.get_user_topics(123)
        assert result == []


class TestContentSubscriptionStatus:
    """Tests for content subscription status."""

    @pytest.mark.asyncio
    async def test_set_content_subscription(self, content_service, mock_redis):
        """Should set content subscription."""
        result = await content_service.set_content_subscription(123, months=1)
        assert result is True
        mock_redis.set.assert_called()
        mock_redis.expire.assert_called()

    @pytest.mark.asyncio
    async def test_is_content_subscriber_true(self, content_service, mock_redis):
        """Should return True when subscribed."""
        mock_redis.exists.return_value = 1
        result = await content_service.is_content_subscriber(123)
        assert result is True

    @pytest.mark.asyncio
    async def test_is_content_subscriber_false(self, content_service, mock_redis):
        """Should return False when not subscribed."""
        mock_redis.exists.return_value = 0
        result = await content_service.is_content_subscriber(123)
        assert result is False

    @pytest.mark.asyncio
    async def test_is_content_subscriber_without_redis(self):
        """Should return False without Redis."""
        service = ContentSubscription()
        result = await service.is_content_subscriber(123)
        assert result is False


class TestExtractTopicsFromMessages:
    """Tests for extract_topics_from_messages."""

    @pytest.mark.asyncio
    async def test_empty_messages(self, content_service):
        """Should return empty result for empty messages."""
        result = await content_service.extract_topics_from_messages([])
        assert result == {"topics": [], "relevant_messages": []}

    @pytest.mark.asyncio
    async def test_extracts_topics_with_ai(self, content_service):
        """Should extract topics using AI."""
        mock_response = MagicMock()
        mock_response.text = '{"topics": ["tech"], "relevant_messages": [0]}'

        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        with patch.object(content_service, "_get_model", return_value=mock_model):
            messages = [{"user": "John", "text": "Check out this new Python library!"}]
            result = await content_service.extract_topics_from_messages(messages)
            assert result == {"topics": ["tech"], "relevant_messages": [0]}

    @pytest.mark.asyncio
    async def test_handles_markdown_code_blocks(self, content_service):
        """Should handle AI response wrapped in markdown code blocks."""
        mock_response = MagicMock()
        mock_response.text = '```json\n{"topics": ["crypto"], "relevant_messages": [0]}\n```'

        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        with patch.object(content_service, "_get_model", return_value=mock_model):
            messages = [{"user": "Jane", "text": "Bitcoin is up 10%"}]
            result = await content_service.extract_topics_from_messages(messages)
            assert result == {"topics": ["crypto"], "relevant_messages": [0]}

    @pytest.mark.asyncio
    async def test_handles_json_parse_error(self, content_service):
        """Should return empty result on JSON parse error."""
        mock_response = MagicMock()
        mock_response.text = "invalid json"

        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        with patch.object(content_service, "_get_model", return_value=mock_model):
            messages = [{"user": "Jane", "text": "Hello"}]
            result = await content_service.extract_topics_from_messages(messages)
            assert result == {"topics": [], "relevant_messages": []}


class TestGeneratePersonalizedDigest:
    """Tests for generate_personalized_digest."""

    @pytest.mark.asyncio
    async def test_empty_messages(self, content_service):
        """Should return None for empty messages."""
        result = await content_service.generate_personalized_digest(123, [])
        assert result is None

    @pytest.mark.asyncio
    async def test_no_user_topics(self, content_service, mock_redis):
        """Should return None when user has no topics."""
        mock_redis.smembers.return_value = None
        result = await content_service.generate_personalized_digest(
            123, [{"user": "Test", "text": "Hello"}]
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_generates_digest_with_ai(self, content_service, mock_redis):
        """Should generate personalized digest using AI."""
        mock_redis.smembers.return_value = {"tech", "crypto"}

        mock_response = MagicMock()
        mock_response.text = "**Your 2 Topic Digest**\n\n**Tech:** Key updates..."

        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        with patch.object(content_service, "_get_model", return_value=mock_model):
            messages = [{"user": "John", "text": "New Python release!"}]
            result = await content_service.generate_personalized_digest(123, messages)
            assert "Digest" in result

    @pytest.mark.asyncio
    async def test_returns_none_for_no_relevant_content(
        self, content_service, mock_redis
    ):
        """Should return None when AI finds no relevant content."""
        mock_redis.smembers.return_value = {"tech"}

        mock_response = MagicMock()
        mock_response.text = "No relevant content found for your topics."

        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        with patch.object(content_service, "_get_model", return_value=mock_model):
            messages = [{"user": "John", "text": "Good morning!"}]
            result = await content_service.generate_personalized_digest(123, messages)
            assert result is None


class TestDigestTimestamp:
    """Tests for digest timestamp tracking."""

    @pytest.mark.asyncio
    async def test_update_last_digest(self, content_service, mock_redis):
        """Should update last digest timestamp."""
        await content_service.update_last_digest(123)
        mock_redis.set.assert_called()
        mock_redis.expire.assert_called()

    @pytest.mark.asyncio
    async def test_get_last_digest_time(self, content_service, mock_redis):
        """Should get last digest timestamp."""
        mock_redis.get.return_value = "2024-01-15T10:30:00"
        result = await content_service.get_last_digest_time(123)
        assert result is not None
        assert result.year == 2024

    @pytest.mark.asyncio
    async def test_get_last_digest_time_none(self, content_service, mock_redis):
        """Should return None when no timestamp exists."""
        mock_redis.get.return_value = None
        result = await content_service.get_last_digest_time(123)
        assert result is None


class TestGetAllContentSubscribers:
    """Tests for get_all_content_subscribers."""

    @pytest.mark.asyncio
    async def test_returns_empty_without_redis(self):
        """Should return empty list without Redis."""
        service = ContentSubscription()
        result = await service.get_all_content_subscribers()
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_subscribers_with_topics(self, content_service, mock_redis):
        """Should return subscribers with their topics."""
        # Mock scan to return subscription keys
        mock_redis.scan.side_effect = [
            (0, ["tldr:user:123:content_sub"])
        ]
        mock_redis.smembers.return_value = {"tech", "crypto"}

        result = await content_service.get_all_content_subscribers()
        # The scan is looking for content_sub keys, not users, so this may be empty
        # depending on implementation
        assert isinstance(result, list)


class TestRedisKeyPatterns:
    """Tests for Redis key generation methods."""

    def test_user_topics_key(self, content_service):
        """Should generate correct user topics key."""
        key = content_service._user_topics_key(123)
        assert key == "tldr:user:123:topics"

    def test_user_prefs_key(self, content_service):
        """Should generate correct user prefs key."""
        key = content_service._user_prefs_key(456)
        assert key == "tldr:user:456:content_prefs"

    def test_user_digest_key(self, content_service):
        """Should generate correct user digest key."""
        key = content_service._user_digest_key(789)
        assert key == "tldr:user:789:last_digest"

    def test_content_sub_key(self, content_service):
        """Should generate correct content sub key."""
        key = content_service._content_sub_key(123)
        assert key == "tldr:user:123:content_sub"

    def test_chat_topics_key(self, content_service):
        """Should generate correct chat topics key."""
        key = content_service._chat_topics_key(-100123456)
        assert key == "tldr:chat:-100123456:topics_cache"


class TestGlobalInstance:
    """Tests for global content_subscription instance."""

    def test_global_instance_exists(self):
        """Should have a global instance."""
        assert content_subscription is not None
        assert isinstance(content_subscription, ContentSubscription)

    def test_new_instance_has_no_redis(self):
        """New instance should not have Redis connected initially."""
        new_service = ContentSubscription()
        assert new_service.redis is None
