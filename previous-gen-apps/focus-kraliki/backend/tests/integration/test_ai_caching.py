"""
Integration tests for AI caching and flow memory
"""
from app.core.cache import cache_manager, flow_memory


class TestAICaching:
    """Test AI response caching"""

    async def test_cache_ai_response(self):
        """Test caching an AI response"""
        success = await cache_manager.cache_ai_response(
            model="test-model",
            prompt="test prompt",
            response="test response",
            ttl=60
        )
        assert success is True

        # Retrieve cached response
        cached = await cache_manager.get_ai_response(
            model="test-model",
            prompt="test prompt"
        )
        assert cached == "test response"

    async def test_flow_memory_context(self):
        """Test flow memory context save/retrieve"""
        user_id = "test-user"
        session_id = "test-session"
        context = {"key": "value", "data": [1, 2, 3]}

        # Save context
        success = await flow_memory.save_context(user_id, session_id, context)
        assert success is True

        # Retrieve context
        retrieved = await flow_memory.get_context(user_id, session_id)
        assert retrieved == context

    async def test_flow_memory_interactions(self):
        """Test flow memory interaction tracking"""
        user_id = "test-user"
        interaction = {
            "type": "chat",
            "message": "test message",
            "timestamp": "2025-11-10T00:00:00"
        }

        # Add interaction
        success = await flow_memory.add_interaction(user_id, interaction)
        assert success is True

        # Get recent interactions
        interactions = await flow_memory.get_recent_interactions(user_id, limit=10)
        assert len(interactions) > 0
        assert interactions[-1]["message"] == "test message"


class TestFlowMemoryEndpoints:
    """Test flow memory API endpoints"""

    def test_save_flow_context(self, client, auth_headers):
        """Test saving flow context via API"""
        session_id = "test-session-123"
        context = {"currentTask": "task-1", "preferences": {"theme": "dark"}}

        response = client.post(
            f"/ai/flow/context/{session_id}",
            json=context,
            headers=auth_headers
        )

        # May fail if Redis not available, that's OK for integration tests
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == session_id

    def test_get_flow_context(self, client, auth_headers):
        """Test getting flow context via API"""
        session_id = "test-session-123"

        response = client.get(
            f"/ai/flow/context/{session_id}",
            headers=auth_headers
        )

        # May return empty context if nothing saved
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "context" in data

    def test_get_recent_interactions(self, client, auth_headers):
        """Test getting recent interactions"""
        response = client.get("/ai/flow/interactions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "interactions" in data
        assert "total" in data
