# Voice Core

Real-time AI voice providers for Voice by Kraliki core.

## Package Ecosystem

```
voice-kraliki/packages/
├── voice-core/         # AI voice providers (Gemini, OpenAI)
├── telephony-core/     # Phone adapters (Telnyx, Twilio)
└── transcription-core/ # Transcription (Deepgram)
```

## Providers

| Provider | Role | SDK |
|----------|------|-----|
| **Gemini Live** | Primary | `google-genai` (official) |
| **OpenAI Realtime** | Secondary/hedge | WebSocket |

## Installation

```bash
# Core with Gemini (recommended)
pip install voice-core[gemini]

# With all providers
pip install voice-core[all]

# With telephony and transcription
pip install voice-core[all] telephony-core[all] transcription-core[all]
```

## Quick Start

```python
from voice_core import GeminiLiveProvider, SessionConfig, AudioChunk, AudioFormat

# Create provider
provider = GeminiLiveProvider(api_key="your-api-key")

# Connect
config = SessionConfig(
    model_id="gemini-2.5-flash-preview-native-audio-dialog",
    system_prompt="You are a helpful assistant.",
)
await provider.connect(config)

# Send audio
await provider.send_audio(AudioChunk(
    data=audio_bytes,
    format=AudioFormat.PCM16,
    sample_rate=16000,
))

# Receive responses
async for event in provider.receive_events():
    if event.type == "audio.output":
        play_audio(event.data["audio"])
    elif event.type == "text.output":
        print(event.data["text"])

await provider.disconnect()
```

## With Telephony (Phone Calls)

```python
from voice_core import GeminiLiveProvider, WebSocketBridge
from telephony_core import TelnyxAdapter

# Create components
provider = GeminiLiveProvider(api_key="gemini-key")
telephony = TelnyxAdapter(api_key="telnyx-key")

# Bridge connects them
bridge = WebSocketBridge(provider, telephony)
await bridge.start(config)

# Handle audio bidirectionally
await bridge.handle_telephony_audio(incoming_bytes)
await bridge.process_provider_events(send_to_phone)
```

## Audio Formats

| Direction | Format | Sample Rate |
|-----------|--------|-------------|
| Input (to AI) | PCM16 | 16 kHz |
| Output (from AI) | PCM16 | 24 kHz |

## Related Packages

- **telephony-core**: Telnyx, Twilio phone adapters
- **transcription-core**: Deepgram transcription
