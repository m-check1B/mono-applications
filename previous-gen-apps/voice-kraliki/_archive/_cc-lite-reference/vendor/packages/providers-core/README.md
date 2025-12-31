# @stack-2025/providers-core

Unified provider interfaces for multi-vendor support. Prevents vendor lock-in and enables easy provider switching.

## Why This Exists

Instead of being locked into a single provider (Twilio, OpenAI, etc.), this package provides:
- **Unified interfaces** for all provider types
- **Easy switching** between providers
- **Consistent API** across different vendors
- **TypeScript-first** with full type safety

## Provider Types

### 1. LLM Providers
```typescript
import { LLMProviderFactory, AnthropicClient } from '@stack-2025/providers-core';

// Register provider
LLMProviderFactory.register('anthropic', AnthropicClient);

// Create client
const llm = LLMProviderFactory.create('anthropic', {
  apiKey: process.env.ANTHROPIC_API_KEY
});

// Use same interface regardless of provider
const response = await llm.complete([
  { role: 'user', content: 'Hello!' }
]);
```

**Supported Providers:**
- Anthropic (Claude)
- OpenAI (GPT)
- Google (Gemini)
- Azure OpenAI
- AWS Bedrock
- Local (Ollama)

### 2. Telephony Providers
```typescript
import { TelephonyProviderFactory, TwilioClient } from '@stack-2025/providers-core';

// Register provider
TelephonyProviderFactory.register('twilio', TwilioClient);

// Create client
const phone = TelephonyProviderFactory.create('twilio', {
  accountSid: process.env.TWILIO_ACCOUNT_SID,
  authToken: process.env.TWILIO_AUTH_TOKEN
});

// Same interface for any telephony provider
const call = await phone.makeCall('+1234567890', '+0987654321', {
  url: 'https://example.com/twiml'
});
```

**Supported Providers:**
- Twilio
- Vonage (Nexmo)
- AWS Connect
- Azure Communication Services
- Plivo
- Bandwidth
- SignalWire

### 3. Voice Providers (STT/TTS)
```typescript
import { STTProviderFactory, TTSProviderFactory } from '@stack-2025/providers-core';

// Speech-to-Text
const stt = STTProviderFactory.create('openai-whisper', {
  apiKey: process.env.OPENAI_API_KEY
});

const transcription = await stt.transcribe(audioBuffer, {
  language: 'en'
});

// Text-to-Speech
const tts = TTSProviderFactory.create('elevenlabs', {
  apiKey: process.env.ELEVENLABS_API_KEY
});

const audio = await tts.synthesize('Hello, world!', {
  voice: 'rachel'
});
```

**STT Providers:**
- OpenAI Whisper
- Google Speech-to-Text
- AWS Transcribe
- Azure Speech
- Deepgram
- AssemblyAI
- Rev.ai

**TTS Providers:**
- OpenAI TTS
- Google Text-to-Speech
- AWS Polly
- Azure Speech
- ElevenLabs
- Play.ht
- Murf.ai

### 4. Storage Providers
```typescript
import { StorageProviderFactory } from '@stack-2025/providers-core';

// SQL Database
const db = StorageProviderFactory.create('postgresql', {
  connectionString: process.env.DATABASE_URL
});

// Vector Database
const vectorDb = StorageProviderFactory.create('pinecone', {
  apiKey: process.env.PINECONE_API_KEY
});

// Same interface for CRUD operations
const user = await db.get('users', 'user123');
const results = await vectorDb.vectorSearch('embeddings', {
  vector: [0.1, 0.2, ...],
  topK: 10
});
```

**Supported Storage Types:**
- SQL: PostgreSQL, MySQL, SQLite
- NoSQL: MongoDB, DynamoDB, Firestore
- Vector: Pinecone, Qdrant, Weaviate
- Object: S3, GCS, Azure Blob
- Cache: Redis

## Benefits

1. **No Vendor Lock-in**: Switch providers with a single line change
2. **Consistent API**: Learn once, use everywhere
3. **Type Safety**: Full TypeScript support
4. **Testability**: Easy to mock providers for testing
5. **Cost Optimization**: Switch to cheaper providers easily

## Usage in Apps

```typescript
// In your app configuration
import { providers } from '@stack-2025/providers-core';

// Configure once
providers.configureLLM('anthropic', { apiKey: '...' });
providers.configureTelephony('twilio', { ... });
providers.configureSTT('deepgram', { ... });

// Use anywhere
const llm = providers.getLLM();
const phone = providers.getTelephony();
const stt = providers.getSTT();
```

## Adding New Providers

```typescript
import { BaseLLMClient, LLMProvider } from '@stack-2025/providers-core';

class MyCustomLLM extends BaseLLMClient {
  provider: LLMProvider = 'custom';
  
  async complete(messages, options) {
    // Your implementation
  }
  
  // ... other methods
}

// Register it
LLMProviderFactory.register('custom', MyCustomLLM);
```

## Migration from Direct APIs

Before (locked to OpenAI):
```typescript
import OpenAI from 'openai';
const openai = new OpenAI({ apiKey: '...' });
const completion = await openai.chat.completions.create({...});
```

After (provider-agnostic):
```typescript
import { getLLM } from '@stack-2025/providers-core';
const llm = getLLM(); // Could be OpenAI, Anthropic, etc.
const completion = await llm.complete([...]);
```

## Best Practices

1. **Always use environment variables** for API keys
2. **Set default providers** in your app config
3. **Handle provider-specific features** gracefully
4. **Test with multiple providers** to ensure compatibility
5. **Monitor costs** across different providers

## Future Additions

- Payment providers (Stripe, PayPal, Square)
- Email providers (SendGrid, AWS SES, Postmark)
- SMS providers (separate from telephony)
- Analytics providers (Mixpanel, Amplitude, Segment)
- Monitoring providers (Sentry, DataDog, New Relic)