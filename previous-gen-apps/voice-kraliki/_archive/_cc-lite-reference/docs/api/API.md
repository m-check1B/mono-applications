# Voice by Kraliki API Documentation

> **Complete tRPC API Reference - 22 Active Routers**

## Overview

Voice by Kraliki provides a comprehensive tRPC-based API for all call center operations. All endpoints use type-safe procedures with Zod validation and automatic TypeScript code generation.

## Base Configuration

```typescript
// Frontend tRPC Client
import { createTRPCProxyClient, httpBatchLink } from '@trpc/client';
import type { AppRouter } from '../server/trpc';

const trpc = createTRPCProxyClient<AppRouter>({
  links: [
    httpBatchLink({
      url: 'http://127.0.0.1:3010/trpc',
      headers: {
        authorization: `Bearer ${token}`,
      },
    }),
  ],
});
```

## Authentication

All protected procedures require JWT authentication via Authorization header or secure cookie.

### Auth Router (`/trpc/auth.*`)

| Procedure | Type | Description | Access |
|-----------|------|-------------|---------|
| `login` | Mutation | User authentication | Public |
| `logout` | Mutation | Session termination | Protected |
| `refresh` | Mutation | Token refresh | Protected |
| `profile` | Query | Current user profile | Protected |
| `changePassword` | Mutation | Password update | Protected |

```typescript
// Login example
const result = await trpc.auth.login.mutate({
  email: 'agent@cc-lite.local',
  password: 'password123'
});

// Get profile
const profile = await trpc.auth.profile.query();
```

## Core Operations

### Call Management (`/trpc/call.*`)

Primary call control and management operations.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `list` | Query | Get all calls | `{ status?, limit?, offset? }` |
| `get` | Query | Get specific call | `{ id: string }` |
| `create` | Mutation | Start new call | `{ phoneNumber, campaignId?, metadata? }` |
| `answer` | Mutation | Answer incoming call | `{ callId: string }` |
| `hangup` | Mutation | End call | `{ callId: string }` |
| `hold` | Mutation | Put call on hold | `{ callId: string }` |
| `transfer` | Mutation | Transfer call | `{ callId: string, targetNumber: string }` |
| `mute` | Mutation | Mute/unmute call | `{ callId: string, muted: boolean }` |
| `startRecording` | Mutation | Begin call recording | `{ callId: string }` |
| `stopRecording` | Mutation | End call recording | `{ callId: string }` |

```typescript
// Start a new call
const call = await trpc.call.create.mutate({
  phoneNumber: '+1234567890',
  campaignId: 'campaign-123',
  metadata: { source: 'manual' }
});

// Answer incoming call
await trpc.call.answer.mutate({ callId: call.id });

// Transfer call
await trpc.call.transfer.mutate({
  callId: call.id,
  targetNumber: '+1987654321'
});
```

### Agent Management (`/trpc/agent.*`)

Agent status, performance, and control operations.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `list` | Query | Get all agents | `{ status?, team? }` |
| `get` | Query | Get agent details | `{ id: string }` |
| `setStatus` | Mutation | Update agent status | `{ status: 'AVAILABLE' \| 'BUSY' \| 'OFFLINE' }` |
| `getStats` | Query | Agent performance stats | `{ agentId: string, period?: string }` |
| `assignCall` | Mutation | Assign call to agent | `{ callId: string, agentId: string }` |

```typescript
// Set agent status
await trpc.agent.setStatus.mutate({ status: 'AVAILABLE' });

// Get agent statistics
const stats = await trpc.agent.getStats.query({
  agentId: 'agent-123',
  period: 'today'
});
```

## AI & Analytics

### AI Services (`/trpc/ai.*`)

AI-powered call analysis and assistance.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `transcribe` | Mutation | Transcribe audio | `{ audioUrl: string, language?: string }` |
| `analyze` | Mutation | Analyze conversation | `{ transcript: string, context? }` |
| `suggest` | Query | Get AI suggestions | `{ callId: string, context: string }` |
| `summarize` | Mutation | Summarize call | `{ callId: string }` |

### Sentiment Analysis (`/trpc/sentiment.*`)

Real-time emotion and sentiment detection.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `analyze` | Mutation | Analyze sentiment | `{ text: string, language?: string }` |
| `stream` | Subscription | Real-time sentiment | `{ callId: string }` |
| `history` | Query | Sentiment history | `{ callId: string }` |

```typescript
// Analyze sentiment
const sentiment = await trpc.sentiment.analyze.mutate({
  text: "I'm really frustrated with this service",
  language: 'en'
});

// Subscribe to real-time sentiment
const unsubscribe = trpc.sentiment.stream.subscribe(
  { callId: 'call-123' },
  {
    onData: (sentiment) => {
      console.log('Sentiment update:', sentiment);
    }
  }
);
```

### Agent Assistance (`/trpc/agent-assist.*`)

AI-powered agent support and suggestions.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `getContextInfo` | Query | Get context for call | `{ callId: string }` |
| `getSuggestions` | Query | Get response suggestions | `{ callId: string, context: string }` |
| `getKnowledgeBase` | Query | Search knowledge base | `{ query: string, category? }` |

## Dashboard & Monitoring

### Dashboard Data (`/trpc/dashboard.*`)

Real-time dashboard metrics and data.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `getMetrics` | Query | Dashboard metrics | `{ period?: string, role: string }` |
| `getActiveCalls` | Query | Active calls overview | `{ agentId?: string }` |
| `getQueueStatus` | Query | Call queue status | `{ queueId?: string }` |
| `getAlerts` | Query | Active alerts | `{ severity?: string }` |

### Analytics (`/trpc/analytics.*`)

Performance analytics and reporting.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `getCallStats` | Query | Call statistics | `{ period: string, filters? }` |
| `getAgentPerformance` | Query | Agent performance | `{ agentId?: string, period: string }` |
| `getConversionRates` | Query | Campaign conversion | `{ campaignId?: string, period: string }` |
| `exportReport` | Mutation | Generate report | `{ type: string, filters: object }` |

## Telephony Integration

### Telephony Router (`/trpc/telephony.*`)

Core telephony operations and provider integration.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `getProviders` | Query | Available providers | `{}` |
| `testConnection` | Mutation | Test provider connection | `{ provider: string }` |
| `getCapabilities` | Query | Provider capabilities | `{ provider: string }` |
| `configureProvider` | Mutation | Update provider config | `{ provider: string, config: object }` |

### Twilio Webhooks (`/trpc/twilio-webhooks.*`)

Twilio-specific webhook handling.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `handleIncoming` | Mutation | Process incoming call | `{ From: string, To: string, CallSid: string }` |
| `handleStatus` | Mutation | Process status update | `{ CallSid: string, CallStatus: string }` |
| `handleRecording` | Mutation | Process recording | `{ RecordingSid: string, CallSid: string }` |

## Campaign Management

### Campaign Router (`/trpc/campaign.*`)

Campaign creation, management, and execution.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `list` | Query | Get all campaigns | `{ status?, limit? }` |
| `create` | Mutation | Create campaign | `{ name: string, config: object }` |
| `start` | Mutation | Start campaign | `{ campaignId: string }` |
| `pause` | Mutation | Pause campaign | `{ campaignId: string }` |
| `getStats` | Query | Campaign statistics | `{ campaignId: string }` |

### Contact Management (`/trpc/contact.*`)

Contact database and list management.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `list` | Query | Get contacts | `{ campaignId?, limit?, offset? }` |
| `create` | Mutation | Add contact | `{ name: string, phone: string, metadata? }` |
| `import` | Mutation | Bulk import contacts | `{ file: File, campaignId: string }` |
| `update` | Mutation | Update contact | `{ id: string, data: object }` |

## Team & Supervision

### Supervisor Router (`/trpc/supervisor.*`)

Supervisor-specific operations and controls.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `getTeamStatus` | Query | Team overview | `{ teamId?: string }` |
| `listenToCall` | Mutation | Listen to active call | `{ callId: string }` |
| `whisperToAgent` | Mutation | Send private message | `{ agentId: string, message: string }` |
| `bargeInCall` | Mutation | Join active call | `{ callId: string }` |

### Team Management (`/trpc/team.*`)

Team organization and management.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `list` | Query | Get all teams | `{}` |
| `create` | Mutation | Create team | `{ name: string, description?: string }` |
| `addMember` | Mutation | Add team member | `{ teamId: string, agentId: string }` |
| `getPerformance` | Query | Team performance | `{ teamId: string, period: string }` |

## System Operations

### Metrics & Monitoring (`/trpc/metrics.*`)

System performance and health metrics.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `getSystemHealth` | Query | System health status | `{}` |
| `getPerformanceMetrics` | Query | Performance metrics | `{ period: string }` |
| `getErrorRates` | Query | Error statistics | `{ service?: string }` |

### Circuit Breaker (`/trpc/circuit-breaker.*`)

Circuit breaker pattern for external services.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `getStatus` | Query | Circuit breaker status | `{ service: string }` |
| `reset` | Mutation | Reset circuit breaker | `{ service: string }` |
| `configure` | Mutation | Update configuration | `{ service: string, config: object }` |

### Application Performance Monitoring (`/trpc/apm.*`)

APM integration and monitoring.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `getTraces` | Query | Get trace data | `{ traceId?: string, limit? }` |
| `getSpans` | Query | Get span details | `{ spanId: string }` |
| `reportError` | Mutation | Report application error | `{ error: object, context: object }` |

## Webhooks & Integration

### General Webhooks (`/trpc/webhooks.*`)

Generic webhook management and processing.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `register` | Mutation | Register webhook | `{ url: string, events: string[], secret?: string }` |
| `list` | Query | Get registered webhooks | `{}` |
| `test` | Mutation | Test webhook delivery | `{ webhookId: string }` |
| `delete` | Mutation | Remove webhook | `{ webhookId: string }` |

### BYOK Features (`/trpc/call-byok.*`)

Bring-Your-Own-Key functionality.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `configureKey` | Mutation | Set API key | `{ service: string, apiKey: string }` |
| `testKey` | Mutation | Validate API key | `{ service: string, apiKey: string }` |
| `getServices` | Query | Available BYOK services | `{}` |

## Additional Services

### IVR System (`/trpc/ivr.*`)

Interactive Voice Response configuration.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `getFlows` | Query | Get IVR flows | `{}` |
| `createFlow` | Mutation | Create IVR flow | `{ name: string, config: object }` |
| `testFlow` | Mutation | Test IVR flow | `{ flowId: string, input: string }` |

### AI Health Monitoring (`/trpc/ai-health.*`)

AI service health and performance monitoring.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `getStatus` | Query | AI services status | `{}` |
| `testModels` | Mutation | Test AI model availability | `{ models: string[] }` |
| `getUsageStats` | Query | AI usage statistics | `{ period: string }` |

### Payments Integration (`/trpc/payments.*`)

Billing and payment processing.

| Procedure | Type | Description | Parameters |
|-----------|------|-------------|------------|
| `getSubscription` | Query | Current subscription | `{}` |
| `getUsage` | Query | Usage metrics | `{ period: string }` |
| `updatePayment` | Mutation | Update payment method | `{ paymentMethodId: string }` |

## Error Handling

All tRPC procedures follow consistent error handling:

```typescript
try {
  const result = await trpc.call.create.mutate(data);
} catch (error) {
  if (error.data?.code === 'UNAUTHORIZED') {
    // Handle authentication error
  } else if (error.data?.code === 'BAD_REQUEST') {
    // Handle validation error
  } else {
    // Handle other errors
  }
}
```

## Type Safety

All procedures are fully type-safe with automatic TypeScript inference:

```typescript
// Input and output types are automatically inferred
const call: {
  id: string;
  phoneNumber: string;
  status: 'RINGING' | 'ANSWERED' | 'ENDED';
  createdAt: Date;
} = await trpc.call.create.mutate({
  phoneNumber: '+1234567890' // TypeScript enforces correct input
});
```

## Real-time Subscriptions

WebSocket-based subscriptions for real-time updates:

```typescript
// Subscribe to call status changes
const unsubscribe = trpc.call.statusUpdates.subscribe(
  { callId: 'call-123' },
  {
    onData: (update) => {
      console.log('Call status changed:', update);
    },
    onError: (error) => {
      console.error('Subscription error:', error);
    }
  }
);

// Cleanup subscription
unsubscribe();
```

## Rate Limiting

API endpoints are rate-limited based on user role:

- **Agent**: 100 requests/minute
- **Supervisor**: 200 requests/minute
- **Admin**: 500 requests/minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

## API Versioning

Current API version: `v1`

Future versions will maintain backward compatibility with proper deprecation notices.