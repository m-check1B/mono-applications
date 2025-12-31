"""Telephony Core - Unified telephony adapters for Platform 2026.

Supports:
- Telnyx (recommended - native PCM, cheaper)
- Twilio (industry standard)
"""

from telephony_core.base import (
    AudioChunk,
    AudioFormat,
    CallDirection,
    CallInfo,
    CallState,
    TelephonyAdapter,
    TelephonyCapabilities,
)

__all__ = [
    # Base types
    "AudioChunk",
    "AudioFormat",
    "CallDirection",
    "CallInfo",
    "CallState",
    "TelephonyAdapter",
    "TelephonyCapabilities",
]

# Telnyx adapter
try:
    from telephony_core.adapters.telnyx import TelnyxAdapter, create_telnyx_adapter
    __all__.extend(["TelnyxAdapter", "create_telnyx_adapter"])
except ImportError:
    pass

# Twilio adapter
try:
    from telephony_core.adapters.twilio import TwilioAdapter, create_twilio_adapter
    __all__.extend(["TwilioAdapter", "create_twilio_adapter"])
except ImportError:
    pass
