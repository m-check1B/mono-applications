from __future__ import annotations

from typing import Dict, Optional

from .errors import TelephonyProviderUnavailable
from .providers.base import BaseTelephonyProvider
from .providers.telnyx import TelnyxProvider
from .providers.twilio import TwilioProvider
from .types import OutboundCallRequest, SmsMessage, TelephonyProvider


class TelephonyManager:
    def __init__(
        self,
        *,
        twilio: Optional[TwilioProvider] = None,
        telnyx: Optional[TelnyxProvider] = None,
    ) -> None:
        self._providers: Dict[TelephonyProvider, BaseTelephonyProvider] = {}
        if twilio:
            self._providers[TelephonyProvider.TWILIO] = twilio
        if telnyx:
            self._providers[TelephonyProvider.TELNYX] = telnyx

    @classmethod
    def from_config(
        cls,
        *,
        twilio_sid: Optional[str],
        twilio_token: Optional[str],
        telnyx_api_key: Optional[str],
    ) -> "TelephonyManager":
        twilio_provider = TwilioProvider(account_sid=twilio_sid, auth_token=twilio_token) if twilio_sid and twilio_token else None
        telnyx_provider = TelnyxProvider(api_key=telnyx_api_key) if telnyx_api_key else None
        return cls(twilio=twilio_provider, telnyx=telnyx_provider)

    def is_available(self, provider: TelephonyProvider) -> bool:
        handler = self._providers.get(provider)
        return bool(handler and handler.is_available())

    async def create_call(self, request: OutboundCallRequest):
        handler = self._providers.get(request.provider)
        if not handler:
            raise TelephonyProviderUnavailable(f"Provider {request.provider.value} is not configured")
        return await handler.create_call(request)

    async def send_sms(self, message: SmsMessage):
        handler = self._providers.get(message.provider)
        if not handler:
            raise TelephonyProviderUnavailable(f"Provider {message.provider.value} is not configured")
        return await handler.send_sms(message)

    @property
    def available_providers(self) -> Dict[TelephonyProvider, bool]:
        return {provider: handler.is_available() for provider, handler in self._providers.items()}


__all__ = ["TelephonyManager"]
