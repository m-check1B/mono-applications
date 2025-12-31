"""
AI Scheduler Router - Smart task prioritization and scheduling
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.services.ai_scheduler import AISchedulerService

router = APIRouter(prefix="/ai", tags=["ai-scheduler"])


@router.get("/tasks/prioritize")
@limiter.limit("30/minute")  # Rate limit AI prioritization - involves computation
async def prioritize_tasks(
    request: Request,
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered task prioritization.

    Returns tasks sorted by intelligent priority score considering:
    - Deadline urgency
    - User priority
    - Estimated time
    - Task age
    - Project context
    """
    query = db.query(Task).filter(Task.userId == current_user.id)

    # Filter by status if provided
    if status:
        query = query.filter(Task.status == status)
    else:
        # Default: only show incomplete tasks
        query = query.filter(Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]))

    tasks = query.all()

    if not tasks:
        return {
            "prioritized_tasks": [],
            "total_tasks": 0,
            "message": "No tasks found"
        }

    prioritized = AISchedulerService.prioritize_tasks(
        tasks=tasks,
        user_id=current_user.id,
        db=db
    )

    # Format response
    result = []
    for item in prioritized:
        task = item["task"]
        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "due_date": task.dueDate.isoformat() if task.dueDate else None,
            "estimated_hours": (task.estimatedMinutes / 60) if task.estimatedMinutes else None,
            "priority_score": item["priority_score"],
            "urgency_level": item["urgency_level"],
            "recommendation": item["recommendation"],
            "score_breakdown": item.get("score_breakdown"),
            "dependency_context": item.get("dependency_context")
        })

    return {
        "prioritized_tasks": result,
        "total_tasks": len(result),
        "algorithm": "AI-powered multi-factor prioritization"
    }


@router.get("/schedule/suggest")
@limiter.limit("20/minute")  # Rate limit AI schedule suggestions - involves computation
async def suggest_schedule(
    request: Request,
    start_date: Optional[str] = Query(None, description="Schedule start date (ISO format)"),
    available_hours: int = Query(default=8, ge=1, le=16, description="Available hours per day"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate optimal task schedule based on AI analysis.

    Considers:
    - Task priorities and deadlines
    - User's peak productivity hours
    - Task dependencies
    - Available time per day
    """
    # Get incomplete tasks
    tasks = db.query(Task).filter(
        Task.userId == current_user.id,
        Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
    ).all()

    if not tasks:
        return {
            "schedule": [],
            "message": "No tasks to schedule"
        }

    # Parse start date
    start_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD)")

    # Generate schedule
    schedule = AISchedulerService.suggest_schedule(
        tasks=tasks,
        user_id=current_user.id,
        db=db,
        start_date=start_dt,
        available_hours_per_day=available_hours
    )

    return schedule


@router.get("/focus/recommendations")
@limiter.limit("30/minute")  # Rate limit focus recommendations
async def get_focus_recommendations(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized focus and productivity recommendations.

    Analyzes your work patterns to suggest:
    - Best times to focus on deep work
    - When to take breaks
    - Productivity insights
    """
    recommendations = AISchedulerService.get_focus_recommendations(
        user_id=current_user.id,
        db=db
    )

    return recommendations


@router.get("/distractions/detect")
@limiter.limit("30/minute")  # Rate limit distraction detection
async def detect_distractions(
    request: Request,
    threshold_minutes: int = Query(default=15, ge=5, le=60, description="Session length threshold"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detect potential distraction patterns and productivity issues.

    Analyzes recent time tracking to identify:
    - Unusually short work sessions
    - Gaps in time tracking
    - Inconsistent work patterns
    """
    alerts = AISchedulerService.detect_distractions(
        user_id=current_user.id,
        db=db,
        threshold_minutes=threshold_minutes
    )

    return {
        "alerts": alerts,
        "total_alerts": len(alerts),
        "analysis_period": "Last 7 days"
    }


@router.get("/insights/productivity")
@limiter.limit("15/minute")  # Rate limit productivity insights - complex analysis
async def get_productivity_insights(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Comprehensive productivity insights combining multiple AI analyses.

    Returns:
    - Task prioritization summary
    - Focus recommendations
    - Distraction alerts
    - Overall productivity score
    """
    # Get all incomplete tasks
    tasks = db.query(Task).filter(
        Task.userId == current_user.id,
        Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
    ).all()

    # Get prioritization
    prioritized = AISchedulerService.prioritize_tasks(tasks, current_user.id, db) if tasks else []

    # Get focus recommendations
    focus_recs = AISchedulerService.get_focus_recommendations(current_user.id, db)

    # Get distraction alerts
    distraction_alerts = AISchedulerService.detect_distractions(current_user.id, db)

    # Calculate productivity score (0-100)
    productivity_score = 50  # Base score

    # Boost for having few high-urgency overdue tasks
    critical_tasks = sum(1 for t in prioritized if t["urgency_level"] == "critical")
    productivity_score -= min(30, critical_tasks * 10)

    # Boost for consistent time tracking
    if "days_tracked" in focus_recs:
        days_tracked = focus_recs["days_tracked"]
        productivity_score += min(20, days_tracked * 3)

    # Penalty for many distractions
    productivity_score -= min(20, len(distraction_alerts) * 5)

    productivity_score = max(0, min(100, productivity_score))

    return {
        "productivity_score": productivity_score,
        "score_breakdown": {
            "task_management": 100 - (critical_tasks * 10),
            "time_tracking": min(100, (focus_recs.get("days_tracked", 0) * 20)),
            "focus_quality": max(0, 100 - (len(distraction_alerts) * 10))
        },
        "total_tasks": len(tasks),
        "critical_tasks": critical_tasks,
        "recommendations": focus_recs.get("recommendations", []),
        "alerts": distraction_alerts,
        "summary": AISchedulerService._get_productivity_summary(productivity_score)
    }


# Helper for productivity summary
def _get_productivity_summary(score: int) -> str:
    """Generate human-readable productivity summary."""
    if score >= 80:
        return "🌟 Excellent! You're highly productive and well-organized."
    elif score >= 60:
        return "✅ Good productivity! Some room for improvement."
    elif score >= 40:
        return "⚠️ Moderate productivity. Focus on prioritization and consistency."
    else:
        return "🔴 Low productivity. Consider reviewing your task management and time tracking habits."


# Patch the helper into the service
AISchedulerService._get_productivity_summary = staticmethod(_get_productivity_summary)
