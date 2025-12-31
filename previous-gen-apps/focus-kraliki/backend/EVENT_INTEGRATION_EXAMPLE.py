"""
Event Publishing Integration Examples for Focus by Kraliki

Events to publish:
1. task.created - New task created (Agents module can suggest workflow)
2. task.completed - Task completed (trigger campaign or notification)
3. project.milestone_reached - Project milestone (send team notification)
4. shadow.insight_generated - Shadow analysis insight (store in Flow Memory)
5. flow_memory.context_updated - AI context available (cross-session)
"""

from fastapi import APIRouter, Depends
from app.core.events import event_publisher
from app.core.ed25519_auth import get_current_user
from datetime import datetime

router = APIRouter()

# Example 1: Task created event
@router.post("/tasks")
async def create_task(task_data: dict, current_user = Depends(get_current_user)):
    # ... existing task creation logic ...
    task_id = "task-123"

    await event_publisher.publish(
        event_type="task.created",
        data={
            "task_id": task_id,
            "title": task_data.get("title"),
            "priority": task_data.get("priority"),
            "assignee_id": task_data.get("assignee_id"),
            "project_id": task_data.get("project_id")
        },
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    return {"id": task_id, "event_published": True}

# Example 2: Task completed event
@router.patch("/tasks/{task_id}/complete")
async def complete_task(task_id: str, current_user = Depends(get_current_user)):
    # ... existing completion logic ...

    await event_publisher.publish(
        event_type="task.completed",
        data={
            "task_id": task_id,
            "completed_at": datetime.utcnow().isoformat(),
            "completed_by": current_user.get("sub"),
            "outcome": "success"
        },
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    return {"status": "completed", "event_published": True}

# Example 3: Project milestone reached
@router.post("/projects/{project_id}/milestone")
async def reach_milestone(project_id: str, milestone: str, current_user = Depends(get_current_user)):

    await event_publisher.publish(
        event_type="project.milestone_reached",
        data={
            "project_id": project_id,
            "milestone": milestone,
            "progress": 75,
            "team_members": ["user-1", "user-2"]
        },
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    return {"milestone": milestone, "notification_sent": True}

# Example 4: Shadow insight generated
@router.post("/shadow/analyze")
async def generate_insight(data: dict, current_user = Depends(get_current_user)):
    # ... AI shadow analysis ...

    await event_publisher.publish(
        event_type="shadow.insight_generated",
        data={
            "insight_type": "workflow_optimization",
            "content": "Consider batching similar tasks",
            "confidence": 0.85,
            "applicable_to": ["task-1", "task-2"]
        },
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    return {"insight_generated": True}

# Example 5: Flow memory context updated
@router.post("/flow-memory/update")
async def update_context(context: dict, current_user = Depends(get_current_user)):

    await event_publisher.publish(
        event_type="flow_memory.context_updated",
        data={
            "context_type": "project_preferences",
            "embedding_id": "emb-123",
            "available_for_retrieval": True
        },
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    return {"context_stored": True}
