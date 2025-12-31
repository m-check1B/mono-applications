"""
Analytics and Aggregation Services

Comprehensive analytics services for metrics aggregation, trend analysis,
alerting, and report generation.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.analytics import (
    AggregationType,
    AlertStatus,
    Metric,
    MetricAggregation,
    MetricThreshold,
    PerformanceAlert,
    TimeGranularity,
)
from app.models.report import Report, ReportFormat, ReportStatus, ReportTemplate


class AggregationService:
    """Service for computing metric aggregations"""

    def __init__(self, db: Session):
        self.db = db

    def compute_aggregation(
        self,
        metric_name: str,
        aggregation_type: AggregationType,
        granularity: TimeGranularity,
        start_time: datetime,
        end_time: datetime,
        team_id: int | None = None,
        agent_id: int | None = None,
        campaign_id: int | None = None
    ) -> list[MetricAggregation]:
        """Compute and store metric aggregations"""

        # Determine time buckets based on granularity
        buckets = self._generate_time_buckets(start_time, end_time, granularity)

        aggregations = []
        for window_start, window_end in buckets:
            # Query metrics in this window
            query = self.db.query(Metric).filter(
                Metric.metric_name == metric_name,
                Metric.timestamp >= window_start,
                Metric.timestamp < window_end,
                Metric.is_deleted == False
            )

            if team_id:
                query = query.filter(Metric.team_id == team_id)
            if agent_id:
                query = query.filter(Metric.agent_id == agent_id)
            if campaign_id:
                query = query.filter(Metric.campaign_id == campaign_id)

            # Compute aggregation
            values = [m.value for m in query.all()]

            if not values:
                continue

            agg_value = self._compute_value(values, aggregation_type)

            agg = MetricAggregation(
                metric_name=metric_name,
                metric_type="computed",
                aggregation_type=aggregation_type.value,
                granularity=granularity.value,
                value=agg_value,
                count=len(values),
                min_value=min(values),
                max_value=max(values),
                window_start=window_start,
                window_end=window_end,
                team_id=team_id,
                agent_id=agent_id,
                campaign_id=campaign_id
            )

            self.db.add(agg)
            aggregations.append(agg)

        self.db.commit()
        return aggregations

    def _generate_time_buckets(
        self,
        start: datetime,
        end: datetime,
        granularity: TimeGranularity
    ) -> list[tuple]:
        """Generate time buckets based on granularity"""
        buckets = []
        current = start

        delta_map = {
            TimeGranularity.MINUTE: timedelta(minutes=1),
            TimeGranularity.HOUR: timedelta(hours=1),
            TimeGranularity.DAY: timedelta(days=1),
            TimeGranularity.WEEK: timedelta(weeks=1),
            TimeGranularity.MONTH: timedelta(days=30),  # Approximation
        }

        delta = delta_map.get(granularity, timedelta(hours=1))

        while current < end:
            bucket_end = min(current + delta, end)
            buckets.append((current, bucket_end))
            current = bucket_end

        return buckets

    def _compute_value(self, values: list[float], agg_type: AggregationType) -> float:
        """Compute aggregation value"""
        if agg_type == AggregationType.SUM:
            return sum(values)
        elif agg_type == AggregationType.AVERAGE:
            return sum(values) / len(values)
        elif agg_type == AggregationType.MIN:
            return min(values)
        elif agg_type == AggregationType.MAX:
            return max(values)
        elif agg_type == AggregationType.COUNT:
            return len(values)
        elif agg_type == AggregationType.MEDIAN:
            sorted_values = sorted(values)
            n = len(sorted_values)
            return sorted_values[n // 2]
        return 0.0


class AlertingService:
    """Service for managing performance alerts and thresholds"""

    def __init__(self, db: Session):
        self.db = db

    def evaluate_thresholds(self, metric: Metric) -> list[PerformanceAlert]:
        """Evaluate metric against active thresholds"""

        # Find matching thresholds
        thresholds = self.db.query(MetricThreshold).filter(
            MetricThreshold.is_active == True,
            MetricThreshold.metric_name == metric.metric_name
        )

        if metric.team_id:
            thresholds = thresholds.filter(
                or_(MetricThreshold.team_id == metric.team_id, MetricThreshold.team_id == None)
            )

        alerts = []
        for threshold in thresholds.all():
            if self._check_threshold_violation(metric.value, threshold):
                alert = self._create_alert(metric, threshold)
                alerts.append(alert)

        return alerts

    def _check_threshold_violation(self, value: float, threshold: MetricThreshold) -> bool:
        """Check if value violates threshold"""
        if threshold.operator == "gt":
            return value > threshold.threshold_value
        elif threshold.operator == "lt":
            return value < threshold.threshold_value
        elif threshold.operator == "gte":
            return value >= threshold.threshold_value
        elif threshold.operator == "lte":
            return value <= threshold.threshold_value
        elif threshold.operator == "eq":
            return value == threshold.threshold_value
        return False

    def _create_alert(self, metric: Metric, threshold: MetricThreshold) -> PerformanceAlert:
        """Create a performance alert"""
        alert = PerformanceAlert(
            alert_type="threshold_violation",
            alert_name=threshold.name,
            severity=threshold.severity,
            status=AlertStatus.ACTIVE.value,
            metric_type=metric.metric_type,
            metric_name=metric.metric_name,
            threshold_value=threshold.threshold_value,
            actual_value=metric.value,
            threshold_operator=threshold.operator,
            message=f"{threshold.name}: {metric.metric_name} = {metric.value} (threshold: {threshold.threshold_value})",
            team_id=metric.team_id,
            agent_id=metric.agent_id,
            campaign_id=metric.campaign_id
        )

        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        return alert


class ReportGeneratorService:
    """Service for generating reports"""

    def __init__(self, db: Session):
        self.db = db

    def generate_report(
        self,
        template_id: int,
        filters: dict[str, Any],
        format: ReportFormat = ReportFormat.PDF,
        requested_by_id: int | None = None
    ) -> Report:
        """Generate a report from template"""

        template = self.db.query(ReportTemplate).filter(
            ReportTemplate.id == template_id
        ).first()

        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Create report record
        report = Report(
            name=f"{template.name} - {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')}",
            report_type=template.report_type,
            template_id=template_id,
            status=ReportStatus.GENERATING.value,
            format=format.value,
            filters=filters,
            requested_by_id=requested_by_id,
            requested_at=datetime.now(UTC),
            started_at=datetime.now(UTC)
        )

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        # Generate report data
        try:
            report_data = self._generate_report_data(template, filters)

            report.report_data = report_data
            report.summary = self._generate_summary(report_data)
            report.status = ReportStatus.COMPLETED.value
            report.completed_at = datetime.now(UTC)

        except Exception as e:
            report.status = ReportStatus.FAILED.value
            report.error_message = str(e)

        self.db.commit()
        self.db.refresh(report)

        return report

    def _generate_report_data(
        self,
        template: ReportTemplate,
        filters: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate report data based on template configuration"""

        # Extract date range from filters
        start_date = filters.get("start_date", datetime.now(UTC) - timedelta(days=7))
        end_date = filters.get("end_date", datetime.now(UTC))
        team_id = filters.get("team_id")

        # Query metrics based on report type
        data = {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "sections": []
        }

        # Add call metrics section
        call_metrics = self._get_call_metrics(start_date, end_date, team_id)
        data["sections"].append({
            "title": "Call Metrics",
            "data": call_metrics
        })

        # Add agent metrics section
        agent_metrics = self._get_agent_metrics(start_date, end_date, team_id)
        data["sections"].append({
            "title": "Agent Performance",
            "data": agent_metrics
        })

        return data

    def _get_call_metrics(
        self,
        start: datetime,
        end: datetime,
        team_id: int | None
    ) -> dict[str, Any]:
        """Get call metrics for period"""

        query = self.db.query(Metric).filter(
            Metric.metric_type == "call",
            Metric.timestamp >= start,
            Metric.timestamp <= end,
            Metric.is_deleted == False
        )

        if team_id:
            query = query.filter(Metric.team_id == team_id)

        metrics = query.all()

        return {
            "total_calls": len(metrics),
            "avg_duration": sum(m.value for m in metrics if m.metric_name == "call_duration") / max(len([m for m in metrics if m.metric_name == "call_duration"]), 1)
        }

    def _get_agent_metrics(
        self,
        start: datetime,
        end: datetime,
        team_id: int | None
    ) -> dict[str, Any]:
        """Get agent metrics for period"""

        query = self.db.query(Metric).filter(
            Metric.metric_type == "agent",
            Metric.timestamp >= start,
            Metric.timestamp <= end,
            Metric.is_deleted == False
        )

        if team_id:
            query = query.filter(Metric.team_id == team_id)

        metrics = query.all()

        return {
            "active_agents": len(set(m.agent_id for m in metrics if m.agent_id)),
            "total_talk_time": sum(m.value for m in metrics if m.metric_name == "agent_talk_time")
        }

    def _generate_summary(self, report_data: dict[str, Any]) -> dict[str, Any]:
        """Generate executive summary from report data"""
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "sections_count": len(report_data.get("sections", [])),
            "period": report_data.get("period", {})
        }
