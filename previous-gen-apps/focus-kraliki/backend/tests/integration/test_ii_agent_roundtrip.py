"""
Integration Tests for Focus by Kraliki ↔ II-Agent Roundtrip

These tests verify the complete integration between Focus by Kraliki's backend and II-Agent:
1. Agent authentication (token generation)
2. Focus tools calling backend endpoints (knowledge, tasks, projects)
3. End-to-end workflows simulating II-Agent operations

Track 1 - Platform Hardening: Critical path validation
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.item_type import ItemType
from app.models.knowledge_item import KnowledgeItem
from app.models.task import Task, TaskStatus, Project
from app.core.security import generate_id


# ========== Agent Authentication Tests ==========

class TestAgentAuthentication:
    """Test II-Agent authentication and token validation."""

    @pytest.mark.asyncio
    async def test_agent_authentication_with_token(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test that agent can authenticate using generated token"""
        # Try to access a protected endpoint
        response = await async_client.get(
            "/agent-tools/knowledge",
            headers=auth_headers
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_unauthorized_access_to_agent_tools(
        self,
        async_client: AsyncClient
    ):
        """Test that agent tools require authentication"""
        # Try to access agent tools without authentication
        response = await async_client.get("/agent-tools/knowledge")
        assert response.status_code == 401  # Unauthorized

        response = await async_client.post("/agent-tools/knowledge/create", json={})
        assert response.status_code == 401  # Unauthorized

        response = await async_client.post("/agent-tools/tasks", json={})
        assert response.status_code == 401  # Unauthorized


# ========== Knowledge Item Roundtrip Tests ==========

class TestKnowledgeRoundtrip:
    """Test Focus ↔ II-Agent knowledge item operations."""

    @pytest.mark.asyncio
    async def test_create_knowledge_item_via_agent_tools(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        knowledge_type_ids: dict
    ):
        """
        Test II-Agent → Focus by Kraliki: Create knowledge item

        Simulates II-Agent calling the /agent-tools/knowledge/create endpoint
        to create a new knowledge item for the user.
        """
        note_type_id = knowledge_type_ids["Notes"]

        # Simulate II-Agent creating a knowledge item
        payload = {
            "typeId": note_type_id,
            "title": "Meeting Notes: Project Planning",
            "content": "Discussed Q1 goals and roadmap priorities.",
            "item_metadata": {
                "source": "ii-agent",
                "tags": ["planning", "meeting"]
            }
        }

        response = await async_client.post(
            "/agent-tools/knowledge/create",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert data["title"] == payload["title"]
        assert data["content"] == payload["content"]
        assert data["typeId"] == note_type_id
        assert data["item_metadata"] == payload["item_metadata"]

    @pytest.mark.asyncio
    async def test_update_knowledge_item_via_agent_tools(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        knowledge_type_ids: dict,
        test_user: User,
        db: Session
    ):
        """Test II-Agent updating an existing knowledge item"""
        note_type_id = knowledge_type_ids["Notes"]

        # Create a knowledge item first
        knowledge_item = KnowledgeItem(
            id=generate_id(),
            userId=test_user.id,
            typeId=note_type_id,
            title="Original Title",
            content="Original content",
            completed=False
        )
        db.add(knowledge_item)
        db.commit()

        # Simulate II-Agent updating the item
        update_payload = {
            "title": "Updated Title",
            "content": "Updated content with new insights",
            "completed": True
        }

        response = await async_client.patch(
            f"/agent-tools/knowledge/{knowledge_item.id}",
            json=update_payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify updates
        assert data["title"] == update_payload["title"]
        assert data["content"] == update_payload["content"]
        assert data["completed"] == True

    @pytest.mark.asyncio
    async def test_list_knowledge_items_via_agent_tools(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        knowledge_type_ids: dict,
        test_user: User,
        db: Session
    ):
        """Test II-Agent retrieving knowledge items for context"""
        note_type_id = knowledge_type_ids["Notes"]

        # Create multiple knowledge items
        items = [
            KnowledgeItem(
                id=generate_id(),
                userId=test_user.id,
                typeId=note_type_id,
                title=f"Note {i}",
                content=f"Content {i}",
                completed=False
            )
            for i in range(3)
        ]

        for item in items:
            db.add(item)
        db.commit()

        # Simulate II-Agent listing knowledge items
        response = await async_client.get(
            "/agent-tools/knowledge?limit=10",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 3
        assert data["total"] == 3


# ========== Task Roundtrip Tests ==========

class TestTaskRoundtrip:
    """Test Focus ↔ II-Agent task operations using KnowledgeItems."""

    @pytest.mark.asyncio
    async def test_create_task_via_agent_tools(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test II-Agent creating a task for the user"""
        # Simulate II-Agent creating a task
        payload = {
            "title": "Implement II-Agent integration tests",
            "description": "Write comprehensive roundtrip tests for Focus ↔ II-Agent",
            "priority": 3,
            "estimatedMinutes": 120
        }

        response = await async_client.post(
            "/agent-tools/tasks",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response
        assert "id" in data
        assert data["title"] == payload["title"]
        assert data["description"] == payload["description"]
        assert data["priority"] == payload["priority"]
        assert data["estimatedMinutes"] == payload["estimatedMinutes"]
        assert data["status"] == TaskStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_update_task_status_via_agent_tools(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test II-Agent marking a task as completed"""
        # Create a task first via API
        create_res = await async_client.post(
            "/agent-tools/tasks",
            json={
                "title": "Test Task",
                "description": "Task description",
                "priority": 2
            },
            headers=auth_headers
        )
        task_id = create_res.json()["id"]

        # Simulate II-Agent updating task status
        update_payload = {
            "status": TaskStatus.COMPLETED.value
        }

        response = await async_client.patch(
            f"/agent-tools/tasks/{task_id}",
            json=update_payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify update
        assert data["status"] == TaskStatus.COMPLETED.value
        assert data["completedAt"] is not None  # Auto-set by endpoint

    @pytest.mark.asyncio
    async def test_list_tasks_via_agent_tools(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test II-Agent retrieving tasks for planning"""
        # Create multiple tasks via API
        for i in range(4):
            await async_client.post(
                "/agent-tools/tasks",
                json={
                    "title": f"Task {i}",
                    "description": f"Description {i}",
                    "priority": 2
                },
                headers=auth_headers
            )
            
        # Complete some tasks
        # List first to get IDs
        list_res = await async_client.get("/agent-tools/tasks", headers=auth_headers)
        all_tasks = list_res.json()["tasks"]
        
        for i, task in enumerate(all_tasks):
            if i % 2 != 0: # Mark odd ones as completed
                await async_client.patch(
                    f"/agent-tools/tasks/{task['id']}",
                    json={"status": "COMPLETED"},
                    headers=auth_headers
                )

        # Simulate II-Agent listing pending tasks only
        response = await async_client.get(
            f"/agent-tools/tasks?status={TaskStatus.PENDING.value}&limit=10",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "tasks" in data
        assert "total" in data
        # We should have at least 2 pending tasks from this test (plus maybe others from other tests, so check >= 2)
        assert len(data["tasks"]) >= 2 
        assert all(task["status"] == TaskStatus.PENDING.value for task in data["tasks"])


# ========== Project Roundtrip Tests ==========

class TestProjectRoundtrip:
    """Test Focus ↔ II-Agent project operations."""

    @pytest.mark.asyncio
    async def test_create_or_get_project_via_agent_tools(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test II-Agent ensuring a project exists before assigning tasks"""
        # Simulate II-Agent creating a project
        payload = {
            "name": "II-Agent Integration",
            "description": "Integration testing and development",
            "color": "#3B82F6"
        }

        response = await async_client.post(
            "/agent-tools/projects/create-or-get",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response
        assert "id" in data
        assert data["name"] == payload["name"]
        assert data["description"] == payload["description"]
        assert data["color"] == payload["color"]

        # Try to "create" the same project again (should return existing)
        response2 = await async_client.post(
            "/agent-tools/projects/create-or-get",
            json=payload,
            headers=auth_headers
        )

        assert response2.status_code == 200
        data2 = response2.json()

        # Should return the same project
        assert data2["id"] == data["id"]


# ========== Complete Workflow Tests ==========

class TestCompleteWorkflow:
    """Test complete Focus ↔ II-Agent workflows."""

    @pytest.mark.asyncio
    async def test_complete_workflow_create_project_tasks_and_knowledge(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        knowledge_type_ids: dict
    ):
        """
        Test complete Focus ↔ II-Agent workflow

        Simulates II-Agent executing a complex workflow:
        1. Create a project
        2. Create tasks associated with the project
        3. Create knowledge items documenting the work
        4. Update task status
        5. Retrieve all data for summary

        This is the critical roundtrip test for Track 1.
        """
        note_type_id = knowledge_type_ids["Notes"]

        # Step 1: Create a project
        project_response = await async_client.post(
            "/agent-tools/projects/create-or-get",
            json={
                "name": "Website Redesign",
                "description": "Redesign company website",
                "color": "#8B5CF6"
            },
            headers=auth_headers
        )
        assert project_response.status_code == 200
        project = project_response.json()

        # Step 2: Create tasks for the project
        task_titles = [
            "Create wireframes",
            "Design new homepage",
            "Implement responsive layout"
        ]

        task_ids = []
        for title in task_titles:
            task_response = await async_client.post(
                "/agent-tools/tasks",
                json={
                    "title": title,
                    "description": f"Task: {title}",
                    "priority": 2,
                    "projectId": project["id"]
                },
                headers=auth_headers
            )
            assert task_response.status_code == 200
            task_ids.append(task_response.json()["id"])

        # Step 3: Create knowledge items documenting the project
        knowledge_response = await async_client.post(
            "/agent-tools/knowledge/create",
            json={
                "typeId": note_type_id,
                "title": "Website Redesign - Initial Planning",
                "content": "Discussed with team. Prioritizing mobile-first design.",
                "item_metadata": {
                    "project_id": project["id"],
                    "related_tasks": task_ids
                }
            },
            headers=auth_headers
        )
        assert knowledge_response.status_code == 200

        # Step 4: Complete the first task
        update_response = await async_client.patch(
            f"/agent-tools/tasks/{task_ids[0]}",
            json={"status": TaskStatus.COMPLETED.value},
            headers=auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["status"] == TaskStatus.COMPLETED.value

        # Step 5: Retrieve all tasks for the project
        tasks_list_response = await async_client.get(
            f"/agent-tools/tasks?projectId={project['id']}&limit=10",
            headers=auth_headers
        )
        assert tasks_list_response.status_code == 200
        tasks_data = tasks_list_response.json()

        # Verify workflow results
        assert tasks_data["total"] == 3
        completed_tasks = [t for t in tasks_data["tasks"] if t["status"] == TaskStatus.COMPLETED.value]
        assert len(completed_tasks) == 1

        # Step 6: Retrieve knowledge items
        knowledge_list_response = await async_client.get(
            "/agent-tools/knowledge?limit=10",
            headers=auth_headers
        )
        assert knowledge_list_response.status_code == 200
        knowledge_data = knowledge_list_response.json()

        assert knowledge_data["total"] == 1
        assert knowledge_data["items"][0]["title"] == "Website Redesign - Initial Planning"


# ========== Security Tests ==========

class TestSecurityIsolation:
    """Test security and user isolation in II-Agent integration."""

    @pytest.mark.asyncio
    async def test_cross_user_isolation_in_agent_tools(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        test_user_2: User,
        knowledge_type_ids: dict,
        db: Session
    ):
        """
        Test that users cannot access each other's data via agent tools

        Critical security test for multi-user Focus by Kraliki deployment.
        """
        note_type_id = knowledge_type_ids["Notes"]

        # Create knowledge item for user 1
        knowledge1 = KnowledgeItem(
            id=generate_id(),
            userId=test_user.id,
            typeId=note_type_id,
            title="User 1's Private Note",
            content="Secret content",
            completed=False
        )
        db.add(knowledge1)
        db.commit()

        # User 1 tries to access their own data (should work)
        response = await async_client.get(
            f"/agent-tools/knowledge",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "User 1's Private Note"

        # Create token for user 2
        from app.core.ed25519_auth import ed25519_auth
        user2_token = ed25519_auth.create_access_token(data={"sub": test_user_2.id})
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # User 2 tries to access knowledge items (should see 0 items, not user 1's items)
        response = await async_client.get(
            f"/agent-tools/knowledge",
            headers=user2_headers
        )

        assert response.status_code == 200
        data = response.json()

        # User 2 should see 0 items (not user 1's items)
        assert data["total"] == 0
        assert len(data["items"]) == 0
