# Tools-Core Integration for Voice by Kraliki

**Created**: October 5, 2025
**Status**: Week 6 Implementation
**Component**: SMS Service Integration

---

## Overview

Voice by Kraliki integrates with the `@ocelot-platform/tools-core` package for shared communication services (SMS, Email, Calendar). This enables:

1. **Standalone Mode**: Voice by Kraliki imports tools-core directly
2. **Platform Mode**: Voice by Kraliki publishes events, platform routes to tools-core
3. **Shared Components**: UI components exported to `@ocelot/ui-core`

---

## SMS Service Integration

### Current Implementation Status

✅ **Completed (Week 6)**:
- Backend SMS router (`/api/sms/*`) with inbox, send, conversations endpoints
- Frontend SMS inbox UI with conversation list
- SMSComposer component (will be extracted to ui-core)
- Bottom navigation includes SMS icon
- Event publishing for SMS sent/received

⏳ **Pending (Tools-Core Package)**:
- SMSService class in tools-core
- Twilio → Telnyx failover logic
- SMS database table migration
- Rate limiting and quota management

---

## Backend Integration

### Standalone Mode (Direct Import)

```python
# app/routers/sms.py (future implementation)
from ocelot_platform.packages.tools_core import SMSService

sms_service = SMSService(
    provider="twilio",
    credentials={
        "account_sid": settings.TWILIO_ACCOUNT_SID,
        "auth_token": settings.TWILIO_AUTH_TOKEN,
        "phone_number": settings.TWILIO_PHONE_NUMBER
    },
    fallback_provider="telnyx"
)

@router.post("/send")
async def send_sms(sms_data: SMSCreate):
    result = await sms_service.send(
        to_number=sms_data.to_number,
        body=sms_data.body,
        from_number=settings.TWILIO_PHONE_NUMBER
    )

    # Publish event
    await event_publisher.publish(
        event_type="sms.sent",
        data={
            "message_id": result.id,
            "to": sms_data.to_number,
            "status": result.status
        },
        organization_id=current_user.organization_id
    )

    return result
```

### Platform Mode (Event-Driven)

```python
# app/routers/sms.py (platform mode)
@router.post("/send")
async def send_sms(sms_data: SMSCreate):
    # Publish request event instead of calling service directly
    await event_publisher.publish(
        event_type="sms.send_request",
        data={
            "request_id": str(uuid4()),
            "to_number": sms_data.to_number,
            "body": sms_data.body,
            "from_number": settings.TWILIO_PHONE_NUMBER,
            "idempotency_key": f"sms-{current_user.id}-{int(time.time())}"
        },
        organization_id=current_user.organization_id,
        user_id=current_user.id
    )

    return {"status": "queued", "message": "SMS queued for sending"}
```

### Event Contracts (Tools-Core)

**Request Event** (`sms.send_request`):
```json
{
  "request_id": "uuid",
  "correlation_id": "uuid",
  "tenant_id": "org_uuid",
  "actor": {"user_id": "uuid"},
  "idempotency_key": "unique",
  "ttl": 3600,
  "data": {
    "to_number": "+1234567890",
    "body": "Message text",
    "from_number": "+1987654321",
    "metadata": {}
  }
}
```

**Response Event** (`sms.sent` / `sms.failed`):
```json
{
  "event_id": "uuid",
  "correlation_id": "uuid (matches request)",
  "timestamp": "ISO8601",
  "status": "success|failed",
  "data": {
    "message_id": "twilio_sid",
    "to_number": "+1234567890",
    "provider": "twilio",
    "cost": 0.0075,
    "error": null
  }
}
```

### Error Taxonomy

- `VALIDATION_ERROR` - Invalid phone number or message format
- `AUTH_ERROR` - Invalid Twilio credentials
- `RATE_LIMITED` - Provider quota exceeded
- `PROVIDER_ERROR` - Twilio/Telnyx error (with fallback)
- `TIMEOUT` - Request timed out
- `RETRYING` - Currently retrying (exponential backoff)
- `FINAL_FAILURE` - All retries exhausted

---

## Frontend Integration

### Using SMSComposer Component

```svelte
<script lang="ts">
  import SMSComposer from '$lib/components/SMSComposer.svelte';

  async function handleSend(to: string, body: string) {
    const response = await fetch('/api/sms/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to_number: to, body })
    });

    if (!response.ok) {
      throw new Error('Failed to send SMS');
    }

    const result = await response.json();
    console.log('SMS sent:', result);
  }
</script>

<SMSComposer
  to=""
  message=""
  maxLength={1600}
  onSend={handleSend}
  placeholder="Type your message..."
/>
```

### Component API

**Props**:
- `to: string` - Phone number (with country code)
- `message: string` - Message body
- `maxLength: number` - Max characters (default: 1600)
- `onSend: (to, body) => Promise<void>` - Send callback
- `placeholder: string` - Textarea placeholder

**Features**:
- Phone number validation (E.164 format)
- Character counter with SMS segment calculation
- Multi-segment warning (>160 chars)
- Auto-formatting phone numbers
- Disabled state during sending

---

## Database Schema (Pending Migration)

```sql
-- SMS messages table
CREATE TABLE sms_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),

    -- Message details
    from_number VARCHAR(20) NOT NULL,
    to_number VARCHAR(20) NOT NULL,
    body TEXT NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),

    -- Provider tracking
    provider VARCHAR(20), -- 'twilio', 'telnyx'
    provider_message_id VARCHAR(100),
    status VARCHAR(20) NOT NULL, -- 'queued', 'sent', 'delivered', 'failed'
    error_message TEXT,

    -- Cost tracking
    cost_usd DECIMAL(10, 6),
    segments INTEGER DEFAULT 1,

    -- Metadata
    campaign_id UUID REFERENCES campaigns(id),
    contact_id UUID REFERENCES contacts(id),
    metadata JSONB,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,

    CONSTRAINT valid_phone_numbers CHECK (
        from_number ~ '^\+[1-9]\d{1,14}$' AND
        to_number ~ '^\+[1-9]\d{1,14}$'
    )
);

-- Indexes for performance
CREATE INDEX idx_sms_messages_org ON sms_messages(organization_id);
CREATE INDEX idx_sms_messages_contact ON sms_messages(contact_id);
CREATE INDEX idx_sms_messages_created ON sms_messages(created_at DESC);
CREATE INDEX idx_sms_messages_direction ON sms_messages(direction, organization_id);
```

---

## Tools-Core Package Structure

```
packages/tools-core/
├── services/
│   ├── sms/
│   │   ├── __init__.py
│   │   ├── base.py          # BaseSMSService interface
│   │   ├── twilio.py        # TwilioSMSProvider
│   │   ├── telnyx.py        # TelnyxSMSProvider
│   │   └── manager.py       # SMSServiceManager (failover logic)
│   ├── email/
│   │   ├── sendgrid.py
│   │   ├── ses.py
│   │   └── resend.py
│   └── calendar/
│       └── google.py
├── events/
│   ├── publisher.py         # Event publishing
│   └── schemas.py           # Event schemas
└── utils/
    ├── validators.py        # Phone/email validation
    └── rate_limiter.py      # Rate limiting
```

---

## Deployment Checklist

### Week 6 Deliverables (Complete)
- [x] Backend SMS router with inbox/send/conversations endpoints
- [x] Frontend SMS inbox UI with conversation list
- [x] SMSComposer component created
- [x] SMS icon added to bottom navigation
- [x] Event publishing stub in place

### Tools-Core Package (Next Phase)
- [ ] Create `packages/tools-core/services/sms/` module
- [ ] Implement TwilioSMSProvider
- [ ] Implement TelnyxSMSProvider (fallback)
- [ ] Add SMS database migration
- [ ] Implement rate limiting (100 SMS/hour per org)
- [ ] Add Twilio webhook handlers for delivery status
- [ ] Extract SMSComposer to `@ocelot/ui-core`

### Integration Testing
- [ ] Test SMS sending via Twilio
- [ ] Test failover to Telnyx on Twilio error
- [ ] Test rate limiting enforcement
- [ ] Test delivery status webhooks
- [ ] Test event publishing to platform bus

---

## Configuration

### Environment Variables

```bash
# Standalone Mode
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_PHONE_NUMBER=+1234567890

# Failover Provider
TELNYX_API_KEY=xxxx
TELNYX_PHONE_NUMBER=+1987654321

# Rate Limits
SMS_RATE_LIMIT=100  # per hour per organization
SMS_DAILY_LIMIT=500 # per day per organization
```

### Platform Mode

```python
# settings.py
PLATFORM_MODE = os.getenv("PLATFORM_MODE", "false").lower() == "true"

# Only use direct service in standalone mode
if not PLATFORM_MODE:
    from ocelot_platform.packages.tools_core import SMSService
    sms_service = SMSService(...)
```

---

## Cost Tracking

SMS costs are tracked per message:

| Provider | Cost per SMS | Segments |
|----------|-------------|----------|
| Twilio   | $0.0075     | 160 chars |
| Telnyx   | $0.0040     | 160 chars |

**Multi-segment messages**:
- 1-160 chars: 1 segment
- 161-320 chars: 2 segments
- 321-480 chars: 3 segments
- etc.

---

## Next Steps

1. **Week 7**: Create tools-core SMS service package
2. **Week 8**: Implement Twilio integration and testing
3. **Week 9**: Add Telnyx fallback and rate limiting
4. **Week 10**: Extract SMSComposer to ui-core
5. **Week 11**: Integration testing and production deployment

---

**Author**: Claude Code
**Last Updated**: October 5, 2025
**Review**: Week 6 Implementation Complete
