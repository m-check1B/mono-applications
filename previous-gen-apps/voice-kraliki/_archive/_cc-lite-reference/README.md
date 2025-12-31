# Voice by Kraliki (Communications Module)

**Ocelot Platform Communications Module** - Voice AI calling, campaigns, and transcription

[![Stack 2026](https://img.shields.io/badge/Stack-2026-brightgreen)]()
[![Compliance](https://img.shields.io/badge/Compliance-95%2F100-brightgreen)]()
[![Security](https://img.shields.io/badge/Security-95%2F100-brightgreen)]()
[![Port](https://img.shields.io/badge/Port-3018-blue)]()

Professional AI call center platform built with Stack 2026 standards: Python + FastAPI backend, SvelteKit frontend, Ed25519 JWT authentication.

## 📋 Current Status

**Stack 2026 Compliance**: 95/100
**Security Score**: 95/100
**Port**: 3018
**NPM Package**: `@ocelot-apps/cc-lite`

### ✅ Week 1-2 Complete (October 2025)
- Ed25519 JWT authentication
- RabbitMQ event publishing (5 event types)
- NPM package export
- Platform module integration
- Integration tests (100% coverage for new code)

### 🚧 Week 3-4 In Progress
- [ ] Mobile-first PWA design
- [ ] Czech + English i18n
- [ ] Code cleanup (TypeScript removal)
- [ ] Final route migration

## 🎯 Product Overview

Voice by Kraliki follows a **focused simplicity** approach:
- **Essential Features Only** - Core call center capabilities without bloat
- **AI-Enhanced Operations** - Real-time transcription, sentiment analysis, agent assistance
- **Multi-Language Support** - English, Spanish, and Czech with automatic detection
- **Role-Based Dashboards** - Tailored interfaces for operators, supervisors, and administrators
- **Production Ready** - Comprehensive testing, security, and deployment automation

## 🚀 Quick Start

### Development (Local)
```bash
# Install dependencies
pnpm install

# Start local services (Postgres + Redis)
# (Use `pnpm db:cluster:start` instead when Docker isn't available, e.g. on Replit)
pnpm dev:services

# Setup database (generate client, migrate, seed demo users)
pnpm db:setup

# Start development servers
pnpm dev         # Frontend on http://127.0.0.1:3007
pnpm dev:server  # Backend on http://127.0.0.1:3010
```

### Production (Docker) - MANDATORY
```bash
# Build and run with Docker Compose (REQUIRED for production)
docker compose -f infra/docker/production.yml up -d

# Or using existing PM2 inside Docker
docker build -t cc-lite:latest .
docker run -d --name cc-lite -p 80:3010 cc-lite:latest
```

**📖 Docker Policy**: All production deployments MUST use Docker. See [Docker Deployment Policy](./docs/DOCKER_DEPLOYMENT_POLICY.md) for mandatory requirements.

### Demo Access
- **Dashboard**: http://127.0.0.1:3007/operator - Operator dashboard
- **Supervisor**: http://127.0.0.1:3007/supervisor - Supervisor cockpit
- **Login**: Use universal test account (see [Authentication](#authentication))

## 📚 Documentation

- [Documentation Hub](./docs/README.md) – consolidated index for API, architecture, deployment, development, security, testing, and user guides.

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- **Framework**: Vite + React 18 + TypeScript
- **UI Library**: NextUI + Tailwind CSS
- **State Management**: React Context + tRPC React Query
- **Routing**: React Router
- **Testing**: Playwright (multi-browser)

**Backend:**
- **Framework**: Fastify + TypeScript
- **API**: tRPC (18 routers implemented)
- **Database**: PostgreSQL + Prisma ORM
- **Authentication**: JWT with Stack 2025 auth-core
- **Real-time**: WebSockets + Server-Sent Events

**AI & Telephony:**
- **Voice Providers**: Twilio, Telnyx (via @unified/telephony)
- **Speech Processing**: Deepgram (STT/TTS)
- **AI Models**: OpenAI GPT-4, Google Gemini
- **Language Detection**: Custom multi-language engine

### Project Structure

```
cc-lite/
├── src/                      # Frontend (React + Vite)
│   ├── components/          # UI components
│   │   ├── dashboard/       # Dashboard components
│   │   ├── monitoring/      # Live monitoring
│   │   ├── agent/          # Agent assistance
│   │   └── sentiment/      # Sentiment analysis
│   ├── contexts/           # React contexts
│   ├── services/           # Frontend services
│   └── pages/              # React Router pages
│
├── server/                  # Backend (Fastify)
│   ├── trpc/               # tRPC API (18 routers)
│   │   └── routers/        # Individual route modules
│   ├── services/           # Business logic
│   ├── core/               # AI/Voice integrations
│   └── routes/             # Legacy REST (being migrated)
│
├── prisma/                 # Database schema & migrations
├── tests/                  # Comprehensive test suite
│   ├── e2e/               # Playwright end-to-end
│   ├── integration/        # API integration tests
│   └── unit/              # Unit tests
│
└── docs/                   # Organized documentation
    ├── api/               # API documentation
    ├── architecture/      # System design
    ├── deployment/        # Production deployment
    ├── development/       # Development guides
    ├── security/          # Security documentation
    └── user-guides/       # User documentation
```

## 🔧 Core Features

### 📞 Call Management
- **Real-time Call Control**: Answer, hold, transfer, mute operations
- **Queue Management**: Intelligent call routing and distribution
- **Call Recording**: Automated recording with compliance features
- **Live Monitoring**: Real-time call status and agent monitoring

### 🤖 AI-Powered Features
- **Real-time Transcription**: Live call transcription with speaker detection
- **Sentiment Analysis**: Real-time emotion detection and alerting
- **Agent Assistance**: AI-powered suggestions and context information
- **Conversation Intelligence**: Extract insights and action items
- **Predictive Analytics**: Call outcome prediction and optimization

### 🌐 Multi-Language Support

| Language | Code | Voice Provider | STT Provider | Voices Available | Status |
|----------|------|---------------|--------------|------------------|--------|
| **English** | en | Deepgram | Deepgram | 14+ voices | ✅ Production |
| **Spanish** | es | Deepgram | Deepgram | 9+ voices | ✅ Production |
| **Czech** | cs | ElevenLabs | Deepgram | 2+ voices | ✅ Production |

**Language Features:**
- Automatic language detection from text and audio
- Dynamic voice service routing based on language
- Real-time language switching during conversations
- Regional accent and dialect support
- Language usage analytics and reporting

### 👥 Role-Based Dashboards

**Operator Dashboard** (`/operator`)
- Active call management interface
- Real-time queue status
- Quick action buttons
- Performance metrics
- Agent status controls

**Supervisor Dashboard** (`/supervisor`)
- Live call monitoring
- Team performance overview
- Real-time transcript viewing
- Alert management
- Resource allocation

**Administrator Dashboard** (`/admin`)
- System configuration
- User management
- Analytics and reporting
- Campaign management
- System health monitoring

## 🔌 API Architecture

### tRPC Routers (18 Active)

**Core Operations:**
- `auth.ts` - Authentication and session management
- `call.ts` - Call control and management
- `agent.ts` - Agent status and controls
- `dashboard.ts` - Dashboard data and metrics

**AI & Analytics:**
- `ai.ts` - AI model interactions
- `sentiment.ts` - Sentiment analysis engine
- `agent-assist.ts` - Real-time agent assistance
- `analytics.ts` - Performance analytics

**Communication:**
- `telephony.ts` - Phone system integration
- `twilio-webhooks.ts` - Twilio webhook handling
- `webhooks.ts` - General webhook management

**Management:**
- `campaign.ts` - Campaign management
- `contact.ts` - Contact management
- `team.ts` - Team organization
- `supervisor.ts` - Supervisor functions

**System:**
- `ivr.ts` - Interactive voice response
- `payments.ts` - Billing integration
- `call-byok.ts` - Bring-your-own-key features

### REST API (Legacy - Being Migrated)
Limited REST endpoints remaining for legacy compatibility. All new features use tRPC.

## 🔒 Authentication

### Universal Test Account
```yaml
Email: test.assistant@stack2025.com
Password: Stack2025!Test@Assistant#Secure$2024
Role: TESTER_UNIVERSAL
Features: All features enabled
```

### Local Development Accounts
```yaml
# Administrator
Email: admin@cc-light.local
Password: [Set via DEFAULT_ADMIN_PASSWORD env var]

# Supervisor
Email: supervisor@cc-light.local
Password: [Set via DEFAULT_SUPERVISOR_PASSWORD env var]

# Agent
Email: agent1@cc-light.local
Password: [Set via DEFAULT_AGENT_PASSWORD env var]
```

## 🧪 Testing

### Comprehensive Test Suite

```bash
# All tests
pnpm test

# End-to-end tests (Playwright)
pnpm test:e2e                    # All browsers
pnpm test:e2e:auth              # Authentication workflow
pnpm test:e2e:dashboard         # Dashboard functionality
pnpm test:accessibility         # Accessibility compliance
pnpm test:performance           # Performance benchmarks

# Integration tests
pnpm test:integration           # API integration
pnpm test:integration:trpc      # tRPC endpoints
pnpm test:integration:websocket # Real-time features

# Multi-language testing
pnpm test:multi-language        # Language detection & routing
pnpm test:voice                 # Voice service integration

# Security testing
pnpm test:security              # Security compliance
```

### Testing Coverage
- ✅ **Cross-browser**: Chrome, Firefox, Safari, Mobile
- ✅ **User Flows**: Complete workflows tested with user agents
- ✅ **API Testing**: All tRPC endpoints validated
- ✅ **Security**: Authentication, authorization, input validation
- ✅ **Performance**: Load testing and optimization
- ✅ **Accessibility**: WCAG 2.1 compliance testing

## 🚀 Production Deployment

### Quick Production Setup

```bash
# Generate secrets
pnpm run secrets:generate

# Configure environment
cp .env.template .env.production
# Edit .env.production with your secrets

# Deploy with PM2
pnpm run pm2:deploy
```

### Production Configuration

**Ports (Stack 2025 Standard):**
- Frontend: `127.0.0.1:3007` (Vite preview)
- Backend: `127.0.0.1:3010` (Fastify API)

**Services:**
- **Database**: PostgreSQL on `127.0.0.1:5432`
- **Cache**: Redis on `127.0.0.1:6379` (optional)
- **Process Manager**: PM2 with ecosystem configuration

**Environment Variables:**
```bash
# Core
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@127.0.0.1:5432/cc_light_prod

# Authentication
JWT_SECRET=[generated]
COOKIE_SECRET=[generated]

# Telephony
TELEPHONY_PROVIDER=twilio|telnyx
TELEPHONY_ENABLED=true
TWILIO_ACCOUNT_SID=[your-sid]
TWILIO_AUTH_TOKEN=[your-token]

# AI Services
OPENAI_API_KEY=[your-key]
DEEPGRAM_API_KEY=[your-key]
```

### Production Health Checks

```bash
# Validate environment
pnpm run env:validate:production

# Startup validation
pnpm run startup:validate

# PM2 monitoring
pnpm run pm2:status
pnpm run pm2:logs
```

## 📖 Documentation

All documentation is organized in the `docs/` directory:

### 📋 [Documentation Index](./docs/INDEX.md)
Complete overview of all available documentation with quick navigation.

### 🔧 Quick References
- **[API Documentation](./docs/api/API_DOCUMENTATION.md)** - Complete tRPC API reference
- **[Production Deployment Guide](./docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md)** - Step-by-step deployment
- **[Security Documentation](./docs/security/)** - Security best practices and compliance
- **[Multi-Language Operations](./docs/development/MULTI_LANGUAGE_OPERATIONS.md)** - Language support guide

### 🏗️ Architecture & Design
- **[AI Enhanced Architecture](./docs/architecture/AI_ENHANCED_ARCHITECTURE.md)** - System architecture
- **[Design System](./docs/architecture/DESIGN_SYSTEM.md)** - UI components and patterns
- **[Integration Guide](./docs/architecture/INTEGRATION_WITH_HUB_FAMILY.md)** - Stack 2025 integration

## 🔐 Security

### Security Features
- **JWT Authentication** with Ed25519 signatures
- **Role-based Access Control** (RBAC)
- **API Rate Limiting** and request validation
- **WebSocket Security** with authentication
- **Cookie Security** with httpOnly and secure flags
- **Input Validation** with Zod schemas
- **SQL Injection Protection** via Prisma ORM

### Compliance
- **Data Privacy**: GDPR-compliant data handling
- **Call Recording**: Consent management and secure storage
- **Audit Logging**: Comprehensive security event logging
- **Vulnerability Scanning**: Automated security testing

## 🔄 Development Workflow

### Contributing Guidelines

1. **Create Feature Branch**: `git checkout -b feature/your-feature`
2. **Implement Changes**: Follow TypeScript and testing standards
3. **Run Tests**: `pnpm test` - ensure all tests pass
4. **Test Multi-Language**: `pnpm test:multi-language`
5. **Security Check**: `pnpm test:security`
6. **Create PR**: Include screenshots and test results

### Code Standards
- **TypeScript**: Strict mode enabled
- **ESLint**: Configured for React and Node.js
- **Prettier**: Consistent code formatting
- **tRPC**: All new APIs must use tRPC
- **Testing**: Comprehensive test coverage required

## 🎯 Roadmap

### Current Status (v2.0.0 Beta)
- ✅ Core call management features
- ✅ Multi-language support (EN/ES/CS)
- ✅ AI-powered features (transcription, sentiment)
- ✅ Role-based dashboards
- ✅ Production deployment automation
- ✅ Comprehensive testing suite

### Upcoming Features
- **Enhanced AI Models**: Integration with latest language models
- **Advanced Analytics**: Predictive call analytics
- **Mobile Application**: Native mobile operator app
- **Additional Languages**: French, German, Italian support
- **Integration Marketplace**: Third-party service integrations

## 📄 License

Proprietary - All rights reserved

---

## 🐳 Production Deployment

### Mandatory Docker Deployment

**All production deployments MUST use Docker** as per Stack 2025 policy. This ensures consistency, security, and scalability.

#### Recommended Setup: Hetzner Cloud + Docker

```bash
# Production deployment on Hetzner CCX13 ($27/month)
# 1. Provision Hetzner Cloud VM
# 2. Clone repository and configure environment
git clone https://github.com/your-org/cc-lite.git
cd cc-lite
cp .env.example .env.production

# 3. Deploy with Docker Compose
docker compose -f infra/docker/production.yml up -d

# 4. Setup SSL with Let's Encrypt
./scripts/setup-ssl.sh

# 5. Configure monitoring
docker compose -f monitoring/docker compose.yml up -d
```

#### Architecture Options

| Deployment Type | Monthly Cost | Concurrent Users | Setup Complexity |
|-----------------|-------------|------------------|------------------|
| **Single VM + Docker** | $27 | 10-50 | Simple |
| **Load Balanced VMs** | $80 | 50-200 | Moderate |
| **Docker Swarm** | $150 | 200-500 | Moderate |
| **Kubernetes Cluster** | $200+ | 500+ | Complex |

#### Why Docker on VM?

1. **Cost Efficiency**: 15-20x cheaper than AWS/Azure ($27 vs $535/month)
2. **Performance**: Only 3-5% overhead vs bare metal
3. **Portability**: Move to any cloud provider without code changes
4. **Consistency**: Identical environments across dev/staging/production
5. **PM2 Integration**: Process management inside containers

#### Required Docker Files

- `Dockerfile` - Multi-stage build with PM2 runtime
- `docker compose.yml` - Development configuration
- `infra/docker/production.yml` - Production overrides
- `ecosystem.config.js` - PM2 process management

For detailed deployment instructions, see:
- [Docker Deployment Policy](./docs/DOCKER_DEPLOYMENT_POLICY.md)
- [Production Deployment Guide](./docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md)
- [Infrastructure Analysis](./docs/deployment/INFRASTRUCTURE_DEPLOYMENT_ANALYSIS.md)

## 🆘 Support

### Getting Help
- **Documentation**: Start with [Documentation Index](./docs/INDEX.md)
- **API Reference**: See [API Documentation](./docs/api/API_DOCUMENTATION.md)
- **Deployment Issues**: Check [Production Deployment Guide](./docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md)
- **Security Concerns**: Review [Security Documentation](./docs/security/)

### Development Support
- **Setup Issues**: Follow [Developer Quick Start](./docs/development/developer-quickstart-security.md)
- **Testing Problems**: See [Testing Policy](./docs/development/TESTING_POLICY.md)
- **Feature Implementation**: Check [Implementation Coordination](./docs/development/IMPLEMENTATION_COORDINATION.md)

---

**Voice by Kraliki v2.0.0** - Professional AI call center platform built for modern operations with Stack 2025 standards.
