"""
Unit tests for agent sessions router
Tests agent session creation and management
"""

import pytest
from fastapi.testclient import TestClient


class TestAgentSessionsAPI:
    """Test agent sessions router via HTTP client"""

    def test_create_session_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.post("/agent/sessions", json={"goal": "Test goal"})
        assert response.status_code == 401

    def test_create_session_authenticated(
        self, client: TestClient, auth_headers: dict
    ):
        """Should create agent session for authenticated user"""
        payload = {"goal": "Complete a test task"}
        response = client.post("/agent/sessions", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "agentToken" in data
        assert "sessionUuid" in data
        assert "id" in data
        assert "status" in data
        assert data["goal"] == "Complete a test task"
        assert len(data["agentToken"]) > 0
        assert len(data["sessionUuid"]) > 0

    def test_create_session_with_structured_goal(
        self, client: TestClient, auth_headers: dict
    ):
        """Should create agent session with structured goal"""
        payload = {
            "goal": "Create new task",
            "structuredGoal": {
                "action": "create_task",
                "params": {"title": "New Task", "priority": 5}
            },
            "context": {"project_id": "proj123"}
        }
        response = client.post("/agent/sessions", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "agentToken" in data
        assert "sessionUuid" in data
        assert data["structuredGoal"]["action"] == "create_task"

    def test_create_session_without_telemetry(
        self, client: TestClient, auth_headers: dict
    ):
        """Should create session without optional telemetry ID"""
        payload = {
            "goal": "Test without telemetry",
        }
        response = client.post("/agent/sessions", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "agentToken" in data
        assert data["goal"] == "Test without telemetry"

    def test_agent_token_structure(self, client: TestClient, auth_headers: dict):
        """Should return properly structured agent token response"""
        payload = {"goal": "Token structure test"}
        response = client.post("/agent/sessions", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data["agentToken"], str)
        assert isinstance(data["sessionUuid"], str)
        assert isinstance(data["id"], str)
        assert isinstance(data["status"], str)

        assert data["agentToken"].startswith("eyJ")  # JWT format
        assert len(data["sessionUuid"]) >= 10

    def test_multiple_sessions(self, client: TestClient, auth_headers: dict):
        """Should allow creating multiple agent sessions"""
        payload = {"goal": "First session"}
        response1 = client.post("/agent/sessions", json=payload, headers=auth_headers)
        assert response1.status_code == 200
        data1 = response1.json()

        payload2 = {"goal": "Second session"}
        response2 = client.post("/agent/sessions", json=payload2, headers=auth_headers)
        assert response2.status_code == 200
        data2 = response2.json()

        assert data1["sessionUuid"] != data2["sessionUuid"]
        assert data1["id"] != data2["id"]

    def test_create_session_requires_goal(
        self, client: TestClient, auth_headers: dict
    ):
        """Should return 422 when goal is missing"""
        response = client.post("/agent/sessions", json={}, headers=auth_headers)
        assert response.status_code == 422
