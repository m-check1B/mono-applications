"""
Analytics API Endpoints

REST API for metrics, analytics, aggregations, and alerts.
"""

from datetime import UTC, datetime, timedelta

from app.database import get_db
from app.models.analytics import (
    AggregationType,
    AlertStatus,
    MetricAggregation,
    MetricAggregationResponse,
    MetricCreate,
    MetricResponse,
    MetricThreshold,
    MetricThresholdCreate,
    MetricThresholdResponse,
    MetricType,
    PerformanceAlert,
    PerformanceAlertResponse,
    TimeGranularity,
)
from app.services.analytics import AggregationService
from app.services.metrics import MetricsCollectorService
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# ============================================================================
# Metrics Endpoints
# ============================================================================

@router.post("/metrics", response_model=MetricResponse)
def create_metric(
    metric: MetricCreate,
    db: Session = Depends(get_db)
):
    """Record a new metric data point"""
    service = MetricsCollectorService(db)
    return service.record_metric(
        metric_type=metric.metric_type,
        metric_name=metric.metric_name,
        value=metric.value,
        unit=metric.unit,
        team_id=metric.team_id,
        agent_id=metric.agent_id,
        campaign_id=metric.campaign_id,
        call_id=metric.call_id,
        tags=metric.tags,
        dimensions=metric.dimensions,
        metadata=metric.metadata,
        timestamp=metric.timestamp
    )


@router.post("/metrics/batch", response_model=list[MetricResponse])
def create_metrics_batch(
    metrics: list[MetricCreate],
    db: Session = Depends(get_db)
):
    """Record multiple metrics in batch"""
    service = MetricsCollectorService(db)
    return service.record_metrics_batch(metrics)


@router.get("/metrics", response_model=list[MetricResponse])
def get_metrics(
    metric_type: str | None = None,
    metric_name: str | None = None,
    team_id: int | None = None,
    agent_id: int | None = None,
    campaign_id: int | None = None,
    start_time: datetime | None = Query(None),
    end_time: datetime | None = Query(None),
    limit: int = Query(1000, le=10000),
    db: Session = Depends(get_db)
):
    """Query metrics with filters"""
    service = MetricsCollectorService(db)

    metric_type_enum = MetricType(metric_type) if metric_type else None

    return service.get_metrics(
        metric_type=metric_type_enum,
        metric_name=metric_name,
        team_id=team_id,
        agent_id=agent_id,
        campaign_id=campaign_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )


@router.get("/metrics/{metric_name}/statistics")
def get_metric_statistics(
    metric_name: str,
    team_id: int | None = None,
    agent_id: int | None = None,
    campaign_id: int | None = None,
    start_time: datetime | None = Query(None),
    end_time: datetime | None = Query(None),
    db: Session = Depends(get_db)
):
    """Get statistics for a specific metric"""
    service = MetricsCollectorService(db)

    return service.get_metric_statistics(
        metric_name=metric_name,
        team_id=team_id,
        agent_id=agent_id,
        campaign_id=campaign_id,
        start_time=start_time,
        end_time=end_time
    )


# ============================================================================
# Aggregations Endpoints
# ============================================================================

@router.post("/aggregations", response_model=list[MetricAggregationResponse])
def compute_aggregation(
    metric_name: str,
    aggregation_type: AggregationType,
    granularity: TimeGranularity,
    start_time: datetime,
    end_time: datetime,
    team_id: int | None = None,
    agent_id: int | None = None,
    campaign_id: int | None = None,
    db: Session = Depends(get_db)
):
    """Compute metric aggregations"""
    service = AggregationService(db)

    return service.compute_aggregation(
        metric_name=metric_name,
        aggregation_type=aggregation_type,
        granularity=granularity,
        start_time=start_time,
        end_time=end_time,
        team_id=team_id,
        agent_id=agent_id,
        campaign_id=campaign_id
    )


@router.get("/aggregations", response_model=list[MetricAggregationResponse])
def get_aggregations(
    metric_name: str | None = None,
    granularity: str | None = None,
    team_id: int | None = None,
    start_time: datetime | None = Query(None),
    end_time: datetime | None = Query(None),
    limit: int = Query(1000, le=10000),
    db: Session = Depends(get_db)
):
    """Query pre-computed aggregations"""
    query = db.query(MetricAggregation)

    if metric_name:
        query = query.filter(MetricAggregation.metric_name == metric_name)
    if granularity:
        query = query.filter(MetricAggregation.granularity == granularity)
    if team_id:
        query = query.filter(MetricAggregation.team_id == team_id)
    if start_time:
        query = query.filter(MetricAggregation.window_start >= start_time)
    if end_time:
        query = query.filter(MetricAggregation.window_end <= end_time)

    return query.order_by(MetricAggregation.window_start.desc()).limit(limit).all()


# ============================================================================
# Alerts Endpoints
# ============================================================================

@router.get("/alerts", response_model=list[PerformanceAlertResponse])
def get_alerts(
    status: str | None = None,
    severity: str | None = None,
    team_id: int | None = None,
    agent_id: int | None = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get performance alerts"""
    query = db.query(PerformanceAlert)

    if status:
        query = query.filter(PerformanceAlert.status == status)
    if severity:
        query = query.filter(PerformanceAlert.severity == severity)
    if team_id:
        query = query.filter(PerformanceAlert.team_id == team_id)
    if agent_id:
        query = query.filter(PerformanceAlert.agent_id == agent_id)

    return query.order_by(PerformanceAlert.triggered_at.desc()).limit(limit).all()


@router.put("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    acknowledged_by_id: int,
    db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    alert = db.query(PerformanceAlert).filter(PerformanceAlert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = AlertStatus.ACKNOWLEDGED.value
    alert.acknowledged_at = datetime.now(UTC)
    alert.acknowledged_by_id = acknowledged_by_id

    db.commit()
    db.refresh(alert)

    return alert


@router.put("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    resolved_by_id: int,
    db: Session = Depends(get_db)
):
    """Resolve an alert"""
    alert = db.query(PerformanceAlert).filter(PerformanceAlert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = AlertStatus.RESOLVED.value
    alert.resolved_at = datetime.now(UTC)
    alert.resolved_by_id = resolved_by_id

    db.commit()
    db.refresh(alert)

    return alert


# ============================================================================
# Thresholds Endpoints
# ============================================================================

@router.post("/thresholds", response_model=MetricThresholdResponse)
def create_threshold(
    threshold: MetricThresholdCreate,
    db: Session = Depends(get_db)
):
    """Create a metric threshold for alerting"""
    db_threshold = MetricThreshold(
        name=threshold.name,
        description=threshold.description,
        metric_type=threshold.metric_type.value,
        metric_name=threshold.metric_name,
        threshold_value=threshold.threshold_value,
        operator=threshold.operator,
        severity=threshold.severity.value,
        team_id=threshold.team_id,
        campaign_id=threshold.campaign_id,
        notification_channels=threshold.notification_channels,
        notification_recipients=threshold.notification_recipients,
        cooldown_minutes=threshold.cooldown_minutes
    )

    db.add(db_threshold)
    db.commit()
    db.refresh(db_threshold)

    return db_threshold


@router.get("/thresholds", response_model=list[MetricThresholdResponse])
def get_thresholds(
    is_active: bool | None = None,
    metric_name: str | None = None,
    team_id: int | None = None,
    db: Session = Depends(get_db)
):
    """Get metric thresholds"""
    query = db.query(MetricThreshold)

    if is_active is not None:
        query = query.filter(MetricThreshold.is_active == is_active)
    if metric_name:
        query = query.filter(MetricThreshold.metric_name == metric_name)
    if team_id:
        query = query.filter(MetricThreshold.team_id == team_id)

    return query.all()


@router.put("/thresholds/{threshold_id}")
def update_threshold(
    threshold_id: int,
    threshold: MetricThresholdCreate,
    db: Session = Depends(get_db)
):
    """Update a metric threshold"""
    db_threshold = db.query(MetricThreshold).filter(
        MetricThreshold.id == threshold_id
    ).first()

    if not db_threshold:
        raise HTTPException(status_code=404, detail="Threshold not found")

    db_threshold.name = threshold.name
    db_threshold.description = threshold.description
    db_threshold.threshold_value = threshold.threshold_value
    db_threshold.operator = threshold.operator
    db_threshold.severity = threshold.severity.value
    db_threshold.notification_channels = threshold.notification_channels
    db_threshold.notification_recipients = threshold.notification_recipients
    db_threshold.cooldown_minutes = threshold.cooldown_minutes
    db_threshold.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(db_threshold)

    return db_threshold


@router.delete("/thresholds/{threshold_id}")
def delete_threshold(
    threshold_id: int,
    db: Session = Depends(get_db)
):
    """Delete a metric threshold"""
    db_threshold = db.query(MetricThreshold).filter(
        MetricThreshold.id == threshold_id
    ).first()

    if not db_threshold:
        raise HTTPException(status_code=404, detail="Threshold not found")

    db.delete(db_threshold)
    db.commit()

    return {"status": "deleted", "id": threshold_id}


# ============================================================================
# Dashboard/Overview Endpoints
# ============================================================================

@router.get("/dashboard/overview")
def get_dashboard_overview(
    team_id: int | None = None,
    period_hours: int = Query(24, le=168),  # Max 1 week
    db: Session = Depends(get_db)
):
    """Get analytics dashboard overview"""
    service = MetricsCollectorService(db)

    start_time = datetime.now(UTC) - timedelta(hours=period_hours)
    end_time = datetime.now(UTC)

    # Get key metrics
    call_stats = service.get_metric_statistics(
        "call_duration",
        team_id=team_id,
        start_time=start_time,
        end_time=end_time
    )

    wait_stats = service.get_metric_statistics(
        "queue_wait_time",
        team_id=team_id,
        start_time=start_time,
        end_time=end_time
    )

    # Get active alerts
    active_alerts = db.query(PerformanceAlert).filter(
        PerformanceAlert.status == AlertStatus.ACTIVE.value
    )
    if team_id:
        active_alerts = active_alerts.filter(PerformanceAlert.team_id == team_id)

    return {
        "period": {
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "hours": period_hours
        },
        "call_metrics": {
            "total_calls": call_stats["count"],
            "avg_duration": call_stats["avg"],
            "max_duration": call_stats["max"],
            "min_duration": call_stats["min"]
        },
        "queue_metrics": {
            "avg_wait_time": wait_stats["avg"],
            "max_wait_time": wait_stats["max"]
        },
        "alerts": {
            "active_count": active_alerts.count(),
            "critical_count": active_alerts.filter(
                PerformanceAlert.severity == "critical"
            ).count()
        }
    }
