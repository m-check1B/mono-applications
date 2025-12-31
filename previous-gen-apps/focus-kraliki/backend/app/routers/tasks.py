from datetime import datetime
from typing import Optional, List
import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.core.security import generate_id, get_current_user
import app.core.events as events
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.services.workspace_service import WorkspaceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _should_publish_events() -> bool:
    if os.getenv("SKIP_EVENT_PUBLISH") != "1":
        return True
    return hasattr(events.event_publisher, "published_events")


# Background indexing for semantic search (VD-340)
def _index_task_background(user_id: str, task_id: str):
    """Background task to index a task for semantic search"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            from app.services.semantic_search import get_semantic_search_service
            search_service = get_semantic_search_service(db, user)
            search_service.index_entity("task", task_id)
            logger.debug(f"Indexed task {task_id} for semantic search")
    except Exception as e:
        logger.warning(f"Failed to index task {task_id}: {e}")
    finally:
        db.close()


def _delete_task_index_background(user_id: str, task_id: str):
    """Background task to remove task from search index"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            from app.services.semantic_search import get_semantic_search_service
            search_service = get_semantic_search_service(db, user)
            search_service.delete_index("task", task_id)
            logger.debug(f"Removed task {task_id} from search index")
    except Exception as e:
        logger.warning(f"Failed to remove task {task_id} from index: {e}")
    finally:
        db.close()


# Use shared get_current_user from app.core.security which handles:
# - Platform mode (X-User-Id/X-Org-Id headers)
# - Kraliki internal bypass
# - Standard JWT authentication


def _to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        dueDate=task.dueDate,
        completedAt=task.completedAt,
        estimatedMinutes=task.estimatedMinutes,
        projectId=task.projectId,
        userId=task.userId,
        createdAt=task.createdAt,
        tags=task.tags or [],
        aiInsights=task.aiInsights,
        urgencyScore=task.urgencyScore,
        energyRequired=task.energyRequired,
        workspaceId=task.workspaceId,
        assignedUserId=task.assignedUserId,
    )


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = Task(
        id=generate_id(),
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority or 1,
        status=TaskStatus.PENDING,
        dueDate=task_data.dueDate,
        estimatedMinutes=task_data.estimatedMinutes,
        energyRequired=task_data.energyRequired,
        tags=task_data.tags or [],
        projectId=task_data.projectId,
        userId=current_user.id,
        workspaceId=task_data.workspaceId,
        assignedUserId=task_data.assignedUserId,
        createdAt=datetime.utcnow(),
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    # Publish task.created event to n8n and event bus (VD-239)
    if _should_publish_events():
        try:
            # Map priority number to string for event
            priority_map = {1: "low", 2: "medium", 3: "high", 4: "urgent"}
            # Fetch workspace settings for n8n (VD-239)
            workspace_settings = None
            if task.workspaceId:
                workspace_settings = WorkspaceService.get_settings(task.workspaceId, db)

            await events.event_publisher.publish_task_created(
                task_id=task.id,
                title=task.title,
                priority=priority_map.get(task.priority, "medium"),
                organization_id=task.workspaceId or current_user.organizationId or "default",
                user_id=current_user.id,
                assignee_id=task.assignedUserId,
                project_id=task.projectId,
                workspace_settings=workspace_settings
            )
            logger.debug(f"Published task.created event for task {task.id}")
        except Exception as e:
            # Don't fail the request if event publishing fails
            logger.warning(f"Failed to publish task.created event: {e}")

    # Index for semantic search (VD-340)
    background_tasks.add_task(_index_task_background, current_user.id, task.id)

    return _to_response(task)


# Support `/tasks` without redirect for strict clients/tests.
router.add_api_route(
    "",
    create_task,
    response_model=TaskResponse,
    methods=["POST"],
    include_in_schema=False,
)


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[TaskStatus] = None,
    projectId: Optional[str] = None,
    priority: Optional[int] = None,
    workspaceId: Optional[str] = Query(None, description="Filter tasks by workspace"),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Task).filter(Task.userId == current_user.id)

    if status:
        query = query.filter(Task.status == status)
    if projectId:
        query = query.filter(Task.projectId == projectId)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    if workspaceId:
        query = query.filter(Task.workspaceId == workspaceId)

    tasks = query.limit(limit).all()
    return TaskListResponse(tasks=[_to_response(t) for t in tasks], total=len(tasks))


# Support `/tasks` without redirect for strict clients/tests.
router.add_api_route(
    "",
    list_tasks,
    response_model=TaskListResponse,
    methods=["GET"],
    include_in_schema=False,
)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.userId == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return _to_response(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.userId == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Track if task was completed in this update
    was_completed = False
    old_status = task.status

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "status":
            setattr(task, "status", value)
            if value == TaskStatus.COMPLETED and old_status != TaskStatus.COMPLETED:
                task.completedAt = datetime.utcnow()
                was_completed = True
        elif hasattr(task, key):
            setattr(task, key, value)

    db.commit()
    db.refresh(task)

    # Publish task.updated event (VD-239/Gap #7)
    if _should_publish_events():
        try:
            # Fetch workspace settings for n8n
            workspace_settings = None
            if task.workspaceId:
                workspace_settings = WorkspaceService.get_settings(task.workspaceId, db)

            await events.event_publisher.publish_task_updated(
                task_id=task.id,
                title=task.title,
                organization_id=task.workspaceId or current_user.organizationId or "default",
                user_id=current_user.id,
                updates=update_data,
                workspace_settings=workspace_settings
            )
            logger.debug(f"Published task.updated event for task {task.id}")
        except Exception as e:
            logger.warning(f"Failed to publish task.updated event: {e}")

    # Publish task.completed event to n8n and event bus (VD-239)
    if was_completed and _should_publish_events():
        try:
            # Calculate duration if task has created date
            duration_minutes = None
            if task.createdAt and task.completedAt:
                duration = task.completedAt - task.createdAt
                duration_minutes = int(duration.total_seconds() / 60)

            # Fetch workspace settings for n8n (VD-239)
            workspace_settings = None
            if task.workspaceId:
                workspace_settings = WorkspaceService.get_settings(task.workspaceId, db)

            await events.event_publisher.publish_task_completed(
                task_id=task.id,
                title=task.title,
                organization_id=task.workspaceId or current_user.organizationId or "default",
                user_id=current_user.id,
                duration_minutes=duration_minutes,
                workspace_settings=workspace_settings
            )
            logger.debug(f"Published task.completed event for task {task.id}")
        except Exception as e:
            # Don't fail the request if event publishing fails
            logger.warning(f"Failed to publish task.completed event: {e}")

    # Re-index for semantic search (VD-340)
    background_tasks.add_task(_index_task_background, current_user.id, task.id)

    return _to_response(task)


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.userId == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_id_copy = task.id  # Copy before deletion
    db.delete(task)
    db.commit()

    # Remove from search index (VD-340)
    background_tasks.add_task(_delete_task_index_background, current_user.id, task_id_copy)

    return {"success": True}
