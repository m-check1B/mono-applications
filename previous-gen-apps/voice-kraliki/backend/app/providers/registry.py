"""Provider registry for dynamic provider management.

This module provides a central registry for AI providers and telephony adapters,
with automatic discovery, capability matching, and configuration validation.
"""

import logging
from enum import Enum
from functools import lru_cache
from typing import Any

from pydantic import BaseModel, Field

from app.config.settings import get_settings
from app.providers.base import (
    AudioFormat,
    ProviderCapabilities,
    RealtimeEndToEndProvider,
    SegmentedVoiceProvider,
    TelephonyAdapter,
)
from app.providers.deepgram import create_deepgram_provider
from app.providers.deepgram_nova3 import (
    create_deepgram_nova3_provider,
)
from app.providers.gemini import create_gemini_provider
from app.providers.openai import create_openai_provider
from app.providers.telnyx import create_telnyx_adapter
from app.providers.twilio import create_twilio_adapter

logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """Provider types."""

    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPGRAM = "deepgram"
    DEEPGRAM_NOVA3 = "deepgram_nova3"


class TelephonyType(str, Enum):
    """Telephony adapter types."""

    TWILIO = "twilio"
    TELNYX = "telnyx"


class ProviderInfo(BaseModel):
    """Provider information and metadata."""

    id: str = Field(description="Provider identifier")
    name: str = Field(description="Display name")
    type: ProviderType = Field(description="Provider type")
    capabilities: ProviderCapabilities = Field(description="Provider capabilities")
    available_models: list[str] = Field(default_factory=list, description="Available model IDs")
    requires_api_key: bool = Field(default=True, description="Requires API key")
    is_configured: bool = Field(default=False, description="API key configured in settings")


class TelephonyInfo(BaseModel):
    """Telephony adapter information."""

    id: str = Field(description="Adapter identifier")
    name: str = Field(description="Display name")
    type: TelephonyType = Field(description="Adapter type")
    capabilities: ProviderCapabilities = Field(description="Adapter capabilities")
    is_configured: bool = Field(default=False, description="Credentials configured in settings")
    is_primary: bool = Field(default=False, description="Primary telephony provider")


class ProviderRegistry:
    """Central registry for AI providers and telephony adapters."""

    def __init__(self):
        """Initialize provider registry."""
        self._settings = get_settings()
        self._providers: dict[ProviderType, ProviderInfo] = {}
        self._telephony: dict[TelephonyType, TelephonyInfo] = {}
        self._initialize_registry()

    def _initialize_registry(self) -> None:
        """Initialize provider and telephony adapter registry."""
        # Register OpenAI provider
        self._providers[ProviderType.OPENAI] = ProviderInfo(
            id="openai",
            name="OpenAI Realtime API",
            type=ProviderType.OPENAI,
            capabilities=ProviderCapabilities(
                supports_realtime=True,
                supports_text=True,
                supports_audio=True,
                supports_multimodal=False,
                supports_function_calling=True,
                supports_streaming=True,
                audio_formats=[AudioFormat.PCM16],
                max_session_duration=1800,
                cost_tier="varies",
            ),
            available_models=[
                "gpt-4o-mini-realtime-preview-2024-12-17",
                "gpt-4o-realtime-preview-2024-12-17",
            ],
            is_configured=bool(self._settings.openai_api_key),
        )

        # Register Gemini provider
        self._providers[ProviderType.GEMINI] = ProviderInfo(
            id="gemini",
            name="Google Gemini Live",
            type=ProviderType.GEMINI,
            capabilities=ProviderCapabilities(
                supports_realtime=True,
                supports_text=True,
                supports_audio=True,
                supports_multimodal=True,
                supports_function_calling=True,
                supports_streaming=True,
                audio_formats=[AudioFormat.PCM16],
                max_session_duration=3600,
                cost_tier="standard",
            ),
            available_models=[
                # Real-time voice capable (bidiGenerateContent) - standard API key
                "models/gemini-2.0-flash-exp",  # Default - supports real-time voice
                # Standard models (text/generateContent only)
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                # TTS Preview models (text-to-speech only, not real-time)
                "gemini-2.5-flash-preview-tts",
            ],
            is_configured=bool(self._settings.gemini_api_key),
        )

        # Register Deepgram segmented provider (legacy)
        self._providers[ProviderType.DEEPGRAM] = ProviderInfo(
            id="deepgram",
            name="Deepgram Segmented Pipeline (Legacy)",
            type=ProviderType.DEEPGRAM,
            capabilities=ProviderCapabilities(
                supports_realtime=False,
                supports_text=True,
                supports_audio=True,
                supports_multimodal=False,
                supports_function_calling=False,
                supports_streaming=True,
                audio_formats=[AudioFormat.PCM16, AudioFormat.ULAW],
                max_session_duration=None,
                cost_tier="standard",
            ),
            available_models=["nova-2", "whisper"],
            is_configured=bool(self._settings.deepgram_api_key and self._settings.gemini_api_key),
        )

        # Register Deepgram Nova 3 Voice Agent provider
        self._providers[ProviderType.DEEPGRAM_NOVA3] = ProviderInfo(
            id="deepgram_nova3",
            name="Deepgram Nova 3 Voice Agent",
            type=ProviderType.DEEPGRAM_NOVA3,
            capabilities=ProviderCapabilities(
                supports_realtime=True,
                supports_text=True,
                supports_audio=True,
                supports_multimodal=False,
                supports_function_calling=True,
                supports_streaming=True,
                audio_formats=[AudioFormat.PCM16, AudioFormat.ULAW],
                max_session_duration=None,
                cost_tier="premium",
            ),
            available_models=["nova-3"],
            is_configured=bool(self._settings.deepgram_api_key),
        )

        # Register Twilio adapter
        self._telephony[TelephonyType.TWILIO] = TelephonyInfo(
            id="twilio",
            name="Twilio",
            type=TelephonyType.TWILIO,
            capabilities=ProviderCapabilities(
                supports_realtime=True,
                supports_text=False,
                supports_audio=True,
                supports_multimodal=False,
                supports_function_calling=False,
                supports_streaming=True,
                audio_formats=[AudioFormat.ULAW, AudioFormat.PCM16],
                max_session_duration=14400,
                cost_tier="standard",
            ),
            is_configured=bool(
                self._settings.twilio_account_sid and self._settings.twilio_auth_token
            ),
            is_primary=False,  # Optional fallback
        )

        # Register Telnyx adapter
        self._telephony[TelephonyType.TELNYX] = TelephonyInfo(
            id="telnyx",
            name="Telnyx",
            type=TelephonyType.TELNYX,
            capabilities=ProviderCapabilities(
                supports_realtime=True,
                supports_text=False,
                supports_audio=True,
                supports_multimodal=False,
                supports_function_calling=False,
                supports_streaming=True,
                audio_formats=[AudioFormat.PCM16],
                max_session_duration=None,
                cost_tier="standard",
            ),
            is_configured=bool(self._settings.telnyx_api_key),
            is_primary=True,  # Default primary
        )

        logger.info(f"Provider registry initialized with {len(self._providers)} providers")

    def list_providers(self) -> list[ProviderInfo]:
        """List all registered AI providers.

        Returns:
            list[ProviderInfo]: List of provider information
        """
        return list(self._providers.values())

    def list_telephony_adapters(self) -> list[TelephonyInfo]:
        """List all registered telephony adapters.

        Returns:
            list[TelephonyInfo]: List of telephony adapter information
        """
        return list(self._telephony.values())

    def get_provider_info(self, provider_type: ProviderType) -> ProviderInfo | None:
        """Get information about a specific provider.

        Args:
            provider_type: Provider type

        Returns:
            ProviderInfo or None: Provider information if found
        """
        return self._providers.get(provider_type)

    def get_telephony_info(self, telephony_type: TelephonyType) -> TelephonyInfo | None:
        """Get information about a specific telephony adapter.

        Args:
            telephony_type: Telephony adapter type

        Returns:
            TelephonyInfo or None: Telephony information if found
        """
        return self._telephony.get(telephony_type)

    def create_provider(
        self, provider_type: ProviderType, model: str | None = None
    ) -> RealtimeEndToEndProvider | SegmentedVoiceProvider:
        """Create and configure a provider instance.

        Args:
            provider_type: Provider type to create
            model: Optional model ID override

        Returns:
            Provider instance (RealtimeEndToEndProvider or SegmentedVoiceProvider)

        Raises:
            ValueError: If provider type is invalid or not configured
        """
        provider_info = self.get_provider_info(provider_type)
        if not provider_info:
            raise ValueError(f"Unknown provider type: {provider_type}")

        if not provider_info.is_configured:
            raise ValueError(f"Provider {provider_type} is not configured (missing API keys)")

        # Create provider based on type
        if provider_type == ProviderType.OPENAI:
            use_premium = bool(model and "mini" not in model)
            if not self._settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            return create_openai_provider(
                api_key=self._settings.openai_api_key,
                use_premium=use_premium,
            )

        elif provider_type == ProviderType.GEMINI:
            if not self._settings.gemini_api_key:
                raise ValueError("Gemini API key not configured")
            return create_gemini_provider(api_key=self._settings.gemini_api_key)

        elif provider_type == ProviderType.DEEPGRAM:
            if not self._settings.deepgram_api_key or not self._settings.gemini_api_key:
                raise ValueError("Deepgram and Gemini API keys required")
            return create_deepgram_provider(
                deepgram_api_key=self._settings.deepgram_api_key,
                gemini_api_key=self._settings.gemini_api_key,
            )

        elif provider_type == ProviderType.DEEPGRAM_NOVA3:
            if not self._settings.deepgram_api_key:
                raise ValueError("Deepgram API key not configured")
            # Check if we have an LLM provider configured
            llm_provider = "open_ai" if self._settings.openai_api_key else "gemini"
            llm_model = "gpt-4o-mini" if llm_provider == "open_ai" else "gemini-2.5-flash"
            return create_deepgram_nova3_provider(
                deepgram_api_key=self._settings.deepgram_api_key,
                llm_provider=llm_provider,
                llm_model=llm_model,
                tts_voice="aura-2-thalia-en",
                stt_model="nova-3",
            )

        raise ValueError(f"Provider creation not implemented for {provider_type}")

    def create_telephony_adapter(self, telephony_type: TelephonyType) -> TelephonyAdapter:
        """Create and configure a telephony adapter instance.

        Args:
            telephony_type: Telephony adapter type to create

        Returns:
            TelephonyAdapter: Configured telephony adapter

        Raises:
            ValueError: If adapter type is invalid or not configured
        """
        telephony_info = self.get_telephony_info(telephony_type)
        if not telephony_info:
            raise ValueError(f"Unknown telephony type: {telephony_type}")

        if not telephony_info.is_configured:
            raise ValueError(
                f"Telephony adapter {telephony_type} is not configured (missing credentials)"
            )

        # Create adapter based on type
        if telephony_type == TelephonyType.TWILIO:
            if not self._settings.twilio_account_sid or not self._settings.twilio_auth_token:
                raise ValueError("Twilio credentials not configured")
            return create_twilio_adapter(
                account_sid=self._settings.twilio_account_sid,
                auth_token=self._settings.twilio_auth_token,
            )

        elif telephony_type == TelephonyType.TELNYX:
            if not self._settings.telnyx_api_key:
                raise ValueError("Telnyx API key not configured")
            return create_telnyx_adapter(
                api_key=self._settings.telnyx_api_key,
                public_key=self._settings.telnyx_public_key,
            )

        raise ValueError(f"Adapter creation not implemented for {telephony_type}")

    def select_best_provider(self, requirements: dict[str, Any]) -> ProviderType | None:
        """Select the best provider based on requirements.

        Args:
            requirements: Dictionary of requirements:
                - realtime: bool (need realtime processing)
                - multimodal: bool (need image support)
                - function_calling: bool (need function calls)
                - cost_preference: str (standard/premium)

        Returns:
            ProviderType or None: Best matching provider type
        """
        candidates = []

        for provider_type, info in self._providers.items():
            if not info.is_configured:
                continue

            caps = info.capabilities
            score = 0

            # Check required capabilities
            if requirements.get("realtime") and caps.supports_realtime:
                score += 10
            if requirements.get("multimodal") and caps.supports_multimodal:
                score += 10
            if requirements.get("function_calling") and caps.supports_function_calling:
                score += 5

            # Cost preference
            cost_pref = requirements.get("cost_preference", "standard")
            if cost_pref == "standard" and caps.cost_tier == "standard":
                score += 5
            elif cost_pref == "premium" and caps.cost_tier == "premium":
                score += 5

            if score > 0:
                candidates.append((provider_type, score))

        if not candidates:
            return None

        # Return highest scoring provider
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]


@lru_cache
def get_provider_registry() -> ProviderRegistry:
    """Get cached provider registry instance.

    Returns:
        ProviderRegistry: Singleton registry instance
    """
    return ProviderRegistry()
