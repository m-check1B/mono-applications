"""
Metrics Collection Service

Service for collecting, storing, and querying metrics data.
Handles time-series data collection from various system components.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.analytics import Metric, MetricCreate, MetricType


class MetricsCollectorService:
    """
    Service for collecting and storing metrics

    Handles:
    - Metric ingestion from various sources
    - Batch metric processing
    - Real-time metric queries
    - Metric retention policies
    """

    def __init__(self, db: Session):
        self.db = db

    # ========================================================================
    # Metric Ingestion
    # ========================================================================

    def record_metric(
        self,
        metric_type: MetricType,
        metric_name: str,
        value: float,
        team_id: int | None = None,
        agent_id: int | None = None,
        campaign_id: int | None = None,
        call_id: int | None = None,
        unit: str | None = None,
        tags: dict[str, Any] | None = None,
        dimensions: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        timestamp: datetime | None = None
    ) -> Metric:
        """
        Record a single metric data point

        Args:
            metric_type: Type of metric (CALL, AGENT, CAMPAIGN, etc.)
            metric_name: Name of the metric
            value: Numeric value
            team_id: Team context (optional)
            agent_id: Agent context (optional)
            campaign_id: Campaign context (optional)
            call_id: Call context (optional)
            unit: Unit of measurement (optional)
            tags: Key-value tags for filtering
            dimensions: Dimensional data
            metadata: Additional metadata
            timestamp: Timestamp (defaults to now)

        Returns:
            Created Metric instance
        """
        metric = Metric(
            metric_type=metric_type.value,
            metric_name=metric_name,
            value=value,
            unit=unit,
            team_id=team_id,
            agent_id=agent_id,
            campaign_id=campaign_id,
            call_id=call_id,
            tags=tags or {},
            dimensions=dimensions or {},
            metadata=metadata or {},
            timestamp=timestamp or datetime.now(UTC)
        )

        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)

        return metric

    def record_metrics_batch(
        self,
        metrics: list[MetricCreate]
    ) -> list[Metric]:
        """
        Record multiple metrics in batch for efficiency

        Args:
            metrics: List of metric creation schemas

        Returns:
            List of created Metric instances
        """
        metric_objects = []

        for metric_data in metrics:
            metric = Metric(
                metric_type=metric_data.metric_type.value,
                metric_name=metric_data.metric_name,
                metric_category=metric_data.metric_category,
                value=metric_data.value,
                unit=metric_data.unit,
                team_id=metric_data.team_id,
                agent_id=metric_data.agent_id,
                campaign_id=metric_data.campaign_id,
                call_id=metric_data.call_id,
                tags=metric_data.tags,
                dimensions=metric_data.dimensions,
                metadata=metric_data.metadata,
                timestamp=metric_data.timestamp or datetime.now(UTC)
            )
            metric_objects.append(metric)

        self.db.bulk_save_objects(metric_objects, return_defaults=True)
        self.db.commit()

        return metric_objects

    # ========================================================================
    # Call Metrics
    # ========================================================================

    def record_call_duration(
        self,
        call_id: int,
        duration_seconds: float,
        team_id: int | None = None,
        agent_id: int | None = None,
        campaign_id: int | None = None
    ) -> Metric:
        """Record call duration metric"""
        return self.record_metric(
            metric_type=MetricType.CALL,
            metric_name="call_duration",
            value=duration_seconds,
            unit="seconds",
            call_id=call_id,
            team_id=team_id,
            agent_id=agent_id,
            campaign_id=campaign_id
        )

    def record_wait_time(
        self,
        wait_seconds: float,
        team_id: int | None = None,
        campaign_id: int | None = None
    ) -> Metric:
        """Record queue wait time metric"""
        return self.record_metric(
            metric_type=MetricType.CALL,
            metric_name="queue_wait_time",
            value=wait_seconds,
            unit="seconds",
            team_id=team_id,
            campaign_id=campaign_id
        )

    def record_call_outcome(
        self,
        outcome: str,
        call_id: int,
        team_id: int | None = None,
        agent_id: int | None = None,
        campaign_id: int | None = None
    ) -> Metric:
        """Record call outcome (answered, abandoned, etc.)"""
        return self.record_metric(
            metric_type=MetricType.CALL,
            metric_name="call_outcome",
            value=1.0,
            unit="count",
            call_id=call_id,
            team_id=team_id,
            agent_id=agent_id,
            campaign_id=campaign_id,
            tags={"outcome": outcome}
        )

    # ========================================================================
    # Agent Metrics
    # ========================================================================

    def record_agent_talk_time(
        self,
        agent_id: int,
        talk_seconds: float,
        team_id: int | None = None
    ) -> Metric:
        """Record agent talk time metric"""
        return self.record_metric(
            metric_type=MetricType.AGENT,
            metric_name="agent_talk_time",
            value=talk_seconds,
            unit="seconds",
            agent_id=agent_id,
            team_id=team_id
        )

    def record_agent_idle_time(
        self,
        agent_id: int,
        idle_seconds: float,
        team_id: int | None = None
    ) -> Metric:
        """Record agent idle time metric"""
        return self.record_metric(
            metric_type=MetricType.AGENT,
            metric_name="agent_idle_time",
            value=idle_seconds,
            unit="seconds",
            agent_id=agent_id,
            team_id=team_id
        )

    def record_agent_status_change(
        self,
        agent_id: int,
        from_status: str,
        to_status: str,
        team_id: int | None = None
    ) -> Metric:
        """Record agent status change"""
        return self.record_metric(
            metric_type=MetricType.AGENT,
            metric_name="agent_status_change",
            value=1.0,
            unit="count",
            agent_id=agent_id,
            team_id=team_id,
            tags={"from_status": from_status, "to_status": to_status}
        )

    # ========================================================================
    # Campaign Metrics
    # ========================================================================

    def record_campaign_call_count(
        self,
        campaign_id: int,
        count: int = 1,
        team_id: int | None = None
    ) -> Metric:
        """Record campaign call count"""
        return self.record_metric(
            metric_type=MetricType.CAMPAIGN,
            metric_name="campaign_calls",
            value=float(count),
            unit="count",
            campaign_id=campaign_id,
            team_id=team_id
        )

    def record_campaign_conversion(
        self,
        campaign_id: int,
        converted: bool,
        team_id: int | None = None
    ) -> Metric:
        """Record campaign conversion"""
        return self.record_metric(
            metric_type=MetricType.CAMPAIGN,
            metric_name="campaign_conversion",
            value=1.0 if converted else 0.0,
            unit="boolean",
            campaign_id=campaign_id,
            team_id=team_id
        )

    # ========================================================================
    # System Metrics
    # ========================================================================

    def record_api_latency(
        self,
        endpoint: str,
        latency_ms: float,
        status_code: int
    ) -> Metric:
        """Record API endpoint latency"""
        return self.record_metric(
            metric_type=MetricType.SYSTEM,
            metric_name="api_latency",
            value=latency_ms,
            unit="milliseconds",
            tags={"endpoint": endpoint, "status_code": str(status_code)}
        )

    def record_error_count(
        self,
        error_type: str,
        service: str
    ) -> Metric:
        """Record system error"""
        return self.record_metric(
            metric_type=MetricType.SYSTEM,
            metric_name="error_count",
            value=1.0,
            unit="count",
            tags={"error_type": error_type, "service": service}
        )

    # ========================================================================
    # Metric Queries
    # ========================================================================

    def get_metrics(
        self,
        metric_type: MetricType | None = None,
        metric_name: str | None = None,
        team_id: int | None = None,
        agent_id: int | None = None,
        campaign_id: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 1000
    ) -> list[Metric]:
        """
        Query metrics with filters

        Args:
            metric_type: Filter by metric type
            metric_name: Filter by metric name
            team_id: Filter by team
            agent_id: Filter by agent
            campaign_id: Filter by campaign
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum number of results

        Returns:
            List of matching metrics
        """
        query = self.db.query(Metric).filter(Metric.is_deleted == False)

        if metric_type:
            query = query.filter(Metric.metric_type == metric_type.value)
        if metric_name:
            query = query.filter(Metric.metric_name == metric_name)
        if team_id:
            query = query.filter(Metric.team_id == team_id)
        if agent_id:
            query = query.filter(Metric.agent_id == agent_id)
        if campaign_id:
            query = query.filter(Metric.campaign_id == campaign_id)
        if start_time:
            query = query.filter(Metric.timestamp >= start_time)
        if end_time:
            query = query.filter(Metric.timestamp <= end_time)

        return query.order_by(desc(Metric.timestamp)).limit(limit).all()

    def get_metric_statistics(
        self,
        metric_name: str,
        team_id: int | None = None,
        agent_id: int | None = None,
        campaign_id: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None
    ) -> dict[str, Any]:
        """
        Calculate statistics for a specific metric

        Returns:
            Dictionary with min, max, avg, sum, count
        """
        query = self.db.query(
            func.min(Metric.value).label('min'),
            func.max(Metric.value).label('max'),
            func.avg(Metric.value).label('avg'),
            func.sum(Metric.value).label('sum'),
            func.count(Metric.id).label('count')
        ).filter(
            Metric.metric_name == metric_name,
            Metric.is_deleted == False
        )

        if team_id:
            query = query.filter(Metric.team_id == team_id)
        if agent_id:
            query = query.filter(Metric.agent_id == agent_id)
        if campaign_id:
            query = query.filter(Metric.campaign_id == campaign_id)
        if start_time:
            query = query.filter(Metric.timestamp >= start_time)
        if end_time:
            query = query.filter(Metric.timestamp <= end_time)

        result = query.first()

        return {
            "min": float(result.min) if result.min else 0,
            "max": float(result.max) if result.max else 0,
            "avg": float(result.avg) if result.avg else 0,
            "sum": float(result.sum) if result.sum else 0,
            "count": result.count or 0
        }

    # ========================================================================
    # Metric Cleanup
    # ========================================================================

    def cleanup_old_metrics(
        self,
        retention_days: int = 90
    ) -> int:
        """
        Delete metrics older than retention period

        Args:
            retention_days: Number of days to retain metrics

        Returns:
            Number of metrics deleted
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)

        deleted_count = self.db.query(Metric).filter(
            Metric.timestamp < cutoff_date,
            Metric.is_deleted == False
        ).update({
            "is_deleted": True,
            "deleted_at": datetime.now(UTC)
        })

        self.db.commit()

        return deleted_count
