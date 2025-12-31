# Voice by Kraliki - Professional AI Call Center Platform

**Version:** 2.0.0
**Last Updated:** November 11, 2025
**Status:** ✅ Production-Ready (Headless backend; UI templates separated)
**Stack:** FastAPI (Python 3.11+) backend; UI templates live in `/applications/*-template`
**Architecture:** Stack 2026 Compliant

## 🚀 Overview

Voice by Kraliki is a headless AI-powered call center backend providing enterprise-grade voice operations, campaign management, and analytics for template UIs.

Voice by Kraliki runs as a standalone backend service. Kraliki Swarm orchestrates workflows via MCP/API (master/slave) without embedding UI in the swarm. Human oversight happens in Swarm; human takeover happens in template UIs when needed.

**UI templates:** The `frontend/` directory is legacy reference only. Current UIs live under `/applications/*-template` and are not deployed with this service.

Telephony defaults to Telnyx (primary for CZ/EU). Twilio remains supported for teams that prefer it.

### Technology Stack
- **Backend:** FastAPI (Python 3.11+), SQLAlchemy ORM, Alembic migrations
- **Template UI:** SvelteKit 2.x, TypeScript, Tailwind CSS, Svelte Stores
- **Database:** PostgreSQL with Alembic schema management
- **Voice AI:** OpenAI Realtime API, Gemini 2.5 Native Audio, Deepgram STT/TTS
- **Telephony:** Twilio MediaStream + Telnyx Call Control
- **Real-time:** WebSocket bidirectional audio/text streaming
- **Security:** JWT authentication with bcrypt password hashing
- **Internationalization:** Custom i18n system with EN, ES, CS support

## 📋 Feature Overview

### ✅ Completed Features (All 12 Weeks)

#### Week 1-2: Campaign Management System
- **Campaign CRUD Operations** - Create, read, update, delete campaigns
- **Contact List Management** - Import, manage, and segment contact lists
- **Call List Builder** - Dynamic contact filtering and prioritization
- **Campaign Templates** - Reusable campaign configurations
- **Multi-Provider Support** - OpenAI, Gemini, Deepgram integration
- **Campaign Analytics** - Real-time tracking and reporting
- **Frontend UI** - 4 comprehensive pages (campaigns, contacts, templates, details)

#### Week 3-4: Team & Supervisor Cockpit
- **Team Management** - Create and manage agent teams
- **Agent Profiles** - Skills, availability, performance tracking
- **Supervisor Dashboard** - Real-time team monitoring
- **Queue Management** - Call queue monitoring and distribution
- **Live Call Monitoring** - Real-time supervisor oversight
- **Performance Metrics** - Agent KPIs and productivity tracking
- **Frontend UI** - 4 feature-complete pages (teams, agents, supervisor cockpit, queues)

#### Week 5-6: Company & Knowledge Base
- **Company Profiles** - Multi-tenant company management
- **Knowledge Base** - Hierarchical article organization
- **Vector Search** - Semantic search with Qdrant integration
- **Document Management** - Upload, categorize, version control
- **Access Controls** - Team-based permissions and visibility
- **Frontend UI** - 4 comprehensive pages (companies, knowledge base, documents, search)

#### Week 7-8: Call Center Operations
- **IVR System** - Interactive Voice Response flow builder
- **Call Routing Engine** - 8 routing strategies (skill-based, round-robin, priority, etc.)
- **Recording Management** - Call recording, playback, analytics
- **Voicemail System** - Voicemail capture, transcription, callback
- **Visual IVR Builder** - Drag-and-drop flow designer with 9 node types
- **Routing Rule Builder** - Complex condition-based routing
- **Frontend UI** - 4 operational pages (IVR, routing, recordings, voicemail)

#### Week 9-10: Analytics & Intelligence
- **Metrics Collection** - Time-series metrics with tags and dimensions
- **Pre-computed Aggregations** - Minute, hour, day, week, month granularities
- **Performance Alerting** - Threshold-based alerts with 4 severity levels
- **Report Generation** - PDF, CSV, Excel, JSON export formats
- **Report Templates** - Reusable report configurations
- **Report Scheduling** - Automated report generation and delivery
- **Dashboard Overview** - Real-time analytics with auto-refresh
- **Frontend UI** - 4 analytics pages (dashboard, reports, templates, metrics)

#### Week 11: Localization & Multi-Language
- **i18n System** - Custom translation framework with Svelte stores
- **Three Languages** - English, Spanish, Czech (185+ strings per language)
- **Dynamic Translation Loading** - Async locale switching
- **Browser Language Detection** - Automatic locale selection
- **Parameter Interpolation** - Dynamic values in translations
- **Language Switcher UI** - Globe icon dropdown component
- **Backend Translation** - Error messages and API responses
- **Module-based Organization** - Common, navigation, analytics, operations, campaigns

#### Week 12: Final Polish & Production Readiness
- **Comprehensive Documentation** - Complete README with architecture and features
- **Deployment Guide** - Docker, Traefik, SSL/TLS configuration
- **API Documentation** - Complete reference for 100+ endpoints
- **Security Documentation** - Best practices and measures
- **Performance Documentation** - Optimizations and caching strategies
- **Troubleshooting Guide** - Common issues and solutions
- **Production Checklist** - Pre-deployment verification steps
- **Backup & Recovery** - Automated backup procedures

## 📦 Current System Status

### Services Running
```bash
✅ Backend API:     http://localhost:8000 (healthy)
Legacy UI:         /frontend (template reference only)
✅ API Docs:        http://localhost:8000/docs
✅ PostgreSQL:      operator_demo database with full schema
✅ Redis:           Port 6379 for caching
✅ Qdrant:          Ports 6333-6334 for vector operations
```

### Database Schema
- **Authentication:** users, sessions, JWT tokens
- **Campaigns:** campaigns, contacts, call_lists, templates
- **Teams:** teams, agents, agent_skills, supervisor_assignments
- **Companies:** companies, knowledge_articles, documents
- **Operations:** ivr_flows, ivr_nodes, routing_rules, recordings, voicemails
- **Analytics:** metrics, metric_aggregations, performance_alerts, metric_thresholds
- **Reports:** report_templates, reports, report_schedules, report_widgets

### Test Credentials
- **Email:** testuser@example.com
- **Password:** test123
- **JWT Token:** Available via `/api/v1/auth/login`

## ✅ Migration Highlights

- **Complete Stack Migration:** From Fastify/Next.js → FastAPI/SvelteKit 2
- **Authentication System:** Ed25519 JWT with bcrypt password hashing
- **Multi-Provider Support:** OpenAI, Gemini, Deepgram with unified interface
- **Telephony Integration:** Twilio MediaStream and Telnyx Call Control
- **Real-time Streaming:** WebSocket support for bidirectional audio/text
- **Database Integration:** PostgreSQL with session management
- **Container Ready:** Docker Compose with production configuration

## 📦 Current System Status

### Services Running
```bash
✅ Backend API:     http://localhost:8000 (healthy)
Legacy UI:         /frontend (template reference only)
✅ API Docs:        http://localhost:8000/docs
✅ PostgreSQL:      operator_demo database with auth tables
✅ Redis:           Port 6379 for caching
✅ Qdrant:          Ports 6333-6334 for vector operations
```

### Test Credentials
- **Email:** testuser@example.com
- **Password:** test123
- **JWT Token:** Available via `/api/v1/auth/login`

## 🏗️ Architecture

### Backend Structure (FastAPI + Python 3.11+)
```
backend/
├── app/
│   ├── main.py                        # FastAPI application with CORS and routers
│   ├── core/
│   │   ├── config.py                  # Environment configuration
│   │   ├── database.py                # SQLAlchemy session management
│   │   └── security.py                # JWT authentication utilities
│   ├── models/
│   │   ├── user.py                    # User and authentication models
│   │   ├── campaign.py                # Campaign, contacts, call lists
│   │   ├── team.py                    # Teams, agents, skills
│   │   ├── company.py                 # Companies, knowledge base
│   │   ├── operations.py              # IVR, routing, recordings
│   │   ├── analytics.py               # Metrics, aggregations, alerts
│   │   └── report.py                  # Report templates and instances
│   ├── schemas/
│   │   ├── campaign.py                # Pydantic schemas for validation
│   │   ├── team.py                    # Team and agent schemas
│   │   ├── operations.py              # Operations schemas
│   │   └── analytics.py               # Analytics and report schemas
│   ├── services/
│   │   ├── campaign.py                # Campaign business logic
│   │   ├── team.py                    # Team management logic
│   │   ├── knowledge.py               # Knowledge base with vector search
│   │   ├── ivr.py                     # IVR flow execution
│   │   ├── routing.py                 # Call routing strategies
│   │   ├── metrics.py                 # Metrics collection service
│   │   ├── analytics.py               # Analytics and alerting
│   │   └── reports.py                 # Report generation
│   ├── api/v1/
│   │   └── endpoints/
│   │       ├── auth.py                # Authentication endpoints
│   │       ├── campaigns.py           # Campaign CRUD + 7 additional endpoints
│   │       ├── teams.py               # Team management + agent operations
│   │       ├── companies.py           # Company and knowledge base
│   │       ├── ivr.py                 # IVR flow management
│   │       ├── routing.py             # Routing rules
│   │       ├── recordings.py          # Recording operations
│   │       ├── voicemail.py           # Voicemail management
│   │       ├── analytics.py           # Metrics, alerts, thresholds
│   │       └── reports.py             # Report templates and generation
│   ├── i18n/
│   │   ├── translator.py              # Backend translation system
│   │   └── __init__.py                # Translation utilities
│   └── alembic/
│       └── versions/                  # Database migrations (50+ migrations)
```

### Frontend Structure (SvelteKit 2.x + TypeScript)
```
frontend/
├── src/
│   ├── routes/                        # File-based routing (SvelteKit)
│   │   ├── +page.svelte              # Main dashboard
│   │   ├── +layout.svelte            # Root layout with Header
│   │   ├── login/                    # Authentication pages
│   │   ├── campaigns/                # Campaign management (4 pages)
│   │   │   ├── +page.svelte         # Campaign list
│   │   │   ├── [id]/+page.svelte    # Campaign details
│   │   │   ├── templates/           # Campaign templates
│   │   │   └── contacts/            # Contact management
│   │   ├── teams/                    # Team management (4 pages)
│   │   │   ├── +page.svelte         # Team list
│   │   │   ├── agents/              # Agent profiles
│   │   │   ├── supervisor/          # Supervisor cockpit
│   │   │   └── queues/              # Queue monitoring
│   │   ├── companies/                # Company management (4 pages)
│   │   │   ├── +page.svelte         # Company list
│   │   │   ├── knowledge/           # Knowledge base
│   │   │   ├── documents/           # Document management
│   │   │   └── search/              # Semantic search
│   │   ├── operations/               # Call center operations (4 pages)
│   │   │   ├── ivr/                 # IVR flows + builder
│   │   │   ├── routing/             # Routing rules + builder
│   │   │   ├── recordings/          # Call recordings
│   │   │   └── voicemail/           # Voicemail management
│   │   ├── analytics/                # Analytics & reporting (4 pages)
│   │   │   ├── dashboard/           # Real-time dashboard
│   │   │   ├── reports/             # Report management
│   │   │   ├── templates/           # Report templates
│   │   │   └── metrics/             # Metrics explorer
│   │   ├── calls/                    # Call interfaces
│   │   │   ├── outbound/            # Outbound calling
│   │   │   └── incoming/            # Incoming calls
│   │   └── settings/                 # Provider settings
│   ├── lib/
│   │   ├── api/                      # API client utilities
│   │   ├── stores/
│   │   │   ├── auth.ts              # Authentication store
│   │   │   └── theme.ts             # Theme management
│   │   ├── i18n/
│   │   │   ├── index.ts             # i18n configuration
│   │   │   └── locales/             # Translation files (EN/ES/CS)
│   │   │       ├── en/              # English translations
│   │   │       ├── es/              # Spanish translations
│   │   │       └── cs/              # Czech translations
│   │   └── components/
│   │       └── layout/
│   │           ├── Header.svelte    # Main navigation header
│   │           ├── ThemeToggle.svelte
│   │           └── LanguageSwitcher.svelte
│   └── hooks.server.ts               # JWT cookie authentication
```

### Design Patterns
- **Service Layer Pattern:** Business logic separated from API endpoints
- **Repository Pattern:** SQLAlchemy ORM with clean data access
- **Reactive State Management:** Svelte stores for frontend state
- **Component-based UI:** Reusable Svelte components with TypeScript
- **RESTful API Design:** Standard HTTP methods with consistent responses
- **Migration-based Schema:** Alembic for version-controlled database changes

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 24+ (for local development)
- Python 3.11+ (for local development)

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repository>
cd operator-demo-multiprovider

# 2. Environment setup (already configured)
# API keys are in .env file (test keys included)

# 3. Start all services
docker compose -f docker-compose.prod.yml up -d

# 4. Check service health
docker compose -f docker-compose.prod.yml ps

# 5. Access the application
# Backend API: http://localhost:8000
# Frontend:    http://localhost:3000
# API Docs:    http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload

# Frontend
cd frontend
pnpm install
pnpm dev
```

## 🔑 API Endpoints

### Authentication
```http
POST /api/v1/auth/register        # Register new user
POST /api/v1/auth/login           # Login and get JWT token
GET  /api/v1/auth/me              # Get current user profile
```

### Campaigns (Week 1-2)
```http
GET    /api/v1/campaigns                    # List campaigns
POST   /api/v1/campaigns                    # Create campaign
GET    /api/v1/campaigns/{id}               # Get campaign details
PUT    /api/v1/campaigns/{id}               # Update campaign
DELETE /api/v1/campaigns/{id}               # Delete campaign
POST   /api/v1/campaigns/{id}/start         # Start campaign
POST   /api/v1/campaigns/{id}/pause         # Pause campaign
POST   /api/v1/campaigns/{id}/clone         # Clone campaign

GET    /api/v1/contacts                     # List contacts
POST   /api/v1/contacts                     # Create contact
POST   /api/v1/contacts/import              # Bulk import contacts
GET    /api/v1/contacts/{id}                # Get contact details
PUT    /api/v1/contacts/{id}                # Update contact
DELETE /api/v1/contacts/{id}                # Delete contact

GET    /api/v1/call-lists                   # List call lists
POST   /api/v1/call-lists                   # Create call list
GET    /api/v1/call-lists/{id}              # Get call list
PUT    /api/v1/call-lists/{id}              # Update call list

GET    /api/v1/campaign-templates           # List templates
POST   /api/v1/campaign-templates           # Create template
GET    /api/v1/campaign-templates/{id}      # Get template
```

### Teams & Agents (Week 3-4)
```http
GET    /api/v1/teams                        # List teams
POST   /api/v1/teams                        # Create team
GET    /api/v1/teams/{id}                   # Get team details
PUT    /api/v1/teams/{id}                   # Update team
DELETE /api/v1/teams/{id}                   # Delete team
GET    /api/v1/teams/{id}/agents            # Get team agents
GET    /api/v1/teams/{id}/performance       # Team performance metrics

GET    /api/v1/agents                       # List agents
POST   /api/v1/agents                       # Create agent
GET    /api/v1/agents/{id}                  # Get agent profile
PUT    /api/v1/agents/{id}                  # Update agent
DELETE /api/v1/agents/{id}                  # Delete agent
POST   /api/v1/agents/{id}/skills           # Add agent skills
GET    /api/v1/agents/{id}/performance      # Agent performance

GET    /api/v1/queues                       # List call queues
GET    /api/v1/queues/{id}                  # Get queue details
GET    /api/v1/queues/{id}/calls            # Get queued calls
```

### Companies & Knowledge Base (Week 5-6)
```http
GET    /api/v1/companies                    # List companies
POST   /api/v1/companies                    # Create company
GET    /api/v1/companies/{id}               # Get company
PUT    /api/v1/companies/{id}               # Update company
DELETE /api/v1/companies/{id}               # Delete company

GET    /api/v1/knowledge                    # List knowledge articles
POST   /api/v1/knowledge                    # Create article
GET    /api/v1/knowledge/{id}               # Get article
PUT    /api/v1/knowledge/{id}               # Update article
DELETE /api/v1/knowledge/{id}               # Delete article
POST   /api/v1/knowledge/search             # Semantic search (vector)

GET    /api/v1/documents                    # List documents
POST   /api/v1/documents                    # Upload document
GET    /api/v1/documents/{id}               # Get document
DELETE /api/v1/documents/{id}               # Delete document
```

### Call Center Operations (Week 7-8)
```http
# IVR Management
GET    /api/ivr/flows                       # List IVR flows
POST   /api/ivr/flows                       # Create IVR flow
GET    /api/ivr/flows/{id}                  # Get IVR flow
PUT    /api/ivr/flows/{id}                  # Update IVR flow
DELETE /api/ivr/flows/{id}                  # Delete IVR flow
POST   /api/ivr/flows/{id}/publish          # Publish flow version
GET    /api/ivr/flows/{id}/analytics        # Flow analytics

# Routing Rules
GET    /api/routing/rules                   # List routing rules
POST   /api/routing/rules                   # Create routing rule
GET    /api/routing/rules/{id}              # Get routing rule
PUT    /api/routing/rules/{id}              # Update routing rule
DELETE /api/routing/rules/{id}              # Delete routing rule

# Recordings
GET    /api/recordings                      # List recordings
GET    /api/recordings/{id}                 # Get recording
DELETE /api/recordings/{id}                 # Delete recording
GET    /api/recordings/{id}/transcription   # Get transcription
POST   /api/recordings/{id}/analyze         # Analyze recording

# Voicemail
GET    /api/voicemail                       # List voicemails
GET    /api/voicemail/{id}                  # Get voicemail
DELETE /api/voicemail/{id}                  # Delete voicemail
PUT    /api/voicemail/{id}                  # Update voicemail status
```

### Analytics & Reports (Week 9-10)
```http
# Metrics
POST   /api/analytics/metrics               # Record metric
GET    /api/analytics/metrics               # Query metrics
GET    /api/analytics/metrics/{id}          # Get metric details

# Aggregations
GET    /api/analytics/aggregations          # Get aggregated metrics
POST   /api/analytics/aggregations/compute  # Trigger aggregation

# Alerts
GET    /api/analytics/alerts                # List alerts
GET    /api/analytics/alerts/{id}           # Get alert details
PUT    /api/analytics/alerts/{id}/acknowledge  # Acknowledge alert

# Thresholds
GET    /api/analytics/thresholds            # List metric thresholds
POST   /api/analytics/thresholds            # Create threshold
PUT    /api/analytics/thresholds/{id}       # Update threshold
DELETE /api/analytics/thresholds/{id}       # Delete threshold

# Dashboard
GET    /api/analytics/dashboard/overview    # Dashboard overview

# Report Templates
GET    /api/reports/templates               # List report templates
POST   /api/reports/templates               # Create template
GET    /api/reports/templates/{id}          # Get template
PUT    /api/reports/templates/{id}          # Update template
DELETE /api/reports/templates/{id}          # Delete template

# Reports
GET    /api/reports/                        # List reports
POST   /api/reports/generate                # Generate report
GET    /api/reports/{id}                    # Get report details
DELETE /api/reports/{id}                    # Delete report

# Report Schedules
GET    /api/reports/schedules               # List schedules
POST   /api/reports/schedules               # Create schedule
PUT    /api/reports/schedules/{id}          # Update schedule
DELETE /api/reports/schedules/{id}          # Delete schedule
```

### Interactive API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database (using existing postgres container)
DATABASE_URL=postgresql://postgres:password@operator-demo-postgres:5432/operator_demo

# AI Providers (test keys included)
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSy...
DEEPGRAM_API_KEY=25deda7e...

# Telephony (test credentials)
TWILIO_ACCOUNT_SID=ACa75fdadde...
TWILIO_AUTH_TOKEN=8e2cee6f53...
TWILIO_PHONE_NUMBER_US=+18455954168

# Security
JWT_SECRET=change-this-in-production
SECRET_KEY=change-this-in-production
```

## 🔒 Security Measures

### Authentication & Authorization
- **JWT Tokens:** Secure token-based authentication
- **Password Hashing:** bcrypt with salt rounds
- **HTTP-Only Cookies:** Secure cookie storage for frontend
- **Token Expiration:** Configurable token lifetime
- **CORS Protection:** Configured allowed origins

### Data Security
- **SQL Injection Prevention:** Parameterized queries via SQLAlchemy ORM
- **XSS Protection:** Input sanitization and output encoding
- **Environment Variables:** Sensitive data in .env files (never committed)
- **Database Encryption:** PostgreSQL connection encryption (production)

### API Security
- **Rate Limiting:** Request throttling (configurable)
- **Input Validation:** Pydantic schemas for all API inputs
- **Error Handling:** Generic error messages (no sensitive data leakage)
- **HTTPS:** SSL/TLS in production deployments

### Best Practices
- **Principle of Least Privilege:** Role-based access control
- **Audit Logging:** User actions and system events
- **Regular Updates:** Dependencies kept up-to-date
- **Security Headers:** CORS, CSP, X-Frame-Options

## ⚡ Performance Optimizations

### Backend Performance
- **Database Indexing:** Indexes on frequently queried columns
  - `campaigns.status`, `campaigns.created_by_id`
  - `contacts.campaign_id`, `contacts.email`
  - `agents.team_id`, `agents.status`
  - `metrics.timestamp`, `metrics.metric_type`, `metrics.metric_name`
- **Connection Pooling:** SQLAlchemy connection pool (10-20 connections)
- **Query Optimization:** Eager loading with `joinedload()` to prevent N+1 queries
- **Pagination:** Limit/offset pagination for large datasets
- **Pre-computed Aggregations:** Hourly/daily metrics aggregation (Week 9-10)

### Frontend Performance
- **Code Splitting:** Route-based code splitting in SvelteKit
- **Lazy Loading:** Dynamic imports for heavy components
- **Svelte Compilation:** Compile-time optimization (no virtual DOM)
- **Asset Optimization:** Minification and compression
- **Caching:** Browser caching for static assets

### Caching Strategy
- **Redis Caching:** Session data and frequently accessed data
- **Client-side Caching:** LocalStorage for user preferences
- **HTTP Caching:** Cache-Control headers for static content

## 📊 Feature Comparison Matrix

| Feature | Status | Lines of Code | Key Technologies |
|---------|--------|--------------|------------------|
| **Authentication** | ✅ Complete | 500+ | JWT, bcrypt, SQLAlchemy |
| **Campaign Management** | ✅ Complete (Week 1-2) | 2,800+ | FastAPI, Pydantic, Svelte |
| **Team Management** | ✅ Complete (Week 3-4) | 2,600+ | Service layer, Stores |
| **Knowledge Base** | ✅ Complete (Week 5-6) | 2,400+ | Qdrant, Vector search |
| **Call Center Ops** | ✅ Complete (Week 7-8) | 3,200+ | IVR builder, Routing engine |
| **Analytics & Reports** | ✅ Complete (Week 9-10) | 3,700+ | Time-series, Aggregations |
| **Multi-Language** | ✅ Complete (Week 11) | 1,100+ | Custom i18n, 3 languages |
| **Documentation** | ✅ Complete (Week 12) | 4,100+ | Markdown, Guides |
| **Total Implementation** | **12 Weeks Complete** | **20,400+ LOC** | **Production-ready platform** |

## 🐛 Known Issues & Solutions

### Issue: Bcrypt Password Hashing
- **Problem:** passlib conflict with bcrypt 5.0
- **Solution:** Using bcrypt directly without passlib wrapper
- **Status:** ✅ Fixed

### Issue: Database Connection
- **Problem:** Container network connectivity
- **Solution:** Connected containers to shared network
- **Status:** ✅ Fixed

### Issue: Frontend Build
- **Problem:** SvelteKit adapter-node configuration
- **Solution:** Installed and configured @sveltejs/adapter-node
- **Status:** ✅ Fixed

## 📚 Documentation

### Current Documentation
- **[Documentation Index](./DOCUMENTATION_INDEX.md)** - Complete documentation structure and navigation
- **[README.md](./README.md)** - Comprehensive project overview (1,030 lines)
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment guide (1,280 lines)
- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Complete API reference (1,800+ lines)
- **API Documentation:** http://localhost:8000/docs - Interactive OpenAPI
- **Code Guidelines:** [CLAUDE.md](./CLAUDE.md) - Code simplicity principles
- **Technical Docs:** `/docs/` - Architecture, voice bridge, telephony, testing

### Archived Documentation
- **Historical Audits:** `/_archive/docs-historical-audits/` - Pre-migration audit reports
- **Migration Reports:** `/_archive/migration-reports/` - Complete migration analysis
- **Legacy Docs:** `/_archive/docs/` - Outdated root-level documentation
- **Legacy Code:** `/_archive/legacy-backend/` and `/_archive/legacy-frontend/` - Original implementations

See [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) for complete documentation structure.

## 🔄 Development Roadmap Progress

### ✅ Completed (All 12 Weeks)

#### Week 1-2: Campaign Management System
- [x] Campaign CRUD backend (SQLAlchemy models, Pydantic schemas)
- [x] Contact management with import functionality
- [x] Call list builder with filtering
- [x] Campaign templates system
- [x] Campaign analytics tracking
- [x] 4 frontend pages (campaigns, contacts, templates, details)
- [x] Service layer with business logic
- [x] API endpoints (15+ routes)

#### Week 3-4: Team & Supervisor Cockpit
- [x] Team management backend
- [x] Agent profiles with skills tracking
- [x] Supervisor dashboard with real-time monitoring
- [x] Queue management system
- [x] Performance metrics collection
- [x] 4 frontend pages (teams, agents, supervisor, queues)
- [x] Team performance reporting
- [x] Agent status tracking

#### Week 5-6: Company & Knowledge Base
- [x] Multi-tenant company management
- [x] Knowledge base with hierarchical articles
- [x] Vector search integration (Qdrant)
- [x] Document management system
- [x] Access control and permissions
- [x] 4 frontend pages (companies, knowledge, documents, search)
- [x] Semantic search implementation
- [x] Article versioning

#### Week 7-8: Call Center Operations
- [x] IVR system backend (flows, nodes, analytics)
- [x] Call routing engine (8 strategies)
- [x] Recording management with transcription
- [x] Voicemail system with callbacks
- [x] Visual IVR builder (9 node types)
- [x] Routing rule builder with conditions
- [x] 4 frontend pages (IVR, routing, recordings, voicemail)
- [x] Flow analytics and performance tracking

#### Week 9-10: Analytics & Intelligence
- [x] Metrics collection service (time-series)
- [x] Pre-computed aggregations (5 granularities)
- [x] Performance alerting system (4 severity levels)
- [x] Report generation (PDF, CSV, Excel, JSON)
- [x] Report templates and scheduling
- [x] Dashboard overview API
- [x] 4 frontend pages (dashboard, reports, templates, metrics)
- [x] Real-time analytics with auto-refresh

#### Week 11: Localization & Multi-Language
- [x] Custom i18n system with Svelte stores
- [x] Three language support (EN, ES, CS)
- [x] 185+ translated strings (common, navigation, analytics, operations, campaigns)
- [x] Dynamic translation loading
- [x] Browser language detection
- [x] Language switcher UI component
- [x] Backend translation system
- [x] Parameter interpolation in translations

#### Week 12: Final Polish & Production Readiness
- [x] Comprehensive README documentation
- [x] Deployment guide (Docker, Traefik, SSL)
- [x] API documentation summary
- [x] Troubleshooting guide
- [x] Performance tuning documentation
- [x] Security measures documentation
- [x] Production deployment procedures
- [x] Monitoring and backup procedures

### 📊 Implementation Statistics
- **Total Weeks Completed:** 12/12 (100%)
- **Total Lines of Code:** 20,400+
- **Backend Models:** 40+ SQLAlchemy models
- **API Endpoints:** 100+ RESTful routes
- **Frontend Pages:** 28+ SvelteKit pages
- **Database Tables:** 35+ tables with relationships
- **Alembic Migrations:** 50+ version-controlled migrations
- **Translation Strings:** 185+ per language (3 languages)
- **Documentation Files:** 3 comprehensive guides (4,100+ lines)

## 🧪 Testing

### Backend Testing
```bash
# Run all tests
cd backend
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_campaigns.py -v

# Run with coverage
uv run pytest --cov=app tests/

# Run integration tests
uv run pytest tests/integration/ -v
```

### Frontend Testing
```bash
cd frontend

# Run unit tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run E2E tests (if configured)
pnpm test:e2e
```

### Test Coverage
- **Backend:** Models, services, API endpoints
- **Frontend:** Components, stores, utilities
- **Integration:** Full API workflow tests
- **E2E:** Critical user journeys (future)

## 🛠️ Development

### Local Development Setup
```bash
# 1. Install dependencies
cd backend && uv sync
cd ../frontend && pnpm install

# 2. Setup database (if needed)
cd backend
uv run alembic upgrade head

# 3. Run development servers
# Terminal 1: Backend
cd backend && uv run uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && pnpm dev

# Access:
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Database Operations
```bash
# Connect to PostgreSQL
docker exec -it operator-demo-postgres psql -U postgres -d operator_demo

# Common SQL operations
\dt                          # List all tables
\d campaigns                 # Describe campaigns table
SELECT * FROM users;         # Query users
SELECT * FROM campaigns WHERE status = 'active';

# Database migrations
cd backend
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
uv run alembic downgrade -1
```

### Building for Production
```bash
# Using Docker (recommended)
docker compose -f docker-compose.prod.yml build

# Manual build
cd backend && uv sync --no-dev
cd frontend && pnpm build

# The built frontend will be in frontend/build/
# The backend is ready to run with: uvicorn app.main:app
```

## 🚀 Deployment

### Pre-Deployment Checklist
- [ ] Update environment variables in `.env` file
- [ ] Set secure `JWT_SECRET` and `SECRET_KEY`
- [ ] Configure production database URL
- [ ] Set up API keys for OpenAI, Gemini, Deepgram
- [ ] Configure Twilio/Telnyx credentials
- [ ] Enable HTTPS/SSL certificates
- [ ] Set CORS allowed origins
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerting
- [ ] Test database migrations
- [ ] Review security headers

### Docker Production Deployment
```bash
# 1. Build production images
docker compose -f docker-compose.prod.yml build

# 2. Start all services
docker compose -f docker-compose.prod.yml up -d

# 3. Check service health
docker compose -f docker-compose.prod.yml ps

# 4. View logs
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend

# 5. Access services
# Backend API: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Production with Traefik (Advanced)
```bash
# For production with reverse proxy and SSL
./migrate-to-traefik.sh

# Access via custom domains
https://operator.yourdomain.com    # Frontend
https://api.yourdomain.com         # Backend API
```

### Environment-Specific Configuration

#### Development (.env.development)
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/operator_demo
DEBUG=true
LOG_LEVEL=debug
```

#### Production (.env.production)
```bash
DATABASE_URL=postgresql://user:password@prod-db:5432/cc_lite_prod
DEBUG=false
LOG_LEVEL=info
JWT_SECRET=<generate-secure-random-string>
SECRET_KEY=<generate-secure-random-string>
ALLOWED_ORIGINS=https://yourdomain.com
```

### Common Docker Commands
```bash
# Start services
docker compose -f docker-compose.prod.yml up -d

# Stop services
docker compose -f docker-compose.prod.yml down

# Restart specific service
docker compose -f docker-compose.prod.yml restart backend

# View logs (follow mode)
docker compose -f docker-compose.prod.yml logs -f

# View logs for specific service
docker compose -f docker-compose.prod.yml logs -f backend

# Execute command in container
docker compose -f docker-compose.prod.yml exec backend bash

# Scale services
docker compose -f docker-compose.prod.yml up -d --scale backend=3

# Remove all containers and volumes
docker compose -f docker-compose.prod.yml down -v
```

### Database Backup & Restore
```bash
# Backup database
docker exec operator-demo-postgres pg_dump -U postgres operator_demo > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20251111.sql | docker exec -i operator-demo-postgres psql -U postgres operator_demo

# Automated backup (add to crontab)
0 2 * * * /path/to/backup-script.sh
```

### Monitoring & Health Checks
```bash
# Backend health check
curl http://localhost:8000/health

# Check service status
docker compose -f docker-compose.prod.yml ps

# Monitor resource usage
docker stats

# View container resource limits
docker inspect operator-demo-backend | grep -A 10 Resources
```

## 🔧 Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Check database connection
psql -h localhost -U postgres -d operator_demo

# Check environment variables
cat .env | grep DATABASE_URL

# View backend logs
docker compose logs backend
```

#### Frontend won't start
```bash
# Check if port 3000 is already in use
lsof -i :3000

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
pnpm install

# Check SvelteKit version
pnpm list @sveltejs/kit
```

#### Database migration errors
```bash
# Check current migration version
cd backend
uv run alembic current

# View migration history
uv run alembic history

# Rollback one migration
uv run alembic downgrade -1

# Force to latest version (use with caution)
uv run alembic stamp head
```

#### API returns 401 Unauthorized
```bash
# Check if JWT token is valid
# Login again to get fresh token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"test123"}'

# Check JWT_SECRET in .env
cat .env | grep JWT_SECRET
```

#### CORS errors in browser
```bash
# Update ALLOWED_ORIGINS in backend .env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Restart backend after changing .env
docker compose restart backend
```

#### Qdrant vector search not working
```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# Check Qdrant collections
curl http://localhost:6333/collections

# Restart Qdrant
docker compose restart qdrant
```

### Performance Issues

#### Slow database queries
```sql
-- Check for missing indexes
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM campaigns WHERE status = 'active';
```

#### High memory usage
```bash
# Check container memory usage
docker stats

# Limit container memory in docker-compose.yml
services:
  backend:
    mem_limit: 512m
    memswap_limit: 1g
```

## 📚 Additional Resources

### Documentation
- **[UPDATED_ROADMAP_NOVEMBER_2025.md](./UPDATED_ROADMAP_NOVEMBER_2025.md)** - Complete development roadmap
- **[DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)** - Documentation navigation
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment guide (1,280 lines)
- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Complete API reference (1,800+ lines)
- **Interactive API Docs:** http://localhost:8000/docs

### Technology References
- **FastAPI:** https://fastapi.tiangolo.com/
- **SvelteKit:** https://kit.svelte.dev/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **Alembic:** https://alembic.sqlalchemy.org/
- **Pydantic:** https://docs.pydantic.dev/

### Community & Support
- Report issues in the project repository
- Check `/docs` folder for technical documentation
- Review `/backend/app/api` for API implementation examples
- See `/frontend/src/routes` for UI component examples

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a production application developed following the Stack 2026 architecture. For contributions:
1. Follow the existing code structure and patterns
2. Write tests for new features
3. Update documentation for API changes
4. Use Alembic for database schema changes
5. Follow TypeScript best practices in frontend
6. Maintain backwards compatibility

## 📊 Project Status

**Current Version:** 2.0.0
**Last Updated:** November 11, 2025
**Development Stage:** Week 12/12 Complete (100%)
**Production Ready:** All features complete, fully documented and ready for deployment
**Architecture:** Stack 2026 Compliant
**Total Implementation:** 20,400+ lines of code across 12 weeks

---

**Voice by Kraliki** - A comprehensive AI-powered call center platform with enterprise-grade features, built with modern technologies and best practices.
