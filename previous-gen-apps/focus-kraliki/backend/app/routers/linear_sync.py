"""
Linear Sync Router - Sync Focus by Kraliki tasks to Linear issues

This enables the Flow:
BRAIN (strategy) → FOCUS (tasks) → LINEAR (issues) → SWARM (execution)
"""

import os
import logging
from datetime import datetime
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security_v2 import decode_token
from app.core.webhook_security import linear_webhook_verifier
from app.models.user import User
from app.models.task import Task, TaskStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/linear", tags=["linear-sync"])

LINEAR_API_URL = "https://api.linear.app/graphql"
LINEAR_API_KEY_PATH = "/home/adminmatej/github/secrets/linear_api_key.txt"


class SyncRequest(BaseModel):
    labels: Optional[list[str]] = ["GIN", "GIN-DEV"]
    priority: Optional[str] = "medium"  # urgent, high, medium, low
    team_key: Optional[str] = "PRO"


class SyncResponse(BaseModel):
    success: bool
    linear_id: Optional[str] = None
    linear_url: Optional[str] = None
    message: str


@router.post("/webhook")
async def linear_webhook(
    payload: dict = Depends(linear_webhook_verifier.verify_linear_webhook),
    db: Session = Depends(get_db)
):
    """
    Handle Linear webhooks for issue updates.
    
    Syncs Linear issue status back to Focus by Kraliki tasks.
    """
    action = payload.get("action")
    data_type = payload.get("type")
    
    if data_type != "Issue":
        return {"status": "ignored", "reason": f"Unsupported type: {data_type}"}
    
    if action not in ["update", "create"]:
        return {"status": "ignored", "reason": f"Unsupported action: {action}"}
        
    data = payload.get("data", {})
    linear_id = data.get("id")
    state = data.get("state", {})
    state_type = state.get("type")
    state_name = state.get("name")
    
    if not linear_id or not state_type:
        return {"status": "error", "message": "Missing linear_id or state_type"}
        
    # Find task with this linear_id
    task = db.query(Task).filter(Task.linear_id == linear_id).first()
    if not task:
        # It's okay if we don't have the task, might be from another app
        return {"status": "ignored", "reason": f"Task with linear_id {linear_id} not found"}
        
    # Map Linear state to Focus by Kraliki TaskStatus
    # Linear state types: backlog, unstarted, started, completed, canceled
    # Focus by Kraliki TaskStatus: PENDING, IN_PROGRESS, COMPLETED, ARCHIVED
    
    status_mapping = {
        "backlog": TaskStatus.PENDING,
        "unstarted": TaskStatus.PENDING,
        "started": TaskStatus.IN_PROGRESS,
        "completed": TaskStatus.COMPLETED,
        "canceled": TaskStatus.ARCHIVED
    }
    
    new_status = status_mapping.get(state_type)
    if not new_status:
        return {"status": "ignored", "reason": f"Unknown state type: {state_type}"}
        
    if task.status != new_status:
        old_status = task.status
        task.status = new_status
        if new_status == TaskStatus.COMPLETED:
            task.completedAt = datetime.utcnow()
            
        db.commit()
        logger.info(f"Updated task {task.id} status from {old_status} to {new_status} via Linear webhook (Issue {linear_id})")
        return {"status": "success", "task_id": task.id, "new_status": new_status}
        
    return {"status": "no_change", "task_id": task.id}


@router.post("/sync-task/{task_id}", response_model=SyncResponse)
async def sync_task_to_linear(
    task_id: str,
    sync_request: SyncRequest = SyncRequest(),
    db: Session = Depends(get_db),
):
    """
    Sync a Focus by Kraliki task to Linear.

    This creates a Linear issue from the Focus task, enabling the swarm to pick it up.
    """
    # Get task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if already synced
    if hasattr(task, "linear_id") and task.linear_id:
        return SyncResponse(
            success=True,
            linear_id=task.linear_id,
            message=f"Task already synced to Linear",
        )

    # Get Linear API key
    api_key = get_linear_api_key()

    # Get team ID
    team_key = sync_request.team_key or "PRO"
    team_id = await get_team_id(api_key, team_key)
    if not team_id:
        raise HTTPException(
            status_code=400, detail=f"Team '{team_key}' not found in Linear"
        )

    # Get or create labels
    label_ids = []
    for label_name in sync_request.labels:
        label_id = await get_or_create_label(api_key, team_id, label_name)
        if label_id:
            label_ids.append(label_id)

    # Map priority
    priority_map = {"urgent": 1, "high": 2, "medium": 3, "low": 4}
    priority = priority_map.get(sync_request.priority, 3)

    # Create issue
    description = (
        f"{task.description or ''}\n\n---\n*Synced from Focus by Kraliki (task: {task.id})*"
    )

    result = await create_linear_issue(
        api_key=api_key,
        team_id=team_id,
        title=task.title,
        description=description,
        priority=priority,
        label_ids=label_ids,
    )

    if not result.get("success"):
        return SyncResponse(
            success=False,
            message=f"Failed to create Linear issue: {result.get('error')}",
        )

    # Store linear_id on task (if model supports it)
    # Note: May need migration to add linear_id column
    try:
        task.linear_id = result.get("id")
        db.commit()
    except Exception as e:
        logger.warning(f"Could not store linear_id on task: {e}")

    return SyncResponse(
        success=True,
        linear_id=result.get("id"),
        linear_url=result.get("url"),
        message=f"Created Linear issue {result.get('identifier')}",
    )


@router.get("/status/{task_id}")
async def get_linear_status(task_id: str, db: Session = Depends(get_db)):
    """Get Linear sync status for a Focus task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    linear_id = getattr(task, "linear_id", None)

    if not linear_id:
        return {
            "synced": False,
            "linear_id": None,
            "message": "Task not synced to Linear",
        }

    # Get issue status from Linear
    api_key = get_linear_api_key()

    query = """
    query($id: String!) {
        issue(id: $id) {
            id
            identifier
            title
            state {
                name
                type
            }
            url
        }
    }
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            LINEAR_API_URL,
            headers={"Authorization": api_key, "Content-Type": "application/json"},
            json={"query": query, "variables": {"id": linear_id}},
        )

        if response.status_code == 200:
            data = response.json()
            issue = data.get("data", {}).get("issue", {})

            return {
                "synced": True,
                "linear_id": linear_id,
                "identifier": issue.get("identifier"),
                "title": issue.get("title"),
                "state": issue.get("state", {}).get("name"),
                "state_type": issue.get("state", {}).get("type"),
                "url": issue.get("url"),
            }

    return {
        "synced": True,
        "linear_id": linear_id,
        "message": "Could not fetch status from Linear",
    }


@router.post("/tasks/{task_id}/sync-to-linear", response_model=SyncResponse)
async def sync_task_to_linear_legacy(
    task_id: str,
    sync_request: SyncRequest = SyncRequest(),
    db: Session = Depends(get_db),
):
    """Legacy path for compatibility - sync a Focus by Kraliki task to Linear."""
    return await sync_task_to_linear(task_id, sync_request, db)


@router.get("/tasks/{task_id}/linear-status")
async def get_linear_status_legacy(task_id: str, db: Session = Depends(get_db)):
    """Legacy path for compatibility - get Linear sync status for a Focus task."""
    return await get_linear_status(task_id, db)
