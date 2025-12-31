# Telephony Core

Unified telephony adapters for Platform 2026.

## Providers

| Provider | Audio Format | Recommendation |
|----------|--------------|----------------|
| **Telnyx** | Native PCM16 | Recommended (47% cheaper) |
| **Twilio** | u-law | Industry standard |

## Installation

```bash
# Core only
pip install telephony-core

# With Telnyx (recommended)
pip install telephony-core[telnyx]

# With Twilio
pip install telephony-core[twilio]

# All adapters
pip install telephony-core[all]
```

## Quick Start

### Telnyx (Recommended)

```python
from telephony_core import TelnyxAdapter, CallInfo

# Create adapter
adapter = TelnyxAdapter(
    api_key="your-api-key",
    public_key="your-webhook-public-key",  # Optional
)

# Make outbound call
call = await adapter.setup_call({
    "connection_id": "your-connection-id",
    "from_number": "+15551234567",
    "to_number": "+15559876543",
    "stream_url": "wss://your-server.com/stream",
})

print(f"Call ID: {call.call_id}")

# Answer inbound call
await adapter.answer_call(call_id, stream_url)

# End call
await adapter.end_call(call_id)

# Cleanup
await adapter.close()
```

### Twilio

```python
from telephony_core import TwilioAdapter

adapter = TwilioAdapter(
    account_sid="your-account-sid",
    auth_token="your-auth-token",
)

# Make call with TwiML URL
call = await adapter.setup_call({
    "from_number": "+15551234567",
    "to_number": "+15559876543",
    "twiml_url": "https://your-server.com/twiml",
})

# Or with inline TwiML
call = await adapter.setup_call({
    "from_number": "+15551234567",
    "to_number": "+15559876543",
    "twiml": "<Response><Say>Hello!</Say></Response>",
})
```

## Audio Conversion

Both adapters handle audio format conversion:

```python
# Convert from telephony to PCM16
audio_chunk = await adapter.convert_audio_from_telephony(raw_bytes)
# audio_chunk.format == AudioFormat.PCM16
# audio_chunk.sample_rate == 8000

# Convert from PCM16 to telephony format
telephony_bytes = await adapter.convert_audio_to_telephony(audio_chunk)
```

## Webhook Handling

```python
# Validate webhook signature
is_valid = await adapter.validate_webhook(
    signature=request.headers["X-Signature"],
    payload=request.body,
)

# Handle webhook event
result = await adapter.handle_webhook(
    event_type="call.answered",
    payload=request.json(),
)
```

## Integration with Voice Core

Use with `voice-core` for AI-powered voice calls:

```python
from telephony_core import TelnyxAdapter
from voice_core import GeminiLiveProvider, WebSocketBridge

telephony = TelnyxAdapter(api_key="...")
voice = GeminiLiveProvider(api_key="...")

bridge = WebSocketBridge(voice, telephony)
await bridge.start(config)
```
