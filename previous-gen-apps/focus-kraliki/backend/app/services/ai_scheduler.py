"""
AI-Powered Task Scheduling and Prioritization Service
Uses heuristics and simple AI to optimize task scheduling
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.task import Task, TaskStatus
from app.models.time_entry import TimeEntry


def _normalize_priority(priority_value: Any) -> str:
    """Normalize task priority to high/medium/low string."""
    if isinstance(priority_value, str):
        return priority_value.lower()
    try:
        value = int(priority_value or 0)
    except (TypeError, ValueError):
        return "low"

    if value >= 4:
        return "high"
    if value >= 2:
        return "medium"
    return "low"


class AISchedulerService:
    """
    AI-powered task scheduling and prioritization.

    Features:
    - Smart task prioritization based on deadlines, priority, and dependencies
    - Optimal time slot suggestions
    - Focus time recommendations
    - Productivity insights
    - Distraction alerts
    """

    @staticmethod
    def prioritize_tasks(
        tasks: List[Task],
        user_id: str,
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Intelligently prioritize tasks using multiple factors.

        Factors:
        - Deadline urgency (higher weight for closer deadlines)
        - User-set priority (high/medium/low)
        - Task dependencies
        - Estimated time
        - Historical completion patterns

        Returns:
            List of tasks with calculated priority scores
        """
        now = datetime.utcnow()
        task_map = {task.id: task for task in tasks if task.id}
        children_map: Dict[str, List[Task]] = {}

        for task in tasks:
            if task.parentTaskId:
                children_map.setdefault(task.parentTaskId, []).append(task)

        scored_tasks = []

        for task in tasks:
            priority_label = _normalize_priority(task.priority)
            estimated_hours = (task.estimatedMinutes or 0) / 60 if task.estimatedMinutes else None

            # Urgency score (0-1)
            urgency_score = 0.25
            if task.dueDate:
                days_until_due = (task.dueDate - now).days
                if days_until_due < 0:
                    urgency_score = 1.0
                elif days_until_due == 0:
                    urgency_score = 0.9
                elif days_until_due <= 2:
                    urgency_score = 0.8
                elif days_until_due <= 7:
                    urgency_score = 0.6
                else:
                    urgency_score = max(0.2, 1 - (days_until_due / 30))

            # Importance score (0-1) from priority + estimated impact
            priority_scale = {
                "high": 1.0,
                "medium": 0.6,
                "low": 0.3
            }
            importance_score = priority_scale.get(priority_label, 0.3)
            if task.projectId:
                importance_score = min(1.0, importance_score + 0.1)

            # Dependency score (0-1)
            dependency_context = {
                "blockedBy": None,
                "blockingTasks": [],
                "blockingCount": 0
            }
            dependency_score = 0.0

            if task.parentTaskId:
                parent = task_map.get(task.parentTaskId)
                if parent:
                    dependency_context["blockedBy"] = {
                        "id": parent.id,
                        "title": parent.title
                    }
                    dependency_score += 0.4
                    if parent.dueDate and parent.dueDate < now + timedelta(days=3):
                        dependency_score += 0.3

            children = children_map.get(task.id, [])
            if children:
                incomplete_children = [c for c in children if c.status != TaskStatus.COMPLETED]
                dependency_context["blockingCount"] = len(incomplete_children)
                dependency_context["blockingTasks"] = [
                    {"id": c.id, "title": c.title, "status": c.status.value}
                    for c in incomplete_children
                ]
                if incomplete_children:
                    dependency_score += min(0.6, len(incomplete_children) * 0.2)

            dependency_score = min(1.0, dependency_score)

            # Momentum score (0-1) to avoid stale tasks
            created_at = task.createdAt or now
            age_days = max(0, (now - created_at).days)
            momentum_score = min(1.0, age_days / 21)  # Max boost after 3 weeks
            if task.status == TaskStatus.IN_PROGRESS:
                momentum_score = min(1.0, momentum_score + 0.2)

            composite_score = (
                urgency_score * 0.4 +
                importance_score * 0.3 +
                dependency_score * 0.2 +
                momentum_score * 0.1
            )
            priority_score = round(composite_score * 100, 2)

            scored_tasks.append({
                "task": task,
                "priority_score": priority_score,
                "urgency_level": AISchedulerService._get_urgency_level(priority_score),
                "recommendation": AISchedulerService._get_recommendation(task, priority_score),
                "priority_label": priority_label,
                "estimated_hours": estimated_hours,
                "score_breakdown": {
                    "urgency": round(urgency_score * 100, 1),
                    "importance": round(importance_score * 100, 1),
                    "dependencies": round(dependency_score * 100, 1),
                    "momentum": round(momentum_score * 100, 1)
                },
                "dependency_context": dependency_context
            })

        # Sort by priority score descending
        scored_tasks.sort(key=lambda x: x["priority_score"], reverse=True)

        return scored_tasks

    @staticmethod
    def suggest_schedule(
        tasks: List[Task],
        user_id: str,
        db: Session,
        start_date: datetime = None,
        available_hours_per_day: int = 8
    ) -> Dict[str, Any]:
        """
        Generate optimal task schedule based on available time.

        Returns:
            Suggested schedule with time slots for each task
        """
        if not start_date:
            start_date = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)

        # Prioritize tasks first
        prioritized = AISchedulerService.prioritize_tasks(tasks, user_id, db)

        # Get user's productivity patterns
        peak_hours = AISchedulerService._get_peak_productivity_hours(user_id, db)

        schedule = []
        current_date = start_date
        daily_hours_used = 0

        for item in prioritized:
            task = item["task"]
            estimated_hours = item.get("estimated_hours") or ((task.estimatedMinutes or 60) / 60)
            priority_label = item.get("priority_label") or _normalize_priority(task.priority)

            # Check if task fits in current day
            if daily_hours_used + estimated_hours > available_hours_per_day:
                # Move to next day
                current_date += timedelta(days=1)
                daily_hours_used = 0

            # Suggest time slot
            suggested_start = current_date + timedelta(hours=daily_hours_used)
            suggested_end = suggested_start + timedelta(hours=estimated_hours)

            # Adjust to peak hours if possible
            if priority_label == "high" and peak_hours:
                suggested_start = AISchedulerService._adjust_to_peak_hours(
                    suggested_start,
                    peak_hours
                )
                suggested_end = suggested_start + timedelta(hours=estimated_hours)

            schedule.append({
                "task_id": task.id,
                "task_title": task.title,
                "priority": task.priority,
                "priority_label": priority_label,
                "priority_score": item["priority_score"],
                "suggested_start": suggested_start.isoformat(),
                "suggested_end": suggested_end.isoformat(),
                "estimated_hours": estimated_hours,
                "reasoning": item["recommendation"]
            })

            daily_hours_used += estimated_hours

        return {
            "schedule": schedule,
            "total_tasks": len(schedule),
            "total_hours": sum(s["estimated_hours"] for s in schedule),
            "days_required": (current_date - start_date).days + 1,
            "peak_productivity_hours": peak_hours
        }

    @staticmethod
    def get_focus_recommendations(
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Analyze user's work patterns and provide focus recommendations.

        Returns:
            - Best times to focus
            - Suggested break times
            - Productivity insights
        """
        # Analyze time entries to find patterns
        time_entries = db.query(TimeEntry).filter(
            TimeEntry.user_id == user_id,
            TimeEntry.end_time.isnot(None)
        ).order_by(TimeEntry.start_time.desc()).limit(100).all()

        if not time_entries:
            return {
                "message": "Not enough data yet. Start tracking time to get personalized recommendations!",
                "recommendations": []
            }

        # Analyze productivity by hour
        hourly_productivity = {}
        for entry in time_entries:
            hour = entry.start_time.hour
            duration = entry.duration_seconds or 0

            if hour not in hourly_productivity:
                hourly_productivity[hour] = {
                    "total_sessions": 0,
                    "total_duration": 0,
                    "avg_duration": 0
                }

            hourly_productivity[hour]["total_sessions"] += 1
            hourly_productivity[hour]["total_duration"] += duration

        # Calculate averages
        for hour, data in hourly_productivity.items():
            data["avg_duration"] = data["total_duration"] / data["total_sessions"]

        # Find peak hours
        peak_hours = sorted(
            hourly_productivity.items(),
            key=lambda x: x[1]["avg_duration"],
            reverse=True
        )[:3]

        recommendations = []

        # Recommendation 1: Best focus times
        if peak_hours:
            peak_hour_times = [f"{h[0]:02d}:00" for h in peak_hours]
            recommendations.append({
                "type": "focus_time",
                "title": "Your Peak Productivity Hours",
                "description": f"You're most productive around {', '.join(peak_hour_times)}",
                "action": "Schedule high-priority tasks during these times",
                "priority": "high"
            })

        # Recommendation 2: Break reminders
        avg_session_length = sum(e.duration_seconds for e in time_entries) / len(time_entries) / 60
        if avg_session_length > 90:
            recommendations.append({
                "type": "break_reminder",
                "title": "Take More Breaks",
                "description": f"Your average session is {int(avg_session_length)} minutes. Consider shorter focused sessions with breaks.",
                "action": "Try the Pomodoro technique (25 min work + 5 min break)",
                "priority": "medium"
            })

        # Recommendation 3: Consistency
        days_tracked = len(set(e.start_time.date() for e in time_entries))
        if days_tracked < 5:
            recommendations.append({
                "type": "consistency",
                "title": "Build a Tracking Habit",
                "description": f"You've tracked {days_tracked} days. Consistent tracking improves insights!",
                "action": "Track at least 5 days per week",
                "priority": "low"
            })

        return {
            "peak_productivity_hours": [h[0] for h in peak_hours],
            "avg_session_minutes": round(avg_session_length, 1),
            "total_sessions_analyzed": len(time_entries),
            "days_tracked": days_tracked,
            "recommendations": recommendations
        }

    @staticmethod
    def detect_distractions(
        user_id: str,
        db: Session,
        threshold_minutes: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Detect potential distraction patterns.

        Returns:
            List of detected issues
        """
        recent_entries = db.query(TimeEntry).filter(
            and_(
                TimeEntry.user_id == user_id,
                TimeEntry.start_time >= datetime.utcnow() - timedelta(days=7)
            )
        ).all()

        alerts = []

        # Check for very short sessions (possible distractions)
        short_sessions = [
            e for e in recent_entries
            if e.duration_seconds and e.duration_seconds < threshold_minutes * 60
        ]

        if len(short_sessions) > 5:
            alerts.append({
                "type": "short_sessions",
                "severity": "warning",
                "title": "Many Short Sessions Detected",
                "description": f"You have {len(short_sessions)} sessions under {threshold_minutes} minutes in the past week.",
                "suggestion": "Try longer focused work blocks. Consider using focus mode or Pomodoro timer.",
                "count": len(short_sessions)
            })

        # Check for gaps in time tracking (possible untracked work)
        if len(recent_entries) < 5:
            alerts.append({
                "type": "tracking_gaps",
                "severity": "info",
                "title": "Limited Time Tracking",
                "description": "You haven't tracked much time this week.",
                "suggestion": "Regular time tracking helps identify patterns and improve productivity.",
                "count": len(recent_entries)
            })

        return alerts

    # Helper methods
    @staticmethod
    def _get_urgency_level(score: float) -> str:
        """Convert priority score to urgency level."""
        if score >= 70:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 30:
            return "medium"
        else:
            return "low"

    @staticmethod
    def _get_recommendation(task: Task, score: float) -> str:
        """Generate recommendation text for task."""
        if score >= 70:
            return "🔴 URGENT: Complete this task immediately!"
        elif score >= 50:
            return "🟠 HIGH: Schedule this in your next available focus block"
        elif score >= 30:
            return "🟡 MEDIUM: Plan to complete this within the next few days"
        else:
            return "🟢 LOW: Complete when you have availability"

    @staticmethod
    def _get_peak_productivity_hours(user_id: str, db: Session) -> List[int]:
        """Analyze time entries to find user's most productive hours."""
        entries = db.query(TimeEntry).filter(
            TimeEntry.user_id == user_id,
            TimeEntry.end_time.isnot(None)
        ).limit(50).all()

        if not entries:
            return [9, 10, 14]  # Default peak hours

        # Count sessions by hour
        hour_counts = {}
        for entry in entries:
            hour = entry.start_time.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        # Return top 3 hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [h[0] for h in sorted_hours[:3]]

    @staticmethod
    def _adjust_to_peak_hours(
        suggested_time: datetime,
        peak_hours: List[int]
    ) -> datetime:
        """Adjust suggested time to fall within peak productivity hours."""
        if suggested_time.hour in peak_hours:
            return suggested_time

        # Find closest peak hour
        closest_peak = min(peak_hours, key=lambda h: abs(h - suggested_time.hour))

        return suggested_time.replace(hour=closest_peak, minute=0)
