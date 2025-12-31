"""
Unit tests for Voice Service
Tests voice session management, transcription, and synthesis
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from app.services.voice import VoiceService, VoiceServiceConfig


class TestVoiceServiceConfig:
    """Test VoiceServiceConfig dataclass"""

    def test_config_creation(self):
        """Create config with all fields"""
        config = VoiceServiceConfig(
            gemini_api_key="gemini-key-123",
            gemini_model="gemini-pro",
            openai_api_key="sk-openai-key",
            openai_model="whisper-1",
            openai_tts_model="tts-1",
            deepgram_api_key="deepgram-key",
            deepgram_model="nova-2"
        )
        
        assert config.gemini_api_key == "gemini-key-123"
        assert config.gemini_model == "gemini-pro"
        assert config.openai_api_key == "sk-openai-key"
        assert config.openai_model == "whisper-1"
        assert config.openai_tts_model == "tts-1"
        assert config.deepgram_api_key == "deepgram-key"
        assert config.deepgram_model == "nova-2"

    def test_config_with_none_values(self):
        """Config allows None for optional keys"""
        config = VoiceServiceConfig(
            gemini_api_key=None,
            gemini_model="",
            openai_api_key=None,
            openai_model="",
            openai_tts_model="",
            deepgram_api_key=None,
            deepgram_model=""
        )
        
        assert config.gemini_api_key is None
        assert config.openai_api_key is None
        assert config.deepgram_api_key is None


class TestVoiceServiceInit:
    """Test VoiceService initialization"""

    @patch("app.services.voice.VoiceSessionManager")
    def test_service_initialization(self, mock_manager_class):
        """Service initializes with config"""
        mock_manager = MagicMock()
        mock_manager_class.from_config.return_value = mock_manager
        
        config = VoiceServiceConfig(
            gemini_api_key="key1",
            gemini_model="model1",
            openai_api_key="key2",
            openai_model="model2",
            openai_tts_model="tts-model",
            deepgram_api_key="key3",
            deepgram_model="model3"
        )
        
        service = VoiceService(config)
        
        mock_manager_class.from_config.assert_called_once()
        assert service._manager == mock_manager


class TestAvailableProviders:
    """Test available_providers method"""

    @patch("app.services.voice.VoiceSessionManager")
    def test_available_providers_dict(self, mock_manager_class):
        """Returns dict of available providers"""
        from vendor.voice_core import VoiceProvider

        mock_manager = MagicMock()
        mock_manager.available_providers = {
            VoiceProvider.GEMINI_NATIVE: True,
            VoiceProvider.OPENAI_REALTIME: False,
            VoiceProvider.DEEPGRAM_TRANSCRIPTION: True
        }
        mock_manager_class.from_config.return_value = mock_manager

        config = VoiceServiceConfig(
            gemini_api_key="key", gemini_model="m",
            openai_api_key="key", openai_model="m",
            openai_tts_model="m",
            deepgram_api_key="key", deepgram_model="m"
        )
        service = VoiceService(config)

        providers = service.available_providers()

        assert isinstance(providers, dict)

    @patch("app.services.voice.VoiceSessionManager")
    def test_available_providers_callable(self, mock_manager_class):
        """Handles callable available_providers"""
        from vendor.voice_core import VoiceProvider

        mock_manager = MagicMock()
        mock_manager.available_providers = MagicMock(return_value={
            VoiceProvider.GEMINI_NATIVE: True
        })
        mock_manager_class.from_config.return_value = mock_manager

        config = VoiceServiceConfig(
            gemini_api_key="key", gemini_model="m",
            openai_api_key=None, openai_model="m",
            openai_tts_model="m",
            deepgram_api_key=None, deepgram_model="m"
        )
        service = VoiceService(config)

        providers = service.available_providers()

        assert isinstance(providers, dict)

    @patch("app.services.voice.VoiceSessionManager")
    def test_available_providers_list(self, mock_manager_class):
        """Handles list available_providers"""
        from vendor.voice_core import VoiceProvider

        mock_manager = MagicMock()
        mock_manager.available_providers = [VoiceProvider.GEMINI_NATIVE]
        mock_manager_class.from_config.return_value = mock_manager

        config = VoiceServiceConfig(
            gemini_api_key="key", gemini_model="m",
            openai_api_key=None, openai_model="m",
            openai_tts_model="m",
            deepgram_api_key=None, deepgram_model="m"
        )
        service = VoiceService(config)

        providers = service.available_providers()

        assert isinstance(providers, dict)
