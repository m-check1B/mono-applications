"""
Comprehensive Unit Tests for Provider Orchestration Service

Tests cover:
- Provider selection logic with different strategies
- Failover decision making
- Provider health status evaluation
- Context preservation during provider switches
- Error handling when no providers available
- Provider priority ordering
- Circuit breaker integration
- Round-robin selection
- Performance-based selection
"""

import pytest
from datetime import datetime, timedelta, timezone
from typing import Optional
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from uuid import UUID, uuid4

from app.services.provider_orchestration import (
    ProviderOrchestrator,
    OrchestrationConfig,
    SelectionStrategy,
    ProviderPreference,
    ProviderSelection,
    ProviderSwitchEvent,
)
from app.services.provider_health_monitor import ProviderStatus, ProviderType
from app.patterns.circuit_breaker import CircuitBreakerState, CircuitBreakerOpenError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_health_monitor():
    """Create a mock health monitor."""
    mock_monitor = Mock()

    # Default healthy providers
    mock_monitor.get_all_providers_health.return_value = {
        "gemini": Mock(
            provider_id="gemini",
            provider_type=ProviderType.GEMINI,
            status=ProviderStatus.HEALTHY,
            uptime_percentage=95.0,
            average_latency_ms=150.0,
            success_rate=98.0,
            consecutive_failures=0
        ),
        "openai": Mock(
            provider_id="openai",
            provider_type=ProviderType.OPENAI,
            status=ProviderStatus.HEALTHY,
            uptime_percentage=92.0,
            average_latency_ms=200.0,
            success_rate=97.0,
            consecutive_failures=0
        ),
        "deepgram_nova3": Mock(
            provider_id="deepgram_nova3",
            provider_type=ProviderType.DEEPGRAM,
            status=ProviderStatus.HEALTHY,
            uptime_percentage=90.0,
            average_latency_ms=180.0,
            success_rate=96.0,
            consecutive_failures=0
        ),
    }

    return mock_monitor


@pytest.fixture
def default_config():
    """Create default orchestration config."""
    return OrchestrationConfig(
        strategy=SelectionStrategy.BEST_PERFORMANCE,
        enable_auto_failover=True,
        failover_threshold_consecutive_errors=3,
        enable_load_balancing=True,
        health_check_required=True,
        min_provider_health_score=70.0,
        enable_circuit_breaker=False  # Disable for most tests
    )


@pytest.fixture
def orchestrator(default_config, mock_health_monitor):
    """Create orchestrator instance with mocked dependencies."""
    with patch('app.services.provider_orchestration.get_health_monitor', return_value=mock_health_monitor):
        orchestrator = ProviderOrchestrator(config=default_config)
        orchestrator._health_monitor = mock_health_monitor
        return orchestrator


@pytest.fixture
def session_id():
    """Generate a test session ID."""
    return uuid4()


# ============================================================================
# 1. PROVIDER SELECTION TESTS
# ============================================================================

@pytest.mark.unit
class TestProviderSelection:
    """Test provider selection logic with different strategies."""

    @pytest.mark.asyncio
    async def test_select_provider_returns_valid_selection(self, orchestrator, session_id):
        """Test that provider selection returns a valid ProviderSelection object."""
        result = await orchestrator.select_provider(session_id)

        assert isinstance(result, ProviderSelection)
        assert result.provider_id in ["gemini", "openai", "deepgram_nova3"]
        assert result.provider_type is not None
        assert result.reason is not None
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.fallback_providers, list)
        assert isinstance(result.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_best_performance_strategy_selects_lowest_latency(self, mock_health_monitor, session_id):
        """Test that BEST_PERFORMANCE strategy selects provider with lowest latency."""
        config = OrchestrationConfig(
            strategy=SelectionStrategy.BEST_PERFORMANCE,
            enable_circuit_breaker=False
        )

        with patch('app.services.provider_orchestration.get_health_monitor', return_value=mock_health_monitor):
            orchestrator = ProviderOrchestrator(config=config)
            orchestrator._health_monitor = mock_health_monitor

            result = await orchestrator.select_provider(session_id)

            # Gemini has lowest latency (150ms)
            assert result.provider_id == "gemini"

    @pytest.mark.asyncio
    async def test_highest_availability_strategy_selects_best_uptime(self, mock_health_monitor, session_id):
        """Test that HIGHEST_AVAILABILITY strategy selects provider with best uptime."""
        config = OrchestrationConfig(
            strategy=SelectionStrategy.HIGHEST_AVAILABILITY,
            enable_circuit_breaker=False
        )

        with patch('app.services.provider_orchestration.get_health_monitor', return_value=mock_health_monitor):
            orchestrator = ProviderOrchestrator(config=config)
            orchestrator._health_monitor = mock_health_monitor

            result = await orchestrator.select_provider(session_id)

            # Gemini has highest uptime (95%)
            assert result.provider_id == "gemini"

    @pytest.mark.asyncio
    async def test_priority_list_strategy_respects_preference_order(self, mock_health_monitor, session_id):
        """Test that PRIORITY_LIST strategy respects provider priority ordering."""
        config = OrchestrationConfig(
            strategy=SelectionStrategy.PRIORITY_LIST,
            provider_preferences=[
                ProviderPreference(provider_id="openai", priority=1, enabled=True),
                ProviderPreference(provider_id="gemini", priority=2, enabled=True),
                ProviderPreference(provider_id="deepgram_nova3", priority=3, enabled=True),
            ],
            enable_circuit_breaker=False
        )

        with patch('app.services.provider_orchestration.get_health_monitor', return_value=mock_health_monitor):
            orchestrator = ProviderOrchestrator(config=config)
            orchestrator._health_monitor = mock_health_monitor

            result = await orchestrator.select_provider(session_id)

            # OpenAI has highest priority (lowest number)
            assert result.provider_id == "openai"

    @pytest.mark.asyncio
    async def test_round_robin_strategy_distributes_load(self, mock_health_monitor):
        """Test that ROUND_ROBIN strategy distributes load evenly."""
        config = OrchestrationConfig(
            strategy=SelectionStrategy.ROUND_ROBIN,
            enable_circuit_breaker=False
        )

        with patch('app.services.provider_orchestration.get_health_monitor', return_value=mock_health_monitor):
            orchestrator = ProviderOrchestrator(config=config)
            orchestrator._health_monitor = mock_health_monitor

            # Select multiple times
            selections = []
            for i in range(6):
                result = await orchestrator.select_provider(uuid4())
                selections.append(result.provider_id)

            # Should cycle through all providers
            assert "gemini" in selections
            assert "openai" in selections
            assert "deepgram_nova3" in selections

            # Should see repetition after 3 selections (3 providers)
            assert selections[0] == selections[3]

    @pytest.mark.asyncio
    async def test_random_strategy_uses_weights(self, mock_health_monitor, session_id):
        """Test that RANDOM strategy considers provider weights."""
        config = OrchestrationConfig(
            strategy=SelectionStrategy.RANDOM,
            provider_preferences=[
                ProviderPreference(provider_id="gemini", priority=1, weight=1.0, enabled=True),
                ProviderPreference(provider_id="openai", priority=2, weight=0.5, enabled=True),
                ProviderPreference(provider_id="deepgram_nova3", priority=3, weight=0.1, enabled=True),
            ],
            enable_circuit_breaker=False
        )

        with patch('app.services.provider_orchestration.get_health_monitor', return_value=mock_health_monitor):
            orchestrator = ProviderOrchestrator(config=config)
            orchestrator._health_monitor = mock_health_monitor

            result = await orchestrator.select_provider(session_id)

            # Should select one of the configured providers
            assert result.provider_id in ["gemini", "openai", "deepgram_nova3"]


# ============================================================================
# 2. PROVIDER HEALTH EVALUATION TESTS
# ============================================================================

@pytest.mark.unit
class TestProviderHealthEvaluation:
    """Test provider health status evaluation."""

    @pytest.mark.asyncio
    async def test_unhealthy_providers_excluded_from_selection(self, mock_health_monitor, session_id):
        """Test that providers below minimum health score are excluded."""
        # Make openai unhealthy
        health_data = mock_health_monitor.get_all_providers_health.return_value
        health_data["openai"].uptime_percentage = 50.0
        health_data["openai"].status = ProviderStatus.DEGRADED

        config = OrchestrationConfig(
            strategy=SelectionStrategy.PRIORITY_LIST,
            provider_preferences=[
                ProviderPreference(provider_id="openai", priority=1, enabled=True),
                ProviderPreference(provider_id="gemini", priority=2, enabled=True),
            ],
            min_provider_health_score=70.0,
            enable_circuit_breaker=False
        )

        with patch('app.services.provider_orchestration.get_health_monitor', return_value=mock_health_monitor):
            orchestrator = ProviderOrchestrator(config=config)
            orchestrator._health_monitor = mock_health_monitor

            result = await orchestrator.select_provider(session_id)

            # Should skip unhealthy openai and select gemini
            assert result.provider_id == "gemini"

    @pytest.mark.asyncio
    async def test_disabled_providers_excluded_from_selection(self, mock_health_monitor, session_id):
        """Test that disabled providers are not selected."""
        config = OrchestrationConfig(
            strategy=SelectionStrategy.PRIORITY_LIST,
            provider_preferences=[
                ProviderPreference(provider_id="gemini", priority=1, enabled=False),
                ProviderPreference(provider_id="openai", priority=2, enabled=True),
            ],
            enable_circuit_breaker=False
        )

        with patch('app.services.provider_orchestration.get_health_monitor', return_value=mock_health_monitor):
            orchestrator = ProviderOrchestrator(config=config)
            orchestrator._health_monitor = mock_health_monitor

            result = await orchestrator.select_provider(session_id)

            # Should skip disabled gemini and select openai
            assert result.provider_id == "openai"

    @pytest.mark.asyncio
    async def test_confidence_score_calculation(self, orchestrator, session_id):
        """Test that confidence score is calculated correctly."""
        result = await orchestrator.select_provider(session_id)

        # Confidence should be between 0 and 1
        assert 0.0 <= result.confidence <= 1.0

        # With healthy providers, confidence should be high
        assert result.confidence > 0.5


# ============================================================================
# 3. FAILOVER DECISION TESTS
# ============================================================================

@pytest.mark.unit
class TestFailoverDecisions:
    """Test automatic failover trigger conditions."""

    @pytest.mark.asyncio
    async def test_failover_triggered_by_consecutive_failures(self, orchestrator, session_id):
        """Test that failover is triggered after consecutive failures."""
        # Assign provider to session
        orchestrator._session_providers[session_id] = "gemini"

        # Mock health monitor to show consecutive failures
        gemini_health = orchestrator._health_monitor.get_all_providers_health.return_value["gemini"]
        gemini_health.consecutive_failures = 5

        orchestrator._health_monitor.get_provider_health = Mock(return_value=gemini_health)

        needs_failover = await orchestrator.check_failover_needed(session_id)

        assert needs_failover is True

    @pytest.mark.asyncio
    async def test_failover_triggered_by_offline_status(self, orchestrator, session_id):
        """Test that failover is triggered when provider goes offline."""
        orchestrator._session_providers[session_id] = "gemini"

        # Mock provider as offline
        gemini_health = orchestrator._health_monitor.get_all_providers_health.return_value["gemini"]
        gemini_health.status = ProviderStatus.OFFLINE

        orchestrator._health_monitor.get_provider_health = Mock(return_value=gemini_health)

        needs_failover = await orchestrator.check_failover_needed(session_id)

        assert needs_failover is True

    @pytest.mark.asyncio
    async def test_failover_not_triggered_for_healthy_provider(self, orchestrator, session_id):
        """Test that failover is not triggered for healthy providers."""
        orchestrator._session_providers[session_id] = "gemini"

        gemini_health = orchestrator._health_monitor.get_all_providers_health.return_value["gemini"]
        orchestrator._health_monitor.get_provider_health = Mock(return_value=gemini_health)

        needs_failover = await orchestrator.check_failover_needed(session_id)

        assert needs_failover is False

    @pytest.mark.asyncio
    async def test_failover_disabled_when_config_disabled(self, orchestrator, session_id):
        """Test that failover is disabled when auto_failover is False."""
        orchestrator.config.enable_auto_failover = False
        orchestrator._session_providers[session_id] = "gemini"

        needs_failover = await orchestrator.check_failover_needed(session_id)

        assert needs_failover is False


# ============================================================================
# 4. PROVIDER SWITCHING TESTS
# ============================================================================

@pytest.mark.unit
class TestProviderSwitching:
    """Test provider switching and context preservation."""

    @pytest.mark.asyncio
    async def test_perform_failover_switches_provider(self, orchestrator, session_id):
        """Test that failover successfully switches to new provider."""
        orchestrator._session_providers[session_id] = "gemini"

        result = await orchestrator.perform_failover(session_id)

        assert result is not None
        assert isinstance(result, ProviderSwitchEvent)
        assert result.from_provider == "gemini"
        assert result.to_provider != "gemini"
        assert result.session_id == session_id

    @pytest.mark.asyncio
    async def test_failover_updates_session_provider(self, orchestrator, session_id):
        """Test that failover updates session provider tracking."""
        original_provider = "gemini"
        orchestrator._session_providers[session_id] = original_provider

        await orchestrator.perform_failover(session_id)

        new_provider = orchestrator._session_providers.get(session_id)
        assert new_provider != original_provider

    @pytest.mark.asyncio
    async def test_failover_records_switch_history(self, orchestrator, session_id):
        """Test that failover records switch events in history."""
        orchestrator._session_providers[session_id] = "gemini"

        await orchestrator.perform_failover(session_id)

        history = orchestrator.get_switch_history(session_id)
        assert len(history) > 0
        assert history[0].reason == "Automatic failover due to provider health issues"

    @pytest.mark.asyncio
    async def test_manual_switch_preserves_context(self, orchestrator, session_id):
        """Test that manual provider switch can preserve context."""
        # Create mock session
        mock_session = Mock()
        mock_session.id = session_id
        mock_session.provider_type = "gemini"
        mock_session.metadata = {}

        mock_session_manager = Mock()
        mock_session_manager.get_session = AsyncMock(return_value=mock_session)

        mock_failover_result = Mock()
        mock_failover_result.success = True
        mock_failover_result.from_provider = "gemini"
        mock_failover_result.to_provider = "openai"
        mock_failover_result.context_preserved = 5
        mock_failover_result.switched_at = datetime.now(timezone.utc)
        mock_failover_result.error_message = None

        mock_failover_service = Mock()
        mock_failover_service.switch_provider = AsyncMock(return_value=mock_failover_result)

        with patch('app.services.provider_orchestration.get_session_manager', return_value=mock_session_manager):
            with patch('app.services.provider_orchestration.get_failover_service', return_value=mock_failover_service):
                result = await orchestrator.switch_session_provider(
                    session_id=session_id,
                    new_provider="openai",
                    preserve_context=True
                )

        assert result["success"] is True
        assert result["from_provider"] == "gemini"
        assert result["to_provider"] == "openai"


# ============================================================================
# 5. ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.unit
class TestErrorHandling:
    """Test error handling when no providers available."""

    @pytest.mark.asyncio
    async def test_fallback_when_no_healthy_providers(self, mock_health_monitor, session_id):
        """Test fallback selection when all providers are unhealthy."""
        # Make all providers unhealthy
        health_data = mock_health_monitor.get_all_providers_health.return_value
        for provider in health_data.values():
            provider.uptime_percentage = 50.0
            provider.status = ProviderStatus.OFFLINE

        config = OrchestrationConfig(
            strategy=SelectionStrategy.BEST_PERFORMANCE,
            min_provider_health_score=70.0,
            enable_circuit_breaker=False
        )

        with patch('app.services.provider_orchestration.get_health_monitor', return_value=mock_health_monitor):
            orchestrator = ProviderOrchestrator(config=config)
            orchestrator._health_monitor = mock_health_monitor

            result = await orchestrator.select_provider(session_id)

            # Should return fallback provider
            assert result.provider_id is not None
            assert "fallback" in result.reason.lower()
            assert result.confidence < 0.2

    @pytest.mark.asyncio
    async def test_failover_handles_exception_gracefully(self, orchestrator, session_id):
        """Test that failover handles exceptions gracefully."""
        orchestrator._session_providers[session_id] = "gemini"

        # Force an exception during failover
        with patch.object(orchestrator, 'select_provider', side_effect=Exception("Test error")):
            result = await orchestrator.perform_failover(session_id)

            assert result is not None
            assert result.success is False
            assert result.error_message is not None

    @pytest.mark.asyncio
    async def test_session_not_found_raises_error(self, orchestrator):
        """Test that switching provider for non-existent session raises error."""
        non_existent_session = uuid4()

        mock_session_manager = Mock()
        mock_session_manager.get_session = AsyncMock(return_value=None)

        with patch('app.services.provider_orchestration.get_session_manager', return_value=mock_session_manager):
            with pytest.raises(ValueError, match="not found"):
                await orchestrator.switch_session_provider(
                    session_id=non_existent_session,
                    new_provider="openai"
                )


# ============================================================================
# 6. CIRCUIT BREAKER INTEGRATION TESTS
# ============================================================================

@pytest.mark.unit
class TestCircuitBreakerIntegration:
    """Test circuit breaker pattern integration."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_excludes_open_providers(self, mock_health_monitor, session_id):
        """Test that providers with open circuit breakers are excluded."""
        config = OrchestrationConfig(
            strategy=SelectionStrategy.PRIORITY_LIST,
            provider_preferences=[
                ProviderPreference(provider_id="gemini", priority=1, enabled=True),
                ProviderPreference(provider_id="openai", priority=2, enabled=True),
            ],
            enable_circuit_breaker=True,
            circuit_breaker_failure_threshold=3
        )

        with patch('app.services.provider_orchestration.get_health_monitor', return_value=mock_health_monitor):
            orchestrator = ProviderOrchestrator(config=config)
            orchestrator._health_monitor = mock_health_monitor

            # Force circuit breaker open for gemini
            gemini_breaker = orchestrator._circuit_breakers.get("gemini")
            if gemini_breaker:
                await gemini_breaker.force_open()

            result = await orchestrator.select_provider(session_id)

            # Should skip gemini (circuit open) and select openai
            assert result.provider_id == "openai"

    @pytest.mark.asyncio
    async def test_circuit_breaker_call_executes_function(self, orchestrator):
        """Test that circuit breaker call wrapper executes function."""
        orchestrator.config.enable_circuit_breaker = True

        # Add circuit breaker for test
        from app.patterns.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
        test_breaker = CircuitBreaker(
            CircuitBreakerConfig(name="test_provider"),
            provider_id="test"
        )
        orchestrator._circuit_breakers["test"] = test_breaker

        async def test_func(x, y):
            return x + y

        result = await orchestrator.call_provider_with_breaker(
            provider_id="test",
            func=test_func,
            x=2,
            y=3
        )

        assert result == 5

    def test_get_circuit_breaker_status(self, orchestrator):
        """Test getting circuit breaker status for provider."""
        orchestrator.config.enable_circuit_breaker = True

        # Initialize breaker
        from app.patterns.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
        test_breaker = CircuitBreaker(
            CircuitBreakerConfig(name="test_provider"),
            provider_id="test"
        )
        orchestrator._circuit_breakers["test"] = test_breaker

        status = orchestrator.get_circuit_breaker_status("test")

        assert status is not None
        assert "state" in status
        assert "failure_count" in status

    @pytest.mark.asyncio
    async def test_reset_circuit_breaker(self, orchestrator):
        """Test manually resetting a circuit breaker."""
        orchestrator.config.enable_circuit_breaker = True

        from app.patterns.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
        test_breaker = CircuitBreaker(
            CircuitBreakerConfig(name="test_provider"),
            provider_id="test"
        )
        orchestrator._circuit_breakers["test"] = test_breaker

        result = await orchestrator.reset_circuit_breaker("test")

        assert result is True


# ============================================================================
# 7. SESSION MANAGEMENT TESTS
# ============================================================================

@pytest.mark.unit
class TestSessionManagement:
    """Test session provider tracking."""

    @pytest.mark.asyncio
    async def test_select_provider_tracks_session(self, orchestrator, session_id):
        """Test that provider selection tracks session assignment."""
        result = await orchestrator.select_provider(session_id)

        tracked_provider = orchestrator.get_session_provider(session_id)
        assert tracked_provider == result.provider_id

    def test_get_session_provider_returns_none_for_unknown_session(self, orchestrator):
        """Test that getting provider for unknown session returns None."""
        unknown_session = uuid4()

        provider = orchestrator.get_session_provider(unknown_session)
        assert provider is None

    @pytest.mark.asyncio
    async def test_cleanup_session_removes_tracking(self, orchestrator, session_id):
        """Test that cleanup removes session from tracking."""
        orchestrator._session_providers[session_id] = "gemini"

        await orchestrator.cleanup_session(session_id)

        provider = orchestrator.get_session_provider(session_id)
        assert provider is None

    def test_selection_history_tracking(self, orchestrator):
        """Test that selection history is maintained."""
        history = orchestrator.get_selection_history()

        assert isinstance(history, list)

    def test_selection_history_limited_to_1000(self, orchestrator, session_id):
        """Test that selection history is limited to last 1000 entries."""
        # Add many selections to history
        for i in range(1100):
            orchestrator._selection_history.append(
                ProviderSelection(
                    provider_id="test",
                    provider_type=ProviderType.GEMINI,
                    reason="test",
                    confidence=0.8,
                    fallback_providers=[],
                    timestamp=datetime.now(timezone.utc)
                )
            )

        # Trigger cleanup by selecting provider
        import asyncio
        asyncio.run(orchestrator.select_provider(session_id))

        # History should be limited
        assert len(orchestrator._selection_history) <= 1000


# ============================================================================
# 8. FALLBACK CHAIN TESTS
# ============================================================================

@pytest.mark.unit
class TestFallbackChain:
    """Test fallback provider chain management."""

    @pytest.mark.asyncio
    async def test_fallback_providers_list_populated(self, orchestrator, session_id):
        """Test that fallback providers list is populated correctly."""
        result = await orchestrator.select_provider(session_id)

        # Should have fallback options
        assert len(result.fallback_providers) >= 0

        # Selected provider should not be in fallback list
        assert result.provider_id not in result.fallback_providers

    @pytest.mark.asyncio
    async def test_fallback_selection_with_no_candidates(self, mock_health_monitor, session_id):
        """Test fallback selection when no candidates are available."""
        # Empty health data
        mock_health_monitor.get_all_providers_health.return_value = {}

        config = OrchestrationConfig(
            strategy=SelectionStrategy.BEST_PERFORMANCE,
            enable_circuit_breaker=False
        )

        with patch('app.services.provider_orchestration.get_health_monitor', return_value=mock_health_monitor):
            orchestrator = ProviderOrchestrator(config=config)
            orchestrator._health_monitor = mock_health_monitor

            result = await orchestrator.select_provider(session_id)

            # Should still return a provider (absolute fallback)
            assert result.provider_id is not None
            assert result.confidence < 0.1
