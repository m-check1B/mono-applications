"""
Telephony Service Unit Tests
Coverage target: 100% of telephony.py
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from app.services.telephony import (
    TelephonyService,
    TelephonyServiceConfig,
    TelnyxProvider,
)
from vendor.telephony_core import TelephonyProvider, TelephonyProviderUnavailable


class TestTelnyxProvider:
    """Test TelnyxProvider class."""

    def test_init(self):
        """Test TelnyxProvider initialization."""
        provider = TelnyxProvider(api_key="test-key")
        assert provider.api_key == "test-key"

    @pytest.mark.asyncio
    async def test_create_call_raises(self):
        """Test create_call raises unavailable error."""
        provider = TelnyxProvider(api_key="test-key")

        with pytest.raises(TelephonyProviderUnavailable) as exc_info:
            await provider.create_call(
                from_number="+1234567890",
                to_number="+0987654321"
            )

        assert "Telnyx" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_sms_raises(self):
        """Test send_sms raises unavailable error."""
        provider = TelnyxProvider(api_key="test-key")

        with pytest.raises(TelephonyProviderUnavailable) as exc_info:
            await provider.send_sms(
                from_number="+1234567890",
                to_number="+0987654321",
                body="Test message"
            )

        assert "Telnyx" in str(exc_info.value)


class TestTelephonyServiceConfig:
    """Test TelephonyServiceConfig dataclass."""

    def test_config_all_none(self):
        """Test config with all None values."""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key=None
        )

        assert config.twilio_account_sid is None
        assert config.twilio_auth_token is None
        assert config.telnyx_api_key is None

    def test_config_with_twilio(self):
        """Test config with Twilio credentials."""
        config = TelephonyServiceConfig(
            twilio_account_sid="AC123",
            twilio_auth_token="token123",
            telnyx_api_key=None
        )

        assert config.twilio_account_sid == "AC123"
        assert config.twilio_auth_token == "token123"

    def test_config_with_telnyx(self):
        """Test config with Telnyx API key."""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key="telnyx-key"
        )

        assert config.telnyx_api_key == "telnyx-key"


class TestTelephonyService:
    """Test TelephonyService class."""

    def test_available_providers_none(self):
        """Test no providers available."""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key=None
        )
        service = TelephonyService(config)

        result = service.available_providers()

        assert result["twilio"] is False
        assert result["telnyx"] is False

    def test_available_providers_twilio_only(self):
        """Test Twilio available."""
        config = TelephonyServiceConfig(
            twilio_account_sid="AC123",
            twilio_auth_token="token",
            telnyx_api_key=None
        )
        service = TelephonyService(config)

        result = service.available_providers()

        assert result["twilio"] is True
        assert result["telnyx"] is False

    def test_available_providers_telnyx_only(self):
        """Test Telnyx available."""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key="telnyx-key"
        )
        service = TelephonyService(config)

        result = service.available_providers()

        assert result["twilio"] is False
        assert result["telnyx"] is True

    def test_available_providers_both(self):
        """Test both providers available."""
        config = TelephonyServiceConfig(
            twilio_account_sid="AC123",
            twilio_auth_token="token",
            telnyx_api_key="telnyx-key"
        )
        service = TelephonyService(config)

        result = service.available_providers()

        assert result["twilio"] is True
        assert result["telnyx"] is True

    def test_available_providers_twilio_partial(self):
        """Test Twilio with only SID (no token)."""
        config = TelephonyServiceConfig(
            twilio_account_sid="AC123",
            twilio_auth_token=None,
            telnyx_api_key=None
        )
        service = TelephonyService(config)

        result = service.available_providers()

        assert result["twilio"] is False


class TestTelephonyServiceCreateCall:
    """Test create_call method."""

    @pytest.mark.asyncio
    async def test_create_call_twilio_not_configured(self):
        """Test create_call with Twilio not configured."""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key=None
        )
        service = TelephonyService(config)

        with pytest.raises(TelephonyProviderUnavailable) as exc_info:
            await service.create_call(
                provider=TelephonyProvider.TWILIO,
                from_number="+1234567890",
                to_number="+0987654321"
            )

        assert "Twilio" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_call_twilio_sdk_missing(self):
        """Test create_call with Twilio SDK not installed."""
        config = TelephonyServiceConfig(
            twilio_account_sid="AC123",
            twilio_auth_token="token",
            telnyx_api_key=None
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient", None):
            with pytest.raises(TelephonyProviderUnavailable) as exc_info:
                await service.create_call(
                    provider=TelephonyProvider.TWILIO,
                    from_number="+1234567890",
                    to_number="+0987654321"
                )

            assert "SDK" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_call_telnyx_not_configured(self):
        """Test create_call with Telnyx not configured."""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key=None
        )
        service = TelephonyService(config)

        with pytest.raises(TelephonyProviderUnavailable) as exc_info:
            await service.create_call(
                provider=TelephonyProvider.TELNYX,
                from_number="+1234567890",
                to_number="+0987654321"
            )

        assert "Telnyx" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_call_unsupported_provider(self):
        """Test create_call with unsupported provider."""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key=None
        )
        service = TelephonyService(config)

        # Create a mock provider with unsupported value
        mock_provider = MagicMock()
        mock_provider.value = "unsupported"

        with pytest.raises(TelephonyProviderUnavailable) as exc_info:
            await service.create_call(
                provider=mock_provider,
                from_number="+1234567890",
                to_number="+0987654321"
            )

        assert "Unsupported" in str(exc_info.value)


class TestTelephonyServiceSendSms:
    """Test send_sms method."""

    @pytest.mark.asyncio
    async def test_send_sms_twilio_not_configured(self):
        """Test send_sms with Twilio not configured."""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key=None
        )
        service = TelephonyService(config)

        with pytest.raises(TelephonyProviderUnavailable) as exc_info:
            await service.send_sms(
                provider=TelephonyProvider.TWILIO,
                from_number="+1234567890",
                to_number="+0987654321",
                body="Test"
            )

        assert "Twilio" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_sms_twilio_sdk_missing(self):
        """Test send_sms with Twilio SDK not installed."""
        config = TelephonyServiceConfig(
            twilio_account_sid="AC123",
            twilio_auth_token="token",
            telnyx_api_key=None
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient", None):
            with pytest.raises(TelephonyProviderUnavailable) as exc_info:
                await service.send_sms(
                    provider=TelephonyProvider.TWILIO,
                    from_number="+1234567890",
                    to_number="+0987654321",
                    body="Test"
                )

            assert "SDK" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_sms_telnyx_not_configured(self):
        """Test send_sms with Telnyx not configured."""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key=None
        )
        service = TelephonyService(config)

        with pytest.raises(TelephonyProviderUnavailable) as exc_info:
            await service.send_sms(
                provider=TelephonyProvider.TELNYX,
                from_number="+1234567890",
                to_number="+0987654321",
                body="Test"
            )

        assert "Telnyx" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_sms_unsupported_provider(self):
        """Test send_sms with unsupported provider."""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key=None
        )
        service = TelephonyService(config)

        mock_provider = MagicMock()
        mock_provider.value = "unsupported"

        with pytest.raises(TelephonyProviderUnavailable) as exc_info:
            await service.send_sms(
                provider=mock_provider,
                from_number="+1234567890",
                to_number="+0987654321",
                body="Test"
            )

        assert "Unsupported" in str(exc_info.value)
