"""
Unit tests for AI Scheduler Service
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.models.time_entry import TimeEntry
from app.services.ai_scheduler import AISchedulerService

def test_prioritize_tasks_urgency(db: Session, test_user):
    """Test prioritization based on urgency (due date)"""
    now = datetime.utcnow()
    
    # Task 1: Due today (urgent)
    t1 = Task(
        id="t1",
        userId=test_user.id,
        title="Urgent Task",
        dueDate=now,
        priority=3 # medium
    )
    
    # Task 2: Due in 30 days (not urgent)
    t2 = Task(
        id="t2",
        userId=test_user.id,
        title="Future Task",
        dueDate=now + timedelta(days=30),
        priority=3 # medium
    )
    
    results = AISchedulerService.prioritize_tasks([t1, t2], test_user.id, db)
    
    assert len(results) == 2
    # t1 should have higher score than t2
    score1 = next(r["priority_score"] for r in results if r["task"].id == "t1")
    score2 = next(r["priority_score"] for r in results if r["task"].id == "t2")
    assert score1 > score2


def test_prioritize_tasks_priority(db: Session, test_user):
    """Test prioritization based on user priority"""
    t1 = Task(id="t1", userId=test_user.id, title="High", priority=5) # High
    t2 = Task(id="t2", userId=test_user.id, title="Low", priority=1) # Low
    
    results = AISchedulerService.prioritize_tasks([t1, t2], test_user.id, db)
    
    score1 = next(r["priority_score"] for r in results if r["task"].id == "t1")
    score2 = next(r["priority_score"] for r in results if r["task"].id == "t2")
    assert score1 > score2


def test_prioritize_tasks_dependencies(db: Session, test_user):
    """Test prioritization based on dependencies"""
    # Parent task (blocked by nothing)
    parent = Task(id="p1", userId=test_user.id, title="Parent", priority=3, status=TaskStatus.PENDING)
    
    # Child task (blocked by parent)
    t1 = Task(id="t1", userId=test_user.id, title="Child", parentTaskId="p1", priority=3, status=TaskStatus.PENDING)
    t2 = Task(id="t2", userId=test_user.id, title="Orphan", priority=3, status=TaskStatus.PENDING)
    
    # We need to pass both to the function so it can resolve parent
    results = AISchedulerService.prioritize_tasks([parent, t1, t2], test_user.id, db)
    
    # Just verify t1 got some dependency score boost
    item1 = next(r for r in results if r["task"].id == "t1")
    assert item1["dependency_context"]["blockedBy"]["id"] == "p1"
    # Score breakdown check
    assert item1["score_breakdown"]["dependencies"] > 0


def test_suggest_schedule(db: Session, test_user):
    """Test schedule suggestion"""
    t1 = Task(
        id="t1", 
        userId=test_user.id, 
        title="Task 1", 
        estimatedMinutes=120, # 2 hours
        priority=5, # High
        status=TaskStatus.PENDING
    )
    t2 = Task(
        id="t2", 
        userId=test_user.id, 
        title="Task 2", 
        estimatedMinutes=60, # 1 hour
        priority=1, # Low
        status=TaskStatus.PENDING
    )
    
    schedule_data = AISchedulerService.suggest_schedule(
        [t1, t2], 
        test_user.id, 
        db,
        start_date=datetime(2025, 1, 1, 9, 0),
        available_hours_per_day=8
    )
    
    schedule = schedule_data["schedule"]
    assert len(schedule) == 2
    assert schedule_data["total_hours"] == 3.0
    
    # Verify time slots
    slot1 = schedule[0] 
    assert slot1["task_id"] == "t1"
    assert slot1["estimated_hours"] == 2.0


def test_get_focus_recommendations_empty(db: Session, test_user):
    """Test focus recommendations with no data"""
    recs = AISchedulerService.get_focus_recommendations(test_user.id, db)
    assert "Not enough data" in recs["message"]
    assert len(recs["recommendations"]) == 0


def test_get_focus_recommendations_with_data(db: Session, test_user):
    """Test focus recommendations with time entries"""
    # Create task first
    task = Task(id="t1", userId=test_user.id, title="Task 1", priority=3, status=TaskStatus.PENDING)
    db.add(task)
    
    # Create some time entries
    base_time = datetime(2025, 1, 1, 10, 0) # 10 AM
    
    for i in range(5):
        entry = TimeEntry(
            id=f"te{i}",
            user_id=test_user.id,
            task_id="t1",
            start_time=base_time + timedelta(days=i),
            end_time=base_time + timedelta(days=i, minutes=50),
            duration_seconds=50*60
        )
        db.add(entry)
    db.commit()
    
    recs = AISchedulerService.get_focus_recommendations(test_user.id, db)
    
    assert len(recs["recommendations"]) > 0
    # Should recommend 10 AM as peak hour
    peak_hours = recs["peak_productivity_hours"]
    assert 10 in peak_hours


def test_detect_distractions(db: Session, test_user):
    """Test distraction detection"""
    # Create task first
    task = Task(id="t1", userId=test_user.id, title="Task 1", priority=3, status=TaskStatus.PENDING)
    db.add(task)

    # Create many short sessions
    now = datetime.utcnow()
    for i in range(6):
        entry = TimeEntry(
            id=f"te{i}",
            user_id=test_user.id,
            task_id="t1",
            start_time=now - timedelta(minutes=20*i),
            end_time=now - timedelta(minutes=20*i) + timedelta(minutes=5),
            duration_seconds=5*60 # 5 minutes
        )
        db.add(entry)
    db.commit()
    
    alerts = AISchedulerService.detect_distractions(test_user.id, db, threshold_minutes=10)
    
    assert len(alerts) > 0
    short_session_alert = next((a for a in alerts if a["type"] == "short_sessions"), None)
    assert short_session_alert is not None
    assert short_session_alert["count"] >= 6
