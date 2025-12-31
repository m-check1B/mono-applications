"""Voice providers for voice-core.

Real-time voice AI providers (native audio-to-audio):
- GeminiLiveProvider (PRIMARY - best latency, multimodal)
- OpenAIRealtimeProvider (SECONDARY - hedge option)

For telephony (Telnyx, Twilio): use telephony-core package
For transcription (Deepgram): use transcription-core package
"""

from voice_core.providers.gemini import GeminiLiveProvider, create_gemini_provider

__all__ = [
    "GeminiLiveProvider",
    "create_gemini_provider",
]

# OpenAI provider
try:
    from voice_core.providers.openai import OpenAIRealtimeProvider, create_openai_provider
    __all__.extend(["OpenAIRealtimeProvider", "create_openai_provider"])
except ImportError:
    pass
