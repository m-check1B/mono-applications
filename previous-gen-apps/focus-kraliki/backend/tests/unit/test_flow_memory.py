"""
Unit tests for FlowMemoryService - Redis-based conversational memory system
Tests interaction storage, context retrieval, pattern extraction, and session management
"""
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.flow_memory import FlowMemoryService


class MockRedis:
    """Mock Redis client for testing FlowMemoryService"""
    
    def __init__(self):
        self.data = {}
    
    async def get(self, key: str):
        return self.data.get(key)
    
    async def setex(self, key: str, ttl: int, value: str):
        self.data[key] = value
    
    async def delete(self, key: str):
        self.data.pop(key, None)
    
    async def scan_iter(self, match: str = None):
        """Async generator for scan_iter"""
        for key in list(self.data.keys()):
            if match:
                pattern = match.replace('*', '')
                if pattern in key:
                    yield key
            else:
                yield key


@pytest.fixture
def mock_redis():
    """Provide mock Redis client"""
    return MockRedis()


@pytest.fixture
def flow_memory_service(mock_redis):
    """Provide FlowMemoryService with mock Redis"""
    return FlowMemoryService(mock_redis)


class TestStoreInteraction:
    """Test interaction storage"""

    @pytest.mark.asyncio
    async def test_store_first_interaction(self, flow_memory_service, mock_redis):
        """First interaction should create new memory structure"""
        user_id = "test-user-123"
        interaction = {
            "user_message": "Hello AI",
            "ai_response": "Hello! How can I help?"
        }
        
        result = await flow_memory_service.store_interaction(user_id, interaction)
        
        assert result == True
        memory_key = f"user:{user_id}:memory"
        assert memory_key in mock_redis.data
        
        memory = json.loads(mock_redis.data[memory_key])
        assert len(memory["interactions"]) == 1
        assert memory["interactions"][0]["user_message"] == "Hello AI"

    @pytest.mark.asyncio
    async def test_store_adds_timestamp(self, flow_memory_service, mock_redis):
        """Interaction without timestamp should get one added"""
        user_id = "test-user-123"
        interaction = {
            "user_message": "Test message"
        }
        
        await flow_memory_service.store_interaction(user_id, interaction)
        
        memory_key = f"user:{user_id}:memory"
        memory = json.loads(mock_redis.data[memory_key])
        
        assert "timestamp" in memory["interactions"][0]

    @pytest.mark.asyncio
    async def test_store_with_session_id(self, flow_memory_service, mock_redis):
        """Interaction with session_id should update session data"""
        user_id = "test-user-123"
        session_id = "session-456"
        interaction = {
            "user_message": "Session message"
        }
        
        await flow_memory_service.store_interaction(user_id, interaction, session_id)
        
        # Check session was created
        session_key = f"user:{user_id}:session:{session_id}"
        assert session_key in mock_redis.data
        
        session = json.loads(mock_redis.data[session_key])
        assert session["session_id"] == session_id
        assert len(session["interactions"]) == 1

    @pytest.mark.asyncio
    async def test_store_truncates_old_interactions(self, flow_memory_service, mock_redis):
        """Should keep only last N interactions"""
        user_id = "test-user-123"
        flow_memory_service.max_interactions = 5
        
        # Store 10 interactions
        for i in range(10):
            await flow_memory_service.store_interaction(
                user_id, 
                {"user_message": f"Message {i}"}
            )
        
        memory_key = f"user:{user_id}:memory"
        memory = json.loads(mock_redis.data[memory_key])
        
        # Should only have last 5
        assert len(memory["interactions"]) == 5
        assert memory["interactions"][0]["user_message"] == "Message 5"
        assert memory["interactions"][-1]["user_message"] == "Message 9"

    @pytest.mark.asyncio
    async def test_store_extracts_patterns(self, flow_memory_service, mock_redis):
        """Storing interactions should extract patterns"""
        user_id = "test-user-123"
        
        # Store interactions with questions
        await flow_memory_service.store_interaction(
            user_id,
            {"user_message": "What is Python?", "timestamp": datetime.utcnow().isoformat()}
        )
        await flow_memory_service.store_interaction(
            user_id,
            {"user_message": "How do I create a task?", "timestamp": datetime.utcnow().isoformat()}
        )
        
        memory_key = f"user:{user_id}:memory"
        memory = json.loads(mock_redis.data[memory_key])
        
        assert "patterns" in memory
        # Should detect question intent
        assert memory["patterns"].get("intent_patterns", {}).get("question", 0) >= 2


class TestRetrieveContext:
    """Test context retrieval"""

    @pytest.mark.asyncio
    async def test_retrieve_empty_memory(self, flow_memory_service):
        """Empty memory should return default structure"""
        result = await flow_memory_service.retrieve_context("nonexistent-user")
        
        assert result["interactions"] == []
        assert result["patterns"] == {}
        assert result["insights"] == []
        assert result["context_summary"] is None

    @pytest.mark.asyncio
    async def test_retrieve_with_limit(self, flow_memory_service, mock_redis):
        """Should respect limit parameter"""
        user_id = "test-user-123"
        
        # Store 10 interactions
        for i in range(10):
            await flow_memory_service.store_interaction(
                user_id,
                {"user_message": f"Message {i}"}
            )
        
        # Retrieve with limit of 3
        result = await flow_memory_service.retrieve_context(user_id, limit=3)
        
        assert len(result["interactions"]) == 3

    @pytest.mark.asyncio
    async def test_retrieve_with_query_filter(self, flow_memory_service, mock_redis):
        """Should filter interactions by query relevance"""
        user_id = "test-user-123"
        
        # Store diverse interactions
        await flow_memory_service.store_interaction(
            user_id,
            {"user_message": "Tell me about Python programming"}
        )
        await flow_memory_service.store_interaction(
            user_id,
            {"user_message": "What's the weather today?"}
        )
        await flow_memory_service.store_interaction(
            user_id,
            {"user_message": "How do I write Python code?"}
        )
        
        # Query for Python-related content
        result = await flow_memory_service.retrieve_context(
            user_id, 
            query="Python programming",
            limit=10
        )
        
        # Should return Python-related interactions first
        assert len(result["interactions"]) >= 2

    @pytest.mark.asyncio
    async def test_retrieve_includes_compressed_context(self, flow_memory_service, mock_redis):
        """Should include compressed context if available"""
        user_id = "test-user-123"
        
        # Store compressed context
        await flow_memory_service.compress_and_store_context(
            user_id,
            "User prefers Python programming and task management"
        )
        
        # Store an interaction
        await flow_memory_service.store_interaction(
            user_id,
            {"user_message": "Test message"}
        )
        
        result = await flow_memory_service.retrieve_context(user_id)
        
        assert result["context_summary"] == "User prefers Python programming and task management"


class TestExtractPatterns:
    """Test pattern extraction"""

    @pytest.mark.asyncio
    async def test_extract_empty_interactions(self, flow_memory_service):
        """Empty interactions should return empty patterns"""
        patterns = await flow_memory_service._extract_patterns([])
        assert patterns == {}

    @pytest.mark.asyncio
    async def test_extract_topics(self, flow_memory_service):
        """Should extract topic keywords from messages"""
        interactions = [
            {"user_message": "Python programming is fun"},
            {"user_message": "Python tasks are easy"},
            {"user_message": "Programming helps productivity"}
        ]
        
        patterns = await flow_memory_service._extract_patterns(interactions)
        
        assert "topics" in patterns
        assert "python" in patterns["topics"]
        assert "programming" in patterns["topics"]

    @pytest.mark.asyncio
    async def test_extract_intent_question(self, flow_memory_service):
        """Should detect question intent"""
        interactions = [
            {"user_message": "What is Python?"},
            {"user_message": "How does this work?"},
            {"user_message": "Why is the sky blue?"}
        ]
        
        patterns = await flow_memory_service._extract_patterns(interactions)
        
        assert patterns["intent_patterns"]["question"] == 3

    @pytest.mark.asyncio
    async def test_extract_intent_command(self, flow_memory_service):
        """Should detect command intent"""
        interactions = [
            {"user_message": "Create a new task"},
            {"user_message": "Add this to my list"},
            {"user_message": "Make a project"}
        ]
        
        patterns = await flow_memory_service._extract_patterns(interactions)
        
        assert patterns["intent_patterns"]["command"] == 3

    @pytest.mark.asyncio
    async def test_extract_time_patterns(self, flow_memory_service):
        """Should extract time patterns from timestamps"""
        interactions = [
            {"user_message": "Morning message", "timestamp": "2025-01-01T10:00:00"},
            {"user_message": "Another morning", "timestamp": "2025-01-02T10:00:00"},
            {"user_message": "Afternoon message", "timestamp": "2025-01-01T14:00:00"}
        ]
        
        patterns = await flow_memory_service._extract_patterns(interactions)
        
        assert "time_patterns" in patterns
        assert "most_active_hour" in patterns["time_patterns"]
        # Hour 10 appears twice, should be most active
        assert patterns["time_patterns"]["most_active_hour"] == 10


class TestSessionManagement:
    """Test session management"""

    @pytest.mark.asyncio
    async def test_update_session(self, flow_memory_service, mock_redis):
        """Should update session data"""
        user_id = "test-user-123"
        session_id = "session-456"
        
        await flow_memory_service._update_session(
            user_id,
            session_id,
            {"user_message": "Session message"}
        )
        
        session_key = f"user:{user_id}:session:{session_id}"
        assert session_key in mock_redis.data
        
        session = json.loads(mock_redis.data[session_key])
        assert session["session_id"] == session_id
        assert "started_at" in session
        assert "last_activity" in session

    @pytest.mark.asyncio
    async def test_get_session(self, flow_memory_service, mock_redis):
        """Should retrieve session data"""
        user_id = "test-user-123"
        session_id = "session-456"
        
        # Create session
        await flow_memory_service._update_session(
            user_id,
            session_id,
            {"user_message": "Test"}
        )
        
        # Retrieve session
        session = await flow_memory_service.get_session(user_id, session_id)
        
        assert session is not None
        assert session["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, flow_memory_service):
        """Non-existent session should return None"""
        session = await flow_memory_service.get_session("user", "nonexistent")
        assert session is None


class TestMemoryOperations:
    """Test memory operations"""

    @pytest.mark.asyncio
    async def test_compress_and_store_context(self, flow_memory_service, mock_redis):
        """Should store compressed context"""
        user_id = "test-user-123"
        summary = "User prefers morning work sessions and Python programming"
        
        result = await flow_memory_service.compress_and_store_context(user_id, summary)
        
        assert result == True
        context_key = f"user:{user_id}:context"
        assert context_key in mock_redis.data
        
        context = json.loads(mock_redis.data[context_key])
        assert context["summary"] == summary
        assert "created_at" in context

    @pytest.mark.asyncio
    async def test_clear_memory(self, flow_memory_service, mock_redis):
        """Should clear all user memory"""
        user_id = "test-user-123"
        
        # Create memory and context
        await flow_memory_service.store_interaction(
            user_id,
            {"user_message": "Test"}
        )
        await flow_memory_service.compress_and_store_context(
            user_id,
            "Test context"
        )
        await flow_memory_service._update_session(
            user_id,
            "session-1",
            {"user_message": "Test"}
        )
        
        # Verify data exists
        memory_key = f"user:{user_id}:memory"
        context_key = f"user:{user_id}:context"
        assert memory_key in mock_redis.data
        assert context_key in mock_redis.data
        
        # Clear memory
        result = await flow_memory_service.clear_memory(user_id)
        
        assert result == True
        assert memory_key not in mock_redis.data
        assert context_key not in mock_redis.data

    @pytest.mark.asyncio
    async def test_get_memory_stats_no_data(self, flow_memory_service):
        """No data should return empty stats"""
        stats = await flow_memory_service.get_memory_stats("nonexistent-user")
        
        assert stats["total_interactions"] == 0
        assert stats["memory_exists"] == False

    @pytest.mark.asyncio
    async def test_get_memory_stats_with_data(self, flow_memory_service, mock_redis):
        """Should return correct memory statistics"""
        user_id = "test-user-123"
        
        # Store some interactions
        for i in range(5):
            await flow_memory_service.store_interaction(
                user_id,
                {"user_message": f"Python task {i}"}
            )
        
        stats = await flow_memory_service.get_memory_stats(user_id)
        
        assert stats["total_interactions"] == 5
        assert stats["memory_exists"] == True
        assert "last_update" in stats
        assert "top_topics" in stats


class TestFilterRelevant:
    """Test relevance filtering"""

    @pytest.mark.asyncio
    async def test_filter_by_keyword_overlap(self, flow_memory_service):
        """Should filter by keyword overlap"""
        interactions = [
            {"user_message": "Python programming basics", "ai_response": "Python is a language"},
            {"user_message": "Weather forecast today", "ai_response": "It will be sunny"},
            {"user_message": "Advanced Python techniques", "ai_response": "Use decorators"}
        ]
        
        result = await flow_memory_service._filter_relevant(
            interactions,
            "Python programming",
            limit=10
        )
        
        # Python-related messages should come first
        assert len(result) >= 2
        assert "Python" in result[0].get("user_message", "") or "Python" in result[0].get("ai_response", "")

    @pytest.mark.asyncio
    async def test_filter_respects_limit(self, flow_memory_service):
        """Should respect the limit parameter"""
        interactions = [
            {"user_message": f"Python topic {i}", "ai_response": "Response"}
            for i in range(10)
        ]
        
        result = await flow_memory_service._filter_relevant(
            interactions,
            "Python",
            limit=3
        )
        
        assert len(result) <= 3

    @pytest.mark.asyncio
    async def test_filter_empty_query(self, flow_memory_service):
        """Empty query should still work"""
        interactions = [
            {"user_message": "Test message"}
        ]
        
        result = await flow_memory_service._filter_relevant(
            interactions,
            "",
            limit=10
        )
        
        # Empty query has no overlap, so nothing matches
        assert len(result) == 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_invalid_timestamp_handling(self, flow_memory_service):
        """Should handle invalid timestamps gracefully"""
        interactions = [
            {"user_message": "Test", "timestamp": "invalid-timestamp"},
            {"user_message": "Test 2", "timestamp": "2025-01-01T10:00:00"}
        ]
        
        # Should not raise exception
        patterns = await flow_memory_service._extract_patterns(interactions)
        
        # Should still extract some patterns
        assert "intent_patterns" in patterns

    @pytest.mark.asyncio
    async def test_empty_user_message(self, flow_memory_service):
        """Should handle empty user messages"""
        interactions = [
            {"user_message": "", "ai_response": "How can I help?"},
            {"message": ""}  # Alternative field name
        ]
        
        patterns = await flow_memory_service._extract_patterns(interactions)
        
        # Should not crash
        assert patterns is not None

    @pytest.mark.asyncio
    async def test_unicode_content(self, flow_memory_service, mock_redis):
        """Should handle unicode content properly"""
        user_id = "test-user-123"
        
        await flow_memory_service.store_interaction(
            user_id,
            {"user_message": "Привет! 你好! مرحبا!"}
        )
        
        result = await flow_memory_service.retrieve_context(user_id)
        
        assert "Привет" in result["interactions"][0]["user_message"]
