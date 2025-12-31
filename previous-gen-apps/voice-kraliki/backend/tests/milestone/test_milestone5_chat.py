"""
Milestone 5 - Browser Channel Parity Tests
Tests for web chat functionality and APIs
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from datetime import datetime
import uuid

from app.main import app
from app.api.chat import chat_sessions, chat_messages, manager

client = TestClient(app)


class TestChatAPI:
    """Test chat API endpoints"""

    def setup_method(self):
        """Setup for each test"""
        # Clear in-memory storage
        chat_sessions.clear()
        chat_messages.clear()
        # Clear connection manager
        manager.active_connections.clear()
        manager.session_connections.clear()

    def test_create_chat_session(self):
        """Test creating a new chat session"""
        request_data = {
            "user_id": "test_user_123",
            "company_id": "test_company_456",
            "context": {
                "campaign": "insurance-english",
                "customer_info": {"name": "John Doe", "phone": "+1234567890"},
            },
        }

        response = client.post("/api/chat/sessions", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["status"] == "created"
        assert "created_at" in data

        # Verify session was stored
        session_id = data["session_id"]
        assert session_id in chat_sessions
        assert chat_sessions[session_id]["user_id"] == "test_user_123"
        assert chat_sessions[session_id]["company_id"] == "test_company_456"

    def test_get_chat_session(self):
        """Test retrieving a chat session"""
        # First create a session
        create_response = client.post(
            "/api/chat/sessions", json={"user_id": "test_user", "company_id": "test_company"}
        )
        session_id = create_response.json()["session_id"]

        # Then retrieve it
        response = client.get(f"/api/chat/sessions/{session_id}")

        assert response.status_code == 200
        data = response.json()
        assert "session" in data
        assert "messages" in data
        assert "message_count" in data
        assert data["session"]["id"] == session_id
        assert data["message_count"] == 0

    def test_get_nonexistent_session(self):
        """Test retrieving a non-existent session"""
        fake_session_id = str(uuid.uuid4())
        response = client.get(f"/api/chat/sessions/{fake_session_id}")

        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

    def test_list_chat_sessions(self):
        """Test listing chat sessions"""
        # Create multiple sessions
        session_ids = []
        for i in range(3):
            response = client.post(
                "/api/chat/sessions", json={"user_id": f"user_{i}", "company_id": "test_company"}
            )
            session_ids.append(response.json()["session_id"])

        # List sessions
        response = client.get("/api/chat/sessions")

        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data
        assert data["total"] >= 3

        # Check that our sessions are in the list
        returned_session_ids = [s["id"] for s in data["sessions"]]
        for session_id in session_ids:
            assert session_id in returned_session_ids

    def test_send_message(self):
        """Test sending a message to a chat session"""
        # Create session
        create_response = client.post(
            "/api/chat/sessions", json={"user_id": "test_user", "company_id": "test_company"}
        )
        session_id = create_response.json()["session_id"]

        # Send message
        message_data = {
            "session_id": session_id,
            "message": {
                "role": "user",
                "content": "Hello, I need help with my insurance claim",
                "metadata": {"source": "web"},
            },
        }

        response = client.post("/api/chat/messages", json=message_data)

        assert response.status_code == 200
        data = response.json()
        assert "message_id" in data
        assert data["status"] == "sent"

        # Verify message was stored
        assert session_id in chat_messages
        assert len(chat_messages[session_id]) == 1
        assert (
            chat_messages[session_id][0]["content"] == "Hello, I need help with my insurance claim"
        )
        assert chat_messages[session_id][0]["role"] == "user"

    def test_send_message_to_nonexistent_session(self):
        """Test sending a message to a non-existent session"""
        fake_session_id = str(uuid.uuid4())
        message_data = {
            "session_id": fake_session_id,
            "message": {"role": "user", "content": "Hello"},
        }

        response = client.post("/api/chat/messages", json=message_data)

        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

    def test_get_session_messages(self):
        """Test retrieving messages for a session"""
        # Create session
        create_response = client.post(
            "/api/chat/sessions", json={"user_id": "test_user", "company_id": "test_company"}
        )
        session_id = create_response.json()["session_id"]

        # Send multiple messages
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there! How can I help?"},
            {"role": "user", "content": "I need help with insurance"},
        ]

        for msg in messages:
            client.post("/api/chat/messages", json={"session_id": session_id, "message": msg})

        # Get messages
        response = client.get(f"/api/chat/sessions/{session_id}/messages")

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "total" in data
        assert data["total"] == len(messages)

        # Check message content
        returned_contents = [msg["content"] for msg in data["messages"]]
        for msg in messages:
            assert msg["content"] in returned_contents

    def test_update_session_context(self):
        """Test updating session context"""
        # Create session
        create_response = client.post(
            "/api/chat/sessions", json={"user_id": "test_user", "company_id": "test_company"}
        )
        session_id = create_response.json()["session_id"]

        # Update context
        context_update = {
            "session_id": session_id,
            "context": {
                "voice_session_id": "voice_123",
                "campaign": "insurance-english",
                "customer_info": {"name": "Jane Smith", "policy_number": "POL123456"},
            },
        }

        response = client.put(f"/api/chat/sessions/{session_id}/context", json=context_update)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        assert "context" in data
        assert data["context"]["voice_session_id"] == "voice_123"
        assert data["context"]["campaign"] == "insurance-english"

    def test_end_chat_session(self):
        """Test ending a chat session"""
        # Create session
        create_response = client.post(
            "/api/chat/sessions", json={"user_id": "test_user", "company_id": "test_company"}
        )
        session_id = create_response.json()["session_id"]

        # End session
        response = client.delete(f"/api/chat/sessions/{session_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ended"
        assert "ended_at" in data

        # Verify session status was updated
        assert chat_sessions[session_id]["status"] == "ended"
        assert "ended_at" in chat_sessions[session_id]

    def test_list_sessions_with_status_filter(self):
        """Test listing sessions with status filter"""
        # Create sessions
        active_session_id = client.post(
            "/api/chat/sessions", json={"user_id": "user1", "company_id": "company"}
        ).json()["session_id"]

        ended_session_id = client.post(
            "/api/chat/sessions", json={"user_id": "user2", "company_id": "company"}
        ).json()["session_id"]

        # End one session
        client.delete(f"/api/chat/sessions/{ended_session_id}")

        # List only active sessions
        response = client.get("/api/chat/sessions?status=active")

        assert response.status_code == 200
        data = response.json()
        active_sessions = [s for s in data["sessions"] if s["id"] == active_session_id]
        ended_sessions = [s for s in data["sessions"] if s["id"] == ended_session_id]

        assert len(active_sessions) == 1
        assert len(ended_sessions) == 0

    def test_session_pagination(self):
        """Test session list pagination"""
        # Create multiple sessions
        for i in range(5):
            client.post(
                "/api/chat/sessions", json={"user_id": f"user_{i}", "company_id": "company"}
            )

        # Test pagination
        response = client.get("/api/chat/sessions?limit=2&offset=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 1
        assert data["total"] >= 5


class TestUnreadMessageTracking:
    """Test unread message tracking functionality"""

    def setup_method(self):
        """Setup for each test"""
        chat_sessions.clear()
        chat_messages.clear()
        manager.active_connections.clear()
        manager.session_connections.clear()

    def test_unread_count_initial_zero(self):
        """Test that new session has zero unread messages"""
        create_response = client.post(
            "/api/chat/sessions", json={"user_id": "test_user", "company_id": "test_company"}
        )
        session_id = create_response.json()["session_id"]

        # Get session
        response = client.get(f"/api/chat/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()

        assert "session" in data
        assert data["session"]["unread_count"] == 0

    def test_unread_count_increases_with_messages(self):
        """Test that unread count increases when messages are sent"""
        create_response = client.post(
            "/api/chat/sessions", json={"user_id": "test_user", "company_id": "test_company"}
        )
        session_id = create_response.json()["session_id"]

        # Send some messages
        for i in range(3):
            client.post(
                "/api/chat/messages",
                json={
                    "session_id": session_id,
                    "message": {"role": "user", "content": f"Message {i + 1}"},
                },
            )

        # Get session - should show unread count
        response = client.get(f"/api/chat/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()

        assert data["session"]["unread_count"] == 3

    def test_mark_session_read_resets_unread_count(self):
        """Test that marking session as read resets unread count"""
        create_response = client.post(
            "/api/chat/sessions", json={"user_id": "test_user", "company_id": "test_company"}
        )
        session_id = create_response.json()["session_id"]

        # Send messages
        for i in range(2):
            client.post(
                "/api/chat/messages",
                json={
                    "session_id": session_id,
                    "message": {"role": "user", "content": f"Message {i + 1}"},
                },
            )

        # Verify unread count
        response = client.get(f"/api/chat/sessions/{session_id}")
        assert response.json()["session"]["unread_count"] == 2

        # Mark as read
        read_response = client.post(f"/api/chat/sessions/{session_id}/read")
        assert read_response.status_code == 200
        assert read_response.json()["unread_count"] == 0

        # Verify unread count is now 0
        response = client.get(f"/api/chat/sessions/{session_id}")
        assert response.json()["session"]["unread_count"] == 0

    def test_unread_count_only_counts_messages_after_last_read(self):
        """Test that only messages after last_read_at are counted as unread"""
        create_response = client.post(
            "/api/chat/sessions", json={"user_id": "test_user", "company_id": "test_company"}
        )
        session_id = create_response.json()["session_id"]

        # Send initial messages
        for i in range(2):
            client.post(
                "/api/chat/messages",
                json={
                    "session_id": session_id,
                    "message": {"role": "user", "content": f"Initial {i + 1}"},
                },
            )

        # Mark as read
        client.post(f"/api/chat/sessions/{session_id}/read")

        # Send more messages
        for i in range(3):
            client.post(
                "/api/chat/messages",
                json={
                    "session_id": session_id,
                    "message": {"role": "user", "content": f"New {i + 1}"},
                },
            )

        # Should only count the 3 new messages
        response = client.get(f"/api/chat/sessions/{session_id}")
        assert response.json()["session"]["unread_count"] == 3

    def test_list_sessions_includes_unread_count(self):
        """Test that session list includes unread count for each session"""
        # Create sessions with different message counts
        session_ids = []
        for i in range(3):
            create_response = client.post(
                "/api/chat/sessions", json={"user_id": f"user_{i}", "company_id": "company"}
            )
            session_id = create_response.json()["session_id"]
            session_ids.append(session_id)

            # Send different number of messages to each
            for j in range(i + 1):
                client.post(
                    "/api/chat/messages",
                    json={
                        "session_id": session_id,
                        "message": {"role": "user", "content": f"Message {j + 1}"},
                    },
                )

        # List sessions
        response = client.get("/api/chat/sessions")
        assert response.status_code == 200
        data = response.json()

        # Check that unread counts are present and correct
        for session in data["sessions"]:
            assert "unread_count" in session
            assert "message_count" in session
            assert session["unread_count"] <= session["message_count"]

    def test_get_messages_does_not_affect_unread_count(self):
        """Test that retrieving messages doesn't automatically mark them as read"""
        create_response = client.post(
            "/api/chat/sessions", json={"user_id": "test_user", "company_id": "test_company"}
        )
        session_id = create_response.json()["session_id"]

        # Send messages
        for i in range(2):
            client.post(
                "/api/chat/messages",
                json={
                    "session_id": session_id,
                    "message": {"role": "user", "content": f"Message {i + 1}"},
                },
            )

        # Get unread count before retrieving messages
        response = client.get(f"/api/chat/sessions/{session_id}")
        unread_before = response.json()["session"]["unread_count"]
        assert unread_before == 2

        # Get messages (should not mark as read)
        client.get(f"/api/chat/sessions/{session_id}/messages")

        # Get unread count after retrieving messages
        response = client.get(f"/api/chat/sessions/{session_id}")
        unread_after = response.json()["session"]["unread_count"]
        assert unread_after == 2


class TestWebSocketConnection:
    """Test WebSocket functionality"""

    def setup_method(self):
        """Setup for each test"""
        chat_sessions.clear()
        chat_messages.clear()
        manager.active_connections.clear()
        manager.session_connections.clear()

    def test_websocket_connection(self):
        """Test WebSocket connection and basic messaging"""
        # Create session first
        create_response = client.post(
            "/api/chat/sessions", json={"user_id": "test_user", "company_id": "test_company"}
        )
        session_id = create_response.json()["session_id"]

        with client.websocket_connect("/api/chat/ws") as websocket:
            # Join session
            websocket.send_text(json.dumps({"type": "join", "session_id": session_id}))

            # Should receive connection confirmation
            data = websocket.receive_text()
            response = json.loads(data)
            assert response["type"] == "connected"
            assert response["session_id"] == session_id

            # Send a message
            websocket.send_text(
                json.dumps({"type": "message", "role": "user", "content": "Hello via WebSocket"})
            )

            # Should receive the message back (echo)
            data = websocket.receive_text()
            response = json.loads(data)
            assert response["type"] == "message"
            assert response["content"] == "Hello via WebSocket"
            assert response["role"] == "user"

    def test_websocket_invalid_session(self):
        """Test WebSocket connection with invalid session"""
        fake_session_id = str(uuid.uuid4())

        with pytest.raises(Exception):  # Should raise an exception
            with client.websocket_connect("/api/chat/ws") as websocket:
                websocket.send_text(json.dumps({"type": "join", "session_id": fake_session_id}))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
