class VoiceProviderUnavailable(RuntimeError):
    """Raised when a requested provider is not configured or healthy."""


class VoiceSessionNotFound(KeyError):
    """Raised when the requested voice session is not tracked locally."""


__all__ = [
    "VoiceProviderUnavailable",
    "VoiceSessionNotFound",
]
