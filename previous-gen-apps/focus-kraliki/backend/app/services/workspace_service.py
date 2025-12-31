"""
Workspace service utilities for managing collaborative teams.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import generate_id
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole


class WorkspaceService:
    """Helper methods for workspace operations."""

    @staticmethod
    def ensure_default_workspace(user: User, db: Session) -> Workspace:
        """
        Ensure the user has an active workspace.

        Returns existing workspace if it exists, otherwise creates a private one.
        """
        if user.activeWorkspaceId:
            workspace = db.query(Workspace).filter(Workspace.id == user.activeWorkspaceId).first()
            if workspace:
                return workspace

        # Try to reuse membership workspace if any exists
        membership = db.query(WorkspaceMember).filter(WorkspaceMember.userId == user.id).first()
        if membership:
            user.activeWorkspaceId = membership.workspaceId
            db.commit()
            db.refresh(user)
            return membership.workspace

        # Create default workspace
        workspace = Workspace(
            id=generate_id(),
            name=f"{user.firstName or user.email}'s Workspace",
            description="Personal workspace",
            ownerId=user.id,
            color="#2563eb"
        )
        db.add(workspace)
        db.flush()

        membership = WorkspaceMember(
            id=generate_id(),
            workspaceId=workspace.id,
            userId=user.id,
            role=WorkspaceRole.OWNER
        )
        db.add(membership)
        user.activeWorkspaceId = workspace.id

        db.commit()
        db.refresh(user)
        return workspace

    @staticmethod
    def list_user_workspaces(user_id: str, db: Session) -> List[WorkspaceMember]:
        """Return membership rows for the user."""
        return db.query(WorkspaceMember).filter(WorkspaceMember.userId == user_id).all()

    @staticmethod
    def require_membership(user_id: str, workspace_id: str, db: Session) -> WorkspaceMember:
        """Ensure the user belongs to the workspace."""
        membership = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspaceId == workspace_id,
            WorkspaceMember.userId == user_id
        ).first()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this workspace"
            )
        return membership

    @staticmethod
    def user_can_manage(user_id: str, workspace_id: str, db: Session) -> bool:
        """Return True if user is owner/admin of workspace."""
        membership = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspaceId == workspace_id,
            WorkspaceMember.userId == user_id
        ).first()

        if not membership:
            return False
        return membership.role in {WorkspaceRole.OWNER, WorkspaceRole.ADMIN}

    @staticmethod
    def set_active_workspace(user: User, workspace_id: str, db: Session) -> Workspace:
        """Switch active workspace after validating membership."""
        membership = WorkspaceService.require_membership(user.id, workspace_id, db)
        user.activeWorkspaceId = workspace_id
        db.commit()
        db.refresh(user)
        return membership.workspace

    @staticmethod
    def get_workspace_with_access(user: User, workspace_id: Optional[str], db: Session) -> Workspace:
        """Resolve workspace ensuring membership or fall back to the user's default workspace."""
        if workspace_id:
            membership = WorkspaceService.require_membership(user.id, workspace_id, db)
            return membership.workspace

        return WorkspaceService.ensure_default_workspace(user, db)

    @staticmethod
    def get_settings(workspace_id: str, db: Session) -> Dict[str, Any]:
        """Fetch workspace settings as a dictionary."""
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if workspace and workspace.settings:
            return workspace.settings
        return {}
