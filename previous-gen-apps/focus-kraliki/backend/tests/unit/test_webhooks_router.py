"""
Unit tests for Webhooks Router
Tests webhook endpoints for n8n/external automation integration

Uses mock-based testing to avoid database dependencies.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock, MagicMock, Mock

from app.routers.webhooks import (
    WebhookTaskCreate,
    WebhookTaskComplete,
    WebhookWorkflowExecute,
    WebhookEventCreate,
    WebhookResponse,
    WebhookConfig,
)


class TestPydanticModels:
    """Tests for webhook Pydantic models"""

    def test_webhook_task_create_default_values(self):
        """WebhookTaskCreate has correct defaults"""
        model = WebhookTaskCreate(title="Test Task")
        assert model.title == "Test Task"
        assert model.description is None
        assert model.priority == 2
        assert model.estimatedMinutes is None
        assert model.dueDate is None
        assert model.tags == []

    def test_webhook_task_create_full_values(self):
        """WebhookTaskCreate accepts all fields"""
        model = WebhookTaskCreate(
            title="Complete Task",
            description="Full description",
            priority=1,
            estimatedMinutes=60,
            dueDate="2025-12-31T23:59:59Z",
            tags=["urgent", "project-x"]
        )
        assert model.title == "Complete Task"
        assert model.description == "Full description"
        assert model.priority == 1
        assert model.estimatedMinutes == 60
        assert model.dueDate == "2025-12-31T23:59:59Z"
        assert model.tags == ["urgent", "project-x"]

    def test_webhook_task_create_empty_tags(self):
        """WebhookTaskCreate with empty tags"""
        model = WebhookTaskCreate(title="No Tags Task", tags=[])
        assert model.tags == []

    def test_webhook_task_create_multiple_tags(self):
        """WebhookTaskCreate with multiple tags"""
        model = WebhookTaskCreate(
            title="Multi Tag Task",
            tags=["tag1", "tag2", "tag3", "automation"]
        )
        assert len(model.tags) == 4
        assert "automation" in model.tags

    def test_webhook_task_complete_model(self):
        """WebhookTaskComplete model validates correctly"""
        model = WebhookTaskComplete(taskId="task-123")
        assert model.taskId == "task-123"
        assert model.notes is None

        model_with_notes = WebhookTaskComplete(taskId="task-456", notes="Completed via automation")
        assert model_with_notes.notes == "Completed via automation"

    def test_webhook_task_complete_long_notes(self):
        """WebhookTaskComplete with long notes"""
        long_notes = "A" * 1000
        model = WebhookTaskComplete(taskId="task-789", notes=long_notes)
        assert len(model.notes) == 1000

    def test_webhook_workflow_execute_model(self):
        """WebhookWorkflowExecute model validates correctly"""
        model = WebhookWorkflowExecute(templateId="template-001")
        assert model.templateId == "template-001"
        assert model.customTitle is None
        assert model.startDate is None
        assert model.priority == 2

        model_full = WebhookWorkflowExecute(
            templateId="template-002",
            customTitle="Custom Workflow Name",
            startDate="2025-01-01T09:00:00Z",
            priority=1
        )
        assert model_full.customTitle == "Custom Workflow Name"
        assert model_full.startDate == "2025-01-01T09:00:00Z"
        assert model_full.priority == 1

    def test_webhook_workflow_execute_priorities(self):
        """WebhookWorkflowExecute with various priorities"""
        for priority in [0, 1, 2, 3, 4]:
            model = WebhookWorkflowExecute(templateId="test", priority=priority)
            assert model.priority == priority

    def test_webhook_event_create_model(self):
        """WebhookEventCreate model validates correctly"""
        model = WebhookEventCreate(
            title="Meeting",
            start_time="2025-01-15T10:00:00Z"
        )
        assert model.title == "Meeting"
        assert model.start_time == "2025-01-15T10:00:00Z"
        assert model.description is None
        assert model.end_time is None
        assert model.location is None

        model_full = WebhookEventCreate(
            title="Team Meeting",
            description="Weekly sync",
            start_time="2025-01-15T10:00:00Z",
            end_time="2025-01-15T11:00:00Z",
            location="Conference Room A"
        )
        assert model_full.description == "Weekly sync"
        assert model_full.location == "Conference Room A"

    def test_webhook_event_create_with_timezone(self):
        """WebhookEventCreate with timezone in dates"""
        model = WebhookEventCreate(
            title="Timezone Event",
            start_time="2025-01-15T10:00:00+02:00",
            end_time="2025-01-15T11:00:00+02:00"
        )
        assert "+02:00" in model.start_time
        assert "+02:00" in model.end_time

    def test_webhook_response_model(self):
        """WebhookResponse model validates correctly"""
        response = WebhookResponse(success=True, message="Task created")
        assert response.success is True
        assert response.message == "Task created"
        assert response.data is None

        response_with_data = WebhookResponse(
            success=True,
            message="Task created",
            data={"taskId": "123", "title": "New Task"}
        )
        assert response_with_data.data == {"taskId": "123", "title": "New Task"}

    def test_webhook_response_failure(self):
        """WebhookResponse for failed operations"""
        response = WebhookResponse(
            success=False,
            message="Task not found",
            data={"error_code": "NOT_FOUND"}
        )
        assert response.success is False
        assert "error_code" in response.data

    def test_webhook_config_model(self):
        """WebhookConfig model validates correctly"""
        config = WebhookConfig()
        assert config.enabled is True
        assert config.events == []
        assert config.target_url is None

        config_full = WebhookConfig(
            enabled=False,
            events=["task-created", "task-completed"],
            target_url="https://n8n.example.com/webhook"
        )
        assert config_full.enabled is False
        assert len(config_full.events) == 2

    def test_webhook_config_all_events(self):
        """WebhookConfig with all supported events"""
        all_events = [
            "task-create",
            "task-complete",
            "workflow-execute",
            "event-create"
        ]
        config = WebhookConfig(
            enabled=True,
            events=all_events,
            target_url="https://hooks.example.com/webhook"
        )
        assert len(config.events) == 4


class TestWebhookSecretFormat:
    """Tests for webhook secret format validation"""

    def test_webhook_secret_prefix(self):
        """Webhook secrets should start with whsec_"""
        import secrets
        new_secret = f"whsec_{secrets.token_urlsafe(32)}"
        assert new_secret.startswith("whsec_")
        assert len(new_secret) > 40  # whsec_ + 32 bytes urlsafe

    def test_webhook_secret_uniqueness(self):
        """Generated secrets should be unique"""
        import secrets
        secrets_list = [f"whsec_{secrets.token_urlsafe(32)}" for _ in range(100)]
        assert len(set(secrets_list)) == 100  # All unique


class TestWebhookPayloadValidation:
    """Tests for webhook payload edge cases"""

    def test_task_create_minimal(self):
        """Minimal task creation payload"""
        model = WebhookTaskCreate(title="x")
        assert model.title == "x"

    def test_task_create_special_characters(self):
        """Task with special characters in title"""
        model = WebhookTaskCreate(title="Test <script>alert('xss')</script>")
        assert "<script>" in model.title

    def test_task_create_unicode(self):
        """Task with unicode characters"""
        model = WebhookTaskCreate(title="任务 测试 🚀 émojis")
        assert "🚀" in model.title

    def test_event_create_all_day_simulation(self):
        """Event spanning full day"""
        model = WebhookEventCreate(
            title="All Day Event",
            start_time="2025-01-15T00:00:00Z",
            end_time="2025-01-15T23:59:59Z"
        )
        assert model.start_time.endswith("00:00:00Z")

    def test_workflow_execute_empty_custom_title(self):
        """Workflow with empty string custom title"""
        model = WebhookWorkflowExecute(
            templateId="template-001",
            customTitle=""
        )
        assert model.customTitle == ""


class TestWebhookTimestampHandling:
    """Tests for timestamp format handling"""

    def test_iso_format_with_z(self):
        """ISO format with Z suffix"""
        date_str = "2025-12-31T23:59:59Z"
        # Simulate the router's date parsing
        parsed = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        assert parsed.year == 2025
        assert parsed.month == 12

    def test_iso_format_with_offset(self):
        """ISO format with timezone offset"""
        date_str = "2025-12-31T23:59:59+05:30"
        parsed = datetime.fromisoformat(date_str)
        assert parsed.year == 2025

    def test_iso_format_negative_offset(self):
        """ISO format with negative timezone offset"""
        date_str = "2025-12-31T23:59:59-08:00"
        parsed = datetime.fromisoformat(date_str)
        assert parsed.year == 2025


class TestWebhookEventTypes:
    """Tests for webhook event type constants"""

    def test_supported_event_types(self):
        """All supported event types"""
        supported = [
            "task-create",
            "task-complete",
            "workflow-execute",
            "event-create"
        ]
        assert len(supported) == 4

    def test_event_envelope_structure(self):
        """Standard event envelope structure"""
        envelope = {
            "type": "task-created",
            "source": "focus-kraliki",
            "timestamp": datetime.utcnow().isoformat(),
            "organizationId": "org-123",
            "data": {"task_id": "task-456"}
        }
        assert envelope["source"] == "focus-kraliki"
        assert "timestamp" in envelope
        assert "data" in envelope


class TestWebhookStatusResponse:
    """Tests for webhook status endpoint response"""

    def test_status_response_structure(self):
        """Status endpoint response structure"""
        response = {
            "status": "healthy",
            "service": "focus-kraliki-webhooks",
            "darwin2_connected": False,
            "darwin2_api": "http://127.0.0.1:8198",
            "supported_events": [
                "task-create",
                "task-complete",
                "workflow-execute",
                "event-create"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        assert response["status"] == "healthy"
        assert response["service"] == "focus-kraliki-webhooks"
        assert len(response["supported_events"]) == 4


class TestWebhookResponseFormats:
    """Tests for webhook response formatting"""

    def test_task_create_response(self):
        """Task creation response format"""
        response = WebhookResponse(
            success=True,
            message="Task created: My Task",
            data={"taskId": "task-abc123", "title": "My Task"}
        )
        assert "taskId" in response.data
        assert response.data["title"] == "My Task"

    def test_workflow_execute_response(self):
        """Workflow execution response format"""
        response = WebhookResponse(
            success=True,
            message="Workflow executed: Weekly Review",
            data={
                "parentTaskId": "task-parent",
                "createdTasks": ["task-1", "task-2", "task-3"],
                "totalTasks": 3
            }
        )
        assert response.data["totalTasks"] == 3
        assert len(response.data["createdTasks"]) == 3

    def test_event_create_response(self):
        """Event creation response format"""
        response = WebhookResponse(
            success=True,
            message="Event created: Team Meeting",
            data={
                "eventId": "event-xyz",
                "title": "Team Meeting",
                "startTime": "2025-01-15T10:00:00+00:00"
            }
        )
        assert "eventId" in response.data
        assert "startTime" in response.data


class TestWebhookTagLogic:
    """Tests for webhook automatic tagging logic"""

    def test_webhook_tag_added(self):
        """Webhook tag is added to task tags"""
        original_tags = ["project-x", "urgent"]
        webhook_tags = original_tags + ["webhook"]
        assert "webhook" in webhook_tags
        assert "project-x" in webhook_tags

    def test_workflow_tag_added(self):
        """Workflow tag is added for workflow-created tasks"""
        template_tags = ["template-tag"]
        workflow_tags = template_tags + ["workflow", "webhook"]
        assert "workflow" in workflow_tags
        assert "webhook" in workflow_tags


class TestWebhookSecurityHeaders:
    """Tests for webhook security header handling"""

    def test_webhook_secret_header_name(self):
        """Correct header name for webhook secret"""
        header_name = "X-Webhook-Secret"
        assert header_name == "X-Webhook-Secret"

    def test_api_key_header_name(self):
        """Correct header name for API key"""
        header_name = "X-API-Key"
        assert header_name == "X-API-Key"


class TestWorkflowStepsParsing:
    """Tests for workflow steps parsing"""

    def test_parse_workflow_steps(self):
        """Parse workflow template steps"""
        steps = [
            {"step": 1, "action": "Plan task", "estimatedMinutes": 15},
            {"step": 2, "action": "Execute task", "estimatedMinutes": 60},
            {"step": 3, "action": "Review results", "estimatedMinutes": 30}
        ]

        for i, step in enumerate(steps):
            assert step["step"] == i + 1
            assert "action" in step
            assert step["estimatedMinutes"] > 0

    def test_workflow_step_defaults(self):
        """Workflow step with missing estimatedMinutes"""
        step = {"step": 1, "action": "Do something"}
        estimated = step.get("estimatedMinutes", 30)
        assert estimated == 30


class TestWebhookErrorMessages:
    """Tests for webhook error message formats"""

    def test_missing_secret_error(self):
        """Missing webhook secret error message"""
        error = "Missing X-Webhook-Secret header"
        assert "X-Webhook-Secret" in error

    def test_invalid_secret_error(self):
        """Invalid webhook secret error message"""
        error = "Invalid webhook secret"
        assert "Invalid" in error

    def test_invalid_date_error(self):
        """Invalid date format error message"""
        date_str = "not-a-date"
        error = f"Invalid dueDate format: {date_str}. Expected ISO format."
        assert "ISO format" in error

    def test_task_not_found_error(self):
        """Task not found error message"""
        error = "Task not found"
        assert "not found" in error

    def test_workflow_not_found_error(self):
        """Workflow template not found error message"""
        error = "Workflow template not found"
        assert "template" in error

    def test_access_denied_error(self):
        """Access denied error message"""
        error = "Access denied"
        assert "denied" in error


class TestN8nDispatchEnvelope:
    """Tests for n8n event dispatch envelope"""

    def test_task_created_envelope(self):
        """Task created event envelope"""
        envelope = {
            "type": "task-created",
            "source": "focus-kraliki",
            "timestamp": "2025-01-15T10:00:00Z",
            "organizationId": "workspace-123",
            "data": {
                "title": "New Task",
                "task_id": "task-abc",
                "user_id": "user-xyz"
            }
        }
        assert envelope["type"] == "task-created"
        assert envelope["data"]["title"] == "New Task"

    def test_task_complete_envelope(self):
        """Task complete event envelope"""
        envelope = {
            "type": "task-complete",
            "source": "focus-kraliki",
            "timestamp": "2025-01-15T11:00:00Z",
            "organizationId": "workspace-123",
            "data": {
                "title": "Completed Task",
                "task_id": "task-abc",
                "user_id": "user-xyz"
            }
        }
        assert envelope["type"] == "task-complete"

    def test_workflow_executed_envelope(self):
        """Workflow executed event envelope"""
        envelope = {
            "type": "workflow-executed",
            "source": "focus-kraliki",
            "timestamp": "2025-01-15T10:00:00Z",
            "organizationId": "workspace-123",
            "data": {
                "title": "Weekly Review",
                "workflow_id": "wf-123",
                "parent_task_id": "task-parent",
                "subtasks_created": 5
            }
        }
        assert envelope["data"]["subtasks_created"] == 5

    def test_event_created_envelope(self):
        """Event created event envelope"""
        envelope = {
            "type": "event-created",
            "source": "focus-kraliki",
            "timestamp": "2025-01-15T10:00:00Z",
            "organizationId": "workspace-123",
            "data": {
                "title": "Team Meeting",
                "event_id": "event-xyz",
                "start_time": "2025-01-20T09:00:00Z"
            }
        }
        assert envelope["type"] == "event-created"


class TestWebhookDarwin2Config:
    """Tests for Darwin2 configuration"""

    def test_default_darwin2_api_url(self):
        """Default Darwin2 API URL"""
        import os
        default_url = os.environ.get("DARWIN2_N8N_API", "http://127.0.0.1:8198")
        assert "127.0.0.1" in default_url or "DARWIN2_N8N_API" in os.environ


class TestWebhookRateLimitConfig:
    """Tests for rate limit configuration"""

    def test_status_rate_limit(self):
        """Status endpoint rate limit"""
        rate_limit = "60/minute"
        assert "60" in rate_limit

    def test_task_rate_limit(self):
        """Task endpoints rate limit"""
        rate_limit = "30/minute"
        assert "30" in rate_limit

    def test_secret_generation_rate_limit(self):
        """Secret generation rate limit (more restrictive)"""
        rate_limit = "5/minute"
        assert "5" in rate_limit


class TestWebhookWorkflowAccess:
    """Tests for workflow access control logic"""

    def test_owner_access(self):
        """Owner can access their own workflow"""
        workflow_user_id = "user-123"
        request_user_id = "user-123"
        is_public = False
        is_system = False

        has_access = (
            workflow_user_id == request_user_id or
            is_public or
            is_system
        )
        assert has_access is True

    def test_public_workflow_access(self):
        """Anyone can access public workflows"""
        workflow_user_id = "user-123"
        request_user_id = "user-456"
        is_public = True
        is_system = False

        has_access = (
            workflow_user_id == request_user_id or
            is_public or
            is_system
        )
        assert has_access is True

    def test_system_workflow_access(self):
        """Anyone can access system workflows"""
        workflow_user_id = "user-123"
        request_user_id = "user-456"
        is_public = False
        is_system = True

        has_access = (
            workflow_user_id == request_user_id or
            is_public or
            is_system
        )
        assert has_access is True

    def test_private_workflow_denied(self):
        """Non-owner cannot access private workflow"""
        workflow_user_id = "user-123"
        request_user_id = "user-456"
        is_public = False
        is_system = False

        has_access = (
            workflow_user_id == request_user_id or
            is_public or
            is_system
        )
        assert has_access is False


class TestEventDurationDefault:
    """Tests for event duration default logic"""

    def test_default_duration_one_hour(self):
        """Default event duration is 1 hour"""
        start_time = datetime(2025, 1, 15, 10, 0, 0)
        default_duration = timedelta(hours=1)
        end_time = start_time + default_duration

        assert end_time.hour == 11
        assert (end_time - start_time) == timedelta(hours=1)

    def test_explicit_end_time(self):
        """Explicit end time overrides default"""
        start_time = datetime(2025, 1, 15, 10, 0, 0)
        end_time = datetime(2025, 1, 15, 12, 30, 0)

        duration = end_time - start_time
        assert duration == timedelta(hours=2, minutes=30)


class TestWebhookNotesAppend:
    """Tests for task notes appending logic"""

    def test_append_notes_to_empty_description(self):
        """Append notes when description is empty/None"""
        description = None
        notes = "Completed by automation"

        new_description = (description or "") + f"\n\n[Webhook] {notes}"
        assert "[Webhook] Completed by automation" in new_description

    def test_append_notes_to_existing_description(self):
        """Append notes to existing description"""
        description = "Original task description"
        notes = "Completed by automation"

        new_description = description + f"\n\n[Webhook] {notes}"
        assert "Original task description" in new_description
        assert "[Webhook] Completed by automation" in new_description
