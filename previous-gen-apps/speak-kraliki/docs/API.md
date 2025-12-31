# API Reference

Base URL: `http://localhost:8000/api`

## Authentication

### POST /auth/register

Register a new company and admin user.

**Request:**
```json
{
  "email": "admin@company.com",
  "password": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Acme Corp"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "admin@company.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "owner",
  "company_id": "uuid"
}
```

### POST /auth/login

Authenticate and receive tokens.

**Request:** `application/x-www-form-urlencoded`
```
username=admin@company.com&password=securepass123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### POST /auth/refresh

Refresh access token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### GET /auth/me

Get current user info.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "admin@company.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "owner",
  "company_id": "uuid"
}
```

---

## Surveys

All endpoints require `Authorization: Bearer <token>` header.

### GET /speak/surveys

List all surveys for the company.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "Monthly Check-in",
    "description": "Monthly employee feedback",
    "status": "active",
    "frequency": "monthly",
    "questions": [...],
    "conversation_count": 50,
    "completion_rate": 72.5,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### POST /speak/surveys

Create a new survey.

**Request:**
```json
{
  "name": "Q1 Feedback",
  "description": "Quarterly feedback survey",
  "frequency": "quarterly",
  "questions": [
    {
      "question": "How are you doing this quarter?",
      "follow_up_count": 1
    },
    {
      "question": "Any concerns about workload?",
      "follow_up_count": 2
    }
  ],
  "target_departments": ["uuid1", "uuid2"]
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "Q1 Feedback",
  "status": "draft",
  ...
}
```

### GET /speak/surveys/{survey_id}

Get survey details.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "Monthly Check-in",
  "description": "...",
  "status": "active",
  "frequency": "monthly",
  "questions": [
    {
      "id": 1,
      "question": "How are you doing?",
      "follow_up_count": 1
    }
  ],
  "starts_at": "2024-01-01T00:00:00Z",
  "ends_at": "2024-01-31T23:59:59Z"
}
```

### PATCH /speak/surveys/{survey_id}

Update survey (draft/paused only).

**Request:**
```json
{
  "name": "Updated Name",
  "description": "Updated description"
}
```

### POST /speak/surveys/{survey_id}/launch

Launch survey and send invitations.

**Response:** `200 OK`
```json
{
  "message": "Survey launched, 45 employees invited",
  "invited_count": 45
}
```

### POST /speak/surveys/{survey_id}/pause

Pause an active survey.

**Response:** `200 OK`
```json
{
  "message": "Survey paused"
}
```

### GET /speak/surveys/{survey_id}/stats

Get survey statistics.

**Response:** `200 OK`
```json
{
  "total_invited": 50,
  "total_completed": 36,
  "total_in_progress": 2,
  "total_skipped": 5,
  "completion_rate": 72.0,
  "avg_duration_seconds": 342,
  "avg_sentiment": 0.35
}
```

---

## Voice Interface

### WebSocket /speak/voice/ws/{token}

Real-time voice conversation endpoint.

**Connection:** `wss://host/api/speak/voice/ws/{magic_link_token}`

**Client → Server Messages:**

```json
// Text message
{"type": "text", "content": "I'm doing well, thanks"}

// Switch to text mode
{"type": "fallback", "reason": "mic_denied"}

// End conversation
{"type": "end"}
```

**Server → Client Messages:**

```json
// AI message
{
  "type": "ai_message",
  "content": "That's great to hear!",
  "question_id": 1,
  "is_greeting": false,
  "is_final": false
}

// Mode change confirmation
{"type": "mode_changed", "mode": "text"}

// Error
{"type": "error", "message": "Invalid message format"}

// Completion
{
  "type": "completed",
  "message": "Conversation completed. Thank you!",
  "can_review_transcript": true
}
```

### POST /speak/voice/start

Initialize conversation (get metadata before WebSocket).

**Query:** `?token={magic_link_token}`

**Response:** `200 OK`
```json
{
  "conversation_id": "uuid",
  "employee_name": "John",
  "websocket_url": "/speak/voice/ws/{token}",
  "mode": "voice"
}
```

---

## Conversations

### GET /speak/conversations

List conversations (filtered by company).

**Query Parameters:**
- `survey_id`: Filter by survey
- `status`: Filter by status (pending, invited, in_progress, completed)
- `limit`: Results per page (default 50)
- `offset`: Pagination offset

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "anonymous_id": "EMP-A1B2C3D4",
    "status": "completed",
    "sentiment_score": 0.45,
    "topics": ["workload", "team"],
    "duration_seconds": 320,
    "completed_at": "2024-01-15T14:30:00Z"
  }
]
```

### GET /speak/conversations/{conversation_id}

Get conversation details (no transcript for privacy).

---

## Employee Endpoints

### POST /speak/employee/consent

Record employee consent (via magic link).

**Query:** `?token={magic_link_token}`

**Response:** `200 OK`
```json
{
  "message": "Consent recorded",
  "conversation_id": "uuid"
}
```

### GET /speak/employee/transcript

Get transcript for employee review.

**Query:** `?token={magic_link_token}`

**Response:** `200 OK`
```json
{
  "transcript": [
    {"role": "ai", "content": "Hello!", "timestamp": "..."},
    {"role": "user", "content": "Hi", "timestamp": "..."}
  ],
  "can_redact": true
}
```

### POST /speak/employee/redact

Redact parts of transcript.

**Query:** `?token={magic_link_token}`

**Request:**
```json
{
  "indices": [2, 5, 8]
}
```

### DELETE /speak/employee/data

Delete all employee data (GDPR).

**Query:** `?token={magic_link_token}`

---

## Alerts

### GET /speak/alerts

List alerts.

**Query Parameters:**
- `is_read`: Filter by read status
- `type`: Filter by type (flight_risk, burnout, toxic_manager, etc.)
- `severity`: Filter by severity (high, medium, low)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "type": "flight_risk",
    "severity": "high",
    "description": "Employee may be considering leaving",
    "department_id": "uuid",
    "trigger_keywords": "leaving, new job",
    "is_read": false,
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

### PATCH /speak/alerts/{alert_id}/read

Mark alert as read.

### POST /speak/alerts/{alert_id}/create-action

Create action from alert.

---

## Actions (Action Loop)

### GET /speak/actions

List actions.

**Query Parameters:**
- `status`: new, heard, in_progress, resolved

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "topic": "Workload concerns in Engineering",
    "status": "in_progress",
    "public_message": "We're hiring 2 more engineers",
    "department_id": "uuid",
    "created_at": "2024-01-10T00:00:00Z"
  }
]
```

### POST /speak/actions

Create action manually.

**Request:**
```json
{
  "topic": "Office environment feedback",
  "internal_notes": "Multiple employees mentioned AC",
  "department_id": "uuid"
}
```

### PATCH /speak/actions/{action_id}

Update action status/message.

**Request:**
```json
{
  "status": "in_progress",
  "public_message": "We've contacted facilities to fix the AC"
}
```

### GET /speak/actions/public

Get public actions (for employees via magic link).

**Query:** `?token={magic_link_token}`

---

## Insights

### GET /speak/insights/overview

Get company-wide metrics overview.

**Response:** `200 OK`
```json
{
  "sentiment": {
    "current": 0.42,
    "previous": 0.38,
    "change": 0.04
  },
  "participation": {
    "current": 0.78,
    "total_invited": 100,
    "total_completed": 78
  },
  "top_topics": [
    {"topic": "workload", "count": 25, "sentiment": -0.15},
    {"topic": "team", "count": 20, "sentiment": 0.65}
  ],
  "active_alerts_count": 3,
  "pending_actions_count": 5
}
```

### GET /speak/insights/trends

Get sentiment trends over time.

**Query Parameters:**
- `period`: week, month, quarter
- `department_id`: Filter by department

---

## Employees

### GET /speak/employees

List employees.

### POST /speak/employees

Add employee.

### POST /speak/employees/import

Bulk import employees (CSV).

### PATCH /speak/employees/{employee_id}

Update employee.

### DELETE /speak/employees/{employee_id}

Soft delete employee.

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Invalid data format |
| 500 | Server Error - Internal error |
