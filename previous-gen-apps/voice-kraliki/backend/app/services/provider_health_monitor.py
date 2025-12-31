"""Provider Health Monitor Service

Monitors the health and performance of all voice/AI providers:
- Real-time health checks
- Latency tracking
- Error rate monitoring
- Automatic failover detection
- Historical metrics
"""

import asyncio
import logging
import time
from datetime import UTC, datetime, timedelta
from enum import Enum

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProviderStatus(str, Enum):
    """Provider health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class ProviderType(str, Enum):
    """Supported provider types."""
    GEMINI = "gemini"
    OPENAI = "openai"
    DEEPGRAM = "deepgram_nova3"
    TWILIO = "twilio"
    TELNYX = "telnyx"


class HealthCheckResult(BaseModel):
    """Result of a provider health check."""
    provider_id: str
    provider_type: ProviderType
    status: ProviderStatus
    latency_ms: float
    timestamp: datetime
    error_message: str | None = None
    response_time: float  # seconds
    success: bool


class ProviderMetrics(BaseModel):
    """Aggregated metrics for a provider."""
    provider_id: str
    provider_type: ProviderType
    status: ProviderStatus
    total_checks: int
    successful_checks: int
    failed_checks: int
    success_rate: float
    average_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    last_check_time: datetime
    last_success_time: datetime | None
    last_error: str | None
    consecutive_failures: int
    uptime_percentage: float


class ProviderHealthConfig(BaseModel):
    """Configuration for provider health monitoring."""
    check_interval_seconds: int = 30
    timeout_seconds: int = 5
    max_consecutive_failures: int = 3
    latency_warning_threshold_ms: float = 1000
    latency_error_threshold_ms: float = 3000
    history_retention_hours: int = 24


class ProviderHealthMonitor:
    """Real-time health monitoring for all providers.

    Continuously monitors provider health, tracks performance metrics,
    and enables automatic failover based on health status.
    """

    def __init__(self, config: ProviderHealthConfig = ProviderHealthConfig()):
        """Initialize provider health monitor.

        Args:
            config: Health monitoring configuration
        """
        self.config = config
        self._running = False
        self._monitor_task: asyncio.Task | None = None

        # Health check history
        self._check_history: dict[str, list[HealthCheckResult]] = {}

        # Current metrics
        self._metrics: dict[str, ProviderMetrics] = {}

        # Provider configurations
        self._provider_configs: dict[str, dict] = {
            "gemini": {
                "type": ProviderType.GEMINI,
                "endpoint": "https://generativelanguage.googleapis.com",
                "enabled": True
            },
            "openai": {
                "type": ProviderType.OPENAI,
                "endpoint": "https://api.openai.com",
                "enabled": True
            },
            "deepgram_nova3": {
                "type": ProviderType.DEEPGRAM,
                "endpoint": "https://api.deepgram.com",
                "enabled": True
            },
            "twilio": {
                "type": ProviderType.TWILIO,
                "endpoint": "https://api.twilio.com",
                "enabled": True
            },
            "telnyx": {
                "type": ProviderType.TELNYX,
                "endpoint": "https://api.telnyx.com",
                "enabled": True
            }
        }

    async def start(self) -> None:
        """Start health monitoring."""
        if self._running:
            logger.warning("Health monitor already running")
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Provider health monitor started")

    async def stop(self) -> None:
        """Stop health monitoring."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Provider health monitor stopped")

    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                # Check all providers
                await self._check_all_providers()

                # Clean old history
                self._clean_old_history()

                # Wait for next check
                await asyncio.sleep(self.config.check_interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as error:
                logger.error(f"Error in health monitor loop: {error}")
                await asyncio.sleep(5)  # Brief pause before retry

    async def _check_all_providers(self) -> None:
        """Check health of all enabled providers."""
        tasks = []
        for provider_id, config in self._provider_configs.items():
            if config.get("enabled", False):
                tasks.append(self._check_provider(provider_id, config))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_provider(
        self,
        provider_id: str,
        provider_config: dict
    ) -> HealthCheckResult:
        """Perform health check on a specific provider.

        Args:
            provider_id: Provider identifier
            provider_config: Provider configuration

        Returns:
            Health check result
        """
        start_time = time.time()

        try:
            # Simulate health check (in production, make actual API calls)
            # This would be replaced with actual provider-specific health checks
            await asyncio.sleep(0.1)  # Simulate network call

            # For demo purposes, occasionally simulate failures
            import random
            if random.random() < 0.05:  # 5% failure rate
                raise Exception("Simulated provider failure")

            response_time = time.time() - start_time
            latency_ms = response_time * 1000

            # Determine status based on latency
            if latency_ms > self.config.latency_error_threshold_ms:
                status = ProviderStatus.UNHEALTHY
            elif latency_ms > self.config.latency_warning_threshold_ms:
                status = ProviderStatus.DEGRADED
            else:
                status = ProviderStatus.HEALTHY

            result = HealthCheckResult(
                provider_id=provider_id,
                provider_type=provider_config["type"],
                status=status,
                latency_ms=latency_ms,
                timestamp=datetime.now(UTC),
                response_time=response_time,
                success=True
            )

        except Exception as error:
            response_time = time.time() - start_time
            result = HealthCheckResult(
                provider_id=provider_id,
                provider_type=provider_config["type"],
                status=ProviderStatus.OFFLINE,
                latency_ms=response_time * 1000,
                timestamp=datetime.now(UTC),
                error_message=str(error),
                response_time=response_time,
                success=False
            )

        # Store result
        self._store_check_result(result)

        # Update metrics
        self._update_metrics(provider_id)

        return result

    def _store_check_result(self, result: HealthCheckResult) -> None:
        """Store health check result in history.

        Args:
            result: Health check result to store
        """
        provider_id = result.provider_id

        if provider_id not in self._check_history:
            self._check_history[provider_id] = []

        self._check_history[provider_id].append(result)

        # Keep only recent history
        max_history = (self.config.history_retention_hours * 3600) // self.config.check_interval_seconds
        if len(self._check_history[provider_id]) > max_history:
            self._check_history[provider_id] = self._check_history[provider_id][-max_history:]

    def _update_metrics(self, provider_id: str) -> None:
        """Update aggregated metrics for a provider.

        Args:
            provider_id: Provider identifier
        """
        history = self._check_history.get(provider_id, [])
        if not history:
            return

        # Calculate metrics
        total_checks = len(history)
        successful_checks = sum(1 for r in history if r.success)
        failed_checks = total_checks - successful_checks
        success_rate = (successful_checks / total_checks * 100) if total_checks > 0 else 0

        latencies = [r.latency_ms for r in history if r.success]
        average_latency_ms = sum(latencies) / len(latencies) if latencies else 0
        min_latency_ms = min(latencies) if latencies else 0
        max_latency_ms = max(latencies) if latencies else 0

        last_result = history[-1]
        last_success_time = next(
            (r.timestamp for r in reversed(history) if r.success),
            None
        )

        # Count consecutive failures
        consecutive_failures = 0
        for result in reversed(history):
            if result.success:
                break
            consecutive_failures += 1

        # Calculate uptime
        uptime_percentage = success_rate

        # Determine overall status
        if consecutive_failures >= self.config.max_consecutive_failures:
            status = ProviderStatus.OFFLINE
        elif last_result.status == ProviderStatus.HEALTHY and success_rate >= 95:
            status = ProviderStatus.HEALTHY
        elif success_rate >= 70:
            status = ProviderStatus.DEGRADED
        else:
            status = ProviderStatus.UNHEALTHY

        self._metrics[provider_id] = ProviderMetrics(
            provider_id=provider_id,
            provider_type=last_result.provider_type,
            status=status,
            total_checks=total_checks,
            successful_checks=successful_checks,
            failed_checks=failed_checks,
            success_rate=round(success_rate, 2),
            average_latency_ms=round(average_latency_ms, 2),
            min_latency_ms=round(min_latency_ms, 2),
            max_latency_ms=round(max_latency_ms, 2),
            last_check_time=last_result.timestamp,
            last_success_time=last_success_time,
            last_error=last_result.error_message,
            consecutive_failures=consecutive_failures,
            uptime_percentage=round(uptime_percentage, 2)
        )

    def _clean_old_history(self) -> None:
        """Remove history older than retention period."""
        cutoff_time = datetime.now(UTC) - timedelta(hours=self.config.history_retention_hours)

        for provider_id in self._check_history:
            self._check_history[provider_id] = [
                r for r in self._check_history[provider_id]
                if r.timestamp > cutoff_time
            ]

    def get_provider_health(self, provider_id: str) -> ProviderMetrics | None:
        """Get health metrics for a specific provider.

        Args:
            provider_id: Provider identifier

        Returns:
            Provider metrics if available
        """
        return self._metrics.get(provider_id)

    def get_all_providers_health(self) -> dict[str, ProviderMetrics]:
        """Get health metrics for all providers.

        Returns:
            Dictionary of provider metrics
        """
        return self._metrics.copy()

    def get_healthy_providers(self) -> list[str]:
        """Get list of currently healthy provider IDs.

        Returns:
            List of healthy provider IDs
        """
        return [
            provider_id
            for provider_id, metrics in self._metrics.items()
            if metrics.status == ProviderStatus.HEALTHY
        ]

    def is_provider_healthy(self, provider_id: str) -> bool:
        """Check if a specific provider is healthy.

        Args:
            provider_id: Provider identifier

        Returns:
            True if provider is healthy
        """
        metrics = self._metrics.get(provider_id)
        return metrics is not None and metrics.status == ProviderStatus.HEALTHY


# Singleton instance
_health_monitor: ProviderHealthMonitor | None = None


def get_health_monitor() -> ProviderHealthMonitor:
    """Get singleton health monitor instance.

    Returns:
        ProviderHealthMonitor instance
    """
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = ProviderHealthMonitor()
    return _health_monitor
