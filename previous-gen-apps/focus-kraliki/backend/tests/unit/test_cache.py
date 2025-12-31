"""
Unit tests for Cache Manager
Tests Redis caching operations, flow memory, and AI response caching
"""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import timedelta

from app.core.cache import CacheManager, FlowMemory


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = AsyncMock()
    redis_mock.from_url = MagicMock(return_value=redis_mock)
    return redis_mock


@pytest.fixture
def cache_manager(mock_redis):
    """Create cache manager with mocked Redis"""
    with patch("app.core.cache.settings.REDIS_URL", "redis://localhost:6379"):
        manager = CacheManager()
        manager._redis = mock_redis
        manager._loop_id = id(__import__("asyncio").get_event_loop())
        return manager


class TestCacheManager:
    """Tests for CacheManager class"""

    @pytest.mark.asyncio
    async def test_get_redis_creates_connection(self, cache_manager):
        """Test get_redis creates new connection"""
        with patch("app.core.cache.redis.asyncio.from_url") as mock_from_url:
            mock_redis_instance = AsyncMock()
            mock_from_url.return_value = mock_redis_instance

            result = await cache_manager.get_redis()

            assert result == mock_redis_instance
            mock_from_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_redis_reuses_connection(self, cache_manager, mock_redis):
        """Test get_redis reuses existing connection"""
        cache_manager._redis = mock_redis
        cache_manager._loop_id = id(__import__("asyncio").get_event_loop())

        result = await cache_manager.get_redis()

        assert result == mock_redis

    @pytest.mark.asyncio
    async def test_close_redis_connection(self, cache_manager):
        """Test close method"""
        cache_manager._redis = AsyncMock()

        await cache_manager.close()

        cache_manager._redis.close.assert_called_once()
        assert cache_manager._redis is None

    @pytest.mark.asyncio
    async def test_context_manager(self, cache_manager):
        """Test async context manager"""
        cache_manager._redis = AsyncMock()

        async with cache_manager:
            pass

        cache_manager._redis.close.assert_called_once()

    def test_generate_key_with_dict(self, cache_manager):
        """Test key generation with dict"""
        data = {"key1": "value1", "key2": "value2"}
        key = cache_manager._generate_key("prefix", data)

        assert key.startswith("prefix:")
        assert ":" in key

    def test_generate_key_with_string(self, cache_manager):
        """Test key generation with string"""
        key = cache_manager._generate_key("prefix", "data")

        assert key.startswith("prefix:")
        assert ":" in key

    @pytest.mark.asyncio
    async def test_get_cached_value(self, cache_manager, mock_redis):
        """Test get retrieves and deserializes cached value"""
        test_value = {"response": "test"}
        mock_redis.get.return_value = json.dumps(test_value)

        result = await cache_manager.get("key")

        assert result == test_value
        mock_redis.get.assert_called_once_with("key")

    @pytest.mark.asyncio
    async def test_get_returns_none_for_miss(self, cache_manager, mock_redis):
        """Test get returns None for cache miss"""
        mock_redis.get.return_value = None

        result = await cache_manager.get("key")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_handles_error(self, cache_manager, mock_redis):
        """Test get handles Redis errors gracefully"""
        mock_redis.get.side_effect = Exception("Redis error")

        result = await cache_manager.get("key")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_cached_value(self, cache_manager, mock_redis):
        """Test set stores value with TTL"""
        value = {"response": "test"}

        result = await cache_manager.set("key", value, ttl=100)

        assert result is True
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "key"
        assert call_args[0][2] == json.dumps(value)

    @pytest.mark.asyncio
    async def test_set_handles_error(self, cache_manager, mock_redis):
        """Test set handles Redis errors gracefully"""
        mock_redis.setex.side_effect = Exception("Redis error")

        result = await cache_manager.set("key", "value")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_key(self, cache_manager, mock_redis):
        """Test delete removes key"""
        result = await cache_manager.delete("key")

        assert result is True
        mock_redis.delete.assert_called_once_with("key")

    @pytest.mark.asyncio
    async def test_delete_handles_error(self, cache_manager, mock_redis):
        """Test delete handles Redis errors gracefully"""
        mock_redis.delete.side_effect = Exception("Redis error")

        result = await cache_manager.delete("key")

        assert result is False

    @pytest.mark.asyncio
    async def test_get_ai_response(self, cache_manager, mock_redis):
        """Test get_ai_response retrieves cached AI response"""
        cached_data = {"response": "AI response", "model": "gpt-4"}
        mock_redis.get.return_value = json.dumps(cached_data)

        result = await cache_manager.get_ai_response("gpt-4", "test prompt")

        assert result == "AI response"

    @pytest.mark.asyncio
    async def test_cache_ai_response(self, cache_manager, mock_redis):
        """Test cache_ai_response stores AI response"""
        result = await cache_manager.cache_ai_response(
            "gpt-4", "test prompt", "AI response"
        )

        assert result is True
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_ai_response_with_context(self, cache_manager, mock_redis):
        """Test cache_ai_response stores context"""
        context = {"user_id": "123"}
        result = await cache_manager.cache_ai_response(
            "gpt-4", "test prompt", "AI response", context=context
        )

        assert result is True
        mock_redis.setex.assert_called_once()


class TestFlowMemory:
    """Tests for FlowMemory class"""

    @pytest.fixture
    def flow_memory(self, cache_manager):
        """Create flow memory with mocked cache"""
        return FlowMemory(cache_manager)

    @pytest.mark.asyncio
    async def test_save_context(self, flow_memory, cache_manager):
        """Test save_context stores session context"""
        context = {"user_id": "123", "page": "tasks"}

        result = await flow_memory.save_context("user-123", "session-1", context)

        assert result is True
        cache_manager.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_context(self, flow_memory, cache_manager):
        """Test get_context retrieves session context"""
        context = {"user_id": "123", "page": "tasks"}
        cache_manager.get.return_value = context

        result = await flow_memory.get_context("user-123", "session-1")

        assert result == context

    @pytest.mark.asyncio
    async def test_get_context_returns_none_for_miss(self, flow_memory, cache_manager):
        """Test get_context returns None for missing context"""
        cache_manager.get.return_value = None

        result = await flow_memory.get_context("user-123", "session-1")

        assert result is None

    @pytest.mark.asyncio
    async def test_update_context(self, flow_memory, cache_manager):
        """Test update_context merges new values"""
        existing_context = {"user_id": "123", "page": "tasks"}
        cache_manager.get.return_value = existing_context

        result = await flow_memory.update_context(
            "user-123", "session-1", {"page": "projects"}
        )

        assert result is True
        cache_manager.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_context_creates_new(self, flow_memory, cache_manager):
        """Test update_context creates new context if none exists"""
        cache_manager.get.return_value = None

        result = await flow_memory.update_context(
            "user-123", "session-1", {"page": "tasks"}
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_save_memory(self, flow_memory, cache_manager):
        """Test save_memory stores long-term memory"""
        result = await flow_memory.save_memory("user-123", "preference", "dark_mode")

        assert result is True
        cache_manager.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_memory_with_custom_ttl(self, flow_memory, cache_manager):
        """Test save_memory with custom TTL"""
        result = await flow_memory.save_memory("user-123", "temp", "value", ttl=300)

        assert result is True
        cache_manager.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_recall_memory(self, flow_memory, cache_manager):
        """Test recall_memory retrieves stored memory"""
        cache_manager.get.return_value = "dark_mode"

        result = await flow_memory.recall_memory("user-123", "preference")

        assert result == "dark_mode"

    @pytest.mark.asyncio
    async def test_recall_memory_returns_none_for_miss(
        self, flow_memory, cache_manager
    ):
        """Test recall_memory returns None for missing memory"""
        cache_manager.get.return_value = None

        result = await flow_memory.recall_memory("user-123", "preference")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_recent_interactions(self, flow_memory, cache_manager):
        """Test get_recent_interactions returns recent history"""
        interactions = [
            {"type": "chat", "timestamp": "2024-01-01"},
            {"type": "task", "timestamp": "2024-01-02"},
        ]
        cache_manager.get.return_value = interactions

        result = await flow_memory.get_recent_interactions("user-123", limit=10)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_recent_interactions_with_limit(self, flow_memory, cache_manager):
        """Test get_recent_interactions respects limit"""
        interactions = [{"type": f"action_{i}"} for i in range(20)]
        cache_manager.get.return_value = interactions

        result = await flow_memory.get_recent_interactions("user-123", limit=5)

        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_add_interaction(self, flow_memory, cache_manager):
        """Test add_interaction appends to history"""
        cache_manager.get.return_value = []

        result = await flow_memory.add_interaction("user-123", {"type": "chat"})

        assert result is True
        cache_manager.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_interaction_keeps_last_100(self, flow_memory, cache_manager):
        """Test add_interaction limits to 100 interactions"""
        existing = [{"type": f"action_{i}"} for i in range(100)]
        cache_manager.get.return_value = existing

        result = await flow_memory.add_interaction("user-123", {"type": "new_action"})

        assert result is True
        call_args = cache_manager.set.call_args
        stored_interactions = call_args[0][1]
        assert len(stored_interactions) == 100
