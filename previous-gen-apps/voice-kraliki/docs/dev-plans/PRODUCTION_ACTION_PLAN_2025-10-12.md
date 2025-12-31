# Production Action Plan - Operator Demo 2026
## From Audit to Production: Actionable Development Tasks

**Date**: October 12, 2025
**Based On**: PRODUCTION_READINESS_AUDIT_2025-10-12.md
**Timeline**: 4 weeks to beta, 12 weeks to enterprise
**Priority**: CRITICAL PATH

---

## Executive Summary

This action plan translates the production readiness audit into **concrete, actionable tasks** for getting operator-demo-2026 into production. Tasks are prioritized by blocker severity and organized into 4 weekly sprints.

**Critical Path**: Complete Week 1-2 tasks BEFORE any production traffic.

---

## Week 1: Critical Security & Monitoring (BLOCKERS)

**Goal**: Eliminate critical vulnerabilities and enable production observability
**Duration**: 5 business days
**Required**: MUST complete before production launch

### Day 1-2: Rate Limiting & Security Hardening

#### Task 1.1: Implement Rate Limiting ⚠️ CRITICAL
**Priority**: P0 (Blocker)
**Effort**: 1.5 days
**Owner**: Backend Dev

**Implementation:**
```bash
# Install dependencies
pip install slowapi redis

# Files to create/modify:
backend/app/middleware/rate_limit.py     # New
backend/app/config/redis.py              # New
backend/main.py                           # Modify
backend/requirements.txt                  # Modify
docker-compose.yml                        # Add Redis service
```

**Specifications:**
- Global rate limit: 1000 req/hour per IP
- API endpoints: 100 req/min per user
- Login endpoint: 5 attempts per 15 min
- Use Redis for distributed counting
- Return 429 with Retry-After header

**Acceptance Criteria:**
- [ ] Redis container running
- [ ] Rate limits enforced on all routes
- [ ] 429 responses with correct headers
- [ ] Redis connection fallback (in-memory)
- [ ] Rate limit tests passing

**Files to modify:**
```python
# backend/app/middleware/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://redis:6379"
)

# Apply to app in main.py
app.state.limiter = limiter
```

#### Task 1.2: Fix CORS Configuration ⚠️ HIGH
**Priority**: P0 (Blocker)
**Effort**: 0.5 days
**Owner**: Backend Dev

**Current Issue:**
```python
# backend/main.py (UNSAFE)
allow_origins=["*"]  # ⚠️ Accepts any origin
```

**Fix:**
```python
# backend/main.py
import os
from typing import List

ALLOWED_ORIGINS: List[str] = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
    os.getenv("PRODUCTION_URL", "https://yourdomain.com"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)
```

**Acceptance Criteria:**
- [ ] CORS restricted to specific domains
- [ ] Environment-based origin configuration
- [ ] Pre-flight requests working
- [ ] Credentials properly handled
- [ ] CORS tests passing

#### Task 1.3: Add Security Headers ⚠️ MEDIUM
**Priority**: P1
**Effort**: 0.5 days
**Owner**: Backend Dev

**Implementation:**
```python
# backend/app/middleware/security_headers.py
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
```

**Acceptance Criteria:**
- [ ] All security headers present in responses
- [ ] CSP policy configured
- [ ] HSTS enabled
- [ ] Security scanner (Mozilla Observatory) passes

### Day 3-4: Monitoring & Observability

#### Task 1.4: Integrate Sentry for Error Tracking ⚠️ CRITICAL
**Priority**: P0 (Blocker)
**Effort**: 1 day
**Owner**: Backend + Frontend Dev

**Backend Setup:**
```bash
pip install sentry-sdk[fastapi]
```

```python
# backend/app/config/sentry.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

def init_sentry():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("ENVIRONMENT", "production"),
        traces_sample_rate=0.1,
        integrations=[FastApiIntegration()],
    )
```

**Frontend Setup:**
```bash
npm install @sentry/sveltekit
```

```typescript
// frontend/src/hooks.client.ts
import * as Sentry from '@sentry/sveltekit';

Sentry.init({
  dsn: import.meta.env.PUBLIC_SENTRY_DSN,
  environment: import.meta.env.MODE,
  tracesSampleRate: 0.1,
});
```

**Acceptance Criteria:**
- [ ] Sentry project created
- [ ] Backend errors tracked
- [ ] Frontend errors tracked
- [ ] User context captured
- [ ] Test error sent successfully
- [ ] Alert rules configured

#### Task 1.5: Add Prometheus Metrics ⚠️ HIGH
**Priority**: P1
**Effort**: 1 day
**Owner**: Backend Dev

**Implementation:**
```bash
pip install prometheus-fastapi-instrumentator
```

```python
# backend/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

**Custom Metrics:**
```python
# backend/app/metrics.py
from prometheus_client import Counter, Histogram

call_duration = Histogram('call_duration_seconds', 'Call duration')
campaign_executions = Counter('campaign_executions_total', 'Campaign runs')
provider_failures = Counter('provider_failures_total', 'Provider errors', ['provider'])
```

**Acceptance Criteria:**
- [ ] /metrics endpoint available
- [ ] Default HTTP metrics tracked
- [ ] Custom business metrics implemented
- [ ] Grafana dashboard created
- [ ] Metrics exportable to monitoring system

### Day 5: Backups & Disaster Recovery

#### Task 1.6: Automated Database Backups ⚠️ CRITICAL
**Priority**: P0 (Blocker)
**Effort**: 1 day
**Owner**: DevOps/Backend

**Implementation:**
```bash
# Create backup script
# scripts/backup-db.sh

#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${TIMESTAMP}.sql"
S3_BUCKET="your-backup-bucket"

# Backup database
pg_dump $DATABASE_URL > /tmp/$BACKUP_FILE

# Compress
gzip /tmp/$BACKUP_FILE

# Upload to S3
aws s3 cp /tmp/${BACKUP_FILE}.gz s3://${S3_BUCKET}/postgres/

# Cleanup local file
rm /tmp/${BACKUP_FILE}.gz

# Keep only last 30 days on S3
aws s3 ls s3://${S3_BUCKET}/postgres/ | \
  while read -r line; do
    createDate=$(echo $line|awk {'print $1" "$2'})
    createDate=$(date -d "$createDate" +%s)
    olderThan=$(date -d "30 days ago" +%s)
    if [[ $createDate -lt $olderThan ]]; then
      fileName=$(echo $line|awk {'print $4'})
      aws s3 rm s3://${S3_BUCKET}/postgres/$fileName
    fi
  done
```

**Cron Setup:**
```bash
# Add to crontab
0 2 * * * /app/scripts/backup-db.sh >> /var/log/backup.log 2>&1
```

**Restore Procedure:**
```bash
# scripts/restore-db.sh
#!/bin/bash
BACKUP_FILE=$1

# Download from S3
aws s3 cp s3://${S3_BUCKET}/postgres/${BACKUP_FILE} /tmp/

# Restore
gunzip /tmp/${BACKUP_FILE}
psql $DATABASE_URL < /tmp/${BACKUP_FILE%.gz}
```

**Acceptance Criteria:**
- [ ] Daily backup cron running
- [ ] Backups stored in S3
- [ ] 30-day retention policy
- [ ] Restore procedure tested successfully
- [ ] Monitoring for backup failures
- [ ] RTO < 1 hour documented
- [ ] RPO < 24 hours documented

#### Task 1.7: Database Migration System ⚠️ HIGH
**Priority**: P1
**Effort**: 1 day
**Owner**: Backend Dev

**Implementation:**
```bash
pip install alembic
alembic init migrations
```

```python
# alembic/env.py
from app.models import Base
target_metadata = Base.metadata

# Generate initial migration from existing schema
alembic revision --autogenerate -m "initial schema"

# Apply migrations
alembic upgrade head
```

**Migration Template:**
```python
# migrations/versions/001_add_user_preferences.py
def upgrade():
    op.add_column('users', sa.Column('preferences', sa.JSON(), nullable=True))
    op.create_index('ix_users_preferences', 'users', ['preferences'])

def downgrade():
    op.drop_index('ix_users_preferences')
    op.drop_column('users', 'preferences')
```

**Acceptance Criteria:**
- [ ] Alembic initialized
- [ ] Initial migration from existing schema
- [ ] Migration applies successfully
- [ ] Rollback tested
- [ ] CI/CD integration for auto-migrations
- [ ] Migration documentation

---

## Week 2: Infrastructure & Testing

**Goal**: Production infrastructure and critical test coverage
**Duration**: 5 business days

### Day 6-7: CI/CD Pipeline

#### Task 2.1: GitHub Actions Workflow ⚠️ HIGH
**Priority**: P1
**Effort**: 1.5 days
**Owner**: DevOps

**Implementation:**
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-report=term
        env:
          DATABASE_URL: postgresql://postgres:test@localhost/test_db
          REDIS_URL: redis://localhost:6379

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Type check
        run: |
          cd frontend
          npm run check

      - name: Build
        run: |
          cd frontend
          npm run build

  build-and-push:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: yourorg/operator-demo-backend:${{ github.sha }},yourorg/operator-demo-backend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: yourorg/operator-demo-frontend:${{ github.sha }},yourorg/operator-demo-frontend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Deploy to production
        run: |
          # SSH to server and update containers
          ssh ${{ secrets.DEPLOY_USER }}@${{ secrets.DEPLOY_HOST }} << 'EOF'
            cd /app/operator-demo-2026
            docker-compose pull
            docker-compose up -d
          EOF
```

**Acceptance Criteria:**
- [ ] CI runs on every PR
- [ ] Tests must pass before merge
- [ ] Docker images built automatically
- [ ] Auto-deploy to staging on develop
- [ ] Manual approval for production
- [ ] Slack/email notifications
- [ ] Build time < 10 minutes

### Day 8-9: Caching & Performance

#### Task 2.2: Redis Caching Layer ⚠️ HIGH
**Priority**: P1
**Effort**: 1.5 days
**Owner**: Backend Dev

**Implementation:**
```python
# backend/app/cache/redis_client.py
from redis.asyncio import Redis
import json
from typing import Optional, Any
from datetime import timedelta

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any, ttl: int = 300):
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def clear_pattern(self, pattern: str):
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

# Usage in routes
@router.get("/campaigns")
async def get_campaigns(cache: CacheManager = Depends(get_cache)):
    cached = await cache.get("campaigns:all")
    if cached:
        return cached

    campaigns = await fetch_campaigns()
    await cache.set("campaigns:all", campaigns, ttl=3600)
    return campaigns
```

**Cache Strategy:**
- Campaign scripts: 1 hour TTL
- Provider settings: 15 min TTL
- Session data: 24 hour TTL
- User preferences: 30 min TTL
- API responses: 5 min TTL

**Acceptance Criteria:**
- [ ] Redis deployed in docker-compose
- [ ] Cache manager implemented
- [ ] Campaign scripts cached
- [ ] Provider settings cached
- [ ] Cache invalidation working
- [ ] 50%+ reduction in DB queries
- [ ] Performance tests passing

#### Task 2.3: Load Testing with Locust ⚠️ CRITICAL
**Priority**: P0 (Blocker)
**Effort**: 1 day
**Owner**: Backend Dev + QA

**Implementation:**
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between
import random

class OperatorDemoUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login
        response = self.client.post("/auth/login", json={
            "email": f"user{random.randint(1, 100)}@example.com",
            "password": "test123"
        })
        self.token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def get_campaigns(self):
        self.client.get("/campaigns", headers=self.headers)

    @task(2)
    def get_companies(self):
        self.client.get("/api/v1/companies", headers=self.headers)

    @task(1)
    def create_session(self):
        self.client.post("/api/v1/sessions",
            headers=self.headers,
            json={
                "provider_type": "twilio",
                "telephony_provider": "twilio"
            }
        )

    @task(1)
    def health_check(self):
        self.client.get("/health")
```

**Test Scenarios:**
```bash
# Baseline: 10 users, 1 min
locust -f tests/load/locustfile.py --users 10 --spawn-rate 2 --run-time 1m --headless

# Target: 100 users, 5 min
locust -f tests/load/locustfile.py --users 100 --spawn-rate 10 --run-time 5m --headless

# Stress: 500 users, 10 min
locust -f tests/load/locustfile.py --users 500 --spawn-rate 50 --run-time 10m --headless
```

**Performance Targets:**
- p50: < 100ms
- p95: < 200ms
- p99: < 500ms
- Throughput: > 100 req/sec
- Error rate: < 1%

**Acceptance Criteria:**
- [ ] Locust tests created
- [ ] 100 concurrent users supported
- [ ] p95 response time < 200ms
- [ ] Zero errors at target load
- [ ] Bottlenecks identified and documented
- [ ] Performance report generated

### Day 10: Testing & Documentation

#### Task 2.4: Increase Test Coverage to 80% ⚠️ HIGH
**Priority**: P1
**Effort**: 1 day
**Owner**: Backend Dev

**Current State:**
- 15 pytest tests
- ~40% estimated coverage
- No service layer tests
- No provider tests

**Test Plan:**
```python
# tests/test_services/test_campaign_service.py
@pytest.mark.asyncio
async def test_get_campaign_by_id():
    campaign = await campaign_service.get_by_id(1)
    assert campaign.id == 1
    assert campaign.language == "en"

# tests/test_services/test_telephony_manager.py
@pytest.mark.asyncio
async def test_provider_failover():
    # Test Twilio -> Telnyx failover
    with patch('app.providers.twilio.make_call', side_effect=Exception):
        result = await telephony_manager.initiate_call(...)
        assert result.provider == "telnyx"

# tests/test_api/test_companies.py
async def test_create_company_unauthorized(client):
    response = await client.post("/api/v1/companies", json={...})
    assert response.status_code == 401

# tests/test_auth/test_jwt.py
def test_ed25519_signature_verification():
    token = generate_token(user_id, private_key)
    assert verify_token(token, public_key)
```

**Coverage Targets:**
- Auth module: 90%+
- Services: 80%+
- API routes: 85%+
- Providers: 75%+
- Models: 95%+

**Acceptance Criteria:**
- [ ] 50+ unit tests added
- [ ] Overall coverage > 80%
- [ ] All critical paths covered
- [ ] Pytest-cov report generated
- [ ] Coverage badge in README
- [ ] No critical uncovered code

---

## Week 3: Compliance & Scaling

**Goal**: GDPR compliance and horizontal scaling capability
**Duration**: 5 business days

### Day 11-12: GDPR Implementation

#### Task 3.1: Data Export API ⚠️ HIGH
**Priority**: P1 (Compliance)
**Effort**: 1 day
**Owner**: Backend Dev

**Implementation:**
```python
# backend/app/api/gdpr.py
from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/gdpr", tags=["GDPR"])

@router.get("/export")
async def export_user_data(user: User = Depends(get_current_user)):
    """Export all user data in machine-readable format"""
    data = {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "created_at": user.created_at.isoformat(),
        },
        "sessions": await get_user_sessions(user.id),
        "calls": await get_user_calls(user.id),
        "settings": await get_user_settings(user.id),
        "dispositions": await get_user_dispositions(user.id),
    }

    # Log export request for audit
    await log_gdpr_action(user.id, "data_export")

    return data

@router.delete("/delete-account")
async def delete_account(
    user: User = Depends(get_current_user),
    confirmation: str = Body(...)
):
    """Permanently delete user account and all associated data"""
    if confirmation != user.email:
        raise HTTPException(400, "Confirmation email doesn't match")

    # Cascade delete
    await delete_user_data(user.id)

    # Log deletion for compliance
    await log_gdpr_action(user.id, "account_deleted", retain=True)

    return {"message": "Account scheduled for deletion"}

@router.get("/privacy-settings")
async def get_privacy_settings(user: User = Depends(get_current_user)):
    return await get_user_privacy_preferences(user.id)

@router.put("/privacy-settings")
async def update_privacy_settings(
    settings: PrivacySettings,
    user: User = Depends(get_current_user)
):
    await update_user_privacy(user.id, settings)
    return {"message": "Privacy settings updated"}
```

**Acceptance Criteria:**
- [ ] Data export API working
- [ ] Account deletion API working
- [ ] Privacy settings manageable
- [ ] Audit log for GDPR actions
- [ ] 30-day grace period for deletion
- [ ] Email notifications sent
- [ ] GDPR compliance checklist 80% complete

#### Task 3.2: Data Retention Policies ⚠️ MEDIUM
**Priority**: P2
**Effort**: 1 day
**Owner**: Backend Dev

**Implementation:**
```python
# backend/app/tasks/data_retention.py
from datetime import datetime, timedelta
from app.db.session import get_db

async def cleanup_old_data():
    """Run daily to enforce retention policies"""

    # Delete sessions older than 90 days
    cutoff_sessions = datetime.utcnow() - timedelta(days=90)
    await db.execute(
        "DELETE FROM sessions WHERE ended_at < :cutoff",
        {"cutoff": cutoff_sessions}
    )

    # Archive calls older than 1 year to cold storage
    cutoff_calls = datetime.utcnow() - timedelta(days=365)
    old_calls = await db.fetch_all(
        "SELECT * FROM telephony_calls WHERE ended_at < :cutoff",
        {"cutoff": cutoff_calls}
    )
    await archive_to_s3(old_calls, "calls-archive")
    await db.execute(
        "DELETE FROM telephony_calls WHERE ended_at < :cutoff",
        {"cutoff": cutoff_calls}
    )

    # Anonymize call dispositions older than 2 years
    cutoff_anon = datetime.utcnow() - timedelta(days=730)
    await db.execute("""
        UPDATE call_dispositions
        SET notes = '[ANONYMIZED]',
            custom_fields = '{}'::jsonb
        WHERE created_at < :cutoff
    """, {"cutoff": cutoff_anon})

# Add to crontab
# 0 3 * * * python -m app.tasks.data_retention
```

**Acceptance Criteria:**
- [ ] Retention policies documented
- [ ] Automated cleanup job
- [ ] Old data archived to S3
- [ ] PII anonymization working
- [ ] Compliance audit trail

### Day 13-14: Horizontal Scaling

#### Task 3.3: Load Balancer Setup ⚠️ HIGH
**Priority**: P1
**Effort**: 1.5 days
**Owner**: DevOps

**Nginx Configuration:**
```nginx
# nginx/load-balancer.conf
upstream backend {
    least_conn;
    server backend1:8000 max_fails=3 fail_timeout=30s;
    server backend2:8000 max_fails=3 fail_timeout=30s;
    server backend3:8000 max_fails=3 fail_timeout=30s;
}

upstream frontend {
    server frontend1:3000;
    server frontend2:3000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;

    # API requests
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Frontend requests
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://backend;
    }
}
```

**Docker Compose with Scaling:**
```yaml
# docker-compose.prod.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx:/etc/nginx/conf.d
      - ./certs:/etc/nginx/certs
    depends_on:
      - backend
      - frontend

  backend:
    image: yourorg/operator-demo-backend:latest
    deploy:
      replicas: 3
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=${DATABASE_URL}

  frontend:
    image: yourorg/operator-demo-frontend:latest
    deploy:
      replicas: 2

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data

  postgres:
    image: postgres:15
    volumes:
      - postgres-data:/var/lib/postgresql/data
```

**Acceptance Criteria:**
- [ ] Nginx load balancer deployed
- [ ] 3 backend replicas running
- [ ] 2 frontend replicas running
- [ ] Health checks working
- [ ] SSL/TLS configured
- [ ] Sticky sessions if needed
- [ ] Load testing with multiple instances

#### Task 3.4: Database Read Replicas ⚠️ MEDIUM
**Priority**: P2
**Effort**: 1 day
**Owner**: DevOps + Backend

**PostgreSQL Replication:**
```yaml
# docker-compose.prod.yml
services:
  postgres-primary:
    image: postgres:15
    environment:
      - POSTGRES_REPLICATION_MODE=master
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=${REPLICATION_PASSWORD}
    volumes:
      - pg-primary:/var/lib/postgresql/data

  postgres-replica:
    image: postgres:15
    environment:
      - POSTGRES_REPLICATION_MODE=slave
      - POSTGRES_MASTER_HOST=postgres-primary
      - POSTGRES_MASTER_PORT=5432
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=${REPLICATION_PASSWORD}
    volumes:
      - pg-replica:/var/lib/postgresql/data
    depends_on:
      - postgres-primary
```

**Application Config:**
```python
# backend/app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine

# Write operations
write_engine = create_async_engine(
    os.getenv("DATABASE_WRITE_URL"),
    pool_size=20,
    max_overflow=10
)

# Read operations
read_engine = create_async_engine(
    os.getenv("DATABASE_READ_URL"),
    pool_size=30,
    max_overflow=20
)

class DatabaseRouter:
    def get_engine(self, operation: str):
        if operation in ["SELECT", "COUNT"]:
            return read_engine
        return write_engine
```

**Acceptance Criteria:**
- [ ] Primary-replica replication working
- [ ] Read queries routed to replica
- [ ] Write queries to primary only
- [ ] Replication lag < 1 second
- [ ] Failover tested
- [ ] Connection pooling optimized

### Day 15: CDN & Asset Optimization

#### Task 3.5: CloudFront CDN Setup ⚠️ MEDIUM
**Priority**: P2
**Effort**: 0.5 days
**Owner**: DevOps

**CloudFront Configuration:**
```typescript
// infrastructure/cdn-stack.ts (if using CDK)
const distribution = new cloudfront.Distribution(this, 'CDN', {
  defaultBehavior: {
    origin: new origins.S3Origin(bucket),
    viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
    cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
    compress: true,
  },
  additionalBehaviors: {
    '/api/*': {
      origin: new origins.LoadBalancerV2Origin(alb),
      cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
    }
  },
  certificate: cert,
  domainNames: ['yourdomain.com'],
});
```

**Asset Optimization:**
```javascript
// frontend/vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['svelte', '@tanstack/svelte-query'],
          'ui': ['lucide-svelte'],
        }
      }
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
      }
    }
  },
  plugins: [
    imageOptimizer(),
    compression({ algorithm: 'brotli' }),
  ]
});
```

**Acceptance Criteria:**
- [ ] CDN distribution created
- [ ] Static assets served from CDN
- [ ] Brotli compression enabled
- [ ] Cache headers optimized
- [ ] Images optimized (WebP)
- [ ] Load time < 1.5s (LCP)

---

## Week 4: Enterprise Features & Final Prep

**Goal**: Enterprise-ready features and production launch prep
**Duration**: 5 business days

### Day 16-17: Security Audit

#### Task 4.1: OWASP ZAP Security Scan ⚠️ HIGH
**Priority**: P1
**Effort**: 1 day
**Owner**: Security/QA

**Implementation:**
```bash
# Run OWASP ZAP scan
docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable \
  zap-full-scan.py -t https://staging.yourdomain.com \
  -r zap-report.html

# Review findings
cat zap-report.html | grep -A 5 "High\|Medium"
```

**Common Issues to Fix:**
- SQL injection vulnerabilities
- XSS attack vectors
- CSRF token validation
- Insecure dependencies
- Information disclosure

**Acceptance Criteria:**
- [ ] OWASP ZAP scan completed
- [ ] All HIGH severity issues fixed
- [ ] MEDIUM issues documented/mitigated
- [ ] Security report generated
- [ ] Penetration test scheduled

#### Task 4.2: Dependency Security Audit ⚠️ MEDIUM
**Priority**: P2
**Effort**: 0.5 days
**Owner**: Backend + Frontend Dev

**Backend:**
```bash
# Install safety
pip install safety

# Scan dependencies
safety check --full-report

# Auto-update vulnerabilities
pip-audit --fix
```

**Frontend:**
```bash
# Scan npm packages
npm audit

# Fix automatically
npm audit fix

# For unfixable issues
npm audit fix --force
```

**Acceptance Criteria:**
- [ ] No critical vulnerabilities
- [ ] High severity patched
- [ ] Snyk monitoring enabled
- [ ] Dependabot alerts configured
- [ ] Weekly security scans scheduled

### Day 18-19: Multi-Tenancy Foundation

#### Task 4.3: Organization Isolation ⚠️ HIGH
**Priority**: P1 (Enterprise blocker)
**Effort**: 1.5 days
**Owner**: Backend Dev

**Database Changes:**
```sql
-- Add organization table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Update users table
ALTER TABLE users ADD COLUMN organization_id UUID REFERENCES organizations(id);
ALTER TABLE users ADD CONSTRAINT users_org_fk FOREIGN KEY (organization_id) REFERENCES organizations(id);

-- Add RLS policies
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
CREATE POLICY companies_isolation ON companies
  USING (organization_id = current_setting('app.current_org_id')::UUID);

ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY sessions_isolation ON sessions
  USING (user_id IN (
    SELECT id FROM users WHERE organization_id = current_setting('app.current_org_id')::UUID
  ));
```

**Application Changes:**
```python
# backend/app/middleware/tenant.py
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    user = request.state.user
    if user and user.organization_id:
        # Set organization context
        await db.execute(
            "SET LOCAL app.current_org_id = :org_id",
            {"org_id": str(user.organization_id)}
        )
    response = await call_next(request)
    return response

# Resource quotas per organization
class OrganizationQuota:
    max_calls_per_month: int = 10000
    max_concurrent_calls: int = 10
    max_users: int = 25
    max_campaigns: int = 50
```

**Acceptance Criteria:**
- [ ] Organizations table created
- [ ] Row-level security enabled
- [ ] All queries organization-scoped
- [ ] Resource quotas enforced
- [ ] Cross-org data leak tested (none)
- [ ] Organization admin dashboard

### Day 20: Final Production Prep

#### Task 4.4: Production Runbooks ⚠️ HIGH
**Priority**: P1
**Effort**: 1 day
**Owner**: DevOps + Backend

**Create Runbooks:**

**1. Deployment Runbook** (`docs/runbooks/deployment.md`)
```markdown
# Production Deployment Runbook

## Pre-deployment Checklist
- [ ] All tests passing in CI
- [ ] Staging tested successfully
- [ ] Database migrations ready
- [ ] Backup completed
- [ ] Rollback plan documented

## Deployment Steps
1. Enable maintenance mode
2. Run database migrations
3. Deploy new Docker images
4. Health check verification
5. Smoke tests
6. Disable maintenance mode
7. Monitor for 30 minutes

## Rollback Procedure
1. Revert Docker images
2. Rollback database migrations
3. Clear caches
4. Verify health checks
```

**2. Incident Response** (`docs/runbooks/incident-response.md`)
```markdown
# Incident Response Runbook

## Severity Levels
- P0: Complete outage
- P1: Major feature broken
- P2: Minor feature degraded
- P3: Cosmetic issue

## On-Call Procedure
1. Acknowledge alert in PagerDuty
2. Check monitoring dashboards
3. Review recent deployments
4. Check error logs in Sentry
5. Update status page

## Common Issues
### Database connection errors
- Check connection pool
- Verify credentials
- Check RDS status

### High response times
- Check Redis cache
- Review slow queries
- Check CPU/memory
```

**3. Backup & Restore** (`docs/runbooks/backup-restore.md`)

**Acceptance Criteria:**
- [ ] 5+ runbooks created
- [ ] Deployment procedure tested
- [ ] Incident response trained
- [ ] Backup restore verified
- [ ] On-call rotation configured

#### Task 4.5: Production Launch Checklist ⚠️ CRITICAL
**Priority**: P0
**Effort**: 0.5 days
**Owner**: Tech Lead

**Final Verification:**
```markdown
# Production Launch Checklist

## Infrastructure
- [ ] All services deployed and healthy
- [ ] Load balancer configured
- [ ] SSL certificates valid
- [ ] DNS configured correctly
- [ ] CDN serving assets
- [ ] Backup job running
- [ ] Monitoring dashboards live

## Security
- [ ] Rate limiting active
- [ ] CORS restricted
- [ ] Security headers present
- [ ] Secrets in vault
- [ ] OWASP scan passed
- [ ] Pen test completed

## Compliance
- [ ] GDPR features live
- [ ] Privacy policy published
- [ ] Terms of service updated
- [ ] Cookie consent implemented
- [ ] Data retention configured

## Monitoring
- [ ] Sentry capturing errors
- [ ] Prometheus metrics flowing
- [ ] Grafana dashboards created
- [ ] Alerts configured
- [ ] PagerDuty integration working
- [ ] Status page setup

## Performance
- [ ] Load testing passed (100+ users)
- [ ] p95 response time < 200ms
- [ ] CDN caching working
- [ ] Database optimized
- [ ] Redis caching active

## Operations
- [ ] Runbooks documented
- [ ] On-call rotation setup
- [ ] Incident response tested
- [ ] Backup restore tested
- [ ] Rollback procedure verified

## Business
- [ ] Beta customers onboarded
- [ ] Support team trained
- [ ] Documentation complete
- [ ] Pricing configured
- [ ] Analytics tracking live
```

---

## Summary & Timeline

### Critical Path (Must Complete)

**Week 1: Security & Monitoring (5 days)**
- Rate limiting + Redis
- CORS restrictions
- Security headers
- Sentry integration
- Prometheus metrics
- Database backups
- Alembic migrations

**Week 2: Infrastructure (5 days)**
- CI/CD pipeline
- Redis caching
- Load testing (Locust)
- Test coverage 80%+

**Week 3: Compliance (5 days)**
- GDPR features
- Data retention
- Load balancer
- Database replication
- CDN setup

**Week 4: Enterprise (5 days)**
- Security audit
- Multi-tenancy
- Runbooks
- Launch checklist

### Resource Requirements

**Development Team:**
- 1 Backend Developer (full-time, 4 weeks)
- 1 Frontend Developer (part-time, 2 weeks)
- 1 DevOps Engineer (full-time, 4 weeks)
- 1 QA Engineer (part-time, 2 weeks)

**Infrastructure:**
- Staging environment: Week 1
- Production environment: Week 3
- Monitoring tools: Week 1
- CDN: Week 3

**Budget:**
- Development: $40K-65K
- Infrastructure: $5K-10K
- Security audit: $10K-20K
- Total: ~$60K-95K

### Success Criteria

**Week 1 Complete:**
- [ ] No critical security vulnerabilities
- [ ] Production monitoring operational
- [ ] Automated backups running

**Week 2 Complete:**
- [ ] CI/CD deploying automatically
- [ ] Load testing passed
- [ ] 80%+ test coverage

**Week 3 Complete:**
- [ ] GDPR compliant
- [ ] Horizontal scaling working
- [ ] CDN serving assets

**Week 4 Complete:**
- [ ] Security audit passed
- [ ] Multi-tenant ready
- [ ] Production launch approved

### Go/No-Go Decision

**LAUNCH CRITERIA:**
1. ✅ All Week 1-2 tasks complete
2. ✅ Load testing passed (100+ users)
3. ✅ Security audit no critical issues
4. ✅ Monitoring operational
5. ✅ Runbooks documented
6. ✅ Backup/restore tested

**If NO-GO:**
- Document blockers
- Extend timeline
- Beta launch with restrictions

---

## Appendix: Quick Reference

### Development Commands
```bash
# Start development
./start.sh

# Run tests
./test.sh
pytest --cov=app --cov-report=html

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Load testing
locust -f tests/load/locustfile.py --users 100 --spawn-rate 10

# Security scan
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:8000

# Build & deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Monitoring URLs
- Sentry: https://sentry.io/yourorg/operator-demo
- Grafana: https://metrics.yourdomain.com
- Status Page: https://status.yourdomain.com
- API Docs: https://api.yourdomain.com/docs

### Emergency Contacts
- On-Call DevOps: PagerDuty
- Tech Lead: [contact]
- Security Team: [contact]

---

**Document Version**: 1.0.0
**Last Updated**: October 12, 2025
**Next Review**: Weekly during implementation
**Owner**: Engineering Team
**Status**: ACTIVE - Ready for Sprint Planning
