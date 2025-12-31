# @stack-2025/deepgram-agent-core

Complete Deepgram Voice Agent API integration for Stack 2025. Enables real-time voice-to-voice conversations with built-in LLM orchestration, conversation management, and function calling.

## 🚀 Features

- **Voice-to-Voice Conversations**: Complete speech-to-text, LLM processing, and text-to-speech pipeline
- **Multi-Provider LLM Support**: OpenAI GPT, Anthropic Claude, and Deepgram native models
- **Advanced Event System**: Comprehensive event handling with TypeScript types
- **Function Calling**: Built-in support for custom function execution
- **Auto-Reconnection**: Robust connection management with keep-alive
- **Conversation Context**: Automatic conversation history and context management
- **Industry Presets**: Pre-configured setups for healthcare, finance, customer service, etc.
- **TypeScript First**: Complete type safety and IntelliSense support

## 📦 Installation

```bash
pnpm add @stack-2025/deepgram-agent-core
```

## 🔑 Environment Setup

```bash
# Required
DEEPGRAM_API_KEY=your_deepgram_api_key

# Optional - for specific LLM providers
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## 🎯 Quick Start

```typescript
import { 
  DeepgramVoiceAgent, 
  PresetConfigs, 
  StandardEventHandlers 
} from '@stack-2025/deepgram-agent-core';

// Create agent with preset configuration
const agent = new DeepgramVoiceAgent(
  PresetConfigs.customerService().build(),
  { api_key: process.env.DEEPGRAM_API_KEY! }
);

// Set up event handlers
agent.on('UtteranceEnd', (event) => {
  console.log('User said:', event.data.alternatives[0]?.transcript);
});

agent.on('AgentSpeaking', () => {
  console.log('Agent is responding...');
});

// Register function handlers
agent.onFunction('get_current_time', async () => {
  return { time: new Date().toISOString() };
});

// Connect and start conversation
await agent.connect();

// Send audio data (from microphone, WebRTC, etc.)
agent.sendAudio(audioBuffer);
```

## 🛠️ Custom Configuration

```typescript
import { 
  DeepgramVoiceAgent,
  createVoiceAgentConfig,
  LLMProviders,
  VoiceModels,
  FunctionDefinitions
} from '@stack-2025/deepgram-agent-core';

// Build custom configuration
const config = createVoiceAgentConfig()
  .listen({
    model: 'nova-2-conversational',
    language: 'en',
    smart_format: true
  })
  .think(LLMProviders.anthropic({
    model: 'claude-3-5-sonnet-20241022',
    temperature: 0.7,
    system_prompt: 'You are a helpful assistant.',
    functions: [
      FunctionDefinitions.getCurrentTime(),
      FunctionDefinitions.getWeather()
    ]
  }))
  .speak(VoiceModels.english.asteria)
  .build();

const agent = new DeepgramVoiceAgent(config, {
  api_key: process.env.DEEPGRAM_API_KEY!,
  auto_reconnect: true,
  conversation_context: true
});
```

## 🎭 Industry Presets

### Customer Service

```typescript
const agent = new DeepgramVoiceAgent(
  PresetConfigs.customerService().build(),
  { api_key: process.env.DEEPGRAM_API_KEY! }
);
```

### Healthcare

```typescript
const agent = new DeepgramVoiceAgent(
  PresetConfigs.medicalConsultation().build(),
  { api_key: process.env.DEEPGRAM_API_KEY! }
);
```

### Financial Services

```typescript
const agent = new DeepgramVoiceAgent(
  PresetConfigs.financialServices().build(),
  { api_key: process.env.DEEPGRAM_API_KEY! }
);
```

### Drive-Thru

```typescript
const agent = new DeepgramVoiceAgent(
  PresetConfigs.driveThru().build(),
  { api_key: process.env.DEEPGRAM_API_KEY! }
);
```

## 🔧 Function Calling

### Built-in Functions

```typescript
import { FunctionDefinitions } from '@stack-2025/deepgram-agent-core';

// Add built-in functions
agent.addFunctions([
  FunctionDefinitions.getCurrentTime(),
  FunctionDefinitions.getWeather(),
  FunctionDefinitions.sendEmail(),
  FunctionDefinitions.scheduleEvent()
]);

// Handle function calls
agent.onFunction('get_weather', async ({ location, units }) => {
  // Call your weather API
  const weather = await getWeatherData(location, units);
  return weather;
});
```

### Custom Functions

```typescript
// Define custom function
const orderPizzaFunction = FunctionDefinitions.custom(
  'order_pizza',
  'Order a pizza with specified toppings',
  {
    type: 'object',
    properties: {
      size: { type: 'string', enum: ['small', 'medium', 'large'] },
      toppings: { type: 'string' },
      delivery_address: { type: 'string' }
    },
    required: ['size', 'delivery_address']
  }
);

agent.addFunctions([orderPizzaFunction]);

// Handle the function call
agent.onFunction('order_pizza', async ({ size, toppings, delivery_address }) => {
  const order = await pizzaService.createOrder({
    size,
    toppings: toppings?.split(',') || [],
    address: delivery_address
  });
  
  return {
    order_id: order.id,
    estimated_time: order.estimatedDelivery,
    total: order.total
  };
});
```

## 📡 Event Handling

### Basic Events

```typescript
// Conversation flow events
agent.on('UserStartedSpeaking', () => {
  console.log('User started speaking');
});

agent.on('UserStoppedSpeaking', () => {
  console.log('User stopped speaking');
});

agent.on('UtteranceEnd', (event) => {
  const transcript = event.data.alternatives[0]?.transcript;
  console.log('Transcript:', transcript);
});

agent.on('AgentThinking', () => {
  console.log('Agent is processing...');
});

agent.on('AgentSpeaking', () => {
  console.log('Agent is responding...');
});

// Connection events
agent.on('connected', () => {
  console.log('Connected to Deepgram Voice Agent');
});

agent.on('disconnected', () => {
  console.log('Disconnected from Deepgram Voice Agent');
});

// Error handling
agent.on('Error', (event) => {
  console.error('Error:', event.data.error);
});
```

### Advanced Event Handlers

```typescript
import { StandardEventHandlers } from '@stack-2025/deepgram-agent-core';

// Create transcript collector
const transcriptCollector = StandardEventHandlers.createTranscriptCollector();
agent.on('UtteranceEnd', transcriptCollector.handler);

// Get all transcripts
const allTranscripts = transcriptCollector.getTranscripts();

// Create conversation state tracker
const stateTracker = StandardEventHandlers.createStateTracker();
agent.on('UserStartedSpeaking', stateTracker.handler);
agent.on('UserStoppedSpeaking', stateTracker.handler);
agent.on('AgentThinking', stateTracker.handler);
agent.on('AgentSpeaking', stateTracker.handler);

// Check current state
const state = stateTracker.getState();
console.log('Is user speaking:', state.isUserSpeaking);
```

## 🔄 Connection Management

### Auto-Reconnection

```typescript
const agent = new DeepgramVoiceAgent(config, {
  api_key: process.env.DEEPGRAM_API_KEY!,
  auto_reconnect: true,
  max_reconnect_attempts: 5,
  reconnect_interval: 1000 // Start with 1 second, exponential backoff
});

// Handle reconnection events
agent.on('reconnecting', ({ attempt, delay }) => {
  console.log(`Reconnecting attempt ${attempt} in ${delay}ms`);
});

agent.on('reconnectFailed', () => {
  console.log('All reconnection attempts failed');
});
```

### Keep-Alive Configuration

```typescript
const agent = new DeepgramVoiceAgent(config, {
  api_key: process.env.DEEPGRAM_API_KEY!,
  keep_alive: {
    enabled: true,
    interval: 30000, // 30 seconds
    timeout: 5000,   // 5 seconds
    max_retries: 3
  }
});
```

## 🎙️ Audio Integration

### Browser Audio (WebRTC)

```typescript
// Get user microphone
const stream = await navigator.mediaDevices.getUserMedia({ 
  audio: {
    sampleRate: 16000,
    channelCount: 1,
    echoCancellation: true,
    noiseSuppression: true
  } 
});

const audioContext = new AudioContext({ sampleRate: 16000 });
const source = audioContext.createMediaStreamSource(stream);
const processor = audioContext.createScriptProcessor(4096, 1, 1);

processor.onaudioprocess = (event) => {
  const inputData = event.inputBuffer.getChannelData(0);
  const pcm16 = new Int16Array(inputData.length);
  
  for (let i = 0; i < inputData.length; i++) {
    pcm16[i] = Math.max(-32768, Math.min(32767, Math.floor(inputData[i] * 32768)));
  }
  
  agent.sendAudio(Buffer.from(pcm16.buffer));
};

source.connect(processor);
processor.connect(audioContext.destination);
```

### Node.js Audio (File/Stream)

```typescript
import fs from 'fs';

// Send audio file
const audioData = fs.readFileSync('audio.wav');
agent.sendAudio(audioData);

// Or stream audio
const audioStream = fs.createReadStream('audio.wav');
audioStream.on('data', (chunk) => {
  agent.sendAudio(chunk);
});
```

## 🏢 Industry-Specific Examples

### Healthcare Virtual Assistant

```typescript
import { IndustryProviders } from '@stack-2025/deepgram-agent-core';

const config = createVoiceAgentConfig()
  .listen({ model: 'nova-2-medical' })
  .think(IndustryProviders.healthcare.claude())
  .speak(VoiceModels.english.athena)
  .build();

const agent = new DeepgramVoiceAgent(config, options);

// Add healthcare-specific functions
agent.addFunctions([
  FunctionDefinitions.scheduleEvent(),
  FunctionDefinitions.custom('check_symptoms', 'Check symptoms against medical database', {
    type: 'object',
    properties: {
      symptoms: { type: 'string' },
      severity: { type: 'string', enum: ['mild', 'moderate', 'severe'] }
    }
  })
]);

agent.onFunction('check_symptoms', async ({ symptoms, severity }) => {
  // IMPORTANT: Always recommend consulting healthcare professionals
  return {
    recommendation: 'Please consult with a healthcare professional for proper diagnosis',
    general_info: 'General information about symptoms...',
    urgency: severity === 'severe' ? 'Seek immediate medical attention' : 'Schedule appointment'
  };
});
```

### Financial Services Bot

```typescript
const config = createVoiceAgentConfig()
  .listen({ model: 'nova-2-finance' })
  .think(IndustryProviders.financial.claude())
  .speak(VoiceModels.english.zeus)
  .build();

agent.addFunctions([
  FunctionDefinitions.custom('check_balance', 'Check account balance', {
    type: 'object',
    properties: {
      account_number: { type: 'string' }
    },
    required: ['account_number']
  }),
  FunctionDefinitions.custom('transfer_funds', 'Transfer funds between accounts', {
    type: 'object',
    properties: {
      from_account: { type: 'string' },
      to_account: { type: 'string' },
      amount: { type: 'number' }
    },
    required: ['from_account', 'to_account', 'amount']
  })
]);
```

## 📊 Conversation Analytics

```typescript
// Get conversation context
const context = agent.getContext();

if (context) {
  console.log('Conversation ID:', context.conversation_id);
  console.log('Total turns:', context.metadata.total_turns);
  console.log('Duration:', Date.now() - context.metadata.started_at);
  console.log('Messages:', context.messages);
  console.log('Functions called:', context.functions_called);
}

// Clear context to start fresh
agent.clearContext();
```

## 🔍 Debugging & Monitoring

```typescript
// Enable comprehensive logging
agent.on('*', StandardEventHandlers.createLogger('[VoiceAgent]'));

// Monitor connection state
agent.on('stateChange', ({ from, to }) => {
  console.log(`Connection state: ${from} -> ${to}`);
});

// Track errors and warnings
agent.on('Error', StandardEventHandlers.createErrorHandler((error, description) => {
  // Send to monitoring service
  monitoringService.reportError(error, description);
}));

// Get current state
console.log('Current state:', agent.getState());
console.log('Is connected:', agent.isConnected());
```

## 🧪 Testing

```typescript
import { DeepgramVoiceAgent, PresetConfigs } from '@stack-2025/deepgram-agent-core';

describe('Voice Agent Tests', () => {
  let agent: DeepgramVoiceAgent;

  beforeEach(() => {
    agent = new DeepgramVoiceAgent(
      PresetConfigs.customerService().build(),
      { api_key: 'test-key' }
    );
  });

  test('should handle transcript events', async () => {
    const transcripts: string[] = [];
    
    agent.on('UtteranceEnd', (event) => {
      transcripts.push(event.data.alternatives[0]?.transcript);
    });

    // Simulate events for testing
    agent.getEmitter().emitEvent({
      type: 'UtteranceEnd',
      timestamp: Date.now(),
      data: {
        channel: 0,
        alternatives: [{ transcript: 'Hello world', confidence: 0.9, words: [] }]
      }
    });

    expect(transcripts).toContain('Hello world');
  });
});
```

## 📚 API Reference

### DeepgramVoiceAgent

Main class for voice agent interactions.

#### Constructor
- `new DeepgramVoiceAgent(config: AgentConfig, options: VoiceAgentOptions)`

#### Methods
- `connect(): Promise<void>` - Connect to Deepgram
- `disconnect(): Promise<void>` - Disconnect from Deepgram
- `sendAudio(data: Buffer): void` - Send audio data
- `sendText(text: string): void` - Send text message
- `on(event, handler): this` - Register event handler
- `onFunction(name, handler): this` - Register function handler
- `getState(): ConnectionState` - Get connection state
- `isConnected(): boolean` - Check if connected
- `getContext(): ConversationContext` - Get conversation context
- `updateConfig(config): void` - Update configuration
- `addFunctions(functions): void` - Add function definitions

### Configuration Classes

- `VoiceAgentConfigBuilder` - Fluent configuration builder
- `LLMProviders` - LLM provider configurations
- `VoiceModels` - Voice model presets
- `PresetConfigs` - Industry-specific presets

### Event Types

- `UserStartedSpeaking`, `UserStoppedSpeaking`
- `SpeechStarted`, `UtteranceEnd`
- `AgentThinking`, `AgentSpeaking`
- `ConversationStarted`, `FunctionCall`
- `Error`, `Warning`, `Metadata`

## 🛡️ Error Handling

```typescript
try {
  await agent.connect();
} catch (error) {
  if (error instanceof ConnectionError) {
    console.error('Connection failed:', error.message);
  } else if (error instanceof ConfigurationError) {
    console.error('Configuration error:', error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

## 📄 License

MIT

## 🤝 Contributing

Part of the Stack 2025 ecosystem. Follow Stack 2025 development standards.

## 🔗 Related Packages

- `@stack-2025/ai-providers-core` - Multi-provider AI integration
- `@stack-2025/telephony-core` - Telephony integration
- `@stack-2025/chat-handler-core` - Chat conversation management
- `@stack-2025/notification-core` - Real-time notifications