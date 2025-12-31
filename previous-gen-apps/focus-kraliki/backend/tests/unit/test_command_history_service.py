"""
Unit tests for Command History Service
Tests command logging, status updates, history queries, and activity summaries
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from app.services.command_history import (
    log_command,
    update_command_status,
    get_command_history,
    get_unified_timeline,
    get_user_activity_summary,
)
from app.models.command_history import CommandHistory, CommandSource, CommandStatus


class TestLogCommand:
    """Tests for log_command function"""

    def test_log_command_basic(self, db, test_user):
        """Log a basic command with required fields"""
        cmd = log_command(
            db,
            user_id=test_user.id,
            source=CommandSource.ASSISTANT_TEXT,
            command="Create a task for tomorrow"
        )

        assert cmd.id is not None
        assert cmd.userId == test_user.id
        assert cmd.source == CommandSource.ASSISTANT_TEXT
        assert cmd.command == "Create a task for tomorrow"
        assert cmd.status == CommandStatus.PENDING
        assert cmd.startedAt is not None

    def test_log_command_with_intent(self, db, test_user):
        """Log command with parsed intent"""
        cmd = log_command(
            db,
            user_id=test_user.id,
            source=CommandSource.ASSISTANT_VOICE,
            command="Add meeting with John at 3pm",
            intent="create_event"
        )

        assert cmd.intent == "create_event"

    def test_log_command_with_context(self, db, test_user):
        """Log command with context data"""
        context = {
            "workspace_id": "ws-123",
            "project_id": "proj-456"
        }
        cmd = log_command(
            db,
            user_id=test_user.id,
            source=CommandSource.DETERMINISTIC_API,
            command="Update task priority",
            context=context
        )

        assert cmd.context == context

    def test_log_command_with_agent_session(self, db, test_user):
        """Log command from II-Agent with session ID"""
        cmd = log_command(
            db,
            user_id=test_user.id,
            source=CommandSource.II_AGENT,
            command="Research market trends",
            agent_session_id="session-uuid-123"
        )

        assert cmd.source == CommandSource.II_AGENT
        assert cmd.agentSessionId == "session-uuid-123"

    def test_log_command_with_model_and_confidence(self, db, test_user):
        """Log command with AI model info"""
        cmd = log_command(
            db,
            user_id=test_user.id,
            source=CommandSource.ASSISTANT_TEXT,
            command="Summarize my tasks",
            model="claude-3-sonnet",
            confidence=0.95
        )

        assert cmd.model == "claude-3-sonnet"
        assert cmd.confidence == 0.95

    def test_log_command_with_metadata(self, db, test_user):
        """Log command with additional metadata"""
        metadata = {"version": "1.0", "client": "web"}
        cmd = log_command(
            db,
            user_id=test_user.id,
            source=CommandSource.DIRECT_API,
            command="GET /api/tasks",
            metadata=metadata
        )

        assert cmd.id is not None
        assert cmd.command == "GET /api/tasks"
        assert cmd.command_metadata == metadata

    def test_log_command_all_sources(self, db, test_user):
        """Test all command sources can be logged"""
        sources = [
            CommandSource.ASSISTANT_VOICE,
            CommandSource.ASSISTANT_TEXT,
            CommandSource.DETERMINISTIC_API,
            CommandSource.II_AGENT,
            CommandSource.WORKFLOW,
            CommandSource.DIRECT_API,
        ]

        for source in sources:
            cmd = log_command(
                db,
                user_id=test_user.id,
                source=source,
                command=f"Test command for {source.value}"
            )
            assert cmd.source == source


class TestUpdateCommandStatus:
    """Tests for update_command_status function"""

    def test_update_to_in_progress(self, db, test_user):
        """Update command to in_progress"""
        cmd = log_command(
            db,
            user_id=test_user.id,
            source=CommandSource.ASSISTANT_TEXT,
            command="Test command"
        )

        updated = update_command_status(
            db,
            command_id=cmd.id,
            status=CommandStatus.IN_PROGRESS
        )

        assert updated.status == CommandStatus.IN_PROGRESS
        assert updated.completedAt is None

    def test_update_to_completed(self, db, test_user):
        """Update command to completed sets completedAt and duration"""
        cmd = log_command(
            db,
            user_id=test_user.id,
            source=CommandSource.ASSISTANT_TEXT,
            command="Test command"
        )

        result = {"task_id": "task-123", "created": True}
        updated = update_command_status(
            db,
            command_id=cmd.id,
            status=CommandStatus.COMPLETED,
            result=result
        )

        assert updated.status == CommandStatus.COMPLETED
        assert updated.completedAt is not None
        assert updated.durationMs is not None
        assert updated.result == result

    def test_update_to_failed(self, db, test_user):
        """Update command to failed with error details"""
        cmd = log_command(
            db,
            user_id=test_user.id,
            source=CommandSource.ASSISTANT_TEXT,
            command="Test command"
        )

        error = {"code": "VALIDATION_ERROR", "message": "Invalid date format"}
        updated = update_command_status(
            db,
            command_id=cmd.id,
            status=CommandStatus.FAILED,
            error=error
        )

        assert updated.status == CommandStatus.FAILED
        assert updated.completedAt is not None
        assert updated.error == error

    def test_update_to_cancelled(self, db, test_user):
        """Update command to cancelled"""
        cmd = log_command(
            db,
            user_id=test_user.id,
            source=CommandSource.II_AGENT,
            command="Long running task"
        )

        updated = update_command_status(
            db,
            command_id=cmd.id,
            status=CommandStatus.CANCELLED
        )

        assert updated.status == CommandStatus.CANCELLED
        assert updated.completedAt is not None

    def test_update_nonexistent_command(self, db):
        """Update returns None for nonexistent command"""
        result = update_command_status(
            db,
            command_id="nonexistent-id",
            status=CommandStatus.COMPLETED
        )

        assert result is None


class TestGetCommandHistory:
    """Tests for get_command_history function"""

    def test_get_history_basic(self, db, test_user):
        """Get command history for user"""
        # Create commands
        for i in range(3):
            log_command(
                db,
                user_id=test_user.id,
                source=CommandSource.ASSISTANT_TEXT,
                command=f"Command {i}"
            )

        commands, total = get_command_history(db, user_id=test_user.id)

        assert total == 3
        assert len(commands) == 3

    def test_get_history_filter_by_source(self, db, test_user):
        """Filter history by source"""
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Text cmd")
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_VOICE, command="Voice cmd")
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Text cmd 2")

        commands, total = get_command_history(
            db,
            user_id=test_user.id,
            source=CommandSource.ASSISTANT_TEXT
        )

        assert total == 2
        assert all(cmd.source == CommandSource.ASSISTANT_TEXT for cmd in commands)

    def test_get_history_filter_by_intent(self, db, test_user):
        """Filter history by intent"""
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Create task", intent="create_task")
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="List tasks", intent="list_tasks")
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="New task", intent="create_task")

        commands, total = get_command_history(
            db,
            user_id=test_user.id,
            intent="create_task"
        )

        assert total == 2

    def test_get_history_filter_by_status(self, db, test_user):
        """Filter history by status"""
        cmd1 = log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Cmd 1")
        cmd2 = log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Cmd 2")
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Cmd 3")

        update_command_status(db, command_id=cmd1.id, status=CommandStatus.COMPLETED)
        update_command_status(db, command_id=cmd2.id, status=CommandStatus.COMPLETED)

        commands, total = get_command_history(
            db,
            user_id=test_user.id,
            status=CommandStatus.COMPLETED
        )

        assert total == 2

    def test_get_history_date_filters(self, db, test_user):
        """Filter history by date range"""
        now = datetime.utcnow()

        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Recent")

        commands, total = get_command_history(
            db,
            user_id=test_user.id,
            since=now - timedelta(hours=1),
            until=now + timedelta(hours=1)
        )

        assert total >= 1

    def test_get_history_pagination(self, db, test_user):
        """Test pagination with limit and offset"""
        for i in range(10):
            log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command=f"Cmd {i}")

        commands, total = get_command_history(
            db,
            user_id=test_user.id,
            limit=3,
            offset=0
        )

        assert total == 10
        assert len(commands) == 3

    def test_get_history_user_isolation(self, db, test_user):
        """Commands from other users are not returned"""
        # Create command for test_user
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="My command")

        # Query for a different user
        commands, total = get_command_history(db, user_id="other-user-id")

        assert total == 0


class TestGetUnifiedTimeline:
    """Tests for get_unified_timeline function"""

    def test_get_timeline_basic(self, db, test_user):
        """Get basic unified timeline"""
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Test")

        timeline = get_unified_timeline(db, user_id=test_user.id)

        assert len(timeline) >= 1
        assert timeline[0]["type"] == "command"

    def test_get_timeline_with_date_range(self, db, test_user):
        """Get timeline with specific date range"""
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Test")

        now = datetime.utcnow()
        timeline = get_unified_timeline(
            db,
            user_id=test_user.id,
            since=now - timedelta(days=1),
            until=now + timedelta(days=1)
        )

        assert len(timeline) >= 1

    def test_get_timeline_filter_sources(self, db, test_user):
        """Filter timeline by command sources"""
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Text")
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_VOICE, command="Voice")

        timeline = get_unified_timeline(
            db,
            user_id=test_user.id,
            sources=[CommandSource.ASSISTANT_TEXT]
        )

        # Should only include text commands
        command_entries = [e for e in timeline if e["type"] == "command"]
        assert all(e["source"] == "assistant_text" for e in command_entries)

    def test_get_timeline_without_telemetry(self, db, test_user):
        """Get timeline excluding telemetry"""
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Test")

        timeline = get_unified_timeline(
            db,
            user_id=test_user.id,
            include_telemetry=False
        )

        # All entries should be commands, not telemetry
        assert all(e["type"] == "command" for e in timeline)

    def test_get_timeline_entry_structure(self, db, test_user):
        """Verify timeline entry has expected fields"""
        cmd = log_command(
            db,
            user_id=test_user.id,
            source=CommandSource.ASSISTANT_TEXT,
            command="Test command",
            intent="test_intent",
            model="claude-3",
            confidence=0.9
        )
        update_command_status(
            db,
            command_id=cmd.id,
            status=CommandStatus.COMPLETED,
            result={"success": True}
        )

        timeline = get_unified_timeline(db, user_id=test_user.id, include_telemetry=False)
        entry = next((e for e in timeline if e["id"] == cmd.id), None)

        assert entry is not None
        assert entry["type"] == "command"
        assert entry["source"] == "assistant_text"
        assert entry["command"] == "Test command"
        assert entry["intent"] == "test_intent"
        assert entry["model"] == "claude-3"
        assert entry["confidence"] == 0.9
        assert entry["status"] == "completed"
        assert entry["result"] == {"success": True}


class TestGetUserActivitySummary:
    """Tests for get_user_activity_summary function"""

    def test_get_summary_basic(self, db, test_user):
        """Get basic activity summary"""
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Test")

        summary = get_user_activity_summary(db, user_id=test_user.id)

        assert "total_commands" in summary
        assert "completed" in summary
        assert "failed" in summary
        assert "in_progress" in summary
        assert "success_rate" in summary
        assert "by_source" in summary
        assert "by_intent" in summary
        assert "period" in summary

    def test_get_summary_counts(self, db, test_user):
        """Verify command counts in summary"""
        cmd1 = log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Cmd 1")
        cmd2 = log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Cmd 2")
        cmd3 = log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Cmd 3")

        update_command_status(db, command_id=cmd1.id, status=CommandStatus.COMPLETED)
        update_command_status(db, command_id=cmd2.id, status=CommandStatus.FAILED)
        # cmd3 stays pending

        summary = get_user_activity_summary(db, user_id=test_user.id)

        assert summary["total_commands"] == 3
        assert summary["completed"] == 1
        assert summary["failed"] == 1

    def test_get_summary_success_rate(self, db, test_user):
        """Verify success rate calculation"""
        cmd1 = log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Cmd 1")
        cmd2 = log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Cmd 2")

        update_command_status(db, command_id=cmd1.id, status=CommandStatus.COMPLETED)
        update_command_status(db, command_id=cmd2.id, status=CommandStatus.COMPLETED)

        summary = get_user_activity_summary(db, user_id=test_user.id)

        assert summary["success_rate"] == 100.0

    def test_get_summary_by_source(self, db, test_user):
        """Verify counts by source"""
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Text 1")
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Text 2")
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_VOICE, command="Voice")

        summary = get_user_activity_summary(db, user_id=test_user.id)

        assert summary["by_source"]["assistant_text"] == 2
        assert summary["by_source"]["assistant_voice"] == 1

    def test_get_summary_by_intent(self, db, test_user):
        """Verify counts by intent"""
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Create", intent="create_task")
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="List", intent="list_tasks")
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Create 2", intent="create_task")

        summary = get_user_activity_summary(db, user_id=test_user.id)

        assert summary["by_intent"]["create_task"] == 2
        assert summary["by_intent"]["list_tasks"] == 1

    def test_get_summary_with_date_range(self, db, test_user):
        """Summary respects date range"""
        now = datetime.utcnow()
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Recent")

        summary = get_user_activity_summary(
            db,
            user_id=test_user.id,
            since=now - timedelta(hours=1),
            until=now + timedelta(hours=1)
        )

        assert summary["total_commands"] >= 1
        assert "since" in summary["period"]
        assert "until" in summary["period"]

    def test_get_summary_empty(self, db, test_user):
        """Summary for user with no commands"""
        summary = get_user_activity_summary(db, user_id="nonexistent-user")

        assert summary["total_commands"] == 0
        assert summary["success_rate"] == 0
        assert summary["by_source"] == {}
        assert summary["by_intent"] == {}

    def test_get_summary_avg_duration(self, db, test_user):
        """Verify average duration calculation"""
        cmd1 = log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Cmd 1")
        cmd2 = log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="Cmd 2")

        update_command_status(db, command_id=cmd1.id, status=CommandStatus.COMPLETED)
        update_command_status(db, command_id=cmd2.id, status=CommandStatus.COMPLETED)

        summary = get_user_activity_summary(db, user_id=test_user.id)

        # avg_duration_ms should be set since we have completed commands
        assert summary["avg_duration_ms"] is not None


class TestCommandHistoryIntegration:
    """Integration tests for command history workflows"""

    def test_full_command_lifecycle(self, db, test_user):
        """Test complete command lifecycle: log -> update -> query"""
        # Log command
        cmd = log_command(
            db,
            user_id=test_user.id,
            source=CommandSource.ASSISTANT_TEXT,
            command="Create a task for meeting prep",
            intent="create_task"
        )
        assert cmd.status == CommandStatus.PENDING

        # Update to in_progress
        update_command_status(db, command_id=cmd.id, status=CommandStatus.IN_PROGRESS)

        # Complete with result
        update_command_status(
            db,
            command_id=cmd.id,
            status=CommandStatus.COMPLETED,
            result={"task_id": "task-123"}
        )

        # Query and verify
        commands, _ = get_command_history(db, user_id=test_user.id)
        completed_cmd = next((c for c in commands if c.id == cmd.id), None)

        assert completed_cmd.status == CommandStatus.COMPLETED
        assert completed_cmd.result == {"task_id": "task-123"}
        assert completed_cmd.durationMs is not None

    def test_multiple_users_isolation(self, db, test_user):
        """Commands are properly isolated between users"""
        # Log for test_user
        log_command(db, user_id=test_user.id, source=CommandSource.ASSISTANT_TEXT, command="User 1 cmd")

        # Get history for test_user (uses working function)
        commands1, total1 = get_command_history(db, user_id=test_user.id)

        # Get history for other user
        commands2, total2 = get_command_history(db, user_id="other-user-id")

        assert total1 >= 1
        assert total2 == 0
