"""Integration test for Circuit Breaker with Provider Orchestration.

Demonstrates how the circuit breaker integrates with the provider
orchestration service to prevent cascade failures.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.patterns.circuit_breaker import CircuitBreakerState, CircuitBreakerOpenError
from app.services.provider_orchestration import (
    ProviderOrchestrator,
    OrchestrationConfig,
    ProviderPreference
)


@pytest.fixture
def orchestration_config():
    """Orchestration config with circuit breaker enabled."""
    return OrchestrationConfig(
        enable_circuit_breaker=True,
        circuit_breaker_failure_threshold=3,
        circuit_breaker_timeout_seconds=1.0,
        circuit_breaker_success_threshold=2,
        provider_preferences=[
            ProviderPreference(provider_id="gemini", priority=1),
            ProviderPreference(provider_id="openai", priority=2),
            ProviderPreference(provider_id="deepgram", priority=3)
        ]
    )


@pytest.fixture
def orchestrator(orchestration_config):
    """Provider orchestrator with circuit breakers."""
    return ProviderOrchestrator(orchestration_config)


@pytest.mark.asyncio
async def test_circuit_breakers_initialized(orchestrator):
    """Circuit breakers should be initialized for all providers."""
    assert len(orchestrator._circuit_breakers) == 3
    assert "gemini" in orchestrator._circuit_breakers
    assert "openai" in orchestrator._circuit_breakers
    assert "deepgram" in orchestrator._circuit_breakers

    # All should start in CLOSED state
    for provider_id, breaker in orchestrator._circuit_breakers.items():
        assert breaker.state == CircuitBreakerState.CLOSED


@pytest.mark.asyncio
async def test_successful_provider_call(orchestrator):
    """Successful provider calls should pass through circuit breaker."""
    async def mock_provider_call():
        return "success"

    result = await orchestrator.call_provider_with_breaker(
        "gemini",
        mock_provider_call
    )

    assert result == "success"

    # Check metrics
    status = orchestrator.get_circuit_breaker_status("gemini")
    assert status["metrics"]["successful_calls"] == 1
    assert status["metrics"]["failed_calls"] == 0


@pytest.mark.asyncio
async def test_failed_provider_calls_open_circuit(orchestrator):
    """Multiple failures should open the circuit breaker."""
    async def mock_failing_call():
        raise Exception("Provider failure")

    # Make failing calls
    for i in range(3):
        with pytest.raises(Exception):
            await orchestrator.call_provider_with_breaker(
                "gemini",
                mock_failing_call
            )

    # Circuit should be open
    status = orchestrator.get_circuit_breaker_status("gemini")
    assert status["state"] == CircuitBreakerState.OPEN.value
    assert status["metrics"]["failed_calls"] == 3


@pytest.mark.asyncio
async def test_open_circuit_rejects_calls(orchestrator):
    """Open circuit should reject calls immediately."""
    async def mock_failing_call():
        raise Exception("Provider failure")

    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await orchestrator.call_provider_with_breaker(
                "gemini",
                mock_failing_call
            )

    # Next call should be rejected
    async def mock_successful_call():
        return "success"

    with pytest.raises(CircuitBreakerOpenError) as exc_info:
        await orchestrator.call_provider_with_breaker(
            "gemini",
            mock_successful_call
        )

    assert "OPEN" in str(exc_info.value)


@pytest.mark.asyncio
async def test_circuit_recovery(orchestrator):
    """Circuit should recover after timeout and successful calls."""
    async def mock_failing_call():
        raise Exception("Provider failure")

    async def mock_successful_call():
        return "success"

    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await orchestrator.call_provider_with_breaker(
                "gemini",
                mock_failing_call
            )

    # Wait for timeout
    await asyncio.sleep(1.1)

    # Make successful calls
    result1 = await orchestrator.call_provider_with_breaker(
        "gemini",
        mock_successful_call
    )
    result2 = await orchestrator.call_provider_with_breaker(
        "gemini",
        mock_successful_call
    )

    assert result1 == "success"
    assert result2 == "success"

    # Circuit should be closed
    status = orchestrator.get_circuit_breaker_status("gemini")
    assert status["state"] == CircuitBreakerState.CLOSED.value


@pytest.mark.asyncio
async def test_get_all_circuit_breaker_status(orchestrator):
    """Should get status for all circuit breakers."""
    all_status = orchestrator.get_all_circuit_breaker_status()

    assert len(all_status) == 3
    assert "gemini" in all_status
    assert "openai" in all_status
    assert "deepgram" in all_status

    for provider_id, status in all_status.items():
        assert "state" in status
        assert "metrics" in status
        assert "config" in status


@pytest.mark.asyncio
async def test_manual_reset(orchestrator):
    """Manual reset should close the circuit."""
    async def mock_failing_call():
        raise Exception("Provider failure")

    # Open the circuit
    for i in range(3):
        with pytest.raises(Exception):
            await orchestrator.call_provider_with_breaker(
                "gemini",
                mock_failing_call
            )

    status = orchestrator.get_circuit_breaker_status("gemini")
    assert status["state"] == CircuitBreakerState.OPEN.value

    # Reset
    success = await orchestrator.reset_circuit_breaker("gemini")
    assert success is True

    status = orchestrator.get_circuit_breaker_status("gemini")
    assert status["state"] == CircuitBreakerState.CLOSED.value


@pytest.mark.asyncio
async def test_manual_force_open(orchestrator):
    """Manual force open should open the circuit."""
    status = orchestrator.get_circuit_breaker_status("gemini")
    assert status["state"] == CircuitBreakerState.CLOSED.value

    # Force open
    success = await orchestrator.force_open_circuit_breaker("gemini")
    assert success is True

    status = orchestrator.get_circuit_breaker_status("gemini")
    assert status["state"] == CircuitBreakerState.OPEN.value


@pytest.mark.asyncio
async def test_circuit_breaker_disabled(orchestration_config):
    """Circuit breaker can be disabled via config."""
    config = orchestration_config.model_copy()
    config.enable_circuit_breaker = False

    orchestrator = ProviderOrchestrator(config)

    async def mock_failing_call():
        raise Exception("Provider failure")

    # Make many failing calls
    for i in range(10):
        with pytest.raises(Exception):
            await orchestrator.call_provider_with_breaker(
                "gemini",
                mock_failing_call
            )

    # No circuit breaker should exist
    assert len(orchestrator._circuit_breakers) == 0


@pytest.mark.asyncio
async def test_provider_selection_excludes_open_circuits(orchestrator):
    """Provider selection should exclude providers with open circuits."""
    # Mock the health monitor to return healthy providers
    with patch.object(orchestrator._health_monitor, 'get_all_providers_health') as mock_health:
        # Setup mock health data
        from app.services.provider_health_monitor import ProviderMetrics, ProviderStatus, ProviderType
        from datetime import datetime, timezone

        mock_health.return_value = {
            "gemini": ProviderMetrics(
                provider_id="gemini",
                provider_type=ProviderType.GEMINI,
                status=ProviderStatus.HEALTHY,
                total_checks=10,
                successful_checks=10,
                failed_checks=0,
                success_rate=100.0,
                average_latency_ms=100.0,
                min_latency_ms=50.0,
                max_latency_ms=150.0,
                last_check_time=datetime.now(timezone.utc),
                last_success_time=datetime.now(timezone.utc),
                last_error=None,
                consecutive_failures=0,
                uptime_percentage=100.0
            ),
            "openai": ProviderMetrics(
                provider_id="openai",
                provider_type=ProviderType.OPENAI,
                status=ProviderStatus.HEALTHY,
                total_checks=10,
                successful_checks=10,
                failed_checks=0,
                success_rate=100.0,
                average_latency_ms=120.0,
                min_latency_ms=60.0,
                max_latency_ms=180.0,
                last_check_time=datetime.now(timezone.utc),
                last_success_time=datetime.now(timezone.utc),
                last_error=None,
                consecutive_failures=0,
                uptime_percentage=100.0
            )
        }

        # Open gemini circuit
        await orchestrator.force_open_circuit_breaker("gemini")

        # Select provider
        selection = await orchestrator.select_provider()

        # Should select openai since gemini circuit is open
        assert selection.provider_id != "gemini"


@pytest.mark.asyncio
async def test_sync_function_support(orchestrator):
    """Circuit breaker should work with synchronous functions."""
    def sync_function():
        return "sync success"

    result = await orchestrator.call_provider_with_breaker(
        "gemini",
        sync_function
    )

    assert result == "sync success"


@pytest.mark.asyncio
async def test_multiple_providers_independent_circuits(orchestrator):
    """Circuit breakers for different providers should be independent."""
    async def mock_failing_call():
        raise Exception("Provider failure")

    # Fail gemini calls
    for i in range(3):
        with pytest.raises(Exception):
            await orchestrator.call_provider_with_breaker(
                "gemini",
                mock_failing_call
            )

    # Gemini should be open
    gemini_status = orchestrator.get_circuit_breaker_status("gemini")
    assert gemini_status["state"] == CircuitBreakerState.OPEN.value

    # OpenAI should still be closed
    openai_status = orchestrator.get_circuit_breaker_status("openai")
    assert openai_status["state"] == CircuitBreakerState.CLOSED.value


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
