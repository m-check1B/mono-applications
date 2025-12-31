"""
Proactive Alerting Service

Monitors call quality, drop rates, webhook failures, and other
telephony metrics to provide proactive alerts and notifications.
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    """Alert status values"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class MetricType(str, Enum):
    """Types of metrics that can trigger alerts"""
    CALL_DROP_RATE = "call_drop_rate"
    CALL_QUALITY = "call_quality"
    WEBHOOK_FAILURE_RATE = "webhook_failure_rate"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    PROVIDER_HEALTH = "provider_health"
    SYSTEM_RESOURCE = "system_resource"

@dataclass
class AlertRule:
    """Rule configuration for triggering alerts"""
    id: str
    name: str
    description: str
    metric_type: MetricType
    severity: AlertSeverity
    threshold: float
    operator: str  # gt, lt, eq, gte, lte
    duration_minutes: int  # How long condition must persist
    enabled: bool = True
    tags: dict[str, str] | None = None
    notification_channels: list[str] | None = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.notification_channels is None:
            self.notification_channels = []

@dataclass
class Alert:
    """Active alert instance"""
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

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MetricValue:
    """Metric value with timestamp"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    labels: dict[str, str] | None = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = {}

class AlertingService:
    """Service for proactive monitoring and alerting"""

    def __init__(self):
        self.alert_rules: dict[str, AlertRule] = {}
        self.active_alerts: dict[str, Alert] = {}
        self.metric_history: list[MetricValue] = []
        self.notification_handlers: dict[str, Callable] = {}
        self._running = False
        self._monitor_task: asyncio.Task | None = None

        # Initialize default alert rules
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize default alert rules for telephony monitoring"""

        # Call drop rate alert
        self.alert_rules["call_drop_rate_high"] = AlertRule(
            id="call_drop_rate_high",
            name="High Call Drop Rate",
            description="Alert when call drop rate exceeds 5%",
            metric_type=MetricType.CALL_DROP_RATE,
            severity=AlertSeverity.HIGH,
            threshold=5.0,
            operator="gt",
            duration_minutes=5,
            tags={"category": "call_quality"},
            notification_channels=["email", "slack"]
        )

        # Call quality alert
        self.alert_rules["call_quality_poor"] = AlertRule(
            id="call_quality_poor",
            name="Poor Call Quality",
            description="Alert when call quality score drops below 3.0",
            metric_type=MetricType.CALL_QUALITY,
            severity=AlertSeverity.MEDIUM,
            threshold=3.0,
            operator="lt",
            duration_minutes=3,
            tags={"category": "call_quality"},
            notification_channels=["email"]
        )

        # Webhook failure rate alert
        self.alert_rules["webhook_failure_rate_high"] = AlertRule(
            id="webhook_failure_rate_high",
            name="High Webhook Failure Rate",
            description="Alert when webhook failure rate exceeds 10%",
            metric_type=MetricType.WEBHOOK_FAILURE_RATE,
            severity=AlertSeverity.HIGH,
            threshold=10.0,
            operator="gt",
            duration_minutes=2,
            tags={"category": "webhook"},
            notification_channels=["email", "slack"]
        )

        # Response time alert
        self.alert_rules["response_time_slow"] = AlertRule(
            id="response_time_slow",
            name="Slow Response Time",
            description="Alert when API response time exceeds 2 seconds",
            metric_type=MetricType.RESPONSE_TIME,
            severity=AlertSeverity.MEDIUM,
            threshold=2000.0,  # milliseconds
            operator="gt",
            duration_minutes=5,
            tags={"category": "performance"},
            notification_channels=["email"]
        )

        # Error rate alert
        self.alert_rules["error_rate_high"] = AlertRule(
            id="error_rate_high",
            name="High Error Rate",
            description="Alert when error rate exceeds 5%",
            metric_type=MetricType.ERROR_RATE,
            severity=AlertSeverity.HIGH,
            threshold=5.0,
            operator="gt",
            duration_minutes=3,
            tags={"category": "errors"},
            notification_channels=["email", "slack"]
        )

        # Provider health alert
        self.alert_rules["provider_unhealthy"] = AlertRule(
            id="provider_unhealthy",
            name="Provider Unhealthy",
            description="Alert when provider health score drops below 70%",
            metric_type=MetricType.PROVIDER_HEALTH,
            severity=AlertSeverity.CRITICAL,
            threshold=70.0,
            operator="lt",
            duration_minutes=1,
            tags={"category": "provider"},
            notification_channels=["email", "slack", "pagerduty"]
        )

    def add_metric(self, metric_type: MetricType, value: float,
                   labels: dict[str, str] | None = None):
        """Add a metric value for monitoring"""
        metric = MetricValue(
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(UTC),
            labels=labels or {}
        )

        self.metric_history.append(metric)

        # Keep only recent metrics (last 10000)
        if len(self.metric_history) > 10000:
            self.metric_history = self.metric_history[-10000:]

        # Check if this metric triggers any alerts
        self._check_metric_against_rules(metric)

    def _check_metric_against_rules(self, metric: MetricValue):
        """Check if a metric value triggers any alert rules"""
        for rule in self.alert_rules.values():
            if not rule.enabled or rule.metric_type != metric.metric_type:
                continue

            # Check if threshold condition is met
            if self._evaluate_condition(metric.value, rule.operator, rule.threshold):
                # Check if condition has persisted for required duration
                if self._check_condition_duration(metric, rule):
                    self._trigger_alert(rule, metric)
            else:
                # Check if we should resolve an existing alert
                self._check_alert_resolution(rule, metric)

    def _evaluate_condition(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluate if a value meets the threshold condition"""
        if operator == "gt":
            return value > threshold
        elif operator == "gte":
            return value >= threshold
        elif operator == "lt":
            return value < threshold
        elif operator == "lte":
            return value <= threshold
        elif operator == "eq":
            return value == threshold
        else:
            return False

    def _check_condition_duration(self, metric: MetricValue, rule: AlertRule) -> bool:
        """Check if condition has persisted for required duration"""
        cutoff_time = datetime.now(UTC) - timedelta(minutes=rule.duration_minutes)

        # Get recent metrics of the same type
        recent_metrics = [
            m for m in self.metric_history
            if (m.metric_type == metric.metric_type and
                m.timestamp >= cutoff_time and
                self._evaluate_condition(m.value, rule.operator, rule.threshold))
        ]

        # Need at least some data points to confirm persistence
        return len(recent_metrics) >= max(2, rule.duration_minutes)

    def _trigger_alert(self, rule: AlertRule, metric: MetricValue):
        """Trigger an alert for a rule"""
        alert_id = f"{rule.id}_{metric.metric_type.value}"

        # Check if alert already exists
        if alert_id in self.active_alerts:
            existing_alert = self.active_alerts[alert_id]
            if existing_alert.status == AlertStatus.ACTIVE:
                return  # Alert already active

        # Create new alert
        alert = Alert(
            id=alert_id,
            rule_id=rule.id,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            title=rule.name,
            description=f"{rule.description}. Current value: {metric.value:.2f}",
            metric_value=metric.value,
            threshold=rule.threshold,
            triggered_at=datetime.now(UTC),
            metadata={
                "metric_type": metric.metric_type.value,
                "labels": metric.labels,
                "rule_tags": rule.tags
            }
        )

        self.active_alerts[alert_id] = alert

        # Send notifications
        self._send_notifications(alert, rule.notification_channels)

        logger.warning(f"Alert triggered: {alert.title} - {alert.description}")

    def _check_alert_resolution(self, rule: AlertRule, metric: MetricValue):
        """Check if any active alerts should be resolved"""
        alert_id = f"{rule.id}_{metric.metric_type.value}"

        if alert_id not in self.active_alerts:
            return

        alert = self.active_alerts[alert_id]
        if alert.status != AlertStatus.ACTIVE:
            return

        # Check if condition has been resolved for sufficient time
        cutoff_time = datetime.now(UTC) - timedelta(minutes=2)

        recent_metrics = [
            m for m in self.metric_history
            if (m.metric_type == metric.metric_type and
                m.timestamp >= cutoff_time and
                not self._evaluate_condition(m.value, rule.operator, rule.threshold))
        ]

        if len(recent_metrics) >= 3:  # Condition resolved for 2+ minutes
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now(UTC)

            # Send resolution notification
            self._send_notifications(alert, rule.notification_channels, is_resolution=True)

            logger.info(f"Alert resolved: {alert.title}")

    def _send_notifications(self, alert: Alert, channels: list[str] | None, is_resolution: bool = False):
        """Send alert notifications through configured channels"""
        if not channels:
            return

        for channel in channels:
            handler = self.notification_handlers.get(channel)
            if handler:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(alert, is_resolution))
                    else:
                        handler(alert, is_resolution)
                except Exception as e:
                    logger.error(f"Failed to send {channel} notification: {e}")

    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        if alert.status != AlertStatus.ACTIVE:
            return False

        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now(UTC)
        if alert.metadata:
            alert.metadata["acknowledged_by"] = user_id

        logger.info(f"Alert acknowledged: {alert.title} by {user_id}")
        return True

    def resolve_alert(self, alert_id: str, user_id: str) -> bool:
        """Manually resolve an alert"""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        if alert.status in [AlertStatus.RESOLVED, AlertStatus.SUPPRESSED]:
            return False

        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now(UTC)
        if alert.metadata:
            alert.metadata["resolved_by"] = user_id

        logger.info(f"Alert resolved: {alert.title} by {user_id}")
        return True

    def get_active_alerts(self, severity: AlertSeverity | None = None) -> list[Alert]:
        """Get active alerts with optional severity filter"""
        alerts = [
            alert for alert in self.active_alerts.values()
            if alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]
        ]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return sorted(alerts, key=lambda x: x.triggered_at, reverse=True)

    def get_alert_history(self, limit: int = 100) -> list[Alert]:
        """Get alert history"""
        all_alerts = list(self.active_alerts.values())
        return sorted(all_alerts, key=lambda x: x.triggered_at, reverse=True)[:limit]

    def get_metrics_summary(self, metric_type: MetricType | None = None,
                           minutes: int = 60) -> dict[str, Any]:
        """Get summary of recent metrics"""
        cutoff_time = datetime.now(UTC) - timedelta(minutes=minutes)

        recent_metrics = [
            m for m in self.metric_history
            if m.timestamp >= cutoff_time and
            (metric_type is None or m.metric_type == metric_type)
        ]

        if not recent_metrics:
            return {"count": 0, "avg": 0, "min": 0, "max": 0}

        values = [m.value for m in recent_metrics]

        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "latest": values[-1] if values else 0
        }

    def register_notification_handler(self, channel: str, handler: Callable):
        """Register a notification handler for a channel"""
        self.notification_handlers[channel] = handler

    # Default notification handlers
    @staticmethod
    def email_notification_handler(alert: Alert, is_resolution: bool = False):
        """Default email notification handler (placeholder)"""
        status = "RESOLVED" if is_resolution else "TRIGGERED"
        logger.info(f"EMAIL NOTIFICATION: {status} - {alert.title}: {alert.description}")

    @staticmethod
    def slack_notification_handler(alert: Alert, is_resolution: bool = False):
        """Default Slack notification handler (placeholder)"""
        status = "RESOLVED" if is_resolution else "TRIGGERED"
        logger.info(f"SLACK NOTIFICATION: {status} - {alert.title}: {alert.description}")

    @staticmethod
    def pagerduty_notification_handler(alert: Alert, is_resolution: bool = False):
        """Default PagerDuty notification handler (placeholder)"""
        if not is_resolution and alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            logger.info(f"PAGERDUTY ALERT: {alert.title}: {alert.description}")

# Global instance
alerting_service = AlertingService()

# Register default notification handlers
alerting_service.register_notification_handler("email", AlertingService.email_notification_handler)
alerting_service.register_notification_handler("slack", AlertingService.slack_notification_handler)
alerting_service.register_notification_handler("pagerduty", AlertingService.pagerduty_notification_handler)
