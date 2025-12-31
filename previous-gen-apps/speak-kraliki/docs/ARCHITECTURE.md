# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    SvelteKit 5                           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │   │
│  │  │  Routes  │  │  Stores  │  │     API Client       │   │   │
│  │  │ /login   │  │  auth    │  │  REST + WebSocket    │   │   │
│  │  │ /dash    │  │  voice   │  │                      │   │   │
│  │  │ /v/:tok  │  │          │  │                      │   │   │
│  │  └──────────┘  └──────────┘  └──────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS / WSS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    FastAPI                               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │   │
│  │  │ Routers  │  │ Services │  │        Core          │   │   │
│  │  │ auth     │  │ ai_conv  │  │  config, auth, db    │   │   │
│  │  │ surveys  │  │ analysis │  │                      │   │   │
│  │  │ voice    │  │ email    │  │                      │   │   │
│  │  │ actions  │  │          │  │                      │   │   │
│  │  └──────────┘  └──────────┘  └──────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ SQL
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       POSTGRESQL                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │companies │  │employees │  │ surveys  │  │  alerts  │        │
│  │  users   │  │  depts   │  │  convos  │  │ actions  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Multi-Tenant Architecture

Every entity includes `company_id` for tenant isolation:

```python
class Conversation(Base):
    company_id: Mapped[uuid.UUID]  # Tenant isolation
    survey_id: Mapped[uuid.UUID]
    employee_id: Mapped[uuid.UUID]
```

### 2. Voice Pipeline

```
Employee → WebSocket → STT (Gemini) → AI Response → TTS → Employee
                ↓
         Transcript Storage
                ↓
         Sentiment Analysis
                ↓
         Alert Generation
```

### 3. Trust Layer

Anonymity and trust features:

1. **Consent Screen**: Employee sees privacy guarantees before starting
2. **Magic Links**: No login required for employees
3. **Anonymous IDs**: `EMP-XXXXXXXX` instead of real names
4. **Transcript Review**: Employees can redact parts before submission
5. **Data Deletion**: GDPR-compliant full data deletion

### 4. Action Loop

Feedback cycle from employees to leadership:

```
Alert Detected → CEO Reviews → Creates Action → Public Update → Employees See
      ↑                                                              │
      └──────────────── Next Survey Cycle ───────────────────────────┘
```

## Data Flow

### Survey Launch Flow

```
1. HR creates survey with questions
2. HR launches survey
3. System generates magic links per employee
4. Emails sent with personalized links
5. Conversations created with status="invited"
```

### Conversation Flow

```
1. Employee clicks magic link
2. Consent screen shown (Trust Layer)
3. WebSocket connection established
4. AI greeting + first question
5. Employee responds (voice/text)
6. AI asks follow-ups or next question
7. Repeat until complete
8. Analysis runs (sentiment, topics, flags)
9. Alerts generated if needed
10. Employee can review transcript
```

### Analysis Flow

```
Transcript → Sentiment Score → Topic Extraction → Flag Detection → Alert Creation
                 │                    │                  │
                 ▼                    ▼                  ▼
           -1.0 to 1.0         [workload,        [flight_risk,
                               management,        burnout,
                               team, ...]         toxic_manager]
```

## Security Model

### Authentication

| Actor | Method | Token Type |
|-------|--------|------------|
| HR/CEO | Email + Password | JWT (15min access, 7d refresh) |
| Employee | Magic Link | URL Token (7d expiry) |

### Authorization

| Role | Permissions |
|------|-------------|
| `owner` | All company data |
| `manager` | Filtered by department |
| `employee` | Own data only |

### Data Protection

- Passwords: bcrypt hashed
- JWTs: HS256 signed (Ed25519 ready)
- Employee responses: Anonymized
- Transcripts: Redactable
- All data: Soft deletable

## External Services

| Service | Purpose | Fallback |
|---------|---------|----------|
| Gemini 2.5 Flash | AI conversation | Mock responses |
| Resend | Email delivery | Console logging |
| Stripe | Payments | Disabled |
