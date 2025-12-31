"""Webhook endpoint for receiving alerts from Alertmanager.

This module provides an endpoint for Alertmanager to push alerts
to the backend for logging and potential processing.
"""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.logging import get_logger

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = get_logger(__name__)


class AlertLabel(BaseModel):
    """Alert labels."""

    alertname: str
    severity: str
    component: str | None = None
    service: str | None = None
    team: str | None = None


class AlertAnnotation(BaseModel):
    """Alert annotations."""

    summary: str
    description: str | None = None
    runbook: str | None = None
    dashboard: str | None = None


class Alert(BaseModel):
    """Individual alert from Alertmanager."""

    status: str = Field(description="firing|resolved")
    labels: AlertLabel
    annotations: AlertAnnotation
    startsAt: datetime
    endsAt: datetime | None = None
    generatorURL: str | None = None
    fingerprint: str


class AlertmanagerPayload(BaseModel):
    """Alertmanager webhook payload."""

    receiver: str
    status: str
    alerts: list[Alert]
    groupLabels: dict[str, str]
    commonLabels: dict[str, str]
    commonAnnotations: dict[str, str]
    externalURL: str
    version: str
    groupKey: str
    truncatedAlerts: int = 0


@router.post("/alerts")
async def receive_alertmanager_webhook(payload: AlertmanagerPayload) -> dict[str, str]:
    """Receive alerts from Alertmanager.

    This endpoint accepts webhook notifications from Alertmanager.
    Alerts are logged and can be processed further (e.g., store in DB,
    send to Slack, trigger remediation actions).

    Args:
        payload: Alertmanager webhook payload

    Returns:
        dict: Acknowledgment response
    """
    logger.info(
        "Received alerts from Alertmanager",
        receiver=payload.receiver,
        status=payload.status,
        alert_count=len(payload.alerts),
    )

    for alert in payload.alerts:
        alert_name = alert.labels.alertname
        severity = alert.labels.severity
        summary = alert.annotations.summary
        status = alert.status

        if status == "firing":
            logger.warning(
                "Alert firing",
                alert_name=alert_name,
                severity=severity,
                summary=summary,
                fingerprint=alert.fingerprint,
            )
        else:
            logger.info(
                "Alert resolved",
                alert_name=alert_name,
                fingerprint=alert.fingerprint,
            )

    return {"status": "accepted", "alerts_received": len(payload.alerts)}
