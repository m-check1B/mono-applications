from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.security import generate_id
from app.models.request_telemetry import (
    RequestTelemetry,
    TelemetryRoute,
    TelemetrySource,
    WorkflowDecisionStatus,
)


def _merge_details(existing: Optional[Dict[str, Any]], new_data: Optional[Dict[str, Any]]):
    if not new_data:
        return existing
    base = existing.copy() if existing else {}
    base.update(new_data)
    return base


def log_enhance_input(
    db: Session,
    *,
    user_id: str,
    intent: Optional[str],
    detected_type: Optional[str],
    confidence: Optional[float],
    details: Optional[Dict[str, Any]] = None,
) -> RequestTelemetry:
    telemetry = RequestTelemetry(
        id=generate_id(),
        userId=user_id,
        source=TelemetrySource.ENHANCE_INPUT,
        intent=intent,
        detectedType=detected_type,
        confidence=confidence,
        details=details,
    )
    db.add(telemetry)
    db.commit()
    db.refresh(telemetry)
    return telemetry


def update_workflow_details(
    db: Session,
    *,
    telemetry_id: str,
    workflow_steps: int,
    confidence: Optional[float] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Optional[RequestTelemetry]:
    telemetry = (
        db.query(RequestTelemetry)
        .filter(RequestTelemetry.id == telemetry_id)
        .first()
    )
    if not telemetry:
        return None

    telemetry.workflowSteps = workflow_steps
    telemetry.details = _merge_details(telemetry.details, details)
    if confidence is not None:
        telemetry.confidence = confidence
    db.commit()
    db.refresh(telemetry)
    return telemetry


def log_orchestrate_event(
    db: Session,
    *,
    user_id: str,
    workflow_steps: int,
    confidence: Optional[float] = None,
    details: Optional[Dict[str, Any]] = None,
) -> RequestTelemetry:
    telemetry = RequestTelemetry(
        id=generate_id(),
        userId=user_id,
        source=TelemetrySource.ORCHESTRATE_TASK,
        workflowSteps=workflow_steps,
        confidence=confidence,
        details=details,
    )
    db.add(telemetry)
    db.commit()
    db.refresh(telemetry)
    return telemetry


def mark_route_decision(
    db: Session,
    *,
    telemetry_id: str,
    route: TelemetryRoute,
    reason: Optional[Dict[str, Any]] = None,
) -> Optional[RequestTelemetry]:
    telemetry = (
        db.query(RequestTelemetry)
        .filter(RequestTelemetry.id == telemetry_id)
        .first()
    )
    if not telemetry:
        return None

    telemetry.route = route
    telemetry.escalationReason = reason
    db.commit()
    db.refresh(telemetry)
    return telemetry


def record_workflow_decision(
    db: Session,
    *,
    telemetry_id: str,
    status: WorkflowDecisionStatus,
    notes: Optional[Dict[str, Any]] = None,
) -> Optional[RequestTelemetry]:
    telemetry = (
        db.query(RequestTelemetry)
        .filter(RequestTelemetry.id == telemetry_id)
        .first()
    )
    if not telemetry:
        return None

    telemetry.decisionStatus = status
    telemetry.decisionNotes = notes
    telemetry.decisionAt = datetime.utcnow()
    db.commit()
    db.refresh(telemetry)
    return telemetry
