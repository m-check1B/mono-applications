"""Telephony adapters."""

__all__ = []

try:
    from telephony_core.adapters.telnyx import TelnyxAdapter, create_telnyx_adapter
    __all__.extend(["TelnyxAdapter", "create_telnyx_adapter"])
except ImportError:
    pass

try:
    from telephony_core.adapters.twilio import TwilioAdapter, create_twilio_adapter
    __all__.extend(["TwilioAdapter", "create_twilio_adapter"])
except ImportError:
    pass
