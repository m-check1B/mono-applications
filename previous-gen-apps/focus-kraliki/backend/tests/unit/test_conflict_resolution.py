"""
Unit tests for Conflict Resolution Module
Tests conflict detection, resolution policies, and merge strategies
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from app.core.conflict_resolution import (
    ConflictResolver,
    ConflictResolutionPolicy,
    ConflictType,
    SyncConflict
)


class TestConflictResolutionPolicy:
    """Tests for ConflictResolutionPolicy enum"""

    def test_policy_values(self):
        """All policies have valid values"""
        assert ConflictResolutionPolicy.LAST_MODIFIED_WINS.value == "last_modified_wins"
        assert ConflictResolutionPolicy.SOURCE_WINS.value == "source_wins"
        assert ConflictResolutionPolicy.DESTINATION_WINS.value == "destination_wins"
        assert ConflictResolutionPolicy.MANUAL_APPROVAL.value == "manual_approval"
        assert ConflictResolutionPolicy.MERGE_FIELDS.value == "merge_fields"

    def test_policy_from_string(self):
        """Policies can be created from strings"""
        assert ConflictResolutionPolicy("last_modified_wins") == ConflictResolutionPolicy.LAST_MODIFIED_WINS
        assert ConflictResolutionPolicy("source_wins") == ConflictResolutionPolicy.SOURCE_WINS
        assert ConflictResolutionPolicy("destination_wins") == ConflictResolutionPolicy.DESTINATION_WINS
        assert ConflictResolutionPolicy("manual_approval") == ConflictResolutionPolicy.MANUAL_APPROVAL
        assert ConflictResolutionPolicy("merge_fields") == ConflictResolutionPolicy.MERGE_FIELDS

    def test_invalid_policy_raises(self):
        """Invalid policy string raises ValueError"""
        with pytest.raises(ValueError):
            ConflictResolutionPolicy("invalid_policy")


class TestConflictType:
    """Tests for ConflictType enum"""

    def test_conflict_types(self):
        """All conflict types exist"""
        assert ConflictType.OVERLAPPING_EDIT
        assert ConflictType.DELETE_CONFLICT
        assert ConflictType.DUPLICATE_ENTRY
        assert ConflictType.FIELD_MISMATCH


class TestSyncConflict:
    """Tests for SyncConflict dataclass"""

    def test_create_conflict(self):
        """Create SyncConflict with required fields"""
        conflict = SyncConflict(
            conflict_type=ConflictType.FIELD_MISMATCH,
            focus_item={"id": "f1", "title": "Focus Title"},
            calendar_item={"id": "c1", "summary": "Calendar Title"}
        )

        assert conflict.conflict_type == ConflictType.FIELD_MISMATCH
        assert conflict.focus_item["id"] == "f1"
        assert conflict.calendar_item["id"] == "c1"
        assert conflict.detected_at is not None

    def test_conflict_with_field_diffs(self):
        """Create conflict with field-level diffs"""
        conflict = SyncConflict(
            conflict_type=ConflictType.OVERLAPPING_EDIT,
            focus_item={"id": "f1"},
            calendar_item={"id": "c1"},
            field_diffs=["title", "description"]
        )

        assert "title" in conflict.field_diffs
        assert "description" in conflict.field_diffs

    def test_conflict_to_dict(self):
        """Convert conflict to dict for serialization"""
        conflict = SyncConflict(
            conflict_type=ConflictType.FIELD_MISMATCH,
            focus_item={"id": "f1"},
            calendar_item={"id": "c1"},
            field_diffs=["title"]
        )

        result = conflict.to_dict()
        assert result["conflict_type"] == "field_mismatch"
        assert result["focus_item"] == {"id": "f1"}
        assert result["calendar_item"] == {"id": "c1"}
        assert "detected_at" in result


class TestConflictResolver:
    """Tests for ConflictResolver class"""

    def test_init_default_policy(self):
        """Default policy is last_modified_wins"""
        resolver = ConflictResolver()
        assert resolver.policy == ConflictResolutionPolicy.LAST_MODIFIED_WINS

    def test_init_custom_policy(self):
        """Custom policy is set correctly"""
        resolver = ConflictResolver(policy=ConflictResolutionPolicy.SOURCE_WINS)
        assert resolver.policy == ConflictResolutionPolicy.SOURCE_WINS

    def test_detect_conflicts_no_changes(self):
        """No conflict when items were not modified since last sync"""
        resolver = ConflictResolver()

        now = datetime.utcnow()
        # Both items were modified BEFORE the last sync (so no changes since sync)
        focus_item = {
            "id": "f1",
            "title": "Test Task",
            "description": "Description",
            "dueDate": now,
            "updatedAt": now - timedelta(hours=3)  # Modified 3 hours ago
        }

        calendar_item = {
            "id": "c1",
            "summary": "Test Task",
            "description": "Description",
            "start": {"dateTime": focus_item["dueDate"].isoformat()},
            "updated": (now - timedelta(hours=3)).isoformat()  # Also modified 3 hours ago
        }

        # Last sync was 2 hours ago, so both items were modified BEFORE last sync
        conflict = resolver.detect_conflicts(
            focus_item=focus_item,
            calendar_item=calendar_item,
            last_sync_time=now - timedelta(hours=2)  # Sync happened 2 hours ago
        )

        # No OVERLAPPING_EDIT conflict expected since neither was modified after last sync
        # But may still have FIELD_MISMATCH if fields differ (which they don't here)
        assert conflict is None or conflict.conflict_type == ConflictType.FIELD_MISMATCH

    def test_detect_conflicts_title_changed(self):
        """Detect title change conflict"""
        resolver = ConflictResolver()

        now = datetime.utcnow()
        focus_item = {
            "id": "f1",
            "title": "Updated Focus Title",
            "description": "Same description",
            "updatedAt": now
        }

        calendar_item = {
            "id": "c1",
            "summary": "Original Calendar Title",
            "description": "Same description",
            "updated": (now - timedelta(minutes=5)).isoformat()
        }

        conflict = resolver.detect_conflicts(
            focus_item=focus_item,
            calendar_item=calendar_item,
            last_sync_time=now - timedelta(hours=1)
        )

        assert conflict is not None
        assert conflict.conflict_type in [ConflictType.OVERLAPPING_EDIT, ConflictType.FIELD_MISMATCH]

    def test_detect_conflicts_both_modified(self):
        """Detect when both items modified since last sync"""
        resolver = ConflictResolver()

        last_sync = datetime.utcnow() - timedelta(hours=1)

        focus_item = {
            "id": "f1",
            "title": "Focus Modified",
            "description": "Focus desc",
            "updatedAt": datetime.utcnow() - timedelta(minutes=30)
        }

        calendar_item = {
            "id": "c1",
            "summary": "Calendar Modified",
            "description": "Calendar desc",
            "updated": (datetime.utcnow() - timedelta(minutes=15)).isoformat()
        }

        conflict = resolver.detect_conflicts(
            focus_item=focus_item,
            calendar_item=calendar_item,
            last_sync_time=last_sync
        )

        assert conflict is not None
        assert conflict.conflict_type == ConflictType.OVERLAPPING_EDIT

    def test_resolve_conflict_last_modified_wins_focus(self):
        """Last modified wins - Focus is newer"""
        resolver = ConflictResolver(policy=ConflictResolutionPolicy.LAST_MODIFIED_WINS)

        now = datetime.utcnow()
        conflict = SyncConflict(
            conflict_type=ConflictType.FIELD_MISMATCH,
            focus_item={"title": "Focus Title", "updatedAt": now},  # Newer
            calendar_item={"summary": "Calendar Title", "updated": (now - timedelta(minutes=10)).isoformat()}
        )

        winning_side, resolved_data = resolver.resolve_conflict(conflict)

        assert winning_side == "focus"

    def test_resolve_conflict_last_modified_wins_calendar(self):
        """Last modified wins - Calendar is newer"""
        resolver = ConflictResolver(policy=ConflictResolutionPolicy.LAST_MODIFIED_WINS)

        now = datetime.utcnow()
        conflict = SyncConflict(
            conflict_type=ConflictType.FIELD_MISMATCH,
            focus_item={"title": "Focus Title", "updatedAt": (now - timedelta(minutes=10))},
            calendar_item={"summary": "Calendar Title", "updated": now.isoformat()}  # Newer
        )

        winning_side, resolved_data = resolver.resolve_conflict(conflict)

        assert winning_side == "calendar"

    def test_resolve_conflict_source_wins(self):
        """Source (Calendar) always wins regardless of time"""
        resolver = ConflictResolver(policy=ConflictResolutionPolicy.SOURCE_WINS)

        now = datetime.utcnow()
        conflict = SyncConflict(
            conflict_type=ConflictType.FIELD_MISMATCH,
            focus_item={"title": "Focus Title", "updatedAt": now},  # Even though Focus is newer
            calendar_item={"summary": "Calendar Title", "updated": (now - timedelta(hours=1)).isoformat()}
        )

        winning_side, resolved_data = resolver.resolve_conflict(conflict)

        assert winning_side == "calendar"

    def test_resolve_conflict_destination_wins(self):
        """Destination (Focus) always wins regardless of time"""
        resolver = ConflictResolver(policy=ConflictResolutionPolicy.DESTINATION_WINS)

        now = datetime.utcnow()
        conflict = SyncConflict(
            conflict_type=ConflictType.FIELD_MISMATCH,
            focus_item={"title": "Focus Title", "updatedAt": (now - timedelta(hours=1))},
            calendar_item={"summary": "Calendar Title", "updated": now.isoformat()}  # Even though Calendar is newer
        )

        winning_side, resolved_data = resolver.resolve_conflict(conflict)

        assert winning_side == "focus"

    def test_resolve_conflict_manual(self):
        """Manual policy returns conflict for user review"""
        resolver = ConflictResolver(policy=ConflictResolutionPolicy.MANUAL_APPROVAL)

        conflict = SyncConflict(
            conflict_type=ConflictType.OVERLAPPING_EDIT,
            focus_item={"title": "Focus"},
            calendar_item={"summary": "Calendar"}
        )

        winning_side, resolved_data = resolver.resolve_conflict(conflict)

        assert winning_side == "manual"
        # Resolved data contains conflict info for UI
        assert resolved_data is not None

    def test_resolve_conflict_merge(self):
        """Merge policy combines non-conflicting changes"""
        resolver = ConflictResolver(policy=ConflictResolutionPolicy.MERGE_FIELDS)

        now = datetime.utcnow()
        conflict = SyncConflict(
            conflict_type=ConflictType.OVERLAPPING_EDIT,
            focus_item={
                "title": "Focus Title",  # Changed in Focus
                "description": "Original Desc",  # Not changed
                "updatedAt": now
            },
            calendar_item={
                "summary": "Original Title",  # Not changed
                "description": "Calendar Desc",  # Changed in Calendar
                "updated": (now - timedelta(minutes=5)).isoformat()
            },
            field_diffs=["title", "description"]
        )

        winning_side, resolved_data = resolver.resolve_conflict(conflict)

        assert winning_side == "merged"
        # Merged data should exist
        assert resolved_data is not None


class TestConflictDetectionEdgeCases:
    """Edge case tests for conflict detection"""

    def test_detect_no_last_sync(self):
        """Detection works without last sync time"""
        resolver = ConflictResolver()

        focus_item = {"id": "f1", "title": "Test", "updatedAt": datetime.utcnow()}
        calendar_item = {"id": "c1", "summary": "Test"}

        # Should not raise even without last_sync_time
        conflict = resolver.detect_conflicts(
            focus_item=focus_item,
            calendar_item=calendar_item,
            last_sync_time=None
        )

        # May or may not have conflict, but shouldn't crash
        assert True

    def test_detect_missing_updated_at(self):
        """Detection handles missing updatedAt"""
        resolver = ConflictResolver()

        focus_item = {"id": "f1", "title": "Test"}  # No updatedAt
        calendar_item = {"id": "c1", "summary": "Different"}

        # Should handle gracefully
        try:
            conflict = resolver.detect_conflicts(
                focus_item=focus_item,
                calendar_item=calendar_item,
                last_sync_time=datetime.utcnow()
            )
        except Exception as e:
            pytest.fail(f"Should handle missing updatedAt gracefully: {e}")

    def test_detect_empty_items(self):
        """Detection handles empty items"""
        resolver = ConflictResolver()

        conflict = resolver.detect_conflicts(
            focus_item={},
            calendar_item={},
            last_sync_time=datetime.utcnow()
        )

        # Empty items shouldn't crash
        assert True


class TestConflictResolutionIntegration:
    """Integration tests for conflict resolution workflow"""

    def test_full_workflow_detect_and_resolve(self):
        """Full workflow: detect conflict then resolve"""
        resolver = ConflictResolver(policy=ConflictResolutionPolicy.LAST_MODIFIED_WINS)

        now = datetime.utcnow()
        last_sync = now - timedelta(hours=1)

        focus_item = {
            "id": "f1",
            "title": "Updated in Focus",
            "description": "Same",
            "updatedAt": now - timedelta(minutes=10)
        }

        calendar_item = {
            "id": "c1",
            "summary": "Updated in Calendar",
            "description": "Same",
            "updated": (now - timedelta(minutes=5)).isoformat()  # Newer
        }

        # Step 1: Detect
        conflict = resolver.detect_conflicts(
            focus_item=focus_item,
            calendar_item=calendar_item,
            last_sync_time=last_sync
        )

        assert conflict is not None

        # Step 2: Resolve
        winning_side, resolved_data = resolver.resolve_conflict(conflict)

        assert winning_side == "calendar"  # Calendar is newer

    def test_multiple_conflicts_batch(self):
        """Handle multiple conflicts in batch"""
        resolver = ConflictResolver(policy=ConflictResolutionPolicy.DESTINATION_WINS)

        now = datetime.utcnow()

        items = [
            (
                {"id": "f1", "title": "Focus 1", "updatedAt": now},
                {"id": "c1", "summary": "Cal 1", "updated": now.isoformat()}
            ),
            (
                {"id": "f2", "title": "Focus 2", "updatedAt": now},
                {"id": "c2", "summary": "Cal 2", "updated": now.isoformat()}
            ),
        ]

        results = []
        for focus, calendar in items:
            conflict = resolver.detect_conflicts(
                focus_item=focus,
                calendar_item=calendar,
                last_sync_time=now - timedelta(hours=1)
            )
            if conflict:
                winning_side, _ = resolver.resolve_conflict(conflict)
                results.append(winning_side)

        # All should be resolved with destination_wins (Focus) policy
        assert all(r == "focus" for r in results)


class TestPendingConflicts:
    """Tests for pending conflict management"""

    def test_get_pending_conflicts(self):
        """Get pending conflicts returns serialized list"""
        resolver = ConflictResolver(policy=ConflictResolutionPolicy.MANUAL_APPROVAL)

        conflict = SyncConflict(
            conflict_type=ConflictType.OVERLAPPING_EDIT,
            focus_item={"id": "f1"},
            calendar_item={"id": "c1"}
        )

        # Resolve with manual policy adds to pending
        resolver.resolve_conflict(conflict)

        pending = resolver.get_pending_conflicts()
        assert len(pending) == 1
        assert pending[0]["conflict_type"] == "overlapping_edit"

    def test_resolve_pending_conflict(self):
        """Resolve a pending conflict with user decision"""
        resolver = ConflictResolver(policy=ConflictResolutionPolicy.MANUAL_APPROVAL)

        conflict = SyncConflict(
            conflict_type=ConflictType.OVERLAPPING_EDIT,
            focus_item={"id": "f1"},
            calendar_item={"id": "c1"}
        )

        # Add to pending
        resolver.resolve_conflict(conflict)
        assert len(resolver.pending_conflicts) == 1

        # Resolve
        result = resolver.resolve_pending_conflict(0, "focus")
        assert result is True
        assert len(resolver.pending_conflicts) == 0

    def test_resolve_invalid_pending_index(self):
        """Invalid index returns False"""
        resolver = ConflictResolver()

        result = resolver.resolve_pending_conflict(999, "focus")
        assert result is False
