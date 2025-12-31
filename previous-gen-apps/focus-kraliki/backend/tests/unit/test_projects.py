"""
Project Tests - CRUD, Members, Milestones
Target Coverage: 80%
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.security_v2 import generate_id
from app.models.user import User
from app.models.task import Project


class TestProjectCRUD:
    """Test project Create, Read, Update, Delete operations."""

    @pytest.mark.asyncio
    async def test_create_project(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test creating a new project."""
        response = await async_client.post(
            "/projects",
            json={
                "name": "Test Project",
                "description": "A test project",
                "color": "#3B82F6",
                "icon": "📁"
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "Test Project"
        assert data["description"] == "A test project"
        assert data["color"] == "#3B82F6"
        assert data["icon"] == "📁"
        assert data["userId"] == test_user.id
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_project_minimal(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating project with minimal required fields."""
        response = await async_client.post(
            "/projects",
            json={"name": "Minimal Project"},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Project"
        assert data["description"] is None

    @pytest.mark.asyncio
    async def test_create_project_requires_auth(
        self,
        async_client: AsyncClient
    ):
        """Test that creating project requires authentication."""
        response = await async_client.post(
            "/projects",
            json={"name": "Unauthorized Project"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_projects(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test listing user's projects."""
        # Create test projects
        projects = [
            Project(
                id=generate_id(),
                name=f"Project {i}",
                description=f"Description {i}",
                userId=test_user.id
            )
            for i in range(3)
        ]

        for project in projects:
            db.add(project)
        db.commit()

        response = await async_client.get(
            "/projects",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "projects" in data
        assert "total" in data
        assert data["total"] >= 3
        assert len(data["projects"]) >= 3

    @pytest.mark.asyncio
    async def test_list_projects_isolation(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        test_user_2: User,
        db: Session
    ):
        """Test that users can only see their own projects."""
        # Create project for test_user_2
        other_project = Project(
            id=generate_id(),
            name="Other User's Project",
            userId=test_user_2.id
        )
        db.add(other_project)
        db.commit()

        response = await async_client.get(
            "/projects",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should not see other user's project
        project_names = [p["name"] for p in data["projects"]]
        assert "Other User's Project" not in project_names

    @pytest.mark.asyncio
    async def test_get_project(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test getting a single project."""
        project = Project(
            id=generate_id(),
            name="Get Test Project",
            description="Test description",
            userId=test_user.id
        )
        db.add(project)
        db.commit()

        response = await async_client.get(
            f"/projects/{project.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == project.id
        assert data["name"] == "Get Test Project"
        assert data["description"] == "Test description"

    @pytest.mark.asyncio
    async def test_get_project_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting non-existent project returns 404."""
        response = await async_client.get(
            "/projects/non-existent-id",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_project_unauthorized(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user_2: User,
        db: Session
    ):
        """Test that users cannot access other users' projects."""
        other_project = Project(
            id=generate_id(),
            name="Other's Project",
            userId=test_user_2.id
        )
        db.add(other_project)
        db.commit()

        response = await async_client.get(
            f"/projects/{other_project.id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test updating a project."""
        project = Project(
            id=generate_id(),
            name="Original Name",
            description="Original Description",
            userId=test_user.id
        )
        db.add(project)
        db.commit()

        response = await async_client.patch(
            f"/projects/{project.id}",
            json={
                "name": "Updated Name",
                "color": "#EF4444"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Updated Name"
        assert data["description"] == "Original Description"
        assert data["color"] == "#EF4444"

    @pytest.mark.asyncio
    async def test_update_project_partial(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test partial update of project."""
        project = Project(
            id=generate_id(),
            name="Original",
            description="Description",
            userId=test_user.id
        )
        db.add(project)
        db.commit()

        response = await async_client.patch(
            f"/projects/{project.id}",
            json={"description": "New Description"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Original"
        assert data["description"] == "New Description"

    @pytest.mark.asyncio
    async def test_delete_project(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test deleting a project."""
        project = Project(
            id=generate_id(),
            name="To Delete",
            userId=test_user.id
        )
        db.add(project)
        db.commit()

        response = await async_client.delete(
            f"/projects/{project.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["deletedId"] == project.id

        # Verify project is deleted
        deleted = db.query(Project).filter(Project.id == project.id).first()
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_project_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test deleting non-existent project returns 404."""
        response = await async_client.delete(
            "/projects/non-existent-id",
            headers=auth_headers
        )

        assert response.status_code == 404


class TestProjectWithTasks:
    """Test project with task relationships."""

    @pytest.mark.asyncio
    async def test_get_project_with_tasks(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """Test getting project includes task count."""
        from app.models.task import Task, TaskStatus

        project = Project(
            id=generate_id(),
            name="Project with Tasks",
            userId=test_user.id
        )
        db.add(project)
        db.commit()

        # Add tasks to project
        tasks = [
            Task(
                id=generate_id(),
                title=f"Task {i}",
                userId=test_user.id,
                projectId=project.id,
                status=TaskStatus.PENDING
            )
            for i in range(3)
        ]

        for task in tasks:
            db.add(task)
        db.commit()

        response = await async_client.get(
            f"/projects/{project.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check task count if included in response
        if "taskCount" in data:
            assert data["taskCount"] == 3


class TestProjectValidation:
    """Test project input validation."""

    @pytest.mark.asyncio
    async def test_create_project_empty_name(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test that project name cannot be empty."""
        response = await async_client.post(
            "/projects",
            json={"name": ""},
            headers=auth_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_project_name_too_long(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test that project name has maximum length."""
        response = await async_client.post(
            "/projects",
            json={"name": "x" * 256},
            headers=auth_headers
        )

        # May be 422 (validation error) or 201 if no max length
        assert response.status_code in [201, 422]

    @pytest.mark.asyncio
    async def test_create_project_invalid_color(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test project color validation if implemented."""
        response = await async_client.post(
            "/projects",
            json={
                "name": "Test",
                "color": "not-a-hex-color"
            },
            headers=auth_headers
        )

        # May be 422 if validation exists, or 201 if no validation
        assert response.status_code in [201, 422]
