# Voice by Kraliki SvelteKit Architecture Document

**Date**: 2025-09-30
**Status**: Planning Phase
**Goal**: Replace React frontend with SvelteKit while keeping Node.js backend intact

---

## 🎯 Architecture Goals

1. **Simplicity** - Reduce 75 React components to ~30 Svelte components
2. **Performance** - 50% smaller bundle, faster hydration
3. **Maintainability** - Clear patterns, no duplicate dashboards
4. **Real-time** - WebSocket + tRPC seamless integration
5. **Type Safety** - Full TypeScript + tRPC type inference

---

## 📊 Backend Analysis (Current Capabilities)

### tRPC Routers Available (22 total)
```typescript
Backend provides:
├── auth          - Login, register, session management
├── agent         - Agent CRUD, status updates, metrics
├── supervisor    - Call monitoring, analytics, team oversight
├── dashboard     - Overview stats, KPIs, real-time data
├── callApi       - Call management, history, controls
├── campaign      - Campaign CRUD, contact lists, automation
├── contact       - Contact management, import/export
├── telephony     - Twilio/Telnyx integration, dialing
├── analytics     - Reports, charts, performance metrics
├── sentiment     - Real-time sentiment analysis
├── agentAssist   - AI suggestions, knowledge base
├── ivr           - IVR flow management
├── team          - Team management, assignments
├── webhooks      - External integrations
├── payments      - Polar subscription integration
├── twilioWebhooks - Twilio callback handling
├── apm           - Performance monitoring
├── aiHealth      - AI service health checks
├── circuitBreaker - Service resilience monitoring
├── metrics       - Prometheus metrics
├── ai            - AI model management
└── callByok      - Bring Your Own Keys for AI
```

### Database Schema (Prisma)
- **User** - Auth, roles, profiles, BYOK keys
- **Organization** - Multi-tenancy
- **Team** - Team structure
- **Agent** - Agent status, skills, capacity
- **Call** - Call records, transcripts, recordings
- **Campaign** - Outbound campaigns, contact lists
- **Contact** - Contact management
- **CallQueue** - Queue management
- **Recording** - Call recordings (GDPR compliant)
- **Transcription** - Real-time transcripts
- **SentimentAnalysis** - AI sentiment tracking
- **IVRInteraction** - IVR flow tracking

### WebSocket Services
- Real-time call updates
- Live transcription streams
- Sentiment analysis updates
- Agent status broadcasts
- Queue status updates

### Key Services Available
- **AuthService** - JWT auth, session management
- **TelephonyService** - Twilio/Telnyx abstraction
- **AIAnalyticsService** - Call insights, sentiment
- **CampaignService** - Campaign automation
- **RedisService** - Caching, real-time state
- **QueueService** - RabbitMQ message queue
- **APMService** - Performance monitoring
- **MetricsService** - Prometheus metrics

---

## 🎨 Frontend Requirements Analysis

### User Roles & Views

#### 1. **AGENT Role** (Operator Dashboard)
**Primary tasks:**
- Handle incoming calls
- View current call info
- Access customer history
- Get AI-powered suggestions
- Control call (hold, transfer, hangup)
- Take notes
- View queue status

**Features needed:**
- Real-time call queue display
- Active call panel (with timer, customer info)
- AI agent assist panel (real-time suggestions)
- Customer sentiment indicator
- Quick actions (transfer, hold, hangup)
- Call history sidebar
- Knowledge base search
- Note-taking interface

#### 2. **SUPERVISOR Role** (Supervisor Cockpit)
**Primary tasks:**
- Monitor all active calls
- View team performance
- Listen to live calls
- Intervene in calls (whisper, barge)
- View real-time metrics
- Analyze sentiment trends
- Generate reports

**Features needed:**
- Live call monitoring grid
- Agent status overview
- Real-time metrics dashboard
- Sentiment analysis view
- Queue management
- Call recording playback
- Team performance charts
- Alert notifications

#### 3. **ADMIN Role** (Admin Dashboard)
**Primary tasks:**
- Manage users and teams
- Configure campaigns
- View analytics
- Manage subscriptions
- Configure integrations
- System health monitoring

**Features needed:**
- User management CRUD
- Campaign builder
- Analytics reports
- Subscription management (Polar)
- System metrics (APM)
- BYOK configuration
- IVR flow designer

### Common Features (All Roles)
- Login/logout
- Profile settings
- Dark/light theme
- Notifications
- Bug reporting
- Help/documentation

---

## 🏗️ SvelteKit Architecture Design

### Directory Structure
```
sveltekit-ui/
├── src/
│   ├── routes/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── +page.svelte
│   │   │   └── +layout.svelte          # Auth layout (no nav)
│   │   ├── (app)/
│   │   │   ├── operator/
│   │   │   │   ├── +page.svelte        # Operator dashboard
│   │   │   │   └── +page.ts            # Load data
│   │   │   ├── supervisor/
│   │   │   │   ├── +page.svelte        # Supervisor cockpit
│   │   │   │   └── +page.ts
│   │   │   ├── admin/
│   │   │   │   ├── +page.svelte        # Admin dashboard
│   │   │   │   ├── campaigns/
│   │   │   │   │   ├── +page.svelte    # Campaign list
│   │   │   │   │   └── [id]/+page.svelte # Campaign detail
│   │   │   │   ├── users/
│   │   │   │   │   └── +page.svelte    # User management
│   │   │   │   └── analytics/
│   │   │   │       └── +page.svelte    # Reports
│   │   │   ├── settings/
│   │   │   │   └── +page.svelte        # User settings
│   │   │   └── +layout.svelte          # App layout (with nav)
│   │   └── +page.svelte                # Landing/redirect
│   ├── lib/
│   │   ├── trpc/
│   │   │   ├── client.ts               # tRPC client setup
│   │   │   └── types.ts                # Generated types
│   │   ├── stores/
│   │   │   ├── auth.svelte.ts          # Auth state (Svelte 5 runes)
│   │   │   ├── calls.svelte.ts         # Active calls state
│   │   │   ├── agents.svelte.ts        # Agent status state
│   │   │   └── websocket.svelte.ts     # WebSocket connection
│   │   ├── components/
│   │   │   ├── shared/
│   │   │   │   ├── Button.svelte
│   │   │   │   ├── Card.svelte
│   │   │   │   ├── Modal.svelte
│   │   │   │   ├── Table.svelte
│   │   │   │   └── Loading.svelte
│   │   │   ├── operator/
│   │   │   │   ├── ActiveCallPanel.svelte
│   │   │   │   ├── CallQueue.svelte
│   │   │   │   ├── AgentAssist.svelte
│   │   │   │   └── CustomerInfo.svelte
│   │   │   ├── supervisor/
│   │   │   │   ├── LiveCallGrid.svelte
│   │   │   │   ├── AgentStatusGrid.svelte
│   │   │   │   ├── MetricsOverview.svelte
│   │   │   │   └── SentimentChart.svelte
│   │   │   └── admin/
│   │   │       ├── UserTable.svelte
│   │   │       ├── CampaignBuilder.svelte
│   │   │       └── AnalyticsChart.svelte
│   │   ├── utils/
│   │   │   ├── format.ts               # Date, number formatters
│   │   │   ├── validation.ts           # Form validation
│   │   │   └── constants.ts            # App constants
│   │   └── types/
│   │       └── app.d.ts                # App-wide types
│   ├── app.html                        # HTML template
│   └── app.css                         # Global styles (Tailwind)
├── static/
│   ├── favicon.png
│   └── assets/
├── package.json
├── svelte.config.js
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

---

## 🔌 State Management Strategy

### Svelte 5 Runes (Primary)
Use Svelte 5's new reactivity system for local and shared state:

```typescript
// lib/stores/auth.svelte.ts
import { trpc } from '$lib/trpc/client';

class AuthStore {
  user = $state<User | null>(null);
  loading = $state(false);

  async login(email: string, password: string) {
    this.loading = true;
    try {
      const result = await trpc.auth.login.mutate({ email, password });
      this.user = result.user;
    } finally {
      this.loading = false;
    }
  }

  logout() {
    this.user = null;
  }
}

export const auth = new AuthStore();
```

### tRPC Query Cache (Secondary)
Let tRPC handle server state caching:
- Dashboard metrics
- Call lists
- Agent lists
- Campaign data

### WebSocket Store (Real-time)
```typescript
// lib/stores/websocket.svelte.ts
class WebSocketStore {
  socket = $state<WebSocket | null>(null);
  connected = $state(false);

  connect(token: string) {
    this.socket = new WebSocket(`ws://localhost:3010/ws?token=${token}`);
    this.socket.onopen = () => this.connected = true;
    this.socket.onmessage = (event) => this.handleMessage(event);
  }

  private handleMessage(event: MessageEvent) {
    const data = JSON.parse(event.data);
    // Update relevant stores (calls, agents, etc.)
  }
}

export const ws = new WebSocketStore();
```

---

## 🔄 Real-time Data Flow Architecture

### Integration Pattern
```
User Action (Svelte)
    ↓
tRPC Mutation (HTTP)
    ↓
Backend Processing
    ↓
WebSocket Broadcast
    ↓
All Connected Clients Update (Svelte stores)
```

### Example: Call Status Change
1. Agent clicks "Accept Call" button
2. Svelte calls `trpc.callApi.accept.mutate({ callId })`
3. Backend updates database via Prisma
4. Backend broadcasts via WebSocket: `{ type: 'call:accepted', callId, agentId }`
5. All supervisors see real-time update in their dashboard

### WebSocket Message Types
```typescript
type WSMessage =
  | { type: 'call:created', call: Call }
  | { type: 'call:updated', call: Call }
  | { type: 'call:ended', callId: string }
  | { type: 'agent:status', agentId: string, status: AgentStatus }
  | { type: 'transcript:chunk', callId: string, text: string }
  | { type: 'sentiment:update', callId: string, sentiment: Sentiment }
  | { type: 'queue:updated', queue: CallQueue };
```

---

## 🔐 Authentication Flow

### Login Flow
```
1. User enters email/password
2. POST /trpc/auth.login (via tRPC)
3. Backend validates credentials
4. Backend returns JWT token + user data
5. Frontend stores token in httpOnly cookie (set by backend)
6. Frontend stores user in auth store
7. All subsequent requests include cookie automatically
```

### Protected Routes
```typescript
// routes/(app)/+layout.ts
import { redirect } from '@sveltejs/kit';
import { auth } from '$lib/stores/auth.svelte';

export async function load() {
  if (!auth.user) {
    throw redirect(302, '/login');
  }

  return { user: auth.user };
}
```

### Role-based Access
```typescript
// routes/(app)/admin/+layout.ts
export async function load({ parent }) {
  const { user } = await parent();

  if (user.role !== 'ADMIN') {
    throw redirect(302, '/operator');
  }
}
```

---

## 📦 Component Hierarchy & Reusability

### Design Principles
1. **Atomic Design** - Atoms → Molecules → Organisms → Templates
2. **Single Responsibility** - Each component does ONE thing
3. **Composition over Props Drilling** - Use context when needed
4. **NO Duplicates** - ONE component per concept

### Component Categories

#### Atoms (Basic UI elements)
- `Button.svelte` - All button variants
- `Input.svelte` - Text inputs
- `Badge.svelte` - Status badges
- `Avatar.svelte` - User avatars
- `Icon.svelte` - Icon wrapper
- `Spinner.svelte` - Loading spinner

#### Molecules (Compound elements)
- `Card.svelte` - Container with header/body/footer
- `Modal.svelte` - Dialog/overlay
- `Dropdown.svelte` - Dropdown menu
- `SearchBox.svelte` - Search input with icon
- `StatsCard.svelte` - Metric display card
- `StatusDot.svelte` - Status indicator with label

#### Organisms (Complex components)
- `CallQueue.svelte` - Queue display table
- `ActiveCallPanel.svelte` - Active call info + controls
- `AgentStatusGrid.svelte` - Grid of agent cards
- `MetricsOverview.svelte` - Dashboard metrics section
- `SentimentChart.svelte` - Real-time sentiment visualization
- `CampaignBuilder.svelte` - Campaign creation form

#### Templates (Page layouts)
- `DashboardTemplate.svelte` - Standard dashboard layout
- `TwoColumnTemplate.svelte` - Sidebar + main content
- `EmptyState.svelte` - No data placeholder

### Reusability Strategy
```svelte
<!-- GOOD: Flexible, composable -->
<Card>
  <svelte:fragment slot="header">
    <h2>Active Calls</h2>
  </svelte:fragment>
  <CallQueue calls={activeCalls} />
</Card>

<!-- BAD: Rigid, specific -->
<ActiveCallsCard calls={activeCalls} />
```

---

## 🎨 Styling Strategy

### Tailwind CSS (Primary)
- Utility-first approach
- Consistent spacing/colors
- Responsive by default

### CSS Variables (Theme)
```css
/* app.css */
:root {
  --color-primary: #3b82f6;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-danger: #ef4444;
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f3f4f6;
  --color-text-primary: #111827;
  --color-text-secondary: #6b7280;
}

[data-theme="dark"] {
  --color-bg-primary: #1f2937;
  --color-bg-secondary: #111827;
  --color-text-primary: #f9fafb;
  --color-text-secondary: #d1d5db;
}
```

### Component Styles (Scoped)
```svelte
<style>
  /* Scoped to component, no conflicts */
  .call-panel {
    @apply flex flex-col gap-4 p-4 bg-white dark:bg-gray-800 rounded-lg shadow;
  }
</style>
```

---

## 🚀 Performance Optimizations

### Code Splitting
- Automatic route-based splitting (SvelteKit default)
- Lazy load admin features: `const CampaignBuilder = await import('$lib/components/admin/CampaignBuilder.svelte');`

### Data Loading Strategy
- **SSR for initial load** - Fast first paint
- **Client-side tRPC** - Real-time updates
- **WebSocket for push** - No polling

### Bundle Size Targets
- Initial bundle: < 100KB (gzipped)
- Route chunks: < 50KB each
- Total JS: < 300KB (vs React: ~600KB)

---

## 🧪 Testing Strategy

### Unit Tests (Vitest)
- Pure functions (utils, formatters)
- Store logic
- tRPC client mocks

### Component Tests (Playwright Component Testing)
- Component rendering
- User interactions
- Accessibility

### E2E Tests (Playwright)
- Complete user flows
- Authentication
- Role-based access
- Real-time updates

---

## 📈 Migration Plan

### Phase 1: Foundation (Week 1)
- [ ] Set up SvelteKit project in `sveltekit-ui/`
- [ ] Configure tRPC client
- [ ] Build auth flow (login → dashboard)
- [ ] Create base components (Button, Card, Modal)
- [ ] Implement layout system

### Phase 2: Operator Dashboard (Week 1)
- [ ] Active call panel
- [ ] Call queue display
- [ ] Agent assist panel
- [ ] Customer info sidebar
- [ ] WebSocket integration
- [ ] **DECISION POINT**: Compare with React version

### Phase 3: Supervisor Cockpit (Week 2)
- [ ] Live call monitoring grid
- [ ] Agent status overview
- [ ] Real-time metrics
- [ ] Sentiment analysis view
- [ ] Queue management

### Phase 4: Admin Dashboard (Week 2-3)
- [ ] User management
- [ ] Campaign builder
- [ ] Analytics reports
- [ ] Subscription management
- [ ] System monitoring

### Phase 5: Testing & Launch (Week 3)
- [ ] E2E test suite
- [ ] Performance audit
- [ ] Accessibility audit
- [ ] Deploy alongside React
- [ ] A/B test with users
- [ ] Full cutover

---

## 🔍 Success Metrics

### Code Metrics
- **Component count**: 75 → 30 (60% reduction)
- **Bundle size**: 600KB → 300KB (50% reduction)
- **Lines of code**: ~15,000 → ~7,500 (50% reduction)

### Performance Metrics
- **Initial load**: < 2s (vs React: ~4s)
- **Time to Interactive**: < 3s (vs React: ~6s)
- **Lighthouse score**: > 90 (vs React: ~75)

### Developer Experience
- **Build time**: < 10s (vs React: ~30s)
- **Hot reload**: < 1s (vs React: ~3s)
- **Type safety**: 100% (tRPC inference)

---

## ⚠️ Risk Mitigation

### Risk 1: Repeat Same Mistakes
**Mitigation**:
- Strict component approval process
- ONE component per concept (no duplicates)
- Code review before merge

### Risk 2: Backend Changes Required
**Mitigation**:
- Keep backend untouched
- Use existing tRPC routers as-is
- WebSocket protocol stays same

### Risk 3: User Disruption
**Mitigation**:
- Run both frontends in parallel
- Gradual rollout (10% → 50% → 100%)
- Easy rollback (nginx config change)

### Risk 4: Missing Features
**Mitigation**:
- Feature parity checklist
- E2E tests for all critical flows
- Beta testing with real users

---

## 📚 Technology Stack Summary

### Frontend
- **Framework**: SvelteKit 2.0
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: Svelte 5 runes + tRPC cache
- **Real-time**: WebSocket + Svelte stores
- **Testing**: Vitest + Playwright
- **Build**: Vite

### Backend (Unchanged)
- **Framework**: Fastify
- **API**: tRPC
- **Database**: PostgreSQL + Prisma
- **Cache**: Redis
- **Queue**: RabbitMQ
- **Telephony**: Twilio/Telnyx
- **Monitoring**: OpenTelemetry + Sentry

---

## 🎯 Next Steps

1. **Review this architecture** - Approve/modify design decisions
2. **Create PoC** - Build operator dashboard (Week 1 goal)
3. **Compare metrics** - React vs Svelte side-by-side
4. **Go/No-Go decision** - Continue or fix React instead

---

**Document Version**: 1.0
**Last Updated**: 2025-09-30
**Author**: Claude Code + User
**Status**: Pending Approval
