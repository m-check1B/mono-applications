# @ocelot-apps/cc-lite

> Communications Module for Ocelot Platform - Multichannel calling, campaigns, and AI-powered call center

[![Version](https://img.shields.io/npm/v/@ocelot-apps/cc-lite)](https://www.npmjs.com/package/@ocelot-apps/cc-lite)
[![License](https://img.shields.io/npm/l/@ocelot-apps/cc-lite)](https://github.com/ocelot-platform/cc-lite/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)

## Features

- **Voice Calling**: Twilio/Vonage integration with WebRTC
- **SMS Messaging**: Send/receive SMS messages
- **Campaign Management**: Automated outbound calling campaigns
- **Real-time Transcription**: Deepgram-powered call transcription
- **Sentiment Analysis**: AI-powered emotion detection
- **Agent Assist**: Real-time AI suggestions during calls
- **IVR System**: Interactive voice response builder
- **Call Analytics**: Comprehensive reporting and dashboards
- **Team Management**: Multi-team support with permissions
- **Multi-language**: Support for 8 languages

## Installation

```bash
npm install @ocelot-apps/cc-lite
# or
pnpm add @ocelot-apps/cc-lite
# or
yarn add @ocelot-apps/cc-lite
```

## Quick Start

### Backend (Python FastAPI)

```python
from cc_lite.backend.app.module import CommsModule

# Initialize in platform mode
comms = CommsModule(
    event_publisher=platform_event_bus,
    platform_mode=True
)

# Mount in API Gateway
app.mount("/api/communications", comms.get_app())
```

### Frontend (TypeScript/SvelteKit)

```typescript
import { MODULE_CONFIG, CommunicationsModule } from '@ocelot-apps/cc-lite';
import type { Call, Campaign } from '@ocelot-apps/cc-lite/types';

// Initialize module
const commsModule = new CommunicationsModule({
  eventBus: platformEventBus,
  apiClient: platformApiClient
});

// Mount lifecycle
await commsModule.onMount();
```

## Package Exports

### Python Backend

```python
# Main module
from cc_lite.backend.app.module import CommsModule

# Event publisher
from cc_lite.backend.app.core.events import EventPublisher, event_publisher

# Security (Ed25519 JWT)
from cc_lite.backend.app.core.security import Ed25519JWTManager

# Configuration
from cc_lite.backend.app.core.config import settings
```

### TypeScript Frontend

```typescript
// Module configuration
import { MODULE_CONFIG, metadata } from '@ocelot-apps/cc-lite';

// Module class
import { CommunicationsModule } from '@ocelot-apps/cc-lite';

// TypeScript types
import type {
  Call,
  Campaign,
  Agent,
  Analytics,
  Contact,
  Transcript
} from '@ocelot-apps/cc-lite/types';

// Components (when implemented)
// import { CallQueue, CampaignCard } from '@ocelot-apps/cc-lite/components';
```

## Dual Mode Operation

### Standalone Mode

Run as independent application for development:

```bash
# Backend
cd backend
python -m app.module

# Frontend
cd frontend
pnpm dev
```

### Platform Mode

Integrated into Ocelot Platform:

```python
# Platform mode (trusts API Gateway headers)
comms = CommsModule(
    event_publisher=platform_event_bus,
    platform_mode=True
)

# Headers required: X-User-Id, X-Org-Id, X-User-Role
```

## Event Integration

### Events Published

```python
"comms.call.started"      # Call initiated
"comms.call.ended"        # Call completed
"comms.call.transcribed"  # Transcription ready
"comms.campaign.completed" # Campaign finished
"comms.sentiment.analyzed" # Sentiment analysis done
```

### Events Consumed

```python
"planning.task.completed"  # Task done → trigger campaign
"crm.contact.created"      # New contact → sync to comms
"tasks.milestone_reached"  # Milestone → send notifications
```

### Subscribe to Events

```python
# Backend
@event_bus.on("comms.call.ended")
async def handle_call_ended(event):
    print(f"Call ended: {event.data}")
```

```typescript
// Frontend
platformEventBus.on('comms.call.started', (event) => {
  console.log('Call started:', event.data);
});
```

## API Endpoints

All endpoints prefixed with `/api/communications` in platform mode:

### Calls
- `GET /calls` - List calls
- `POST /calls` - Initiate call
- `GET /calls/{id}` - Get call details
- `PUT /calls/{id}` - Update call
- `DELETE /calls/{id}` - End call

### Campaigns
- `GET /campaigns` - List campaigns
- `POST /campaigns` - Create campaign
- `GET /campaigns/{id}` - Get campaign
- `PUT /campaigns/{id}` - Update campaign
- `POST /campaigns/{id}/start` - Start campaign
- `POST /campaigns/{id}/pause` - Pause campaign

### Agents
- `GET /agents` - List agents
- `POST /agents` - Create agent
- `PUT /agents/{id}/status` - Update status

### Analytics
- `GET /analytics/dashboard` - Dashboard metrics
- `GET /analytics/calls` - Call analytics
- `GET /analytics/agents` - Agent performance

## Configuration

### Environment Variables

```bash
# Platform Mode
PLATFORM_MODE=true
RABBITMQ_URL=amqp://localhost:5672
API_GATEWAY_URL=http://localhost:8000

# Standalone Mode
JWT_PUBLIC_KEY=...
JWT_PRIVATE_KEY=...
DATABASE_URL=postgresql://...

# Telephony
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...

# AI Services
DEEPGRAM_API_KEY=...
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

## TypeScript Types

```typescript
import type {
  Call,
  Campaign,
  Agent,
  Analytics,
  Contact,
  Transcript,
  Team,
  IVRFlow,
  Webhook,
  PlatformEvent,
  ModuleConfig
} from '@ocelot-apps/cc-lite/types';

// Call type
const call: Call = {
  id: '123',
  from_number: '+1234567890',
  to_number: '+0987654321',
  status: 'in-progress',
  direction: 'outbound',
  created_at: '2025-10-05T10:00:00Z'
};

// Campaign type
const campaign: Campaign = {
  id: '456',
  name: 'Q4 Outreach',
  status: 'active',
  type: 'outbound',
  created_at: '2025-10-01T00:00:00Z',
  updated_at: '2025-10-05T10:00:00Z'
};
```

## Testing

### Backend Tests (pytest)

```bash
cd backend

# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Coverage
pytest --cov=app --cov-report=html
```

### Frontend Tests (Vitest + Playwright)

```bash
cd frontend

# Unit tests
pnpm test:unit

# E2E tests
pnpm test:e2e
```

## Platform Integration Example

### Complete Integration

```python
# platform/api_gateway/main.py
from fastapi import FastAPI, Request
from cc_lite.backend.app.module import CommsModule
from platform.core.events import platform_event_bus
from platform.core.auth import get_current_user

app = FastAPI(title="Ocelot Platform")

# Initialize communications
comms = CommsModule(
    event_publisher=platform_event_bus,
    platform_mode=True
)

# Add auth middleware
@app.middleware("http")
async def add_platform_headers(request: Request, call_next):
    if request.url.path.startswith("/api/communications"):
        user = await get_current_user(request)
        request.headers["X-User-Id"] = str(user.id)
        request.headers["X-Org-Id"] = str(user.org_id)
        request.headers["X-User-Role"] = user.role

    return await call_next(request)

# Mount module
app.mount("/api/communications", comms.get_app())

# Event forwarding
@platform_event_bus.on("planning.*")
async def forward_to_comms(event):
    await comms.handle_event(event)
```

```typescript
// platform/src/lib/modules/index.ts
import { MODULE_CONFIG, CommunicationsModule } from '@ocelot-apps/cc-lite';

export const commsModule = new CommunicationsModule({
  eventBus: platformEventBus,
  apiClient: fetch
});

// Mount on platform startup
await commsModule.onMount();

// Register in navigation
export const modules = [
  MODULE_CONFIG,
  // ... other modules
];
```

## Documentation

- [Module Export Guide](./MODULE_EXPORT.md) - Complete NPM package documentation
- [Platform Integration Guide](./PLATFORM_INTEGRATION.md) - Integration examples
- [API Documentation](http://localhost:3018/docs) - OpenAPI/Swagger docs (when running)

## Architecture

### Backend (Python FastAPI)
- **Framework**: FastAPI 0.110+
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Auth**: Ed25519 JWT (python-jose)
- **Events**: RabbitMQ (aio-pika)
- **Telephony**: Twilio/Vonage SDKs
- **AI**: OpenAI, Anthropic, Deepgram

### Frontend (TypeScript/SvelteKit)
- **Framework**: SvelteKit 2.0
- **Language**: TypeScript 5.0+
- **UI**: Tailwind CSS
- **API**: Fetch API
- **State**: Svelte stores

## Security

### Standalone Mode
- Ed25519 JWT authentication
- Token expiration: 24 hours
- Refresh tokens: 30 days
- Bcrypt password hashing

### Platform Mode
- Trusts API Gateway headers
- X-User-Id, X-Org-Id validation
- No JWT verification
- Rate limiting via gateway

## Performance

- API response: < 50ms (p95)
- Call initiation: < 500ms
- Transcription: < 1s latency
- WebSocket events: < 100ms

## Module Metadata

```typescript
import { metadata } from '@ocelot-apps/cc-lite';

console.log(metadata);
// {
//   version: '2.0.0',
//   author: 'Ocelot Platform',
//   description: 'Multichannel communications module',
//   capabilities: [
//     'voice_calls',
//     'sms_messaging',
//     'campaigns',
//     'call_analytics',
//     'sentiment_analysis',
//     'real_time_transcription',
//     'ai_agent_assist',
//     'ivr_system',
//     'call_recording',
//     'team_management'
//   ]
// }
```

## Support

- **Repository**: https://github.com/ocelot-platform/cc-lite
- **Issues**: https://github.com/ocelot-platform/cc-lite/issues
- **Documentation**: https://docs.ocelot-platform.com/modules/communications

## License

MIT License - See [LICENSE](./LICENSE) for details

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.

---

**Built for Ocelot Platform** | Python FastAPI + SvelteKit + AI
