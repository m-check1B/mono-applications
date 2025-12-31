"""
Targeted tests to improve coverage for Caching system
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import json

from app.core.cache import CacheManager, FlowMemory

@pytest.fixture
def mock_redis():
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.setex = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=True)
    mock.close = AsyncMock()
    return mock

@pytest.mark.asyncio
async def test_cache_manager_logic(mock_redis):
    """Test CacheManager operations"""
    with patch("app.core.cache.redis.from_url", return_value=mock_redis), \
         patch("asyncio.get_running_loop", return_value=MagicMock()):
        
        manager = CacheManager()
        
        # Test set
        await manager.set("key1", {"a": 1})
        mock_redis.setex.assert_called_with("key1", 3600, json.dumps({"a": 1}))
        
        # Test get
        mock_redis.get.return_value = json.dumps({"a": 1})
        val = await manager.get("key1")
        assert val == {"a": 1}
        
        # Test delete
        await manager.delete("key1")
        mock_redis.delete.assert_called_with("key1")

@pytest.mark.asyncio
async def test_cache_ai_response_logic(mock_redis):
    """Test AI response caching logic"""
    with patch("app.core.cache.redis.from_url", return_value=mock_redis), \
         patch("asyncio.get_running_loop", return_value=MagicMock()):
        
        manager = CacheManager()
        
        # Cache response
        await manager.cache_ai_response("model1", "prompt1", "response1", context={"c": 1})
        assert mock_redis.setex.called
        
        # Get cached response
        mock_redis.get.return_value = json.dumps({"response": "response1"})
        cached = await manager.get_ai_response("model1", "prompt1", context={"c": 1})
        assert cached == "response1"

@pytest.mark.asyncio
async def test_flow_memory_logic(mock_redis):
    """Test FlowMemory operations"""
    with patch("app.core.cache.redis.from_url", return_value=mock_redis), \
         patch("asyncio.get_running_loop", return_value=MagicMock()):
        
        manager = CacheManager()
        fm = FlowMemory(manager)
        
        # Save context
        await fm.save_context("u1", "s1", {"state": "init"})
        assert mock_redis.setex.called
        
        # Get context
        mock_redis.get.return_value = json.dumps({"state": "init"})
        ctx = await fm.get_context("u1", "s1")
        assert ctx == {"state": "init"}
        
        # Update context
        await fm.update_context("u1", "s1", {"new": "data"})
        assert mock_redis.setex.called
        
        # Recall memory
        await fm.recall_memory("u1", "k1")
        mock_redis.get.assert_called()
        
        # Add interaction
        mock_redis.get.return_value = None
        await fm.add_interaction("u1", {"msg": "hi"})
        assert mock_redis.setex.called