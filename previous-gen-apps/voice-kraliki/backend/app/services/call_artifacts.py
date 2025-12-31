"""
Call Artifacts Service

Manages post-call artifacts including:
- Call summaries and recordings
- Transcripts and insights
- Analytics and metrics
- Search and filtering capabilities
"""

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)

class ArtifactType(Enum):
    SUMMARY = "summary"
    TRANSCRIPT = "transcript"
    RECORDING = "recording"
    INSIGHTS = "insights"
    ANALYTICS = "analytics"
    SUGGESTIONS = "suggestions"
    WORKFLOW_EXECUTION = "workflow_execution"

class CallStatus(Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    IN_PROGRESS = "in_progress"

@dataclass
class CallArtifact:
    id: str
    call_id: str
    artifact_type: ArtifactType
    content: dict[str, Any]
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)

@dataclass
class CallRecord:
    id: str
    customer_phone: str
    agent_id: str | None
    provider: str
    status: CallStatus
    duration: int | None  # seconds
    started_at: datetime
    ended_at: datetime | None
    artifacts: list[str]  # artifact IDs
    metadata: dict[str, Any]

    def __post_init__(self):
        if isinstance(self.started_at, str):
            self.started_at = datetime.fromisoformat(self.started_at)
        if isinstance(self.ended_at, str):
            self.ended_at = datetime.fromisoformat(self.ended_at)

@dataclass
class SearchQuery:
    query: str
    filters: dict[str, Any]
    sort_by: str = "created_at"
    sort_order: str = "desc"
    limit: int = 50
    offset: int = 0

class CallArtifactsService:
    """Service for managing call artifacts and records"""

    def __init__(self):
        self.artifacts: dict[str, CallArtifact] = {}
        self.call_records: dict[str, CallRecord] = {}
        self.search_index: dict[str, list[str]] = {}  # Simple text search index

    async def create_call_record(self,
                               customer_phone: str,
                               provider: str,
                               agent_id: str | None = None,
                               metadata: dict[str, Any] | None = None) -> str:
        """Create a new call record"""
        call_id = str(uuid4())

        call_record = CallRecord(
            id=call_id,
            customer_phone=customer_phone,
            agent_id=agent_id,
            provider=provider,
            status=CallStatus.IN_PROGRESS,
            duration=None,
            started_at=datetime.now(),
            ended_at=None,
            artifacts=[],
            metadata=metadata or {}
        )

        self.call_records[call_id] = call_record
        logger.info(f"Created call record: {call_id}")
        return call_id

    async def update_call_status(self,
                               call_id: str,
                               status: CallStatus,
                               duration: int | None = None) -> bool:
        """Update call status and duration"""
        call_record = self.call_records.get(call_id)
        if not call_record:
            return False

        call_record.status = status
        if duration is not None:
            call_record.duration = duration

        if status in [CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.ABANDONED]:
            call_record.ended_at = datetime.now()

        logger.info(f"Updated call {call_id} status to {status.value}")
        return True

    async def add_artifact(self,
                          call_id: str,
                          artifact_type: ArtifactType,
                          content: dict[str, Any],
                          metadata: dict[str, Any] | None = None) -> str:
        """Add an artifact to a call"""
        call_record = self.call_records.get(call_id)
        if not call_record:
            raise ValueError(f"Call record not found: {call_id}")

        artifact_id = str(uuid4())

        artifact = CallArtifact(
            id=artifact_id,
            call_id=call_id,
            artifact_type=artifact_type,
            content=content,
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.artifacts[artifact_id] = artifact
        call_record.artifacts.append(artifact_id)

        # Update search index
        self._update_search_index(artifact_id, content)

        logger.info(f"Added artifact {artifact_type.value} to call {call_id}")
        return artifact_id

    async def get_call_record(self, call_id: str) -> CallRecord | None:
        """Get call record by ID"""
        return self.call_records.get(call_id)

    async def get_artifact(self, artifact_id: str) -> CallArtifact | None:
        """Get artifact by ID"""
        return self.artifacts.get(artifact_id)

    async def get_call_artifacts(self,
                               call_id: str,
                               artifact_types: list[ArtifactType] | None = None) -> list[CallArtifact]:
        """Get all artifacts for a call, optionally filtered by type"""
        call_record = self.call_records.get(call_id)
        if not call_record:
            return []

        artifacts = []
        for artifact_id in call_record.artifacts:
            artifact = self.artifacts.get(artifact_id)
            if artifact and (not artifact_types or artifact.artifact_type in artifact_types):
                artifacts.append(artifact)

        return artifacts

    async def search_calls(self, search_query: SearchQuery) -> dict[str, Any]:
        """Search calls based on query and filters"""
        # Simple text search implementation
        matching_calls = []

        # Extract search terms
        search_terms = re.findall(r'\w+', search_query.query.lower())

        for call_record in self.call_records.values():
            # Check if call matches search criteria
            if self._matches_search_criteria(call_record, search_terms, search_query.filters):
                matching_calls.append(call_record)

        # Sort results
        reverse = search_query.sort_order == "desc"
        if search_query.sort_by == "created_at":
            matching_calls.sort(key=lambda x: x.started_at, reverse=reverse)
        elif search_query.sort_by == "duration":
            matching_calls.sort(key=lambda x: x.duration or 0, reverse=reverse)
        elif search_query.sort_by == "status":
            matching_calls.sort(key=lambda x: x.status.value, reverse=reverse)

        # Apply pagination
        total = len(matching_calls)
        start = search_query.offset
        end = start + search_query.limit
        paginated_calls = matching_calls[start:end]

        return {
            "calls": [asdict(call) for call in paginated_calls],
            "total": total,
            "offset": search_query.offset,
            "limit": search_query.limit
        }

    async def search_artifacts(self, search_query: SearchQuery) -> dict[str, Any]:
        """Search artifacts based on query and filters"""
        matching_artifacts = []

        # Extract search terms
        search_terms = re.findall(r'\w+', search_query.query.lower())

        for artifact in self.artifacts.values():
            # Check if artifact matches search criteria
            if self._artifact_matches_search_criteria(artifact, search_terms, search_query.filters):
                matching_artifacts.append(artifact)

        # Sort results
        reverse = search_query.sort_order == "desc"
        if search_query.sort_by == "created_at":
            matching_artifacts.sort(key=lambda x: x.created_at, reverse=reverse)

        # Apply pagination
        total = len(matching_artifacts)
        start = search_query.offset
        end = start + search_query.limit
        paginated_artifacts = matching_artifacts[start:end]

        return {
            "artifacts": [asdict(artifact) for artifact in paginated_artifacts],
            "total": total,
            "offset": search_query.offset,
            "limit": search_query.limit
        }

    async def get_call_analytics(self,
                               start_date: datetime | None = None,
                               end_date: datetime | None = None) -> dict[str, Any]:
        """Get analytics for calls within date range"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # Filter calls by date range
        filtered_calls = [
            call for call in self.call_records.values()
            if start_date <= call.started_at <= end_date
        ]

        # Calculate analytics
        total_calls = len(filtered_calls)
        completed_calls = len([c for c in filtered_calls if c.status == CallStatus.COMPLETED])
        failed_calls = len([c for c in filtered_calls if c.status == CallStatus.FAILED])
        abandoned_calls = len([c for c in filtered_calls if c.status == CallStatus.ABANDONED])

        # Calculate average duration
        completed_with_duration = [c for c in filtered_calls if c.duration is not None]
        avg_duration = sum(c.duration or 0 for c in completed_with_duration) / len(completed_with_duration) if completed_with_duration else 0

        # Provider breakdown
        provider_stats = {}
        for call in filtered_calls:
            provider = call.provider
            if provider not in provider_stats:
                provider_stats[provider] = {"total": 0, "completed": 0}
            provider_stats[provider]["total"] += 1
            if call.status == CallStatus.COMPLETED:
                provider_stats[provider]["completed"] += 1

        # Artifact counts
        artifact_counts = {}
        for artifact in self.artifacts.values():
            artifact_type = artifact.artifact_type.value
            artifact_counts[artifact_type] = artifact_counts.get(artifact_type, 0) + 1

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "call_stats": {
                "total": total_calls,
                "completed": completed_calls,
                "failed": failed_calls,
                "abandoned": abandoned_calls,
                "completion_rate": (completed_calls / total_calls * 100) if total_calls > 0 else 0,
                "average_duration": avg_duration
            },
            "provider_stats": provider_stats,
            "artifact_counts": artifact_counts
        }

    async def delete_call_record(self, call_id: str) -> bool:
        """Delete a call record and its artifacts"""
        call_record = self.call_records.get(call_id)
        if not call_record:
            return False

        # Delete artifacts
        for artifact_id in call_record.artifacts:
            if artifact_id in self.artifacts:
                del self.artifacts[artifact_id]
                # Remove from search index
                if artifact_id in self.search_index:
                    del self.search_index[artifact_id]

        # Delete call record
        del self.call_records[call_id]

        logger.info(f"Deleted call record and artifacts: {call_id}")
        return True

    def _update_search_index(self, artifact_id: str, content: dict[str, Any]):
        """Update search index for artifact"""
        # Extract searchable text from content
        searchable_text = json.dumps(content).lower()
        words = re.findall(r'\w+', searchable_text)

        self.search_index[artifact_id] = words

    def _matches_search_criteria(self,
                               call_record: CallRecord,
                               search_terms: list[str],
                               filters: dict[str, Any]) -> bool:
        """Check if call record matches search criteria"""
        # Check text search in artifacts
        if search_terms:
            matches_text = False
            for artifact_id in call_record.artifacts:
                if artifact_id in self.search_index:
                    indexed_words = self.search_index[artifact_id]
                    if any(term in indexed_words for term in search_terms):
                        matches_text = True
                        break

            if not matches_text:
                return False

        # Apply filters
        if filters.get("status") and call_record.status.value != filters["status"]:
            return False

        if filters.get("provider") and call_record.provider != filters["provider"]:
            return False

        if filters.get("customer_phone") and filters["customer_phone"] not in call_record.customer_phone:
            return False

        if filters.get("date_from") and call_record.started_at < datetime.fromisoformat(filters["date_from"]):
            return False

        if filters.get("date_to") and call_record.started_at > datetime.fromisoformat(filters["date_to"]):
            return False

        return True

    def _artifact_matches_search_criteria(self,
                                        artifact: CallArtifact,
                                        search_terms: list[str],
                                        filters: dict[str, Any]) -> bool:
        """Check if artifact matches search criteria"""
        # Check text search
        if search_terms:
            if artifact.id not in self.search_index:
                return False

            indexed_words = self.search_index[artifact.id]
            if not any(term in indexed_words for term in search_terms):
                return False

        # Apply filters
        if filters.get("artifact_type") and artifact.artifact_type.value != filters["artifact_type"]:
            return False

        if filters.get("call_id") and artifact.call_id != filters["call_id"]:
            return False

        return True

# Global instance
call_artifacts_service = CallArtifactsService()
