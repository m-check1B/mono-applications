"""
Command History Service

Provides functions for logging and querying command execution history
across all Focus by Kraliki interaction channels (voice, text, API, workflows).
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session

from app.core.security import generate_id
from app.models.command_history import CommandHistory, CommandSource, CommandStatus


def log_command(
    db: Session,
    *,
    user_id: str,
    source: CommandSource,
    command: str,
    intent: Optional[str] = None,
    status: CommandStatus = CommandStatus.PENDING,
    context: Optional[Dict[str, Any]] = None,
    telemetry_id: Optional[str] = None,
    agent_session_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    model: Optional[str] = None,
    confidence: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> CommandHistory:
    """
    Log a new command to the history.

    Args:
        db: Database session
        user_id: User ID
        source: Command source (voice, api, agent, etc.)
        command: The command text/description
        intent: Parsed intent (optional)
        status: Initial status (default: PENDING)
        context: Additional context (workspace, project, etc.)
        telemetry_id: Link to routing telemetry
        agent_session_id: II-Agent session UUID
        conversation_id: AI conversation ID
        model: AI model used
        confidence: Confidence score
        metadata: Additional metadata

    Returns:
        Created CommandHistory record
    """
    cmd = CommandHistory(
        id=generate_id(),
        userId=user_id,
        source=source,
        command=command,
        intent=intent,
        status=status,
        startedAt=datetime.utcnow(),
        context=context,
        telemetryId=telemetry_id,
        agentSessionId=agent_session_id,
        conversationId=conversation_id,
        model=model,
        confidence=confidence,
        command_metadata=metadata,
    )
    db.add(cmd)
    db.commit()
    db.refresh(cmd)
    return cmd


def update_command_status(
    db: Session,
    *,
    command_id: str,
    status: CommandStatus,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, Any]] = None,
) -> Optional[CommandHistory]:
    """
    Update command status and results.

    Args:
        db: Database session
        command_id: Command ID to update
        status: New status
        result: Execution result (optional)
        error: Error details (optional)

    Returns:
        Updated CommandHistory or None if not found
    """
    cmd = db.query(CommandHistory).filter(CommandHistory.id == command_id).first()
    if not cmd:
        return None

    cmd.status = status

    if status in (CommandStatus.COMPLETED, CommandStatus.FAILED, CommandStatus.CANCELLED):
        cmd.completedAt = datetime.utcnow()
        if cmd.startedAt:
            duration = (cmd.completedAt - cmd.startedAt).total_seconds() * 1000
            cmd.durationMs = duration

    if result:
        cmd.result = result
    if error:
        cmd.error = error

    db.commit()
    db.refresh(cmd)
    return cmd


def get_command_history(
    db: Session,
    *,
    user_id: str,
    source: Optional[CommandSource] = None,
    intent: Optional[str] = None,
    status: Optional[CommandStatus] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[List[CommandHistory], int]:
    """
    Query command history with filters.

    Args:
        db: Database session
        user_id: User ID
        source: Filter by command source (optional)
        intent: Filter by intent (optional)
        status: Filter by status (optional)
        since: Start date filter (optional)
        until: End date filter (optional)
        limit: Maximum results
        offset: Pagination offset

    Returns:
        Tuple of (command list, total count)
    """
    query = db.query(CommandHistory).filter(CommandHistory.userId == user_id)

    if source:
        query = query.filter(CommandHistory.source == source)
    if intent:
        query = query.filter(CommandHistory.intent == intent)
    if status:
        query = query.filter(CommandHistory.status == status)
    if since:
        query = query.filter(CommandHistory.startedAt >= since)
    if until:
        query = query.filter(CommandHistory.startedAt <= until)

    total = query.count()
    commands = query.order_by(desc(CommandHistory.startedAt)).limit(limit).offset(offset).all()

    return commands, total


def get_unified_timeline(
    db: Session,
    *,
    user_id: str,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    sources: Optional[List[CommandSource]] = None,
    include_telemetry: bool = True,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Get unified timeline of user activity across commands and telemetry.

    This answers the question: "What did I work on last week?"

    Args:
        db: Database session
        user_id: User ID
        since: Start date (default: 7 days ago)
        until: End date (default: now)
        sources: Filter by command sources (optional)
        include_telemetry: Include routing telemetry in timeline
        limit: Maximum timeline entries

    Returns:
        List of timeline entries with unified schema
    """
    if not since:
        since = datetime.utcnow() - timedelta(days=7)
    if not until:
        until = datetime.utcnow()

    # Build command history query
    cmd_query = db.query(CommandHistory).filter(
        and_(
            CommandHistory.userId == user_id,
            CommandHistory.startedAt >= since,
            CommandHistory.startedAt <= until,
        )
    )

    if sources:
        cmd_query = cmd_query.filter(CommandHistory.source.in_(sources))

    commands = cmd_query.order_by(desc(CommandHistory.startedAt)).limit(limit).all()

    # Build timeline entries
    timeline = []

    for cmd in commands:
        entry = {
            "id": cmd.id,
            "type": "command",
            "timestamp": cmd.startedAt,
            "source": cmd.source.value,
            "command": cmd.command,
            "intent": cmd.intent,
            "status": cmd.status.value,
            "context": cmd.context,
            "result": cmd.result,
            "error": cmd.error,
            "durationMs": cmd.durationMs,
            "model": cmd.model,
            "confidence": cmd.confidence,
            "telemetryId": cmd.telemetryId,
            "agentSessionId": cmd.agentSessionId,
            "conversationId": cmd.conversationId,
        }
        timeline.append(entry)

    # Optionally include routing telemetry
    if include_telemetry:
        from app.models.request_telemetry import RequestTelemetry

        telemetry_query = db.query(RequestTelemetry).filter(
            and_(
                RequestTelemetry.userId == user_id,
                RequestTelemetry.createdAt >= since,
                RequestTelemetry.createdAt <= until,
            )
        )

        telemetry_records = telemetry_query.order_by(desc(RequestTelemetry.createdAt)).limit(limit).all()

        for tel in telemetry_records:
            # Skip telemetry if already represented by a command
            if any(e.get("telemetryId") == tel.id for e in timeline):
                continue

            entry = {
                "id": tel.id,
                "type": "telemetry",
                "timestamp": tel.createdAt,
                "source": tel.source.value,
                "intent": tel.intent,
                "detectedType": tel.detectedType,
                "confidence": tel.confidence,
                "route": tel.route.value,
                "workflowSteps": tel.workflowSteps,
                "escalationReason": tel.escalationReason,
                "decisionStatus": tel.decisionStatus.value if tel.decisionStatus else None,
                "details": tel.details,
            }
            timeline.append(entry)

    # Sort unified timeline by timestamp
    timeline.sort(key=lambda x: x["timestamp"], reverse=True)

    return timeline[:limit]


def get_user_activity_summary(
    db: Session,
    *,
    user_id: str,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Get summary statistics of user activity.

    Args:
        db: Database session
        user_id: User ID
        since: Start date (default: 7 days ago)
        until: End date (default: now)

    Returns:
        Dictionary with activity statistics
    """
    if not since:
        since = datetime.utcnow() - timedelta(days=7)
    if not until:
        until = datetime.utcnow()

    query = db.query(CommandHistory).filter(
        and_(
            CommandHistory.userId == user_id,
            CommandHistory.startedAt >= since,
            CommandHistory.startedAt <= until,
        )
    )

    total_commands = query.count()
    completed = query.filter(CommandHistory.status == CommandStatus.COMPLETED).count()
    failed = query.filter(CommandHistory.status == CommandStatus.FAILED).count()
    in_progress = query.filter(CommandHistory.status == CommandStatus.IN_PROGRESS).count()

    # Count by source
    by_source = {}
    for source in CommandSource:
        count = query.filter(CommandHistory.source == source).count()
        if count > 0:
            by_source[source.value] = count

    # Count by intent
    intent_counts = (
        db.query(CommandHistory.intent, func.count(CommandHistory.id))
        .filter(
            and_(
                CommandHistory.userId == user_id,
                CommandHistory.startedAt >= since,
                CommandHistory.startedAt <= until,
                CommandHistory.intent.isnot(None),
            )
        )
        .group_by(CommandHistory.intent)
        .all()
    )
    by_intent = {intent: count for intent, count in intent_counts if intent}

    # Calculate average duration for completed commands
    completed_with_duration = query.filter(
        and_(
            CommandHistory.status == CommandStatus.COMPLETED,
            CommandHistory.durationMs.isnot(None),
        )
    ).all()

    avg_duration_ms = None
    if completed_with_duration:
        total_duration = sum(cmd.durationMs for cmd in completed_with_duration)
        avg_duration_ms = total_duration / len(completed_with_duration)

    return {
        "period": {
            "since": since.isoformat(),
            "until": until.isoformat(),
        },
        "total_commands": total_commands,
        "completed": completed,
        "failed": failed,
        "in_progress": in_progress,
        "success_rate": (completed / total_commands * 100) if total_commands > 0 else 0,
        "by_source": by_source,
        "by_intent": by_intent,
        "avg_duration_ms": avg_duration_ms,
    }
