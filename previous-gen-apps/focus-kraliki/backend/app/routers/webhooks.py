"""
Webhooks Router - n8n Integration for Focus by Kraliki
=================================================
Provides webhook endpoints for external automation (n8n, Zapier, etc.)

Endpoints:
    POST /webhooks/task/create     - Create a task from external trigger
    POST /webhooks/task/complete   - Mark task complete from external trigger
    POST /webhooks/workflow/execute - Execute a workflow template
    POST /webhooks/event/create    - Create calendar event
    GET  /webhooks/status          - Webhook system status

Security:
    - API key authentication via X-Webhook-Secret header
    - Webhook secrets stored in user preferences
    - Rate limiting: 30 requests/minute per client IP (via slowapi)

Integration with Darwin2:
    - Sends events to Darwin2 n8n API when tasks complete
    - Can be triggered by Darwin2 agents
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel
import logging
import httpx
import os

from app.core.database import get_db
from app.core.security import generate_id
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.event import Event
from app.models.workflow_template import WorkflowTemplate
from app.middleware.rate_limit import limiter, webhook_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Darwin2 n8n API configuration
DARWIN2_N8N_API = os.environ.get("DARWIN2_N8N_API", "http://127.0.0.1:8198")


# ============ Pydantic Models ============

class WebhookTaskCreate(BaseModel):
    """Task creation from webhook"""
    title: str
    description: Optional[str] = None
    priority: int = 2
    estimatedMinutes: Optional[int] = None
    dueDate: Optional[str] = None
    tags: List[str] = []


class WebhookTaskComplete(BaseModel):
    """Task completion from webhook"""
    taskId: str
    notes: Optional[str] = None


class WebhookWorkflowExecute(BaseModel):
    """Workflow execution from webhook"""
    templateId: str
    customTitle: Optional[str] = None
    startDate: Optional[str] = None
    priority: int = 2


class WebhookEventCreate(BaseModel):
    """Event creation from webhook"""
    title: str
    description: Optional[str] = None
    start_time: str
    end_time: Optional[str] = None
    location: Optional[str] = None


class WebhookResponse(BaseModel):
    """Standard webhook response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class WebhookConfig(BaseModel):
    """Webhook configuration"""
    enabled: bool = True
    events: List[str] = []  # Events to trigger outbound webhooks
    target_url: Optional[str] = None  # Where to send outbound webhooks


# ============ Auth Helper ============

async def get_user_by_webhook_secret(
    x_webhook_secret: str = Header(...),
    db: Session = Depends(get_db)
) -> User:
    """
    Authenticate webhook request via secret header.

    Webhook secret is stored in user.preferences.webhook_secret
    """
    if not x_webhook_secret:
        raise HTTPException(status_code=401, detail="Missing X-Webhook-Secret header")

    # Find user with matching webhook secret
    users = db.query(User).all()
    for user in users:
        prefs = user.preferences or {}
        if prefs.get("webhook_secret") == x_webhook_secret:
            return user

    raise HTTPException(status_code=401, detail="Invalid webhook secret")


# ============ Outbound Webhook Helper ============

async def dispatch_to_n8n(event_type: str, payload: Dict[str, Any], workspace_id: Optional[str] = None, db: Session = None):
    """
    Dispatch an event to n8n for workflow automation.
    
    If workspace_id is provided, it uses workspace-specific n8n settings (BYO n8n).
    Otherwise, it falls back to the default system n8n.
    """
    from app.services.n8n_client import get_n8n_client
    from app.services.workspace_service import WorkspaceService

    workspace_settings = None
    if workspace_id and db:
        workspace_settings = WorkspaceService.get_settings(workspace_id, db)

    client = get_n8n_client(workspace_settings)
    
    # Standardize the event envelope
    event = {
        "type": event_type,
        "source": "focus-kraliki",
        "timestamp": datetime.utcnow().isoformat(),
        "organizationId": workspace_id,
        "data": payload
    }

    try:
        await client.dispatch_event(event)
        logger.info(f"Dispatched {event_type} to n8n")
    except Exception as e:
        # Don't fail the primary action if orchestration fails
        logger.warning(f"Orchestration dispatch failed: {e}")


# ============ Webhook Endpoints ============

@router.get("/status")
@limiter.limit("60/minute")
async def webhook_status(request: Request):
    """Check webhook system status"""
    # Check Darwin2 connection
    darwin2_healthy = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{DARWIN2_N8N_API}/health")
            darwin2_healthy = response.status_code == 200
    except Exception as e:
        logger.debug(f"Darwin2 health check failed (non-critical): {e}")

    return {
        "status": "healthy",
        "service": "focus-kraliki-webhooks",
        "darwin2_connected": darwin2_healthy,
        "darwin2_api": DARWIN2_N8N_API,
        "supported_events": [
            "task-create",
            "task-complete",
            "workflow-execute",
            "event-create"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/task/create", response_model=WebhookResponse)
@limiter.limit("30/minute")
async def webhook_create_task(
    request: Request,
    payload: WebhookTaskCreate,
    user: User = Depends(get_user_by_webhook_secret),
    db: Session = Depends(get_db)
):
    """
    Create a task from external webhook (n8n, Zapier, etc.)

    Requires X-Webhook-Secret header matching user's webhook_secret preference.
    Rate limited to 30 requests/minute per client IP.
    """
    task = Task(
        id=generate_id(),
        userId=user.id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        status=TaskStatus.PENDING,
        estimatedMinutes=payload.estimatedMinutes,
        tags=payload.tags + ["webhook"],
        createdAt=datetime.utcnow()
    )

    if payload.dueDate:
        try:
            task.dueDate = datetime.fromisoformat(payload.dueDate.replace("Z", "+00:00"))
        except ValueError as e:
            logger.warning(f"Failed to parse dueDate '{payload.dueDate}' for user {user.id}: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid dueDate format: {payload.dueDate}. Expected ISO format.")

    db.add(task)
    db.commit()
    db.refresh(task)

    # Notify n8n
    await dispatch_to_n8n("task-created", {
        "title": task.title,
        "task_id": task.id,
        "user_id": user.id
    }, workspace_id=user.activeWorkspaceId, db=db)

    return WebhookResponse(
        success=True,
        message=f"Task created: {task.title}",
        data={"taskId": task.id, "title": task.title}
    )


@router.post("/task/complete", response_model=WebhookResponse)
@limiter.limit("30/minute")
async def webhook_complete_task(
    request: Request,
    payload: WebhookTaskComplete,
    user: User = Depends(get_user_by_webhook_secret),
    db: Session = Depends(get_db)
):
    """
    Mark a task as complete from external webhook.

    Useful for automation workflows that complete tasks in external systems.
    Rate limited to 30 requests/minute per client IP.
    """
    task = db.query(Task).filter(
        Task.id == payload.taskId,
        Task.userId == user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = TaskStatus.COMPLETED
    task.completedAt = datetime.utcnow()

    if payload.notes:
        task.description = (task.description or "") + f"\n\n[Webhook] {payload.notes}"

    db.commit()

    # Notify n8n
    await dispatch_to_n8n("task-complete", {
        "title": task.title,
        "task_id": task.id,
        "user_id": user.id
    }, workspace_id=user.activeWorkspaceId, db=db)

    return WebhookResponse(
        success=True,
        message=f"Task completed: {task.title}",
        data={"taskId": task.id, "title": task.title}
    )


@router.post("/workflow/execute", response_model=WebhookResponse)
@limiter.limit("30/minute")
async def webhook_execute_workflow(
    request: Request,
    payload: WebhookWorkflowExecute,
    user: User = Depends(get_user_by_webhook_secret),
    db: Session = Depends(get_db)
):
    """
    Execute a workflow template from external webhook.

    Creates parent task and subtasks from workflow steps.
    Rate limited to 30 requests/minute per client IP.
    """
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.id == payload.templateId
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Workflow template not found")

    # Check access
    if (template.userId != user.id and
        not template.isPublic and
        not template.isSystem):
        raise HTTPException(status_code=403, detail="Access denied")

    # Create parent task
    parent_task = Task(
        id=generate_id(),
        userId=user.id,
        title=payload.customTitle or template.name,
        description=template.description,
        priority=payload.priority,
        status=TaskStatus.PENDING,
        tags=template.tags + ["workflow", "webhook"],
        estimatedMinutes=template.totalEstimatedMinutes,
        createdAt=datetime.utcnow()
    )

    if payload.startDate:
        try:
            parent_task.dueDate = datetime.fromisoformat(payload.startDate.replace("Z", "+00:00"))
        except ValueError as e:
            logger.warning(f"Failed to parse startDate '{payload.startDate}' for user {user.id}: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid startDate format: {payload.startDate}. Expected ISO format.")

    db.add(parent_task)

    # Create subtasks
    created_tasks = []
    for step in template.steps:
        subtask = Task(
            id=generate_id(),
            userId=user.id,
            parentTaskId=parent_task.id,
            title=step.get("action", f"Step {step.get('step')}"),
            description=f"Workflow step {step.get('step')}",
            priority=payload.priority,
            status=TaskStatus.PENDING,
            estimatedMinutes=step.get("estimatedMinutes", 30),
            tags=[f"workflow:{template.name}"],
            createdAt=datetime.utcnow()
        )
        db.add(subtask)
        created_tasks.append(subtask.id)

    # Increment usage count
    template.usageCount += 1

    db.commit()

    # Notify n8n
    await dispatch_to_n8n("workflow-executed", {
        "title": template.name,
        "workflow_id": template.id,
        "parent_task_id": parent_task.id,
        "subtasks_created": len(created_tasks)
    }, workspace_id=user.activeWorkspaceId, db=db)

    return WebhookResponse(
        success=True,
        message=f"Workflow executed: {template.name}",
        data={
            "parentTaskId": parent_task.id,
            "createdTasks": created_tasks,
            "totalTasks": len(created_tasks)
        }
    )


@router.post("/event/create", response_model=WebhookResponse)
@limiter.limit("30/minute")
async def webhook_create_event(
    request: Request,
    payload: WebhookEventCreate,
    user: User = Depends(get_user_by_webhook_secret),
    db: Session = Depends(get_db)
):
    """
    Create a calendar event from external webhook.

    Useful for syncing events from n8n workflows.
    Rate limited to 30 requests/minute per client IP.
    """
    event = Event(
        id=generate_id(),
        user_id=user.id,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    try:
        event.start_time = datetime.fromisoformat(payload.start_time.replace("Z", "+00:00"))
        if payload.end_time:
            event.end_time = datetime.fromisoformat(payload.end_time.replace("Z", "+00:00"))
        else:
            # Default 1 hour duration
            from datetime import timedelta
            event.end_time = event.start_time + timedelta(hours=1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")

    db.add(event)
    db.commit()
    db.refresh(event)

    # Notify n8n
    await dispatch_to_n8n("event-created", {
        "title": event.title,
        "event_id": event.id,
        "start_time": event.start_time.isoformat()
    }, workspace_id=user.activeWorkspaceId, db=db)

    return WebhookResponse(
        success=True,
        message=f"Event created: {event.title}",
        data={
            "eventId": event.id,
            "title": event.title,
            "startTime": event.start_time.isoformat()
        }
    )


@router.post("/config/secret")
@limiter.limit("5/minute")
async def generate_webhook_secret(
    request: Request,
    db: Session = Depends(get_db),
    x_api_key: str = Header(None)
):
    """
    Generate a new webhook secret for API key authenticated user.

    This endpoint requires regular API key auth, not webhook auth.
    Returns the new webhook secret to store for future webhook calls.
    Rate limited to 5 requests/minute per client IP (sensitive operation).
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")

    # Find user by API key (stored in preferences)
    users = db.query(User).all()
    user = None
    for u in users:
        prefs = u.preferences or {}
        if prefs.get("api_key") == x_api_key:
            user = u
            break

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Generate new webhook secret
    import secrets
    new_secret = f"whsec_{secrets.token_urlsafe(32)}"

    # Store in user preferences
    prefs = user.preferences or {}
    prefs["webhook_secret"] = new_secret
    user.preferences = prefs
    db.commit()

    return {
        "success": True,
        "webhook_secret": new_secret,
        "message": "Store this secret securely. Use it in X-Webhook-Secret header for webhook calls."
    }
