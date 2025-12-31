"""
Telephony manager that handles multiple providers.
"""

import logging
from enum import Enum
from typing import Any

from app.providers.telephony_provider import (
    CallRecord,
    CallRequest,
    CallResponse,
    TelephonyProvider,
)
from app.services.telnyx_service import TelnyxService
from app.services.twilio_service import TwilioService


class ProviderType(str, Enum):
    TWILIO = "twilio"
    TELNYX = "telnyx"


class TelephonyManager:
    """Manages multiple telephony providers with failover and load balancing."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.providers: dict[str, TelephonyProvider] = {}
        self.primary_provider: str | None = None
        self.fallback_providers: list[str] = []
        self.logger = logging.getLogger(__name__)

        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all configured telephony providers."""
        provider_configs = self.config.get("providers", {})

        # Initialize Twilio if configured
        if "twilio" in provider_configs:
            try:
                self.providers[ProviderType.TWILIO] = TwilioService(provider_configs["twilio"])
                self.logger.info("Twilio provider initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Twilio provider: {e}")

        # Initialize Telnyx if configured
        if "telnyx" in provider_configs:
            try:
                self.providers[ProviderType.TELNYX] = TelnyxService(provider_configs["telnyx"])
                self.logger.info("Telnyx provider initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Telnyx provider: {e}")

        # Set primary and fallback providers
        self.primary_provider = self.config.get("primary_provider")
        self.fallback_providers = self.config.get("fallback_providers", [])

        # If no primary specified, use first available
        if not self.primary_provider and self.providers:
            self.primary_provider = list(self.providers.keys())[0]

        # If no fallbacks specified, use all other providers
        if not self.fallback_providers:
            self.fallback_providers = [
                provider for provider in self.providers.keys()
                if provider != self.primary_provider
            ]

    async def make_call(self, request: CallRequest) -> CallResponse:
        """Make a call with automatic failover to fallback providers."""
        providers_to_try = [self.primary_provider] + self.fallback_providers

        # If request specifies a provider, try it first
        if request.provider and request.provider in self.providers:
            providers_to_try = [request.provider] + [
                p for p in providers_to_try if p != request.provider
            ]

        last_error = None

        for provider_name in providers_to_try:
            if provider_name not in self.providers:
                continue

            provider = self.providers[provider_name]

            try:
                self.logger.info(f"Attempting call with provider: {provider_name}")
                response = await provider.make_call(request)

                if response.success:
                    self.logger.info(f"Call successful with provider: {provider_name}")
                    return response
                else:
                    last_error = response.error
                    self.logger.warning(f"Call failed with provider {provider_name}: {response.error}")

            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Exception with provider {provider_name}: {e}")
                continue

        # All providers failed
        return CallResponse(
            success=False,
            error=f"All providers failed. Last error: {last_error}",
            provider="none"
        )

    async def get_call_status(self, call_id: str, provider: str | None = None) -> CallRecord:
        """Get call status from the appropriate provider."""
        if provider and provider in self.providers:
            return await self.providers[provider].get_call_status(call_id)

        # Try all providers to find the call
        for provider_name, provider_instance in self.providers.items():
            try:
                return await provider_instance.get_call_status(call_id)
            except Exception as e:
                self.logger.debug(f"Call {call_id} not found with provider {provider_name}: {e}")
                continue

        raise ValueError(f"Call {call_id} not found with any provider")

    async def end_call(self, call_id: str, provider: str | None = None) -> bool:
        """End a call with the appropriate provider."""
        if provider and provider in self.providers:
            return await self.providers[provider].end_call(call_id)

        # Try all providers
        for provider_name, provider_instance in self.providers.items():
            try:
                if await provider_instance.end_call(call_id):
                    return True
            except Exception as e:
                self.logger.debug(f"Failed to end call {call_id} with provider {provider_name}: {e}")
                continue

        return False

    async def get_provider_health(self) -> dict[str, Any]:
        """Get health status of all providers."""
        health_results = {}

        for provider_name, provider in self.providers.items():
            try:
                health = await provider.health_check()
                health_results[provider_name] = health
            except Exception as e:
                health_results[provider_name] = {
                    "provider": provider_name,
                    "status": "unhealthy",
                    "error": str(e)
                }

        return health_results

    def get_available_providers(self) -> list[str]:
        """Get list of available providers."""
        return list(self.providers.keys())

    def get_provider_features(self, provider_name: str) -> list[str]:
        """Get supported features for a specific provider."""
        if provider_name in self.providers:
            return self.providers[provider_name].get_supported_features()
        return []

    def supports_feature(self, feature: str, provider_name: str | None = None) -> bool:
        """Check if a provider supports a specific feature."""
        if provider_name and provider_name in self.providers:
            return self.providers[provider_name].supports_feature(feature)

        # Check if any provider supports the feature
        for provider in self.providers.values():
            if provider.supports_feature(feature):
                return True

        return False

    async def validate_phone_number(self, phone_number: str, provider: str | None = None) -> dict[str, Any]:
        """Validate a phone number using specified or primary provider."""
        target_provider = provider or self.primary_provider

        if not target_provider or target_provider not in self.providers:
            return {
                "valid": False,
                "error": "No suitable provider available for validation"
            }

        return await self.providers[target_provider].validate_phone_number(phone_number)

    async def get_available_numbers(self, country_code: str = "US", provider: str | None = None) -> dict[str, list[str]]:
        """Get available numbers from all or specified provider."""
        if provider and provider in self.providers:
            try:
                numbers = await self.providers[provider].get_available_numbers(country_code)
                return {provider: numbers}
            except Exception:
                return {provider: []}

        # Get from all providers
        results = {}
        for provider_name, provider_instance in self.providers.items():
            try:
                numbers = await provider_instance.get_available_numbers(country_code)
                results[provider_name] = numbers
            except Exception:
                results[provider_name] = []

        return results

    def get_provider_stats(self) -> dict[str, Any]:
        """Get statistics for all providers."""
        stats = {
            "total_providers": len(self.providers),
            "primary_provider": self.primary_provider,
            "fallback_providers": self.fallback_providers,
            "providers": {}
        }

        for provider_name, provider in self.providers.items():
            stats["providers"][provider_name] = {
                "name": provider.provider_name,
                "features": provider.get_supported_features(),
                "config": provider.get_provider_config()
            }

        return stats


# Global telephony manager instance
_telephony_manager: TelephonyManager | None = None


def get_telephony_manager(config: dict[str, Any] | None = None) -> TelephonyManager:
    """Get or create the global telephony manager instance."""
    global _telephony_manager

    if _telephony_manager is None:
        if config is None:
            raise ValueError("Telephony manager not initialized and no config provided")
        _telephony_manager = TelephonyManager(config)

    return _telephony_manager


def initialize_telephony_manager(config: dict[str, Any]) -> TelephonyManager:
    """Initialize the global telephony manager."""
    global _telephony_manager
    _telephony_manager = TelephonyManager(config)
    return _telephony_manager
