"""Type definitions for events-core."""

from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class EventPriority(str, Enum):
    """Event priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Event(BaseModel):
    """Standard event envelope."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str = Field(..., description="Event type (e.g., 'user.created')")
    data: Dict[str, Any] = Field(default_factory=dict)
    source: Optional[str] = Field(None, description="Source module/service")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = Field(None, description="For tracing related events")
    priority: EventPriority = Field(default=EventPriority.NORMAL)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EventResult(BaseModel):
    """Result from publishing an event."""
    event_id: str
    published: bool
    routing_key: str
    error: Optional[str] = None


# Type aliases for handlers
EventHandler = Callable[[Event], Awaitable[None]]
RawEventHandler = Callable[[str, Dict[str, Any]], Awaitable[None]]
