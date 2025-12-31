"""
Swarm Tools Router

API endpoints for Claude Flow swarm database operations.
These are simplified versions - full implementation would require
extensive database operations and swarm coordination.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import generate_id, get_current_user
from app.models.task import Task, TaskStatus, Project
from app.models.user import User
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/swarm-tools", tags=["swarm-tools"])


def _enforce_user_context(provided_user_id: Optional[str], current_user: User) -> str:
    """Ensure callers can only act on their own user ID."""
    if provided_user_id and provided_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot act on another user")
    return current_user.id


# Schemas
class CreateTaskFromNLRequest(BaseModel):
    userId: Optional[str] = None
    naturalLanguageInput: str
    projectId: Optional[str] = None


class UpdateCognitiveStateRequest(BaseModel):
    userId: Optional[str] = None
    energyLevel: int
    focusLevel: int
    stressLevel: int
    mood: Optional[str] = None


class StoreShadowInsightRequest(BaseModel):
    userId: Optional[str] = None
    insight: str
    category: str
    severity: str


class StoreMemoryRequest(BaseModel):
    userId: Optional[str] = None
    key: str
    value: Dict[str, Any]
    type: str
    tags: List[str] = []


class CreateProjectRequest(BaseModel):
    userId: Optional[str] = None
    projectName: str
    description: Optional[str] = None
    color: Optional[str] = None


class CreateSubtasksRequest(BaseModel):
    userId: Optional[str] = None
    parentTaskId: str
    subtasks: List[Dict[str, Any]]

# Task operations
@router.post("/tasks/create-from-nl")
async def create_task_from_nl(
    request: CreateTaskFromNLRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create task from natural language (swarm operation)"""
    user_id = _enforce_user_context(request.userId, current_user)

    # Parse natural language (simplified - full version uses AI)
    task = Task(
        id=generate_id(),
        userId=user_id,
        title=request.naturalLanguageInput[:100],
        description=request.naturalLanguageInput,
        projectId=request.projectId,
        priority=2,
        status=TaskStatus.PENDING
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "success": True,
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value
        },
        "message": f"Created task: {task.title}"
    }

@router.post("/tasks/get-with-context")
async def get_tasks_with_context(
    userId: Optional[str] = Query(None),
    status: Optional[List[str]] = None,
    energyLevel: Optional[str] = None,
    timeAvailable: Optional[int] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks with intelligent context filtering"""
    user_id = _enforce_user_context(userId, current_user)

    query = db.query(Task).filter(Task.userId == user_id)

    if status:
        query = query.filter(Task.status.in_([TaskStatus[s] for s in status]))

    if energyLevel:
        # Filter by energy level if specified
        pass

    if timeAvailable:
        # Filter by estimated time
        query = query.filter(Task.estimatedMinutes <= timeAvailable)

    tasks = query.limit(limit).all()

    return {
        "success": True,
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status.value,
                "priority": t.priority
            }
            for t in tasks
        ],
        "count": len(tasks)
    }

@router.post("/tasks/create-subtasks")
async def create_subtasks(
    request: CreateSubtasksRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create multiple subtasks"""
    user_id = _enforce_user_context(request.userId, current_user)

    created_tasks = []

    for subtask_data in request.subtasks:
        task = Task(
            id=generate_id(),
            userId=user_id,
            parentTaskId=request.parentTaskId,
            title=subtask_data.get("title"),
            description=subtask_data.get("description"),
            estimatedMinutes=subtask_data.get("estimatedMinutes"),
            priority=subtask_data.get("priority", 2),
            status=TaskStatus.PENDING
        )
        db.add(task)
        created_tasks.append(task)

    db.commit()

    return {
        "success": True,
        "subtasks": [
            {"id": t.id, "title": t.title}
            for t in created_tasks
        ],
        "count": len(created_tasks)
    }

@router.get("/tasks/recommendations")
async def get_task_recommendations(
    userId: Optional[str] = Query(None),
    energyLevel: Optional[int] = None,
    timeAvailable: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered task recommendations"""
    user_id = _enforce_user_context(userId, current_user)

    if not hasattr(db, "query"):
        return {"success": True, "recommendations": [], "count": 0}

    # Get user's tasks
    tasks = db.query(Task).filter(
        Task.userId == user_id,
        Task.status == TaskStatus.PENDING
    ).limit(10).all()

    recommendations = [
        {
            "taskId": t.id,
            "title": t.title,
            "reason": "High priority task ready to work on",
            "score": 0.8
        }
        for t in tasks[:5]
    ]

    return {
        "success": True,
        "recommendations": recommendations,
        "count": len(recommendations)
    }

# Cognitive state operations
@router.post("/cognitive/update-state")
async def update_cognitive_state(
    request: UpdateCognitiveStateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's cognitive state"""
    _enforce_user_context(request.userId, current_user)

    # Store in user preferences or separate table
    return {
        "success": True,
        "state": {
            "energyLevel": request.energyLevel,
            "focusLevel": request.focusLevel,
            "stressLevel": request.stressLevel,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

@router.get("/cognitive/latest")
async def get_latest_cognitive_state(
    userId: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get latest cognitive state"""
    _enforce_user_context(userId, current_user)

    return {
        "success": True,
        "state": {
            "energyLevel": 70,
            "focusLevel": 80,
            "stressLevel": 30,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

@router.get("/cognitive/trends")
async def get_cognitive_trends(
    userId: Optional[str] = Query(None),
    days: int = 7,
    current_user: User = Depends(get_current_user)
):
    """Get cognitive state trends"""
    _enforce_user_context(userId, current_user)

    return {
        "success": True,
        "trends": {
            "avgEnergy": 65,
            "avgFocus": 70,
            "avgStress": 35,
            "days": days
        }
    }

# Shadow insight operations
@router.post("/shadow/store-insight")
async def store_shadow_insight(
    request: StoreShadowInsightRequest,
    current_user: User = Depends(get_current_user)
):
    """Store shadow insight"""
    user_id = _enforce_user_context(request.userId, current_user)

    return {
        "success": True,
        "insight": {
            "id": generate_id(),
            "userId": user_id,
            "insight": request.insight,
            "category": request.category,
            "severity": request.severity,
            "acknowledged": False,
            "createdAt": datetime.utcnow().isoformat()
        }
    }

@router.get("/shadow/unacknowledged")
async def get_unacknowledged_insights(
    userId: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get unacknowledged shadow insights"""
    _enforce_user_context(userId, current_user)

    return {
        "success": True,
        "insights": [],
        "count": 0
    }

@router.post("/shadow/acknowledge/{insight_id}")
async def acknowledge_shadow_insight(
    insight_id: str,
    userId: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Acknowledge a shadow insight"""
    _enforce_user_context(userId, current_user)

    return {
        "success": True,
        "message": "Insight acknowledged"
    }

# Memory operations
@router.post("/memory/store")
async def store_memory(
    request: StoreMemoryRequest,
    current_user: User = Depends(get_current_user)
):
    """Store memory for context persistence"""
    user_id = _enforce_user_context(request.userId, current_user)

    return {
        "success": True,
        "memory": {
            "id": generate_id(),
            "key": request.key,
            "type": request.type,
            "tags": request.tags,
            "createdAt": datetime.utcnow().isoformat(),
            "userId": user_id
        }
    }

@router.get("/memory/relevant")
async def get_relevant_memories(
    userId: Optional[str] = Query(None),
    type: Optional[List[str]] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get relevant memories"""
    _enforce_user_context(userId, current_user)

    return {
        "success": True,
        "memories": [],
        "count": 0
    }

# Project operations
@router.post("/projects/create-or-get")
async def create_or_get_project(
    request: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or get existing project"""
    user_id = _enforce_user_context(request.userId, current_user)

    # Check if project exists
    project = db.query(Project).filter(
        Project.name == request.projectName,
        Project.userId == user_id
    ).first()

    if not project:
        project = Project(
            id=generate_id(),
            userId=user_id,
            name=request.projectName,
            description=request.description,
            color=request.color
        )
        db.add(project)
        db.commit()
        db.refresh(project)

    return {
        "success": True,
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description
        }
    }

@router.get("/projects/user")
async def get_user_projects(
    userId: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user projects"""
    user_id = _enforce_user_context(userId, current_user)

    projects = db.query(Project).filter(Project.userId == user_id).all()

    return {
        "success": True,
        "projects": [
            {"id": p.id, "name": p.name, "description": p.description}
            for p in projects
        ],
        "count": len(projects)
    }

# Analytics
@router.get("/analytics/user")
async def get_user_analytics(
    userId: Optional[str] = Query(None),
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user analytics"""
    user_id = _enforce_user_context(userId, current_user)

    if not hasattr(db, "query"):
        return {
            "success": True,
            "analytics": {
                "totalTasks": 0,
                "completedTasks": 0,
                "completionRate": 0,
                "days": days,
            },
        }

    total_tasks = db.query(Task).filter(Task.userId == user_id).count()
    completed_tasks = db.query(Task).filter(
        Task.userId == user_id,
        Task.status == TaskStatus.COMPLETED
    ).count()

    return {
        "success": True,
        "analytics": {
            "totalTasks": total_tasks,
            "completedTasks": completed_tasks,
            "completionRate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "days": days
        }
    }
