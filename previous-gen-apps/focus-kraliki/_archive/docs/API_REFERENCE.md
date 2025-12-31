# Focus Lite API Reference

> **Version**: 2.1.0
> **Last Updated**: November 14, 2025
> **Base URL**: `http://127.0.0.1:3017`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Knowledge API](#knowledge-api)
3. [Agent Tools API](#agent-tools-api)
4. [Agent Sessions API](#agent-sessions-api)
5. [Settings API](#settings-api)
6. [Tasks API](#tasks-api)
7. [Projects API](#projects-api)
8. [AI API](#ai-api)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

---

## Authentication

All API endpoints (except registration and login) require JWT authentication.

### Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Obtaining a Token

**Register**

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response**
```json
{
  "id": "usr_abc123",
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Login**

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "usr_abc123",
    "email": "user@example.com",
    "isPremium": false,
    "usageCount": 42
  }
}
```

---

## Knowledge API

The Knowledge API manages item types and knowledge items.

### Item Types

#### List Item Types

```http
GET /api/knowledge/item-types?limit=50
Authorization: Bearer <token>
```

**Query Parameters**
- `limit` (optional): Max results (1-100, default: 50)

**Response**
```json
{
  "itemTypes": [
    {
      "id": "type_abc123",
      "userId": "usr_abc123",
      "name": "Ideas",
      "icon": "lightbulb",
      "color": "#FFD700",
      "createdAt": "2025-11-14T10:00:00Z"
    }
  ],
  "total": 5
}
```

#### Create Item Type

```http
POST /api/knowledge/item-types
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Meeting Notes",
  "icon": "calendar",
  "color": "#4A90E2"
}
```

**Response**
```json
{
  "id": "type_xyz789",
  "userId": "usr_abc123",
  "name": "Meeting Notes",
  "icon": "calendar",
  "color": "#4A90E2",
  "createdAt": "2025-11-14T10:05:00Z"
}
```

#### Get Item Type

```http
GET /api/knowledge/item-types/{type_id}
Authorization: Bearer <token>
```

**Response**
```json
{
  "id": "type_abc123",
  "userId": "usr_abc123",
  "name": "Ideas",
  "icon": "lightbulb",
  "color": "#FFD700",
  "createdAt": "2025-11-14T10:00:00Z"
}
```

#### Update Item Type

```http
PATCH /api/knowledge/item-types/{type_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Creative Ideas",
  "color": "#FF6B6B"
}
```

**Response**
```json
{
  "id": "type_abc123",
  "userId": "usr_abc123",
  "name": "Creative Ideas",
  "icon": "lightbulb",
  "color": "#FF6B6B",
  "createdAt": "2025-11-14T10:00:00Z"
}
```

#### Delete Item Type

```http
DELETE /api/knowledge/item-types/{type_id}
Authorization: Bearer <token>
```

**Response**
```json
{
  "success": true,
  "deletedId": "type_abc123"
}
```

**Note**: Cascade deletes all associated knowledge items.

### Knowledge Items

#### List Knowledge Items

```http
GET /api/knowledge/items?typeId=type_abc123&completed=false&limit=50
Authorization: Bearer <token>
```

**Query Parameters**
- `typeId` (optional): Filter by item type
- `completed` (optional): Filter by completion status
- `limit` (optional): Max results (1-100, default: 50)

**Response**
```json
{
  "items": [
    {
      "id": "item_abc123",
      "userId": "usr_abc123",
      "typeId": "type_abc123",
      "title": "AI-powered customer support",
      "content": "Explore using GPT-4 for automated support responses...",
      "item_metadata": {
        "priority": "high",
        "tags": ["ai", "customer-service"]
      },
      "completed": false,
      "createdAt": "2025-11-14T10:00:00Z",
      "updatedAt": "2025-11-14T10:00:00Z"
    }
  ],
  "total": 12
}
```

#### Create Knowledge Item

```http
POST /api/knowledge/items
Authorization: Bearer <token>
Content-Type: application/json

{
  "typeId": "type_abc123",
  "title": "Q4 Product Strategy",
  "content": "Focus areas: 1. User retention...",
  "item_metadata": {
    "priority": "high",
    "deadline": "2025-12-31"
  }
}
```

**Response**
```json
{
  "id": "item_xyz789",
  "userId": "usr_abc123",
  "typeId": "type_abc123",
  "title": "Q4 Product Strategy",
  "content": "Focus areas: 1. User retention...",
  "item_metadata": {
    "priority": "high",
    "deadline": "2025-12-31"
  },
  "completed": false,
  "createdAt": "2025-11-14T11:00:00Z",
  "updatedAt": "2025-11-14T11:00:00Z"
}
```

#### Get Knowledge Item

```http
GET /api/knowledge/items/{item_id}
Authorization: Bearer <token>
```

**Response**
```json
{
  "id": "item_abc123",
  "userId": "usr_abc123",
  "typeId": "type_abc123",
  "title": "AI-powered customer support",
  "content": "Explore using GPT-4...",
  "item_metadata": {
    "priority": "high"
  },
  "completed": false,
  "createdAt": "2025-11-14T10:00:00Z",
  "updatedAt": "2025-11-14T10:00:00Z"
}
```

#### Update Knowledge Item

```http
PATCH /api/knowledge/items/{item_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "AI customer support - Updated",
  "completed": true,
  "item_metadata": {
    "priority": "medium",
    "status": "implemented"
  }
}
```

**Response**
```json
{
  "id": "item_abc123",
  "userId": "usr_abc123",
  "typeId": "type_abc123",
  "title": "AI customer support - Updated",
  "content": "Explore using GPT-4...",
  "item_metadata": {
    "priority": "medium",
    "status": "implemented"
  },
  "completed": true,
  "createdAt": "2025-11-14T10:00:00Z",
  "updatedAt": "2025-11-14T12:00:00Z"
}
```

#### Delete Knowledge Item

```http
DELETE /api/knowledge/items/{item_id}
Authorization: Bearer <token>
```

**Response**
```json
{
  "success": true,
  "deletedId": "item_abc123"
}
```

#### Toggle Knowledge Item Completion

```http
POST /api/knowledge/items/{item_id}/toggle
Authorization: Bearer <token>
```

**Response**
```json
{
  "id": "item_abc123",
  "completed": true,
  "updatedAt": "2025-11-14T12:30:00Z"
}
```

#### Search Knowledge Items

```http
GET /api/knowledge/search?query=customer%20support&typeId=type_abc123
Authorization: Bearer <token>
```

**Query Parameters**
- `query` (required): Search term
- `typeId` (optional): Filter by item type

**Response**
```json
{
  "items": [
    {
      "id": "item_abc123",
      "title": "AI customer support",
      "content": "Explore using GPT-4...",
      "typeId": "type_abc123"
    }
  ],
  "total": 1,
  "query": "customer support"
}
```

---

## Agent Tools API

The Agent Tools API provides a simplified interface for II-Agent to interact with Focus Lite.

### Knowledge Tools

#### Create Knowledge Item (Agent)

```http
POST /api/agent-tools/knowledge/create
Authorization: Bearer <agent_token>
Content-Type: application/json

{
  "typeId": "type_abc123",
  "title": "Sprint Planning Notes",
  "content": "Discussion points from today's meeting...",
  "item_metadata": {
    "attendees": ["Alice", "Bob"],
    "duration": 60
  }
}
```

**Response**
```json
{
  "id": "item_xyz789",
  "userId": "usr_abc123",
  "typeId": "type_abc123",
  "title": "Sprint Planning Notes",
  "content": "Discussion points...",
  "item_metadata": {
    "attendees": ["Alice", "Bob"],
    "duration": 60
  },
  "completed": false,
  "createdAt": "2025-11-14T14:00:00Z",
  "updatedAt": "2025-11-14T14:00:00Z"
}
```

#### Update Knowledge Item (Agent)

```http
PATCH /api/agent-tools/knowledge/{item_id}
Authorization: Bearer <agent_token>
Content-Type: application/json

{
  "title": "Sprint Planning - Updated",
  "completed": true
}
```

**Response**
```json
{
  "id": "item_xyz789",
  "title": "Sprint Planning - Updated",
  "completed": true,
  "updatedAt": "2025-11-14T15:00:00Z"
}
```

#### List Knowledge Items (Agent)

```http
GET /api/agent-tools/knowledge?typeId=type_abc123&limit=50
Authorization: Bearer <agent_token>
```

**Query Parameters**
- `typeId` (optional): Filter by item type
- `limit` (optional): Max results (1-100, default: 50)

**Response**
```json
{
  "items": [
    {
      "id": "item_abc123",
      "title": "Sprint Planning Notes",
      "typeId": "type_abc123",
      "completed": false
    }
  ],
  "total": 1
}
```

### Task Tools

#### Create Task (Agent)

```http
POST /api/agent-tools/tasks
Authorization: Bearer <agent_token>
Content-Type: application/json

{
  "title": "Complete API documentation",
  "description": "Document all new endpoints added in Phase 8",
  "priority": 3,
  "estimatedMinutes": 120,
  "dueDate": "2025-11-20T17:00:00Z",
  "projectId": "proj_abc123"
}
```

**Response**
```json
{
  "id": "task_xyz789",
  "title": "Complete API documentation",
  "description": "Document all new endpoints...",
  "status": "pending",
  "priority": 3,
  "estimatedMinutes": 120,
  "dueDate": "2025-11-20T17:00:00Z",
  "projectId": "proj_abc123",
  "userId": "usr_abc123",
  "createdAt": "2025-11-14T16:00:00Z"
}
```

#### Update Task (Agent)

```http
PATCH /api/agent-tools/tasks/{task_id}
Authorization: Bearer <agent_token>
Content-Type: application/json

{
  "status": "completed",
  "priority": 4
}
```

**Response**
```json
{
  "id": "task_xyz789",
  "title": "Complete API documentation",
  "status": "completed",
  "priority": 4,
  "completedAt": "2025-11-14T18:00:00Z"
}
```

**Note**: When status changes to "completed", `completedAt` is automatically set.

#### List Tasks (Agent)

```http
GET /api/agent-tools/tasks?status=pending&projectId=proj_abc123&limit=50
Authorization: Bearer <agent_token>
```

**Query Parameters**
- `status` (optional): Filter by task status (pending, in_progress, completed, cancelled)
- `projectId` (optional): Filter by project
- `limit` (optional): Max results (1-100, default: 50)

**Response**
```json
{
  "tasks": [
    {
      "id": "task_abc123",
      "title": "Review security audit",
      "status": "pending",
      "priority": 5,
      "dueDate": "2025-11-15T17:00:00Z"
    }
  ],
  "total": 3
}
```

### Project Tools

#### Create or Get Project (Agent)

```http
POST /api/agent-tools/projects/create-or-get
Authorization: Bearer <agent_token>
Content-Type: application/json

{
  "name": "Website Redesign",
  "description": "Complete overhaul of public website",
  "color": "#FF6B6B",
  "icon": "globe"
}
```

**Response** (created)
```json
{
  "id": "proj_xyz789",
  "name": "Website Redesign",
  "description": "Complete overhaul of public website",
  "color": "#FF6B6B",
  "icon": "globe",
  "userId": "usr_abc123"
}
```

**Response** (existing)
```json
{
  "id": "proj_abc123",
  "name": "Website Redesign",
  "description": "Complete overhaul of public website",
  "color": "#FF6B6B",
  "icon": "globe",
  "userId": "usr_abc123"
}
```

**Note**: This endpoint is idempotent - if a project with the same name exists, it returns the existing project instead of creating a duplicate.

---

## Agent Sessions API

The Agent Sessions API manages authentication tokens for II-Agent.

### Create Agent Session

```http
POST /api/agent/sessions
Authorization: Bearer <user_token>
```

**Response**
```json
{
  "agentToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "sessionUuid": "session_abc123xyz",
  "userId": "usr_abc123",
  "expiresIn": 7200
}
```

**Fields**
- `agentToken`: JWT token for II-Agent to use (2-hour expiry)
- `sessionUuid`: Unique session identifier
- `userId`: Authenticated user's ID
- `expiresIn`: Token expiry in seconds (7200 = 2 hours)

**Usage**

1. Frontend calls this endpoint with user's auth token
2. Receives agent token and session UUID
3. Passes agent token to II-Agent
4. II-Agent uses token for all subsequent API calls

---

## Settings API

The Settings API manages user preferences and API keys.

### OpenRouter Key Management

#### Save OpenRouter Key

```http
POST /api/settings/openrouter-key
Authorization: Bearer <token>
Content-Type: application/json

{
  "apiKey": "sk-or-v1-abc123..."
}
```

**Response**
```json
{
  "success": true,
  "message": "API key saved successfully"
}
```

#### Delete OpenRouter Key

```http
DELETE /api/settings/openrouter-key
Authorization: Bearer <token>
```

**Response**
```json
{
  "success": true,
  "message": "API key removed"
}
```

#### Test OpenRouter Key

```http
POST /api/settings/test-openrouter-key
Content-Type: application/json

{
  "apiKey": "sk-or-v1-abc123..."
}
```

**Response** (valid)
```json
{
  "success": true,
  "message": "API key is valid"
}
```

**Response** (invalid)
```json
{
  "success": false,
  "message": "API key validation failed: 401"
}
```

### Usage Statistics

#### Get Usage Stats

```http
GET /api/settings/usage-stats
Authorization: Bearer <token>
```

**Response** (free tier)
```json
{
  "usageCount": 42,
  "isPremium": false,
  "remainingUsage": 58,
  "hasCustomKey": false
}
```

**Response** (BYOK)
```json
{
  "usageCount": 142,
  "isPremium": false,
  "remainingUsage": null,
  "hasCustomKey": true
}
```

**Fields**
- `usageCount`: Total AI requests made
- `isPremium`: Premium subscription status
- `remainingUsage`: Requests remaining (null for premium/BYOK)
- `hasCustomKey`: Whether user has BYOK configured

---

## Tasks API

### Create Task

```http
POST /api/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Review pull request #123",
  "description": "Check code quality and test coverage",
  "priority": 3,
  "status": "pending",
  "estimatedMinutes": 30,
  "dueDate": "2025-11-15T17:00:00Z",
  "projectId": "proj_abc123"
}
```

**Response**
```json
{
  "id": "task_xyz789",
  "title": "Review pull request #123",
  "description": "Check code quality and test coverage",
  "status": "pending",
  "priority": 3,
  "estimatedMinutes": 30,
  "dueDate": "2025-11-15T17:00:00Z",
  "projectId": "proj_abc123",
  "userId": "usr_abc123",
  "createdAt": "2025-11-14T10:00:00Z",
  "completedAt": null
}
```

### List Tasks

```http
GET /api/tasks?status=pending&priority=3&projectId=proj_abc123&limit=20
Authorization: Bearer <token>
```

**Query Parameters**
- `status` (optional): pending | in_progress | completed | cancelled
- `priority` (optional): 1-5
- `projectId` (optional): Filter by project
- `search` (optional): Search in title/description
- `limit` (optional): Max results (default: 50)
- `offset` (optional): Pagination offset

**Response**
```json
{
  "tasks": [
    {
      "id": "task_abc123",
      "title": "Review pull request #123",
      "status": "pending",
      "priority": 3,
      "dueDate": "2025-11-15T17:00:00Z"
    }
  ],
  "total": 5,
  "limit": 20,
  "offset": 0
}
```

### Update Task

```http
PATCH /api/tasks/{task_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "in_progress",
  "priority": 4
}
```

**Response**
```json
{
  "id": "task_abc123",
  "status": "in_progress",
  "priority": 4,
  "updatedAt": "2025-11-14T11:00:00Z"
}
```

### Delete Task

```http
DELETE /api/tasks/{task_id}
Authorization: Bearer <token>
```

**Response**
```json
{
  "success": true,
  "deletedId": "task_abc123"
}
```

---

## Projects API

### Create Project

```http
POST /api/projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Mobile App Rewrite",
  "description": "Rebuild mobile app with React Native",
  "color": "#4A90E2",
  "icon": "mobile"
}
```

**Response**
```json
{
  "id": "proj_xyz789",
  "name": "Mobile App Rewrite",
  "description": "Rebuild mobile app with React Native",
  "color": "#4A90E2",
  "icon": "mobile",
  "userId": "usr_abc123",
  "createdAt": "2025-11-14T10:00:00Z"
}
```

### List Projects

```http
GET /api/projects?limit=20
Authorization: Bearer <token>
```

**Response**
```json
{
  "projects": [
    {
      "id": "proj_abc123",
      "name": "Website Redesign",
      "description": "Complete overhaul",
      "color": "#FF6B6B",
      "taskCount": 12,
      "completedTaskCount": 5
    }
  ],
  "total": 3
}
```

### Get Project

```http
GET /api/projects/{project_id}
Authorization: Bearer <token>
```

**Response**
```json
{
  "id": "proj_abc123",
  "name": "Website Redesign",
  "description": "Complete overhaul of public website",
  "color": "#FF6B6B",
  "icon": "globe",
  "tasks": [
    {
      "id": "task_123",
      "title": "Design mockups",
      "status": "completed"
    }
  ],
  "stats": {
    "totalTasks": 12,
    "completedTasks": 5,
    "progress": 41.67
  }
}
```

### Update Project

```http
PATCH /api/projects/{project_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Website Redesign 2.0",
  "color": "#00C9A7"
}
```

**Response**
```json
{
  "id": "proj_abc123",
  "name": "Website Redesign 2.0",
  "color": "#00C9A7",
  "updatedAt": "2025-11-14T12:00:00Z"
}
```

### Delete Project

```http
DELETE /api/projects/{project_id}
Authorization: Bearer <token>
```

**Response**
```json
{
  "success": true,
  "deletedId": "proj_abc123"
}
```

**Note**: Deleting a project does not delete associated tasks (they become unassigned).

---

## AI API

### Chat

```http
POST /api/ai/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "What are my top priorities for today?",
  "conversationId": "conv_abc123",
  "useCache": true
}
```

**Response**
```json
{
  "response": "Based on your tasks, your top priorities are:\n1. Review security audit (due today)\n2. Complete API documentation\n3. Fix critical bug #456",
  "conversationId": "conv_abc123",
  "tokensUsed": 245,
  "cached": false
}
```

### Parse Task

```http
POST /api/ai/parse-task
Authorization: Bearer <token>
Content-Type: application/json

{
  "input": "Review the authentication code and fix any security issues by next Friday"
}
```

**Response**
```json
{
  "title": "Review authentication code and fix security issues",
  "description": "Review the authentication code and identify security vulnerabilities",
  "priority": 4,
  "estimatedMinutes": 120,
  "dueDate": "2025-11-22T17:00:00Z",
  "suggestedProject": "Security Improvements"
}
```

### Function Calling (Knowledge AI)

```http
POST /api/ai/chat-with-tools
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Create an idea about implementing dark mode",
  "conversationHistory": []
}
```

**Response**
```json
{
  "message": "I've created a new idea: 'Implement dark mode across the application'. Would you like me to create some initial tasks for this?",
  "toolCalls": [
    {
      "function": "create_knowledge_item",
      "arguments": {
        "typeId": "type_ideas",
        "title": "Implement dark mode",
        "content": "Add system-wide dark mode support with user preference toggle"
      },
      "result": {
        "id": "item_xyz789",
        "created": true
      }
    }
  ],
  "conversationId": "conv_xyz789"
}
```

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "error_type": "ValidationError"
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Request completed successfully |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource |
| 422 | Validation Error | Pydantic validation failed |
| 429 | Rate Limit | Too many requests |
| 500 | Server Error | Internal server error |

### Common Errors

**Invalid Token**
```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

**Resource Not Found**
```json
{
  "detail": "Knowledge item with id 'item_xyz' not found",
  "status_code": 404
}
```

**Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "status_code": 422
}
```

**Rate Limit**
```json
{
  "detail": "Usage limit exceeded. Upgrade to premium or add BYOK key.",
  "status_code": 429,
  "usageCount": 100,
  "limit": 100
}
```

---

## Rate Limiting

### Free Tier

- **Limit**: 100 AI requests per month
- **Reset**: Monthly on signup anniversary
- **Scope**: Per user account

### Premium Tier

- **Limit**: Unlimited
- **Cost**: $10/month

### BYOK (Bring Your Own Key)

- **Limit**: Unlimited
- **Cost**: Pay-as-you-go via OpenRouter
- **Configuration**: Settings → API Keys

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1699920000
```

---

## Webhooks (Coming Soon)

Future webhook support for:
- Task completion events
- Knowledge item creation
- Project updates
- AI conversation milestones

---

## API Versioning

Current version: **v1**

All endpoints are prefixed with `/api/`

Future versions will use: `/api/v2/`, `/api/v3/`, etc.

---

## Interactive API Documentation

Visit the auto-generated Swagger UI for interactive testing:

```
http://127.0.0.1:3017/docs
```

Features:
- Try endpoints directly in browser
- View request/response schemas
- OAuth2 authentication flow
- Example payloads

---

## Client Libraries

### Python

```python
import requests

class FocusLiteClient:
    def __init__(self, token):
        self.base_url = "http://127.0.0.1:3017/api"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def create_knowledge_item(self, type_id, title, content):
        response = requests.post(
            f"{self.base_url}/knowledge/items",
            headers=self.headers,
            json={
                "typeId": type_id,
                "title": title,
                "content": content
            }
        )
        return response.json()

# Usage
client = FocusLiteClient("your_token_here")
item = client.create_knowledge_item(
    type_id="type_abc123",
    title="My Idea",
    content="This is a great idea..."
)
```

### JavaScript/TypeScript

```typescript
class FocusLiteClient {
  private baseUrl = "http://127.0.0.1:3017/api";
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  async createKnowledgeItem(typeId: string, title: string, content: string) {
    const response = await fetch(`${this.baseUrl}/knowledge/items`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${this.token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ typeId, title, content })
    });
    return response.json();
  }
}

// Usage
const client = new FocusLiteClient("your_token_here");
const item = await client.createKnowledgeItem(
  "type_abc123",
  "My Idea",
  "This is a great idea..."
);
```

---

## Deprecated Endpoints

### Swarm Tools API (Deprecated)

> **Warning**: The `/swarm-tools/*` endpoints are deprecated as of v2.1.0 and will be removed in v3.0.0.
>
> **Migration Path**: Use `/agent-tools/*` endpoints via II-Agent instead.

**Deprecated Endpoints:**
- `POST /api/swarm-tools/tasks/create-from-nl` → Use `POST /api/agent-tools/tasks`
- `POST /api/swarm-tools/tasks/get-with-context` → Use `GET /api/agent-tools/tasks`
- `POST /api/swarm-tools/projects/create-or-get` → Use `POST /api/agent-tools/projects/create-or-get`
- `POST /api/swarm-tools/cognitive/*` → Removed (use Shadow Analysis API)
- `POST /api/swarm-tools/shadow/*` → Removed (use Shadow Analysis API)
- `POST /api/swarm-tools/memory/*` → Removed (use Flow Memory API)

**Timeline:**
- v2.1.0 (Current): Deprecation warnings added
- v2.5.0 (Q1 2026): Endpoints return 410 Gone
- v3.0.0 (Q2 2026): Endpoints removed

---

## Support

- **Documentation**: [User Guide](/docs/USER_GUIDE.md)
- **Developer Guide**: [DEVELOPER_GUIDE.md](/docs/DEVELOPER_GUIDE.md)
- **GitHub Issues**: https://github.com/your-org/focus-lite/issues
- **Email**: support@focuslite.app

---

**Focus Lite API** - Empowering developers to build on top of AI-first productivity.
