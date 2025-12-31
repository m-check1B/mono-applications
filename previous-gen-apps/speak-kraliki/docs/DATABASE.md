# Database Documentation

## Overview

Speak by Kraliki uses PostgreSQL 17+ with SQLAlchemy 2.0 async ORM.

## Schema

```
┌─────────────────────────────────────────────────────────────────┐
│                         COMPANIES                                │
│  id, name, slug, plan, stripe_*, is_active, settings            │
└─────────────────────────────────────────────────────────────────┘
           │
           │ 1:N
           ▼
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│      USERS        │    │   DEPARTMENTS     │    │    EMPLOYEES      │
│  HR/CEO accounts  │    │  Org structure    │    │  Survey targets   │
│  email, password  │    │  parent_id (tree) │    │  magic_link_token │
└───────────────────┘    └───────────────────┘    └───────────────────┘
                                  │                        │
                                  │                        │
                                  ▼                        ▼
                         ┌───────────────────────────────────────┐
                         │           Speak_SURVEYS                  │
                         │  questions (JSONB), frequency, status  │
                         └───────────────────────────────────────┘
                                         │
                                         │ 1:N
                                         ▼
                         ┌───────────────────────────────────────┐
                         │        Speak_CONVERSATIONS               │
                         │  transcript (JSONB), sentiment, topics │
                         └───────────────────────────────────────┘
                                         │
                                         │ 1:N
                                         ▼
┌───────────────────────────────────────┐    ┌───────────────────────────────────────┐
│           Speak_ALERTS                   │    │           Speak_ACTIONS                  │
│  type, severity, trigger_keywords      │───▶│  topic, status, public_message        │
│  flight_risk, burnout, toxic_manager   │    │  Action Loop for transparency         │
└───────────────────────────────────────┘    └───────────────────────────────────────┘
```

## Tables

### companies

Multi-tenant root table. All other entities reference this.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(200) | Company display name |
| slug | VARCHAR(100) | URL-safe identifier (unique) |
| plan | VARCHAR(50) | starter, growth, enterprise |
| stripe_customer_id | VARCHAR(100) | Stripe customer ID |
| stripe_subscription_id | VARCHAR(100) | Stripe subscription ID |
| is_active | BOOLEAN | Soft delete flag |
| settings | TEXT | JSON settings blob |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### users

HR and executive users who manage surveys.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | FK to companies |
| email | VARCHAR(255) | Login email (unique) |
| password_hash | VARCHAR(255) | bcrypt hash |
| first_name | VARCHAR(100) | First name |
| last_name | VARCHAR(100) | Last name |
| role | VARCHAR(50) | owner, manager |
| is_active | BOOLEAN | Account status |
| last_login | TIMESTAMP | Last login time |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Indexes:** `company_id`, `email`

### departments

Organizational structure with hierarchy support.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | FK to companies |
| name | VARCHAR(200) | Department name |
| parent_id | UUID | FK to departments (self-ref) |
| is_active | BOOLEAN | Active status |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Indexes:** `company_id`

### employees

Employee records targeted by surveys.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | FK to companies |
| department_id | UUID | FK to departments |
| email | VARCHAR(255) | Employee email |
| first_name | VARCHAR(100) | First name |
| last_name | VARCHAR(100) | Last name |
| employee_id | VARCHAR(100) | Internal employee ID |
| hire_date | DATE | Employment start |
| is_active | BOOLEAN | Employment status |
| magic_link_token | VARCHAR(100) | Survey access token |
| magic_link_expires | TIMESTAMP | Token expiry |
| speak_opted_out | BOOLEAN | Survey opt-out |
| speak_last_survey | TIMESTAMP | Last survey date |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Indexes:** `company_id`, `magic_link_token`

### speak_surveys

Survey definitions with questions.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | FK to companies |
| name | VARCHAR(200) | Survey name |
| description | TEXT | Survey description |
| status | VARCHAR(20) | draft, active, paused, completed |
| frequency | VARCHAR(50) | weekly, monthly, quarterly |
| questions | JSONB | Question definitions |
| custom_system_prompt | TEXT | AI prompt customization |
| starts_at | TIMESTAMP | Survey start date |
| ends_at | TIMESTAMP | Survey end date |
| target_departments | JSONB | Department UUIDs to include |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Questions JSONB structure:**
```json
[
  {
    "id": 1,
    "question": "How are you doing?",
    "follow_up_count": 2
  }
]
```

**Indexes:** `company_id`

### speak_conversations

Individual employee survey conversations.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | FK to companies |
| survey_id | UUID | FK to speak_surveys |
| employee_id | UUID | FK to employees |
| status | VARCHAR(20) | pending, invited, in_progress, completed, skipped |
| invited_at | TIMESTAMP | Invitation sent |
| started_at | TIMESTAMP | Conversation started |
| completed_at | TIMESTAMP | Conversation finished |
| duration_seconds | INTEGER | Time spent |
| transcript | JSONB | Full conversation |
| transcript_reviewed_by_employee | BOOLEAN | Employee reviewed |
| redacted_sections | JSONB | Redacted message indices |
| audio_url | VARCHAR(500) | Audio recording URL |
| fallback_to_text | BOOLEAN | Switched to text mode |
| fallback_reason | VARCHAR(100) | Why fallback occurred |
| sentiment_score | NUMERIC(3,2) | -1.00 to 1.00 |
| topics | JSONB | Extracted topics |
| flags | JSONB | Detected flags |
| summary | TEXT | AI-generated summary |
| anonymous_id | VARCHAR(50) | EMP-XXXXXXXX format |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Transcript JSONB structure:**
```json
[
  {"role": "ai", "content": "Hello!", "timestamp": "2024-01-01T00:00:00Z"},
  {"role": "user", "content": "Hi", "timestamp": "2024-01-01T00:00:05Z"}
]
```

**Indexes:** `company_id`, `survey_id`, `employee_id`

### speak_alerts

Automated alerts from conversation analysis.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | FK to companies |
| conversation_id | UUID | FK to speak_conversations |
| type | VARCHAR(50) | flight_risk, burnout, toxic_manager, safety, legal |
| severity | VARCHAR(20) | low, medium, high |
| department_id | UUID | FK to departments |
| description | TEXT | Alert description |
| trigger_keywords | VARCHAR(500) | Keywords that triggered |
| is_read | BOOLEAN | Read status |
| read_at | TIMESTAMP | When read |
| read_by | UUID | FK to users |
| created_at | TIMESTAMP | Creation timestamp |

**Indexes:** `company_id`, `type`

### speak_actions

Action Loop items for transparency.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | FK to companies |
| department_id | UUID | FK to departments |
| created_from_alert_id | UUID | FK to speak_alerts |
| topic | VARCHAR(200) | Action topic |
| status | VARCHAR(20) | new, heard, in_progress, resolved |
| internal_notes | TEXT | Private notes |
| public_message | TEXT | Visible to employees |
| assigned_to | UUID | FK to users |
| resolved_at | TIMESTAMP | Resolution time |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Indexes:** `company_id`, `status`

## Migrations

### Running Migrations

```bash
cd backend

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history
```

### Creating New Migrations

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "add_new_field"

# Create empty migration
alembic revision -m "custom_migration"
```

### Migration Best Practices

1. Always review auto-generated migrations
2. Test migrations on a copy of production data
3. Include both `upgrade()` and `downgrade()` functions
4. Use transactions for data migrations

## Queries

### Common Query Patterns

**Get surveys with stats:**
```python
from sqlalchemy import select, func

stmt = (
    select(
        Survey,
        func.count(Conversation.id).label('conversation_count'),
        func.avg(Conversation.sentiment_score).label('avg_sentiment')
    )
    .outerjoin(Conversation)
    .where(Survey.company_id == company_id)
    .group_by(Survey.id)
)
```

**Get unread alerts:**
```python
stmt = (
    select(Alert)
    .where(Alert.company_id == company_id)
    .where(Alert.is_read == False)
    .order_by(Alert.created_at.desc())
)
```

**Department hierarchy:**
```python
# Get all child departments recursively
with_recursive = """
WITH RECURSIVE dept_tree AS (
    SELECT id, name, parent_id, 0 AS level
    FROM departments
    WHERE id = :dept_id

    UNION ALL

    SELECT d.id, d.name, d.parent_id, dt.level + 1
    FROM departments d
    JOIN dept_tree dt ON d.parent_id = dt.id
)
SELECT * FROM dept_tree;
"""
```

## Performance

### Indexes

Critical indexes are defined in migrations:

- `ix_users_email` - Login lookups
- `ix_employees_magic_link_token` - Survey access
- `ix_speak_conversations_survey_id` - Survey stats
- `ix_speak_alerts_type` - Alert filtering

### Connection Pooling

```python
# database.py
engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)
```

### Query Optimization

- Use `select()` with specific columns instead of loading full models
- Use `joinedload()` for related data needed immediately
- Use `selectinload()` for collections
- Add `LIMIT` to list queries

## Backup & Recovery

### Daily Backup Script

```bash
#!/bin/bash
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U speak speak | gzip > $BACKUP_DIR/speak_$DATE.sql.gz

# Keep last 7 days
find $BACKUP_DIR -name "speak_*.sql.gz" -mtime +7 -delete
```

### Point-in-Time Recovery

Enable WAL archiving in `postgresql.conf`:

```
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/%f'
```

### Restore

```bash
# Stop application
docker compose stop backend

# Restore from backup
gunzip -c backup.sql.gz | psql -U speak speak

# Restart
docker compose start backend
```

## Data Retention

| Data Type | Retention | Notes |
|-----------|-----------|-------|
| Transcripts | 2 years | Anonymized after analysis |
| Alerts | 1 year | Archive to cold storage |
| Actions | Indefinite | Business records |
| Employees | Until deletion request | GDPR compliant |

### GDPR Deletion

```python
async def delete_employee_data(employee_id: UUID, db: AsyncSession):
    # Delete conversations
    await db.execute(
        delete(Conversation).where(Conversation.employee_id == employee_id)
    )

    # Delete employee record
    await db.execute(
        delete(Employee).where(Employee.id == employee_id)
    )

    await db.commit()
```
