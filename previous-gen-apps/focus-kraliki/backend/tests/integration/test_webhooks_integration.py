"""
Integration tests for Webhooks Router
Tests actual endpoint calls with database interactions
"""

import pytest
from datetime import datetime
from httpx import AsyncClient

from app.core.security_v2 import generate_id
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.event import Event
from app.models.workflow_template import WorkflowTemplate


class TestWebhookStatus:
    """Integration tests for webhook status endpoint"""

    @pytest.mark.asyncio
    async def test_webhook_status_returns_healthy(self, async_client: AsyncClient):
        """GET /webhooks/status returns healthy status"""
        response = await async_client.get("/webhooks/status")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "focus-kraliki-webhooks"
        assert "supported_events" in data
        assert len(data["supported_events"]) == 4
        assert "task-create" in data["supported_events"]
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_webhook_status_darwin2_connection_info(self, async_client: AsyncClient):
        """Webhook status includes Darwin2 connection info"""
        response = await async_client.get("/webhooks/status")
        assert response.status_code == 200

        data = response.json()
        assert "darwin2_connected" in data
        assert "darwin2_api" in data


class TestWebhookSecretGeneration:
    """Integration tests for webhook secret generation"""

    @pytest.mark.asyncio
    async def test_generate_secret_without_api_key_fails(self, async_client: AsyncClient):
        """POST /webhooks/config/secret without API key returns 401"""
        response = await async_client.post("/webhooks/config/secret")
        assert response.status_code == 401
        assert "Missing X-API-Key" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_generate_secret_with_invalid_api_key(self, async_client: AsyncClient):
        """POST /webhooks/config/secret with invalid API key returns 401"""
        response = await async_client.post(
            "/webhooks/config/secret",
            headers={"X-API-Key": "invalid-key-12345"}
        )
        assert response.status_code == 401
        assert "Invalid API key" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_generate_secret_with_valid_api_key(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/config/secret with valid API key generates secret"""
        # Set up API key for user
        api_key = f"apikey_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["api_key"] = api_key
        test_user.preferences = prefs
        db.commit()

        response = await async_client.post(
            "/webhooks/config/secret",
            headers={"X-API-Key": api_key}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "webhook_secret" in data
        assert data["webhook_secret"].startswith("whsec_")


class TestWebhookTaskCreate:
    """Integration tests for task creation webhook"""

    @pytest.mark.asyncio
    async def test_create_task_without_secret_fails(self, async_client: AsyncClient):
        """POST /webhooks/task/create without secret returns 422"""
        response = await async_client.post(
            "/webhooks/task/create",
            json={"title": "Test Task"}
        )
        # FastAPI returns 422 for missing required header
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_with_invalid_secret(self, async_client: AsyncClient):
        """POST /webhooks/task/create with invalid secret returns 401"""
        response = await async_client.post(
            "/webhooks/task/create",
            json={"title": "Test Task"},
            headers={"X-Webhook-Secret": "invalid-secret"}
        )
        assert response.status_code == 401
        assert "Invalid webhook secret" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_task_with_valid_secret(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/task/create with valid secret creates task"""
        # Set up webhook secret for user
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        response = await async_client.post(
            "/webhooks/task/create",
            json={"title": "Webhook Created Task"},
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "Task created" in data["message"]
        assert "taskId" in data["data"]

        # Verify task was created in database
        task = db.query(Task).filter(Task.id == data["data"]["taskId"]).first()
        assert task is not None
        assert task.title == "Webhook Created Task"
        assert "webhook" in task.tags

    @pytest.mark.asyncio
    async def test_create_task_with_all_fields(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/task/create with all optional fields"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        response = await async_client.post(
            "/webhooks/task/create",
            json={
                "title": "Full Task",
                "description": "Detailed description",
                "priority": 1,
                "estimatedMinutes": 60,
                "dueDate": "2025-12-31T23:59:59Z",
                "tags": ["urgent", "project-x"]
            },
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 200

        task = db.query(Task).filter(Task.id == response.json()["data"]["taskId"]).first()
        assert task.priority == 1
        assert task.estimatedMinutes == 60
        assert "urgent" in task.tags
        assert "webhook" in task.tags

    @pytest.mark.asyncio
    async def test_create_task_with_invalid_date_format(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/task/create with invalid date returns 400"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        response = await async_client.post(
            "/webhooks/task/create",
            json={
                "title": "Bad Date Task",
                "dueDate": "not-a-valid-date"
            },
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 400
        assert "Invalid dueDate format" in response.json()["detail"]


class TestWebhookTaskComplete:
    """Integration tests for task completion webhook"""

    @pytest.mark.asyncio
    async def test_complete_nonexistent_task(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/task/complete for nonexistent task returns 404"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        response = await async_client.post(
            "/webhooks/task/complete",
            json={"taskId": "nonexistent-task-id"},
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_complete_existing_task(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/task/complete marks task as completed"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        # Create a task first
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Task to Complete",
            status=TaskStatus.PENDING,
            createdAt=datetime.utcnow(),
            tags=[]
        )
        db.add(task)
        db.commit()

        response = await async_client.post(
            "/webhooks/task/complete",
            json={"taskId": task.id},
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "Task completed" in data["message"]

        # Verify task status changed
        db.refresh(task)
        assert task.status == TaskStatus.COMPLETED
        assert task.completedAt is not None

    @pytest.mark.asyncio
    async def test_complete_task_with_notes(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/task/complete appends notes to description"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Task with Notes",
            description="Original description",
            status=TaskStatus.PENDING,
            createdAt=datetime.utcnow(),
            tags=[]
        )
        db.add(task)
        db.commit()

        response = await async_client.post(
            "/webhooks/task/complete",
            json={
                "taskId": task.id,
                "notes": "Completed via automation"
            },
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 200

        db.refresh(task)
        assert "[Webhook] Completed via automation" in task.description


class TestWebhookEventCreate:
    """Integration tests for event creation webhook"""

    @pytest.mark.asyncio
    async def test_create_event_minimal(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/event/create with minimal fields"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        response = await async_client.post(
            "/webhooks/event/create",
            json={
                "title": "Quick Meeting",
                "start_time": "2025-01-15T10:00:00Z"
            },
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "eventId" in data["data"]

        # Verify event was created with default 1-hour duration
        event = db.query(Event).filter(Event.id == data["data"]["eventId"]).first()
        assert event is not None
        assert event.title == "Quick Meeting"
        # End time should be 1 hour after start
        duration = event.end_time - event.start_time
        assert duration.seconds == 3600  # 1 hour

    @pytest.mark.asyncio
    async def test_create_event_full(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/event/create with all fields"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        response = await async_client.post(
            "/webhooks/event/create",
            json={
                "title": "Team Meeting",
                "description": "Weekly sync",
                "start_time": "2025-01-15T10:00:00Z",
                "end_time": "2025-01-15T11:30:00Z",
                "location": "Conference Room A"
            },
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 200

        event = db.query(Event).filter(Event.id == response.json()["data"]["eventId"]).first()
        assert event.description == "Weekly sync"
        assert event.location == "Conference Room A"

    @pytest.mark.asyncio
    async def test_create_event_invalid_date(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/event/create with invalid date returns 400"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        response = await async_client.post(
            "/webhooks/event/create",
            json={
                "title": "Bad Date Event",
                "start_time": "invalid-date"
            },
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]


class TestWebhookWorkflowExecute:
    """Integration tests for workflow execution webhook"""

    @pytest.mark.asyncio
    async def test_execute_nonexistent_workflow(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/workflow/execute for nonexistent workflow returns 404"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        response = await async_client.post(
            "/webhooks/workflow/execute",
            json={"templateId": "nonexistent-template"},
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 404
        assert "Workflow template not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_execute_own_workflow(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/workflow/execute executes user's own workflow"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        # Create workflow template
        template = WorkflowTemplate(
            id=generate_id(),
            userId=test_user.id,
            name="Morning Routine",
            description="Daily startup workflow",
            steps=[
                {"step": 1, "action": "Check email", "estimatedMinutes": 15},
                {"step": 2, "action": "Plan day", "estimatedMinutes": 10}
            ],
            tags=["routine"],
            isPublic=False,
            isSystem=False,
            totalEstimatedMinutes=25,
            usageCount=0
        )
        db.add(template)
        db.commit()

        response = await async_client.post(
            "/webhooks/workflow/execute",
            json={"templateId": template.id},
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["totalTasks"] == 2
        assert len(data["data"]["createdTasks"]) == 2

        # Verify template usage count increased
        db.refresh(template)
        assert template.usageCount == 1

    @pytest.mark.asyncio
    async def test_execute_public_workflow(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/workflow/execute can access public workflows"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        # Create public workflow owned by different user
        other_user = User(
            id=generate_id(),
            email="other@example.com",
            username="otheruser",
            passwordHash="hash",
            organizationId=generate_id()
        )
        db.add(other_user)

        template = WorkflowTemplate(
            id=generate_id(),
            userId=other_user.id,
            name="Public Workflow",
            description="Shared workflow",
            steps=[{"step": 1, "action": "Do task", "estimatedMinutes": 30}],
            tags=[],
            isPublic=True,
            isSystem=False,
            totalEstimatedMinutes=30,
            usageCount=0
        )
        db.add(template)
        db.commit()

        response = await async_client.post(
            "/webhooks/workflow/execute",
            json={"templateId": template.id},
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_execute_private_workflow_denied(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/workflow/execute denies access to others' private workflows"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        # Create private workflow owned by different user
        other_user = User(
            id=generate_id(),
            email="private@example.com",
            username="privateuser",
            passwordHash="hash",
            organizationId=generate_id()
        )
        db.add(other_user)

        template = WorkflowTemplate(
            id=generate_id(),
            userId=other_user.id,
            name="Private Workflow",
            description="Private workflow",
            steps=[{"step": 1, "action": "Secret task", "estimatedMinutes": 30}],
            tags=[],
            isPublic=False,
            isSystem=False,
            totalEstimatedMinutes=30,
            usageCount=0
        )
        db.add(template)
        db.commit()

        response = await async_client.post(
            "/webhooks/workflow/execute",
            json={"templateId": template.id},
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_execute_workflow_with_custom_title(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """POST /webhooks/workflow/execute uses custom title"""
        webhook_secret = f"whsec_{generate_id()}"
        prefs = test_user.preferences or {}
        prefs["webhook_secret"] = webhook_secret
        test_user.preferences = prefs
        db.commit()

        template = WorkflowTemplate(
            id=generate_id(),
            userId=test_user.id,
            name="Template Name",
            description="Description",
            steps=[{"step": 1, "action": "Step", "estimatedMinutes": 10}],
            tags=[],
            isPublic=False,
            isSystem=False,
            totalEstimatedMinutes=10,
            usageCount=0
        )
        db.add(template)
        db.commit()

        response = await async_client.post(
            "/webhooks/workflow/execute",
            json={
                "templateId": template.id,
                "customTitle": "My Custom Workflow Title"
            },
            headers={"X-Webhook-Secret": webhook_secret}
        )
        assert response.status_code == 200

        # Check parent task has custom title
        parent_task = db.query(Task).filter(
            Task.id == response.json()["data"]["parentTaskId"]
        ).first()
        assert parent_task.title == "My Custom Workflow Title"


class TestWebhookCrossFunctionality:
    """Tests for cross-cutting webhook concerns"""

    @pytest.mark.asyncio
    async def test_user_isolation(
        self, async_client: AsyncClient, db, test_user: User
    ):
        """Users can only complete their own tasks"""
        # Set up user 1 with webhook secret
        secret1 = f"whsec_{generate_id()}"
        prefs1 = test_user.preferences or {}
        prefs1["webhook_secret"] = secret1
        test_user.preferences = prefs1
        db.commit()

        # Create another user with their own task
        user2 = User(
            id=generate_id(),
            email="user2@example.com",
            username="user2",
            passwordHash="hash",
            organizationId=generate_id()
        )
        db.add(user2)

        task_user2 = Task(
            id=generate_id(),
            userId=user2.id,
            title="User2 Task",
            status=TaskStatus.PENDING,
            createdAt=datetime.utcnow(),
            tags=[]
        )
        db.add(task_user2)
        db.commit()

        # User1 tries to complete user2's task
        response = await async_client.post(
            "/webhooks/task/complete",
            json={"taskId": task_user2.id},
            headers={"X-Webhook-Secret": secret1}
        )
        assert response.status_code == 404  # Task not found (for this user)
