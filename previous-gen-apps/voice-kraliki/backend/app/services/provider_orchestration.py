"""Provider Orchestration Service

Intelligent provider selection and hot-swapping:
- Provider selection based on health and performance
- Automatic failover during active calls
- Load balancing across providers
- Fallback chain management
- Provider preference rules
- Circuit breaker pattern for cascade failure prevention
"""

import asyncio
import logging
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from app.patterns.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitBreakerState,
)

from .provider_health_monitor import ProviderStatus, ProviderType, get_health_monitor

logger = logging.getLogger(__name__)


class SelectionStrategy(str, Enum):
    """Provider selection strategies."""
    BEST_PERFORMANCE = "best_performance"  # Lowest latency
    HIGHEST_AVAILABILITY = "highest_availability"  # Best uptime
    ROUND_ROBIN = "round_robin"  # Distribute load evenly
    PRIORITY_LIST = "priority_list"  # Use preferred order
    RANDOM = "random"  # Random selection


class ProviderPreference(BaseModel):
    """Provider preference configuration."""
    provider_id: str
    priority: int  # Lower number = higher priority
    weight: float = 1.0  # For weighted selection
    enabled: bool = True


class OrchestrationConfig(BaseModel):
    """Configuration for provider orchestration."""
    strategy: SelectionStrategy = SelectionStrategy.BEST_PERFORMANCE
    enable_auto_failover: bool = True
    failover_threshold_consecutive_errors: int = 3
    enable_load_balancing: bool = True
    health_check_required: bool = True
    min_provider_health_score: float = 70.0
    provider_preferences: list[ProviderPreference] = []

    # Circuit breaker configuration
    enable_circuit_breaker: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout_seconds: float = 60.0
    circuit_breaker_success_threshold: int = 2
    circuit_breaker_half_open_max_calls: int = 3


class ProviderSelection(BaseModel):
    """Result of provider selection."""
    provider_id: str
    provider_type: ProviderType
    reason: str
    confidence: float  # 0-1
    fallback_providers: list[str]
    timestamp: datetime


class ProviderSwitchEvent(BaseModel):
    """Event for provider switching."""
    session_id: UUID
    from_provider: str | None
    to_provider: str
    reason: str
    timestamp: datetime
    success: bool
    error_message: str | None = None


class ProviderOrchestrator:
    """Intelligent provider orchestration service.

    Manages provider selection, load balancing, and automatic failover
    to ensure optimal performance and reliability.
    """

    def __init__(self, config: OrchestrationConfig = OrchestrationConfig()):
        """Initialize provider orchestrator.

        Args:
            config: Orchestration configuration
        """
        self.config = config
        self._health_monitor = get_health_monitor()

        # Active sessions and their providers
        self._session_providers: dict[UUID, str] = {}

        # Round-robin counter
        self._round_robin_index = 0

        # Provider selection history
        self._selection_history: list[ProviderSelection] = []

        # Switch event history
        self._switch_history: dict[UUID, list[ProviderSwitchEvent]] = {}

        # Default preferences if not provided
        # Note: Gemini Live (bidiGenerateContent) has quota limitations with standard API keys
        # Deepgram pipeline uses Gemini text API (which works) + Deepgram STT/TTS
        if not self.config.provider_preferences:
            self.config.provider_preferences = [
                ProviderPreference(provider_id="deepgram", priority=1, weight=1.0),  # Reliable STT+TTS pipeline
                ProviderPreference(provider_id="openai", priority=2, weight=0.9),  # OpenAI Realtime
                ProviderPreference(provider_id="deepgram_nova3", priority=3, weight=0.8),  # Nova 3 Voice Agent
                ProviderPreference(provider_id="gemini", priority=4, weight=0.5),  # Quota-limited
            ]

        # Initialize circuit breakers for each provider
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        if self.config.enable_circuit_breaker:
            self._initialize_circuit_breakers()

    def _initialize_circuit_breakers(self) -> None:
        """Initialize circuit breakers for all providers."""
        for pref in self.config.provider_preferences:
            breaker_config = CircuitBreakerConfig(
                name=f"provider_{pref.provider_id}",
                failure_threshold=self.config.circuit_breaker_failure_threshold,
                timeout_seconds=self.config.circuit_breaker_timeout_seconds,
                success_threshold=self.config.circuit_breaker_success_threshold,
                half_open_max_calls=self.config.circuit_breaker_half_open_max_calls
            )

            self._circuit_breakers[pref.provider_id] = CircuitBreaker(
                breaker_config,
                provider_id=pref.provider_id
            )

            logger.info(
                f"Initialized circuit breaker for provider '{pref.provider_id}' "
                f"(threshold={breaker_config.failure_threshold}, "
                f"timeout={breaker_config.timeout_seconds}s)"
            )

    async def select_provider(
        self,
        session_id: UUID | None = None,
        required_capabilities: list[str] | None = None
    ) -> ProviderSelection:
        """Select the best provider for a new session.

        Args:
            session_id: Optional session identifier
            required_capabilities: Required provider capabilities

        Returns:
            Provider selection result
        """
        # Get health status of all providers
        all_health = self._health_monitor.get_all_providers_health()

        # Filter enabled and healthy providers
        candidate_providers = []
        for pref in self.config.provider_preferences:
            if not pref.enabled:
                continue

            health = all_health.get(pref.provider_id)
            if not health:
                continue

            # Check circuit breaker status
            if self.config.enable_circuit_breaker:
                breaker = self._circuit_breakers.get(pref.provider_id)
                if breaker and breaker.state == CircuitBreakerState.OPEN:
                    logger.debug(
                        f"Provider {pref.provider_id} circuit breaker is OPEN, "
                        f"excluding from selection"
                    )
                    continue

            # Check minimum health score
            if self.config.health_check_required:
                if health.uptime_percentage < self.config.min_provider_health_score:
                    logger.debug(f"Provider {pref.provider_id} below minimum health score")
                    continue

            candidate_providers.append({
                "provider_id": pref.provider_id,
                "provider_type": health.provider_type,
                "preference": pref,
                "health": health
            })

        if not candidate_providers:
            # No healthy providers, use fallback
            logger.warning("No healthy providers available, using fallback")
            return self._select_fallback_provider()

        # Select based on strategy
        if self.config.strategy == SelectionStrategy.BEST_PERFORMANCE:
            selected = self._select_best_performance(candidate_providers)
        elif self.config.strategy == SelectionStrategy.HIGHEST_AVAILABILITY:
            selected = self._select_highest_availability(candidate_providers)
        elif self.config.strategy == SelectionStrategy.ROUND_ROBIN:
            selected = self._select_round_robin(candidate_providers)
        elif self.config.strategy == SelectionStrategy.PRIORITY_LIST:
            selected = self._select_by_priority(candidate_providers)
        else:  # RANDOM
            selected = self._select_random(candidate_providers)

        # Build fallback list
        fallback_providers = [
            p["provider_id"] for p in candidate_providers
            if p["provider_id"] != selected["provider_id"]
        ]

        result = ProviderSelection(
            provider_id=selected["provider_id"],
            provider_type=selected["provider_type"],
            reason=f"Selected using {self.config.strategy.value} strategy",
            confidence=self._calculate_confidence(selected),
            fallback_providers=fallback_providers,
            timestamp=datetime.now(UTC)
        )

        # Store selection
        if session_id:
            self._session_providers[session_id] = selected["provider_id"]

        self._selection_history.append(result)

        # Keep only recent history (last 1000)
        if len(self._selection_history) > 1000:
            self._selection_history = self._selection_history[-1000:]

        logger.info(
            f"Selected provider {result.provider_id} for session {session_id} "
            f"(strategy: {self.config.strategy.value})"
        )

        return result

    def _select_best_performance(self, candidates: list[dict]) -> dict:
        """Select provider with best performance (lowest latency).

        Args:
            candidates: List of candidate providers

        Returns:
            Selected provider
        """
        return min(candidates, key=lambda p: p["health"].average_latency_ms)

    def _select_highest_availability(self, candidates: list[dict]) -> dict:
        """Select provider with highest availability.

        Args:
            candidates: List of candidate providers

        Returns:
            Selected provider
        """
        return max(candidates, key=lambda p: p["health"].uptime_percentage)

    def _select_round_robin(self, candidates: list[dict]) -> dict:
        """Select provider using round-robin.

        Args:
            candidates: List of candidate providers

        Returns:
            Selected provider
        """
        selected = candidates[self._round_robin_index % len(candidates)]
        self._round_robin_index += 1
        return selected

    def _select_by_priority(self, candidates: list[dict]) -> dict:
        """Select provider by priority order.

        Args:
            candidates: List of candidate providers

        Returns:
            Selected provider
        """
        return min(candidates, key=lambda p: p["preference"].priority)

    def _select_random(self, candidates: list[dict]) -> dict:
        """Select provider randomly (weighted by preference).

        Args:
            candidates: List of candidate providers

        Returns:
            Selected provider
        """
        import random

        weights = [p["preference"].weight for p in candidates]
        return random.choices(candidates, weights=weights)[0]

    def _calculate_confidence(self, provider: dict) -> float:
        """Calculate confidence in provider selection.

        Args:
            provider: Selected provider info

        Returns:
            Confidence score (0-1)
        """
        health = provider["health"]

        # Factors contributing to confidence
        uptime_factor = health.uptime_percentage / 100.0
        latency_factor = max(0, 1.0 - (health.average_latency_ms / 3000.0))
        success_factor = health.success_rate / 100.0

        # Weighted average
        confidence = (
            uptime_factor * 0.4 +
            latency_factor * 0.3 +
            success_factor * 0.3
        )

        return round(confidence, 2)

    def _select_fallback_provider(self) -> ProviderSelection:
        """Select fallback provider when no healthy providers available.

        Returns:
            Fallback provider selection
        """
        # Use first enabled provider
        for pref in self.config.provider_preferences:
            if pref.enabled:
                return ProviderSelection(
                    provider_id=pref.provider_id,
                    provider_type=ProviderType.GEMINI,  # Default
                    reason="Fallback provider (no healthy providers available)",
                    confidence=0.1,
                    fallback_providers=[],
                    timestamp=datetime.now(UTC)
                )

        # Absolute fallback
        return ProviderSelection(
            provider_id="gemini",
            provider_type=ProviderType.GEMINI,
            reason="Default fallback provider",
            confidence=0.05,
            fallback_providers=[],
            timestamp=datetime.now(UTC)
        )

    async def check_failover_needed(self, session_id: UUID) -> bool:
        """Check if a session needs provider failover.

        Args:
            session_id: Session identifier

        Returns:
            True if failover is needed
        """
        if not self.config.enable_auto_failover:
            return False

        provider_id = self._session_providers.get(session_id)
        if not provider_id:
            return False

        # Check provider health
        health = self._health_monitor.get_provider_health(provider_id)
        if not health:
            logger.warning(f"No health data for provider {provider_id}")
            return True

        # Check consecutive failures
        if health.consecutive_failures >= self.config.failover_threshold_consecutive_errors:
            logger.warning(
                f"Provider {provider_id} has {health.consecutive_failures} consecutive failures"
            )
            return True

        # Check if provider is offline
        if health.status == ProviderStatus.OFFLINE:
            logger.warning(f"Provider {provider_id} is offline")
            return True

        return False

    async def perform_failover(self, session_id: UUID) -> ProviderSwitchEvent | None:
        """Perform provider failover for a session.

        Args:
            session_id: Session identifier

        Returns:
            Switch event if successful, None otherwise
        """
        current_provider = self._session_providers.get(session_id)

        try:
            # Select new provider
            selection = await self.select_provider(session_id)

            # Perform switch
            success = await self._switch_provider(
                session_id,
                current_provider,
                selection.provider_id
            )

            event = ProviderSwitchEvent(
                session_id=session_id,
                from_provider=current_provider,
                to_provider=selection.provider_id,
                reason="Automatic failover due to provider health issues",
                timestamp=datetime.now(UTC),
                success=success
            )

            if session_id not in self._switch_history:
                self._switch_history[session_id] = []
            self._switch_history[session_id].append(event)

            if success:
                logger.info(
                    f"Successfully failed over from {current_provider} to "
                    f"{selection.provider_id} for session {session_id}"
                )
            else:
                logger.error(f"Failed to perform failover for session {session_id}")

            return event

        except Exception as error:
            logger.error(f"Error during failover for session {session_id}: {error}")
            return ProviderSwitchEvent(
                session_id=session_id,
                from_provider=current_provider,
                to_provider="unknown",
                reason="Failover failed",
                timestamp=datetime.now(UTC),
                success=False,
                error_message=str(error)
            )

    async def _switch_provider(
        self,
        session_id: UUID,
        from_provider: str | None,
        to_provider: str
    ) -> bool:
        """Switch provider for an active session.

        Args:
            session_id: Session identifier
            from_provider: Current provider
            to_provider: New provider

        Returns:
            True if switch was successful
        """
        # In production, this would:
        # 1. Gracefully disconnect from current provider
        # 2. Establish connection to new provider
        # 3. Transfer session state
        # 4. Resume audio/call

        # For now, just update our tracking
        self._session_providers[session_id] = to_provider

        # Simulate switch delay
        import asyncio
        await asyncio.sleep(0.1)

        return True

    def get_session_provider(self, session_id: UUID) -> str | None:
        """Get current provider for a session.

        Args:
            session_id: Session identifier

        Returns:
            Provider ID if session exists
        """
        return self._session_providers.get(session_id)

    def get_switch_history(self, session_id: UUID) -> list[ProviderSwitchEvent]:
        """Get provider switch history for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of switch events
        """
        return self._switch_history.get(session_id, [])

    def get_selection_history(self, limit: int | None = None) -> list[ProviderSelection]:
        """Get provider selection history.

        Args:
            limit: Maximum number of selections to return

        Returns:
            List of provider selections
        """
        if limit:
            return self._selection_history[-limit:]
        return self._selection_history

    async def switch_session_provider(
        self,
        session_id: UUID,
        new_provider: str,
        preserve_context: bool = True
    ) -> dict:
        """Switch provider for active session.

        Args:
            session_id: Session identifier
            new_provider: Target provider ID
            preserve_context: Whether to preserve conversation context

        Returns:
            Switch result dictionary

        Raises:
            ValueError: If session not found
            RuntimeError: If switch fails
        """
        from app.services.provider_failover import get_failover_service
        from app.sessions.manager import get_session_manager

        session_manager = get_session_manager()
        session = await session_manager.get_session(session_id)

        if not session:
            raise ValueError(f"Session {session_id} not found")

        old_provider = session.provider_type
        failover_service = get_failover_service()

        logger.info(
            f"Switching provider for session {session_id}: "
            f"{old_provider} -> {new_provider}"
        )

        # Execute switch
        result = await failover_service.switch_provider(
            session_id,
            old_provider,
            new_provider,
            reason="manual_switch"
        )

        # Update our tracking
        self._session_providers[session_id] = new_provider

        return {
            "success": result.success,
            "session_id": str(session_id),
            "from_provider": result.from_provider,
            "to_provider": result.to_provider,
            "context_preserved": result.context_preserved,
            "switched_at": result.switched_at.isoformat(),
            "error_message": result.error_message
        }

    async def cleanup_session(self, session_id: UUID) -> None:
        """Clean up orchestration data for a session.

        Args:
            session_id: Session identifier
        """
        if session_id in self._session_providers:
            del self._session_providers[session_id]

        logger.info(f"Cleaned up orchestration data for session {session_id}")

    async def call_provider_with_breaker(
        self,
        provider_id: str,
        func: callable,
        *args,
        **kwargs
    ) -> any:
        """Execute provider call through circuit breaker.

        Args:
            provider_id: Provider identifier
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: If circuit breaker is open
            Exception: Any exception from the provider call
        """
        if not self.config.enable_circuit_breaker:
            # Circuit breaker disabled, call directly
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        breaker = self._circuit_breakers.get(provider_id)
        if not breaker:
            logger.warning(
                f"No circuit breaker found for provider {provider_id}, "
                f"calling directly"
            )
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        # Call through circuit breaker
        try:
            return await breaker.call(func, *args, **kwargs)
        except CircuitBreakerOpenError as e:
            logger.error(
                f"Circuit breaker open for provider {provider_id}: {e}. "
                f"Triggering failover."
            )
            raise

    def get_circuit_breaker_status(self, provider_id: str) -> dict | None:
        """Get circuit breaker status for a provider.

        Args:
            provider_id: Provider identifier

        Returns:
            Circuit breaker status dictionary, or None if not found
        """
        breaker = self._circuit_breakers.get(provider_id)
        if not breaker:
            return None

        return breaker.get_status()

    def get_all_circuit_breaker_status(self) -> dict[str, dict]:
        """Get circuit breaker status for all providers.

        Returns:
            Dictionary mapping provider IDs to their circuit breaker status
        """
        return {
            provider_id: breaker.get_status()
            for provider_id, breaker in self._circuit_breakers.items()
        }

    async def reset_circuit_breaker(self, provider_id: str) -> bool:
        """Manually reset a circuit breaker.

        Args:
            provider_id: Provider identifier

        Returns:
            True if reset successful, False if breaker not found
        """
        breaker = self._circuit_breakers.get(provider_id)
        if not breaker:
            logger.warning(f"No circuit breaker found for provider {provider_id}")
            return False

        await breaker.reset()
        logger.info(f"Reset circuit breaker for provider {provider_id}")
        return True

    async def force_open_circuit_breaker(self, provider_id: str) -> bool:
        """Manually open a circuit breaker.

        Args:
            provider_id: Provider identifier

        Returns:
            True if opened successfully, False if breaker not found
        """
        breaker = self._circuit_breakers.get(provider_id)
        if not breaker:
            logger.warning(f"No circuit breaker found for provider {provider_id}")
            return False

        await breaker.force_open()
        logger.info(f"Forced open circuit breaker for provider {provider_id}")
        return True

    def record_provider_success(self, provider_id: str) -> None:
        """Record a successful provider operation (for external tracking).

        This method allows external code to inform the orchestrator about
        successful provider operations, helping to keep circuit breaker
        state accurate when calls are made outside the breaker.

        Args:
            provider_id: Provider identifier
        """
        if not self.config.enable_circuit_breaker:
            return

        breaker = self._circuit_breakers.get(provider_id)
        if breaker:
            logger.debug(f"External success recorded for provider {provider_id}")

    def record_provider_failure(self, provider_id: str, error: Exception) -> None:
        """Record a failed provider operation (for external tracking).

        This method allows external code to inform the orchestrator about
        failed provider operations, helping to keep circuit breaker
        state accurate when calls are made outside the breaker.

        Args:
            provider_id: Provider identifier
            error: The exception that occurred
        """
        if not self.config.enable_circuit_breaker:
            return

        breaker = self._circuit_breakers.get(provider_id)
        if breaker:
            logger.warning(
                f"External failure recorded for provider {provider_id}: {error}"
            )


# Singleton instance
_orchestrator: ProviderOrchestrator | None = None


def get_orchestrator() -> ProviderOrchestrator:
    """Get singleton orchestrator instance.

    Returns:
        ProviderOrchestrator instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ProviderOrchestrator()
    return _orchestrator
