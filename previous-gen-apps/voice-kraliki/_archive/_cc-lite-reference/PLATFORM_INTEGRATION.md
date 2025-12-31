# Voice by Kraliki Platform Integration Guide

## Quick Start Integration

### 1. Install Package

```bash
pnpm add @ocelot-apps/cc-lite
```

### 2. Backend Integration (Python FastAPI)

```python
# platform/api_gateway/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from cc_lite.backend.app.module import CommsModule
from platform.core.events import platform_event_bus
from platform.core.auth import get_current_user

# Initialize platform
app = FastAPI(title="Ocelot Platform API Gateway", version="1.0.0")

# Initialize communications module
comms_module = CommsModule(
    event_publisher=platform_event_bus,
    platform_mode=True  # Enable platform mode
)

# Add authentication middleware
@app.middleware("http")
async def add_platform_headers(request: Request, call_next):
    """Add platform authentication headers to communications requests"""

    if request.url.path.startswith("/api/communications"):
        # Extract user from JWT or session
        try:
            user = await get_current_user(request)

            # Add platform headers
            request.state.user_id = user.id
            request.state.org_id = user.organization_id
            request.state.user_role = user.role

            # Create mutable headers
            headers = dict(request.headers)
            headers["X-User-Id"] = str(user.id)
            headers["X-Org-Id"] = str(user.organization_id)
            headers["X-User-Role"] = user.role

            # Update request headers
            request._headers = headers

        except Exception as e:
            # Authentication failed
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )

    return await call_next(request)

# Mount communications module
app.mount("/api/communications", comms_module.get_app())

# Health check for comms module
@app.get("/health/communications")
async def check_comms_health():
    return comms_module.get_health()
```

### 3. Frontend Integration (TypeScript/SvelteKit)

```typescript
// platform/src/lib/modules/communications/index.ts
import {
  MODULE_CONFIG,
  metadata,
  CommunicationsModule,
  type ModuleConfig
} from '@ocelot-apps/cc-lite';
import type { PlatformEvent } from '@ocelot-apps/cc-lite/types';

// Initialize module
export const commsModule = new CommunicationsModule({
  eventBus: platformEventBus,
  apiClient: platformApiClient
});

// Mount lifecycle
export async function mountCommunications() {
  await commsModule.onMount();
  console.log('Communications module mounted successfully');
}

// Unmount lifecycle
export async function unmountCommunications() {
  await commsModule.onUnmount();
  console.log('Communications module unmounted');
}

// Export configuration for platform registry
export const communicationsConfig: ModuleConfig = MODULE_CONFIG;
```

### 4. Register in Platform

```typescript
// platform/src/lib/modules/registry.ts
import { communicationsConfig, mountCommunications } from './communications';

export const platformModules = [
  {
    id: 'communications',
    config: communicationsConfig,
    mount: mountCommunications,
    permissions: ['CALL_ACCESS', 'CAMPAIGN_MANAGE']
  },
  // ... other modules
];

// Auto-mount on platform startup
export async function initializeModules() {
  for (const module of platformModules) {
    await module.mount();
  }
}
```

### 5. Navigation Integration

```typescript
// platform/src/routes/+layout.svelte
<script lang="ts">
  import { communicationsConfig } from '$lib/modules/communications';
  import { page } from '$app/stores';

  $: isCommsActive = $page.url.pathname.startsWith('/communications');
</script>

<nav class="sidebar">
  <a
    href="/communications/calls"
    class:active={isCommsActive}
    style="color: {communicationsConfig.color}"
  >
    <Icon name={communicationsConfig.icon} />
    <span>{communicationsConfig.displayName}</span>
  </a>
</nav>

<!-- Communications module routes -->
{#if isCommsActive}
  <div class="module-content">
    <slot />
  </div>
{/if}
```

## Event Integration Examples

### Backend Event Handling

```python
# platform/services/event_handlers.py
from platform.core.events import event_bus
from cc_lite.backend.app.module import comms_module

# Planning module events → Communications
@event_bus.on("planning.task.completed")
async def handle_task_completed(event):
    """When a task completes, check if we should trigger a campaign"""

    task_data = event.data

    # Check if task is linked to a campaign
    if task_data.get("campaign_trigger"):
        await comms_module.handle_event({
            "type": "planning.task.completed",
            "data": {
                "task_id": task_data["id"],
                "campaign_id": task_data["campaign_id"],
                "result": task_data["result"]
            },
            "source": "planning-module",
            "timestamp": event.timestamp
        })

# CRM module events → Communications
@event_bus.on("crm.contact.created")
async def sync_contact_to_comms(event):
    """Sync new CRM contacts to communications database"""

    contact = event.data

    await comms_module.handle_event({
        "type": "crm.contact.created",
        "data": {
            "contact_id": contact["id"],
            "phone_number": contact["phone"],
            "email": contact["email"],
            "name": f"{contact['first_name']} {contact['last_name']}"
        },
        "source": "crm-module",
        "timestamp": event.timestamp
    })

# Listen to communications events in other modules
@event_bus.on("comms.call.ended")
async def log_call_to_crm(event):
    """Log completed calls to CRM timeline"""

    call_data = event.data

    # Add call to CRM contact timeline
    await crm_service.add_timeline_event(
        contact_id=call_data["contact_id"],
        event_type="call",
        data={
            "call_id": call_data["call_id"],
            "duration": call_data["duration"],
            "outcome": call_data["outcome"],
            "transcript": call_data.get("transcript"),
            "sentiment": call_data.get("sentiment_score")
        }
    )
```

### Frontend Event Handling

```typescript
// platform/src/lib/modules/communications/events.ts
import { platformEventBus } from '$lib/core/events';
import type { PlatformEvent } from '@ocelot-apps/cc-lite/types';

// Subscribe to call events
platformEventBus.on('comms.call.started', (event: PlatformEvent) => {
  console.log('Call started:', event.data);

  // Show notification
  notifications.show({
    type: 'info',
    title: 'Call Started',
    message: `Call to ${event.data.to_number} initiated`
  });

  // Update real-time dashboard
  dashboardStore.update(state => ({
    ...state,
    activeCalls: [...state.activeCalls, event.data]
  }));
});

// Subscribe to campaign events
platformEventBus.on('comms.campaign.completed', (event: PlatformEvent) => {
  console.log('Campaign completed:', event.data);

  // Show success notification
  notifications.show({
    type: 'success',
    title: 'Campaign Completed',
    message: `Campaign "${event.data.name}" finished with ${event.data.success_rate}% success rate`
  });
});

// Subscribe to sentiment events
platformEventBus.on('comms.call.sentiment', (event: PlatformEvent) => {
  const sentiment = event.data.sentiment_score;

  if (sentiment < 0.3) {
    // Negative sentiment - alert supervisor
    notifications.show({
      type: 'warning',
      title: 'Negative Sentiment Detected',
      message: `Call ${event.data.call_id} has negative sentiment (${sentiment.toFixed(2)})`
    });
  }
});
```

## API Client Integration

### Using Module API from Platform

```typescript
// platform/src/lib/api/communications.ts
import { commsModule } from '$lib/modules/communications';
import type { Call, Campaign } from '@ocelot-apps/cc-lite/types';

export const communicationsApi = {
  // Calls
  async makeCall(params: { to: string; from?: string; campaignId?: string }): Promise<Call> {
    return await commsModule.makeCall(params);
  },

  async getCalls(filters?: any): Promise<Call[]> {
    const response = await fetch('/api/communications/calls', {
      method: 'GET',
      headers: await getAuthHeaders()
    });
    return response.json();
  },

  // Campaigns
  async getCampaigns(filters?: any): Promise<Campaign[]> {
    return await commsModule.getCampaigns(filters);
  },

  async startCampaign(campaignId: string): Promise<Campaign> {
    const response = await fetch(`/api/communications/campaigns/${campaignId}/start`, {
      method: 'POST',
      headers: await getAuthHeaders()
    });
    return response.json();
  }
};

async function getAuthHeaders(): Promise<HeadersInit> {
  const token = await getAccessToken();
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
}
```

## Database Integration

### Shared Database Tables

```python
# platform/database/models.py
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from platform.database import Base

class Organization(Base):
    """Platform organization table"""
    __tablename__ = "organizations"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    # Relationship to communications
    campaigns = relationship("Campaign", back_populates="organization")
    agents = relationship("Agent", back_populates="organization")


# Voice by Kraliki models extend platform models
from cc_lite.backend.app.models import Campaign, Agent

# Campaign links to platform organization
class Campaign(Base):
    # ... campaign fields ...

    org_id = Column(String, ForeignKey("organizations.id"))
    organization = relationship("Organization", back_populates="campaigns")
```

## Permissions & RBAC

### Platform Permission Checks

```python
# platform/api_gateway/main.py
from fastapi import Depends
from platform.core.auth import require_permission

@app.get("/api/communications/campaigns")
async def get_campaigns(
    user = Depends(require_permission("CAMPAIGN_VIEW"))
):
    # User has CAMPAIGN_VIEW permission
    return await comms_service.get_campaigns(user_id=user.id)

@app.post("/api/communications/campaigns/{id}/start")
async def start_campaign(
    id: str,
    user = Depends(require_permission("CAMPAIGN_MANAGE"))
):
    # User has CAMPAIGN_MANAGE permission
    return await comms_service.start_campaign(id, user_id=user.id)
```

### Frontend Permission Guards

```typescript
// platform/src/routes/communications/campaigns/+page.svelte
<script lang="ts">
  import { hasPermission } from '$lib/core/permissions';

  $: canManageCampaigns = hasPermission('CAMPAIGN_MANAGE');
  $: canViewCampaigns = hasPermission('CAMPAIGN_VIEW');
</script>

{#if canViewCampaigns}
  <CampaignList />

  {#if canManageCampaigns}
    <button on:click={createCampaign}>
      Create Campaign
    </button>
  {/if}
{:else}
  <PermissionDenied />
{/if}
```

## Monitoring & Logging

### Platform-Wide Logging

```python
# platform/core/logging.py
from cc_lite.backend.app.core.logger import get_logger

# Communications logs integrate with platform logger
comms_logger = get_logger("communications")

# Set log level from platform config
comms_logger.setLevel(platform_config.LOG_LEVEL)

# Add platform context to all logs
@app.middleware("http")
async def add_log_context(request: Request, call_next):
    with logging_context(
        org_id=request.state.org_id,
        user_id=request.state.user_id,
        module="communications"
    ):
        return await call_next(request)
```

### Metrics Collection

```python
# platform/monitoring/metrics.py
from prometheus_client import Counter, Histogram

# Communications metrics
comms_calls_total = Counter(
    'platform_comms_calls_total',
    'Total calls handled',
    ['org_id', 'status']
)

comms_call_duration = Histogram(
    'platform_comms_call_duration_seconds',
    'Call duration in seconds',
    ['org_id']
)

# Collect from communications module
@event_bus.on("comms.call.ended")
async def record_call_metrics(event):
    comms_calls_total.labels(
        org_id=event.data["org_id"],
        status=event.data["status"]
    ).inc()

    comms_call_duration.labels(
        org_id=event.data["org_id"]
    ).observe(event.data["duration"])
```

## Testing Integration

### Platform Integration Tests

```python
# platform/tests/integration/test_communications.py
import pytest
from fastapi.testclient import TestClient
from platform.main import app
from cc_lite.backend.app.module import comms_module

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(test_user):
    token = create_test_token(test_user)
    return {"Authorization": f"Bearer {token}"}

def test_make_call_through_platform(client, auth_headers):
    """Test making a call through platform API gateway"""

    response = client.post(
        "/api/communications/calls",
        json={
            "to_number": "+1234567890",
            "from_number": "+0987654321"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "id" in data

def test_event_forwarding(client, auth_headers):
    """Test that platform events are forwarded to communications module"""

    # Emit platform event
    await platform_event_bus.emit({
        "type": "planning.task.completed",
        "data": {"task_id": "123", "campaign_id": "456"},
        "source": "planning-module",
        "timestamp": time.time()
    })

    # Verify communications module received it
    # (Check database or mock event handler)
```

## Migration Guide

### Migrating Standalone Voice by Kraliki to Platform

1. **Update environment variables:**
```bash
# Change from standalone to platform mode
PLATFORM_MODE=true
RABBITMQ_URL=amqp://platform-rabbitmq:5672
DATABASE_URL=postgresql://platform-db:5432/platform
```

2. **Update authentication:**
```python
# Remove standalone JWT verification
# Trust platform headers instead
comms_module = CommsModule(platform_mode=True)
```

3. **Integrate event bus:**
```python
# Share platform event bus
from platform.core.events import platform_event_bus

comms_module = CommsModule(
    event_publisher=platform_event_bus,
    platform_mode=True
)
```

4. **Update API calls in frontend:**
```typescript
// Change API base URL
// From: http://localhost:3018/api
// To: /api/communications
const BASE_URL = '/api/communications';
```

## Troubleshooting

### Common Issues

**Issue**: 401 Unauthorized errors
```python
# Solution: Ensure platform headers are set correctly
@app.middleware("http")
async def add_platform_headers(request: Request, call_next):
    if request.url.path.startswith("/api/communications"):
        # Must set these headers
        request.headers["X-User-Id"] = current_user.id
        request.headers["X-Org-Id"] = current_user.org_id
```

**Issue**: Events not being received
```python
# Solution: Check event bus connection
await platform_event_bus.connect()
await comms_module.startup()  # Connects to event bus
```

**Issue**: Database connection errors
```python
# Solution: Ensure database migrations are run
alembic upgrade head

# Or in platform mode, migrations handled by platform
await platform_db.migrate()
```

## Best Practices

1. **Always use platform mode in production**
2. **Share event bus between all modules**
3. **Use platform authentication headers**
4. **Centralize logging and monitoring**
5. **Test integration points thoroughly**
6. **Document custom events**
7. **Version module APIs carefully**
8. **Handle module failures gracefully**

## Support

For integration support:
- GitHub Issues: https://github.com/ocelot-platform/cc-lite/issues
- Platform Docs: https://docs.ocelot-platform.com
- Integration Examples: https://github.com/ocelot-platform/examples
