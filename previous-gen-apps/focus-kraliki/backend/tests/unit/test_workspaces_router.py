"""
Workspaces Router Tests
Tests workspace CRUD, member management, and access control
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole


class TestListWorkspaces:
    """Test listing workspaces"""

    @pytest.mark.asyncio
    async def test_list_workspaces_empty(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should return empty list when user has no workspaces"""
        response = await async_client.get("/workspaces", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["workspaces"] == []

    @pytest.mark.asyncio
    async def test_list_workspaces_with_data(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should return user's workspaces"""
        from app.core.security import generate_id

        workspace = Workspace(
            id=generate_id(),
            name="Test Workspace",
            description="Test Description",
            ownerId=test_user.id,
        )
        db.add(workspace)

        member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=test_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(member)
        db.commit()

        response = await async_client.get("/workspaces", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["workspaces"]) == 1
        assert data["workspaces"][0]["name"] == "Test Workspace"

    @pytest.mark.asyncio
    async def test_list_workspaces_with_member_count(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should include member count in response"""
        from app.core.security import generate_id
        from app.core.security_v2 import get_password_hash

        workspace = Workspace(
            id=generate_id(), name="Test Workspace", ownerId=test_user.id
        )
        db.add(workspace)

        # Add owner
        owner_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=test_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(owner_member)

        # Add another member
        other_user = User(
            id=generate_id(),
            email="member@example.com",
            hashedPassword=get_password_hash("password123"),
            firstName="Member",
            lastName="User",
        )
        db.add(other_user)

        other_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=other_user.id,
            role=WorkspaceRole.MEMBER,
        )
        db.add(other_member)
        db.commit()

        response = await async_client.get("/workspaces", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["workspaces"][0]["memberCount"] == 2

    @pytest.mark.asyncio
    async def test_list_workspaces_requires_auth(self, async_client: AsyncClient):
        """Should require authentication"""
        response = await async_client.get("/workspaces")

        assert response.status_code == 401


class TestCreateWorkspace:
    """Test workspace creation"""

    @pytest.mark.asyncio
    async def test_create_workspace_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should create workspace with valid data"""
        workspace_data = {
            "name": "New Workspace",
            "description": "Workspace description",
            "color": "#FF5733",
        }

        response = await async_client.post(
            "/workspaces", json=workspace_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Workspace"
        assert data["description"] == "Workspace description"
        assert data["color"] == "#FF5733"
        assert "id" in data
        assert data["memberCount"] == 1

    @pytest.mark.asyncio
    async def test_create_workspace_minimal(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should create workspace with only required fields"""
        workspace_data = {"name": "Minimal Workspace"}

        response = await async_client.post(
            "/workspaces", json=workspace_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Workspace"

    @pytest.mark.asyncio
    async def test_create_workspace_sets_active(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should set new workspace as active for user"""
        workspace_data = {"name": "Active Workspace"}

        response = await async_client.post(
            "/workspaces", json=workspace_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        workspace_id = data["id"]

        # Refresh user and check active workspace
        db.refresh(test_user)
        assert test_user.activeWorkspaceId == workspace_id

    @pytest.mark.asyncio
    async def test_create_workspace_creates_owner_membership(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should create owner membership for creator"""
        workspace_data = {"name": "Owner Workspace"}

        response = await async_client.post(
            "/workspaces", json=workspace_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        workspace_id = data["id"]

        # Check membership exists
        membership = (
            db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspaceId == workspace_id,
                WorkspaceMember.userId == test_user.id,
            )
            .first()
        )
        assert membership is not None
        assert membership.role == WorkspaceRole.OWNER

    @pytest.mark.asyncio
    async def test_create_workspace_invalid_data(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should reject invalid workspace data"""
        workspace_data = {
            # Missing required "name" field
            "description": "No name"
        }

        response = await async_client.post(
            "/workspaces", json=workspace_data, headers=auth_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_workspace_requires_auth(self, async_client: AsyncClient):
        """Should require authentication"""
        workspace_data = {"name": "Test Workspace"}

        response = await async_client.post("/workspaces", json=workspace_data)

        assert response.status_code == 401


class TestGetWorkspace:
    """Test retrieving a single workspace"""

    @pytest.mark.asyncio
    async def test_get_workspace_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should retrieve workspace by ID"""
        from app.core.security import generate_id

        workspace = Workspace(
            id=generate_id(),
            name="Test Workspace",
            description="Test Description",
            ownerId=test_user.id,
        )
        db.add(workspace)

        member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=test_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(member)
        db.commit()

        response = await async_client.get(
            f"/workspaces/{workspace.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == workspace.id
        assert data["name"] == "Test Workspace"
        assert data["memberCount"] == 1

    @pytest.mark.asyncio
    async def test_get_workspace_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should return 404 for non-existent workspace"""
        response = await async_client.get(
            "/workspaces/nonexistent-id", headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_workspace_unauthorized(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should prevent access to non-member workspace"""
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

        member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=other_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(member)
        db.commit()

        response = await async_client.get(
            f"/workspaces/{workspace.id}", headers=auth_headers
        )

        assert response.status_code == 401


class TestSwitchWorkspace:
    """Test switching active workspace"""

    @pytest.mark.asyncio
    async def test_switch_workspace_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should switch to specified workspace"""
        from app.core.security import generate_id

        # Create two workspaces
        workspace1 = Workspace(
            id=generate_id(), name="Workspace 1", ownerId=test_user.id
        )
        db.add(workspace1)

        member1 = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace1.id,
            userId=test_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(member1)

        workspace2 = Workspace(
            id=generate_id(), name="Workspace 2", ownerId=test_user.id
        )
        db.add(workspace2)

        member2 = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace2.id,
            userId=test_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(member2)
        db.commit()

        # Switch to workspace2
        switch_data = {"workspaceId": workspace2.id}

        response = await async_client.post(
            "/workspaces/switch", json=switch_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == workspace2.id

        # Verify user's active workspace updated
        db.refresh(test_user)
        assert test_user.activeWorkspaceId == workspace2.id

    @pytest.mark.asyncio
    async def test_switch_workspace_not_member(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Should prevent switching to non-member workspace"""
        switch_data = {"workspaceId": "nonexistent-workspace"}

        response = await async_client.post(
            "/workspaces/switch", json=switch_data, headers=auth_headers
        )

        assert response.status_code == 404


class TestListMembers:
    """Test listing workspace members"""

    @pytest.mark.asyncio
    async def test_list_members_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should list all workspace members"""
        from app.core.security import generate_id
        from app.core.security_v2 import get_password_hash

        workspace = Workspace(
            id=generate_id(), name="Test Workspace", ownerId=test_user.id
        )
        db.add(workspace)

        owner_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=test_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(owner_member)

        other_user = User(
            id=generate_id(),
            email="member@example.com",
            hashedPassword=get_password_hash("password123"),
            firstName="Member",
            lastName="User",
            username="memberuser",
        )
        db.add(other_user)

        other_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=other_user.id,
            role=WorkspaceRole.MEMBER,
        )
        db.add(other_member)
        db.commit()

        response = await async_client.get(
            f"/workspaces/{workspace.id}/members", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Check both members present
        member_ids = {m["userId"] for m in data}
        assert test_user.id in member_ids
        assert other_user.id in member_ids

    @pytest.mark.asyncio
    async def test_list_members_unauthorized(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should prevent listing members of non-member workspace"""
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

        workspace = Workspace(
            id=generate_id(), name="Other Workspace", ownerId=other_user.id
        )
        db.add(workspace)

        member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=other_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(member)
        db.commit()

        response = await async_client.get(
            f"/workspaces/{workspace.id}/members", headers=auth_headers
        )

        assert response.status_code == 401


class TestAddMember:
    """Test adding members to workspace"""

    @pytest.mark.asyncio
    async def test_add_member_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should add existing user to workspace"""
        from app.core.security import generate_id
        from app.core.security_v2 import get_password_hash

        # Create workspace
        workspace = Workspace(
            id=generate_id(), name="Test Workspace", ownerId=test_user.id
        )
        db.add(workspace)

        owner_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=test_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(owner_member)

        # Create user to add
        new_user = User(
            id=generate_id(),
            email="newmember@example.com",
            hashedPassword=get_password_hash("password123"),
            firstName="New",
            lastName="Member",
            username="newmember",
        )
        db.add(new_user)
        db.commit()

        # Add member
        member_data = {"email": "newmember@example.com", "role": "member"}

        response = await async_client.post(
            f"/workspaces/{workspace.id}/members",
            json=member_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["userId"] == new_user.id
        assert data["role"] == WorkspaceRole.MEMBER

    @pytest.mark.asyncio
    async def test_add_member_not_found(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should return 404 for non-existent user"""
        from app.core.security import generate_id

        workspace = Workspace(
            id=generate_id(), name="Test Workspace", ownerId=test_user.id
        )
        db.add(workspace)

        owner_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=test_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(owner_member)
        db.commit()

        member_data = {"email": "nonexistent@example.com", "role": "member"}

        response = await async_client.post(
            f"/workspaces/{workspace.id}/members",
            json=member_data,
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_add_member_already_in_workspace(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should reject adding user already in workspace"""
        from app.core.security import generate_id

        workspace = Workspace(
            id=generate_id(), name="Test Workspace", ownerId=test_user.id
        )
        db.add(workspace)

        owner_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=test_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(owner_member)
        db.commit()

        member_data = {"email": test_user.email, "role": "member"}

        response = await async_client.post(
            f"/workspaces/{workspace.id}/members",
            json=member_data,
            headers=auth_headers,
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_add_member_requires_admin(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should prevent non-admin from adding members"""
        from app.core.security import generate_id
        from app.core.security_v2 import get_password_hash

        # Create workspace owned by other user
        owner_user = User(
            id=generate_id(),
            email="owner@example.com",
            hashedPassword=get_password_hash("password123"),
            firstName="Owner",
            lastName="User",
        )
        db.add(owner_user)

        workspace = Workspace(
            id=generate_id(), name="Test Workspace", ownerId=owner_user.id
        )
        db.add(workspace)

        owner_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=owner_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(owner_member)

        # Add test_user as regular member
        test_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=test_user.id,
            role=WorkspaceRole.MEMBER,
        )
        db.add(test_member)

        # Create new user to add
        new_user = User(
            id=generate_id(),
            email="new@example.com",
            hashedPassword=get_password_hash("password123"),
            firstName="New",
            lastName="User",
        )
        db.add(new_user)
        db.commit()

        member_data = {"email": "new@example.com", "role": "member"}

        response = await async_client.post(
            f"/workspaces/{workspace.id}/members",
            json=member_data,
            headers=auth_headers,
        )

        assert response.status_code == 403


class TestRemoveMember:
    """Test removing members from workspace"""

    @pytest.mark.asyncio
    async def test_remove_member_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should remove member from workspace"""
        from app.core.security import generate_id
        from app.core.security_v2 import get_password_hash

        workspace = Workspace(
            id=generate_id(), name="Test Workspace", ownerId=test_user.id
        )
        db.add(workspace)

        owner_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=test_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(owner_member)

        # Create member to remove
        remove_user = User(
            id=generate_id(),
            email="remove@example.com",
            hashedPassword=get_password_hash("password123"),
            firstName="Remove",
            lastName="User",
        )
        db.add(remove_user)

        remove_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=remove_user.id,
            role=WorkspaceRole.MEMBER,
        )
        db.add(remove_member)
        db.commit()

        response = await async_client.delete(
            f"/workspaces/{workspace.id}/members/{remove_member.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify removal
        removed = (
            db.query(WorkspaceMember)
            .filter(WorkspaceMember.id == remove_member.id)
            .first()
        )
        assert removed is None

    @pytest.mark.asyncio
    async def test_remove_member_owner_prevented(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should prevent removing workspace owner"""
        from app.core.security import generate_id
        from app.core.security_v2 import get_password_hash

        other_user = User(
            id=generate_id(),
            email="owner@example.com",
            hashedPassword=get_password_hash("password123"),
            firstName="Other",
            lastName="Owner",
        )
        db.add(other_user)

        workspace = Workspace(
            id=generate_id(), name="Test Workspace", ownerId=other_user.id
        )
        db.add(workspace)

        owner_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=other_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(owner_member)

        # Add test_user as admin
        test_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=test_user.id,
            role=WorkspaceRole.ADMIN,
        )
        db.add(test_member)
        db.commit()

        response = await async_client.delete(
            f"/workspaces/{workspace.id}/members/{owner_member.id}",
            headers=auth_headers,
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_remove_member_admin_self_prevented(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
    ):
        """Should prevent admin from removing themselves"""
        from app.core.security import generate_id
        from app.core.security_v2 import get_password_hash

        owner_user = User(
            id=generate_id(),
            email="owner@example.com",
            hashedPassword=get_password_hash("password123"),
            firstName="Owner",
            lastName="User",
        )
        db.add(owner_user)

        workspace = Workspace(
            id=generate_id(), name="Test Workspace", ownerId=owner_user.id
        )
        db.add(workspace)

        owner_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=owner_user.id,
            role=WorkspaceRole.OWNER,
        )
        db.add(owner_member)

        # Add test_user as admin
        test_member = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=test_user.id,
            role=WorkspaceRole.ADMIN,
        )
        db.add(test_member)
        db.commit()

        response = await async_client.delete(
            f"/workspaces/{workspace.id}/members/{test_member.id}", headers=auth_headers
        )

        assert response.status_code == 400
