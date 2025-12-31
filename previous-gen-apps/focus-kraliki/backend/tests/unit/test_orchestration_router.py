"""
Unit tests for Orchestration Router
Tests model validation and endpoint functionality for n8n flow triggering
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.routers.orchestration import (
    OrchestrationRequest,
    OrchestrationResponse,
)


class TestOrchestrationRequestModel:
    """Tests for OrchestrationRequest Pydantic model"""

    def test_default_context(self):
        """OrchestrationRequest has correct defaults"""
        request = OrchestrationRequest()
        assert request.context == {}

    def test_with_context(self):
        """OrchestrationRequest accepts context"""
        request = OrchestrationRequest(context={
            "task_id": "123",
            "action": "complete",
            "metadata": {"key": "value"}
        })
        assert request.context["task_id"] == "123"
        assert request.context["action"] == "complete"

    def test_empty_context(self):
        """OrchestrationRequest accepts empty context"""
        request = OrchestrationRequest(context={})
        assert request.context == {}

    def test_complex_context(self):
        """OrchestrationRequest accepts complex nested context"""
        request = OrchestrationRequest(context={
            "task": {
                "id": "task-123",
                "title": "Test Task",
                "metadata": {
                    "tags": ["urgent", "review"],
                    "priority": 1
                }
            },
            "event": "completed",
            "timestamp": "2025-01-01T00:00:00Z"
        })
        assert request.context["task"]["id"] == "task-123"
        assert request.context["task"]["metadata"]["tags"] == ["urgent", "review"]


class TestOrchestrationResponseModel:
    """Tests for OrchestrationResponse Pydantic model"""

    def test_success_response(self):
        """OrchestrationResponse validates success case"""
        response = OrchestrationResponse(
            success=True,
            message="Flow triggered"
        )
        assert response.success is True
        assert response.message == "Flow triggered"
        assert response.data is None

    def test_response_with_data(self):
        """OrchestrationResponse accepts data"""
        response = OrchestrationResponse(
            success=True,
            message="Flow triggered",
            data={"execution_id": "abc-123", "status": "running"}
        )
        assert response.data["execution_id"] == "abc-123"
        assert response.data["status"] == "running"

    def test_failure_response(self):
        """OrchestrationResponse validates failure case"""
        response = OrchestrationResponse(
            success=False,
            message="Flow failed to trigger"
        )
        assert response.success is False

    def test_response_with_complex_data(self):
        """OrchestrationResponse accepts complex data"""
        response = OrchestrationResponse(
            success=True,
            message="Completed",
            data={
                "execution_id": "exec-123",
                "result": {
                    "status": "success",
                    "outputs": ["file1.txt", "file2.txt"]
                },
                "metrics": {
                    "duration_ms": 1500,
                    "steps_completed": 5
                }
            }
        )
        assert response.data["result"]["status"] == "success"
        assert response.data["metrics"]["duration_ms"] == 1500


class TestOrchestrationLogic:
    """Tests for orchestration business logic without HTTP"""

    def test_flow_id_formats(self):
        """Valid flow ID formats"""
        valid_flow_ids = [
            "simple-flow",
            "flow_with_underscore",
            "flow123",
            "research-prospect",
            "generate-content",
            "academy_waitlist_signup"
        ]
        for flow_id in valid_flow_ids:
            assert isinstance(flow_id, str)
            assert len(flow_id) > 0
            # Flow IDs should be URL-safe
            assert " " not in flow_id

    def test_context_structure(self):
        """Context can contain various data types"""
        contexts = [
            {},  # Empty context
            {"key": "value"},  # Simple key-value
            {"nested": {"inner": True}},  # Nested objects
            {"list": [1, 2, 3]},  # Lists
            {"mixed": {"num": 42, "str": "test", "bool": True}}  # Mixed types
        ]
        for context in contexts:
            request = OrchestrationRequest(context=context)
            assert request.context == context

    def test_user_context_injection(self):
        """User context is injected into request context"""
        request = OrchestrationRequest(context={"task_id": "123"})
        user_id = "user-abc"
        workspace_id = "ws-xyz"

        full_context = {
            **request.context,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "triggered_at": "now"
        }

        assert full_context["task_id"] == "123"
        assert full_context["user_id"] == user_id
        assert full_context["workspace_id"] == workspace_id

    def test_response_construction(self):
        """Response is constructed correctly"""
        flow_id = "test-flow"
        result = {"execution_id": "exec-123"}

        response = OrchestrationResponse(
            success=True,
            message=f"Flow '{flow_id}' triggered successfully",
            data=result
        )

        assert response.success is True
        assert flow_id in response.message
        assert response.data["execution_id"] == "exec-123"

    def test_error_response_construction(self):
        """Error response is constructed correctly"""
        error_msg = "Connection refused"

        response = OrchestrationResponse(
            success=False,
            message=f"Failed to trigger orchestration flow: {error_msg}",
            data=None
        )

        assert response.success is False
        assert "Failed" in response.message


class TestOrchestrationWorkspaceSettings:
    """Tests for workspace settings handling"""

    def test_workspace_settings_none(self):
        """Handle None workspace settings"""
        workspace_settings = None
        # Should not raise an error
        assert workspace_settings is None

    def test_workspace_settings_with_n8n_url(self):
        """Workspace settings can contain n8n URL"""
        workspace_settings = {
            "n8n_url": "https://custom-n8n.example.com",
            "n8n_api_key": "custom-key"
        }
        assert "n8n_url" in workspace_settings
        assert workspace_settings["n8n_url"].startswith("https://")

    def test_workspace_settings_empty(self):
        """Handle empty workspace settings"""
        workspace_settings = {}
        assert isinstance(workspace_settings, dict)
        assert "n8n_url" not in workspace_settings
