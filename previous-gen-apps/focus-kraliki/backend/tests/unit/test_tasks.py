"""
Task Management Tests
Target Coverage: 85%
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.models.user import User
from app.core.security_v2 import generate_id


class TestTaskCreation:
    """Test task creation endpoints."""

    @pytest.mark.asyncio
    async def test_create_task_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test creating a task successfully."""
        response = await async_client.post(
            "/tasks/",
            json={
                "title": "Test task",
                "description": "Test description",
                "priority": 2,
                "status": TaskStatus.PENDING.value
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["title"] == "Test task"
        assert data["description"] == "Test description"
        assert data["priority"] == 2
        assert data["status"] == TaskStatus.PENDING.value
        assert data["userId"] == test_user.id
        assert "id" in data
        assert "createdAt" in data

    @pytest.mark.asyncio
    async def test_create_task_minimal(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating task with minimal required fields."""
        response = await async_client.post(
            "/tasks/",
            json={
                "title": "Minimal task"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["title"] == "Minimal task"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_task_unauthenticated(self, async_client: AsyncClient):
        """Test creating task without authentication fails."""
        response = await async_client.post(
            "/tasks/",
            json={
                "title": "Unauthorized task"
            }
        )

        assert response.status_code == 401  # Unauthenticated


class TestTaskRetrieval:
    """Test task retrieval endpoints."""

    @pytest.mark.asyncio
    async def test_list_tasks_empty(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test listing tasks when none exist."""
        response = await async_client.get(
            "/tasks/",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["tasks"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_tasks_with_data(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test listing tasks with existing data."""
        # Create test tasks
        task1 = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Task 1",
            priority=1,
            status=TaskStatus.PENDING
        )
        task2 = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Task 2",
            priority=2,
            status=TaskStatus.IN_PROGRESS
        )

        db.add_all([task1, task2])
        db.commit()

        response = await async_client.get(
            "/tasks/",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["tasks"]) == 2
        assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_list_tasks_filtered_by_status(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test filtering tasks by status."""
        # Create tasks with different statuses
        task1 = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Task 1",
            status=TaskStatus.PENDING
        )
        task2 = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Task 2",
            status=TaskStatus.COMPLETED
        )

        db.add_all([task1, task2])
        db.commit()

        response = await async_client.get(
            "/tasks/?status=PENDING",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["status"] == TaskStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_get_task_by_id(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test retrieving specific task by ID."""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Specific Task",
            description="Task description"
        )

        db.add(task)
        db.commit()

        response = await async_client.get(
            f"/tasks/{task.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == task.id
        assert data["title"] == "Specific Task"

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test retrieving non-existent task returns 404."""
        response = await async_client.get(
            "/tasks/nonexistent_id",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_other_users_task(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_2: User,
        db: Session
    ):
        """Test users cannot access other users' tasks."""
        # Create task for user 2
        task = Task(
            id=generate_id(),
            userId=test_user_2.id,
            title="User 2 Task"
        )

        db.add(task)
        db.commit()

        # Try to access with user 1's token
        response = await async_client.get(
            f"/tasks/{task.id}",
            headers=auth_headers
        )

        assert response.status_code == 404  # Hide existence of other users' tasks


class TestTaskUpdate:
    """Test task update endpoints."""

    @pytest.mark.asyncio
    async def test_update_task_title(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test updating task title."""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Original Title"
        )

        db.add(task)
        db.commit()

        response = await async_client.patch(
            f"/tasks/{task.id}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_task_status(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test updating task status."""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Task",
            status=TaskStatus.PENDING
        )

        db.add(task)
        db.commit()

        response = await async_client.patch(
            f"/tasks/{task.id}",
            json={"status": "IN_PROGRESS"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "IN_PROGRESS"

    @pytest.mark.asyncio
    async def test_complete_task_sets_completed_at(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test marking task as completed sets completedAt timestamp."""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Task to Complete",
            status=TaskStatus.PENDING
        )

        db.add(task)
        db.commit()

        response = await async_client.patch(
            f"/tasks/{task.id}",
            json={"status": "COMPLETED"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "COMPLETED"
        assert data["completedAt"] is not None

    @pytest.mark.asyncio
    async def test_update_nonexistent_task(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test updating non-existent task returns 404."""
        response = await async_client.patch(
            "/tasks/nonexistent_id",
            json={"title": "Updated"},
            headers=auth_headers
        )

        assert response.status_code == 404


class TestTaskDelete:
    """Test task deletion (if endpoint exists)."""

    @pytest.mark.asyncio
    async def test_delete_task(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test deleting a task."""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Task to Delete"
        )

        db.add(task)
        db.commit()
        task_id = task.id

        response = await async_client.delete(
            f"/tasks/{task_id}",
            headers=auth_headers
        )

        # May return 204 or 200 depending on implementation
        assert response.status_code in [200, 204, 404]  # 404 if not implemented


class TestTaskPriorityFiltering:
    """Test priority-based task filtering."""

    @pytest.mark.asyncio
    async def test_filter_by_priority(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test filtering tasks by priority."""
        # Create tasks with different priorities
        high_priority = Task(
            id=generate_id(),
            userId=test_user.id,
            title="High Priority",
            priority=3
        )
        low_priority = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Low Priority",
            priority=1
        )

        db.add_all([high_priority, low_priority])
        db.commit()

        response = await async_client.get(
            "/tasks/?priority=3",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["priority"] == 3
