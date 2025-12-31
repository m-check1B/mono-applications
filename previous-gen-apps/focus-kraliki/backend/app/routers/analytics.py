import logging
from fastapi import APIRouter, Depends, HTTPException, Query

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.knowledge_item import KnowledgeItem
from app.models.item_type import ItemType
from app.models.task import TaskStatus
from app.models.time_entry import TimeEntry
from app.models.workspace import WorkspaceMember
from app.schemas.workspace import WorkspaceResponse
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/analytics", tags=["analytics"])

def _get_tasks_type_id(db: Session, user_id: str) -> Optional[str]:
    task_type = db.query(ItemType).filter(
        ItemType.userId == user_id,
        ItemType.name == "Tasks"
    ).first()
    return task_type.id if task_type else None

def _load_workspace_task_items(workspace_id: str, db: Session, user_id: str) -> List[KnowledgeItem]:
    type_id = _get_tasks_type_id(db, user_id)
    if not type_id:
        return []
        
    # Load all tasks for user and filter by workspace in python
    # (Inefficient for large datasets, but compatible with JSON metadata)
    items = db.query(KnowledgeItem).filter(
        KnowledgeItem.userId == user_id,
        KnowledgeItem.typeId == type_id
    ).all()
    
    workspace_items = []
    for item in items:
        meta = item.item_metadata or {}
        if meta.get("workspaceId") == workspace_id:
            workspace_items.append(item)
            
    return workspace_items

def _calculate_task_metrics(items: List[KnowledgeItem]) -> Dict[str, Any]:
    total = len(items)
    
    completed = []
    in_progress = []
    pending = []
    overdue = []
    
    now = datetime.utcnow()
    
    for item in items:
        meta = item.item_metadata or {}
        status = meta.get("status", "PENDING")
        
        if item.completed or status == "COMPLETED":
            completed.append(item)
        elif status == "IN_PROGRESS":
            in_progress.append(item)
        else:
            pending.append(item)
            
        # Check overdue
        if meta.get("dueDate") and not (item.completed or status == "COMPLETED"):
            try:
                due_date = datetime.fromisoformat(meta["dueDate"])
                if due_date < now:
                    overdue.append((item, due_date))
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse dueDate '{meta.get('dueDate')}' for item {item.id}: {e}")

    # Completion times
    completion_times = []
    for item in completed:
        meta = item.item_metadata or {}
        if meta.get("completedAt"):
            try:
                completed_at = datetime.fromisoformat(meta["completedAt"])
                # KnowledgeItem doesn't store specific created_at in metadata usually, use item.createdAt
                created_at = item.createdAt
                completion_times.append((completed_at - created_at).total_seconds())
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse completedAt '{meta.get('completedAt')}' for item {item.id}: {e}")

    avg_completion_days = round(
        (sum(completion_times) / len(completion_times)) / 86400, 2
    ) if completion_times else 0

    # Velocity
    velocity_data = defaultdict(int)
    for item in completed:
        meta = item.item_metadata or {}
        if meta.get("completedAt"):
            try:
                completed_at = datetime.fromisoformat(meta["completedAt"])
                day = completed_at.date()
                velocity_data[day] += 1
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse completedAt '{meta.get('completedAt')}' for item {item.id}: {e}")

    velocity = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        velocity.append({"date": day.isoformat(), "completed": velocity_data.get(day, 0)})

    return {
        "total": total,
        "completed": len(completed),
        "pending": len(pending),
        "inProgress": len(in_progress),
        "overdue": len(overdue),
        "overdueTasks": [
            {"id": item.id, "title": item.title, "dueDate": due_date.isoformat()}
            for item, due_date in overdue[:5]
        ],
        "avgCompletionDays": avg_completion_days,
        "velocity": velocity
    }


def _load_time_metrics(workspace_id: str, db: Session) -> Dict[str, any]:
    now = datetime.utcnow()
    start = now - timedelta(days=7)

    entries = db.query(TimeEntry).filter(
        TimeEntry.workspace_id == workspace_id,
        TimeEntry.end_time.isnot(None),
        TimeEntry.start_time >= start
    ).all()

    total_seconds = sum(entry.duration_seconds or 0 for entry in entries)
    avg_session_minutes = (
        (total_seconds / len(entries)) / 60 if entries else 0
    )

    daily_breakdown = defaultdict(int)
    for entry in entries:
        day = entry.start_time.date()
        daily_breakdown[day] += entry.duration_seconds or 0

    breakdown = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        breakdown.append({
            "date": day.isoformat(),
            "hours": round(daily_breakdown.get(day, 0) / 3600, 2)
        })

    return {
        "hoursTrackedLast7Days": round(total_seconds / 3600, 2),
        "avgSessionMinutes": round(avg_session_minutes, 1),
        "dailyBreakdown": breakdown
    }


def _detect_bottlenecks(items: List[KnowledgeItem]) -> List[Dict[str, any]]:
    now = datetime.utcnow()
    bottlenecks: List[Dict[str, any]] = []

    # Simple bottleneck detection for items
    for item in items:
        meta = item.item_metadata or {}
        status = meta.get("status", "PENDING")
        
        # Overdue
        if meta.get("dueDate") and not item.completed and status != "COMPLETED":
            try:
                due_date = datetime.fromisoformat(meta["dueDate"])
                if due_date < now:
                    bottlenecks.append({
                        "taskId": item.id,
                        "title": item.title,
                        "type": "overdue",
                        "detail": "Task is past due date",
                        "severity": "high"
                    })
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse dueDate '{meta.get('dueDate')}' for item {item.id}: {e}")

        # Stuck tasks
        if status == "IN_PROGRESS":
            age_days = (now - (item.createdAt or now)).days
            if age_days > 7:
                bottlenecks.append({
                    "taskId": item.id,
                    "title": item.title,
                    "type": "stalled",
                    "detail": f"In progress for {age_days} days",
                    "severity": "medium"
                })

    # Sort by severity and limit
    severity_order = {"high": 0, "medium": 1, "low": 2}
    bottlenecks.sort(key=lambda x: severity_order.get(x["severity"], 3))
    return bottlenecks[:10]


@router.get("/overview")
async def get_analytics_overview(
    workspaceId: Optional[str] = Query(None, description="Workspace to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        workspace = WorkspaceService.get_workspace_with_access(current_user, workspaceId, db)
    except HTTPException:
        workspace = WorkspaceService.ensure_default_workspace(current_user, db)
    items = _load_workspace_task_items(workspace.id, db, current_user.id)
    task_metrics = _calculate_task_metrics(items)
    focus_metrics = _load_time_metrics(workspace.id, db)
    bottlenecks = _detect_bottlenecks(items)

    return {
        "workspace": WorkspaceResponse(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
            color=workspace.color,
            ownerId=workspace.ownerId,
            createdAt=workspace.createdAt,
            updatedAt=workspace.updatedAt,
            settings=workspace.settings,
            memberCount=db.query(WorkspaceMember).filter(WorkspaceMember.workspaceId == workspace.id).count()
        ),
        "taskMetrics": task_metrics,
        "focusMetrics": focus_metrics,
        "bottlenecks": bottlenecks
    }


@router.get("/bottlenecks")
async def get_bottlenecks(
    workspaceId: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        workspace = WorkspaceService.get_workspace_with_access(current_user, workspaceId, db)
    except HTTPException:
        workspace = WorkspaceService.ensure_default_workspace(current_user, db)
    items = _load_workspace_task_items(workspace.id, db, current_user.id)
    return {
        "workspaceId": workspace.id,
        "bottlenecks": _detect_bottlenecks(items)
    }

# Backwards compatibility alias for agent_tools import
_load_workspace_tasks = _load_workspace_task_items
