# Focus by Kraliki Platform Integration Guide

## Quick Start

### 1. Install Package
```bash
npm install @ocelot-apps/focus-kraliki
```

### 2. Backend Integration (Python)

```python
# main.py - Ocelot Platform API Gateway
from fastapi import FastAPI, Request
from focus_kraliki.backend.app.module import PlanningModule

app = FastAPI(title="Ocelot Platform")

# Initialize Focus by Kraliki in platform mode
planning_module = PlanningModule(
    platform_mode=True,
    event_publisher_instance=platform_event_bus
)

# Mount at /api/planning
app.mount("/api/planning", planning_module.get_app())

# Start event listeners
@app.on_event("startup")
async def startup():
    await planning_module.startup()
    
    # Subscribe to events from other modules
    @platform_event_bus.subscribe("comms.call.ended")
    async def on_call_ended(event):
        await planning_module.handle_event(event)

@app.on_event("shutdown")
async def shutdown():
    await planning_module.shutdown()
```

### 3. Frontend Integration (TypeScript/Svelte)

```typescript
// src/lib/platform/modules.ts
import { MODULE_CONFIG } from '@ocelot-apps/focus-kraliki';

export const platformModules = [
  MODULE_CONFIG,
  // ... other modules
];

// src/routes/planning/+layout.ts
import type { Task, Project } from '@ocelot-apps/focus-kraliki/components';

export async function load({ fetch }) {
  const tasks: Task[] = await fetch('/api/planning/tasks').then(r => r.json());
  return { tasks };
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Ocelot Platform                          │
├─────────────────────────────────────────────────────────────┤
│  API Gateway (FastAPI)                                      │
│  ├─ Authentication (Ed25519 JWT)                            │
│  ├─ Rate Limiting                                           │
│  └─ Request Routing                                         │
├─────────────────────────────────────────────────────────────┤
│  Module: Focus by Kraliki (Planning)        /api/planning/*       │
│  ├─ Tasks API                                               │
│  ├─ Projects API                                            │
│  ├─ Shadow AI                                               │
│  └─ Flow Memory                                             │
├─────────────────────────────────────────────────────────────┤
│  Module: Communications               /api/comms/*          │
│  ├─ Voice Calls                                             │
│  ├─ Campaigns                                               │
│  └─ SMS/Email                                               │
├─────────────────────────────────────────────────────────────┤
│  Module: AI Agents                    /api/agents/*         │
│  ├─ Swarm Coordination                                      │
│  ├─ Workflow Automation                                     │
│  └─ Neural Networks                                         │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    PostgreSQL            Redis Cache         RabbitMQ
   (Shared DB)        (Token Revocation)   (Event Bus)
```

## Event Flow Examples

### Example 1: Call Ended → Create Follow-up Task

```python
# Communications module publishes event
await event_bus.publish({
    "type": "comms.call.ended",
    "timestamp": "2025-10-05T10:00:00Z",
    "user_id": "user_123",
    "org_id": "org_456",
    "data": {
        "call_id": "call_789",
        "outcome": "callback_requested",
        "callback_time": "2025-10-06T14:00:00Z",
        "contact": {
            "name": "John Doe",
            "phone": "+1234567890"
        }
    }
})

# Focus by Kraliki receives and creates task
# backend/app/module.py - handle_event()
async def handle_event(self, event: dict):
    if event["type"] == "comms.call.ended":
        if event["data"]["outcome"] == "callback_requested":
            # Create follow-up task
            task = await create_task(
                user_id=event["user_id"],
                org_id=event["org_id"],
                title=f"Call back {event['data']['contact']['name']}",
                description=f"Scheduled callback at {event['data']['callback_time']}",
                due_date=event["data"]["callback_time"],
                priority="high",
                metadata={
                    "source": "call",
                    "call_id": event["data"]["call_id"]
                }
            )
            
            # Publish task created event
            await event_publisher.publish({
                "type": "planning.task.created",
                "user_id": event["user_id"],
                "org_id": event["org_id"],
                "data": {"task_id": task.id, "source": "call_callback"}
            })
```

### Example 2: Task Completed → Update Campaign

```python
# Focus by Kraliki publishes task completed
await event_bus.publish({
    "type": "planning.task.completed",
    "user_id": "user_123",
    "org_id": "org_456",
    "data": {
        "task_id": "task_789",
        "campaign_id": "campaign_456"  # linked to campaign
    }
})

# Communications module updates campaign progress
@event_bus.subscribe("planning.task.completed")
async def on_task_completed(event):
    if "campaign_id" in event["data"]:
        await update_campaign_progress(
            campaign_id=event["data"]["campaign_id"],
            completed_tasks=1
        )
```

### Example 3: AI Workflow → Auto-create Tasks

```python
# AI Agents module suggests workflow
await event_bus.publish({
    "type": "agents.workflow.suggested",
    "user_id": "user_123",
    "org_id": "org_456",
    "data": {
        "workflow_id": "wf_789",
        "steps": [
            {"action": "Call lead", "priority": "high"},
            {"action": "Send proposal", "priority": "medium"},
            {"action": "Follow up", "priority": "low"}
        ]
    }
})

# Focus by Kraliki creates tasks from workflow
@event_bus.subscribe("agents.workflow.suggested")
async def on_workflow_suggested(event):
    for i, step in enumerate(event["data"]["steps"]):
        await create_task(
            user_id=event["user_id"],
            org_id=event["org_id"],
            title=step["action"],
            priority=step["priority"],
            order=i,
            metadata={
                "source": "ai_workflow",
                "workflow_id": event["data"]["workflow_id"]
            }
        )
```

## Authentication Flow

### Platform Mode (Recommended)

```python
# API Gateway handles authentication
@app.middleware("http")
async def platform_auth_middleware(request: Request, call_next):
    # Extract JWT from Authorization header
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # Verify Ed25519 JWT
    jwt_manager = Ed25519JWTManager()
    payload = jwt_manager.verify_token(token)
    
    # Check Redis revocation
    if await token_blacklist.is_revoked(token):
        raise HTTPException(401, "Token revoked")
    
    # Set platform headers for modules
    request.headers["X-User-Id"] = payload["sub"]
    request.headers["X-Org-Id"] = payload["org_id"]
    request.headers["X-Roles"] = ",".join(payload.get("roles", []))
    
    return await call_next(request)

# Focus by Kraliki trusts headers
# No JWT verification needed in module
```

### Standalone Mode

```python
# Focus by Kraliki performs its own authentication
# backend/app/module.py - _setup_middleware()
@self.app.middleware("http")
async def auth_middleware(request: Request, call_next):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # Verify Ed25519 JWT
    jwt_manager = Ed25519JWTManager()
    payload = jwt_manager.verify_token(token)
    
    # Check Redis revocation
    if await token_blacklist.is_revoked(token):
        raise HTTPException(401, "Token revoked")
    
    request.state.user_id = payload["sub"]
    request.state.org_id = payload["org_id"]
    
    return await call_next(request)
```

## Database Strategy

### Option 1: Shared Database (Recommended)
```python
# All modules share one PostgreSQL database
DATABASE_URL = "postgresql://ocelot:pass@localhost:5432/ocelot_platform"

# Each module uses table prefixes
# Focus by Kraliki: planning_tasks, planning_projects, planning_shadow
# Communications: comms_calls, comms_campaigns
# Agents: agents_swarms, agents_workflows
```

### Option 2: Separate Databases
```python
# Each module has its own database
PLANNING_DB = "postgresql://ocelot:pass@localhost:5432/focus_kraliki"
COMMS_DB = "postgresql://ocelot:pass@localhost:5432/communications"
AGENTS_DB = "postgresql://ocelot:pass@localhost:5432/ai_agents"

# Cross-module queries use events instead of joins
```

## Testing Platform Integration

```bash
# 1. Start dependencies
docker-compose up -d postgres redis rabbitmq

# 2. Start platform in development
cd /path/to/ocelot-platform
python main.py

# 3. Test authentication
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'

# Response: {"access_token": "eyJ0eXAi...", "token_type": "bearer"}

# 4. Test Focus by Kraliki via platform
TOKEN="eyJ0eXAi..."
curl http://localhost:8000/api/planning/tasks \
  -H "Authorization: Bearer $TOKEN"

# 5. Create task via platform
curl -X POST http://localhost:8000/api/planning/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "priority": "high"}'

# 6. Monitor RabbitMQ events
# Check RabbitMQ management UI: http://localhost:15672
# Queue: planning.events
# Exchange: platform.events
```

## Deployment

### Docker Compose
```yaml
version: '3.8'

services:
  platform:
    image: ocelot/platform:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://ocelot:pass@postgres:5432/ocelot
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - postgres
      - redis
      - rabbitmq

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=ocelot
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=ocelot
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
```

## Migration Checklist

- [ ] Install @ocelot-apps/focus-kraliki package
- [ ] Configure shared PostgreSQL database
- [ ] Configure shared Redis instance
- [ ] Configure shared RabbitMQ instance
- [ ] Generate Ed25519 key pair (or reuse platform keys)
- [ ] Update environment variables
- [ ] Mount module at /api/planning in platform
- [ ] Set up event subscriptions
- [ ] Test authentication flow
- [ ] Test event publishing/subscribing
- [ ] Update frontend routing
- [ ] Deploy and monitor

## Performance Optimization

### Redis Caching
```python
# Cache user tasks for 5 minutes
@lru_cache(maxsize=1000, ttl=300)
async def get_user_tasks(user_id: str):
    return await db.query(Task).filter(Task.user_id == user_id).all()
```

### Database Connection Pooling
```python
# SQLAlchemy connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

### Event Publishing
```python
# Async non-blocking event publishing
await event_publisher.publish(event, wait=False)
```

## Monitoring

### Health Checks
```python
# Platform health includes all modules
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "modules": {
            "planning": await planning_module.health_check(),
            "comms": await comms_module.health_check(),
            "agents": await agents_module.health_check()
        }
    }
```

### Metrics
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

task_created_counter = Counter('planning_tasks_created', 'Tasks created')
task_completion_time = Histogram('planning_task_completion_seconds', 'Task completion time')
```

## Next Steps

1. Review MODULE_EXPORT.md for detailed API documentation
2. Check backend/app/module.py for implementation details
3. Explore frontend/src/lib/module.ts for frontend config
4. Test event flow with other modules
5. Set up monitoring and alerting
6. Deploy to production

## Support

For issues or questions:
- Documentation: /docs/
- API Docs: http://localhost:8000/docs
- RabbitMQ Management: http://localhost:15672
