"""
Projects Router Tests
Tests project CRUD operations, access control, and workspace integration
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.task import Project
from app.models.workspace import Workspace, WorkspaceMember
from app.models.task import Task


class TestListProjects:
    """Test listing projects"""

    @pytest.mark.asyncio
    async def test_list_projects_empty(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should return empty list when user has no projects"""
        response = await async_client.get("/projects", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["projects"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_projects_with_data(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should return user's projects"""
        # Create a project
        from app.core.security import generate_id

        project = Project(
            id=generate_id(),
            userId=test_user.id,
            name="Test Project",
            description="Test Description",
        )
        db.add(project)
        db.commit()

        response = await async_client.get("/projects", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["projects"]) == 1
        assert data["projects"][0]["name"] == "Test Project"

    @pytest.mark.asyncio
    async def test_list_projects_with_limit(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should respect limit parameter"""
        from app.core.security import generate_id

        # Create multiple projects
        for i in range(5):
            project = Project(
                id=generate_id(), userId=test_user.id, name=f"Project {i}"
            )
            db.add(project)
        db.commit()

        response = await async_client.get("/projects?limit=3", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["projects"]) == 3

    @pytest.mark.asyncio
    async def test_list_projects_limit_validation(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should validate limit parameter"""
        # Test with limit > 100
        response = await async_client.get("/projects?limit=101", headers=auth_headers)

        assert response.status_code == 422  # Validation error

        # Test with limit < 1
        response = await async_client.get("/projects?limit=0", headers=auth_headers)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_projects_requires_auth(self, async_client: AsyncClient):
        """Should require authentication"""
        response = await async_client.get("/projects")

        assert response.status_code == 401


class TestCreateProject:
    """Test project creation"""

    @pytest.mark.asyncio
    async def test_create_project_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should create project with valid data"""
        project_data = {
            "name": "New Project",
            "description": "Project description",
            "color": "#FF5733",
            "icon": "folder",
        }

        response = await async_client.post(
            "/projects", json=project_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Project"
        assert data["description"] == "Project description"
        assert data["color"] == "#FF5733"
        assert data["icon"] == "folder"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_project_minimal(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should create project with only required fields"""
        project_data = {"name": "Minimal Project"}

        response = await async_client.post(
            "/projects", json=project_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Project"

    @pytest.mark.asyncio
    async def test_create_project_with_workspace(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should create project in specified workspace"""
        from app.core.security import generate_id

        # Create a workspace
        workspace = Workspace(
            id=generate_id(), name="Test Workspace", ownerId=test_user.id
        )
        db.add(workspace)

        # Add user as member
        member = WorkspaceMember(
            id=generate_id(),
            userId=test_user.id,
            workspaceId=workspace.id,
            role="owner",
        )
        db.add(member)
        db.commit()

        project_data = {"name": "Workspace Project", "workspaceId": workspace.id}

        response = await async_client.post(
            "/projects", json=project_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["workspaceId"] == workspace.id

    @pytest.mark.asyncio
    async def test_create_project_invalid_data(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should reject invalid project data"""
        project_data = {
            # Missing required "name" field
            "description": "No name"
        }

        response = await async_client.post(
            "/projects", json=project_data, headers=auth_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_project_requires_auth(self, async_client: AsyncClient):
        """Should require authentication"""
        project_data = {"name": "Test Project"}

        response = await async_client.post("/projects", json=project_data)

        assert response.status_code == 401


class TestGetProject:
    """Test retrieving a single project"""

    @pytest.mark.asyncio
    async def test_get_project_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should retrieve project by ID"""
        from app.core.security import generate_id

        project = Project(
            id=generate_id(),
            userId=test_user.id,
            name="Test Project",
            description="Test Description",
        )
        db.add(project)
        db.commit()

        response = await async_client.get(
            f"/projects/{project.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project.id
        assert data["name"] == "Test Project"
        assert data["taskCount"] == 0

    @pytest.mark.asyncio
    async def test_get_project_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should return 404 for non-existent project"""
        response = await async_client.get(
            "/projects/nonexistent-id", headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_project_unauthorized(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should prevent access to other user's project"""
        from app.core.security import generate_id
        from app.core.security_v2 import get_password_hash

        # Create another user
        other_user = User(
            id=generate_id(),
            email="other@example.com",
            hashedPassword=get_password_hash("password123"),
            firstName="Other",
            lastName="User",
        )
        db.add(other_user)

        # Create project for other user
        project = Project(
            id=generate_id(), userId=other_user.id, name="Other User Project"
        )
        db.add(project)
        db.commit()

        response = await async_client.get(
            f"/projects/{project.id}", headers=auth_headers
        )

        assert response.status_code == 404  # Treated as not found for security

    @pytest.mark.asyncio
    async def test_get_project_task_count(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should include task count in response"""
        from app.core.security import generate_id

        project = Project(
            id=generate_id(), userId=test_user.id, name="Project with Tasks"
        )
        db.add(project)

        # Add tasks
        for i in range(3):
            task = Task(
                id=generate_id(),
                userId=test_user.id,
                projectId=project.id,
                title=f"Task {i}",
            )
            db.add(task)

        db.commit()

        response = await async_client.get(
            f"/projects/{project.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["taskCount"] == 3


class TestUpdateProject:
    """Test project updates"""

    @pytest.mark.asyncio
    async def test_update_project_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should update project fields"""
        from app.core.security import generate_id

        project = Project(
            id=generate_id(),
            userId=test_user.id,
            name="Original Name",
            description="Original Description",
        )
        db.add(project)
        db.commit()

        update_data = {"name": "Updated Name", "description": "Updated Description"}

        response = await async_client.patch(
            f"/projects/{project.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated Description"

    @pytest.mark.asyncio
    async def test_update_project_partial(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should update only provided fields"""
        from app.core.security import generate_id

        project = Project(
            id=generate_id(),
            userId=test_user.id,
            name="Original Name",
            description="Original Description",
            color="#FF5733",
        )
        db.add(project)
        db.commit()

        update_data = {"name": "New Name"}

        response = await async_client.patch(
            f"/projects/{project.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "Original Description"  # Unchanged
        assert data["color"] == "#FF5733"  # Unchanged

    @pytest.mark.asyncio
    async def test_update_project_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should return 404 for non-existent project"""
        update_data = {"name": "Updated"}

        response = await async_client.patch(
            "/projects/nonexistent-id", json=update_data, headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project_unauthorized(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should prevent updating other user's project"""
        from app.core.security import generate_id
        from app.core.security_v2 import get_password_hash

        other_user = User(
            id=generate_id(),
            email="other@example.com",
            hashedPassword=get_password_hash("password123"),
            firstName="Other",
            lastName="User",
        )
        db.add(other_user)

        project = Project(
            id=generate_id(), userId=other_user.id, name="Other User Project"
        )
        db.add(project)
        db.commit()

        update_data = {"name": "Hacked Name"}

        response = await async_client.patch(
            f"/projects/{project.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project_empty_body(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should handle empty update body"""
        from app.core.security import generate_id

        project = Project(id=generate_id(), userId=test_user.id, name="Original Name")
        db.add(project)
        db.commit()

        response = await async_client.patch(
            f"/projects/{project.id}", json={}, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Original Name"  # Unchanged


class TestDeleteProject:
    """Test project deletion"""

    @pytest.mark.asyncio
    async def test_delete_project_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should delete project"""
        from app.core.security import generate_id

        project = Project(id=generate_id(), userId=test_user.id, name="To Delete")
        db.add(project)
        db.commit()

        response = await async_client.delete(
            f"/projects/{project.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deletedId"] == project.id

        # Verify deletion
        deleted = db.query(Project).filter(Project.id == project.id).first()
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_project_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should return 404 for non-existent project"""
        response = await async_client.delete(
            "/projects/nonexistent-id", headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project_unauthorized(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should prevent deleting other user's project"""
        from app.core.security import generate_id
        from app.core.security_v2 import get_password_hash

        other_user = User(
            id=generate_id(),
            email="other@example.com",
            hashedPassword=get_password_hash("password123"),
            firstName="Other",
            lastName="User",
        )
        db.add(other_user)

        project = Project(
            id=generate_id(), userId=other_user.id, name="Other User Project"
        )
        db.add(project)
        db.commit()

        response = await async_client.delete(
            f"/projects/{project.id}", headers=auth_headers
        )

        assert response.status_code == 404

        # Verify project still exists
        not_deleted = db.query(Project).filter(Project.id == project.id).first()
        assert not_deleted is not None


class TestProjectWorkspaceIntegration:
    """Test project workspace integration and access control"""

    @pytest.mark.asyncio
    async def test_list_workspace_projects(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should list projects filtered by workspace"""
        from app.core.security import generate_id

        # Create workspace
        workspace = Workspace(
            id=generate_id(), name="Test Workspace", ownerId=test_user.id
        )
        db.add(workspace)

        # Add user as member
        member = WorkspaceMember(
            id=generate_id(),
            userId=test_user.id,
            workspaceId=workspace.id,
            role="member",
        )
        db.add(member)

        # Create projects in workspace
        ws_project = Project(
            id=generate_id(),
            userId=test_user.id,
            name="Workspace Project",
            workspaceId=workspace.id,
        )
        db.add(ws_project)

        # Create project outside workspace
        other_project = Project(
            id=generate_id(), userId=test_user.id, name="Other Project"
        )
        db.add(other_project)
        db.commit()

        response = await async_client.get(
            f"/projects?workspaceId={workspace.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["projects"]) == 1
        assert data["projects"][0]["id"] == ws_project.id

    @pytest.mark.asyncio
    async def test_workspace_access_control(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should prevent access to workspace projects without membership"""
        from app.core.security import generate_id
        from app.core.security_v2 import get_password_hash

        # Create other user and workspace
        other_user = User(
            id=generate_id(),
            email="other@example.com",
            hashedPassword=get_password_hash("password123"),
            firstName="Other",
            lastName="User",
        )
        db.add(other_user)

        workspace = Workspace(
            id=generate_id(), name="Other Workspace", ownerId=other_user.id
        )
        db.add(workspace)

        project = Project(
            id=generate_id(),
            userId=other_user.id,
            workspaceId=workspace.id,
            name="Workspace Project",
        )
        db.add(project)
        db.commit()

        response = await async_client.get(
            f"/projects?workspaceId={workspace.id}", headers=auth_headers
        )

        assert response.status_code == 401 or response.status_code == 403
