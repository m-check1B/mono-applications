"""
Command History Schemas

Pydantic models for command history API requests and responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.models.command_history import CommandSource, CommandStatus


# Request schemas

class LogCommandRequest(BaseModel):
    """Request to log a new command"""
    source: CommandSource
    command: str = Field(..., min_length=1, description="Command text or description")
    intent: Optional[str] = Field(None, description="Parsed intent")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    telemetryId: Optional[str] = Field(None, description="Link to routing telemetry")
    agentSessionId: Optional[str] = Field(None, description="II-Agent session UUID")
    conversationId: Optional[str] = Field(None, description="AI conversation ID")
    model: Optional[str] = Field(None, description="AI model used")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class UpdateCommandStatusRequest(BaseModel):
    """Request to update command status"""
    status: CommandStatus
    result: Optional[Dict[str, Any]] = Field(None, description="Execution result")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details")


class CommandHistoryQueryRequest(BaseModel):
    """Request to query command history"""
    source: Optional[CommandSource] = Field(None, description="Filter by command source")
    intent: Optional[str] = Field(None, description="Filter by intent")
    status: Optional[CommandStatus] = Field(None, description="Filter by status")
    since: Optional[datetime] = Field(None, description="Start date filter")
    until: Optional[datetime] = Field(None, description="End date filter")
    limit: int = Field(50, ge=1, le=200, description="Maximum results")
    offset: int = Field(0, ge=0, description="Pagination offset")


class UnifiedTimelineRequest(BaseModel):
    """Request for unified timeline"""
    since: Optional[datetime] = Field(None, description="Start date (default: 7 days ago)")
    until: Optional[datetime] = Field(None, description="End date (default: now)")
    sources: Optional[List[CommandSource]] = Field(None, description="Filter by command sources")
    includeTelemetry: bool = Field(True, description="Include routing telemetry")
    limit: int = Field(100, ge=1, le=500, description="Maximum timeline entries")


class ActivitySummaryRequest(BaseModel):
    """Request for activity summary"""
    since: Optional[datetime] = Field(None, description="Start date (default: 7 days ago)")
    until: Optional[datetime] = Field(None, description="End date (default: now)")


# Response schemas

class CommandHistoryResponse(BaseModel):
    """Command history record"""
    id: str
    userId: str
    source: str
    command: str
    intent: Optional[str]
    status: str
    startedAt: datetime
    completedAt: Optional[datetime]
    durationMs: Optional[float]
    context: Optional[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    error: Optional[Dict[str, Any]]
    telemetryId: Optional[str]
    agentSessionId: Optional[str]
    conversationId: Optional[str]
    model: Optional[str]
    confidence: Optional[float]
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class CommandHistoryListResponse(BaseModel):
    """List of command history records"""
    commands: List[CommandHistoryResponse]
    total: int
    limit: int
    offset: int


class TimelineEntry(BaseModel):
    """Unified timeline entry (can be command or telemetry)"""
    id: str
    type: str  # "command" or "telemetry"
    timestamp: datetime
    source: str

    # Command-specific fields (when type="command")
    command: Optional[str] = None
    intent: Optional[str] = None
    status: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    durationMs: Optional[float] = None
    model: Optional[str] = None
    confidence: Optional[float] = None
    telemetryId: Optional[str] = None
    agentSessionId: Optional[str] = None
    conversationId: Optional[str] = None

    # Telemetry-specific fields (when type="telemetry")
    detectedType: Optional[str] = None
    route: Optional[str] = None
    workflowSteps: Optional[int] = None
    escalationReason: Optional[Dict[str, Any]] = None
    decisionStatus: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class UnifiedTimelineResponse(BaseModel):
    """Unified timeline of user activity"""
    timeline: List[TimelineEntry]
    total: int
    period: Dict[str, str]  # {since, until}


class ActivitySummaryResponse(BaseModel):
    """Summary of user activity"""
    period: Dict[str, str]
    total_commands: int
    completed: int
    failed: int
    in_progress: int
    success_rate: float
    by_source: Dict[str, int]
    by_intent: Dict[str, int]
    avg_duration_ms: Optional[float]


# Additional helper schemas

class CommandSourceInfo(BaseModel):
    """Information about command source types"""
    value: str
    description: str


class CommandSourcesResponse(BaseModel):
    """List of available command sources"""
    sources: List[CommandSourceInfo]


class CommandStatusInfo(BaseModel):
    """Information about command status types"""
    value: str
    description: str


class CommandStatusesResponse(BaseModel):
    """List of available command statuses"""
    statuses: List[CommandStatusInfo]
