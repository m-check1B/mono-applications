from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.security import get_current_user, generate_id
from app.models.user import User
from app.models.task import Project, Task
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/projects", tags=["projects"])


def _ensure_project_access(project: Project, current_user: User, db: Session):
    if project.userId == current_user.id:
        return
    if project.workspaceId:
        WorkspaceService.require_membership(current_user.id, project.workspaceId, db)
        return
    raise HTTPException(status_code=404, detail="Project not found")


def _project_to_response(project: Project, db: Session) -> ProjectResponse:
    task_count = db.query(Task).filter(Task.projectId == project.id).count()
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        color=project.color,
        icon=project.icon,
        userId=project.userId,
        workspaceId=project.workspaceId,
        taskCount=task_count,
    )


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    limit: int = Query(default=50, ge=1, le=100),
    workspaceId: Optional[str] = Query(None, description="Filter projects by workspace"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Project)

    if workspaceId:
        WorkspaceService.require_membership(current_user.id, workspaceId, db)
        query = query.filter(Project.workspaceId == workspaceId)
    else:
        memberships = WorkspaceService.list_user_workspaces(current_user.id, db)
        workspace_ids: List[str] = [m.workspaceId for m in memberships]
        filters = [Project.userId == current_user.id]
        if workspace_ids:
            filters.append(Project.workspaceId.in_(workspace_ids))
        query = query.filter(or_(*filters))

    projects = query.limit(limit).all()
    responses = [_project_to_response(p, db) for p in projects]
    return ProjectListResponse(projects=responses, total=len(responses))


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workspace = WorkspaceService.ensure_default_workspace(current_user, db)
    workspace_id = project_data.workspaceId or workspace.id

    project = Project(
        id=generate_id(),
        userId=current_user.id,
        workspaceId=workspace_id,
        name=project_data.name,
        description=project_data.description,
        color=project_data.color,
        icon=project_data.icon,
        createdAt=datetime.utcnow(),
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return _project_to_response(project, db)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    _ensure_project_access(project, current_user, db)
    return _project_to_response(project, db)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    _ensure_project_access(project, current_user, db)

    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return _project_to_response(project, db)


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    _ensure_project_access(project, current_user, db)

    db.delete(project)
    db.commit()
    return {"success": True, "deletedId": project_id}
