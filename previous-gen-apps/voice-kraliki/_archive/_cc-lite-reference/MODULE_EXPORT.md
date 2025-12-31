# Voice by Kraliki Module Export (@ocelot-apps/cc-lite)

## Overview
Voice by Kraliki is the **Communications Module** for Ocelot Platform, providing multichannel calling, campaign management, and AI-powered call center capabilities.

## NPM Package Structure

```
@ocelot-apps/cc-lite/
├── backend/app/                   # Python FastAPI backend
│   ├── module.py                 # Main module export
│   ├── core/
│   │   ├── events.py            # Event publisher (RabbitMQ)
│   │   ├── security.py          # Ed25519 JWT auth
│   │   └── config.py            # Configuration
│   ├── routers/                 # API endpoints
│   ├── services/                # Business logic
│   └── models/                  # Database models
├── frontend/src/lib/             # TypeScript/SvelteKit frontend
│   ├── module.ts                # Module config & lifecycle
│   ├── components/index.ts      # UI component exports
│   ├── types.ts                 # TypeScript definitions
│   └── api/                     # API client
└── MODULE_EXPORT.md             # This file
```

## Installation

```bash
npm install @ocelot-apps/cc-lite
# or
pnpm add @ocelot-apps/cc-lite
# or
yarn add @ocelot-apps/cc-lite
```

## Usage in Ocelot Platform

### Backend Integration (Python FastAPI)

#### 1. Mount in API Gateway

```python
# platform/api_gateway/main.py
from fastapi import FastAPI, Request
from cc_lite.backend.app.module import CommsModule

# Initialize platform
app = FastAPI(title="Ocelot Platform API Gateway")

# Initialize communications module in platform mode
comms_module = CommsModule(
    event_publisher=platform_event_bus,
    platform_mode=True  # Trust API Gateway headers
)

# Mount communications module
app.mount("/api/communications", comms_module.get_app())

# Or use as a sub-application with routing
@app.middleware("http")
async def add_user_context(request: Request, call_next):
    # Add platform authentication headers
    if request.url.path.startswith("/api/communications"):
        # Extract from JWT or session
        request.headers.mutablecopy()
        request.headers["X-User-Id"] = current_user.id
        request.headers["X-Org-Id"] = current_user.org_id
        request.headers["X-User-Role"] = current_user.role

    return await call_next(request)
```

#### 2. Event Integration

```python
# platform/event_bus.py
from cc_lite.backend.app.module import CommsModule

# Subscribe to platform events
@event_bus.on("planning.task.completed")
async def notify_task_completion(event):
    """Forward task completion to communications module"""
    await comms_module.handle_event({
        "type": "planning.task.completed",
        "data": event.data,
        "source": "planning-module",
        "timestamp": event.timestamp
    })

@event_bus.on("crm.contact.created")
async def sync_contact(event):
    """Sync new contacts to communications module"""
    await comms_module.handle_event({
        "type": "crm.contact.created",
        "data": event.data,
        "source": "crm-module",
        "timestamp": event.timestamp
    })
```

#### 3. Health Checks

```python
# platform/health.py
from cc_lite.backend.app.module import CommsModule

@app.get("/health/communications")
async def check_comms_health():
    """Check communications module health"""
    return comms_module.get_health()
```

### Frontend Integration (TypeScript/SvelteKit)

#### 1. Register Module in Platform

```typescript
// platform/src/lib/modules/registry.ts
import {
  MODULE_CONFIG,
  metadata,
  CommunicationsModule
} from '@ocelot-apps/cc-lite';

// Register module
platformModules.register({
  ...MODULE_CONFIG,
  instance: new CommunicationsModule({
    eventBus: platformEventBus,
    apiClient: platformApiClient
  })
});
```

#### 2. Use in Platform Routes

```typescript
// platform/src/routes/+layout.svelte
<script lang="ts">
  import { MODULE_CONFIG } from '@ocelot-apps/cc-lite';

  const modules = [
    // ... other modules
    MODULE_CONFIG
  ];
</script>

<nav>
  {#each modules as module}
    <a href={module.routes[0].path}>
      <Icon name={module.icon} />
      {module.displayName}
    </a>
  {/each}
</nav>
```

#### 3. Use Components

```typescript
// platform/src/routes/dashboard/+page.svelte
<script lang="ts">
  import { components } from '@ocelot-apps/cc-lite/components';
  import type { Call, Campaign } from '@ocelot-apps/cc-lite/components';

  let activeCalls: Call[] = [];
  let campaigns: Campaign[] = [];
</script>

<!-- Use exported components (when implemented) -->
<div class="grid grid-cols-2 gap-4">
  <!-- <CallQueue calls={activeCalls} /> -->
  <!-- <CampaignCard campaign={campaigns[0]} /> -->
</div>
```

#### 4. Event Handling

```typescript
// platform/src/lib/modules/communications.ts
import { CommunicationsModule } from '@ocelot-apps/cc-lite';

const commsModule = new CommunicationsModule({
  eventBus: platformEventBus,
  apiClient: fetch
});

// Mount lifecycle
await commsModule.onMount();

// Module will automatically handle platform events
platformEventBus.emit({
  type: 'planning.task.completed',
  data: { taskId: '123', result: 'success' },
  source: 'planning-module',
  timestamp: Date.now()
});
```

## Dual Mode Operation

### Standalone Mode (Development/Testing)

Run Voice by Kraliki as an independent application:

```bash
# Start backend
cd backend
python -m app.module

# Or with uvicorn directly
uvicorn app.module:CommsModule --host 0.0.0.0 --port 3018

# Start frontend
cd frontend
pnpm dev
```

**Features:**
- Full Ed25519 JWT authentication
- Independent database
- Standalone event publisher
- Runs on port 3018 (backend) + 5173 (frontend)

### Platform Mode (Production)

Mounted in Ocelot Platform API Gateway:

```python
# Platform mode initialization
comms = CommsModule(
    event_publisher=platform_event_bus,
    platform_mode=True
)

# Mounted at /api/communications/*
app.mount("/api/communications", comms.get_app())
```

**Features:**
- Trusts API Gateway headers (X-User-Id, X-Org-Id, X-User-Role)
- Shared event bus with platform
- Integrated authentication
- No JWT verification (handled by gateway)

## Event Publishing

### Events Published by Module

```python
# Call events
"comms.call.started"        # New call initiated
"comms.call.answered"       # Call answered
"comms.call.ended"          # Call completed
"comms.call.failed"         # Call failed
"comms.call.transcribed"    # Transcription completed
"comms.call.sentiment"      # Sentiment analysis complete

# Campaign events
"comms.campaign.started"    # Campaign activated
"comms.campaign.completed"  # Campaign finished
"comms.campaign.paused"     # Campaign paused

# Agent events
"comms.agent.available"     # Agent became available
"comms.agent.busy"          # Agent on call
"comms.agent.offline"       # Agent logged off

# Metrics events
"comms.metrics.updated"     # Real-time metrics update
```

### Events Consumed by Module

```python
# Planning module events
"planning.task.completed"   # Task completed → trigger campaign
"planning.project.milestone_reached"  # Milestone → send notifications

# CRM module events
"crm.contact.created"       # New contact → sync to comms
"crm.contact.updated"       # Contact updated → update comms DB

# Task module events
"tasks.assigned"            # Task assigned → notify via call/SMS
"tasks.overdue"             # Task overdue → send reminder
```

## Module Capabilities

- **Voice Calling**: Twilio/Vonage integration with WebRTC
- **SMS Messaging**: Send/receive SMS messages
- **Campaign Management**: Automated outbound calling campaigns
- **Real-time Transcription**: Deepgram-powered call transcription
- **Sentiment Analysis**: AI-powered emotion detection
- **Agent Assist**: Real-time AI suggestions during calls
- **IVR System**: Interactive voice response builder
- **Call Analytics**: Comprehensive reporting and dashboards
- **Team Management**: Multi-team support with permissions
- **Call Recording**: Secure call recording and playback
- **Multi-language**: Support for 8 languages (EN, ES, FR, DE, IT, PT, ZH, JA)

## Configuration

### Environment Variables

```bash
# Platform Mode
PLATFORM_MODE=true              # Enable platform mode
RABBITMQ_URL=amqp://...        # Shared event bus
API_GATEWAY_URL=http://...     # Platform API gateway

# Standalone Mode
JWT_PUBLIC_KEY=...             # Ed25519 public key
JWT_PRIVATE_KEY=...            # Ed25519 private key
DATABASE_URL=postgresql://...  # PostgreSQL connection

# Telephony Providers
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...

VONAGE_API_KEY=...
VONAGE_API_SECRET=...
VONAGE_APPLICATION_ID=...

# AI Services
DEEPGRAM_API_KEY=...           # Transcription
OPENAI_API_KEY=...             # Sentiment analysis
ANTHROPIC_API_KEY=...          # Agent assist (Claude)

# Feature Flags
ENABLE_RECORDING=true
ENABLE_TRANSCRIPTION=true
ENABLE_SENTIMENT=true
ENABLE_AI_ASSIST=true
```

### Database Setup

```bash
# Standalone mode - uses PostgreSQL
alembic upgrade head

# Platform mode - shares platform database
# Migrations handled by platform
```

## API Endpoints

All endpoints are prefixed with `/api/communications` in platform mode:

### Calls
- `GET /api/communications/calls` - List calls
- `POST /api/communications/calls` - Initiate call
- `GET /api/communications/calls/{id}` - Get call details
- `PUT /api/communications/calls/{id}` - Update call
- `DELETE /api/communications/calls/{id}` - End call

### Campaigns
- `GET /api/communications/campaigns` - List campaigns
- `POST /api/communications/campaigns` - Create campaign
- `GET /api/communications/campaigns/{id}` - Get campaign
- `PUT /api/communications/campaigns/{id}` - Update campaign
- `POST /api/communications/campaigns/{id}/start` - Start campaign
- `POST /api/communications/campaigns/{id}/pause` - Pause campaign

### Agents
- `GET /api/communications/agents` - List agents
- `POST /api/communications/agents` - Create agent
- `GET /api/communications/agents/{id}` - Get agent
- `PUT /api/communications/agents/{id}/status` - Update status

### Analytics
- `GET /api/communications/analytics/dashboard` - Dashboard metrics
- `GET /api/communications/analytics/calls` - Call analytics
- `GET /api/communications/analytics/agents` - Agent performance
- `GET /api/communications/analytics/campaigns` - Campaign results

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

# Specific test
pytest tests/unit/test_module.py -v -k "test_platform_mode"
```

### Frontend Tests (Vitest + Playwright)

```bash
cd frontend

# Unit tests
pnpm test:unit

# Integration tests
pnpm test:integration

# E2E tests
pnpm test:e2e

# All tests
pnpm test
```

## Package Exports

```json
{
  "name": "@ocelot-apps/cc-lite",
  "version": "2.0.0",
  "exports": {
    ".": {
      "python": "./backend/app/module.py",
      "default": "./backend/app/module.py"
    },
    "./events": {
      "python": "./backend/app/core/events.py"
    },
    "./security": {
      "python": "./backend/app/core/security.py"
    },
    "./components": {
      "import": "./frontend/src/lib/components/index.ts",
      "types": "./frontend/src/lib/components/index.ts"
    }
  }
}
```

## Deployment

### Standalone Deployment

```bash
# Build frontend
cd frontend && pnpm build

# Run with Docker
docker compose up -d

# Or with PM2
pm2 start ecosystem.config.cjs
```

### Platform Deployment

```bash
# Install as npm package
pnpm add @ocelot-apps/cc-lite

# Import in platform
from cc_lite.backend.app.module import CommsModule

# Mount in gateway
app.mount("/api/communications", comms_module.get_app())
```

## Security Considerations

### Standalone Mode
- Ed25519 JWT authentication
- JWT tokens signed with private key
- Public key verification on each request
- Token expiration: 24 hours
- Refresh tokens: 30 days

### Platform Mode
- No JWT verification (handled by API Gateway)
- Trusts X-User-Id, X-Org-Id headers
- API Gateway must validate all requests
- Rate limiting via gateway
- CORS handled by gateway

### General Security
- All passwords hashed with bcrypt
- API keys encrypted at rest
- Webhook signatures verified (HMAC-SHA256)
- SQL injection protection (SQLAlchemy ORM)
- XSS protection (input sanitization)
- CSRF protection (SameSite cookies)

## Performance

### Benchmarks
- API response time: < 50ms (p95)
- Call initiation: < 500ms
- Transcription latency: < 1s
- WebSocket events: < 100ms
- Database queries: < 20ms

### Scaling
- Horizontal scaling: Add more backend instances
- Load balancing: Nginx/HAProxy
- Database: PostgreSQL with read replicas
- Event bus: RabbitMQ cluster
- Cache: Redis for session storage

## Monitoring & Observability

### Metrics Exposed
- `comms_calls_total` - Total calls handled
- `comms_calls_active` - Active calls
- `comms_call_duration_seconds` - Call duration histogram
- `comms_campaign_success_rate` - Campaign success rate
- `comms_agent_utilization` - Agent utilization percentage

### Health Endpoints
- `GET /health` - Overall health
- `GET /health/db` - Database connection
- `GET /health/redis` - Redis connection
- `GET /health/rabbitmq` - Event bus connection
- `GET /health/twilio` - Twilio API status

## Support & Documentation

- **API Documentation**: `/docs` (FastAPI auto-generated OpenAPI)
- **Repository**: https://github.com/ocelot-platform/cc-lite
- **Issues**: https://github.com/ocelot-platform/cc-lite/issues
- **Changelog**: [CHANGELOG.md](./CHANGELOG.md)
- **Contributing**: [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

MIT License - See [LICENSE](./LICENSE) for details

## Version History

- **2.0.0** - Python FastAPI backend, Ed25519 JWT auth, RabbitMQ events
- **1.0.0** - Initial TypeScript/Node.js version

## Roadmap

- [ ] Voice biometrics authentication
- [ ] Advanced IVR with AI routing
- [ ] Multi-provider telephony failover
- [ ] Real-time call quality monitoring
- [ ] Predictive dialing algorithms
- [ ] WhatsApp Business integration
- [ ] Video calling support
- [ ] Speech analytics dashboard
