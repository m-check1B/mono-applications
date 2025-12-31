"""
Conflict Resolution Module - Advanced conflict handling for calendar sync

Provides conflict detection and resolution strategies for two-way sync between
Focus tasks/events and Google Calendar.
"""

from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConflictResolutionPolicy(str, Enum):
    """
    Conflict resolution strategies.
    """
    LAST_MODIFIED_WINS = "last_modified_wins"  # Most recently modified wins (default)
    MANUAL_APPROVAL = "manual_approval"        # Surface to UI for user decision
    SOURCE_WINS = "source_wins"                # Calendar always wins
    DESTINATION_WINS = "destination_wins"      # Focus always wins
    MERGE_FIELDS = "merge_fields"              # Intelligent field-level merge


class ConflictType(str, Enum):
    """
    Types of sync conflicts.
    """
    OVERLAPPING_EDIT = "overlapping_edit"      # Both sides modified since last sync
    DELETE_CONFLICT = "delete_conflict"         # One side deleted, other modified
    DUPLICATE_ENTRY = "duplicate_entry"         # Same event exists on both sides
    FIELD_MISMATCH = "field_mismatch"          # Specific fields differ


class SyncConflict:
    """
    Represents a sync conflict between Focus and Calendar.
    """

    def __init__(
        self,
        conflict_type: ConflictType,
        focus_item: Optional[Dict[str, Any]],
        calendar_item: Optional[Dict[str, Any]],
        field_diffs: Optional[List[str]] = None
    ):
        self.conflict_type = conflict_type
        self.focus_item = focus_item
        self.calendar_item = calendar_item
        self.field_diffs = field_diffs or []
        self.detected_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert conflict to dict for serialization."""
        return {
            "conflict_type": self.conflict_type.value,
            "focus_item": self.focus_item,
            "calendar_item": self.calendar_item,
            "field_diffs": self.field_diffs,
            "detected_at": self.detected_at.isoformat()
        }


class ConflictResolver:
    """
    Advanced conflict resolution for calendar sync.
    """

    def __init__(self, policy: ConflictResolutionPolicy = ConflictResolutionPolicy.LAST_MODIFIED_WINS):
        self.policy = policy
        self.pending_conflicts: List[SyncConflict] = []

    def detect_conflicts(
        self,
        focus_item: Dict[str, Any],
        calendar_item: Dict[str, Any],
        last_sync_time: Optional[datetime] = None
    ) -> Optional[SyncConflict]:
        """
        Detect conflicts between Focus and Calendar items.

        Args:
            focus_item: Focus task/event data
            calendar_item: Calendar event data
            last_sync_time: Time of last successful sync

        Returns:
            SyncConflict if conflict detected, None otherwise
        """
        # Check if both items were modified since last sync
        focus_modified = focus_item.get("updatedAt") or focus_item.get("updated")
        calendar_modified = calendar_item.get("updated")

        if not focus_modified or not calendar_modified:
            # Can't detect conflict without modification times
            return None

        # Parse modification times
        try:
            if isinstance(focus_modified, str):
                focus_modified = datetime.fromisoformat(focus_modified.replace("Z", "+00:00"))
            if isinstance(calendar_modified, str):
                calendar_modified = datetime.fromisoformat(calendar_modified.replace("Z", "+00:00"))
        except Exception as e:
            logger.error(f"Failed to parse modification times: {e}")
            return None

        # If we have last sync time, check for overlapping edits
        if last_sync_time:
            focus_edited_after_sync = focus_modified > last_sync_time
            calendar_edited_after_sync = calendar_modified > last_sync_time

            if focus_edited_after_sync and calendar_edited_after_sync:
                # Both sides modified since last sync - overlapping edit
                field_diffs = self._find_field_differences(focus_item, calendar_item)
                return SyncConflict(
                    conflict_type=ConflictType.OVERLAPPING_EDIT,
                    focus_item=focus_item,
                    calendar_item=calendar_item,
                    field_diffs=field_diffs
                )

        # Check for field-level differences
        field_diffs = self._find_field_differences(focus_item, calendar_item)
        if field_diffs:
            return SyncConflict(
                conflict_type=ConflictType.FIELD_MISMATCH,
                focus_item=focus_item,
                calendar_item=calendar_item,
                field_diffs=field_diffs
            )

        return None

    def _find_field_differences(
        self,
        focus_item: Dict[str, Any],
        calendar_item: Dict[str, Any]
    ) -> List[str]:
        """
        Find which fields differ between Focus and Calendar items.

        Args:
            focus_item: Focus task/event data
            calendar_item: Calendar event data

        Returns:
            List of field names that differ
        """
        diffs = []

        # Map calendar fields to focus fields
        field_mapping = {
            "summary": "title",
            "description": "description",
            "start.dateTime": "dueDate",
            "end.dateTime": "endDate"
        }

        for calendar_field, focus_field in field_mapping.items():
            # Handle nested fields (e.g., "start.dateTime")
            calendar_value = self._get_nested_value(calendar_item, calendar_field)
            focus_value = focus_item.get(focus_field)

            # Normalize values for comparison
            if calendar_value != focus_value:
                # Special handling for dates
                if "date" in focus_field.lower() or "DateTime" in calendar_field:
                    try:
                        if isinstance(calendar_value, str):
                            calendar_value = datetime.fromisoformat(calendar_value.replace("Z", "+00:00"))
                        if isinstance(focus_value, str):
                            focus_value = datetime.fromisoformat(focus_value.replace("Z", "+00:00"))

                        # Allow small time differences (< 1 minute)
                        if calendar_value and focus_value:
                            time_diff = abs((calendar_value - focus_value).total_seconds())
                            if time_diff < 60:
                                continue
                    except Exception as e:
                        logger.debug(f"Date comparison failed during conflict detection: {e}")

                diffs.append(focus_field)

        return diffs

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dict using dot notation."""
        parts = path.split(".")
        value = data
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value

    def resolve_conflict(
        self,
        conflict: SyncConflict,
        user_policy: Optional[ConflictResolutionPolicy] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Resolve a sync conflict based on policy.

        Args:
            conflict: The conflict to resolve
            user_policy: Optional user-specific policy override

        Returns:
            Tuple of (winning_side, resolved_data)
            - winning_side: "focus", "calendar", "merged", or "manual"
            - resolved_data: The resolved item data
        """
        policy = user_policy or self.policy

        if policy == ConflictResolutionPolicy.LAST_MODIFIED_WINS:
            return self._resolve_last_modified_wins(conflict)

        elif policy == ConflictResolutionPolicy.SOURCE_WINS:
            # Calendar wins
            return ("calendar", conflict.calendar_item)

        elif policy == ConflictResolutionPolicy.DESTINATION_WINS:
            # Focus wins
            return ("focus", conflict.focus_item)

        elif policy == ConflictResolutionPolicy.MERGE_FIELDS:
            return self._resolve_merge_fields(conflict)

        elif policy == ConflictResolutionPolicy.MANUAL_APPROVAL:
            # Add to pending conflicts for UI review
            self.pending_conflicts.append(conflict)
            return ("manual", conflict.to_dict())

        else:
            # Default to last modified wins
            return self._resolve_last_modified_wins(conflict)

    def _resolve_last_modified_wins(
        self,
        conflict: SyncConflict
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Resolve conflict by choosing most recently modified item.
        """
        focus_modified = conflict.focus_item.get("updatedAt") or conflict.focus_item.get("updated")
        calendar_modified = conflict.calendar_item.get("updated")

        try:
            if isinstance(focus_modified, str):
                focus_modified = datetime.fromisoformat(focus_modified.replace("Z", "+00:00"))
            if isinstance(calendar_modified, str):
                calendar_modified = datetime.fromisoformat(calendar_modified.replace("Z", "+00:00"))

            if calendar_modified and focus_modified:
                if calendar_modified > focus_modified:
                    return ("calendar", conflict.calendar_item)
                else:
                    return ("focus", conflict.focus_item)
        except Exception as e:
            logger.error(f"Failed to compare modification times: {e}")

        # Fallback to focus if comparison fails
        return ("focus", conflict.focus_item)

    def _resolve_merge_fields(
        self,
        conflict: SyncConflict
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Resolve conflict by intelligently merging fields.

        Strategy:
        - For each differing field, take the most recently modified value
        - For non-conflicting fields, merge both sides
        """
        merged = conflict.focus_item.copy()
        focus_modified = conflict.focus_item.get("updatedAt") or conflict.focus_item.get("updated")
        calendar_modified = conflict.calendar_item.get("updated")

        try:
            if isinstance(focus_modified, str):
                focus_modified = datetime.fromisoformat(focus_modified.replace("Z", "+00:00"))
            if isinstance(calendar_modified, str):
                calendar_modified = datetime.fromisoformat(calendar_modified.replace("Z", "+00:00"))

            # For conflicting fields, use calendar values if it's newer
            if calendar_modified and focus_modified and calendar_modified > focus_modified:
                field_mapping = {
                    "title": "summary",
                    "description": "description",
                    "dueDate": "start.dateTime"
                }

                for focus_field in conflict.field_diffs:
                    calendar_field = field_mapping.get(focus_field)
                    if calendar_field:
                        calendar_value = self._get_nested_value(conflict.calendar_item, calendar_field)
                        if calendar_value:
                            merged[focus_field] = calendar_value

            return ("merged", merged)

        except Exception as e:
            logger.error(f"Failed to merge fields: {e}")
            # Fallback to last modified wins
            return self._resolve_last_modified_wins(conflict)

    def get_pending_conflicts(self) -> List[Dict[str, Any]]:
        """
        Get all pending conflicts awaiting manual resolution.

        Returns:
            List of conflict dicts for UI display
        """
        return [conflict.to_dict() for conflict in self.pending_conflicts]

    def resolve_pending_conflict(
        self,
        conflict_index: int,
        resolution: str
    ) -> bool:
        """
        Resolve a pending conflict with user's decision.

        Args:
            conflict_index: Index in pending_conflicts list
            resolution: "focus", "calendar", or "merged"

        Returns:
            True if resolved, False if invalid index
        """
        if 0 <= conflict_index < len(self.pending_conflicts):
            conflict = self.pending_conflicts.pop(conflict_index)
            logger.info(f"Manually resolved conflict: {conflict.conflict_type.value} -> {resolution}")
            return True
        return False
