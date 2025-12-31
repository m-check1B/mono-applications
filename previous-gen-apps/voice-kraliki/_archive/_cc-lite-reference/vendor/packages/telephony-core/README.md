# @stack/telephony

Provider-agnostic telephony abstraction supporting Twilio and Telnyx with EU compliance.

## Installation

```bash
pnpm add @stack/telephony
```

## Configuration

```typescript
import { initTelephony } from '@stack/telephony';

// For Twilio
initTelephony({
  provider: 'twilio',
  region: 'eu',
  twilio: {
    accountSid: process.env.STACK_TWILIO_ACCOUNT_SID,
    authToken: process.env.STACK_TWILIO_AUTH_TOKEN,
    region: 'dublin',  // EU region
    edge: 'dublin'     // EU edge location
  }
});

// For Telnyx
initTelephony({
  provider: 'telnyx',
  region: 'eu',
  telnyx: {
    apiKey: process.env.STACK_TELNYX_API_KEY,
    publicKey: process.env.STACK_TELNYX_PUBLIC_KEY // For webhook verification
  }
});
```

## Usage

```typescript
import { telephony } from '@stack/telephony';

// Create outbound call
const callId = await telephony().createOutboundCall({
  from: '+420123456789',
  to: '+420987654321',
  metadata: { userId: '123', campaign: 'support' }
});

// Hangup call
await telephony().hangup(callId);

// Play text-to-speech
await telephony().whisper(callId, 'Your call is being recorded');

// Transfer call
await telephony().transfer(callId, '+420111222333');

// Get recording
const recordingStream = await telephony().getRecording(callId);
```

## Webhook Verification

```typescript
import { telephony } from '@stack/telephony';

// In your webhook handler
app.post('/webhooks/telephony', (req, res) => {
  const rawBody = req.rawBody; // Buffer
  const headers = req.headers;
  
  if (!telephony().verifySignature(rawBody, headers)) {
    return res.status(401).send('Invalid signature');
  }
  
  // Process webhook...
});
```

## Feature Parity

| Feature | Twilio | Telnyx |
|---------|--------|--------|
| Outbound Calls | ✅ | ✅ |
| Webhook Verification | ✅ | ✅ |
| Hangup | ✅ | ✅ |
| Text-to-Speech | ✅ | ✅ |
| Call Transfer | ✅ | ✅ |
| Recordings | ✅ | ✅ |
| WebRTC | Twilio Voice SDK | Telnyx WebRTC SDK |
| EU Region | Dublin | Yes |
| GDPR Compliant | ✅ | ✅ |

## Compliance

- **Recording**: Off by default (EU compliance)
- **Data Residency**: EU region by default
- **PII Protection**: Phone numbers masked in logs
- **Retention**: Configurable per provider

## Environment Variables

### Twilio
```bash
STACK_TWILIO_ACCOUNT_SID=xxx
STACK_TWILIO_AUTH_TOKEN=xxx
STACK_TWILIO_WEBHOOK_URL=https://api.example.com/webhooks/twilio
STACK_TWILIO_STATUS_CALLBACK_URL=https://api.example.com/webhooks/twilio/status
STACK_TWILIO_FROM_NUMBER=+420123456789
```

### Telnyx
```bash
STACK_TELNYX_API_KEY=xxx
STACK_TELNYX_PUBLIC_KEY=xxx
STACK_TELNYX_CONNECTION_ID=xxx
STACK_TELNYX_WEBHOOK_URL=https://api.example.com/webhooks/telnyx
STACK_TELNYX_FROM_NUMBER=+420123456789
```