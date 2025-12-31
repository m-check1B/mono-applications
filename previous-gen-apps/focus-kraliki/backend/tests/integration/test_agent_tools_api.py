"""
Agent Tools API Integration Tests
Tests for II-Agent HTTP API endpoints - all 7 agent tools.
Target Coverage: 95%
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.user import User
from app.models.knowledge_item import KnowledgeItem
from app.models.task import Task, TaskStatus, Project


class TestAgentToolsAuthentication:
    """Test agent token authentication."""

    @pytest.mark.asyncio
    async def test_agent_tools_require_auth(
        self,
        async_client: AsyncClient
    ):
        """Test that agent tools endpoints require authentication."""
        endpoints = [
            "/agent-tools/knowledge/create",
            "/agent-tools/knowledge",
            "/agent-tools/tasks",
        ]

        for endpoint in endpoints:
            response = await async_client.get(endpoint)
            assert response.status_code in [401, 405]  # 405 for POST-only endpoints

    @pytest.mark.asyncio
    async def test_agent_token_valid(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        test_user_with_knowledge_types: User
    ):
        """Test that valid agent token works."""
        response = await async_client.get(
            "/agent-tools/knowledge",
            headers=agent_headers
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_regular_token_works_for_agent_tools(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_with_knowledge_types: User
    ):
        """Test that regular user tokens also work for agent tools."""
        response = await async_client.get(
            "/agent-tools/knowledge",
            headers=auth_headers
        )

        assert response.status_code == 200


class TestAgentKnowledgeTools:
    """Test II-Agent knowledge management tools."""

    @pytest.mark.asyncio
    async def test_create_knowledge_item(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        knowledge_type_ids: dict,
        test_user_with_knowledge_types: User
    ):
        """Test agent creating a knowledge item."""
        ideas_id = knowledge_type_ids["Ideas"]

        response = await async_client.post(
            "/agent-tools/knowledge/create",
            json={
                "typeId": ideas_id,
                "title": "Agent-Created Idea",
                "content": "Created by II-Agent",
                "item_metadata": {"source": "ii-agent"}
            },
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["title"] == "Agent-Created Idea"
        assert data["content"] == "Created by II-Agent"
        assert data["typeId"] == ideas_id
        assert data["userId"] == test_user_with_knowledge_types.id
        assert data["item_metadata"]["source"] == "ii-agent"
        assert data["completed"] is False

    @pytest.mark.asyncio
    async def test_create_knowledge_item_invalid_type(
        self,
        async_client: AsyncClient,
        agent_headers: dict
    ):
        """Test creating knowledge item with invalid typeId fails."""
        response = await async_client.post(
            "/agent-tools/knowledge/create",
            json={
                "typeId": "nonexistent-type-id",
                "title": "Should Fail"
            },
            headers=agent_headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_knowledge_item(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        knowledge_type_ids: dict,
        db: Session,
        test_user_with_knowledge_types: User
    ):
        """Test agent updating a knowledge item."""
        from app.core.security import generate_id

        ideas_id = knowledge_type_ids["Ideas"]

        # Create item directly in DB
        item = KnowledgeItem(
            id=generate_id(),
            userId=test_user_with_knowledge_types.id,
            typeId=ideas_id,
            title="Original Title",
            content="Original Content",
            completed=False
        )
        db.add(item)
        db.commit()

        # Update via agent API
        response = await async_client.patch(
            f"/agent-tools/knowledge/{item.id}",
            json={
                "title": "Updated by Agent",
                "completed": True
            },
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["title"] == "Updated by Agent"
        assert data["content"] == "Original Content"  # Unchanged
        assert data["completed"] is True

    @pytest.mark.asyncio
    async def test_update_knowledge_item_not_found(
        self,
        async_client: AsyncClient,
        agent_headers: dict
    ):
        """Test updating non-existent knowledge item fails."""
        response = await async_client.patch(
            "/agent-tools/knowledge/nonexistent-id",
            json={"title": "Should Fail"},
            headers=agent_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_knowledge_items(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        knowledge_type_ids: dict,
        db: Session,
        test_user_with_knowledge_types: User
    ):
        """Test agent listing knowledge items."""
        from app.core.security import generate_id

        ideas_id = knowledge_type_ids["Ideas"]
        notes_id = knowledge_type_ids["Notes"]

        # Create items
        for i in range(3):
            item = KnowledgeItem(
                id=generate_id(),
                userId=test_user_with_knowledge_types.id,
                typeId=ideas_id if i < 2 else notes_id,
                title=f"Item {i}",
                completed=False
            )
            db.add(item)
        db.commit()

        # List all items
        response = await async_client.get(
            "/agent-tools/knowledge",
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 3
        assert len(data["items"]) == 3

    @pytest.mark.asyncio
    async def test_list_knowledge_items_filtered(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        knowledge_type_ids: dict,
        db: Session,
        test_user_with_knowledge_types: User
    ):
        """Test agent listing knowledge items with type filter."""
        from app.core.security import generate_id

        ideas_id = knowledge_type_ids["Ideas"]
        notes_id = knowledge_type_ids["Notes"]

        # Create items of different types
        item1 = KnowledgeItem(
            id=generate_id(),
            userId=test_user_with_knowledge_types.id,
            typeId=ideas_id,
            title="Idea 1",
            completed=False
        )
        item2 = KnowledgeItem(
            id=generate_id(),
            userId=test_user_with_knowledge_types.id,
            typeId=notes_id,
            title="Note 1",
            completed=False
        )
        db.add(item1)
        db.add(item2)
        db.commit()

        # Filter by Ideas type
        response = await async_client.get(
            f"/agent-tools/knowledge?typeId={ideas_id}",
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 1
        assert data["items"][0]["typeId"] == ideas_id


class TestAgentTaskTools:
    """Test II-Agent task management tools using KnowledgeItems."""

    @pytest.mark.asyncio
    async def test_create_task(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        test_user_with_knowledge_types: User
    ):
        """Test agent creating a task."""
        response = await async_client.post(
            "/agent-tools/tasks",
            json={
                "title": "Agent-Created Task",
                "description": "This task was created by II-Agent",
                "priority": 3,
                "estimatedMinutes": 30
            },
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["title"] == "Agent-Created Task"
        assert data["description"] == "This task was created by II-Agent"
        assert data["priority"] == 3
        assert data["estimatedMinutes"] == 30
        assert data["status"] == "PENDING"
        assert data["userId"] == test_user_with_knowledge_types.id

    @pytest.mark.asyncio
    async def test_create_task_with_project(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        db: Session,
        test_user_with_knowledge_types: User
    ):
        """Test agent creating a task with project association."""
        from app.core.security import generate_id

        # Create project
        project = Project(
            id=generate_id(),
            userId=test_user_with_knowledge_types.id,
            name="Test Project"
        )
        db.add(project)
        db.commit()

        # Create task with project
        response = await async_client.post(
            "/agent-tools/tasks",
            json={
                "title": "Project Task",
                "projectId": project.id
            },
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["projectId"] == project.id

    @pytest.mark.asyncio
    async def test_create_task_invalid_project(
        self,
        async_client: AsyncClient,
        agent_headers: dict
    ):
        """Test creating task with invalid projectId fails."""
        response = await async_client.post(
            "/agent-tools/tasks",
            json={
                "title": "Task",
                "projectId": "nonexistent-project-id"
            },
            headers=agent_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_task(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        db: Session,
        test_user_with_knowledge_types: User
    ):
        """Test agent updating a task."""
        # Create task via API to ensure it's a KnowledgeItem
        create_res = await async_client.post(
            "/agent-tools/tasks",
            json={
                "title": "Original Task",
                "priority": 1
            },
            headers=agent_headers
        )
        assert create_res.status_code == 200
        task_id = create_res.json()["id"]

        # Update task
        response = await async_client.patch(
            f"/agent-tools/tasks/{task_id}",
            json={
                "title": "Updated by Agent",
                "status": "IN_PROGRESS",
                "priority": 5
            },
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["title"] == "Updated by Agent"
        assert data["status"] == "IN_PROGRESS"
        assert data["priority"] == 5

    @pytest.mark.asyncio
    async def test_update_task_to_completed_sets_timestamp(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        db: Session,
        test_user_with_knowledge_types: User
    ):
        """Test that completing a task auto-sets completedAt timestamp."""
        # Create task via API
        create_res = await async_client.post(
            "/agent-tools/tasks",
            json={
                "title": "Task to Complete",
                "priority": 1
            },
            headers=agent_headers
        )
        task_id = create_res.json()["id"]

        # Complete task
        response = await async_client.patch(
            f"/agent-tools/tasks/{task_id}",
            json={"status": "COMPLETED"},
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "COMPLETED"
        assert data["completedAt"] is not None

    @pytest.mark.asyncio
    async def test_list_tasks(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        db: Session,
        test_user_with_knowledge_types: User
    ):
        """Test agent listing tasks."""
        # Create tasks via API
        for i in range(3):
            await async_client.post(
                "/agent-tools/tasks",
                json={
                    "title": f"Task {i}",
                    "priority": 1
                },
                headers=agent_headers
            )

        # List all tasks
        response = await async_client.get(
            "/agent-tools/tasks",
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        # We might have more tasks from other tests, so just check we have at least 3
        assert data["total"] >= 3
        assert len(data["tasks"]) >= 3

    @pytest.mark.asyncio
    async def test_list_tasks_filtered_by_status(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        db: Session,
        test_user_with_knowledge_types: User
    ):
        """Test agent listing tasks filtered by status."""
        # Create tasks with different statuses
        await async_client.post(
            "/agent-tools/tasks",
            json={"title": "Pending Task", "priority": 1},
            headers=agent_headers
        )
        
        # Create and complete a task
        res = await async_client.post(
            "/agent-tools/tasks",
            json={"title": "Completed Task", "priority": 1},
            headers=agent_headers
        )
        task_id = res.json()["id"]
        await async_client.patch(
            f"/agent-tools/tasks/{task_id}",
            json={"status": "COMPLETED"},
            headers=agent_headers
        )

        # Filter by PENDING status
        response = await async_client.get(
            "/agent-tools/tasks?status=PENDING",
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should find at least the one we created
        pending_tasks = [t for t in data["tasks"] if t["title"] == "Pending Task"]
        assert len(pending_tasks) >= 1
        assert data["tasks"][0]["status"] == "PENDING"


class TestAgentProjectTools:
    """Test II-Agent project management tools."""

    @pytest.mark.asyncio
    async def test_create_or_get_project_creates_new(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        test_user_with_knowledge_types: User
    ):
        """Test creating a new project when it doesn't exist."""
        response = await async_client.post(
            "/agent-tools/projects/create-or-get",
            json={
                "name": "New Project",
                "description": "Created by II-Agent",
                "color": "#3B82F6",
                "icon": "📁"
            },
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "New Project"
        assert data["description"] == "Created by II-Agent"
        assert data["color"] == "#3B82F6"
        assert data["icon"] == "📁"
        assert data["userId"] == test_user_with_knowledge_types.id

    @pytest.mark.asyncio
    async def test_create_or_get_project_returns_existing(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        db: Session,
        test_user_with_knowledge_types: User
    ):
        """Test that create-or-get returns existing project with same name."""
        from app.core.security import generate_id

        # Create existing project
        existing_project = Project(
            id=generate_id(),
            userId=test_user_with_knowledge_types.id,
            name="Existing Project",
            description="Already exists"
        )
        db.add(existing_project)
        db.commit()

        # Try to create project with same name
        response = await async_client.post(
            "/agent-tools/projects/create-or-get",
            json={
                "name": "Existing Project",
                "description": "Different description"
            },
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should return existing project (same ID)
        assert data["id"] == existing_project.id
        assert data["description"] == "Already exists"  # Original description

    @pytest.mark.asyncio
    async def test_create_or_get_project_case_sensitive(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        db: Session,
        test_user_with_knowledge_types: User
    ):
        """Test that project name matching is case-sensitive."""
        from app.core.security import generate_id

        # Create project with lowercase name
        project1 = Project(
            id=generate_id(),
            userId=test_user_with_knowledge_types.id,
            name="myproject"
        )
        db.add(project1)
        db.commit()

        # Create project with different case
        response = await async_client.post(
            "/agent-tools/projects/create-or-get",
            json={"name": "MyProject"},
            headers=agent_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should create new project (different ID)
        assert data["id"] != project1.id
        assert data["name"] == "MyProject"


class TestAgentToolsDataIsolation:
    """Test that agent tools respect user data isolation."""

    @pytest.mark.asyncio
    async def test_cannot_access_other_user_knowledge(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        test_user_2: User,
        db: Session
    ):
        """Test that agents cannot access other users' knowledge items."""
        from app.core.security import generate_id
        from app.models.item_type import ItemType

        # Create type and item for user 2
        other_type = ItemType(
            id=generate_id(),
            userId=test_user_2.id,
            name="Other Type"
        )
        db.add(other_type)
        db.commit()

        other_item = KnowledgeItem(
            id=generate_id(),
            userId=test_user_2.id,
            typeId=other_type.id,
            title="Private Item",
            completed=False
        )
        db.add(other_item)
        db.commit()

        # Try to update with user 1's agent token
        response = await async_client.patch(
            f"/agent-tools/knowledge/{other_item.id}",
            json={"title": "Hacked"},
            headers=agent_headers
        )

        assert response.status_code == 404

        # Verify item unchanged
        db.refresh(other_item)
        assert other_item.title == "Private Item"

    @pytest.mark.asyncio
    async def test_cannot_access_other_user_tasks(
        self,
        async_client: AsyncClient,
        agent_headers: dict,
        test_user_2: User,
        db: Session
    ):
        """Test that agents cannot access other users' tasks."""
        from app.core.security import generate_id

        # Create task for user 2
        other_task = Task(
            id=generate_id(),
            userId=test_user_2.id,
            title="Private Task",
            status=TaskStatus.PENDING,
            priority=1
        )
        db.add(other_task)
        db.commit()

        # Try to update with user 1's agent token
        response = await async_client.patch(
            f"/agent-tools/tasks/{other_task.id}",
            json={"title": "Hacked"},
            headers=agent_headers
        )

        assert response.status_code == 404

        # Verify task unchanged
        db.refresh(other_task)
        assert other_task.title == "Private Task"
