"""AI Service Manager - Unified orchestration of multiple AI providers.

This module provides a unified interface for managing multiple AI providers
(Gemini, OpenAI, Deepgram) with intelligent routing, failover, and load balancing.
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Any

from app.providers.base import AudioFormat, BaseProvider, SessionConfig
from app.providers.deepgram import DeepgramSegmentedProvider
from app.providers.gemini import GeminiLiveProvider
from app.providers.openai import OpenAIRealtimeProvider

logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """Supported AI provider types."""
    GEMINI = "gemini"
    OPENAI = "openai"
    DEEPGRAM = "deepgram"


class ProviderStatus(str, Enum):
    """Provider status states."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DISABLED = "disabled"


class RoutingStrategy(str, Enum):
    """Provider routing strategies."""
    ROUND_ROBIN = "round_robin"
    PRIORITY = "priority"
    LOAD_BALANCED = "load_balanced"
    COST_OPTIMIZED = "cost_optimized"


class ProviderConfig:
    """Configuration for an AI provider."""

    def __init__(
        self,
        provider_type: ProviderType,
        api_key: str,
        enabled: bool = True,
        priority: int = 1,
        max_concurrent_sessions: int = 10,
        cost_per_minute: float = 0.0,
        latency_threshold_ms: float = 1000.0,
        **kwargs
    ):
        self.provider_type = provider_type
        self.api_key = api_key
        self.enabled = enabled
        self.priority = priority
        self.max_concurrent_sessions = max_concurrent_sessions
        self.cost_per_minute = cost_per_minute
        self.latency_threshold_ms = latency_threshold_ms
        self.additional_config = kwargs

        # Runtime metrics
        self.active_sessions = 0
        self.total_sessions = 0
        self.failed_sessions = 0
        self.average_latency_ms = 0.0
        self.last_health_check = 0.0
        self.status = ProviderStatus.HEALTHY


class AIServiceManager:
    """Unified AI service manager with multi-provider support."""

    def __init__(self, routing_strategy: RoutingStrategy = RoutingStrategy.PRIORITY):
        """Initialize AI service manager.
        
        Args:
            routing_strategy: Strategy for selecting providers
        """
        self.routing_strategy = routing_strategy
        self.providers: dict[ProviderType, ProviderConfig] = {}
        self.provider_instances: dict[ProviderType, BaseProvider] = {}
        self.round_robin_index = 0
        self.health_check_interval = 60.0  # seconds
        self._health_check_task: asyncio.Task | None = None

    def add_provider(self, config: ProviderConfig) -> None:
        """Add a provider configuration.
        
        Args:
            config: Provider configuration
        """
        self.providers[config.provider_type] = config

        # Create provider instance
        if config.provider_type == ProviderType.GEMINI:
            instance = GeminiLiveProvider(
                api_key=config.api_key,
                model=config.additional_config.get('model')
            )
        elif config.provider_type == ProviderType.OPENAI:
            model = config.additional_config.get('model', 'gpt-4o-mini-realtime-preview-2024-12-17')
            instance = OpenAIRealtimeProvider(
                api_key=config.api_key,
                model=model
            )
        elif config.provider_type == ProviderType.DEEPGRAM:
            instance = DeepgramSegmentedProvider(
                deepgram_api_key=config.api_key,
                gemini_api_key=config.additional_config.get('gemini_api_key', ''),
                stt_model=config.additional_config.get('stt_model', 'nova-2'),
                tts_voice=config.additional_config.get('tts_voice', 'aura-asteria-en')
            )
        else:
            raise ValueError(f"Unsupported provider type: {config.provider_type}")

        self.provider_instances[config.provider_type] = instance
        logger.info(f"Added {config.provider_type} provider")

    def remove_provider(self, provider_type: ProviderType) -> None:
        """Remove a provider.
        
        Args:
            provider_type: Provider type to remove
        """
        if provider_type in self.providers:
            del self.providers[provider_type]
        if provider_type in self.provider_instances:
            del self.provider_instances[provider_type]
        logger.info(f"Removed {provider_type} provider")

    async def start_health_checks(self) -> None:
        """Start background health check task."""
        if self._health_check_task:
            return

        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Started provider health checks")

    async def stop_health_checks(self) -> None:
        """Stop background health check task."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
        logger.info("Stopped provider health checks")

    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        while True:
            try:
                await self._check_provider_health()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(10)  # Brief pause on error

    async def _check_provider_health(self) -> None:
        """Check health of all enabled providers."""
        current_time = time.time()

        for provider_type, config in self.providers.items():
            if not config.enabled:
                continue

            try:
                # Simple health check - try to create a session config
                instance = self.provider_instances.get(provider_type)
                if not instance:
                    config.status = ProviderStatus.DISABLED
                    continue

                # Check if provider can accept new sessions
                if config.active_sessions >= config.max_concurrent_sessions:
                    config.status = ProviderStatus.DEGRADED
                    continue

                # Update latency (simplified - in real implementation would measure actual latency)
                if config.average_latency_ms > config.latency_threshold_ms:
                    config.status = ProviderStatus.DEGRADED
                else:
                    config.status = ProviderStatus.HEALTHY

                config.last_health_check = current_time

            except Exception as e:
                logger.error(f"Health check failed for {provider_type}: {e}")
                config.status = ProviderStatus.UNHEALTHY

    def select_provider(self, session_config: SessionConfig) -> ProviderType | None:
        """Select the best provider for a new session.
        
        Args:
            session_config: Session configuration requirements
            
        Returns:
            Selected provider type or None if no suitable provider
        """
        # Filter enabled and healthy providers
        available_providers = [
            (ptype, config) for ptype, config in self.providers.items()
            if config.enabled and config.status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED]
        ]

        if not available_providers:
            logger.warning("No healthy providers available")
            return None

        # Apply routing strategy
        if self.routing_strategy == RoutingStrategy.PRIORITY:
            # Sort by priority (lower number = higher priority)
            available_providers.sort(key=lambda x: x[1].priority)
            return available_providers[0][0]

        elif self.routing_strategy == RoutingStrategy.ROUND_ROBIN:
            # Simple round-robin
            healthy_providers = [ptype for ptype, _ in available_providers]
            if not healthy_providers:
                return None

            selected = healthy_providers[self.round_robin_index % len(healthy_providers)]
            self.round_robin_index += 1
            return selected

        elif self.routing_strategy == RoutingStrategy.LOAD_BALANCED:
            # Select provider with fewest active sessions
            available_providers.sort(key=lambda x: x[1].active_sessions)
            return available_providers[0][0]

        elif self.routing_strategy == RoutingStrategy.COST_OPTIMIZED:
            # Select cheapest provider
            available_providers.sort(key=lambda x: x[1].cost_per_minute)
            return available_providers[0][0]

        return None

    async def create_session(
        self,
        session_config: SessionConfig,
        preferred_provider: ProviderType | None = None
    ) -> tuple[BaseProvider, ProviderType]:
        """Create a new AI session.
        
        Args:
            session_config: Session configuration
            preferred_provider: Preferred provider (optional)
            
        Returns:
            Tuple of (provider instance, provider type)
            
        Raises:
            RuntimeError: If no suitable provider is available
        """
        # Try preferred provider first
        if preferred_provider:
            config = self.providers.get(preferred_provider)
            if config and config.enabled and config.status != ProviderStatus.UNHEALTHY:
                if config.active_sessions < config.max_concurrent_sessions:
                    provider = self.provider_instances[preferred_provider]
                    await provider.connect(session_config)
                    config.active_sessions += 1
                    config.total_sessions += 1
                    logger.info(f"Created session with preferred provider: {preferred_provider}")
                    return provider, preferred_provider

        # Select best provider
        selected_type = self.select_provider(session_config)
        if not selected_type:
            raise RuntimeError("No suitable AI provider available")

        config = self.providers[selected_type]
        provider = self.provider_instances[selected_type]

        try:
            await provider.connect(session_config)
            config.active_sessions += 1
            config.total_sessions += 1
            logger.info(f"Created session with provider: {selected_type}")
            return provider, selected_type

        except Exception as e:
            config.failed_sessions += 1
            logger.error(f"Failed to create session with {selected_type}: {e}")
            raise

    async def close_session(self, provider_type: ProviderType, provider: BaseProvider) -> None:
        """Close an AI session.
        
        Args:
            provider_type: Provider type
            provider: Provider instance
        """
        try:
            await provider.disconnect()
            config = self.providers.get(provider_type)
            if config:
                config.active_sessions = max(0, config.active_sessions - 1)
            logger.info(f"Closed session with provider: {provider_type}")
        except Exception as e:
            logger.error(f"Error closing session with {provider_type}: {e}")

    def get_provider_stats(self) -> dict[str, Any]:
        """Get comprehensive provider statistics.
        
        Returns:
            Dictionary with provider statistics
        """
        stats = {
            "routing_strategy": self.routing_strategy,
            "total_providers": len(self.providers),
            "enabled_providers": len([p for p in self.providers.values() if p.enabled]),
            "healthy_providers": len([p for p in self.providers.values() if p.status == ProviderStatus.HEALTHY]),
            "total_active_sessions": sum(p.active_sessions for p in self.providers.values()),
            "providers": {}
        }

        for provider_type, config in self.providers.items():
            stats["providers"][provider_type.value] = {
                "enabled": config.enabled,
                "status": config.status,
                "priority": config.priority,
                "active_sessions": config.active_sessions,
                "total_sessions": config.total_sessions,
                "failed_sessions": config.failed_sessions,
                "success_rate": (
                    (config.total_sessions - config.failed_sessions) / config.total_sessions * 100
                    if config.total_sessions > 0 else 100.0
                ),
                "average_latency_ms": config.average_latency_ms,
                "cost_per_minute": config.cost_per_minute,
                "max_concurrent_sessions": config.max_concurrent_sessions,
                "last_health_check": config.last_health_check
            }

        return stats

    async def test_provider(self, provider_type: ProviderType) -> dict[str, Any]:
        """Test a provider's connectivity and basic functionality.
        
        Args:
            provider_type: Provider type to test
            
        Returns:
            Test results dictionary
        """
        config = self.providers.get(provider_type)
        provider = self.provider_instances.get(provider_type)

        if not config or not provider:
            return {
                "provider": provider_type.value,
                "status": "error",
                "message": "Provider not configured"
            }

        test_result = {
            "provider": provider_type.value,
            "status": "unknown",
            "latency_ms": 0,
            "message": "",
            "timestamp": time.time()
        }

        try:
            # Measure connection time
            start_time = time.time()

            # Create minimal session config for testing
            test_config = SessionConfig(
                model_id="test-model",
                system_prompt="Test connection",
                temperature=0.1,
                audio_format=AudioFormat.PCM16
            )

            await provider.connect(test_config)

            connection_time = (time.time() - start_time) * 1000
            test_result["latency_ms"] = connection_time
            test_result["status"] = "success"
            test_result["message"] = f"Connected successfully in {connection_time:.0f}ms"

            # Update provider metrics
            config.average_latency_ms = (config.average_latency_ms + connection_time) / 2

            await provider.disconnect()

        except Exception as e:
            test_result["status"] = "error"
            test_result["message"] = str(e)
            config.failed_sessions += 1

        return test_result

    async def test_all_providers(self) -> dict[str, dict[str, Any]]:
        """Test all configured providers.
        
        Returns:
            Dictionary with test results for each provider
        """
        results = {}

        for provider_type in self.providers:
            results[provider_type.value] = await self.test_provider(provider_type)

        return results

    def update_routing_strategy(self, strategy: RoutingStrategy) -> None:
        """Update the routing strategy.
        
        Args:
            strategy: New routing strategy
        """
        self.routing_strategy = strategy
        self.round_robin_index = 0  # Reset round-robin index
        logger.info(f"Updated routing strategy to: {strategy}")


# Global instance for easy access
_ai_manager: AIServiceManager | None = None


def get_ai_manager() -> AIServiceManager:
    """Get the global AI service manager instance.
    
    Returns:
        AIServiceManager instance
    """
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIServiceManager()
    return _ai_manager


def configure_ai_manager(configs: list[ProviderConfig], routing_strategy: RoutingStrategy = RoutingStrategy.PRIORITY) -> AIServiceManager:
    """Configure the global AI service manager.
    
    Args:
        configs: List of provider configurations
        routing_strategy: Routing strategy to use
        
    Returns:
        Configured AIServiceManager instance
    """
    global _ai_manager
    _ai_manager = AIServiceManager(routing_strategy)

    for config in configs:
        _ai_manager.add_provider(config)

    return _ai_manager
