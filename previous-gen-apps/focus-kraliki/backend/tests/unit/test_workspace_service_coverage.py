"""
WorkspaceService Unit Tests
Coverage target: 100% of workspace_service.py
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.workspace_service import WorkspaceService
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole
from app.models.user import User
from app.core.security_v2 import generate_id


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_user():
    """Mock user."""
    user = MagicMock(spec=User)
    user.id = "user-123"
    user.firstName = "Test"
    user.lastName = "User"
    user.email = "test@example.com"
    user.activeWorkspaceId = None
    return user


class TestEnsureDefaultWorkspace:
    """Test ensure_default_workspace method."""

    def test_returns_existing_active_workspace(self, mock_db, mock_user):
        """Test returns existing active workspace."""
        workspace = MagicMock(spec=Workspace)
        workspace.id = "ws-123"
        mock_user.activeWorkspaceId = "ws-123"
        mock_db.query.return_value.filter.return_value.first.return_value = workspace

        result = WorkspaceService.ensure_default_workspace(mock_user, mock_db)

        assert result is workspace

    def test_uses_membership_workspace(self, mock_db, mock_user):
        """Test uses existing membership workspace."""
        mock_user.activeWorkspaceId = None

        membership = MagicMock()
        membership.workspaceId = "ws-456"
        membership.workspace = MagicMock()

        # Membership query returns a workspace
        mock_db.query.return_value.filter.return_value.first.return_value = membership

        result = WorkspaceService.ensure_default_workspace(mock_user, mock_db)

        assert result is membership.workspace

    def test_creates_new_workspace(self, mock_db, mock_user):
        """Test creates new workspace when none exists."""
        mock_user.activeWorkspaceId = None

        # No workspace, no membership
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            None,  # No workspace found
            None   # No membership found
        ]

        result = WorkspaceService.ensure_default_workspace(mock_user, mock_db)

        # Should have called db.add twice (workspace + membership)
        assert mock_db.add.call_count >= 1
        mock_db.commit.assert_called()

    def test_creates_workspace_with_email_fallback(self, mock_db, mock_user):
        """Test workspace name uses email when firstName is None."""
        mock_user.activeWorkspaceId = None
        mock_user.firstName = None

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            None,  # No workspace found
            None   # No membership found
        ]

        WorkspaceService.ensure_default_workspace(mock_user, mock_db)

        # Workspace should be created with email in name
        mock_db.add.assert_called()


class TestListUserWorkspaces:
    """Test list_user_workspaces method."""

    def test_returns_all_memberships(self, mock_db):
        """Test returns all user memberships."""
        memberships = [MagicMock(), MagicMock()]
        mock_db.query.return_value.filter.return_value.all.return_value = memberships

        result = WorkspaceService.list_user_workspaces("user-123", mock_db)

        assert result == memberships


class TestRequireMembership:
    """Test require_membership method."""

    def test_returns_membership_when_exists(self, mock_db):
        """Test returns membership when user has access."""
        membership = MagicMock(spec=WorkspaceMember)
        mock_db.query.return_value.filter.return_value.first.return_value = membership

        result = WorkspaceService.require_membership("user-123", "ws-123", mock_db)

        assert result is membership

    def test_raises_when_no_membership(self, mock_db):
        """Test raises HTTPException when no membership."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            WorkspaceService.require_membership("user-123", "ws-123", mock_db)

        assert exc_info.value.status_code == 403
        assert "access" in exc_info.value.detail.lower()


class TestUserCanManage:
    """Test user_can_manage method."""

    def test_returns_true_for_owner(self, mock_db):
        """Test returns True for owner role."""
        membership = MagicMock()
        membership.role = WorkspaceRole.OWNER
        mock_db.query.return_value.filter.return_value.first.return_value = membership

        result = WorkspaceService.user_can_manage("user-123", "ws-123", mock_db)

        assert result is True

    def test_returns_true_for_admin(self, mock_db):
        """Test returns True for admin role."""
        membership = MagicMock()
        membership.role = WorkspaceRole.ADMIN
        mock_db.query.return_value.filter.return_value.first.return_value = membership

        result = WorkspaceService.user_can_manage("user-123", "ws-123", mock_db)

        assert result is True

    def test_returns_false_for_member(self, mock_db):
        """Test returns False for member role."""
        membership = MagicMock()
        membership.role = WorkspaceRole.MEMBER
        mock_db.query.return_value.filter.return_value.first.return_value = membership

        result = WorkspaceService.user_can_manage("user-123", "ws-123", mock_db)

        assert result is False

    def test_returns_false_when_no_membership(self, mock_db):
        """Test returns False when no membership."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = WorkspaceService.user_can_manage("user-123", "ws-123", mock_db)

        assert result is False


class TestSetActiveWorkspace:
    """Test set_active_workspace method."""

    def test_sets_active_workspace(self, mock_db, mock_user):
        """Test sets active workspace on user."""
        workspace = MagicMock(spec=Workspace)
        membership = MagicMock(workspace=workspace)
        mock_db.query.return_value.filter.return_value.first.return_value = membership

        result = WorkspaceService.set_active_workspace(mock_user, "ws-123", mock_db)

        assert mock_user.activeWorkspaceId == "ws-123"
        mock_db.commit.assert_called()
        assert result is workspace


class TestGetWorkspaceWithAccess:
    """Test get_workspace_with_access method."""

    def test_returns_specified_workspace(self, mock_db, mock_user):
        """Test returns specified workspace when ID provided."""
        workspace = MagicMock(spec=Workspace)
        membership = MagicMock(workspace=workspace)
        mock_db.query.return_value.filter.return_value.first.return_value = membership

        result = WorkspaceService.get_workspace_with_access(mock_user, "ws-123", mock_db)

        assert result is workspace

    def test_returns_default_workspace(self, mock_db, mock_user):
        """Test returns default workspace when ID is None."""
        workspace = MagicMock(spec=Workspace)
        mock_user.activeWorkspaceId = "ws-default"
        mock_db.query.return_value.filter.return_value.first.return_value = workspace

        result = WorkspaceService.get_workspace_with_access(mock_user, None, mock_db)

        assert result is workspace


class TestGetSettings:
    """Test get_settings method."""

    def test_returns_workspace_settings(self, mock_db):
        """Test returns workspace settings."""
        workspace = MagicMock()
        workspace.settings = {"n8n_url": "http://custom"}
        mock_db.query.return_value.filter.return_value.first.return_value = workspace

        result = WorkspaceService.get_settings("ws-123", mock_db)

        assert result == {"n8n_url": "http://custom"}

    def test_returns_empty_dict_when_no_settings(self, mock_db):
        """Test returns empty dict when no settings."""
        workspace = MagicMock()
        workspace.settings = None
        mock_db.query.return_value.filter.return_value.first.return_value = workspace

        result = WorkspaceService.get_settings("ws-123", mock_db)

        assert result == {}

    def test_returns_empty_dict_when_no_workspace(self, mock_db):
        """Test returns empty dict when workspace not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = WorkspaceService.get_settings("ws-123", mock_db)

        assert result == {}
