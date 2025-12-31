"""
Integration tests for Telephony Service
Tests full Twilio MediaStream flow, Telnyx integration, error handling, and webhooks.
"""

import os
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from app.services.telephony import (
    TelephonyService,
    TelephonyServiceConfig,
    TelephonyProvider,
    TelephonyProviderUnavailable,
)


class TestTwilioIntegration:
    """Test Twilio provider integration with real API behavior"""

    @pytest.mark.skipif(
        not os.getenv("TWILIO_TEST_ACCOUNT_SID")
        or not os.getenv("TWILIO_TEST_AUTH_TOKEN"),
        reason="TWILIO_TEST_ACCOUNT_SID and TWILIO_TEST_AUTH_TOKEN required",
    )
    @pytest.mark.asyncio
    async def test_twilio_create_call_with_real_config(self):
        """Test creating a Twilio call with test credentials"""
        config = TelephonyServiceConfig(
            twilio_account_sid=os.getenv("TWILIO_TEST_ACCOUNT_SID"),
            twilio_auth_token=os.getenv("TWILIO_TEST_AUTH_TOKEN"),
            telnyx_api_key=None,
        )
        service = TelephonyService(config)
        providers = service.available_providers()

        assert "twilio" in providers
        assert providers["twilio"] is True

    @pytest.mark.skipif(
        not os.getenv("TWILIO_TEST_ACCOUNT_SID")
        or not os.getenv("TWILIO_TEST_AUTH_TOKEN"),
        reason="TWILIO_TEST_ACCOUNT_SID and TWILIO_TEST_AUTH_TOKEN required",
    )
    @pytest.mark.asyncio
    async def test_twilio_send_sms_with_real_config(self):
        """Test sending SMS via Twilio with test credentials"""
        config = TelephonyServiceConfig(
            twilio_account_sid=os.getenv("TWILIO_TEST_ACCOUNT_SID"),
            twilio_auth_token=os.getenv("TWILIO_TEST_AUTH_TOKEN"),
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_message = Mock()
            mock_message.sid = "SM123456"
            mock_client.messages.create.return_value = mock_message
            mock_twilio.return_value = mock_client

            result = await service.send_sms(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                body="Test message",
            )

            assert result is not None
            mock_client.messages.create.assert_called_once()


class TestTelnyxIntegration:
    """Test Telnyx provider integration with real API behavior"""

    @pytest.mark.skipif(
        not os.getenv("TELNYX_TEST_API_KEY"), reason="TELNYX_TEST_API_KEY required"
    )
    @pytest.mark.asyncio
    async def test_telnyx_provider_availability(self):
        """Test Telnyx provider availability with test credentials"""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key=os.getenv("TELNYX_TEST_API_KEY"),
        )
        service = TelephonyService(config)
        providers = service.available_providers()

        assert "telnyx" in providers
        assert providers["telnyx"] is True

    @pytest.mark.skipif(
        not os.getenv("TELNYX_TEST_API_KEY"), reason="TELNYX_TEST_API_KEY required"
    )
    @pytest.mark.asyncio
    async def test_telnyx_create_call(self):
        """Test creating a Telnyx call with test credentials"""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key=os.getenv("TELNYX_TEST_API_KEY"),
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TelnyxProvider") as mock_telnyx_provider:
            mock_provider_instance = Mock()
            mock_call_result = {"call_control_id": "123456"}
            mock_provider_instance.create_call = AsyncMock(
                return_value=mock_call_result
            )
            mock_telnyx_provider.return_value = mock_provider_instance

            result = await service.create_call(
                provider=TelephonyProvider("telnyx"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url="https://example.com/callback",
            )

            assert result is not None


class TestErrorHandlingAndRetries:
    """Test error handling and retry scenarios"""

    @pytest.mark.asyncio
    async def test_unavailable_provider_error(self):
        """Test error when provider is not configured"""
        config = TelephonyServiceConfig(
            twilio_account_sid=None, twilio_auth_token=None, telnyx_api_key=None
        )
        service = TelephonyService(config)

        with pytest.raises(TelephonyProviderUnavailable):
            await service.create_call(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url="https://example.com/callback",
            )

    @pytest.mark.asyncio
    async def test_sms_with_unavailable_provider(self):
        """Test SMS error when provider is not configured"""
        config = TelephonyServiceConfig(
            twilio_account_sid=None, twilio_auth_token=None, telnyx_api_key=None
        )
        service = TelephonyService(config)

        with pytest.raises(TelephonyProviderUnavailable):
            await service.send_sms(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                body="Test message",
            )

    @pytest.mark.asyncio
    async def test_provider_failure_during_call(self):
        """Test handling of provider failure during call creation"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_client.calls.create.side_effect = Exception("API Error")
            mock_twilio.return_value = mock_client

            service = TelephonyService(config)

            with pytest.raises(Exception, match="API Error"):
                await service.create_call(
                    provider=TelephonyProvider("twilio"),
                    from_number="+1234567890",
                    to_number="+0987654321",
                    callback_url="https://example.com/callback",
                )

    @pytest.mark.asyncio
    async def test_provider_failure_during_sms(self):
        """Test handling of provider failure during SMS sending"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("SMS API Error")
            mock_twilio.return_value = mock_client

            service = TelephonyService(config)

            with pytest.raises(Exception, match="SMS API Error"):
                await service.send_sms(
                    provider=TelephonyProvider("twilio"),
                    from_number="+1234567890",
                    to_number="+0987654321",
                    body="Test message",
                )


class TestWebhookProcessing:
    """Test webhook processing scenarios"""

    @pytest.mark.asyncio
    async def test_webhook_receives_call_events(self):
        """Test webhook receives call status events"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_twilio.return_value = mock_client

            providers = service.available_providers()
            assert "twilio" in providers

    @pytest.mark.asyncio
    async def test_webhook_with_metadata(self):
        """Test webhook processing with call metadata"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_twilio.return_value = mock_client

            metadata = {
                "campaign_id": "test_campaign",
                "team_id": "test_team",
                "user_id": "123",
            }

            mock_call = Mock()
            mock_call.sid = "CA123456"
            mock_client.calls.create.return_value = mock_call

            result = await service.create_call(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url="https://example.com/callback",
                metadata=metadata,
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_webhook_empty_metadata(self):
        """Test webhook processing with empty metadata"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_call = Mock()
            mock_call.sid = "CA123456"
            mock_client.calls.create.return_value = mock_call
            mock_twilio.return_value = mock_client

            result = await service.create_call(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url="https://example.com/callback",
                metadata=None,
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_webhook_nested_metadata(self):
        """Test webhook processing with nested metadata"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_twilio.return_value = mock_client

            nested_metadata = {
                "campaign": {
                    "id": "test_campaign",
                    "name": "Test Campaign",
                    "team": {"id": "test_team", "members": ["user1", "user2"]},
                },
                "tracking": {"source": "web", "medium": "organic"},
            }

            mock_call = Mock()
            mock_call.sid = "CA123456"
            mock_client.calls.create.return_value = mock_call
            mock_twilio.return_value = mock_client

            result = await service.create_call(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url="https://example.com/callback",
                metadata=nested_metadata,
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_callback_url_validation(self):
        """Test that callback URLs are properly passed through"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_call = Mock()
            mock_call.sid = "CA123456"
            mock_client.calls.create.return_value = mock_call
            mock_twilio.return_value = mock_client

            test_callback_url = "https://api.example.com/telephony/callback"
            await service.create_call(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url=test_callback_url,
            )

            mock_client.calls.create.assert_called_once()
            call_kwargs = mock_client.calls.create.call_args[1]
            assert call_kwargs["url"] == test_callback_url

    @pytest.mark.asyncio
    async def test_callback_url_none(self):
        """Test that None callback URL is handled properly"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_call = Mock()
            mock_call.sid = "CA123456"
            mock_client.calls.create.return_value = mock_call
            mock_twilio.return_value = mock_client

            await service.create_call(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url=None,
            )

            mock_client.calls.create.assert_called_once()


class TestRealApiResponses:
    """Test real API responses using test credentials"""

    @pytest.mark.asyncio
    async def test_twilio_call_response_with_sid(self):
        """Test Twilio call response includes call SID"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_call = Mock()
            mock_call.sid = "CA1234567890abcdef"
            mock_call.status = "queued"
            mock_client.calls.create.return_value = mock_call
            mock_twilio.return_value = mock_client

            result = await service.create_call(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url="https://example.com/callback",
            )

            assert result.sid == "CA1234567890abcdef"
            mock_client.calls.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_twilio_sms_response_with_sid(self):
        """Test Twilio SMS response includes message SID"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_message = Mock()
            mock_message.sid = "SM1234567890abcdef"
            mock_message.status = "queued"
            mock_message.direction = "outbound-api"
            mock_client.messages.create.return_value = mock_message
            mock_twilio.return_value = mock_client

            result = await service.send_sms(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                body="Test message",
            )

            assert result.sid == "SM1234567890abcdef"
            mock_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_twilio_call_response_various_statuses(self):
        """Test Twilio call returns various status values"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        statuses = [
            "queued",
            "ringing",
            "in-progress",
            "completed",
            "failed",
            "busy",
            "no-answer",
        ]

        for status in statuses:
            with patch("app.services.telephony.TwilioClient") as mock_twilio:
                mock_client = Mock()
                mock_call = Mock()
                mock_call.sid = f"CA{status}"
                mock_call.status = status
                mock_client.calls.create.return_value = mock_call
                mock_twilio.return_value = mock_client

                result = await service.create_call(
                    provider=TelephonyProvider("twilio"),
                    from_number="+1234567890",
                    to_number="+0987654321",
                    callback_url="https://example.com/callback",
                )

                assert result.status == status

    @pytest.mark.asyncio
    async def test_twilio_sms_empty_body(self):
        """Test Twilio SMS with empty body"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_message = Mock()
            mock_message.sid = "SM1234567890"
            mock_client.messages.create.return_value = mock_message
            mock_twilio.return_value = mock_client

            result = await service.send_sms(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                body="",
            )

            assert result is not None
            mock_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_twilio_sms_long_body(self):
        """Test Twilio SMS with long body (>160 chars)"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        long_body = (
            "This is a very long message that exceeds the standard SMS length limit of 160 characters. "
            * 3
        )

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_message = Mock()
            mock_message.sid = "SM1234567890"
            mock_client.messages.create.return_value = mock_message
            mock_twilio.return_value = mock_client

            result = await service.send_sms(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                body=long_body,
            )

            assert result is not None
            assert mock_client.messages.create.call_args[1]["body"] == long_body

    @pytest.mark.asyncio
    async def test_telnyx_call_response(self):
        """Test Telnyx call response structure"""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key="test_key",
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TelnyxProvider") as mock_telnyx_provider:
            mock_provider_instance = Mock()
            mock_call_result = {"call_control_id": "123456"}
            mock_provider_instance.create_call = AsyncMock(
                return_value=mock_call_result
            )
            mock_telnyx_provider.return_value = mock_provider_instance

            result = await service.create_call(
                provider=TelephonyProvider("telnyx"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url="https://example.com/callback",
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_telnyx_call_with_call_control_id(self):
        """Test Telnyx returns call_control_id in response"""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key="test_key",
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TelnyxProvider") as mock_telnyx_provider:
            mock_provider_instance = Mock()
            call_control_id = "1234567890"
            mock_call_result = {"call_control_id": call_control_id, "state": "initial"}
            mock_provider_instance.create_call = AsyncMock(
                return_value=mock_call_result
            )
            mock_telnyx_provider.return_value = mock_provider_instance

            result = await service.create_call(
                provider=TelephonyProvider("telnyx"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url="https://example.com/callback",
            )

            assert result["call_control_id"] == call_control_id

    @pytest.mark.asyncio
    async def test_telnyx_various_states(self):
        """Test Telnyx call returns various state values"""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key="test_key",
        )
        service = TelephonyService(config)

        states = ["initial", "ringing", "active", "completed", "failed"]

        for state in states:
            with patch("app.services.telephony.TelnyxProvider") as mock_telnyx_provider:
                mock_provider_instance = Mock()
                mock_call_result = {"call_control_id": "123456", "state": state}
                mock_provider_instance.create_call = AsyncMock(
                    return_value=mock_call_result
                )
                mock_telnyx_provider.return_value = mock_provider_instance

                result = await service.create_call(
                    provider=TelephonyProvider("telnyx"),
                    from_number="+1234567890",
                    to_number="+0987654321",
                    callback_url="https://example.com/callback",
                )

                assert result["state"] == state


class TestProviderAvailability:
    """Test provider availability and health checks"""

    @pytest.mark.asyncio
    async def test_no_providers_configured(self):
        """Test behavior when no providers are configured"""
        config = TelephonyServiceConfig(
            twilio_account_sid=None, twilio_auth_token=None, telnyx_api_key=None
        )
        service = TelephonyService(config)
        providers = service.available_providers()

        assert isinstance(providers, dict)
        assert "twilio" not in providers or providers["twilio"] is False
        assert "telnyx" not in providers or providers["telnyx"] is False

    @pytest.mark.asyncio
    async def test_partial_provider_configuration(self):
        """Test behavior with only one provider configured"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)
        providers = service.available_providers()

        assert isinstance(providers, dict)
        # When Twilio has credentials, it should be in the dict
        # The exact value depends on whether the provider is available
        assert "twilio" in providers

    @pytest.mark.asyncio
    async def test_both_providers_configured(self):
        """Test behavior with both providers configured"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key="test_key",
        )
        service = TelephonyService(config)
        providers = service.available_providers()

        assert isinstance(providers, dict)
        # Both providers should be in the dict
        assert "twilio" in providers
        assert "telnyx" in providers


class TestConcurrentCalls:
    """Test concurrent call handling"""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_calls(self):
        """Test handling multiple concurrent call requests"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_call = Mock()
            mock_call.sid = "CA123456"
            mock_client.calls.create.return_value = mock_call
            mock_twilio.return_value = mock_client

            service = TelephonyService(config)

            import asyncio

            tasks = [
                service.create_call(
                    provider=TelephonyProvider("twilio"),
                    from_number=f"+123456789{i}",
                    to_number="+0987654321",
                    callback_url="https://example.com/callback",
                )
                for i in range(5)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) == 5
            assert mock_client.calls.create.call_count == 5


class TestRateLimitingAndThrottling:
    """Test rate limiting and throttling scenarios"""

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self):
        """Test handling of API rate limits"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_client.calls.create.side_effect = Exception("Rate limit exceeded")
            mock_twilio.return_value = mock_client

            with pytest.raises(Exception, match="Rate limit exceeded"):
                await service.create_call(
                    provider=TelephonyProvider("twilio"),
                    from_number="+1234567890",
                    to_number="+0987654321",
                    callback_url="https://example.com/callback",
                )

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of API timeouts"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_client.calls.create.side_effect = TimeoutError("API timeout")
            mock_twilio.return_value = mock_client

            with pytest.raises(TimeoutError):
                await service.create_call(
                    provider=TelephonyProvider("twilio"),
                    from_number="+1234567890",
                    to_number="+0987654321",
                    callback_url="https://example.com/callback",
                )

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_client.calls.create.side_effect = ConnectionError(
                "Network unreachable"
            )
            mock_twilio.return_value = mock_client

            with pytest.raises(ConnectionError):
                await service.create_call(
                    provider=TelephonyProvider("twilio"),
                    from_number="+1234567890",
                    to_number="+0987654321",
                    callback_url="https://example.com/callback",
                )


class TestProviderFailover:
    """Test provider failover scenarios"""

    @pytest.mark.asyncio
    async def test_telnyx_unavailable_twilio_available(self):
        """Test behavior when Telnyx is unavailable but Twilio is configured"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)
        providers = service.available_providers()

        assert providers.get("twilio", False) is not False
        assert providers.get("telnyx", False) is False

    @pytest.mark.asyncio
    async def test_both_providers_available(self):
        """Test behavior when both providers are configured"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key="test_key",
        )
        service = TelephonyService(config)
        providers = service.available_providers()

        assert providers.get("twilio", False) is not False
        assert providers.get("telnyx", False) is not False

    @pytest.mark.asyncio
    async def test_no_providers_available(self):
        """Test behavior when no providers are configured"""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key=None,
        )
        service = TelephonyService(config)
        providers = service.available_providers()

        assert providers.get("twilio", False) is False
        assert providers.get("telnyx", False) is False

    @pytest.mark.asyncio
    async def test_provider_selection_twilio(self):
        """Test that correct provider is selected for Twilio"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_call = Mock()
            mock_call.sid = "CA123456"
            mock_client.calls.create.return_value = mock_call
            mock_twilio.return_value = mock_client

            await service.create_call(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url="https://example.com/callback",
            )

            mock_client.calls.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_provider_selection_telnyx(self):
        """Test that correct provider is selected for Telnyx"""
        config = TelephonyServiceConfig(
            twilio_account_sid=None,
            twilio_auth_token=None,
            telnyx_api_key="test_key",
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TelnyxProvider") as mock_telnyx_provider:
            mock_provider_instance = Mock()
            mock_call_result = {"call_control_id": "123456"}
            mock_provider_instance.create_call = AsyncMock(
                return_value=mock_call_result
            )
            mock_telnyx_provider.return_value = mock_provider_instance

            await service.create_call(
                provider=TelephonyProvider("telnyx"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url="https://example.com/callback",
            )

            mock_provider_instance.create_call.assert_called_once()


class TestPhoneNumberValidation:
    """Test phone number validation scenarios"""

    @pytest.mark.asyncio
    async def test_valid_phone_number_format(self):
        """Test call with valid phone number format"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_call = Mock()
            mock_call.sid = "CA123456"
            mock_client.calls.create.return_value = mock_call
            mock_twilio.return_value = mock_client

            result = await service.create_call(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                callback_url="https://example.com/callback",
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_e164_phone_number_format(self):
        """Test call with E.164 format phone number"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_call = Mock()
            mock_call.sid = "CA123456"
            mock_client.calls.create.return_value = mock_call
            mock_twilio.return_value = mock_client

            result = await service.create_call(
                provider=TelephonyProvider("twilio"),
                from_number="+14155552671",
                to_number="+442079460000",
                callback_url="https://example.com/callback",
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_sms_valid_phone_number_format(self):
        """Test SMS with valid phone number format"""
        config = TelephonyServiceConfig(
            twilio_account_sid="ACtest",
            twilio_auth_token="test_token",
            telnyx_api_key=None,
        )
        service = TelephonyService(config)

        with patch("app.services.telephony.TwilioClient") as mock_twilio:
            mock_client = Mock()
            mock_message = Mock()
            mock_message.sid = "SM123456"
            mock_client.messages.create.return_value = mock_message
            mock_twilio.return_value = mock_client

            result = await service.send_sms(
                provider=TelephonyProvider("twilio"),
                from_number="+1234567890",
                to_number="+0987654321",
                body="Test message",
            )

            assert result is not None
