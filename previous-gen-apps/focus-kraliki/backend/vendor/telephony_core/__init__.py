"""Telephony core stub module for testing"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict


class CallDirection(str, Enum):
    """Call direction enum stub"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallStatus(str, Enum):
    """Call status enum stub"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class TelephonyProvider(str, Enum):
    """Telephony provider enum stub"""
    TWILIO = "twilio"
    TELNYX = "telnyx"
    VAPI = "vapi"


class TelephonyProviderUnavailable(Exception):
    """Telephony provider unavailable exception stub"""
    pass


@dataclass
class OutboundCallRequest:
    """Outbound call request stub"""
    provider: TelephonyProvider
    from_number: str
    to_number: str
    callback_url: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class SmsMessage:
    """SMS message stub"""
    provider: TelephonyProvider
    from_number: str
    to_number: str
    body: str


class Call:
    """Call stub"""
    pass


class TelephonyManager:
    """Telephony manager stub"""
    def __init__(self, *args, **kwargs):
        self.available_providers = {}

    @classmethod
    def from_config(cls, **kwargs):
        return cls()
