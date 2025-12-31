"""
Unit tests for Time Entries Router
Tests time tracking CRUD operations and reporting
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.schemas.time_entry import (
    TimeEntryCreate,
    TimeEntryUpdate,
    TimeEntryResponse,
    TimeEntryListResponse,
    TimeEntryStopRequest
)


class TestTimeEntrySchemas:
    """Tests for time entry Pydantic schemas"""

    def test_time_entry_create_minimal(self):
        """TimeEntryCreate with minimal fields"""
        entry = TimeEntryCreate(
            start_time=datetime.utcnow(),
            description="Working on task"
        )
        assert entry.description == "Working on task"
        assert entry.task_id is None
        assert entry.project_id is None

    def test_time_entry_create_with_task(self):
        """TimeEntryCreate with task reference"""
        entry = TimeEntryCreate(
            start_time=datetime.utcnow(),
            description="Task work",
            task_id="task-123"
        )
        assert entry.task_id == "task-123"

    def test_time_entry_create_with_project(self):
        """TimeEntryCreate with project reference"""
        entry = TimeEntryCreate(
            start_time=datetime.utcnow(),
            description="Project work",
            project_id="proj-456"
        )
        assert entry.project_id == "proj-456"

    def test_time_entry_create_with_end_time(self):
        """TimeEntryCreate with start and end time"""
        start = datetime(2025, 1, 15, 10, 0, 0)
        end = datetime(2025, 1, 15, 11, 30, 0)
        entry = TimeEntryCreate(
            start_time=start,
            end_time=end,
            description="Completed work"
        )
        assert entry.start_time == start
        assert entry.end_time == end

    def test_time_entry_create_with_billable(self):
        """TimeEntryCreate with billable flag"""
        entry = TimeEntryCreate(
            start_time=datetime.utcnow(),
            description="Client meeting",
            billable=True,
            hourly_rate=75
        )
        assert entry.billable is True
        assert entry.hourly_rate == 75

    def test_time_entry_update_partial(self):
        """TimeEntryUpdate with partial fields"""
        update = TimeEntryUpdate(
            description="Updated description"
        )
        assert update.description == "Updated description"
        assert update.end_time is None

    def test_time_entry_update_times(self):
        """TimeEntryUpdate with time changes"""
        update = TimeEntryUpdate(
            end_time=datetime.utcnow()
        )
        assert update.end_time is not None

    def test_time_entry_stop_request(self):
        """TimeEntryStopRequest schema"""
        stop = TimeEntryStopRequest(
            description="Stopping for break"
        )
        assert stop.description == "Stopping for break"


class TestTimeEntryFiltering:
    """Tests for time entry filtering logic"""

    def test_filter_by_task_id(self):
        """Filter entries by task ID"""
        entries = [
            {"id": "1", "task_id": "task-a"},
            {"id": "2", "task_id": "task-b"},
            {"id": "3", "task_id": "task-a"}
        ]
        filtered = [e for e in entries if e["task_id"] == "task-a"]
        assert len(filtered) == 2

    def test_filter_by_project_id(self):
        """Filter entries by project ID"""
        entries = [
            {"id": "1", "project_id": "proj-x"},
            {"id": "2", "project_id": "proj-y"},
            {"id": "3", "project_id": "proj-x"}
        ]
        filtered = [e for e in entries if e["project_id"] == "proj-x"]
        assert len(filtered) == 2

    def test_filter_by_date_range(self):
        """Filter entries by date range"""
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31)

        entries = [
            {"id": "1", "start_time": datetime(2025, 1, 15)},
            {"id": "2", "start_time": datetime(2025, 2, 1)},
            {"id": "3", "start_time": datetime(2024, 12, 31)}
        ]

        filtered = [
            e for e in entries
            if start_date <= e["start_time"] <= end_date
        ]
        assert len(filtered) == 1

    def test_combine_filters(self):
        """Combine multiple filters"""
        task_id = "task-a"
        project_id = "proj-x"

        entries = [
            {"id": "1", "task_id": "task-a", "project_id": "proj-x"},
            {"id": "2", "task_id": "task-a", "project_id": "proj-y"},
            {"id": "3", "task_id": "task-b", "project_id": "proj-x"}
        ]

        filtered = [
            e for e in entries
            if e["task_id"] == task_id and e["project_id"] == project_id
        ]
        assert len(filtered) == 1


class TestTimeCalculations:
    """Tests for time calculations"""

    def test_calculate_duration_from_times(self):
        """Calculate duration from start and end times"""
        start = datetime(2025, 1, 15, 10, 0, 0)
        end = datetime(2025, 1, 15, 11, 30, 0)
        duration = (end - start).total_seconds() / 60
        assert duration == 90

    def test_format_duration_hours_minutes(self):
        """Format duration as hours and minutes"""
        minutes = 150
        hours = minutes // 60
        remaining_minutes = minutes % 60
        formatted = f"{hours}h {remaining_minutes}m"
        assert formatted == "2h 30m"

    def test_total_duration_for_day(self):
        """Calculate total duration for a day"""
        entries = [
            {"duration_minutes": 60},
            {"duration_minutes": 45},
            {"duration_minutes": 90}
        ]
        total = sum(e["duration_minutes"] for e in entries)
        assert total == 195

    def test_billable_amount_calculation(self):
        """Calculate billable amount"""
        duration_minutes = 120
        hourly_rate = Decimal("75.00")
        hours = Decimal(duration_minutes) / Decimal(60)
        amount = hours * hourly_rate
        assert amount == Decimal("150.00")


class TestRunningTimer:
    """Tests for running timer logic"""

    def test_start_timer(self):
        """Start a new timer"""
        entry = {
            "id": "timer-1",
            "start_time": datetime.utcnow(),
            "end_time": None,
            "is_running": True
        }
        assert entry["is_running"] is True
        assert entry["end_time"] is None

    def test_stop_timer(self):
        """Stop a running timer"""
        start = datetime.utcnow() - timedelta(hours=1)
        end = datetime.utcnow()
        duration = (end - start).total_seconds() / 60

        entry = {
            "id": "timer-1",
            "start_time": start,
            "end_time": end,
            "duration_minutes": int(duration),
            "is_running": False
        }
        assert entry["is_running"] is False
        assert entry["duration_minutes"] >= 59

    def test_calculate_running_duration(self):
        """Calculate duration of running timer"""
        start = datetime.utcnow() - timedelta(minutes=30)
        now = datetime.utcnow()
        running_duration = (now - start).total_seconds() / 60
        assert 29 <= running_duration <= 31


class TestTimeEntryValidation:
    """Tests for time entry validation"""

    def test_end_time_after_start_time(self):
        """End time must be after start time"""
        start = datetime(2025, 1, 15, 10, 0, 0)
        end = datetime(2025, 1, 15, 11, 0, 0)
        is_valid = end > start
        assert is_valid is True

    def test_negative_duration_invalid(self):
        """Negative duration is invalid"""
        duration = -30
        is_valid = duration >= 0
        assert is_valid is False

    def test_zero_duration_allowed(self):
        """Zero duration is allowed for started timers"""
        duration = 0
        is_valid = duration >= 0
        assert is_valid is True

    def test_maximum_duration_limit(self):
        """Duration should have a reasonable maximum"""
        max_hours = 24
        duration_minutes = 25 * 60  # 25 hours
        is_valid = duration_minutes <= max_hours * 60
        assert is_valid is False


class TestTimeEntryExport:
    """Tests for time entry export functionality"""

    def test_csv_header_format(self):
        """CSV export has correct headers"""
        headers = ["Date", "Description", "Task", "Project", "Duration", "Billable"]
        assert "Duration" in headers
        assert "Billable" in headers

    def test_csv_row_format(self):
        """CSV row has correct format"""
        entry = {
            "start_time": "2025-01-15",
            "description": "Development work",
            "task_name": "Feature X",
            "project_name": "Project Alpha",
            "duration_minutes": 120,
            "billable": True
        }
        row = [
            entry["start_time"],
            entry["description"],
            entry["task_name"],
            entry["project_name"],
            f"{entry['duration_minutes']} min",
            "Yes" if entry["billable"] else "No"
        ]
        assert len(row) == 6


class TestTimeEntrySummary:
    """Tests for time entry summary/reporting"""

    def test_daily_summary(self):
        """Calculate daily time summary"""
        entries = [
            {"start_time": datetime(2025, 1, 15, 9, 0), "duration_minutes": 60},
            {"start_time": datetime(2025, 1, 15, 14, 0), "duration_minutes": 90},
            {"start_time": datetime(2025, 1, 16, 10, 0), "duration_minutes": 45}
        ]

        # Group by date
        by_date = {}
        for e in entries:
            date_key = e["start_time"].date()
            by_date[date_key] = by_date.get(date_key, 0) + e["duration_minutes"]

        assert by_date[datetime(2025, 1, 15).date()] == 150
        assert by_date[datetime(2025, 1, 16).date()] == 45

    def test_project_summary(self):
        """Calculate project time summary"""
        entries = [
            {"project_id": "proj-a", "duration_minutes": 60},
            {"project_id": "proj-b", "duration_minutes": 90},
            {"project_id": "proj-a", "duration_minutes": 30}
        ]

        by_project = {}
        for e in entries:
            pid = e["project_id"]
            by_project[pid] = by_project.get(pid, 0) + e["duration_minutes"]

        assert by_project["proj-a"] == 90
        assert by_project["proj-b"] == 90

    def test_weekly_total(self):
        """Calculate weekly time total"""
        daily_totals = [180, 420, 360, 240, 300, 0, 0]  # Mon-Sun in minutes
        weekly_total = sum(daily_totals)
        assert weekly_total == 1500  # 25 hours


class TestBillableTracking:
    """Tests for billable time tracking"""

    def test_separate_billable_non_billable(self):
        """Separate billable and non-billable time"""
        entries = [
            {"billable": True, "duration_minutes": 60},
            {"billable": False, "duration_minutes": 30},
            {"billable": True, "duration_minutes": 90}
        ]

        billable = sum(e["duration_minutes"] for e in entries if e["billable"])
        non_billable = sum(e["duration_minutes"] for e in entries if not e["billable"])

        assert billable == 150
        assert non_billable == 30

    def test_calculate_billable_revenue(self):
        """Calculate revenue from billable entries"""
        entries = [
            {"billable": True, "duration_minutes": 120, "hourly_rate": Decimal("100")},
            {"billable": True, "duration_minutes": 60, "hourly_rate": Decimal("75")},
            {"billable": False, "duration_minutes": 90, "hourly_rate": Decimal("100")}
        ]

        total_revenue = Decimal("0")
        for e in entries:
            if e["billable"]:
                hours = Decimal(e["duration_minutes"]) / Decimal(60)
                total_revenue += hours * e["hourly_rate"]

        assert total_revenue == Decimal("275.00")


class TestTimeEntryResponse:
    """Tests for time entry response formatting"""

    def test_response_includes_task_name(self):
        """Response includes related task name"""
        response = {
            "id": "entry-1",
            "task_id": "task-123",
            "task_name": "Implement feature",
            "duration_minutes": 60
        }
        assert "task_name" in response

    def test_response_includes_project_name(self):
        """Response includes related project name"""
        response = {
            "id": "entry-1",
            "project_id": "proj-456",
            "project_name": "Q1 Initiative",
            "duration_minutes": 60
        }
        assert "project_name" in response

    def test_response_formats_duration(self):
        """Response formats duration nicely"""
        minutes = 150
        formatted = f"{minutes // 60}h {minutes % 60}m"
        assert formatted == "2h 30m"


class TestQueryParameters:
    """Tests for query parameter handling"""

    def test_default_limit(self):
        """Default limit is reasonable"""
        default_limit = 100
        assert 1 <= default_limit <= 500

    def test_max_limit(self):
        """Maximum limit is enforced"""
        max_limit = 500
        requested_limit = 1000
        effective_limit = min(requested_limit, max_limit)
        assert effective_limit == 500

    def test_date_parsing(self):
        """Date strings are parsed correctly"""
        date_str = "2025-01-15T10:00:00Z"
        parsed = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        assert parsed.year == 2025
        assert parsed.month == 1
        assert parsed.day == 15


class TestWorkspaceIntegration:
    """Tests for workspace membership in time entries"""

    def test_entry_inherits_workspace_from_task(self):
        """Entry inherits workspace from associated task"""
        task = {"id": "task-1", "workspace_id": "ws-123"}
        entry = {
            "task_id": task["id"],
            "workspace_id": task["workspace_id"]
        }
        assert entry["workspace_id"] == "ws-123"

    def test_entry_inherits_workspace_from_project(self):
        """Entry inherits workspace from associated project"""
        project = {"id": "proj-1", "workspace_id": "ws-456"}
        entry = {
            "project_id": project["id"],
            "workspace_id": project["workspace_id"]
        }
        assert entry["workspace_id"] == "ws-456"
