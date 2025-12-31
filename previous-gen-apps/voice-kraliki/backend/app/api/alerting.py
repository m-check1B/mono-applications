"""
Alerting API Routes

Provides endpoints for managing alerts, alert rules, and metrics.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from ..auth.jwt_auth import get_current_user
from ..middleware.rate_limit import API_RATE_LIMIT, limiter
from ..services.alerting import AlertRule, AlertSeverity, AlertStatus, MetricType, alerting_service

router = APIRouter(prefix="/alerting", tags=["alerting"])

# Pydantic models for API
class AlertRuleCreate(BaseModel):
    name: str
    description: str
    metric_type: MetricType
    severity: AlertSeverity
    threshold: float
    operator: str
    duration_minutes: int
    enabled: bool = True
    tags: dict[str, str] | None = None
    notification_channels: list[str] | None = None

class AlertRuleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    severity: AlertSeverity | None = None
    threshold: float | None = None
    operator: str | None = None
    duration_minutes: int | None = None
    enabled: bool | None = None
    tags: dict[str, str] | None = None
    notification_channels: list[str] | None = None

class AlertResponse(BaseModel):
    id: str
    rule_id: str
    severity: AlertSeverity
    status: AlertStatus
    title: str
    description: str
    metric_value: float
    threshold: float
    triggered_at: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    metadata: dict[str, Any] | None = None

class AlertRuleResponse(BaseModel):
    id: str
    name: str
    description: str
    metric_type: MetricType
    severity: AlertSeverity
    threshold: float
    operator: str
    duration_minutes: int
    enabled: bool
    tags: dict[str, str] | None = None
    notification_channels: list[str] | None = None

class MetricSubmission(BaseModel):
    metric_type: MetricType
    value: float
    labels: dict[str, str] | None = None

class AlertAcknowledge(BaseModel):
    user_id: str

class AlertResolve(BaseModel):
    user_id: str

@router.get("/alerts", response_model=list[AlertResponse])
async def get_active_alerts(
    severity: AlertSeverity | None = Query(None, description="Filter by severity"),
    current_user: dict = Depends(get_current_user)
):
    """Get active alerts with optional severity filter"""
    try:
        alerts = alerting_service.get_active_alerts(severity)
        return [AlertResponse(**alert.__dict__) for alert in alerts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/history", response_model=list[AlertResponse])
async def get_alert_history(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of alerts to return"),
    current_user: dict = Depends(get_current_user)
):
    """Get alert history"""
    try:
        alerts = alerting_service.get_alert_history(limit)
        return [AlertResponse(**alert.__dict__) for alert in alerts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    request: AlertAcknowledge,
    current_user: dict = Depends(get_current_user)
):
    """Acknowledge an alert"""
    try:
        success = alerting_service.acknowledge_alert(alert_id, request.user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found or cannot be acknowledged")
        return {"message": "Alert acknowledged successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    request: AlertResolve,
    current_user: dict = Depends(get_current_user)
):
    """Manually resolve an alert"""
    try:
        success = alerting_service.resolve_alert(alert_id, request.user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found or cannot be resolved")
        return {"message": "Alert resolved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules", response_model=list[AlertRuleResponse])
async def get_alert_rules(
    current_user: dict = Depends(get_current_user)
):
    """Get all alert rules"""
    try:
        rules = list(alerting_service.alert_rules.values())
        return [AlertRuleResponse(**rule.__dict__) for rule in rules]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific alert rule"""
    try:
        rule = alerting_service.alert_rules.get(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        return AlertRuleResponse(**rule.__dict__)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rules", response_model=AlertRuleResponse)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new alert rule"""
    try:
        # Generate unique ID
        rule_id = f"rule_{datetime.now(UTC).timestamp()}"

        rule = AlertRule(
            id=rule_id,
            **rule_data.dict()
        )

        alerting_service.alert_rules[rule_id] = rule
        return AlertRuleResponse(**rule.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: str,
    rule_data: AlertRuleUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing alert rule"""
    try:
        rule = alerting_service.alert_rules.get(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")

        # Update fields that are provided
        update_data = rule_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        return AlertRuleResponse(**rule.__dict__)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/rules/{rule_id}")
async def delete_alert_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an alert rule"""
    try:
        if rule_id not in alerting_service.alert_rules:
            raise HTTPException(status_code=404, detail="Alert rule not found")

        del alerting_service.alert_rules[rule_id]
        return {"message": "Alert rule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics")
async def submit_metric(
    metric_data: MetricSubmission,
    current_user: dict = Depends(get_current_user)
):
    """Submit a metric value for monitoring"""
    try:
        alerting_service.add_metric(
            metric_type=metric_data.metric_type,
            value=metric_data.value,
            labels=metric_data.labels
        )
        return {"message": "Metric submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/summary")
async def get_metrics_summary(
    metric_type: MetricType | None = Query(None, description="Filter by metric type"),
    minutes: int = Query(60, ge=1, le=1440, description="Time window in minutes"),
    current_user: dict = Depends(get_current_user)
):
    """Get summary of recent metrics"""
    try:
        summary = alerting_service.get_metrics_summary(metric_type, minutes)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@limiter.limit(API_RATE_LIMIT)
@router.get("/health")
async def alerting_health(request: Request):
    """Health check for alerting service"""
    try:
        active_alerts = len(alerting_service.get_active_alerts())
        total_rules = len(alerting_service.alert_rules)
        metrics_count = len(alerting_service.metric_history)

        return {
            "status": "healthy",
            "active_alerts": active_alerts,
            "total_rules": total_rules,
            "metrics_count": metrics_count,
            "timestamp": datetime.now(UTC).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
