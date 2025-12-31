import pytest
from unittest.mock import MagicMock, patch

from app.services.telephony import (
    TelephonyProvider,
    TelephonyService,
    TelephonyServiceConfig,
)


class TestTelephonyService:
    def test_init(self):
        config = TelephonyServiceConfig(
            twilio_account_sid="sid",
            twilio_auth_token="token",
            telnyx_api_key="key",
        )
        service = TelephonyService(config)
        assert service.available_providers() == {"twilio": True, "telnyx": True}

    def test_available_providers(self):
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key="key",
        )
        service = TelephonyService(config)
        assert service.available_providers() == {"twilio": False, "telnyx": True}

    @pytest.mark.asyncio
    async def test_create_call(self):
        config = TelephonyServiceConfig(
            twilio_account_sid="sid",
            twilio_auth_token="token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        mock_client = MagicMock()
        mock_client.calls.create.return_value = "call_id"
        with patch("app.services.telephony.TwilioClient", return_value=mock_client):
            result = await service.create_call(
                provider=TelephonyProvider.TWILIO,
                from_number="+123456",
                to_number="+654321",
                callback_url="http://cb",
                metadata={"foo": "bar"},
            )

        assert result == "call_id"
        mock_client.calls.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_sms(self):
        config = TelephonyServiceConfig(
            twilio_account_sid="sid",
            twilio_auth_token="token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        mock_client = MagicMock()
        mock_client.messages.create.return_value = "sms_id"
        with patch("app.services.telephony.TwilioClient", return_value=mock_client):
            result = await service.send_sms(
                provider=TelephonyProvider.TWILIO,
                from_number="+123456",
                to_number="+654321",
                body="Hello",
            )

        assert result == "sms_id"
        mock_client.messages.create.assert_called_once()

    
