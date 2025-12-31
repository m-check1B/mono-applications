# API Additions (v2.4.0)

This document details the new API endpoints added in version 2.4.0.

## 🔐 Google OAuth

### `POST /auth/google/url`

Generate the Google OAuth URL with CSRF protection.

**Request Body:**
```json
{
  "state": "client-generated-state-string"
}
```

**Response:**
```json
{
  "url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&response_type=code&scope=...&state=...",
  "csrfToken": "base64-encoded-csrf-token"
}
```

**Rate Limit:** 10 requests/minute

**Error Responses:**
- `503 Service Unavailable`: Google OAuth is not configured (missing `GOOGLE_OAUTH_CLIENT_ID`)

**Notes:**
- The generated URL includes scopes for: `openid`, `email`, `profile`, and Google Calendar access (`calendar.readonly`, `calendar.events`)
- CSRF tokens are stored in-memory (replace with Redis in production)
- The redirect URI is configured via `GOOGLE_OAUTH_REDIRECT_URI` environment variable

---

### `POST /auth/google/login`

Exchange Google OAuth authorization code for user session.

**Parameters:**
- `code` (query/form): Authorization code from Google OAuth callback
- `redirect_uri` (query/form): Redirect URI used in OAuth flow (must match)

**Response:**
```json
{
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "username": "John Doe",
    "firstName": "John",
    "lastName": "Doe",
    "organizationId": "org-id",
    "preferences": {
      "calendar_sync": {
        "enabled": true,
        "access_token": "...",
        "refresh_token": "...",
        "expires_at": "2025-12-30T10:00:00",
        "sync_direction": "two-way",
        "last_sync": null
      }
    }
  },
  "token": "jwt-access-token",
  "refreshToken": null
}
```

**Rate Limit:** 5 requests per 5 minutes

**Error Responses:**
- `400 Bad Request`: Failed to exchange authorization code
- `401 Unauthorized`: Invalid Google ID token
- `503 Service Unavailable`: Google OAuth is not configured

**Behavior:**
- If user exists: logs in and updates session
- If user doesn't exist: creates new user account
- Google Calendar tokens are automatically stored in user preferences
- Returns JWT access token for subsequent API calls

---

## 📅 Calendar Sync

### `POST /calendar-sync/oauth/init`

Initialize Google Calendar OAuth flow.

**Request Body:**
```json
{
  "redirect_uri": "https://your-app.com/calendar/oauth/callback"
}
```

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&scope=...",
  "state": "oauth-state-parameter"
}
```

**Error Responses:**
- `503 Service Unavailable`: Google OAuth is not configured

---

### `POST /calendar-sync/oauth/exchange`

Exchange authorization code for Google Calendar API tokens.

**Request Body:**
```json
{
  "code": "authorization-code-from-google",
  "redirect_uri": "https://your-app.com/calendar/oauth/callback"
}
```

**Response:**
```json
{
  "access_token": "google-api-access-token",
  "refresh_token": "google-api-refresh-token",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid or expired authorization code
- `503 Service Unavailable`: Google OAuth is not configured

---

### `POST /calendar-sync/sync`

Trigger manual calendar sync (requires authentication).

**Request Body:**
```json
{
  "direction": "both",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-01-31T23:59:59Z"
}
```

**Parameters:**
- `direction` (optional): Sync direction - `"to_calendar"`, `"from_calendar"`, or `"both"` (default: `"both"`)
- `start_date` (optional): ISO format date string to sync from
- `end_date` (optional): ISO format date string to sync until

**Response:**
```json
{
  "success": true,
  "message": "Sync completed successfully",
  "synced_events": 15,
  "direction": "both"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired access token
- `400 Bad Request`: Invalid date format or sync direction

**Behavior:**
- Requires authenticated user with valid Google Calendar tokens
- Syncs tasks between Focus app and Google Calendar
- Applies conflict resolution policy for conflicting changes

---

### `POST /calendar-sync/webhook`

Handle Google Calendar push notifications (requires webhook signature verification).

**Headers:**
- `X-Goog-Channel-ID`: Google's channel identifier
- `X-Goog-Resource-State`: Resource state (`sync`, `exists`, `not_exists`)
- `X-Goog-Resource-ID`: Google's resource identifier
- `X-Goog-Resource-URI`: Resource URI
- `X-Goog-Message-Number`: Message sequence number

**Request Body:** Empty (headers contain all necessary information)

**Response:**
```json
{
  "success": true,
  "message": "Webhook received"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid webhook signature
- `400 Bad Request`: Invalid webhook payload

**Security:**
- Webhook URL must be registered in Google Cloud Console
- Requires `GOOGLE_CALENDAR_WEBHOOK_TOKEN` to be configured
- Implements fail-closed security

---

## 🤖 Agent Sessions

### `POST /agent/sessions`

Create a new II-Agent session (requires authentication).

**Request Body:**
```json
{
  "goal": "Analyze project documentation and generate a summary",
  "context": {
    "project_id": "project-id",
    "workspace_id": "workspace-id"
  }
}
```

**Response:**
```json
{
  "id": "session-id",
  "goal": "Analyze project documentation and generate a summary",
  "status": "pending",
  "agentToken": "session-token-for-agent",
  "createdAt": "2025-12-29T16:00:00Z",
  "updatedAt": "2025-12-29T16:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired access token
- `400 Bad Request`: Invalid goal or context

**Behavior:**
- Creates a new AI agent session with the specified goal
- Returns `agentToken` for securing webhook callbacks
- Session status updates are sent via webhook callbacks

---

### `POST /agent/sessions/webhook/callback`

Receive status updates from II-Agent (requires signature verification).

**Headers:**
- `X-II-Agent-Signature` (required): Base64-encoded signature (Ed25519 or HMAC-SHA256)
- `X-II-Agent-Timestamp` (required): Unix timestamp (prevents replay attacks)
- `X-II-Agent-Signature-Type` (optional): `"ed25519"` or `"hmac-sha256"` (default: `"hmac-sha256"`)

**Request Body:**
```json
{
  "session_id": "session-id",
  "event_type": "completed",
  "data": {
    "result": "AI agent execution result",
    "metadata": {
      "duration_ms": 1500,
      "tool_calls": 5
    }
  }
}
```

**Event Types:**
- `"completed"`: Agent finished successfully
- `"failed"`: Agent encountered an error
- `"progress"`: Progress update (partial results)
- `"tool_call"`: Tool was executed

**Response:**
```json
{
  "success": true,
  "message": "Callback processed"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing signature
- `400 Bad Request`: Invalid callback payload
- `404 Not Found`: Session not found

**Security:**
- Signature verification is required (Ed25519 or HMAC-SHA256)
- Timestamp validation prevents replay attacks (rejects requests older than 5 minutes)
- Fail-closed: rejects requests with invalid/missing signatures
- Requires `II_AGENT_WEBHOOK_SECRET` environment variable

---

## 🛠️ Agent Tools

### `POST /agent-tools/knowledge/create`

Create a knowledge item (requires authentication).

**Request Body:**
```json
{
  "title": "Project Architecture Overview",
  "content": "Detailed documentation of project architecture...",
  "typeId": "document-type-id"
}
```

**Response:**
```json
{
  "id": "knowledge-id",
  "title": "Project Architecture Overview",
  "content": "Detailed documentation of project architecture...",
  "typeId": "document-type-id",
  "createdAt": "2025-12-29T16:00:00Z",
  "updatedAt": "2025-12-29T16:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired access token
- `400 Bad Request`: Invalid request data

---

### `POST /agent-tools/tasks`

Create a task (requires authentication).

**Request Body:**
```json
{
  "title": "Implement user authentication",
  "priority": 3,
  "estimatedMinutes": 60,
  "projectId": "project-id"
}
```

**Parameters:**
- `title` (required): Task title
- `priority` (optional): Priority level (1-5, default: 3)
- `estimatedMinutes` (optional): Estimated duration in minutes
- `projectId` (optional): Associated project ID

**Response:**
```json
{
  "id": "task-id",
  "title": "Implement user authentication",
  "status": "pending",
  "priority": 3,
  "estimatedMinutes": 60,
  "projectId": "project-id",
  "createdAt": "2025-12-29T16:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired access token
- `400 Bad Request`: Invalid request data

---

### `POST /agent-tools/time/start`

Start a time entry (requires authentication).

**Request Body:**
```json
{
  "description": "Work on user authentication",
  "workspace_id": "workspace-id",
  "start_time": "2025-12-29T16:00:00Z",
  "task_id": "task-id"
}
```

**Parameters:**
- `description` (required): Time entry description
- `workspace_id` (required): Workspace ID
- `start_time` (required): ISO format start time
- `task_id` (optional): Associated task ID

**Response:**
```json
{
  "id": "time-entry-id",
  "description": "Work on user authentication",
  "start_time": "2025-12-29T16:00:00Z",
  "workspace_id": "workspace-id",
  "task_id": "task-id",
  "status": "running",
  "createdAt": "2025-12-29T16:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired access token
- `400 Bad Request`: Invalid request data or time format

---

## 📋 Authentication

All endpoints except `/auth/google/url`, `/auth/google/login`, `/calendar-sync/webhook`, and `/agent/sessions/webhook/callback` require authentication.

**Authentication Header:**
```
Authorization: Bearer <jwt-token>
```

**Error Response (Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

**Status Code:** 401 Unauthorized

---

## ⚡ Rate Limits

| Endpoint | Rate Limit | Purpose |
|----------|------------|---------|
| `POST /auth/google/url` | 10/minute | Prevent CSRF token exhaustion |
| `POST /auth/google/login` | 5/5 minutes | Prevent brute force |
| `POST /auth/google/link` | 5/minute | Sensitive operation protection |
| `POST /auth/google/unlink` | 5/minute | Sensitive operation protection |
| Other endpoints | Standard limits | API protection |

**Rate Limit Response:**
```json
{
  "detail": "Rate limit exceeded"
}
```

**Status Code:** 429 Too Many Requests

---

## 🔒 Security Notes

### CSRF Protection
- OAuth endpoints use CSRF tokens to prevent cross-site request forgery
- Tokens are validated on the server side before processing requests

### Signature Verification
- Webhook endpoints require signature verification
- Supports both Ed25519 and HMAC-SHA256 algorithms
- Timestamp validation prevents replay attacks (5-minute window)

### Fail-Closed Security
- All webhook endpoints reject requests with invalid/missing signatures
- No fallback or default behavior for unauthenticated requests

---

## 📝 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_OAUTH_CLIENT_ID` | Yes | Google OAuth 2.0 Client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Yes | Google OAuth 2.0 Client Secret |
| `GOOGLE_OAUTH_REDIRECT_URI` | Yes | OAuth redirect URI |
| `II_AGENT_WEBHOOK_SECRET` | Yes | Secret for II-Agent webhook signature verification |
| `GOOGLE_CALENDAR_WEBHOOK_TOKEN` | Yes | Token for Google Calendar webhook verification |

---

## 🚀 Usage Examples

### Complete Google OAuth Flow

```javascript
// Step 1: Request OAuth URL
const response1 = await fetch('/api/auth/google/url', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ state: 'unique-state-123' })
});
const { url, csrfToken } = await response1.json();

// Step 2: Redirect user to Google OAuth
window.location.href = url;

// Step 3: After callback, exchange code for session
const urlParams = new URLSearchParams(window.location.search);
const code = urlParams.get('code');
const response2 = await fetch('/api/auth/google/login', {
  method: 'POST',
  body: new URLSearchParams({ code, redirect_uri: '...' })
});
const { user, token } = await response2.json();
```

### Trigger Calendar Sync

```javascript
const response = await fetch('/api/calendar-sync/sync', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify({
    direction: 'both',
    start_date: '2025-01-01T00:00:00Z',
    end_date: '2025-01-31T23:59:59Z'
  })
});
const result = await response.json();
```

### Create II-Agent Session

```javascript
const response = await fetch('/api/agent/sessions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify({
    goal: 'Analyze project documentation and generate a summary',
    context: { project_id: 'proj-123', workspace_id: 'ws-456' }
  })
});
const session = await response.json();
```

---

## 📚 Related Documentation

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [II-Agent Documentation](https://github.com/verduona/ii-agent)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Version:** 2.4.0
**Last Updated:** 2025-12-29
