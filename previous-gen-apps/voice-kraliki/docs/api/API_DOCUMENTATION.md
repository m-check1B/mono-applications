# CC-Lite 2026 - API Documentation

**Version:** 2.0.0
**Last Updated:** November 11, 2025
**Base URL:** `http://localhost:8000` (Development) | `https://api.yourdomain.com` (Production)

## Table of Contents

1. [Authentication](#authentication)
2. [Campaigns](#campaigns)
3. [Contacts & Call Lists](#contacts--call-lists)
4. [Campaign Templates](#campaign-templates)
5. [Teams & Agents](#teams--agents)
6. [Queues](#queues)
7. [Companies](#companies)
8. [Knowledge Base](#knowledge-base)
9. [Documents](#documents)
10. [IVR Flows](#ivr-flows)
11. [Routing Rules](#routing-rules)
12. [Recordings](#recordings)
13. [Voicemail](#voicemail)
14. [Analytics & Metrics](#analytics--metrics)
15. [Reports](#reports)
16. [Error Codes](#error-codes)

## Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## Authentication

All API endpoints (except `/auth/register` and `/auth/login`) require authentication using JWT tokens.

### Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Endpoints

#### Register New User
```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "organization": "Acme Corp"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "organization": "Acme Corp",
  "is_active": true,
  "created_at": "2025-11-11T10:00:00Z"
}
```

#### Login
```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "organization": "Acme Corp",
  "is_active": true,
  "created_at": "2025-11-11T10:00:00Z"
}
```

## Campaigns

### List Campaigns
```http
GET /api/v1/campaigns?status=active&limit=50&offset=0
```

**Query Parameters:**
- `status` (optional): Filter by status (draft, active, paused, completed, archived)
- `search` (optional): Search by name
- `limit` (optional): Results per page (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Q4 Sales Campaign",
    "description": "Outbound sales for Q4 products",
    "status": "active",
    "campaign_type": "outbound",
    "provider_type": "openai",
    "provider_model": "gpt-4-realtime-preview",
    "start_date": "2025-11-01T00:00:00Z",
    "end_date": "2025-12-31T23:59:59Z",
    "total_contacts": 1000,
    "completed_calls": 350,
    "success_rate": 0.68,
    "created_by_id": 1,
    "created_at": "2025-10-28T10:00:00Z",
    "updated_at": "2025-11-11T12:00:00Z"
  }
]
```

### Create Campaign
```http
POST /api/v1/campaigns
```

**Request Body:**
```json
{
  "name": "Holiday Sales Campaign",
  "description": "Holiday promotions for premium customers",
  "campaign_type": "outbound",
  "status": "draft",
  "provider_type": "openai",
  "provider_model": "gpt-4-realtime-preview",
  "provider_config": {
    "temperature": 0.7,
    "voice": "alloy"
  },
  "system_prompt": "You are a friendly sales representative...",
  "start_date": "2025-12-01T00:00:00Z",
  "end_date": "2025-12-25T23:59:59Z",
  "max_daily_calls": 100,
  "retry_failed": true,
  "max_retries": 3
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "name": "Holiday Sales Campaign",
  "status": "draft",
  "created_at": "2025-11-11T12:30:00Z",
  ...
}
```

### Get Campaign Details
```http
GET /api/v1/campaigns/{campaign_id}
```

### Update Campaign
```http
PUT /api/v1/campaigns/{campaign_id}
```

### Delete Campaign
```http
DELETE /api/v1/campaigns/{campaign_id}
```

**Response (204 No Content)**

### Campaign Actions

#### Start Campaign
```http
POST /api/v1/campaigns/{campaign_id}/start
```

#### Pause Campaign
```http
POST /api/v1/campaigns/{campaign_id}/pause
```

#### Clone Campaign
```http
POST /api/v1/campaigns/{campaign_id}/clone
```

**Request Body:**
```json
{
  "name": "Q1 Sales Campaign (Copy)"
}
```

#### Get Campaign Statistics
```http
GET /api/v1/campaigns/{campaign_id}/stats
```

**Response (200 OK):**
```json
{
  "total_contacts": 1000,
  "completed_calls": 450,
  "success_rate": 0.72,
  "avg_call_duration": 185.5,
  "total_call_time": 83475,
  "conversion_rate": 0.34,
  "cost_per_call": 0.45
}
```

## Contacts & Call Lists

### List Contacts
```http
GET /api/v1/contacts?campaign_id=1&status=pending&limit=100
```

**Query Parameters:**
- `campaign_id` (optional): Filter by campaign
- `status` (optional): Filter by status (pending, called, completed, failed)
- `search` (optional): Search by name, email, or phone
- `limit`, `offset`: Pagination

### Create Contact
```http
POST /api/v1/contacts
```

**Request Body:**
```json
{
  "campaign_id": 1,
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com",
  "phone_number": "+1234567890",
  "company": "Tech Corp",
  "custom_fields": {
    "industry": "Technology",
    "company_size": "100-500",
    "interests": ["AI", "Automation"]
  },
  "priority": 5
}
```

### Import Contacts (Bulk)
```http
POST /api/v1/contacts/import
```

**Request Body:**
```json
{
  "campaign_id": 1,
  "contacts": [
    {
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": "+1234567890",
      "email": "john@example.com"
    },
    {
      "first_name": "Jane",
      "last_name": "Smith",
      "phone_number": "+1234567891",
      "email": "jane@example.com"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "imported": 2,
  "failed": 0,
  "errors": []
}
```

### Update Contact
```http
PUT /api/v1/contacts/{contact_id}
```

### Delete Contact
```http
DELETE /api/v1/contacts/{contact_id}
```

### List Call Lists
```http
GET /api/v1/call-lists?campaign_id=1
```

### Create Call List
```http
POST /api/v1/call-lists
```

**Request Body:**
```json
{
  "campaign_id": 1,
  "name": "Priority Contacts",
  "filters": {
    "priority_min": 7,
    "status": "pending"
  },
  "sort_by": "priority",
  "sort_order": "desc"
}
```

## Campaign Templates

### List Templates
```http
GET /api/v1/campaign-templates?is_public=true
```

### Create Template
```http
POST /api/v1/campaign-templates
```

**Request Body:**
```json
{
  "name": "Sales Outreach Template",
  "description": "Standard template for B2B sales calls",
  "campaign_type": "outbound",
  "provider_type": "openai",
  "provider_model": "gpt-4-realtime-preview",
  "system_prompt": "You are a professional sales representative...",
  "default_config": {
    "temperature": 0.7,
    "max_duration": 300
  },
  "is_public": true
}
```

### Get Template
```http
GET /api/v1/campaign-templates/{template_id}
```

### Update/Delete Template
```http
PUT /api/v1/campaign-templates/{template_id}
DELETE /api/v1/campaign-templates/{template_id}
```

## Teams & Agents

### List Teams
```http
GET /api/v1/teams?is_active=true
```

### Create Team
```http
POST /api/v1/teams
```

**Request Body:**
```json
{
  "name": "Sales Team Alpha",
  "description": "Senior sales representatives",
  "team_type": "sales",
  "max_agents": 20,
  "supervisor_id": 5,
  "is_active": true
}
```

### Get Team Details
```http
GET /api/v1/teams/{team_id}
```

### Update/Delete Team
```http
PUT /api/v1/teams/{team_id}
DELETE /api/v1/teams/{team_id}
```

### Get Team Agents
```http
GET /api/v1/teams/{team_id}/agents
```

### Get Team Performance
```http
GET /api/v1/teams/{team_id}/performance?period=7d
```

**Response (200 OK):**
```json
{
  "total_calls": 450,
  "avg_duration": 185.5,
  "success_rate": 0.72,
  "agents": [
    {
      "agent_id": 10,
      "name": "John Agent",
      "calls": 95,
      "success_rate": 0.78
    }
  ]
}
```

### List Agents
```http
GET /api/v1/agents?team_id=1&status=available
```

### Create Agent
```http
POST /api/v1/agents
```

**Request Body:**
```json
{
  "user_id": 15,
  "team_id": 1,
  "agent_number": "AG-001",
  "status": "available",
  "skill_level": 8,
  "max_concurrent_calls": 3,
  "languages": ["en", "es"],
  "specialties": ["sales", "support"]
}
```

### Get Agent Profile
```http
GET /api/v1/agents/{agent_id}
```

### Update Agent
```http
PUT /api/v1/agents/{agent_id}
```

### Delete Agent
```http
DELETE /api/v1/agents/{agent_id}
```

### Add Agent Skills
```http
POST /api/v1/agents/{agent_id}/skills
```

**Request Body:**
```json
{
  "skills": [
    {
      "skill_name": "technical_support",
      "proficiency": 8
    },
    {
      "skill_name": "spanish_fluent",
      "proficiency": 10
    }
  ]
}
```

### Get Agent Performance
```http
GET /api/v1/agents/{agent_id}/performance?period=30d
```

## Queues

### List Queues
```http
GET /api/v1/queues?status=active
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Inbound Sales",
    "queue_type": "inbound",
    "status": "active",
    "current_calls": 12,
    "waiting_calls": 5,
    "max_size": 100,
    "avg_wait_time": 45.5,
    "timeout_seconds": 180
  }
]
```

### Get Queue Details
```http
GET /api/v1/queues/{queue_id}
```

### Get Queued Calls
```http
GET /api/v1/queues/{queue_id}/calls
```

**Response (200 OK):**
```json
[
  {
    "call_id": "call_abc123",
    "caller_number": "+1234567890",
    "position": 3,
    "wait_time": 67,
    "priority": 5,
    "queued_at": "2025-11-11T12:15:00Z"
  }
]
```

## Companies

### List Companies
```http
GET /api/v1/companies?is_active=true&limit=50
```

### Create Company
```http
POST /api/v1/companies
```

**Request Body:**
```json
{
  "name": "Acme Corporation",
  "domain": "acme.com",
  "industry": "Technology",
  "size": "500-1000",
  "description": "Leading provider of enterprise software solutions",
  "contact_email": "info@acme.com",
  "contact_phone": "+1234567890",
  "address": {
    "street": "123 Tech Street",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94102",
    "country": "USA"
  },
  "settings": {
    "timezone": "America/Los_Angeles",
    "language": "en"
  },
  "is_active": true
}
```

### Get Company
```http
GET /api/v1/companies/{company_id}
```

### Update/Delete Company
```http
PUT /api/v1/companies/{company_id}
DELETE /api/v1/companies/{company_id}
```

## Knowledge Base

### List Articles
```http
GET /api/v1/knowledge?company_id=1&category=support&limit=50
```

### Create Article
```http
POST /api/v1/knowledge
```

**Request Body:**
```json
{
  "company_id": 1,
  "title": "How to Reset Password",
  "content": "To reset your password, follow these steps...",
  "category": "support",
  "tags": ["password", "security", "account"],
  "is_public": true,
  "language": "en",
  "metadata": {
    "author": "Support Team",
    "last_reviewed": "2025-11-01"
  }
}
```

### Get Article
```http
GET /api/v1/knowledge/{article_id}
```

### Update/Delete Article
```http
PUT /api/v1/knowledge/{article_id}
DELETE /api/v1/knowledge/{article_id}
```

### Semantic Search
```http
POST /api/v1/knowledge/search
```

**Request Body:**
```json
{
  "query": "how to reset my password",
  "company_id": 1,
  "limit": 5,
  "min_score": 0.7
}
```

**Response (200 OK):**
```json
[
  {
    "id": 42,
    "title": "Password Reset Guide",
    "content": "To reset your password...",
    "score": 0.92,
    "category": "support"
  },
  {
    "id": 78,
    "title": "Account Security FAQs",
    "content": "Common security questions...",
    "score": 0.85,
    "category": "security"
  }
]
```

## Documents

### List Documents
```http
GET /api/v1/documents?company_id=1&category=training
```

### Upload Document
```http
POST /api/v1/documents
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Document file (PDF, DOCX, TXT, etc.)
- `company_id`: Company ID
- `category`: Document category
- `description`: Optional description
- `tags`: Optional tags (JSON array)

### Get Document
```http
GET /api/v1/documents/{document_id}
```

### Delete Document
```http
DELETE /api/v1/documents/{document_id}
```

## IVR Flows

### List IVR Flows
```http
GET /api/ivr/flows?is_active=true
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Main Menu IVR",
    "description": "Primary customer service menu",
    "is_active": true,
    "version": 3,
    "timeout_seconds": 30,
    "max_retries": 3,
    "created_at": "2025-10-15T10:00:00Z",
    "node_count": 12
  }
]
```

### Create IVR Flow
```http
POST /api/ivr/flows
```

**Request Body:**
```json
{
  "name": "Sales IVR Flow",
  "description": "IVR for sales inquiries",
  "timeout_seconds": 30,
  "max_retries": 3,
  "language": "en",
  "is_active": false
}
```

### Get IVR Flow
```http
GET /api/ivr/flows/{flow_id}
```

**Response includes full node tree:**
```json
{
  "id": 1,
  "name": "Main Menu IVR",
  "nodes": [
    {
      "id": 1,
      "node_type": "menu",
      "name": "Main Menu",
      "prompt_text": "Welcome! Press 1 for Sales, 2 for Support...",
      "menu_options": [
        {
          "dtmf_key": "1",
          "description": "Sales",
          "target_node_id": 2
        },
        {
          "dtmf_key": "2",
          "description": "Support",
          "target_node_id": 3
        }
      ]
    }
  ]
}
```

### Update/Delete IVR Flow
```http
PUT /api/ivr/flows/{flow_id}
DELETE /api/ivr/flows/{flow_id}
```

### Publish Flow Version
```http
POST /api/ivr/flows/{flow_id}/publish
```

**Request Body:**
```json
{
  "version_notes": "Added new support menu option"
}
```

### Get Flow Analytics
```http
GET /api/ivr/flows/{flow_id}/analytics?period=7d
```

**Response (200 OK):**
```json
{
  "total_sessions": 1250,
  "avg_duration": 95.5,
  "completion_rate": 0.78,
  "most_used_paths": [
    {
      "path": "menu -> sales -> agent",
      "count": 450
    }
  ],
  "drop_off_points": [
    {
      "node_id": 5,
      "drop_rate": 0.15
    }
  ]
}
```

## Routing Rules

### List Routing Rules
```http
GET /api/routing/rules?is_active=true&priority_min=5
```

### Create Routing Rule
```http
POST /api/routing/rules
```

**Request Body:**
```json
{
  "name": "VIP Customer Routing",
  "description": "Route VIP customers to senior agents",
  "priority": 10,
  "strategy": "skill_based",
  "is_active": true,
  "conditions": [
    {
      "field": "customer_tier",
      "operator": "equals",
      "value": "VIP",
      "logic": "AND"
    },
    {
      "field": "call_type",
      "operator": "in",
      "value": ["sales", "support"],
      "logic": "AND"
    }
  ],
  "targets": [
    {
      "target_type": "team",
      "target_id": 5,
      "weight": 70
    },
    {
      "target_type": "agent",
      "target_id": 12,
      "weight": 30
    }
  ],
  "fallback_action": {
    "action_type": "queue",
    "queue_id": 3
  }
}
```

### Get/Update/Delete Routing Rule
```http
GET /api/routing/rules/{rule_id}
PUT /api/routing/rules/{rule_id}
DELETE /api/routing/rules/{rule_id}
```

## Recordings

### List Recordings
```http
GET /api/recordings?campaign_id=1&start_date=2025-11-01&limit=100
```

**Query Parameters:**
- `campaign_id`, `agent_id`, `team_id`: Filter by entity
- `start_date`, `end_date`: Date range filter
- `duration_min`, `duration_max`: Duration filters
- `has_transcription`: Filter by transcription availability

### Get Recording
```http
GET /api/recordings/{recording_id}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "call_id": "call_abc123",
  "campaign_id": 1,
  "agent_id": 10,
  "duration": 185,
  "file_url": "https://storage.example.com/recordings/abc123.mp3",
  "file_size_bytes": 2945600,
  "recorded_at": "2025-11-11T10:30:00Z",
  "has_transcription": true,
  "sentiment_score": 0.75,
  "keywords": ["pricing", "demo", "follow-up"]
}
```

### Delete Recording
```http
DELETE /api/recordings/{recording_id}
```

### Get Transcription
```http
GET /api/recordings/{recording_id}/transcription
```

**Response (200 OK):**
```json
{
  "recording_id": 1,
  "text": "Hello, this is John from Sales...",
  "segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "speaker": "agent",
      "text": "Hello, this is John from Sales"
    },
    {
      "start": 3.6,
      "end": 7.2,
      "speaker": "customer",
      "text": "Hi, I'm interested in your product"
    }
  ],
  "language": "en",
  "confidence": 0.95
}
```

### Analyze Recording
```http
POST /api/recordings/{recording_id}/analyze
```

**Request Body:**
```json
{
  "analysis_types": ["sentiment", "keywords", "summary", "compliance"]
}
```

**Response (200 OK):**
```json
{
  "sentiment": {
    "overall": 0.75,
    "positive": 0.80,
    "negative": 0.05,
    "neutral": 0.15
  },
  "keywords": [
    {"word": "pricing", "count": 5, "relevance": 0.9},
    {"word": "demo", "count": 3, "relevance": 0.85}
  ],
  "summary": "Customer inquired about pricing and requested a product demo...",
  "compliance": {
    "passed": true,
    "issues": []
  }
}
```

## Voicemail

### List Voicemails
```http
GET /api/voicemail?status=new&assigned_to_id=10
```

### Get Voicemail
```http
GET /api/voicemail/{voicemail_id}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "from_number": "+1234567890",
  "to_number": "+1987654321",
  "duration": 45,
  "status": "new",
  "message_url": "https://storage.example.com/voicemail/vm123.mp3",
  "transcription": "Hi, this is Jane calling about the quote...",
  "received_at": "2025-11-11T14:30:00Z",
  "assigned_to_id": 10,
  "priority": 5
}
```

### Update Voicemail
```http
PUT /api/voicemail/{voicemail_id}
```

**Request Body:**
```json
{
  "status": "completed",
  "assigned_to_id": 10,
  "notes": "Returned call and provided quote"
}
```

### Delete Voicemail
```http
DELETE /api/voicemail/{voicemail_id}
```

## Analytics & Metrics

### Record Metric
```http
POST /api/analytics/metrics
```

**Request Body:**
```json
{
  "metric_type": "call",
  "metric_name": "call_duration",
  "value": 185.5,
  "team_id": 1,
  "agent_id": 10,
  "tags": {
    "campaign": "Q4_Sales",
    "outcome": "success"
  },
  "dimensions": {
    "provider": "openai",
    "language": "en"
  }
}
```

### Query Metrics
```http
GET /api/analytics/metrics?metric_type=call&metric_name=call_duration&start_date=2025-11-01&end_date=2025-11-11
```

**Query Parameters:**
- `metric_type`, `metric_name`: Filter by type and name
- `start_date`, `end_date`: Date range
- `team_id`, `agent_id`: Filter by entity
- `limit`, `offset`: Pagination

### Get Aggregated Metrics
```http
GET /api/analytics/aggregations?metric_name=call_duration&granularity=hour&limit=24
```

**Query Parameters:**
- `metric_name`: Metric to aggregate
- `granularity`: minute, hour, day, week, month
- `start_date`, `end_date`: Date range
- `limit`: Number of results

**Response (200 OK):**
```json
[
  {
    "metric_name": "call_duration",
    "granularity": "hour",
    "value": 182.5,
    "count": 45,
    "window_start": "2025-11-11T10:00:00Z",
    "window_end": "2025-11-11T11:00:00Z"
  },
  {
    "metric_name": "call_duration",
    "granularity": "hour",
    "value": 195.2,
    "count": 52,
    "window_start": "2025-11-11T11:00:00Z",
    "window_end": "2025-11-11T12:00:00Z"
  }
]
```

### List Alerts
```http
GET /api/analytics/alerts?status=active&severity=critical
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "alert_name": "High Call Failure Rate",
    "severity": "critical",
    "message": "Call failure rate (15%) exceeds threshold (10%)",
    "actual_value": 0.15,
    "threshold_value": 0.10,
    "metric_type": "call",
    "metric_name": "failure_rate",
    "triggered_at": "2025-11-11T12:45:00Z",
    "status": "active",
    "team_id": 1
  }
]
```

### Acknowledge Alert
```http
PUT /api/analytics/alerts/{alert_id}/acknowledge
```

**Request Body:**
```json
{
  "acknowledged_by_id": 1,
  "notes": "Investigating root cause, temporary network issue identified"
}
```

### List Metric Thresholds
```http
GET /api/analytics/thresholds?is_active=true
```

### Create Threshold
```http
POST /api/analytics/thresholds
```

**Request Body:**
```json
{
  "metric_type": "call",
  "metric_name": "failure_rate",
  "threshold_value": 0.10,
  "comparison_operator": "greater_than",
  "severity": "warning",
  "window_minutes": 60,
  "alert_message": "Call failure rate exceeds 10% in the last hour",
  "team_id": 1,
  "is_active": true
}
```

### Update/Delete Threshold
```http
PUT /api/analytics/thresholds/{threshold_id}
DELETE /api/analytics/thresholds/{threshold_id}
```

### Dashboard Overview
```http
GET /api/analytics/dashboard/overview?period_hours=24
```

**Response (200 OK):**
```json
{
  "call_metrics": {
    "total_calls": 1250,
    "avg_duration": 185.5,
    "max_duration": 450,
    "min_duration": 30
  },
  "queue_metrics": {
    "avg_wait_time": 45.5,
    "max_wait_time": 180
  },
  "alerts": {
    "active_count": 3,
    "critical_count": 1
  }
}
```

## Reports

### List Report Templates
```http
GET /api/reports/templates?report_type=agent_performance&is_public=true
```

### Create Report Template
```http
POST /api/reports/templates
```

**Request Body:**
```json
{
  "name": "Weekly Sales Performance",
  "description": "Weekly report of sales team performance metrics",
  "report_type": "agent_performance",
  "query_definition": {
    "metrics": ["total_calls", "success_rate", "avg_duration"],
    "filters": {
      "team_type": "sales"
    },
    "grouping": ["agent_id", "week"]
  },
  "default_format": "pdf",
  "is_public": false,
  "version": 1
}
```

### Get/Update/Delete Template
```http
GET /api/reports/templates/{template_id}
PUT /api/reports/templates/{template_id}
DELETE /api/reports/templates/{template_id}
```

### List Reports
```http
GET /api/reports/?status=completed&limit=50
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Q4 Sales Performance Report",
    "report_type": "agent_performance",
    "status": "completed",
    "format": "pdf",
    "file_url": "https://storage.example.com/reports/report_1.pdf",
    "file_size_bytes": 524288,
    "expires_at": "2025-12-11T12:00:00Z",
    "requested_at": "2025-11-11T12:00:00Z",
    "completed_at": "2025-11-11T12:05:00Z"
  }
]
```

### Generate Report
```http
POST /api/reports/generate
```

**Request Body:**
```json
{
  "name": "Monthly Performance Report - November",
  "template_id": 5,
  "format": "pdf",
  "filters": {
    "start_date": "2025-11-01",
    "end_date": "2025-11-30",
    "team_id": 1
  },
  "parameters": {
    "include_charts": true,
    "include_raw_data": false
  }
}
```

**Response (202 Accepted):**
```json
{
  "id": 42,
  "name": "Monthly Performance Report - November",
  "status": "generating",
  "estimated_completion": "2025-11-11T12:15:00Z"
}
```

### Get Report
```http
GET /api/reports/{report_id}
```

### Delete Report
```http
DELETE /api/reports/{report_id}
```

### List Report Schedules
```http
GET /api/reports/schedules?is_active=true
```

### Create Schedule
```http
POST /api/reports/schedules
```

**Request Body:**
```json
{
  "name": "Weekly Sales Report",
  "template_id": 5,
  "schedule_type": "weekly",
  "schedule_config": {
    "day_of_week": 1,
    "hour": 9,
    "minute": 0,
    "timezone": "America/Los_Angeles"
  },
  "format": "pdf",
  "recipients": ["manager@example.com", "director@example.com"],
  "is_active": true
}
```

### Update/Delete Schedule
```http
PUT /api/reports/schedules/{schedule_id}
DELETE /api/reports/schedules/{schedule_id}
```

## Error Codes

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content to return
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate)
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "field": "email",
  "timestamp": "2025-11-11T12:00:00Z"
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_ERROR`: Authentication failed
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `DUPLICATE_RESOURCE`: Resource already exists
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `EXTERNAL_SERVICE_ERROR`: Third-party service error

## Rate Limiting

- **Default Limit:** 100 requests per minute per user
- **Burst Limit:** 200 requests per minute
- **Headers:**
  - `X-RateLimit-Limit`: Total requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)

## Pagination

For list endpoints that support pagination:

```http
GET /api/v1/campaigns?limit=50&offset=0
```

**Response Headers:**
- `X-Total-Count`: Total number of records
- `X-Page-Count`: Total number of pages
- `Link`: Links to first, prev, next, last pages

## Webhooks (Future)

Future webhook support for:
- Campaign events (started, paused, completed)
- Call events (started, ended, failed)
- Alert events (triggered, acknowledged, resolved)
- Report events (generated, expired)

---

**For interactive API testing and detailed schema documentation, visit:**
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

**Last Updated:** November 11, 2025
**API Version:** 2.0.0
