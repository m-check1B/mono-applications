"""Tests for persistent storage (Postgres + Redis hybrid)."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
class TestHybridPersistence:
    """Tests for hybrid storage (Redis cache + Postgres primary)."""

    @pytest.fixture
    def mock_redis(self):
        return AsyncMock()

    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        return session

    @pytest.fixture
    def storage(self, mock_redis):
        from app.services.storage import BotStorage
        storage = BotStorage()
        storage.redis = mock_redis
        return storage

    async def test_get_user_from_cache(self, storage, mock_redis):
        """Should return user from Redis if available."""
        import json
        user_data = {
            "user_id": 12345,
            "premium": True,
            "birth_date": datetime(1990, 1, 1).isoformat()
        }
        mock_redis.get.return_value = json.dumps(user_data)

        user = await storage.get_user(12345)

        assert user["user_id"] == 12345
        assert user["premium"] is True
        assert isinstance(user["birth_date"], datetime)
        mock_redis.get.assert_called_with("sense-kraliki:user:12345:profile")

    @patch("app.services.storage.get_session_factory")
    async def test_get_user_from_postgres_and_update_cache(self, mock_get_session_factory, storage, mock_redis):
        """Should fetch from Postgres if not in cache, then update cache."""
        # 1. Cache miss
        mock_redis.get.return_value = None

        # 2. Mock Postgres result
        mock_user_obj = MagicMock()
        mock_user_obj.to_dict.return_value = {
            "user_id": 12345,
            "premium": False,
            "birth_date": datetime(1990, 1, 1)
        }

        session = AsyncMock()
        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__.return_value = session
        mock_get_session_factory.return_value = mock_session_factory

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user_obj
        session.execute.return_value = mock_result

        # 3. Call get_user
        user = await storage.get_user(12345)

        # 4. Verify
        assert user["user_id"] == 12345
        assert mock_redis.set.called # Should update cache
        
    @patch("app.services.storage.get_session_factory")
    async def test_update_user_updates_both(self, mock_get_session_factory, storage, mock_redis):
        """Should update Postgres and then Redis cache."""
        session = AsyncMock()
        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__.return_value = session
        mock_get_session_factory.return_value = mock_session_factory

        mock_user_obj = MagicMock()
        mock_user_obj.to_dict.return_value = {"user_id": 12345, "premium": True}

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user_obj
        session.execute.return_value = mock_result

        await storage.update_user(12345, {"premium": True})

        assert session.commit.called
        assert mock_redis.set.called
