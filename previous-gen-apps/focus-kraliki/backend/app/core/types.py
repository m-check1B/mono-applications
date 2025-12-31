"""
Common type definitions for Focus-Kraliki application.

Provides TypedDicts for frequently used data structures to replace
excessive use of `Dict[str, Any]` and improve type safety.
"""

from typing import Dict, Optional, TypedDict, List, Any


class ToolArguments(TypedDict, total=False):
    """TypedDict for tool function arguments."""

    pass


class ToolResult(TypedDict, total=False):
    """TypedDict for tool execution result."""

    pass


class ContextData(TypedDict, total=False):
    """TypedDict for optional context data passed between components."""

    pass


class MemoryValue(TypedDict, total=False):
    """TypedDict for memory storage values."""

    pass


class ActivityData(TypedDict, total=False):
    """TypedDict for user activity data."""

    pass


class PatternData(TypedDict, total=False):
    """TypedDict for analysis pattern data."""

    pass


class EscalationReason(TypedDict, total=False):
    """TypedDict for escalation reason details."""

    pass


class TaskContext(TypedDict, total=False):
    """TypedDict for task context."""

    pass


class StructuredGoal(TypedDict, total=False):
    """TypedDict for structured goal data."""

    pass


class TelemetryNotes(TypedDict, total=False):
    """TypedDict for telemetry decision notes."""

    pass


class ToolInput(TypedDict, total=False):
    """TypedDict for tool input data."""

    pass


class ToolOutput(TypedDict, total=False):
    """TypedDict for tool output data."""

    pass


class EventData(TypedDict, total=False):
    """TypedDict for event data."""

    pass


class ErrorDetails(TypedDict, total=False):
    """TypedDict for error details."""

    pass


class ExecutionResult(TypedDict, total=False):
    """TypedDict for execution result."""

    pass


class Metadata(TypedDict, total=False):
    """TypedDict for additional metadata."""

    pass
