# Architecture Decision Records (ADR) - CC-Lite 2026

**Created:** November 10, 2025
**Status:** Living Document
**Purpose:** Document and explain key architectural decisions for CC-Lite 2026

---

## 📋 Table of Contents

1. [Technology Stack Decisions](#technology-stack)
2. [Authentication Architecture](#authentication)
3. [Database Design](#database)
4. [Real-time Communication](#realtime)
5. [Voice AI Integration](#voice-ai)
6. [Frontend Architecture](#frontend)
7. [Deployment Strategy](#deployment)
8. [Security Decisions](#security)
9. [Performance Optimizations](#performance)
10. [Testing Strategy](#testing)

---

## 🏗️ Technology Stack Decisions {#technology-stack}

### ADR-001: FastAPI over FastifyJS

**Status:** Accepted
**Date:** October 2025

**Context:**
- Original cc-lite used Fastify (Node.js)
- Need better async support and type safety
- Team has Python expertise

**Decision:**
We will use FastAPI (Python) for the backend.

**Consequences:**
- ✅ Better async/await support with Python 3.11+
- ✅ Automatic OpenAPI documentation
- ✅ Built-in data validation with Pydantic
- ✅ Superior WebSocket support
- ❌ Different ecosystem from Node.js
- ❌ Requires Python knowledge

**Alternatives Considered:**
- Fastify (Node.js): Good but less type safety
- NestJS: Too heavy, opinionated
- Go/Fiber: Less ecosystem support for AI

---

### ADR-002: SvelteKit 2.0 over Next.js 14

**Status:** Accepted
**Date:** October 2025

**Context:**
- Original used Next.js 14 with App Router
- Need better performance and smaller bundles
- Want simpler state management

**Decision:**
We will use SvelteKit 2.0 for the frontend.

**Consequences:**
- ✅ Smaller bundle sizes (no virtual DOM)
- ✅ Better performance (compiled)
- ✅ Simpler state management (stores)
- ✅ File-based routing
- ❌ Smaller ecosystem than React
- ❌ Less third-party components

**Alternatives Considered:**
- Next.js 14: Too heavy for real-time
- Vue 3/Nuxt: Good but less performance
- Solid.js: Too new, smaller ecosystem

---

## 🔐 Authentication Architecture {#authentication}

### ADR-003: Ed25519 JWT over RS256

**Status:** Accepted
**Date:** October 2025

**Context:**
- Need secure, fast token signing
- Want smaller token sizes
- Modern cryptography preferred

**Decision:**
We will use Ed25519 signatures for JWT tokens.

**Consequences:**
- ✅ Faster signing/verification (5x faster than RS256)
- ✅ Smaller signatures (64 bytes vs 256)
- ✅ Modern, secure algorithm
- ✅ Constant-time operations (side-channel resistant)
- ❌ Less library support
- ❌ Not all services support Ed25519

**Implementation:**
```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()
```

---

### ADR-004: Redis for Token Revocation

**Status:** Accepted
**Date:** October 2025

**Context:**
- JWT tokens can't be revoked by design
- Need logout and security revocation
- Want fast lookups

**Decision:**
We will use Redis to maintain a revocation list.

**Consequences:**
- ✅ Fast O(1) lookups
- ✅ TTL support for auto-cleanup
- ✅ Distributed cache support
- ❌ Additional infrastructure
- ❌ Memory usage for blacklist

---

## 🗄️ Database Design {#database}

### ADR-005: PostgreSQL with JSON Support

**Status:** Accepted
**Date:** October 2025

**Context:**
- Need ACID compliance for transactions
- Want flexibility for schema evolution
- Need JSON for dynamic configs

**Decision:**
We will use PostgreSQL with JSONB columns for flexible data.

**Consequences:**
- ✅ ACID compliance
- ✅ JSONB for flexible schemas
- ✅ Full-text search built-in
- ✅ Window functions for analytics
- ❌ More complex than NoSQL
- ❌ Requires careful indexing

**Schema Pattern:**
```sql
CREATE TABLE campaigns (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    config JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Index on JSONB fields
    CREATE INDEX idx_campaign_config ON campaigns USING GIN (config);
);
```

---

### ADR-006: UUID v4 for Primary Keys

**Status:** Accepted
**Date:** October 2025

**Context:**
- Need globally unique identifiers
- Want to avoid sequence conflicts
- Planning for distributed systems

**Decision:**
We will use UUID v4 for all primary keys.

**Consequences:**
- ✅ Globally unique without coordination
- ✅ Can generate IDs client-side
- ✅ No sequence conflicts
- ❌ Larger than integers (16 bytes)
- ❌ Not sequential (index fragmentation)

---

## 🔄 Real-time Communication {#realtime}

### ADR-007: Native WebSocket over Socket.io

**Status:** Accepted
**Date:** October 2025

**Context:**
- Need bidirectional real-time communication
- Want minimal overhead
- FastAPI has excellent WebSocket support

**Decision:**
We will use native WebSocket protocol.

**Consequences:**
- ✅ Lower overhead (no Socket.io protocol)
- ✅ Native browser support
- ✅ Better performance
- ❌ No automatic reconnection
- ❌ No room/namespace abstractions
- ❌ Must implement heartbeat manually

**Implementation:**
```python
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    # Implement reconnection and heartbeat
```

---

### ADR-008: Circuit Breaker Pattern

**Status:** Accepted
**Date:** October 2025

**Context:**
- Multiple external AI providers
- Need resilience to failures
- Want automatic recovery

**Decision:**
We will implement circuit breaker pattern for all external calls.

**Consequences:**
- ✅ Automatic failure detection
- ✅ Prevents cascading failures
- ✅ Self-healing system
- ❌ Added complexity
- ❌ Requires tuning thresholds

**States:**
```
CLOSED -> OPEN (after 3 failures)
OPEN -> HALF_OPEN (after 30 seconds)
HALF_OPEN -> CLOSED (on success) or OPEN (on failure)
```

---

## 🎙️ Voice AI Integration {#voice-ai}

### ADR-009: Multi-Provider Strategy

**Status:** Accepted
**Date:** October 2025

**Context:**
- Different providers have different strengths
- Need fallback for reliability
- Want cost optimization

**Decision:**
We will support multiple AI providers with fallback.

**Consequences:**
- ✅ Provider independence
- ✅ Automatic fallback
- ✅ Cost optimization
- ✅ Best tool for each job
- ❌ Complex abstraction layer
- ❌ Different APIs to maintain

**Provider Matrix:**
```yaml
OpenAI:
  - Best for: General conversation
  - Fallback: Gemini

Gemini:
  - Best for: Long context
  - Fallback: OpenAI

Deepgram:
  - Best for: Real-time STT/TTS
  - Fallback: OpenAI Whisper
```

---

### ADR-010: Unified Audio Pipeline

**Status:** Accepted
**Date:** October 2025

**Context:**
- Different providers use different audio formats
- Need consistent processing
- Want minimal latency

**Decision:**
We will implement a unified audio pipeline with format conversion.

**Consequences:**
- ✅ Provider agnostic audio handling
- ✅ Consistent quality
- ✅ Format conversion built-in
- ❌ Processing overhead
- ❌ Memory usage for buffers

---

## 🎨 Frontend Architecture {#frontend}

### ADR-011: Component-First Design

**Status:** Accepted
**Date:** November 2025

**Context:**
- Need reusable UI components
- Want consistent design
- Planning for scale

**Decision:**
We will build a component library before features.

**Consequences:**
- ✅ Consistent UI/UX
- ✅ Faster feature development
- ✅ Easy testing
- ❌ Upfront investment
- ❌ May over-engineer

**Component Hierarchy:**
```
Atoms: Button, Input, Badge
Molecules: Card, FormField, Alert
Organisms: DataTable, Dashboard, Form
Templates: PageLayout, AuthLayout
Pages: Campaigns, Teams, Analytics
```

---

### ADR-012: Svelte Stores for State

**Status:** Accepted
**Date:** November 2025

**Context:**
- Need reactive state management
- Want simple mental model
- Avoid Redux complexity

**Decision:**
We will use Svelte stores for all state management.

**Consequences:**
- ✅ Simple, reactive
- ✅ No boilerplate
- ✅ Built-in to Svelte
- ❌ Less structured than Redux
- ❌ Need discipline for complex state

---

## 🚀 Deployment Strategy {#deployment}

### ADR-013: Docker Compose for Development

**Status:** Accepted
**Date:** October 2025

**Context:**
- Need consistent dev environments
- Want easy onboarding
- Multiple services to orchestrate

**Decision:**
We will use Docker Compose for development.

**Consequences:**
- ✅ Consistent environments
- ✅ Easy onboarding
- ✅ Service orchestration
- ❌ Resource usage
- ❌ Slower than native

---

### ADR-014: Kubernetes-Ready Architecture

**Status:** Proposed
**Date:** November 2025

**Context:**
- Planning for scale
- Need orchestration
- Want cloud-native

**Decision:**
We will design for Kubernetes deployment.

**Consequences:**
- ✅ Scalable architecture
- ✅ Cloud-native
- ✅ Self-healing
- ❌ Complexity
- ❌ Learning curve

---

## 🔒 Security Decisions {#security}

### ADR-015: Defense in Depth

**Status:** Accepted
**Date:** October 2025

**Context:**
- Handling sensitive call data
- Multiple attack vectors
- Compliance requirements

**Decision:**
We will implement multiple security layers.

**Layers:**
1. Network: Firewall, DDoS protection
2. Application: Input validation, CSRF tokens
3. Data: Encryption at rest and in transit
4. Access: RBAC, MFA
5. Monitoring: Audit logs, anomaly detection

---

### ADR-016: Zero-Trust Internal Network

**Status:** Accepted
**Date:** November 2025

**Context:**
- Microservice communication
- Internal threats
- Compliance requirements

**Decision:**
All internal service communication requires authentication.

**Consequences:**
- ✅ Better security posture
- ✅ Service isolation
- ✅ Audit trail
- ❌ Performance overhead
- ❌ Complex key management

---

## ⚡ Performance Optimizations {#performance}

### ADR-017: Redis Caching Strategy

**Status:** Accepted
**Date:** October 2025

**Context:**
- Database query performance
- Session management
- Real-time features

**Decision:**
We will use Redis for multi-layer caching.

**Cache Layers:**
```yaml
L1 - Application Memory: 10ms TTL, hot data
L2 - Redis Cache: 5min TTL, session data
L3 - PostgreSQL: Persistent storage
```

---

### ADR-018: Database Connection Pooling

**Status:** Accepted
**Date:** October 2025

**Context:**
- Connection overhead
- Concurrent requests
- Resource limits

**Decision:**
We will use SQLAlchemy async with connection pooling.

**Configuration:**
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

---

## 🧪 Testing Strategy {#testing}

### ADR-019: Test Pyramid Approach

**Status:** Accepted
**Date:** November 2025

**Context:**
- Need comprehensive testing
- Want fast feedback
- Balance coverage and speed

**Decision:**
We will follow the test pyramid.

**Distribution:**
```
Unit Tests: 70% (fast, isolated)
Integration Tests: 20% (API, database)
E2E Tests: 10% (critical paths)
```

---

### ADR-020: Contract Testing for APIs

**Status:** Accepted
**Date:** November 2025

**Context:**
- Frontend-backend coordination
- API versioning
- Prevent breaking changes

**Decision:**
We will implement contract testing between frontend and backend.

**Consequences:**
- ✅ Catch breaking changes early
- ✅ Clear API contracts
- ✅ Parallel development
- ❌ Additional test layer
- ❌ Contract maintenance

---

## 📊 Monitoring & Observability

### ADR-021: Structured Logging

**Status:** Accepted
**Date:** October 2025

**Context:**
- Need searchable logs
- Want correlation across services
- Planning for scale

**Decision:**
We will use structured JSON logging with correlation IDs.

**Format:**
```json
{
  "timestamp": "2025-11-10T10:00:00Z",
  "level": "INFO",
  "correlation_id": "abc-123",
  "service": "backend",
  "message": "Campaign created",
  "metadata": {
    "campaign_id": "xyz-789",
    "user_id": "user-456"
  }
}
```

---

### ADR-022: Prometheus Metrics

**Status:** Accepted
**Date:** October 2025

**Context:**
- Need performance monitoring
- Want standard metrics format
- Planning for Grafana dashboards

**Decision:**
We will expose Prometheus metrics on /metrics endpoint.

**Key Metrics:**
```python
http_requests_total
http_request_duration_seconds
websocket_connections_active
ai_provider_requests_total
ai_provider_latency_seconds
database_query_duration_seconds
```

---

## 🔄 Migration Strategy

### ADR-023: Gradual Feature Migration

**Status:** Accepted
**Date:** November 2025

**Context:**
- Can't migrate everything at once
- Need to maintain service
- Want to reduce risk

**Decision:**
We will migrate features gradually over 12 weeks.

**Phases:**
1. Core infrastructure (Weeks 1-2)
2. Campaign management (Weeks 3-4)
3. Team features (Weeks 5-6)
4. Advanced features (Weeks 7-12)

---

## 📝 Documentation Standards

### ADR-024: Documentation as Code

**Status:** Accepted
**Date:** November 2025

**Context:**
- Documentation gets outdated
- Want version control
- Need review process

**Decision:**
All documentation lives in the repository as Markdown.

**Structure:**
```
/docs
  /architecture - System design
  /api - API documentation
  /guides - How-to guides
  /decisions - ADRs
```

---

## 🎯 Future Considerations

### Planned Decisions

1. **GraphQL vs REST**: Evaluate for v3.0
2. **Event Sourcing**: For audit trail
3. **CQRS Pattern**: For complex queries
4. **Serverless Functions**: For scaling
5. **Multi-tenancy**: For SaaS model

### Technology Radar

**Adopt:**
- FastAPI, SvelteKit 2.0
- PostgreSQL, Redis
- Docker, GitHub Actions

**Trial:**
- Kubernetes, Temporal.io
- GraphQL, gRPC

**Assess:**
- Bun runtime, Deno
- WebAssembly, Edge functions

**Hold:**
- Microservices (premature)
- Blockchain (no use case)

---

## 📚 References

- [Stack 2026 Standards](./stack-2026-standards.md)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/best-practices/)
- [SvelteKit Documentation](https://kit.svelte.dev/docs)
- [PostgreSQL JSON Performance](https://www.postgresql.org/docs/current/datatype-json.html)
- [WebSocket Protocol RFC](https://datatracker.ietf.org/doc/html/rfc6455)

---

**Living Document:** This ADR collection will evolve as we make new decisions and learn from implementation.