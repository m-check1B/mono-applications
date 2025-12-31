"""
Unit tests for AISchedulerService - AI-powered task scheduling and prioritization
Tests task prioritization, schedule suggestions, focus recommendations, and distraction detection
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.time_entry import TimeEntry
from app.services.ai_scheduler import AISchedulerService, _normalize_priority
from app.core.security_v2 import generate_id


def create_time_entry_with_task(db: Session, user: User, start_time: datetime, end_time: datetime, duration_seconds: int) -> TimeEntry:
    """Helper to create a time entry with a corresponding task to satisfy FK constraint."""
    task_id = generate_id()
    task = Task(
        id=task_id,
        userId=user.id,
        title=f"Task {task_id[:8]}",
        status=TaskStatus.IN_PROGRESS,
        priority=3
    )
    db.add(task)

    entry = TimeEntry(
        id=generate_id(),
        user_id=user.id,
        task_id=task_id,
        start_time=start_time,
        end_time=end_time,
        duration_seconds=duration_seconds
    )
    db.add(entry)
    return entry


class TestNormalizePriority:
    """Test priority normalization helper function"""

    def test_normalize_priority_string_high(self):
        """String 'high' should normalize to 'high'"""
        assert _normalize_priority("high") == "high"
        assert _normalize_priority("HIGH") == "high"
        assert _normalize_priority("High") == "high"

    def test_normalize_priority_string_medium(self):
        """String 'medium' should normalize to 'medium'"""
        assert _normalize_priority("medium") == "medium"
        assert _normalize_priority("MEDIUM") == "medium"

    def test_normalize_priority_string_low(self):
        """String 'low' should normalize to 'low'"""
        assert _normalize_priority("low") == "low"
        assert _normalize_priority("LOW") == "low"

    def test_normalize_priority_integer_high(self):
        """Integer >= 4 should normalize to 'high'"""
        assert _normalize_priority(4) == "high"
        assert _normalize_priority(5) == "high"
        assert _normalize_priority(10) == "high"

    def test_normalize_priority_integer_medium(self):
        """Integer 2-3 should normalize to 'medium'"""
        assert _normalize_priority(2) == "medium"
        assert _normalize_priority(3) == "medium"

    def test_normalize_priority_integer_low(self):
        """Integer 0-1 should normalize to 'low'"""
        assert _normalize_priority(0) == "low"
        assert _normalize_priority(1) == "low"

    def test_normalize_priority_none(self):
        """None should normalize to 'low'"""
        assert _normalize_priority(None) == "low"

    def test_normalize_priority_invalid(self):
        """Invalid types should normalize to 'low'"""
        assert _normalize_priority("invalid") == "invalid"
        assert _normalize_priority([]) == "low"


class TestPrioritizeTasks:
    """Test task prioritization logic"""

    def test_prioritize_empty_list(self, test_user: User, db: Session):
        """Empty task list should return empty result"""
        result = AISchedulerService.prioritize_tasks([], test_user.id, db)
        assert result == []

    def test_prioritize_single_task(self, test_user: User, db: Session):
        """Single task should be returned with priority score"""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Test Task",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            createdAt=datetime.utcnow()
        )
        db.add(task)
        db.commit()

        result = AISchedulerService.prioritize_tasks([task], test_user.id, db)

        assert len(result) == 1
        assert result[0]["task"] == task
        assert "priority_score" in result[0]
        assert "urgency_level" in result[0]
        assert "recommendation" in result[0]

    def test_prioritize_overdue_task_highest_urgency(self, test_user: User, db: Session):
        """Overdue task should have highest urgency score"""
        overdue_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Overdue Task",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            dueDate=datetime.utcnow() - timedelta(days=1),
            createdAt=datetime.utcnow()
        )
        future_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Future Task",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            dueDate=datetime.utcnow() + timedelta(days=30),
            createdAt=datetime.utcnow()
        )
        db.add_all([overdue_task, future_task])
        db.commit()

        result = AISchedulerService.prioritize_tasks([overdue_task, future_task], test_user.id, db)

        # Overdue task should be first (highest priority)
        assert result[0]["task"].id == overdue_task.id
        assert result[0]["priority_score"] > result[1]["priority_score"]

    def test_prioritize_task_due_today(self, test_user: User, db: Session):
        """Task due today should have very high urgency"""
        today_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Due Today",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            dueDate=datetime.utcnow(),
            createdAt=datetime.utcnow()
        )
        db.add(today_task)
        db.commit()

        result = AISchedulerService.prioritize_tasks([today_task], test_user.id, db)

        assert result[0]["score_breakdown"]["urgency"] >= 90

    def test_prioritize_task_due_within_week(self, test_user: User, db: Session):
        """Task due within a week should have moderate urgency"""
        week_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Due This Week",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            dueDate=datetime.utcnow() + timedelta(days=5),
            createdAt=datetime.utcnow()
        )
        db.add(week_task)
        db.commit()

        result = AISchedulerService.prioritize_tasks([week_task], test_user.id, db)

        assert 50 < result[0]["score_breakdown"]["urgency"] < 80

    def test_prioritize_high_priority_over_low(self, test_user: User, db: Session):
        """High priority task should score higher than low priority"""
        high_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="High Priority",
            status=TaskStatus.PENDING,
            priority=5,  # high
            createdAt=datetime.utcnow()
        )
        low_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Low Priority",
            status=TaskStatus.PENDING,
            priority=1,  # low
            createdAt=datetime.utcnow()
        )
        db.add_all([high_task, low_task])
        db.commit()

        result = AISchedulerService.prioritize_tasks([low_task, high_task], test_user.id, db)

        # High priority should be first after sorting
        assert result[0]["task"].id == high_task.id
        assert result[0]["score_breakdown"]["importance"] > result[1]["score_breakdown"]["importance"]

    def test_prioritize_with_parent_task_dependency(self, test_user: User, db: Session):
        """Task with parent should have dependency context"""
        parent_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Parent Task",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            createdAt=datetime.utcnow()
        )
        db.add(parent_task)
        db.commit()

        child_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Child Task",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            parentTaskId=parent_task.id,
            createdAt=datetime.utcnow()
        )
        db.add(child_task)
        db.commit()

        result = AISchedulerService.prioritize_tasks([parent_task, child_task], test_user.id, db)

        # Find child task in results
        child_result = next(r for r in result if r["task"].id == child_task.id)
        assert child_result["dependency_context"]["blockedBy"] is not None
        assert child_result["dependency_context"]["blockedBy"]["id"] == parent_task.id

    def test_prioritize_with_child_tasks(self, test_user: User, db: Session):
        """Task with children should show blocking count"""
        parent_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Parent Task",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            createdAt=datetime.utcnow()
        )
        db.add(parent_task)
        db.commit()

        child1 = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Child 1",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            parentTaskId=parent_task.id,
            createdAt=datetime.utcnow()
        )
        child2 = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Child 2",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            parentTaskId=parent_task.id,
            createdAt=datetime.utcnow()
        )
        db.add_all([child1, child2])
        db.commit()

        result = AISchedulerService.prioritize_tasks([parent_task, child1, child2], test_user.id, db)

        # Find parent task in results
        parent_result = next(r for r in result if r["task"].id == parent_task.id)
        assert parent_result["dependency_context"]["blockingCount"] == 2

    def test_prioritize_in_progress_momentum_boost(self, test_user: User, db: Session):
        """In-progress task should get momentum boost"""
        in_progress_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="In Progress",
            status=TaskStatus.IN_PROGRESS,
            priority=3,  # medium
            createdAt=datetime.utcnow()
        )
        pending_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Pending",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            createdAt=datetime.utcnow()
        )
        db.add_all([in_progress_task, pending_task])
        db.commit()

        result = AISchedulerService.prioritize_tasks([pending_task, in_progress_task], test_user.id, db)

        in_progress_result = next(r for r in result if r["task"].id == in_progress_task.id)
        pending_result = next(r for r in result if r["task"].id == pending_task.id)

        assert in_progress_result["score_breakdown"]["momentum"] >= pending_result["score_breakdown"]["momentum"]

    def test_prioritize_old_task_momentum_boost(self, test_user: User, db: Session):
        """Old task should get momentum boost to prevent staleness"""
        old_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Old Task",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            createdAt=datetime.utcnow() - timedelta(days=21)
        )
        new_task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="New Task",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            createdAt=datetime.utcnow()
        )
        db.add_all([old_task, new_task])
        db.commit()

        result = AISchedulerService.prioritize_tasks([new_task, old_task], test_user.id, db)

        old_result = next(r for r in result if r["task"].id == old_task.id)
        new_result = next(r for r in result if r["task"].id == new_task.id)

        assert old_result["score_breakdown"]["momentum"] > new_result["score_breakdown"]["momentum"]

    def test_score_breakdown_calculated_correctly(self, test_user: User, db: Session):
        """Score breakdown should have all required components"""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Test Task",
            status=TaskStatus.PENDING,
            priority=5,  # high
            dueDate=datetime.utcnow() + timedelta(days=1),
            createdAt=datetime.utcnow()
        )
        db.add(task)
        db.commit()

        result = AISchedulerService.prioritize_tasks([task], test_user.id, db)

        breakdown = result[0]["score_breakdown"]
        assert "urgency" in breakdown
        assert "importance" in breakdown
        assert "dependencies" in breakdown
        assert "momentum" in breakdown


class TestSuggestSchedule:
    """Test schedule suggestion logic"""

    def test_suggest_schedule_empty_tasks(self, test_user: User, db: Session):
        """Empty task list should return empty schedule"""
        result = AISchedulerService.suggest_schedule([], test_user.id, db)

        assert result["schedule"] == []
        assert result["total_tasks"] == 0
        assert result["total_hours"] == 0

    def test_suggest_schedule_single_task(self, test_user: User, db: Session):
        """Single task should be scheduled"""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Test Task",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            estimatedMinutes=60,
            createdAt=datetime.utcnow()
        )
        db.add(task)
        db.commit()

        result = AISchedulerService.suggest_schedule([task], test_user.id, db)

        assert len(result["schedule"]) == 1
        assert result["schedule"][0]["task_id"] == task.id
        assert result["schedule"][0]["estimated_hours"] == 1.0

    def test_suggest_schedule_multiple_tasks_same_day(self, test_user: User, db: Session):
        """Multiple short tasks should fit in same day"""
        tasks = []
        for i in range(3):
            task = Task(
                id=generate_id(),
                userId=test_user.id,
                title=f"Task {i}",
                status=TaskStatus.PENDING,
                priority=3,  # medium
                estimatedMinutes=60,
                createdAt=datetime.utcnow()
            )
            tasks.append(task)
        db.add_all(tasks)
        db.commit()

        result = AISchedulerService.suggest_schedule(tasks, test_user.id, db)

        assert result["total_tasks"] == 3
        assert result["total_hours"] == 3.0
        assert result["days_required"] == 1

    def test_suggest_schedule_overflow_to_next_day(self, test_user: User, db: Session):
        """Tasks exceeding daily hours should overflow to next day"""
        tasks = []
        for i in range(3):
            task = Task(
                id=generate_id(),
                userId=test_user.id,
                title=f"Task {i}",
                status=TaskStatus.PENDING,
                priority=3,  # medium
                estimatedMinutes=240,  # 4 hours each
                createdAt=datetime.utcnow()
            )
            tasks.append(task)
        db.add_all(tasks)
        db.commit()

        # Only 8 hours available per day, 12 hours of tasks = 2 days
        result = AISchedulerService.suggest_schedule(
            tasks, test_user.id, db,
            available_hours_per_day=8
        )

        assert result["total_hours"] == 12.0
        assert result["days_required"] >= 2

    def test_suggest_schedule_custom_available_hours(self, test_user: User, db: Session):
        """Should respect custom available hours per day"""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Long Task",
            status=TaskStatus.PENDING,
            priority=3,  # medium
            estimatedMinutes=480,  # 8 hours
            createdAt=datetime.utcnow()
        )
        db.add(task)
        db.commit()

        result = AISchedulerService.suggest_schedule(
            [task], test_user.id, db,
            available_hours_per_day=4
        )

        # 8-hour task with 4 hours/day = needs overflow
        assert result["days_required"] >= 2


class TestGetFocusRecommendations:
    """Test focus recommendation logic"""

    def test_recommendations_no_time_entries(self, test_user: User, db: Session):
        """No time entries should return 'not enough data' message"""
        result = AISchedulerService.get_focus_recommendations(test_user.id, db)

        assert "Not enough data" in result["message"]
        assert result["recommendations"] == []

    def test_recommendations_with_time_entries(self, test_user: User, db: Session):
        """Time entries should generate recommendations"""
        # Create time entries with corresponding tasks
        for i in range(10):
            create_time_entry_with_task(
                db=db,
                user=test_user,
                start_time=datetime.utcnow().replace(hour=10) - timedelta(days=i),
                end_time=datetime.utcnow().replace(hour=11) - timedelta(days=i),
                duration_seconds=3600
            )
        db.commit()

        result = AISchedulerService.get_focus_recommendations(test_user.id, db)

        assert "peak_productivity_hours" in result
        assert "recommendations" in result
        assert result["total_sessions_analyzed"] == 10

    def test_recommendations_peak_productivity_hours(self, test_user: User, db: Session):
        """Should identify peak productivity hours"""
        # Create entries consistently at 10 AM with corresponding tasks
        for i in range(5):
            create_time_entry_with_task(
                db=db,
                user=test_user,
                start_time=datetime.utcnow().replace(hour=10, minute=0, second=0) - timedelta(days=i),
                end_time=datetime.utcnow().replace(hour=12, minute=0, second=0) - timedelta(days=i),
                duration_seconds=7200
            )
        db.commit()

        result = AISchedulerService.get_focus_recommendations(test_user.id, db)

        assert 10 in result["peak_productivity_hours"]

    def test_recommendations_long_sessions_break_advice(self, test_user: User, db: Session):
        """Long sessions should trigger break recommendation"""
        # Create long sessions (2+ hours each) with corresponding tasks
        for i in range(5):
            create_time_entry_with_task(
                db=db,
                user=test_user,
                start_time=datetime.utcnow() - timedelta(days=i, hours=2),
                end_time=datetime.utcnow() - timedelta(days=i),
                duration_seconds=7200  # 2 hours
            )
        db.commit()

        result = AISchedulerService.get_focus_recommendations(test_user.id, db)

        # Should recommend breaks for sessions > 90 min
        break_recs = [r for r in result["recommendations"] if r["type"] == "break_reminder"]
        assert len(break_recs) > 0


class TestDetectDistractions:
    """Test distraction detection logic"""

    def test_detect_no_entries(self, test_user: User, db: Session):
        """No entries should trigger tracking gaps alert"""
        result = AISchedulerService.detect_distractions(test_user.id, db)

        # Should have tracking_gaps alert
        tracking_alerts = [a for a in result if a["type"] == "tracking_gaps"]
        assert len(tracking_alerts) > 0

    def test_detect_short_sessions_warning(self, test_user: User, db: Session):
        """Many short sessions should trigger warning"""
        # Create 10 very short sessions with corresponding tasks
        for i in range(10):
            create_time_entry_with_task(
                db=db,
                user=test_user,
                start_time=datetime.utcnow() - timedelta(days=1, hours=i),
                end_time=datetime.utcnow() - timedelta(days=1, hours=i, minutes=-5),
                duration_seconds=300  # 5 minutes
            )
        db.commit()

        result = AISchedulerService.detect_distractions(test_user.id, db)

        short_session_alerts = [a for a in result if a["type"] == "short_sessions"]
        assert len(short_session_alerts) > 0

    def test_custom_threshold_minutes(self, test_user: User, db: Session):
        """Custom threshold should be respected"""
        # Create sessions of 20 minutes with corresponding tasks
        for i in range(10):
            create_time_entry_with_task(
                db=db,
                user=test_user,
                start_time=datetime.utcnow() - timedelta(days=1, hours=i),
                end_time=datetime.utcnow() - timedelta(days=1, hours=i, minutes=-20),
                duration_seconds=1200  # 20 minutes
            )
        db.commit()

        # With 15-minute threshold, 20-min sessions should NOT be flagged
        result = AISchedulerService.detect_distractions(
            test_user.id, db,
            threshold_minutes=15
        )

        short_session_alerts = [a for a in result if a["type"] == "short_sessions"]
        assert len(short_session_alerts) == 0

        # With 30-minute threshold, 20-min sessions SHOULD be flagged
        result = AISchedulerService.detect_distractions(
            test_user.id, db,
            threshold_minutes=30
        )

        short_session_alerts = [a for a in result if a["type"] == "short_sessions"]
        assert len(short_session_alerts) > 0


class TestHelperMethods:
    """Test helper methods"""

    def test_get_urgency_level_critical(self):
        """Score >= 70 should be critical"""
        assert AISchedulerService._get_urgency_level(70) == "critical"
        assert AISchedulerService._get_urgency_level(100) == "critical"

    def test_get_urgency_level_high(self):
        """Score 50-69 should be high"""
        assert AISchedulerService._get_urgency_level(50) == "high"
        assert AISchedulerService._get_urgency_level(69) == "high"

    def test_get_urgency_level_medium(self):
        """Score 30-49 should be medium"""
        assert AISchedulerService._get_urgency_level(30) == "medium"
        assert AISchedulerService._get_urgency_level(49) == "medium"

    def test_get_urgency_level_low(self):
        """Score < 30 should be low"""
        assert AISchedulerService._get_urgency_level(0) == "low"
        assert AISchedulerService._get_urgency_level(29) == "low"

    def test_get_recommendation_urgent(self, test_user: User, db: Session):
        """High score should give urgent recommendation"""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Test",
            status=TaskStatus.PENDING,
            createdAt=datetime.utcnow()
        )

        rec = AISchedulerService._get_recommendation(task, 75)
        assert "URGENT" in rec

    def test_get_recommendation_high(self, test_user: User, db: Session):
        """Medium-high score should give high recommendation"""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Test",
            status=TaskStatus.PENDING,
            createdAt=datetime.utcnow()
        )

        rec = AISchedulerService._get_recommendation(task, 55)
        assert "HIGH" in rec

    def test_get_recommendation_medium(self, test_user: User, db: Session):
        """Medium score should give medium recommendation"""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Test",
            status=TaskStatus.PENDING,
            createdAt=datetime.utcnow()
        )

        rec = AISchedulerService._get_recommendation(task, 35)
        assert "MEDIUM" in rec

    def test_get_recommendation_low(self, test_user: User, db: Session):
        """Low score should give low recommendation"""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Test",
            status=TaskStatus.PENDING,
            createdAt=datetime.utcnow()
        )

        rec = AISchedulerService._get_recommendation(task, 20)
        assert "LOW" in rec

    def test_get_peak_productivity_hours_no_data(self, test_user: User, db: Session):
        """No data should return default hours"""
        result = AISchedulerService._get_peak_productivity_hours(test_user.id, db)

        # Default hours are 9, 10, 14
        assert 9 in result
        assert 10 in result
        assert 14 in result

    def test_adjust_to_peak_hours_already_peak(self):
        """Time already in peak hours should not change"""
        peak_hours = [9, 10, 14]
        suggested = datetime(2025, 1, 1, 10, 0, 0)

        result = AISchedulerService._adjust_to_peak_hours(suggested, peak_hours)

        assert result.hour == 10

    def test_adjust_to_peak_hours_not_peak(self):
        """Time not in peak hours should be adjusted"""
        peak_hours = [9, 10, 14]
        suggested = datetime(2025, 1, 1, 12, 0, 0)  # Not in peak

        result = AISchedulerService._adjust_to_peak_hours(suggested, peak_hours)

        assert result.hour in peak_hours