from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class TelephonyProvider(str, Enum):
    TWILIO = "twilio"
    TELNYX = "telnyx"


@dataclass(slots=True)
class OutboundCallRequest:
    provider: TelephonyProvider
    from_number: str
    to_number: str
    callback_url: Optional[str] = None
    metadata: Dict[str, str] | None = None


@dataclass(slots=True)
class SmsMessage:
    provider: TelephonyProvider
    from_number: str
    to_number: str
    body: str


__all__ = ["TelephonyProvider", "OutboundCallRequest", "SmsMessage"]
