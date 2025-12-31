from __future__ import annotations

import asyncio

try:
    import telnyx
except ImportError:  # pragma: no cover - optional dependency
    telnyx = None  # type: ignore

from ..errors import TelephonyProviderUnavailable
from ..types import OutboundCallRequest, SmsMessage
from .base import BaseTelephonyProvider


class TelnyxProvider(BaseTelephonyProvider):
    def __init__(self, *, api_key: str | None) -> None:
        super().__init__(enabled=bool(api_key))
        if api_key and telnyx is not None:
            telnyx.api_key = api_key
            self._client = telnyx
        else:
            self._client = None

    def _perform_health_check(self) -> bool:
        return bool(self._client)

    async def create_call(self, request: OutboundCallRequest):
        if not self._client:
            raise TelephonyProviderUnavailable("Telnyx client not initialised")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._client.Calls.create(
                connection_id=request.metadata.get("connection_id") if request.metadata else None,
                to=request.to_number,
                from_=request.from_number,
            ),
        )

    async def send_sms(self, message: SmsMessage):
        if not self._client:
            raise TelephonyProviderUnavailable("Telnyx client not initialised")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._client.Message.create(
                to=message.to_number,
                from_=message.from_number,
                text=message.body,
            ),
        )


__all__ = ["TelnyxProvider"]
