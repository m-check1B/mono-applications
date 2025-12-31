# Focus by Kraliki Event Publishing

## Overview
Focus by Kraliki publishes planning events to the platform event bus for cross-module integration.

## Event Types

### 1. task.created
- **Routing key**: `planning.task.created`
- **Data**: `{task_id, title, priority, assignee_id, project_id}`
- **Integration**: Agents module can suggest automation workflow

### 2. task.completed
- **Routing key**: `planning.task.completed`
- **Data**: `{task_id, completed_at, completed_by, outcome}`
- **Integration**: Trigger campaign or notification

### 3. project.milestone_reached
- **Routing key**: `planning.project.milestone_reached`
- **Data**: `{project_id, milestone, progress, team_members}`
- **Integration**: Send team notification

### 4. shadow.insight_generated
- **Routing key**: `planning.shadow.insight_generated`
- **Data**: `{insight_type, content, confidence, applicable_to}`
- **Integration**: Store in Flow Memory (cross-session)

### 5. flow_memory.context_updated
- **Routing key**: `planning.flow_memory.context_updated`
- **Data**: `{context_type, embedding_id, available_for_retrieval}`
- **Integration**: AI insights available for other modules

## Platform Consumption Examples

### CLI-Toris (Agents Module)
```python
@event_bus.subscribe("planning.task.created")
async def on_task_created(event):
    if event.data["priority"] == "high":
        workflow = await suggest_workflow(event.data["task_id"])
        await notify_user(workflow)
```

### Voice by Kraliki (Communications Module)
```python
@event_bus.subscribe("planning.task.completed")
async def on_task_completed(event):
    # Maybe trigger follow-up campaign
    await check_campaign_trigger(event.data["task_id"])
```

## Event Structure

All events follow a standardized envelope format:

```json
{
  "id": "uuid-v4",
  "type": "task.created",
  "source": "planning",
  "timestamp": "2025-10-05T12:34:56.789Z",
  "organizationId": "org-xyz",
  "userId": "user-123",
  "data": {
    "task_id": "task-456",
    "title": "Fix critical bug",
    "priority": "high"
  },
  "metadata": {
    "version": "1.0.0",
    "module": "focus-kraliki"
  }
}
```

## Usage in Code

### Basic Publishing

```python
from app.core.events import event_publisher

# Publish task created event
await event_publisher.publish(
    event_type="task.created",
    data={
        "task_id": "task-123",
        "title": "New feature",
        "priority": "medium"
    },
    organization_id="org-xyz",
    user_id="user-456"
)
```

### Using Helper Methods

```python
# Task created
await event_publisher.publish_task_created(
    task_id="task-123",
    title="Fix bug",
    priority="high",
    organization_id="org-xyz",
    user_id="user-456",
    assignee_id="user-789",
    project_id="project-001"
)

# Task completed
await event_publisher.publish_task_completed(
    task_id="task-123",
    title="Bug fixed",
    organization_id="org-xyz",
    user_id="user-456",
    duration_minutes=45
)

# Project milestone
await event_publisher.publish_project_milestone(
    project_id="project-001",
    milestone_name="Phase 1 Complete",
    organization_id="org-xyz",
    user_id="user-456",
    completion_percentage=33
)

# Shadow insight
await event_publisher.publish_shadow_insight(
    insight_id="insight-123",
    insight_type="workflow_optimization",
    insight_text="Consider batching similar tasks",
    organization_id="org-xyz",
    user_id="user-456",
    task_id="task-789"
)
```

## Configuration

The EventPublisher connects to RabbitMQ using the following default configuration:

```python
EventPublisher(amqp_url="amqp://localhost:5672")
```

For production, set the AMQP URL via environment variable:

```bash
export RABBITMQ_URL="amqp://user:pass@rabbitmq.example.com:5672/"
```

## RabbitMQ Setup

Focus by Kraliki publishes to the `ocelot.planning` topic exchange. Other modules can subscribe to specific event types using routing key patterns:

- Subscribe to all planning events: `planning.#`
- Subscribe to task events only: `planning.task.*`
- Subscribe to specific event: `planning.task.created`

## Testing

Run the event publisher tests:

```bash
cd /home/adminmatej/github/applications/focus-kraliki/backend
python3 -m pytest tests/test_events.py -v --noconftest
```

All tests use mocks, so no running RabbitMQ instance is required.

## Integration with Other Modules

### CLI-Toris (Workflow Automation)
When a high-priority task is created, CLI-Toris can automatically:
- Suggest workflow templates
- Assign AI agents to handle subtasks
- Create automated reminders

### Voice by Kraliki (Communication)
When a task is completed, Voice by Kraliki can:
- Send congratulations email
- Trigger follow-up campaign
- Notify team members

### Flow Memory (AI Context)
Shadow insights are stored in Flow Memory for:
- Cross-session context preservation
- Personalized AI suggestions
- Learning user preferences over time

## Troubleshooting

### Connection Issues

If the publisher can't connect to RabbitMQ:

```python
# The publisher will attempt to reconnect automatically
# Check logs for connection errors
```

### Event Not Received

1. Verify RabbitMQ is running
2. Check exchange exists: `ocelot.planning`
3. Verify routing key pattern in subscriber
4. Check organization/user IDs match

## Performance

- Events are published asynchronously (non-blocking)
- Messages are persistent (survive RabbitMQ restarts)
- Topic exchange allows flexible routing
- Multiple consumers can process same event

## Security

- Events include organization_id for multi-tenancy isolation
- Consumers should validate organization access
- User IDs should be verified before processing
- Sensitive data should not be included in events (use references)
