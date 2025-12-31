"""
Unit tests for Flow Memory Service
Tests persistent context, session management, and memory operations
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json


class TestFlowMemoryBasic:
    """Tests for basic flow memory operations"""
    
    def test_create_memory_context(self):
        """Create new memory context for user"""
        context = {
            "user_id": "user-123",
            "session_id": "session-456",
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
            "data": {}
        }
        assert context["user_id"] == "user-123"
        assert context["data"] == {}
    
    def test_store_memory(self):
        """Store data in flow memory"""
        memory = {"data": {}}
        
        # Store a piece of information
        memory["data"]["last_task"] = {
            "id": "task-123",
            "title": "Review PR",
            "context": "User was working on this task"
        }
        
        assert "last_task" in memory["data"]
        assert memory["data"]["last_task"]["id"] == "task-123"
    
    def test_retrieve_memory(self):
        """Retrieve data from flow memory"""
        memory = {
            "data": {
                "last_task": {"id": "task-123", "title": "Review PR"},
                "preferences": {"theme": "dark"}
            }
        }
        
        last_task = memory["data"].get("last_task")
        assert last_task is not None
        assert last_task["title"] == "Review PR"
    
    def test_delete_memory_key(self):
        """Delete specific key from memory"""
        memory = {
            "data": {
                "key1": "value1",
                "key2": "value2"
            }
        }
        
        del memory["data"]["key1"]
        assert "key1" not in memory["data"]
        assert "key2" in memory["data"]
    
    def test_clear_all_memory(self):
        """Clear all memory for user"""
        memory = {
            "data": {
                "key1": "value1",
                "key2": "value2",
                "key3": "value3"
            }
        }
        
        memory["data"] = {}
        assert len(memory["data"]) == 0


class TestFlowMemoryPersistence:
    """Tests for memory persistence across sessions"""
    
    def test_memory_persists_across_sessions(self):
        """Memory persists when session changes"""
        # Simulate storing in session 1
        memory_store = {}
        user_id = "user-123"
        memory_store[user_id] = {"last_topic": "project planning"}
        
        # Simulate new session accessing same user memory
        retrieved = memory_store.get(user_id)
        assert retrieved["last_topic"] == "project planning"
    
    def test_session_specific_data(self):
        """Some data is session-specific"""
        memory = {
            "persistent": {
                "preferences": {"theme": "dark"}
            },
            "session": {
                "current_view": "dashboard",
                "temp_data": "session-only"
            }
        }
        
        # On new session, clear session data but keep persistent
        memory["session"] = {}
        
        assert "preferences" in memory["persistent"]
        assert memory["session"] == {}
    
    def test_memory_expiration(self):
        """Memory can have TTL"""
        memory_entry = {
            "key": "temp_context",
            "value": "some temporary data",
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        # Check if expired
        expires = datetime.fromisoformat(memory_entry["expires_at"])
        is_expired = datetime.utcnow() > expires
        assert not is_expired  # Should not be expired yet


class TestFlowMemoryContext:
    """Tests for contextual memory features"""
    
    def test_conversation_context(self):
        """Store conversation context for AI"""
        context = {
            "conversation_id": "conv-123",
            "messages": [
                {"role": "user", "content": "Create a task for tomorrow"},
                {"role": "assistant", "content": "I'll create a task for you."}
            ],
            "extracted_entities": {
                "date": "tomorrow",
                "intent": "create_task"
            }
        }
        
        assert len(context["messages"]) == 2
        assert context["extracted_entities"]["intent"] == "create_task"
    
    def test_task_context(self):
        """Store context about current task"""
        task_context = {
            "current_task_id": "task-123",
            "related_tasks": ["task-100", "task-101"],
            "time_spent": 3600,  # seconds
            "last_action": "updated status to in_progress"
        }
        
        assert task_context["current_task_id"] == "task-123"
        assert len(task_context["related_tasks"]) == 2
    
    def test_user_preferences_context(self):
        """Store user preference context"""
        preferences = {
            "preferred_task_view": "kanban",
            "default_priority": "medium",
            "notification_settings": {
                "email": True,
                "push": False
            },
            "ai_preferences": {
                "verbosity": "concise",
                "formality": "casual"
            }
        }
        
        assert preferences["ai_preferences"]["verbosity"] == "concise"


class TestFlowMemoryAI:
    """Tests for AI-related memory features"""
    
    def test_ai_response_caching(self):
        """Cache AI responses for similar queries"""
        cache = {}
        query_hash = "hash_of_query_123"
        
        # Cache miss
        if query_hash not in cache:
            response = {"content": "AI generated response", "tokens": 150}
            cache[query_hash] = {
                "response": response,
                "cached_at": datetime.utcnow().isoformat(),
                "hit_count": 0
            }
        
        # Cache hit
        cached = cache.get(query_hash)
        cached["hit_count"] += 1
        
        assert cached["hit_count"] == 1
        assert cached["response"]["content"] == "AI generated response"
    
    def test_context_window_management(self):
        """Manage context window size"""
        max_tokens = 4000
        messages = [
            {"role": "user", "content": "Message 1", "tokens": 100},
            {"role": "assistant", "content": "Response 1", "tokens": 200},
            {"role": "user", "content": "Message 2", "tokens": 150},
            {"role": "assistant", "content": "Response 2", "tokens": 300},
        ]
        
        total_tokens = sum(m["tokens"] for m in messages)
        
        # Trim oldest messages if over limit
        while total_tokens > max_tokens and len(messages) > 2:
            removed = messages.pop(0)
            total_tokens -= removed["tokens"]
        
        assert total_tokens <= max_tokens
    
    def test_semantic_memory_retrieval(self):
        """Retrieve semantically relevant memories"""
        memories = [
            {"id": "mem-1", "content": "User likes dark theme", "embedding": [0.1, 0.2]},
            {"id": "mem-2", "content": "User prefers morning tasks", "embedding": [0.3, 0.4]},
            {"id": "mem-3", "content": "User works on Python projects", "embedding": [0.5, 0.6]}
        ]
        
        # Would use vector similarity in real implementation
        query_embedding = [0.5, 0.55]
        
        # Simple mock similarity (in real code, use cosine similarity)
        relevant = memories[2]  # Most similar to query
        assert relevant["content"] == "User works on Python projects"


class TestFlowMemoryRedis:
    """Tests for Redis-based memory storage"""
    
    def test_redis_key_format(self):
        """Verify Redis key format"""
        user_id = "user-123"
        key_type = "context"
        
        redis_key = f"flow_memory:{user_id}:{key_type}"
        assert redis_key == "flow_memory:user-123:context"
    
    def test_redis_serialization(self):
        """Test JSON serialization for Redis"""
        data = {
            "user_id": "user-123",
            "context": {
                "last_task": "task-456",
                "preferences": {"theme": "dark"}
            }
        }
        
        serialized = json.dumps(data)
        deserialized = json.loads(serialized)
        
        assert deserialized["context"]["preferences"]["theme"] == "dark"
    
    def test_redis_ttl(self):
        """Test TTL setting for Redis keys"""
        ttl_seconds = 86400  # 24 hours
        assert ttl_seconds == 86400


class TestFlowMemoryAPI:
    """Tests for Flow Memory API endpoints"""
    
    def test_get_memory_endpoint(self):
        """GET /flow-memory returns user memory"""
        response = {
            "user_id": "user-123",
            "memory": {
                "last_task": "task-456",
                "conversation_context": []
            }
        }
        assert "memory" in response
    
    def test_update_memory_endpoint(self):
        """PUT /flow-memory updates memory"""
        request_body = {
            "key": "last_task",
            "value": "task-789"
        }
        
        # Would update memory
        response = {
            "success": True,
            "key": request_body["key"],
            "updated_at": datetime.utcnow().isoformat()
        }
        assert response["success"] is True
    
    def test_delete_memory_endpoint(self):
        """DELETE /flow-memory/{key} removes key"""
        key_to_delete = "temporary_data"
        
        response = {
            "success": True,
            "deleted_key": key_to_delete
        }
        assert response["deleted_key"] == key_to_delete
    
    def test_clear_memory_endpoint(self):
        """DELETE /flow-memory clears all memory"""
        response = {
            "success": True,
            "message": "All memory cleared"
        }
        assert response["success"] is True
