from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user, generate_id
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceListResponse,
    WorkspaceMemberResponse,
    WorkspaceMemberCreate,
    WorkspaceMemberUpdate,
    WorkspaceSwitchRequest
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


def _require_admin(user_id: str, workspace_id: str, db: Session) -> WorkspaceMember:
    membership = WorkspaceService.require_membership(user_id, workspace_id, db)
    if membership.role not in {WorkspaceRole.OWNER, WorkspaceRole.ADMIN}:
        raise HTTPException(status_code=403, detail="Admin permissions required")
    return membership


@router.get("/", response_model=WorkspaceListResponse)
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List workspaces the user belongs to."""
    memberships = WorkspaceService.list_user_workspaces(current_user.id, db)
    workspaces: List[WorkspaceResponse] = []

    for membership in memberships:
        workspace = membership.workspace
        member_count = db.query(WorkspaceMember).filter(WorkspaceMember.workspaceId == workspace.id).count()
        workspaces.append(
            WorkspaceResponse(
                id=workspace.id,
                name=workspace.name,
                description=workspace.description,
                color=workspace.color,
                ownerId=workspace.ownerId,
                createdAt=workspace.createdAt,
                updatedAt=workspace.updatedAt,
                settings=workspace.settings,
                memberCount=member_count
            )
        )

    active_workspace_id = current_user.activeWorkspaceId
    if not active_workspace_id and workspaces:
        workspace = WorkspaceService.ensure_default_workspace(current_user, db)
        active_workspace_id = workspace.id

    return WorkspaceListResponse(workspaces=workspaces, activeWorkspaceId=active_workspace_id)


@router.post("/", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new collaborative workspace."""
    workspace = Workspace(
        id=generate_id(),
        name=workspace_data.name,
        description=workspace_data.description,
        color=workspace_data.color,
        ownerId=current_user.id,
        settings=workspace_data.settings or {}
    )

    db.add(workspace)
    db.flush()

    membership = WorkspaceMember(
        id=generate_id(),
        workspaceId=workspace.id,
        userId=current_user.id,
        role=WorkspaceRole.OWNER
    )
    db.add(membership)

    current_user.activeWorkspaceId = workspace.id
    db.commit()
    db.refresh(workspace)

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        color=workspace.color,
        ownerId=workspace.ownerId,
        createdAt=workspace.createdAt,
        updatedAt=workspace.updatedAt,
        settings=workspace.settings,
        memberCount=1
    )


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workspace details."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    WorkspaceService.require_membership(current_user.id, workspace_id, db)
    member_count = db.query(WorkspaceMember).filter(WorkspaceMember.workspaceId == workspace_id).count()

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        color=workspace.color,
        ownerId=workspace.ownerId,
        createdAt=workspace.createdAt,
        updatedAt=workspace.updatedAt,
        settings=workspace.settings,
        memberCount=member_count
    )


@router.post("/switch", response_model=WorkspaceResponse)
async def switch_workspace(
    request: WorkspaceSwitchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Switch the user's active workspace."""
    workspace = WorkspaceService.set_active_workspace(current_user, request.workspaceId, db)
    member_count = db.query(WorkspaceMember).filter(WorkspaceMember.workspaceId == workspace.id).count()

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        color=workspace.color,
        ownerId=workspace.ownerId,
        createdAt=workspace.createdAt,
        updatedAt=workspace.updatedAt,
        settings=workspace.settings,
        memberCount=member_count
    )


@router.get("/{workspace_id}/members", response_model=List[WorkspaceMemberResponse])
async def list_members(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List members of a workspace."""
    WorkspaceService.require_membership(current_user.id, workspace_id, db)

    members = db.query(WorkspaceMember).filter(WorkspaceMember.workspaceId == workspace_id).all()
    responses: List[WorkspaceMemberResponse] = []
    for membership in members:
        user = db.query(User).filter(User.id == membership.userId).first()
        responses.append(
            WorkspaceMemberResponse(
                id=membership.id,
                workspaceId=membership.workspaceId,
                userId=membership.userId,
                role=membership.role,
                email=user.email if user else None,
                name=user.username if user else None
            )
        )
    return responses


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse, status_code=201)
async def add_member(
    workspace_id: str,
    member_data: WorkspaceMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an existing user to a workspace by email."""
    _require_admin(current_user.id, workspace_id, db)

    user = db.query(User).filter(User.email == member_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspaceId == workspace_id,
        WorkspaceMember.userId == user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already in workspace")

    membership = WorkspaceMember(
        id=generate_id(),
        workspaceId=workspace_id,
        userId=user.id,
        role=member_data.role
    )
    db.add(membership)

    if not user.activeWorkspaceId:
        user.activeWorkspaceId = workspace_id

    db.commit()
    db.refresh(membership)

    return WorkspaceMemberResponse(
        id=membership.id,
        workspaceId=membership.workspaceId,
        userId=membership.userId,
        role=membership.role,
        email=user.email,
        name=user.username
    )


@router.patch("/{workspace_id}/members/{member_id}", response_model=WorkspaceMemberResponse)
async def update_member(
    workspace_id: str,
    member_id: str,
    member_update: WorkspaceMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update member role/permissions."""
    _require_admin(current_user.id, workspace_id, db)

    membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.id == member_id,
        WorkspaceMember.workspaceId == workspace_id
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")

    if member_update.role:
        membership.role = member_update.role

    if member_update.permissions is not None:
        membership.permissions = member_update.permissions

    db.commit()
    db.refresh(membership)

    user = db.query(User).filter(User.id == membership.userId).first()

    return WorkspaceMemberResponse(
        id=membership.id,
        workspaceId=membership.workspaceId,
        userId=membership.userId,
        role=membership.role,
        email=user.email if user else None,
        name=user.username if user else None
    )


@router.delete("/{workspace_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    workspace_id: str,
    member_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a member from the workspace."""
    admin_membership = _require_admin(current_user.id, workspace_id, db)

    membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.id == member_id,
        WorkspaceMember.workspaceId == workspace_id
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")

    if membership.role == WorkspaceRole.OWNER:
        raise HTTPException(status_code=400, detail="Cannot remove workspace owner")

    # Prevent admins from removing themselves accidentally (unless owner)
    if membership.userId == admin_membership.userId and membership.role == WorkspaceRole.ADMIN:
        raise HTTPException(status_code=400, detail="Admins cannot remove themselves")

    db.delete(membership)
    db.commit()
