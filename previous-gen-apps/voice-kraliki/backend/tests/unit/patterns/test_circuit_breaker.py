"""Unit tests for Circuit Breaker Pattern implementation.

Tests cover:
- State transitions (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)
- Failure threshold enforcement
- Timeout behavior
- Success threshold in HALF_OPEN state
- Metrics tracking
- Thread safety
- Manual reset and force open operations
"""

import asyncio
import pytest
import time
from datetime import datetime

from app.patterns.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerState,
    CircuitBreakerOpenError,
    CircuitBreakerMetrics
)


# Test fixtures

@pytest.fixture
def default_config():
    """Default circuit breaker configuration for testing."""
    return CircuitBreakerConfig(
        name="test_breaker",
        failure_threshold=3,
        success_threshold=2,
        timeout_seconds=1.0,
        half_open_max_calls=2
    )


@pytest.fixture
def circuit_breaker(default_config):
    """Circuit breaker instance for testing."""
    return CircuitBreaker(default_config, provider_id="test_provider")


# Helper functions

async def successful_call():
    """Simulate a successful async call."""
    await asyncio.sleep(0.01)
    return "success"


async def failing_call():
    """Simulate a failing async call."""
    await asyncio.sleep(0.01)
    raise Exception("Simulated failure")


def sync_successful_call():
    """Simulate a successful sync call."""
    return "success"


def sync_failing_call():
    """Simulate a failing sync call."""
    raise Exception("Simulated failure")


# State Transition Tests

@pytest.mark.asyncio
async def test_initial_state_is_closed(circuit_breaker):
    """Circuit breaker should start in CLOSED state."""
    assert circuit_breaker.state == CircuitBreakerState.CLOSED


@pytest.mark.asyncio
async def test_transition_to_open_after_failures(circuit_breaker):
    """Circuit should open after exceeding failure threshold."""
    # Execute failing calls until threshold is reached
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_call)

    # Circuit should now be OPEN
    assert circuit_breaker.state == CircuitBreakerState.OPEN


@pytest.mark.asyncio
async def test_transition_to_half_open_after_timeout(circuit_breaker):
    """Circuit should transition to HALF_OPEN after timeout."""
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_call)

    assert circuit_breaker.state == CircuitBreakerState.OPEN

    # Wait for timeout
    await asyncio.sleep(1.1)

    # Next call should transition to HALF_OPEN
    try:
        await circuit_breaker.call(successful_call)
    except Exception:
        pass

    assert circuit_breaker.state in [
        CircuitBreakerState.HALF_OPEN,
        CircuitBreakerState.CLOSED  # May have already closed if successful
    ]


@pytest.mark.asyncio
async def test_transition_to_closed_from_half_open(circuit_breaker):
    """Circuit should close after success threshold in HALF_OPEN."""
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_call)

    assert circuit_breaker.state == CircuitBreakerState.OPEN

    # Wait for timeout
    await asyncio.sleep(1.1)

    # Execute successful calls to close circuit
    for i in range(2):
        result = await circuit_breaker.call(successful_call)
        assert result == "success"

    # Circuit should be CLOSED
    assert circuit_breaker.state == CircuitBreakerState.CLOSED


@pytest.mark.asyncio
async def test_half_open_reopens_on_failure(circuit_breaker):
    """Circuit should reopen if call fails in HALF_OPEN state."""
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_call)

    assert circuit_breaker.state == CircuitBreakerState.OPEN

    # Wait for timeout
    await asyncio.sleep(1.1)

    # First call transitions to HALF_OPEN, then fails
    with pytest.raises(Exception):
        await circuit_breaker.call(failing_call)

    # Circuit should be OPEN again
    assert circuit_breaker.state == CircuitBreakerState.OPEN


# Request Handling Tests

@pytest.mark.asyncio
async def test_closed_circuit_allows_calls(circuit_breaker):
    """CLOSED circuit should allow all calls through."""
    result = await circuit_breaker.call(successful_call)
    assert result == "success"


@pytest.mark.asyncio
async def test_open_circuit_rejects_calls(circuit_breaker):
    """OPEN circuit should reject calls immediately."""
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_call)

    # Circuit is now OPEN, calls should be rejected
    with pytest.raises(CircuitBreakerOpenError) as exc_info:
        await circuit_breaker.call(successful_call)

    assert "OPEN" in str(exc_info.value)


@pytest.mark.asyncio
async def test_half_open_state_behavior(circuit_breaker):
    """HALF_OPEN circuit should handle calls correctly."""
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_call)

    assert circuit_breaker.state == CircuitBreakerState.OPEN

    # Wait for timeout
    await asyncio.sleep(1.1)

    # First successful call in HALF_OPEN
    result = await circuit_breaker.call(successful_call)
    assert result == "success"

    # Circuit should be in HALF_OPEN
    assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN

    # One more success should close the circuit (threshold is 2)
    result = await circuit_breaker.call(successful_call)
    assert result == "success"

    # Circuit should now be CLOSED
    assert circuit_breaker.state == CircuitBreakerState.CLOSED


# Metrics Tests

@pytest.mark.asyncio
async def test_metrics_track_successful_calls(circuit_breaker):
    """Metrics should track successful calls."""
    await circuit_breaker.call(successful_call)
    await circuit_breaker.call(successful_call)

    metrics = circuit_breaker.metrics

    assert metrics.total_calls == 2
    assert metrics.successful_calls == 2
    assert metrics.failed_calls == 0
    assert metrics.consecutive_successes == 2


@pytest.mark.asyncio
async def test_metrics_track_failed_calls(circuit_breaker):
    """Metrics should track failed calls."""
    for i in range(2):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_call)

    metrics = circuit_breaker.metrics

    assert metrics.total_calls == 2
    assert metrics.successful_calls == 0
    assert metrics.failed_calls == 2
    assert metrics.consecutive_failures == 2


@pytest.mark.asyncio
async def test_metrics_track_rejected_calls(circuit_breaker):
    """Metrics should track rejected calls when circuit is open."""
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_call)

    # Try calls while open
    for i in range(2):
        with pytest.raises(CircuitBreakerOpenError):
            await circuit_breaker.call(successful_call)

    metrics = circuit_breaker.metrics

    assert metrics.rejected_calls == 2


@pytest.mark.asyncio
async def test_metrics_track_state_transitions(circuit_breaker):
    """Metrics should track state transitions."""
    initial_transitions = circuit_breaker.metrics.state_transitions

    # Open the circuit (CLOSED -> OPEN)
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_call)

    # Wait and trigger HALF_OPEN (OPEN -> HALF_OPEN)
    await asyncio.sleep(1.1)
    try:
        await circuit_breaker.call(successful_call)
    except Exception:
        pass

    # Should have at least 2 transitions
    assert circuit_breaker.metrics.state_transitions >= initial_transitions + 2


# Sync Function Tests

@pytest.mark.asyncio
async def test_sync_function_support(circuit_breaker):
    """Circuit breaker should support synchronous functions."""
    result = await circuit_breaker.call(sync_successful_call)
    assert result == "success"


@pytest.mark.asyncio
async def test_sync_function_failure(circuit_breaker):
    """Circuit breaker should handle sync function failures."""
    with pytest.raises(Exception):
        await circuit_breaker.call(sync_failing_call)

    metrics = circuit_breaker.metrics
    assert metrics.failed_calls == 1


# Decorator Tests

@pytest.mark.asyncio
async def test_decorator_usage(circuit_breaker):
    """Circuit breaker should work as a decorator."""
    @circuit_breaker
    async def decorated_call():
        return "decorated success"

    result = await decorated_call()
    assert result == "decorated success"


@pytest.mark.asyncio
async def test_decorator_with_failures(circuit_breaker):
    """Decorator should track failures correctly."""
    @circuit_breaker
    async def decorated_failing_call():
        raise Exception("Decorated failure")

    for i in range(3):
        with pytest.raises(Exception):
            await decorated_failing_call()

    assert circuit_breaker.state == CircuitBreakerState.OPEN


# Manual Control Tests

@pytest.mark.asyncio
async def test_manual_reset(circuit_breaker):
    """Manual reset should close the circuit."""
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_call)

    assert circuit_breaker.state == CircuitBreakerState.OPEN

    # Manually reset
    await circuit_breaker.reset()

    assert circuit_breaker.state == CircuitBreakerState.CLOSED
    assert circuit_breaker.metrics.consecutive_failures == 0


@pytest.mark.asyncio
async def test_manual_force_open(circuit_breaker):
    """Force open should open the circuit regardless of state."""
    assert circuit_breaker.state == CircuitBreakerState.CLOSED

    await circuit_breaker.force_open()

    assert circuit_breaker.state == CircuitBreakerState.OPEN


# Status Tests

@pytest.mark.asyncio
async def test_get_status(circuit_breaker):
    """get_status should return comprehensive information."""
    await circuit_breaker.call(successful_call)

    status = circuit_breaker.get_status()

    assert status["name"] == "test_breaker"
    assert status["provider_id"] == "test_provider"
    assert status["state"] == CircuitBreakerState.CLOSED.value
    assert "metrics" in status
    assert "config" in status


@pytest.mark.asyncio
async def test_status_includes_retry_after(circuit_breaker):
    """Status should include retry_after when circuit is open."""
    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_call)

    status = circuit_breaker.get_status()

    assert status["state"] == CircuitBreakerState.OPEN.value
    assert status["retry_after_seconds"] is not None
    assert status["retry_after_seconds"] <= circuit_breaker.config.timeout_seconds


# Configuration Tests

@pytest.mark.asyncio
async def test_custom_failure_threshold():
    """Circuit breaker should respect custom failure threshold."""
    config = CircuitBreakerConfig(
        name="custom_threshold",
        failure_threshold=5,
        timeout_seconds=1.0
    )
    breaker = CircuitBreaker(config, provider_id="test")

    # Fail 4 times (below threshold)
    for i in range(4):
        with pytest.raises(Exception):
            await breaker.call(failing_call)

    # Should still be CLOSED
    assert breaker.state == CircuitBreakerState.CLOSED

    # 5th failure should open it
    with pytest.raises(Exception):
        await breaker.call(failing_call)

    assert breaker.state == CircuitBreakerState.OPEN


@pytest.mark.asyncio
async def test_custom_timeout():
    """Circuit breaker should respect custom timeout."""
    config = CircuitBreakerConfig(
        name="custom_timeout",
        failure_threshold=2,
        timeout_seconds=0.5
    )
    breaker = CircuitBreaker(config, provider_id="test")

    # Open the circuit
    for i in range(2):
        with pytest.raises(Exception):
            await breaker.call(failing_call)

    assert breaker.state == CircuitBreakerState.OPEN

    # Wait for custom timeout
    await asyncio.sleep(0.6)

    # Should transition to HALF_OPEN
    try:
        await breaker.call(successful_call)
    except Exception:
        pass

    assert breaker.state in [
        CircuitBreakerState.HALF_OPEN,
        CircuitBreakerState.CLOSED
    ]


# Edge Case Tests

@pytest.mark.asyncio
async def test_consecutive_counter_resets_on_success(circuit_breaker):
    """Consecutive failure counter should reset on success."""
    # 2 failures
    for i in range(2):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_call)

    assert circuit_breaker.metrics.consecutive_failures == 2

    # Success should reset counter
    await circuit_breaker.call(successful_call)

    assert circuit_breaker.metrics.consecutive_failures == 0
    assert circuit_breaker.state == CircuitBreakerState.CLOSED


@pytest.mark.asyncio
async def test_consecutive_success_resets_on_failure(circuit_breaker):
    """Consecutive success counter should reset on failure."""
    # 2 successes
    for i in range(2):
        await circuit_breaker.call(successful_call)

    assert circuit_breaker.metrics.consecutive_successes == 2

    # Failure should reset counter
    with pytest.raises(Exception):
        await circuit_breaker.call(failing_call)

    assert circuit_breaker.metrics.consecutive_successes == 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
