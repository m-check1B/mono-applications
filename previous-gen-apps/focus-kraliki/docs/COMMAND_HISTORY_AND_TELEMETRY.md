# Command History & Telemetry API

## Overview

The Command History & Telemetry system provides a unified timeline of all user activities in Focus by Kraliki, answering the critical user question: **"What did I work on last week?"**

This system tracks and correlates:
- Voice and text assistant commands
- Deterministic API operations (tasks, projects, knowledge items, etc.)
- II-Agent orchestrated executions
- Workflow template executions
- Routing telemetry (hybrid execution decisions)

## Architecture

### Database Models

#### `command_history` Table

Stores all user commands and their execution details.

| Field | Type | Description |
|-------|------|-------------|
| `id` | String (PK) | Unique command ID |
| `userId` | String (FK → user.id) | User who executed the command |
| `source` | Enum | Command source (voice, API, agent, etc.) |
| `command` | Text | The natural language or API command |
| `intent` | String | Parsed intent (create_task, update_task, etc.) |
| `status` | Enum | Execution status (pending, in_progress, completed, failed, cancelled) |
| `startedAt` | DateTime | When command started |
| `completedAt` | DateTime | When command completed |
| `durationMs` | Float | Execution duration in milliseconds |
| `context` | JSON | Additional context (workspace, project, etc.) |
| `result` | JSON | Execution result (created IDs, updated fields, etc.) |
| `error` | JSON | Error details if failed |
| `telemetryId` | String (FK → request_telemetry.id) | Link to routing telemetry |
| `agentSessionId` | String | II-Agent session UUID |
| `conversationId` | String (FK → ai_conversation.id) | AI conversation ID |
| `model` | String | AI model used |
| `confidence` | Float | Confidence score (0-1) |
| `command_metadata` | JSON | Additional metadata |

**Indexes:**
- `userId` - For user-specific queries
- `source` - For filtering by command source
- `intent` - For filtering by intent
- `status` - For filtering by status
- `startedAt` - For time-range queries

#### Command Sources

```python
class CommandSource(str, enum.Enum):
    ASSISTANT_VOICE = "assistant_voice"      # Voice commands via assistant
    ASSISTANT_TEXT = "assistant_text"        # Text commands via assistant
    DETERMINISTIC_API = "deterministic_api"  # Direct API calls
    II_AGENT = "ii_agent"                    # II-Agent orchestrated
    WORKFLOW = "workflow"                    # Workflow executions
    DIRECT_API = "direct_api"                # Other direct operations
```

#### Command Statuses

```python
class CommandStatus(str, enum.Enum):
    PENDING = "pending"           # Waiting to execute
    IN_PROGRESS = "in_progress"   # Currently executing
    COMPLETED = "completed"       # Successfully completed
    FAILED = "failed"             # Execution failed
    CANCELLED = "cancelled"       # User cancelled
```

## API Endpoints

### 1. GET /assistant/commands

Get command history with filtering and pagination.

**Query Parameters:**
- `source` (optional): Filter by command source
- `intent` (optional): Filter by intent
- `status` (optional): Filter by status
- `since` (optional): Start date (ISO 8601)
- `until` (optional): End date (ISO 8601)
- `limit` (optional): Max results (1-200, default 50)
- `offset` (optional): Pagination offset (default 0)

**Response:**
```json
{
  "commands": [
    {
      "id": "cmd_123",
      "userId": "user_456",
      "source": "assistant_voice",
      "command": "Create a task to review PRs tomorrow",
      "intent": "create_task",
      "status": "completed",
      "startedAt": "2025-11-16T10:30:00Z",
      "completedAt": "2025-11-16T10:30:02Z",
      "durationMs": 2340,
      "context": {"workspace": "work"},
      "result": {"taskId": "task_789"},
      "model": "claude-3-5-sonnet",
      "confidence": 0.95
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

**Example Usage:**
```bash
# Get last week's voice commands
curl "https://api.focus_kraliki.com/assistant/commands?source=assistant_voice&since=2025-11-09T00:00:00Z"

# Get failed commands
curl "https://api.focus_kraliki.com/assistant/commands?status=failed"

# Get all create_task commands
curl "https://api.focus_kraliki.com/assistant/commands?intent=create_task&limit=100"
```

### 2. POST /assistant/commands

Manually log a command to the history.

**Request Body:**
```json
{
  "source": "assistant_text",
  "command": "Show me my tasks for today",
  "intent": "list_tasks",
  "context": {"timeframe": "today"},
  "model": "claude-3-5-sonnet",
  "confidence": 0.98,
  "metadata": {"voiceEnabled": false}
}
```

**Response:**
```json
{
  "id": "cmd_new",
  "userId": "user_456",
  "source": "assistant_text",
  "command": "Show me my tasks for today",
  "intent": "list_tasks",
  "status": "pending",
  "startedAt": "2025-11-16T10:35:00Z",
  ...
}
```

### 3. PATCH /assistant/commands/{command_id}

Update command status and results.

**Request Body:**
```json
{
  "status": "completed",
  "result": {
    "tasksReturned": 5,
    "taskIds": ["task_1", "task_2", "task_3", "task_4", "task_5"]
  }
}
```

**Response:**
```json
{
  "id": "cmd_new",
  "status": "completed",
  "completedAt": "2025-11-16T10:35:01Z",
  "durationMs": 1240,
  "result": {
    "tasksReturned": 5,
    "taskIds": ["task_1", "task_2", "task_3", "task_4", "task_5"]
  },
  ...
}
```

### 4. GET /ai/telemetry/history

**The main endpoint for unified timeline queries.**

Get unified timeline of user activity across commands and telemetry.

**Query Parameters:**
- `since` (optional): Start date (default: 7 days ago)
- `until` (optional): End date (default: now)
- `sources` (optional): Filter by command sources (can be multiple)
- `includeTelemetry` (optional): Include routing telemetry (default: true)
- `limit` (optional): Max entries (1-500, default 100)

**Response:**
```json
{
  "timeline": [
    {
      "id": "cmd_123",
      "type": "command",
      "timestamp": "2025-11-16T10:30:00Z",
      "source": "assistant_voice",
      "command": "Create a task to review PRs tomorrow",
      "intent": "create_task",
      "status": "completed",
      "durationMs": 2340,
      "result": {"taskId": "task_789"},
      "model": "claude-3-5-sonnet",
      "confidence": 0.95
    },
    {
      "id": "tel_456",
      "type": "telemetry",
      "timestamp": "2025-11-16T10:29:58Z",
      "source": "enhance_input",
      "intent": "create_task",
      "detectedType": "task",
      "confidence": 0.95,
      "route": "deterministic",
      "workflowSteps": null
    }
  ],
  "total": 2,
  "period": {
    "since": "2025-11-09T00:00:00Z",
    "until": "2025-11-16T10:40:00Z"
  }
}
```

**Example Usage:**
```bash
# Get last week's activity
curl "https://api.focus_kraliki.com/ai/telemetry/history"

# Get last 30 days, no telemetry
curl "https://api.focus_kraliki.com/ai/telemetry/history?since=2025-10-16T00:00:00Z&includeTelemetry=false"

# Get only II-Agent executions
curl "https://api.focus_kraliki.com/ai/telemetry/history?sources=ii_agent"

# Get voice and agent commands
curl "https://api.focus_kraliki.com/ai/telemetry/history?sources=assistant_voice&sources=ii_agent"
```

### 5. GET /ai/telemetry/activity-summary

Get summary statistics of user activity.

**Query Parameters:**
- `since` (optional): Start date (default: 7 days ago)
- `until` (optional): End date (default: now)

**Response:**
```json
{
  "period": {
    "since": "2025-11-09T00:00:00Z",
    "until": "2025-11-16T10:40:00Z"
  },
  "total_commands": 127,
  "completed": 119,
  "failed": 5,
  "in_progress": 3,
  "success_rate": 93.7,
  "by_source": {
    "assistant_voice": 42,
    "assistant_text": 38,
    "deterministic_api": 35,
    "ii_agent": 8,
    "workflow": 4
  },
  "by_intent": {
    "create_task": 45,
    "update_task": 28,
    "list_tasks": 22,
    "create_note": 15,
    "research": 8,
    "other": 9
  },
  "avg_duration_ms": 1840.5
}
```

**Example Usage:**
```bash
# Get last week's summary
curl "https://api.focus_kraliki.com/ai/telemetry/activity-summary"

# Get last month's summary
curl "https://api.focus_kraliki.com/ai/telemetry/activity-summary?since=2025-10-16T00:00:00Z"
```

### 6. GET /assistant/commands/sources

Get list of available command sources.

**Response:**
```json
{
  "sources": [
    {
      "value": "assistant_voice",
      "description": "Voice commands via assistant"
    },
    {
      "value": "assistant_text",
      "description": "Text commands via assistant"
    },
    ...
  ]
}
```

### 7. GET /assistant/commands/statuses

Get list of available command statuses.

**Response:**
```json
{
  "statuses": [
    {
      "value": "pending",
      "description": "Command is waiting to be executed"
    },
    {
      "value": "in_progress",
      "description": "Command is currently executing"
    },
    ...
  ]
}
```

## Integration Patterns

### 1. Logging Deterministic API Calls

When a user creates a task via the deterministic API:

```python
from app.services.command_history import log_command, update_command_status
from app.models.command_history import CommandSource, CommandStatus

# When request starts
command = log_command(
    db,
    user_id=current_user.id,
    source=CommandSource.DETERMINISTIC_API,
    command=f"Create task: {task_request.title}",
    intent="create_task",
    status=CommandStatus.IN_PROGRESS,
    context={"projectId": task_request.projectId}
)

# After task creation
try:
    task = create_task(db, task_request)
    update_command_status(
        db,
        command_id=command.id,
        status=CommandStatus.COMPLETED,
        result={"taskId": task.id, "title": task.title}
    )
except Exception as e:
    update_command_status(
        db,
        command_id=command.id,
        status=CommandStatus.FAILED,
        error={"message": str(e)}
    )
```

### 2. Logging II-Agent Sessions

When creating an II-Agent session:

```python
# In /agent/sessions endpoint
session = create_agent_session(...)

# Log the command
command = log_command(
    db,
    user_id=current_user.id,
    source=CommandSource.II_AGENT,
    command=payload.goal,
    intent=payload.structuredGoal.get("intent") if payload.structuredGoal else None,
    status=CommandStatus.IN_PROGRESS,
    agent_session_id=session.sessionUuid,
    telemetry_id=payload.telemetryId,
    context=payload.context
)

# Store command_id in session for later updates
session.command_id = command.id
```

When the II-Agent completes:

```python
# Update command with final status
update_command_status(
    db,
    command_id=session.command_id,
    status=CommandStatus.COMPLETED if session.status == "completed" else CommandStatus.FAILED,
    result=session.result,
    error=session.error if session.status == "failed" else None
)
```

### 3. Logging Assistant/Voice Commands

When processing voice input:

```python
# After transcription
command = log_command(
    db,
    user_id=current_user.id,
    source=CommandSource.ASSISTANT_VOICE,
    command=transcription.transcript,
    intent=None,  # Will be filled after enhance-input
    status=CommandStatus.IN_PROGRESS,
    context={"language": request.language},
    model="whisper-1",
    confidence=transcription.confidence
)

# After enhance-input
enhance_response = enhance_input(transcription.transcript)
update_command_status(
    db,
    command_id=command.id,
    status=CommandStatus.IN_PROGRESS,  # Still processing
    result={"enhanced_text": enhance_response.enhanced_text, "intent": enhance_response.intent}
)

# Link to telemetry
command.telemetryId = enhance_response.telemetryId
db.commit()
```

### 4. Linking Telemetry and Commands

The `request_telemetry` table tracks routing decisions, while `command_history` tracks actual executions. They are linked via `telemetryId`:

```python
# In /ai/enhance-input
telemetry = log_enhance_input(db, ...)

# If user proceeds with deterministic route
command = log_command(
    db,
    ...,
    telemetry_id=telemetry.id
)

# If user escalates to II-Agent
agent_session = create_agent_session(
    ...,
    telemetry_id=telemetry.id
)
command = log_command(
    db,
    ...,
    source=CommandSource.II_AGENT,
    telemetry_id=telemetry.id,
    agent_session_id=agent_session.sessionUuid
)
```

## Frontend Integration

### Displaying "What did I work on last week?"

```typescript
// Fetch unified timeline
const response = await fetch('/api/ai/telemetry/history?since=2025-11-09T00:00:00Z');
const { timeline } = await response.json();

// Group by date
const byDate = timeline.reduce((acc, entry) => {
  const date = entry.timestamp.split('T')[0];
  if (!acc[date]) acc[date] = [];
  acc[date].push(entry);
  return acc;
}, {});

// Render timeline
Object.entries(byDate).forEach(([date, entries]) => {
  console.log(`\n${date}:`);
  entries.forEach(entry => {
    if (entry.type === 'command') {
      console.log(`  ✓ ${entry.command} (${entry.source}, ${entry.status})`);
    } else {
      console.log(`  → Routing: ${entry.intent} → ${entry.route}`);
    }
  });
});
```

### Activity Summary Widget

```typescript
// Fetch summary
const response = await fetch('/api/ai/telemetry/activity-summary');
const summary = await response.json();

// Display stats
console.log(`Last week: ${summary.total_commands} commands`);
console.log(`Success rate: ${summary.success_rate}%`);
console.log(`Most common: ${Object.keys(summary.by_intent)[0]}`);
```

## Performance Considerations

### Indexes

The following indexes are created for optimal query performance:

- `ix_command_history_userId` - User-specific queries
- `ix_command_history_source` - Source filtering
- `ix_command_history_intent` - Intent filtering
- `ix_command_history_status` - Status filtering
- `ix_command_history_startedAt` - Time-range queries (most common)

### Pagination

Always use pagination for large result sets:

```bash
# Page 1
curl "https://api.focus_kraliki.com/assistant/commands?limit=50&offset=0"

# Page 2
curl "https://api.focus_kraliki.com/assistant/commands?limit=50&offset=50"
```

### Caching

Timeline queries for recent data (last 24 hours) can be cached for 5-10 minutes:

```typescript
const cacheKey = `timeline:${userId}:${since}:${until}`;
let timeline = await cache.get(cacheKey);
if (!timeline) {
  timeline = await fetchTimeline(userId, since, until);
  await cache.set(cacheKey, timeline, 300); // 5 minutes
}
```

## Security & Privacy

### Access Control

- Users can only access their own command history
- All endpoints require authentication
- Command IDs are UUIDs to prevent enumeration

### Data Retention

- Command history is retained for 90 days by default
- Users can export their history before deletion
- Sensitive data in `context`/`result` fields should be encrypted at rest

### PII Considerations

- Natural language commands may contain PII
- Results may include task titles, project names, etc.
- Ensure GDPR compliance for EU users

## Migration

The migration file is located at:
`backend/alembic/versions/011_add_command_history_table.py`

To apply:
```bash
cd backend
alembic upgrade head
```

To rollback:
```bash
alembic downgrade -1
```

## Testing

Example test cases:

```python
def test_log_command():
    cmd = log_command(
        db,
        user_id="test_user",
        source=CommandSource.ASSISTANT_VOICE,
        command="Create a task",
        intent="create_task"
    )
    assert cmd.id is not None
    assert cmd.status == CommandStatus.PENDING

def test_update_command_status():
    cmd = log_command(db, ...)
    updated = update_command_status(
        db,
        command_id=cmd.id,
        status=CommandStatus.COMPLETED,
        result={"taskId": "task_123"}
    )
    assert updated.status == CommandStatus.COMPLETED
    assert updated.durationMs is not None

def test_unified_timeline():
    timeline = get_unified_timeline(
        db,
        user_id="test_user",
        since=datetime.now() - timedelta(days=7)
    )
    assert len(timeline) > 0
    assert all(e["timestamp"] for e in timeline)
```

## Future Enhancements

1. **Real-time Updates**: WebSocket for live timeline updates
2. **Advanced Analytics**: Command patterns, peak usage times, etc.
3. **Export**: CSV/JSON export for external analysis
4. **Search**: Full-text search across commands
5. **Insights**: AI-generated insights from command history
6. **Replay**: Ability to replay or undo commands

## Related Documentation

- [Hybrid Execution Guide](/docs/HYBRID-EXECUTION-GUIDE.md)
- [II-Agent Handoff](/docs/II_AGENT_HANDOFF.md)
- [User Research - Top Requests](/docs/user-research/README.md#top-10-real-user-requests)
