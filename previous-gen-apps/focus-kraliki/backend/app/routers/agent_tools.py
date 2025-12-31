"""
Agent Tools Router - HTTP API for II-Agent
Provides a minimal, agent-friendly interface for II-Agent to interact with Focus by Kraliki.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
import os

from app.core.database import get_db
from app.core.security import get_current_user, generate_id, create_agent_token
from app.models.user import User
from app.schemas.user import UserPreferences
from app.models.knowledge_item import KnowledgeItem
from app.models.item_type import ItemType
from app.models.task import Task, TaskStatus, Project
from app.models.event import Event
from app.models.time_entry import TimeEntry
from app.models.workflow_template import WorkflowTemplate
from app.models.workspace import Workspace, WorkspaceMember
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventListResponse
from app.schemas.time_entry import TimeEntryCreate, TimeEntryStopRequest, TimeEntryResponse, TimeEntryListResponse
from app.schemas.workflow import WorkflowTemplateResponse, WorkflowListResponse, WorkflowExecuteRequest, WorkflowExecuteResponse
from app.services.workspace_service import WorkspaceService
from app.routers.analytics import _calculate_task_metrics, _load_time_metrics, _detect_bottlenecks, _load_workspace_tasks
from app.schemas.workspace import WorkspaceResponse

router = APIRouter(prefix="/agent-tools", tags=["agent-tools"])

# ========== Request/Response Schemas ==========

class KnowledgeCreateRequest(BaseModel):
    """Request schema for creating a knowledge item"""
    typeId: str = Field(..., description="ID of the item type")
    title: str = Field(..., min_length=1, description="Title of the knowledge item")
    content: Optional[str] = Field(None, description="Content of the knowledge item")
    item_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class KnowledgeUpdateRequest(BaseModel):
    """Request schema for updating a knowledge item"""
    title: Optional[str] = Field(None, description="Updated title")
    content: Optional[str] = Field(None, description="Updated content")
    completed: Optional[bool] = Field(None, description="Completion status")
    item_metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")

class KnowledgeResponse(BaseModel):
    """Response schema for knowledge items"""
    id: str
    userId: str
    typeId: str
    title: str
    content: Optional[str]
    item_metadata: Optional[Dict[str, Any]]
    completed: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class KnowledgeListResponse(BaseModel):
    """Response schema for listing knowledge items"""
    items: List[KnowledgeResponse]
    total: int

class TaskCreateRequest(BaseModel):
    """Request schema for creating a task"""
    title: str = Field(..., min_length=1, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: Optional[int] = Field(1, description="Priority level")
    estimatedMinutes: Optional[int] = Field(None, description="Estimated time in minutes")
    projectId: Optional[str] = Field(None, description="Associated project ID")
    dueDate: Optional[datetime] = Field(None, description="Due date")

class TaskUpdateRequest(BaseModel):
    """Request schema for updating a task"""
    title: Optional[str] = Field(None, description="Updated title")
    description: Optional[str] = Field(None, description="Updated description")
    status: Optional[TaskStatus] = Field(None, description="Updated status")
    estimatedMinutes: Optional[int] = Field(None, description="Updated estimated time")
    priority: Optional[int] = Field(None, description="Updated priority")

class TaskResponse(BaseModel):
    """Response schema for tasks"""
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: int
    dueDate: Optional[datetime]
    completedAt: Optional[datetime]
    estimatedMinutes: Optional[int]
    projectId: Optional[str]
    userId: Optional[str]
    createdAt: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    """Response schema for listing tasks"""
    tasks: List[TaskResponse]
    total: int

class ProjectCreateOrGetRequest(BaseModel):
    """Request schema for creating or getting a project"""
    name: str = Field(..., min_length=1, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    color: Optional[str] = Field(None, description="Project color")
    icon: Optional[str] = Field(None, description="Project icon")

class ProjectResponse(BaseModel):
    """Response schema for projects"""
    id: str
    name: str
    description: Optional[str]
    color: Optional[str]
    icon: Optional[str]
    userId: str

    class Config:
        from_attributes = True

class EventCreateRequest(EventCreate):
    """Create calendar event"""
    pass

class EventUpdateRequest(EventUpdate):
    """Update calendar event"""
    pass

class WorkspaceSwitchRequest(BaseModel):
    workspaceId: str

# ========== Helpers ==========

def _workspace_for_user(user: User, db: Session, workspace_id: Optional[str] = None) -> Workspace:
    """Ensure user has access to workspace (defaults to active/default)."""
    workspace = WorkspaceService.get_workspace_with_access(user, workspace_id, db)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace

# ========== Knowledge Tools ==========

@router.post("/knowledge/create", response_model=KnowledgeResponse)
async def create_knowledge_item(
    item_data: KnowledgeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new knowledge item.

    This endpoint allows II-Agent to create knowledge items on behalf of the user.
    The typeId must belong to the authenticated user.
    """
    # Verify the typeId belongs to the user
    item_type = db.query(ItemType).filter(
        ItemType.id == item_data.typeId,
        ItemType.userId == current_user.id
    ).first()

    if not item_type:
        raise HTTPException(
            status_code=404,
            detail=f"Item type with id '{item_data.typeId}' not found"
        )

    # Create the knowledge item
    knowledge_item = KnowledgeItem(
        id=generate_id(),
        userId=current_user.id,
        typeId=item_data.typeId,
        title=item_data.title,
        content=item_data.content or "",
        item_metadata=item_data.item_metadata,
        completed=False
    )

    db.add(knowledge_item)
    db.commit()
    db.refresh(knowledge_item)

    return KnowledgeResponse.model_validate(knowledge_item)

@router.patch("/knowledge/{item_id}", response_model=KnowledgeResponse)
async def update_knowledge_item(
    item_id: str,
    item_update: KnowledgeUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a knowledge item.

    This endpoint allows II-Agent to update existing knowledge items.
    Only items belonging to the authenticated user can be updated.
    """
    # Find the knowledge item
    knowledge_item = db.query(KnowledgeItem).filter(
        KnowledgeItem.id == item_id,
        KnowledgeItem.userId == current_user.id
    ).first()

    if not knowledge_item:
        raise HTTPException(
            status_code=404,
            detail=f"Knowledge item with id '{item_id}' not found"
        )

    # Update the item with provided fields
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "content" and value is None:
            value = ""
        setattr(knowledge_item, key, value)

    db.commit()
    db.refresh(knowledge_item)

    return KnowledgeResponse.model_validate(knowledge_item)

@router.get("/knowledge", response_model=KnowledgeListResponse)
async def list_knowledge_items(
    typeId: Optional[str] = Query(None, description="Filter by item type ID"),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of items to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List knowledge items for the current user.

    This endpoint allows II-Agent to retrieve knowledge items, optionally filtered by type.
    Results are ordered by creation date (newest first).
    """
    query = db.query(KnowledgeItem).filter(KnowledgeItem.userId == current_user.id)

    if typeId:
        query = query.filter(KnowledgeItem.typeId == typeId)
    else:
        tasks_type = db.query(ItemType).filter(
            ItemType.userId == current_user.id,
            ItemType.name == "Tasks",
        ).first()
        if tasks_type:
            query = query.filter(KnowledgeItem.typeId != tasks_type.id)

    items = query.order_by(KnowledgeItem.createdAt.desc()).limit(limit).all()
    total = query.count()

    return KnowledgeListResponse(
        items=[KnowledgeResponse.model_validate(item) for item in items],
        total=total
    )

# ========== Task Tools ==========

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task (unified with knowledge items).

    This endpoint creates tasks as knowledge items with typeId="Tasks".
    Task-specific fields are stored in item_metadata for backward compatibility.
    """
    # Get or create "Tasks" item type for this user
    task_type = db.query(ItemType).filter(
        ItemType.userId == current_user.id,
        ItemType.name == "Tasks"
    ).first()

    if not task_type:
        # Create Tasks type if it doesn't exist
        task_type = ItemType(
            id=generate_id(),
            userId=current_user.id,
            name="Tasks",
            description="Task items",
            icon="CheckSquare",
            color="blue",
            isDefault=True
        )
        db.add(task_type)
        db.flush()

    # Verify projectId if provided
    if task_data.projectId:
        project = db.query(Project).filter(
            Project.id == task_data.projectId,
            Project.userId == current_user.id
        ).first()

        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"Project with id '{task_data.projectId}' not found"
            )

    # Build metadata with task-specific fields
    metadata = {
        "status": "PENDING",
        "priority": task_data.priority or 1,
        "estimatedMinutes": task_data.estimatedMinutes,
        "projectId": task_data.projectId
    }

    if task_data.dueDate:
        metadata["dueDate"] = task_data.dueDate.isoformat()

    # Create as knowledge item
    knowledge_item = KnowledgeItem(
        id=generate_id(),
        userId=current_user.id,
        typeId=task_type.id,
        title=task_data.title,
        content=task_data.description or "",
        item_metadata=metadata,
        completed=False
    )

    db.add(knowledge_item)
    db.commit()
    db.refresh(knowledge_item)

    # Transform to TaskResponse for backward compatibility
    return TaskResponse(
        id=knowledge_item.id,
        title=knowledge_item.title,
        description=knowledge_item.content,
        status=TaskStatus.PENDING,
        priority=metadata.get("priority", 1),
        dueDate=task_data.dueDate,
        completedAt=None,
        estimatedMinutes=metadata.get("estimatedMinutes"),
        projectId=metadata.get("projectId"),
        userId=knowledge_item.userId,
        createdAt=knowledge_item.createdAt
    )

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a task (unified with knowledge items).

    This endpoint updates tasks stored as knowledge items.
    Task-specific fields are stored in item_metadata.
    """
    # Find the knowledge item
    knowledge_item = db.query(KnowledgeItem).filter(
        KnowledgeItem.id == task_id,
        KnowledgeItem.userId == current_user.id
    ).first()

    if not knowledge_item:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id '{task_id}' not found"
        )

    # Get current metadata
    metadata = knowledge_item.item_metadata or {}
    current_status = metadata.get("status", "PENDING")

    # Update the task with provided fields
    update_data = task_update.model_dump(exclude_unset=True)

    # Update title/description if provided
    if "title" in update_data:
        knowledge_item.title = update_data["title"]
    if "description" in update_data:
        knowledge_item.content = update_data["description"]

    # Update metadata fields
    if "status" in update_data:
        new_status = update_data["status"].value if isinstance(update_data["status"], TaskStatus) else update_data["status"]
        metadata["status"] = new_status

        # Auto-set completedAt when status changes to COMPLETED
        if new_status == "COMPLETED" and current_status != "COMPLETED":
            metadata["completedAt"] = datetime.utcnow().isoformat()
            knowledge_item.completed = True
        elif new_status != "COMPLETED":
            knowledge_item.completed = False

    if "estimatedMinutes" in update_data:
        metadata["estimatedMinutes"] = update_data["estimatedMinutes"]
    if "priority" in update_data:
        metadata["priority"] = update_data["priority"]

    knowledge_item.item_metadata = dict(metadata)
    try:
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(knowledge_item, "item_metadata")
    except Exception:
        pass

    db.commit()
    db.refresh(knowledge_item)

    # Transform to TaskResponse
    return TaskResponse(
        id=knowledge_item.id,
        title=knowledge_item.title,
        description=knowledge_item.content,
        status=TaskStatus(metadata.get("status", "PENDING")),
        priority=metadata.get("priority", 1),
        dueDate=datetime.fromisoformat(metadata["dueDate"]) if metadata.get("dueDate") else None,
        completedAt=datetime.fromisoformat(metadata["completedAt"]) if metadata.get("completedAt") else None,
        estimatedMinutes=metadata.get("estimatedMinutes"),
        projectId=metadata.get("projectId"),
        userId=knowledge_item.userId,
        createdAt=knowledge_item.createdAt
    )

@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    projectId: Optional[str] = Query(None, description="Filter by project ID"),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of tasks to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List tasks for the current user (unified with knowledge items).

    This endpoint reads from knowledge_item table with typeId="Tasks".
    """
    # Get Tasks item type for this user
    task_type = db.query(ItemType).filter(
        ItemType.userId == current_user.id,
        ItemType.name == "Tasks"
    ).first()

    if not task_type:
        # No tasks type yet, return empty list
        return TaskListResponse(tasks=[], total=0)

    # Query knowledge items with Tasks typeId
    query = db.query(KnowledgeItem).filter(
        KnowledgeItem.userId == current_user.id,
        KnowledgeItem.typeId == task_type.id
    )

    # Apply filters based on metadata
    items = query.limit(limit).all()

    # Filter by status and projectId from metadata
    filtered_tasks = []
    for item in items:
        metadata = item.item_metadata or {}
        status_value = metadata.get("status") or ("COMPLETED" if item.completed else "PENDING")

        # Apply status filter
        if status and status_value != status.value:
            continue

        # Apply projectId filter
        if projectId and metadata.get("projectId") != projectId:
            continue

        # Transform to TaskResponse
        task_response = TaskResponse(
            id=item.id,
            title=item.title,
            description=item.content,
            status=TaskStatus(status_value),
            priority=metadata.get("priority", 1),
            dueDate=datetime.fromisoformat(metadata["dueDate"]) if metadata.get("dueDate") else None,
            completedAt=datetime.fromisoformat(metadata["completedAt"]) if metadata.get("completedAt") else None,
            estimatedMinutes=metadata.get("estimatedMinutes"),
            projectId=metadata.get("projectId"),
            userId=item.userId,
            createdAt=item.createdAt
        )
        filtered_tasks.append(task_response)

    return TaskListResponse(
        tasks=filtered_tasks,
        total=len(filtered_tasks)
    )

# ========== Project Tools ==========

@router.post("/projects/create-or-get", response_model=ProjectResponse)
async def create_or_get_project(
    project_data: ProjectCreateOrGetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project or get an existing one by name.

    This endpoint allows II-Agent to ensure a project exists with the given name.
    If a project with the same name already exists for the user, it returns that project.
    Otherwise, it creates a new one.
    """
    # Check if a project with this name already exists for the user
    existing_project = db.query(Project).filter(
        Project.userId == current_user.id,
        Project.name == project_data.name
    ).first()

    if existing_project:
        return ProjectResponse.model_validate(existing_project)

    # Create new project
    project = Project(
        id=generate_id(),
        userId=current_user.id,
        name=project_data.name,
        description=project_data.description,
        color=project_data.color,
        icon=project_data.icon
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return ProjectResponse.model_validate(project)

# ========== Settings Tools ==========

@router.post("/settings/update")
async def update_user_settings(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences (theme, notifications, etc.)"""
    current_prefs = current_user.preferences or {}
    new_prefs = preferences.model_dump(exclude_unset=True)
    current_prefs.update(new_prefs)

    current_user.preferences = current_prefs
    db.commit()

    return {"success": True, "preferences": current_prefs}

# ========== Infra Tools ==========

@router.get("/infra/status")
async def check_infra_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check infrastructure status (DB, system)"""
    status = {"system": "healthy", "services": {}}
    try:
        db.execute(text("SELECT 1"))
        status["services"]["database"] = "healthy"
    except Exception as e:
        status["services"]["database"] = f"unhealthy: {str(e)}"
        status["system"] = "degraded"

    return status

@router.get("/infra/logs")
async def get_infra_logs(
    service: str = Query(..., description="Service name: backend or frontend"),
    lines: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get logs for a service"""
    if service not in ["backend", "frontend"]:
        raise HTTPException(status_code=400, detail="Invalid service")

    log_path = f"../{service}.log"
    if not os.path.exists(log_path):
        log_path = f"{service}.log"
        if not os.path.exists(log_path):
            return {"service": service, "content": "Log file not found"}

    try:
        with open(log_path, "r") as f:
            all_lines = f.readlines()
            return {"service": service, "content": "".join(all_lines[-lines:])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/infra/restart")
async def restart_infra_service(
    service: str = Query(..., description="Service name: backend or frontend"),
    current_user: User = Depends(get_current_user),
):
    """Restart a service using the infra router."""
    if service not in ["backend", "frontend"]:
        raise HTTPException(status_code=400, detail="Invalid service")

    try:
        # Use internal infra router to perform restart; keeps logic centralized
        from app.routers.infra import restart_service as infra_restart  # lazy import to avoid cycles

        return await infra_restart(service=service, current_user=current_user)  # type: ignore
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart service: {str(e)}")

# ========== Calendar (Events) Tools ==========

@router.get("/events", response_model=EventListResponse)
async def list_events_for_agent(
    startDate: Optional[str] = Query(None, description="ISO start date"),
    endDate: Optional[str] = Query(None, description="ISO end date"),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List calendar events for the user."""
    query = db.query(Event).filter(Event.user_id == current_user.id)
    if startDate:
        try:
            query = query.filter(Event.start_time >= datetime.fromisoformat(startDate))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start date")
    if endDate:
        try:
            query = query.filter(Event.end_time <= datetime.fromisoformat(endDate))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end date")

    events = query.order_by(Event.start_time.asc()).limit(limit).all()
    total = query.count()
    return EventListResponse(
        events=[EventResponse.model_validate(e) for e in events],
        total=total
    )

@router.post("/events", response_model=EventResponse)
async def create_event_for_agent(
    event_data: EventCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a calendar event on behalf of the user."""
    event = Event(
        id=generate_id(),
        user_id=current_user.id,
        **event_data.model_dump(exclude_unset=True)
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return EventResponse.model_validate(event)

@router.patch("/events/{event_id}", response_model=EventResponse)
async def update_event_for_agent(
    event_id: str,
    event_update: EventUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a calendar event."""
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in event_update.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return EventResponse.model_validate(event)

@router.delete("/events/{event_id}")
async def delete_event_for_agent(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a calendar event."""
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"success": True, "deletedId": event_id}

# ========== Time Tracking Tools ==========

@router.get("/time", response_model=TimeEntryListResponse)
async def list_time_entries_for_agent(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List recent time entries for the user."""
    entries = db.query(TimeEntry).filter(TimeEntry.user_id == current_user.id).order_by(TimeEntry.start_time.desc()).limit(limit).all()
    total = db.query(TimeEntry).filter(TimeEntry.user_id == current_user.id).count()
    return TimeEntryListResponse(
        entries=[TimeEntryResponse.model_validate(e) for e in entries],
        total=total
    )

@router.post("/time/start", response_model=TimeEntryResponse)
async def start_timer_for_agent(
    entry_data: TimeEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a timer (creates a time entry)."""
    workspace_id = entry_data.workspace_id
    if workspace_id:
        WorkspaceService.require_membership(current_user.id, workspace_id, db)
    else:
        workspace = WorkspaceService.ensure_default_workspace(current_user, db)
        workspace_id = workspace.id

    entry = TimeEntry(
        id=generate_id(),
        user_id=current_user.id,
        workspace_id=workspace_id,
        **entry_data.model_dump(exclude_unset=True, exclude={"workspace_id"})
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return TimeEntryResponse.model_validate(entry)

@router.post("/time/{entry_id}/stop", response_model=TimeEntryResponse)
async def stop_timer_for_agent(
    entry_id: str,
    stop_data: TimeEntryStopRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop a running timer."""
    entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id, TimeEntry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    if entry.end_time:
        raise HTTPException(status_code=400, detail="Timer already stopped")
    end_time = stop_data.end_time if stop_data and stop_data.end_time else datetime.utcnow()
    entry.end_time = end_time
    entry.duration_seconds = int((entry.end_time - entry.start_time).total_seconds())
    if stop_data and stop_data.description:
        entry.description = stop_data.description
    entry.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(entry)
    return TimeEntryResponse.model_validate(entry)

# ========== Workflow Tools ==========

@router.get("/workflow/templates", response_model=WorkflowListResponse)
async def list_workflow_templates_for_agent(
    include_system: bool = True,
    include_public: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List workflow templates available to the user."""
    from sqlalchemy import or_
    query = db.query(WorkflowTemplate).filter(
        or_(
            WorkflowTemplate.userId == current_user.id,
            WorkflowTemplate.isSystem == True,
            WorkflowTemplate.isPublic == True if include_public else False
        )
    )
    templates = query.order_by(WorkflowTemplate.usageCount.desc()).all()
    return WorkflowListResponse(
        templates=[WorkflowTemplateResponse.model_validate(t) for t in templates],
        total=len(templates)
    )

@router.post("/workflow/execute", response_model=WorkflowExecuteResponse)
async def execute_workflow_for_agent(
    request: WorkflowExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a workflow template and create tasks."""
    # Reuse logic from workflow router
    from app.routers.workflow import execute_workflow  # type: ignore
    return await execute_workflow(request, current_user=current_user, db=db)

# ========== Analytics Tools ==========

@router.get("/analytics/overview")
async def analytics_overview_for_agent(
    workspaceId: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics overview for current workspace."""
    workspace = _workspace_for_user(current_user, db, workspaceId)
    tasks = _load_workspace_tasks(workspace.id, db)
    task_metrics = _calculate_task_metrics(tasks)
    focus_metrics = _load_time_metrics(workspace.id, db)
    bottlenecks = _detect_bottlenecks(tasks)

    return {
        "workspace": WorkspaceResponse.model_validate(workspace),
        "taskMetrics": task_metrics,
        "focusMetrics": focus_metrics,
        "bottlenecks": bottlenecks
    }

# ========== Workspace Tools ==========

@router.get("/workspaces")
async def list_workspaces_for_agent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List workspaces the user can access."""
    memberships = db.query(WorkspaceMember).filter(WorkspaceMember.userId == current_user.id).all()
    workspace_ids = [m.workspaceId for m in memberships]
    workspaces = db.query(Workspace).filter(Workspace.id.in_(workspace_ids)).all()
    return {
        "activeWorkspaceId": current_user.activeWorkspaceId,
        "workspaces": [WorkspaceResponse.model_validate(w) for w in workspaces]
    }

@router.post("/workspaces/switch")
async def switch_workspace_for_agent(
    payload: WorkspaceSwitchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Switch active workspace for the user."""
    workspace = _workspace_for_user(current_user, db, payload.workspaceId)
    current_user.activeWorkspaceId = workspace.id
    db.commit()
    return {"success": True, "activeWorkspaceId": workspace.id}
