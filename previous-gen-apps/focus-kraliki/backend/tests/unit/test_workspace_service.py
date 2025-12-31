import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.workspace_service import WorkspaceService
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole
from app.models.user import User

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = "u1"
    user.email = "test@example.com"
    user.firstName = "Test"
    user.activeWorkspaceId = None
    return user

class TestWorkspaceService:
    def test_ensure_default_workspace_exists(self, mock_user, mock_db):
        mock_user.activeWorkspaceId = "w1"
        mock_workspace = MagicMock(spec=Workspace)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_workspace
        
        result = WorkspaceService.ensure_default_workspace(mock_user, mock_db)
        assert result == mock_workspace

    def test_ensure_default_workspace_membership(self, mock_user, mock_db):
        mock_user.activeWorkspaceId = None
        mock_membership = MagicMock(spec=WorkspaceMember)
        mock_membership.workspaceId = "w1"
        mock_workspace = MagicMock(spec=Workspace)
        mock_membership.workspace = mock_workspace
        
        # user.activeWorkspaceId is None, so the first query is for Membership
        mock_db.query.return_value.filter.return_value.first.return_value = mock_membership
        
        result = WorkspaceService.ensure_default_workspace(mock_user, mock_db)
        assert result == mock_workspace
        assert mock_user.activeWorkspaceId == "w1"

    @patch("app.services.workspace_service.generate_id", return_value="new-w")
    def test_ensure_default_workspace_create(self, mock_gen_id, mock_user, mock_db):
        mock_user.activeWorkspaceId = None
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = WorkspaceService.ensure_default_workspace(mock_user, mock_db)
        
        assert result.id == "new-w"
        assert result.ownerId == "u1"
        assert mock_user.activeWorkspaceId == "new-w"
        mock_db.add.assert_called()
        mock_db.commit.assert_called()

    def test_list_user_workspaces(self, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = ["m1", "m2"]
        result = WorkspaceService.list_user_workspaces("u1", mock_db)
        assert result == ["m1", "m2"]

    def test_require_membership_success(self, mock_db):
        mock_membership = MagicMock(spec=WorkspaceMember)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_membership
        
        result = WorkspaceService.require_membership("u1", "w1", mock_db)
        assert result == mock_membership

    def test_require_membership_failure(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            WorkspaceService.require_membership("u1", "w1", mock_db)
        assert exc.value.status_code == 403

    def test_user_can_manage(self, mock_db):
        mock_membership = MagicMock(spec=WorkspaceMember)
        mock_membership.role = WorkspaceRole.OWNER
        mock_db.query.return_value.filter.return_value.first.return_value = mock_membership
        
        assert WorkspaceService.user_can_manage("u1", "w1", mock_db) is True
        
        mock_membership.role = WorkspaceRole.MEMBER
        assert WorkspaceService.user_can_manage("u1", "w1", mock_db) is False

    def test_set_active_workspace(self, mock_user, mock_db):
        mock_membership = MagicMock(spec=WorkspaceMember)
        mock_workspace = MagicMock(spec=Workspace)
        mock_membership.workspace = mock_workspace
        
        with patch.object(WorkspaceService, "require_membership", return_value=mock_membership):
            result = WorkspaceService.set_active_workspace(mock_user, "w1", mock_db)
            assert result == mock_workspace
            assert mock_user.activeWorkspaceId == "w1"

    def test_get_settings(self, mock_db):
        mock_workspace = MagicMock(spec=Workspace)
        mock_workspace.settings = {"theme": "dark"}
        mock_db.query.return_value.filter.return_value.first.return_value = mock_workspace
        
        assert WorkspaceService.get_settings("w1", mock_db) == {"theme": "dark"}
        
        mock_db.query.return_value.filter.return_value.first.return_value = None
        assert WorkspaceService.get_settings("w2", mock_db) == {}