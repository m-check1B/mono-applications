"""
Unit tests for Request Telemetry Service
Tests telemetry logging, routing decisions, and workflow tracking
"""

import pytest
from datetime import datetime

from app.services.request_telemetry import (
    log_enhance_input,
    update_workflow_details,
    log_orchestrate_event,
    mark_route_decision,
    record_workflow_decision,
    _merge_details,
)
from app.models.request_telemetry import (
    RequestTelemetry,
    TelemetryRoute,
    TelemetrySource,
    WorkflowDecisionStatus,
)


class TestMergeDetails:
    """Tests for _merge_details helper function"""

    def test_merge_none_existing(self):
        """Merge new data into None existing"""
        result = _merge_details(None, {"key": "value"})
        assert result == {"key": "value"}

    def test_merge_none_new(self):
        """Merge None new data returns existing"""
        existing = {"key": "value"}
        result = _merge_details(existing, None)
        assert result == existing

    def test_merge_both_none(self):
        """Merge both None returns None"""
        result = _merge_details(None, None)
        assert result is None

    def test_merge_overwrites(self):
        """New data overwrites existing keys"""
        existing = {"key1": "old", "key2": "keep"}
        new_data = {"key1": "new", "key3": "added"}
        result = _merge_details(existing, new_data)

        assert result["key1"] == "new"
        assert result["key2"] == "keep"
        assert result["key3"] == "added"

    def test_merge_preserves_original(self):
        """Merge does not modify original dict"""
        existing = {"key": "original"}
        new_data = {"key": "changed"}

        result = _merge_details(existing, new_data)

        assert existing["key"] == "original"  # Original unchanged
        assert result["key"] == "changed"  # Result has new value


class TestLogEnhanceInput:
    """Tests for log_enhance_input function"""

    def test_log_basic(self, db, test_user):
        """Log basic enhance input telemetry"""
        telemetry = log_enhance_input(
            db,
            user_id=test_user.id,
            intent="create_task",
            detected_type="task_creation",
            confidence=0.95
        )

        assert telemetry.id is not None
        assert telemetry.userId == test_user.id
        assert telemetry.source == TelemetrySource.ENHANCE_INPUT
        assert telemetry.intent == "create_task"
        assert telemetry.detectedType == "task_creation"
        assert telemetry.confidence == 0.95

    def test_log_with_details(self, db, test_user):
        """Log enhance input with details"""
        details = {"entities": ["meeting", "tomorrow"], "raw_text": "schedule meeting"}

        telemetry = log_enhance_input(
            db,
            user_id=test_user.id,
            intent="schedule_event",
            detected_type="event",
            confidence=0.88,
            details=details
        )

        assert telemetry.details == details

    def test_log_with_none_values(self, db, test_user):
        """Log enhance input with optional fields as None"""
        telemetry = log_enhance_input(
            db,
            user_id=test_user.id,
            intent=None,
            detected_type=None,
            confidence=None
        )

        assert telemetry.id is not None
        assert telemetry.intent is None
        assert telemetry.detectedType is None
        assert telemetry.confidence is None

    def test_log_sets_default_route(self, db, test_user):
        """Log enhance input has default UNKNOWN route"""
        telemetry = log_enhance_input(
            db,
            user_id=test_user.id,
            intent="test",
            detected_type="test",
            confidence=0.5
        )

        assert telemetry.route == TelemetryRoute.UNKNOWN


class TestUpdateWorkflowDetails:
    """Tests for update_workflow_details function"""

    def test_update_workflow_steps(self, db, test_user):
        """Update workflow steps on telemetry"""
        telemetry = log_enhance_input(
            db,
            user_id=test_user.id,
            intent="complex_task",
            detected_type="workflow",
            confidence=0.7
        )

        updated = update_workflow_details(
            db,
            telemetry_id=telemetry.id,
            workflow_steps=5
        )

        assert updated.workflowSteps == 5

    def test_update_with_confidence(self, db, test_user):
        """Update workflow details with new confidence"""
        telemetry = log_enhance_input(
            db,
            user_id=test_user.id,
            intent="test",
            detected_type="test",
            confidence=0.5
        )

        updated = update_workflow_details(
            db,
            telemetry_id=telemetry.id,
            workflow_steps=3,
            confidence=0.9
        )

        assert updated.confidence == 0.9

    def test_update_merges_details(self, db, test_user):
        """Update merges new details with existing"""
        telemetry = log_enhance_input(
            db,
            user_id=test_user.id,
            intent="test",
            detected_type="test",
            confidence=0.5,
            details={"existing": "data"}
        )

        updated = update_workflow_details(
            db,
            telemetry_id=telemetry.id,
            workflow_steps=2,
            details={"new": "info", "existing": "updated"}
        )

        assert updated.details["new"] == "info"
        assert updated.details["existing"] == "updated"

    def test_update_nonexistent_returns_none(self, db):
        """Update nonexistent telemetry returns None"""
        result = update_workflow_details(
            db,
            telemetry_id="nonexistent-id",
            workflow_steps=5
        )

        assert result is None


class TestLogOrchestrateEvent:
    """Tests for log_orchestrate_event function"""

    def test_log_basic(self, db, test_user):
        """Log basic orchestrate event"""
        telemetry = log_orchestrate_event(
            db,
            user_id=test_user.id,
            workflow_steps=3
        )

        assert telemetry.id is not None
        assert telemetry.userId == test_user.id
        assert telemetry.source == TelemetrySource.ORCHESTRATE_TASK
        assert telemetry.workflowSteps == 3

    def test_log_with_confidence(self, db, test_user):
        """Log orchestrate event with confidence"""
        telemetry = log_orchestrate_event(
            db,
            user_id=test_user.id,
            workflow_steps=5,
            confidence=0.85
        )

        assert telemetry.confidence == 0.85

    def test_log_with_details(self, db, test_user):
        """Log orchestrate event with details"""
        details = {
            "workflow_name": "research_task",
            "estimated_duration": "10m"
        }

        telemetry = log_orchestrate_event(
            db,
            user_id=test_user.id,
            workflow_steps=7,
            details=details
        )

        assert telemetry.details == details


class TestMarkRouteDecision:
    """Tests for mark_route_decision function"""

    def test_mark_deterministic(self, db, test_user):
        """Mark route as deterministic"""
        telemetry = log_enhance_input(
            db,
            user_id=test_user.id,
            intent="simple_task",
            detected_type="task",
            confidence=0.95
        )

        updated = mark_route_decision(
            db,
            telemetry_id=telemetry.id,
            route=TelemetryRoute.DETERMINISTIC
        )

        assert updated.route == TelemetryRoute.DETERMINISTIC

    def test_mark_orchestrated(self, db, test_user):
        """Mark route as orchestrated"""
        telemetry = log_enhance_input(
            db,
            user_id=test_user.id,
            intent="complex_task",
            detected_type="research",
            confidence=0.7
        )

        updated = mark_route_decision(
            db,
            telemetry_id=telemetry.id,
            route=TelemetryRoute.ORCHESTRATED,
            reason={"trigger": "low_confidence", "threshold": 0.8}
        )

        assert updated.route == TelemetryRoute.ORCHESTRATED
        assert updated.escalationReason["trigger"] == "low_confidence"

    def test_mark_with_reason(self, db, test_user):
        """Mark route decision with reason"""
        telemetry = log_enhance_input(
            db,
            user_id=test_user.id,
            intent="test",
            detected_type="test",
            confidence=0.5
        )

        reason = {
            "decision_factors": ["multi_step", "external_api"],
            "escalated_by": "router"
        }

        updated = mark_route_decision(
            db,
            telemetry_id=telemetry.id,
            route=TelemetryRoute.ORCHESTRATED,
            reason=reason
        )

        assert updated.escalationReason == reason

    def test_mark_nonexistent_returns_none(self, db):
        """Mark nonexistent telemetry returns None"""
        result = mark_route_decision(
            db,
            telemetry_id="nonexistent-id",
            route=TelemetryRoute.DETERMINISTIC
        )

        assert result is None


class TestRecordWorkflowDecision:
    """Tests for record_workflow_decision function"""

    def test_record_approved(self, db, test_user):
        """Record approved workflow decision"""
        telemetry = log_orchestrate_event(
            db,
            user_id=test_user.id,
            workflow_steps=3
        )

        updated = record_workflow_decision(
            db,
            telemetry_id=telemetry.id,
            status=WorkflowDecisionStatus.APPROVED
        )

        assert updated.decisionStatus == WorkflowDecisionStatus.APPROVED
        assert updated.decisionAt is not None

    def test_record_revise(self, db, test_user):
        """Record revise workflow decision"""
        telemetry = log_orchestrate_event(
            db,
            user_id=test_user.id,
            workflow_steps=5
        )

        notes = {"feedback": "Need to add step for verification"}

        updated = record_workflow_decision(
            db,
            telemetry_id=telemetry.id,
            status=WorkflowDecisionStatus.REVISE,
            notes=notes
        )

        assert updated.decisionStatus == WorkflowDecisionStatus.REVISE
        assert updated.decisionNotes == notes

    def test_record_rejected(self, db, test_user):
        """Record rejected workflow decision"""
        telemetry = log_orchestrate_event(
            db,
            user_id=test_user.id,
            workflow_steps=10
        )

        notes = {"reason": "Too complex, breaking into smaller tasks"}

        updated = record_workflow_decision(
            db,
            telemetry_id=telemetry.id,
            status=WorkflowDecisionStatus.REJECTED,
            notes=notes
        )

        assert updated.decisionStatus == WorkflowDecisionStatus.REJECTED
        assert updated.decisionNotes == notes
        assert updated.decisionAt is not None

    def test_record_nonexistent_returns_none(self, db):
        """Record decision on nonexistent telemetry returns None"""
        result = record_workflow_decision(
            db,
            telemetry_id="nonexistent-id",
            status=WorkflowDecisionStatus.APPROVED
        )

        assert result is None

    def test_decision_timestamp_set(self, db, test_user):
        """Decision timestamp is set on record"""
        before = datetime.utcnow()

        telemetry = log_orchestrate_event(
            db,
            user_id=test_user.id,
            workflow_steps=2
        )

        updated = record_workflow_decision(
            db,
            telemetry_id=telemetry.id,
            status=WorkflowDecisionStatus.APPROVED
        )

        after = datetime.utcnow()

        assert before <= updated.decisionAt <= after


class TestTelemetryIntegration:
    """Integration tests for telemetry workflow"""

    def test_full_enhance_input_workflow(self, db, test_user):
        """Test complete enhance input workflow"""
        # 1. Log initial enhance input
        telemetry = log_enhance_input(
            db,
            user_id=test_user.id,
            intent="create_task",
            detected_type="task",
            confidence=0.85,
            details={"raw": "Create a task"}
        )
        assert telemetry.route == TelemetryRoute.UNKNOWN

        # 2. Update workflow details
        telemetry = update_workflow_details(
            db,
            telemetry_id=telemetry.id,
            workflow_steps=1,
            details={"parsed": True}
        )
        assert telemetry.workflowSteps == 1

        # 3. Mark as deterministic (simple task)
        telemetry = mark_route_decision(
            db,
            telemetry_id=telemetry.id,
            route=TelemetryRoute.DETERMINISTIC
        )
        assert telemetry.route == TelemetryRoute.DETERMINISTIC

    def test_full_orchestrate_workflow(self, db, test_user):
        """Test complete orchestrate workflow"""
        # 1. Log orchestrate event
        telemetry = log_orchestrate_event(
            db,
            user_id=test_user.id,
            workflow_steps=5,
            confidence=0.7,
            details={"type": "research"}
        )

        # 2. Mark as orchestrated
        telemetry = mark_route_decision(
            db,
            telemetry_id=telemetry.id,
            route=TelemetryRoute.ORCHESTRATED,
            reason={"trigger": "multi_step_workflow"}
        )
        assert telemetry.route == TelemetryRoute.ORCHESTRATED

        # 3. Record workflow decision
        telemetry = record_workflow_decision(
            db,
            telemetry_id=telemetry.id,
            status=WorkflowDecisionStatus.APPROVED,
            notes={"reviewer": "user"}
        )
        assert telemetry.decisionStatus == WorkflowDecisionStatus.APPROVED

    def test_user_isolation(self, db, test_user):
        """Telemetry is properly scoped to user"""
        telemetry = log_enhance_input(
            db,
            user_id=test_user.id,
            intent="test",
            detected_type="test",
            confidence=0.5
        )

        assert telemetry.userId == test_user.id

        # Try to update - should work for same user's telemetry
        updated = mark_route_decision(
            db,
            telemetry_id=telemetry.id,
            route=TelemetryRoute.DETERMINISTIC
        )
        assert updated is not None
