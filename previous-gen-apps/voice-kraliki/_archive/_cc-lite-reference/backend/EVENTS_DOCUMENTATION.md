# Voice by Kraliki Event Publishing

## Overview
Voice by Kraliki publishes events to the platform event bus (RabbitMQ) for cross-module integration with other Ocelot Platform modules.

## Architecture

### Event Bus
- **Technology**: RabbitMQ with topic exchange
- **Exchange Name**: `ocelot.events`
- **Exchange Type**: TOPIC (for flexible routing)
- **Durability**: Persistent messages for reliability

### Event Flow
```
Voice by Kraliki Module → EventPublisher → RabbitMQ Exchange → Subscribed Modules
                                   (ocelot.events)
```

## Event Types

### 1. call.started
Published when a call begins

- **Routing Key**: `comms.call.started`
- **Data Schema**:
  ```json
  {
    "call_id": "string",
    "from_number": "string (E.164 format)",
    "to_number": "string (E.164 format)",
    "campaign_id": "string|null"
  }
  ```
- **Platform Integration**:
  - Tracking module records call start time
  - Analytics module begins real-time metrics collection

### 2. call.ended
Published when a call completes

- **Routing Key**: `comms.call.ended`
- **Data Schema**:
  ```json
  {
    "call_id": "string",
    "duration": "number (seconds)",
    "outcome": "string (completed|callback_requested|voicemail|failed)",
    "transcript": "string|null"
  }
  ```
- **Platform Integration**:
  - **Planning Module (Focus-Lite)**: Creates follow-up task if outcome = "callback_requested"
  - **CRM Module**: Updates customer interaction history
  - **Analytics**: Updates call completion metrics

### 3. call.transcribed
Published when real-time transcript chunk is available

- **Routing Key**: `comms.call.transcribed`
- **Data Schema**:
  ```json
  {
    "call_id": "string",
    "transcript": "string (transcript chunk)",
    "language": "string (BCP-47 language code)",
    "confidence": "number (0.0-1.0)"
  }
  ```
- **Platform Integration**:
  - AI assistant provides real-time suggestions to agent
  - Compliance module monitors for restricted keywords
  - Training module identifies coaching opportunities

### 4. campaign.completed
Published when campaign finishes

- **Routing Key**: `comms.campaign.completed`
- **Data Schema**:
  ```json
  {
    "campaign_id": "string",
    "total_calls": "number",
    "successful_calls": "number",
    "failed_calls": "number",
    "success_rate": "number (0.0-1.0)"
  }
  ```
- **Platform Integration**:
  - **Agents Module (CLI-Toris)**: Suggests workflow optimizations based on results
  - **Workflow Module**: Triggers next campaign in sequence
  - **Reporting**: Generates comprehensive campaign analytics

### 5. sentiment.analyzed
Published when negative sentiment is detected during call

- **Routing Key**: `comms.sentiment.analyzed`
- **Data Schema**:
  ```json
  {
    "call_id": "string",
    "sentiment": "string (positive|neutral|negative)",
    "score": "number (-1.0 to 1.0)",
    "keywords": ["string"]
  }
  ```
- **Platform Integration**:
  - **Notification Module**: Sends alert to supervisor if score < -0.5
  - **Escalation Module**: Suggests immediate supervisor intervention
  - **Quality Module**: Flags call for quality review

## Event Schema Standard

All events follow the Ocelot Platform event schema:

```json
{
  "id": "uuid (unique event identifier)",
  "type": "string (event type, e.g., 'call.ended')",
  "source": "communications",
  "timestamp": "ISO 8601 timestamp (UTC)",
  "organizationId": "string (for data isolation)",
  "userId": "string|null (who triggered the event)",
  "data": {
    /* Event-specific payload */
  },
  "metadata": {
    "version": "1.0.0",
    "module": "cc-lite"
  }
}
```

## Usage Examples

### Publishing Events in API Endpoints

```python
from fastapi import APIRouter, Depends
from app.core.events import event_publisher
from app.core.security import get_current_user

router = APIRouter()

@router.post("/calls/{call_id}/end")
async def end_call(call_id: str, current_user = Depends(get_current_user)):
    # End call logic...

    # Publish event
    await event_publisher.publish_call_ended(
        call_id=call_id,
        duration=180,
        outcome="completed",
        transcript="Call transcript here",
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    return {"status": "ended"}
```

### Using Generic Publish Method

```python
# For custom event types
await event_publisher.publish(
    event_type="custom.event",
    data={"custom": "data"},
    organization_id="org-123",
    user_id="user-456"
)
```

## Platform Consumption Examples

### Focus-Lite (Planning Module) - Consuming call.ended

```python
import aio_pika
import json

# Subscribe to call.ended events
async def setup_consumer():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "ocelot.events",
        aio_pika.ExchangeType.TOPIC,
        durable=True
    )

    queue = await channel.declare_queue("focus_lite_calls", durable=True)
    await queue.bind(exchange, routing_key="comms.call.ended")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                event = json.loads(message.body.decode())

                if event["data"]["outcome"] == "callback_requested":
                    # Create follow-up task automatically
                    await create_task({
                        "title": f"Call back customer from call {event['data']['call_id']}",
                        "priority": "high",
                        "due_date": "tomorrow",
                        "organizationId": event["organizationId"],
                        "userId": event["userId"]
                    })
```

### CLI-Toris (Agents Module) - Consuming campaign.completed

```python
@event_bus.subscribe("comms.campaign.completed")
async def on_campaign_completed(event):
    """Analyze campaign and suggest workflow optimizations"""

    campaign_id = event["data"]["campaign_id"]
    success_rate = event["data"]["success_rate"]

    # AI analysis
    if success_rate < 0.7:
        suggestions = await analyze_campaign_for_improvements(campaign_id)

        await notify_user({
            "userId": event["userId"],
            "message": f"Campaign completed with {success_rate:.0%} success rate. Here are optimization suggestions:",
            "suggestions": suggestions
        })
```

### Notification Module - Consuming sentiment.negative

```python
@event_bus.subscribe("comms.sentiment.analyzed")
async def on_sentiment_analyzed(event):
    """Send alert on negative sentiment"""

    if event["data"]["score"] < -0.5:
        # High-priority alert to supervisor
        await send_alert({
            "type": "negative_sentiment",
            "priority": "high",
            "call_id": event["data"]["call_id"],
            "sentiment_score": event["data"]["score"],
            "organizationId": event["organizationId"],
            "message": "Negative sentiment detected on active call - consider intervention"
        })
```

## Testing

### Running Event Tests

```bash
cd /home/adminmatej/github/applications/cc-lite/backend
pytest tests/test_events.py -v
```

### Test Coverage

The test suite covers:
- ✅ RabbitMQ connection establishment
- ✅ Event publishing with correct routing keys
- ✅ Event schema validation
- ✅ Convenience methods for each event type
- ✅ Graceful handling of disconnected state
- ✅ Proper cleanup and disconnection

### Manual Testing with RabbitMQ

```bash
# Start RabbitMQ (if not running)
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Access management UI
# http://localhost:15672 (guest/guest)

# Monitor exchanges and queues
# You'll see "ocelot.events" exchange with topic type
```

## Configuration

### Environment Variables

```bash
# RabbitMQ connection URL
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# For production with authentication
RABBITMQ_URL=amqp://username:password@rabbitmq-host:5672/vhost
```

### Application Startup

```python
from app.core.events import event_publisher

# Connect on startup
@app.on_event("startup")
async def startup_event():
    await event_publisher.connect()

# Disconnect on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    await event_publisher.disconnect()
```

## Event Lifecycle

### 1. Publishing
```
API Request → Handler → event_publisher.publish() → RabbitMQ Exchange
```

### 2. Routing
```
Exchange (ocelot.events) → Routing Key (comms.*) → Bound Queues
```

### 3. Consumption
```
Queue → Consumer (other module) → Process Event → Take Action
```

### 4. Acknowledgment
```
Process Success → Message ACK → Remove from Queue
Process Failure → Message NACK → Requeue or Dead Letter
```

## Cross-Module Workflow Example

### Scenario: Customer Callback Request

1. **Voice by Kraliki** (Communications): Call ends with "callback_requested" outcome
   ```python
   await event_publisher.publish_call_ended(
       call_id="call-123",
       outcome="callback_requested",
       transcript="Customer wants callback tomorrow at 2pm",
       ...
   )
   ```

2. **Focus-Lite** (Planning): Receives event and creates task
   ```python
   @subscribe("comms.call.ended")
   async def create_callback_task(event):
       if event.data.outcome == "callback_requested":
           await create_task(...)
   ```

3. **CLI-Toris** (Agents): Suggests optimal callback time based on AI analysis
   ```python
   @subscribe("planning.task.created")
   async def optimize_callback_time(event):
       optimal_time = await ai_suggest_time(event.data.customer_id)
       await update_task(event.data.task_id, due_time=optimal_time)
   ```

4. **Notification Module**: Reminds agent at scheduled time
   ```python
   @subscribe("planning.task.due")
   async def send_reminder(event):
       await notify_agent(event.userId, "Callback due now")
   ```

## Monitoring and Observability

### Metrics to Track
- Events published per minute
- Event processing latency
- Failed event deliveries
- Queue depths
- Consumer lag

### Logging
All events are logged with:
```
📤 Published event: comms.call.ended (id: abc-123)
```

### RabbitMQ Management UI
- View exchange bindings: http://localhost:15672/#/exchanges
- Monitor queue depths: http://localhost:15672/#/queues
- Trace messages: http://localhost:15672/#/trace

## Troubleshooting

### Event Not Being Published
1. Check RabbitMQ connection: `event_publisher.is_connected`
2. Verify RABBITMQ_URL in environment
3. Check logs for connection errors
4. Ensure RabbitMQ is running

### Event Published But Not Received
1. Verify queue is bound to exchange with correct routing key
2. Check queue bindings in RabbitMQ management UI
3. Ensure consumer is running and connected
4. Check for message acknowledgment issues

### Performance Issues
1. Use message batching for high-volume events
2. Implement connection pooling
3. Monitor queue depths for backlog
4. Scale consumers horizontally

## Best Practices

1. **Always include organizationId** for multi-tenant data isolation
2. **Use semantic versioning** in metadata.version
3. **Keep event payloads small** - use references instead of full objects
4. **Make events idempotent** - consumers may receive duplicates
5. **Version your event schemas** - allow for backwards compatibility
6. **Log all published events** for audit trail
7. **Handle connection failures gracefully** - queue events locally if needed
8. **Monitor queue depths** - prevent message backlog

## Security Considerations

1. **Authentication**: Use AMQP credentials (not guest/guest in production)
2. **Authorization**: Restrict queue bindings per organization
3. **Encryption**: Use TLS for RabbitMQ connections (amqps://)
4. **Data Isolation**: Always filter by organizationId in consumers
5. **PII Handling**: Avoid including sensitive data in events (use references)

## Future Enhancements

- [ ] Event schema validation with JSON Schema
- [ ] Dead letter queue for failed events
- [ ] Event replay capability for debugging
- [ ] Event sourcing for audit trail
- [ ] GraphQL subscriptions for real-time UI updates
- [ ] Event archival to S3 for long-term storage

## References

- [RabbitMQ Topic Exchange](https://www.rabbitmq.com/tutorials/tutorial-five-python.html)
- [aio-pika Documentation](https://aio-pika.readthedocs.io/)
- [Event-Driven Architecture Patterns](https://martinfowler.com/articles/201701-event-driven.html)
- [Ocelot Platform Architecture](../docs/PLATFORM_ARCHITECTURE.md)
