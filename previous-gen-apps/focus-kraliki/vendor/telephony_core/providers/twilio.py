from __future__ import annotations

import asyncio

try:
    from twilio.rest import Client as TwilioClient
except ImportError:  # pragma: no cover - optional dependency
    TwilioClient = None  # type: ignore

from ..errors import TelephonyProviderUnavailable
from ..types import OutboundCallRequest, SmsMessage
from .base import BaseTelephonyProvider


class TwilioProvider(BaseTelephonyProvider):
    def __init__(self, *, account_sid: str | None, auth_token: str | None) -> None:
        super().__init__(enabled=bool(account_sid and auth_token))
        self.account_sid = account_sid
        self.auth_token = auth_token
        self._client = (
            TwilioClient(account_sid, auth_token) if (account_sid and auth_token and TwilioClient) else None
        )

    def _perform_health_check(self) -> bool:
        return bool(self._client)

    async def create_call(self, request: OutboundCallRequest):
        if not self._client:
            raise TelephonyProviderUnavailable("Twilio client not initialised")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._client.calls.create(
                to=request.to_number,
                from_=request.from_number,
                url=request.callback_url or "https://handler.twilio.com/twiml/EHxxxx",
            ),
        )

    async def send_sms(self, message: SmsMessage):
        if not self._client:
            raise TelephonyProviderUnavailable("Twilio client not initialised")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._client.messages.create(
                to=message.to_number,
                from_=message.from_number,
                body=message.body,
            ),
        )


__all__ = ["TwilioProvider"]
