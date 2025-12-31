from __future__ import annotations

import abc
from typing import Any

from ..types import OutboundCallRequest, SmsMessage


class BaseTelephonyProvider(abc.ABC):
    def __init__(self, *, enabled: bool = True) -> None:
        self._enabled = enabled

    def is_available(self) -> bool:
        return self._enabled and self._perform_health_check()

    def _perform_health_check(self) -> bool:
        return True

    @abc.abstractmethod
    async def create_call(self, request: OutboundCallRequest) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    async def send_sms(self, message: SmsMessage) -> Any:
        raise NotImplementedError


__all__ = ["BaseTelephonyProvider"]
