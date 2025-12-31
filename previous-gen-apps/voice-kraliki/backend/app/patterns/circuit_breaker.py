"""Circuit Breaker Pattern Implementation

Implements the circuit breaker pattern to prevent cascade failures in provider connections.
The circuit breaker has three states:
- CLOSED: Normal operation, requests pass through
- OPEN: Failure threshold exceeded, requests fail immediately
- HALF_OPEN: Testing recovery, limited requests pass through

This prevents repeated calls to failing services and allows for automatic recovery.
"""

import asyncio
import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from prometheus_client import Counter, Gauge, Histogram
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# Type variables for generic function wrapping
P = ParamSpec('P')
T = TypeVar('T')


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failure threshold exceeded, blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerConfig(BaseModel):
    """Configuration for circuit breaker behavior.

    Attributes:
        failure_threshold: Number of consecutive failures before opening circuit
        success_threshold: Number of consecutive successes in HALF_OPEN to close circuit
        timeout_seconds: Time to wait before transitioning from OPEN to HALF_OPEN
        half_open_max_calls: Maximum concurrent calls allowed in HALF_OPEN state
        name: Unique identifier for this circuit breaker
    """
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 60.0
    half_open_max_calls: int = 3
    name: str = "default"


class CircuitBreakerMetrics(BaseModel):
    """Metrics tracked by circuit breaker.

    Attributes:
        total_calls: Total number of calls attempted
        successful_calls: Number of successful calls
        failed_calls: Number of failed calls
        rejected_calls: Number of calls rejected due to open circuit
        state_transitions: Number of state changes
        last_failure_time: Timestamp of last failure
        last_success_time: Timestamp of last success
        last_state_change: Timestamp of last state change
        consecutive_failures: Current consecutive failure count
        consecutive_successes: Current consecutive success count
    """
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_transitions: int = 0
    last_failure_time: datetime | None = None
    last_success_time: datetime | None = None
    last_state_change: datetime | None = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0


# Prometheus metrics for circuit breakers
circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Current state of circuit breaker (0=CLOSED, 1=HALF_OPEN, 2=OPEN)',
    ['name', 'provider']
)

circuit_breaker_calls_total = Counter(
    'circuit_breaker_calls_total',
    'Total calls through circuit breaker',
    ['name', 'provider', 'status']
)

circuit_breaker_state_transitions = Counter(
    'circuit_breaker_state_transitions',
    'Circuit breaker state transitions',
    ['name', 'provider', 'from_state', 'to_state']
)

circuit_breaker_call_duration = Histogram(
    'circuit_breaker_call_duration_seconds',
    'Duration of calls through circuit breaker',
    ['name', 'provider', 'status']
)


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and rejects a call."""

    def __init__(self, circuit_name: str, retry_after: float):
        """Initialize error with circuit information.

        Args:
            circuit_name: Name of the circuit breaker
            retry_after: Seconds until circuit may close
        """
        self.circuit_name = circuit_name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker '{circuit_name}' is OPEN. "
            f"Retry after {retry_after:.1f} seconds."
        )


class CircuitBreaker:
    """Thread-safe circuit breaker implementation.

    Prevents cascade failures by monitoring call success/failure rates
    and automatically blocking requests when failure threshold is exceeded.
    Supports automatic recovery testing via HALF_OPEN state.

    Example:
        ```python
        config = CircuitBreakerConfig(
            name="gemini_provider",
            failure_threshold=5,
            timeout_seconds=60
        )
        breaker = CircuitBreaker(config)

        # Use as decorator
        @breaker
        async def call_provider():
            return await provider.make_call()

        # Or call directly
        result = await breaker.call(provider.make_call)
        ```
    """

    def __init__(self, config: CircuitBreakerConfig, provider_id: str = "unknown"):
        """Initialize circuit breaker.

        Args:
            config: Circuit breaker configuration
            provider_id: Provider identifier for metrics
        """
        self.config = config
        self.provider_id = provider_id
        self._state = CircuitBreakerState.CLOSED
        self._metrics = CircuitBreakerMetrics()
        self._opened_at: float | None = None
        self._half_open_calls = 0

        # Thread safety
        self._lock = asyncio.Lock()

        logger.info(
            f"Circuit breaker '{config.name}' initialized for provider '{provider_id}' "
            f"(failure_threshold={config.failure_threshold}, "
            f"timeout={config.timeout_seconds}s)"
        )

        # Initialize Prometheus metrics
        self._update_prometheus_state()

    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state.

        Returns:
            Current state
        """
        return self._state

    @property
    def metrics(self) -> CircuitBreakerMetrics:
        """Get current metrics.

        Returns:
            Copy of current metrics
        """
        return self._metrics.model_copy()

    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
        """Decorator to wrap function with circuit breaker.

        Args:
            func: Function to wrap

        Returns:
            Wrapped function
        """
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await self.call(func, *args, **kwargs)

        return wrapper

    async def call(
        self,
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs
    ) -> T:
        """Execute function through circuit breaker.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Any exception raised by the function
        """
        async with self._lock:
            # Check if we should attempt the call
            await self._before_call()

            self._metrics.total_calls += 1
            circuit_breaker_calls_total.labels(
                name=self.config.name,
                provider=self.provider_id,
                status='attempted'
            ).inc()

        # Execute the call (outside lock to allow concurrency)
        start_time = time.time()
        error = None
        result = None

        try:
            # Handle both sync and async functions
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            duration = time.time() - start_time

            # Record success
            async with self._lock:
                await self._on_success(duration)

            return result

        except Exception as e:
            error = e
            duration = time.time() - start_time

            # Record failure
            async with self._lock:
                await self._on_failure(duration, e)

            raise

    async def _before_call(self) -> None:
        """Check circuit state before allowing call.

        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        current_time = time.time()

        if self._state == CircuitBreakerState.CLOSED:
            # Normal operation
            return

        elif self._state == CircuitBreakerState.OPEN:
            # Check if timeout has elapsed
            if self._opened_at is None:
                # Should never happen, but handle gracefully
                logger.error(
                    f"Circuit breaker '{self.config.name}' is OPEN but "
                    f"opened_at is None. Resetting to CLOSED."
                )
                await self._transition_to(CircuitBreakerState.CLOSED)
                return

            elapsed = current_time - self._opened_at

            if elapsed >= self.config.timeout_seconds:
                # Timeout elapsed, try recovery
                logger.info(
                    f"Circuit breaker '{self.config.name}' timeout elapsed "
                    f"({elapsed:.1f}s). Transitioning to HALF_OPEN."
                )
                await self._transition_to(CircuitBreakerState.HALF_OPEN)
                return
            else:
                # Still in timeout period
                retry_after = self.config.timeout_seconds - elapsed
                self._metrics.rejected_calls += 1

                circuit_breaker_calls_total.labels(
                    name=self.config.name,
                    provider=self.provider_id,
                    status='rejected'
                ).inc()

                logger.debug(
                    f"Circuit breaker '{self.config.name}' rejecting call. "
                    f"Retry after {retry_after:.1f}s"
                )

                raise CircuitBreakerOpenError(self.config.name, retry_after)

        elif self._state == CircuitBreakerState.HALF_OPEN:
            # Check if we're at max concurrent calls
            if self._half_open_calls >= self.config.half_open_max_calls:
                self._metrics.rejected_calls += 1

                circuit_breaker_calls_total.labels(
                    name=self.config.name,
                    provider=self.provider_id,
                    status='rejected'
                ).inc()

                raise CircuitBreakerOpenError(
                    self.config.name,
                    5.0  # Short retry in half-open
                )

            self._half_open_calls += 1

    async def _on_success(self, duration: float) -> None:
        """Handle successful call.

        Args:
            duration: Call duration in seconds
        """
        self._metrics.successful_calls += 1
        self._metrics.consecutive_successes += 1
        self._metrics.consecutive_failures = 0
        self._metrics.last_success_time = datetime.now(UTC)

        circuit_breaker_calls_total.labels(
            name=self.config.name,
            provider=self.provider_id,
            status='success'
        ).inc()

        circuit_breaker_call_duration.labels(
            name=self.config.name,
            provider=self.provider_id,
            status='success'
        ).observe(duration)

        if self._state == CircuitBreakerState.HALF_OPEN:
            self._half_open_calls = max(0, self._half_open_calls - 1)

            # Check if we have enough successes to close
            if self._metrics.consecutive_successes >= self.config.success_threshold:
                logger.info(
                    f"Circuit breaker '{self.config.name}' recovered. "
                    f"Transitioning to CLOSED after {self.config.success_threshold} successes."
                )
                await self._transition_to(CircuitBreakerState.CLOSED)

    async def _on_failure(self, duration: float, error: Exception) -> None:
        """Handle failed call.

        Args:
            duration: Call duration in seconds
            error: Exception that occurred
        """
        self._metrics.failed_calls += 1
        self._metrics.consecutive_failures += 1
        self._metrics.consecutive_successes = 0
        self._metrics.last_failure_time = datetime.now(UTC)

        circuit_breaker_calls_total.labels(
            name=self.config.name,
            provider=self.provider_id,
            status='failure'
        ).inc()

        circuit_breaker_call_duration.labels(
            name=self.config.name,
            provider=self.provider_id,
            status='failure'
        ).observe(duration)

        logger.warning(
            f"Circuit breaker '{self.config.name}' call failed: {error}. "
            f"Consecutive failures: {self._metrics.consecutive_failures}"
        )

        if self._state == CircuitBreakerState.HALF_OPEN:
            self._half_open_calls = max(0, self._half_open_calls - 1)

            # Any failure in half-open reopens the circuit
            logger.warning(
                f"Circuit breaker '{self.config.name}' failed in HALF_OPEN. "
                f"Reopening circuit."
            )
            await self._transition_to(CircuitBreakerState.OPEN)

        elif self._state == CircuitBreakerState.CLOSED:
            # Check if we should open
            if self._metrics.consecutive_failures >= self.config.failure_threshold:
                logger.error(
                    f"Circuit breaker '{self.config.name}' failure threshold reached "
                    f"({self._metrics.consecutive_failures} failures). Opening circuit."
                )
                await self._transition_to(CircuitBreakerState.OPEN)

    async def _transition_to(self, new_state: CircuitBreakerState) -> None:
        """Transition to new state.

        Args:
            new_state: Target state
        """
        old_state = self._state

        if old_state == new_state:
            return

        self._state = new_state
        self._metrics.state_transitions += 1
        self._metrics.last_state_change = datetime.now(UTC)

        # State-specific actions
        if new_state == CircuitBreakerState.OPEN:
            self._opened_at = time.time()
            self._metrics.consecutive_successes = 0

        elif new_state == CircuitBreakerState.HALF_OPEN:
            self._half_open_calls = 0
            self._metrics.consecutive_successes = 0
            self._metrics.consecutive_failures = 0

        elif new_state == CircuitBreakerState.CLOSED:
            self._opened_at = None
            self._half_open_calls = 0
            self._metrics.consecutive_failures = 0

        # Update Prometheus metrics
        self._update_prometheus_state()

        circuit_breaker_state_transitions.labels(
            name=self.config.name,
            provider=self.provider_id,
            from_state=old_state.value,
            to_state=new_state.value
        ).inc()

        logger.info(
            f"Circuit breaker '{self.config.name}' transitioned: "
            f"{old_state.value} -> {new_state.value}"
        )

    def _update_prometheus_state(self) -> None:
        """Update Prometheus state gauge."""
        state_value = {
            CircuitBreakerState.CLOSED: 0,
            CircuitBreakerState.HALF_OPEN: 1,
            CircuitBreakerState.OPEN: 2
        }[self._state]

        circuit_breaker_state.labels(
            name=self.config.name,
            provider=self.provider_id
        ).set(state_value)

    async def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state.

        This should be used for administrative purposes only,
        such as after fixing a provider issue.
        """
        async with self._lock:
            logger.info(f"Manually resetting circuit breaker '{self.config.name}'")
            await self._transition_to(CircuitBreakerState.CLOSED)
            self._metrics.consecutive_failures = 0
            self._metrics.consecutive_successes = 0

    async def force_open(self) -> None:
        """Manually open circuit breaker.

        This should be used for administrative purposes only,
        such as during maintenance.
        """
        async with self._lock:
            logger.info(f"Manually opening circuit breaker '{self.config.name}'")
            await self._transition_to(CircuitBreakerState.OPEN)

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive circuit breaker status.

        Returns:
            Status dictionary with state and metrics
        """
        retry_after = None
        if self._state == CircuitBreakerState.OPEN and self._opened_at:
            elapsed = time.time() - self._opened_at
            retry_after = max(0, self.config.timeout_seconds - elapsed)

        return {
            "name": self.config.name,
            "provider_id": self.provider_id,
            "state": self._state.value,
            "retry_after_seconds": retry_after,
            "metrics": {
                "total_calls": self._metrics.total_calls,
                "successful_calls": self._metrics.successful_calls,
                "failed_calls": self._metrics.failed_calls,
                "rejected_calls": self._metrics.rejected_calls,
                "success_rate": (
                    self._metrics.successful_calls / self._metrics.total_calls * 100
                    if self._metrics.total_calls > 0 else 0
                ),
                "consecutive_failures": self._metrics.consecutive_failures,
                "consecutive_successes": self._metrics.consecutive_successes,
                "state_transitions": self._metrics.state_transitions,
                "last_failure_time": (
                    self._metrics.last_failure_time.isoformat()
                    if self._metrics.last_failure_time else None
                ),
                "last_success_time": (
                    self._metrics.last_success_time.isoformat()
                    if self._metrics.last_success_time else None
                ),
                "last_state_change": (
                    self._metrics.last_state_change.isoformat()
                    if self._metrics.last_state_change else None
                )
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout_seconds": self.config.timeout_seconds,
                "half_open_max_calls": self.config.half_open_max_calls
            }
        }
