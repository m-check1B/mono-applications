# Track 7: Command Center Shell - Implementation Guide

This document provides a comprehensive guide to the Track 7 Command Center Shell implementation, which creates a unified AI-First interface with seamless tab navigation and integrated workflow management.

## Overview

Track 7 delivers:
- **Unified Shell Navigation**: Assistant, Work, and Insights tabs with mobile-responsive design
- **UnifiedCanvas Integration**: Seamless integration of Track 3's II-Agent canvas
- **Workflow Management**: Integrated workflow drawer for orchestration inspection
- **Execution Management**: Artifact drawer for task/knowledge editing
- **Hybrid Telemetry**: Enhanced insights with BYOK status indicators
- **Responsive Design**: Mobile-first layout with adaptive breakpoints

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AssistantShell (Layout)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Navigation: Assistant | Work | Insights | Settings     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ASSISTANT TAB (dashboard/+page.svelte)                  │  │
│  │  ┌────────────────────────┐  ┌─────────────────────────┐ │  │
│  │  │  UnifiedCanvas         │  │  Status + Feed Panel    │ │  │
│  │  │  - II-Agent Mode       │  │  - Account Info         │ │  │
│  │  │  - Orchestrated Mode   │  │  - BYOK Status          │ │  │
│  │  │  - Deterministic Mode  │  │  - Workflow Preview     │ │  │
│  │  │  - Voice Input         │  │  - Execution Feed       │ │  │
│  │  └────────────────────────┘  └─────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  WORK TAB (dashboard/work/+page.svelte)                  │  │
│  │  Tabs: Knowledge | Tasks | Calendar                      │  │
│  │  - Knowledge: Type-based item management                 │  │
│  │  - Tasks: Grid view with quick send-to-assistant         │  │
│  │  - Calendar: Link to full calendar page                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  INSIGHTS TAB (dashboard/insights/+page.svelte)          │  │
│  │  - Quick Stats Summary (Account, BYOK, Orchestrations)   │  │
│  │  - Usage Metrics & Remaining Credits                     │  │
│  │  - Subscription Status & Renewal                         │  │
│  │  - Orchestration Telemetry & Confidence                  │  │
│  │  - Route Breakdown & Recent Runs                         │  │
│  │  - Usage History Visualization                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
┌──────────────────────┐           ┌──────────────────────┐
│   WorkflowDrawer     │           │  ExecutionDrawer     │
│  (from Track 3)      │           │  (from Track 3)      │
│  - Workflow steps    │           │  - Task editing      │
│  - Artifacts         │           │  - Knowledge editing │
│  - Approve/Revise    │           │  - Status toggle     │
└──────────────────────┘           └──────────────────────┘
```

## Components

### 1. AssistantShell (`/frontend/src/lib/components/assistant/AssistantShell.svelte`)

Main layout component providing navigation and shell structure.

#### Features
- **Gradient Background**: Radial gradients with glass morphism effect
- **Desktop Rail**: Icon-based vertical navigation (hidden on mobile)
- **Mobile TabBar**: Bottom navigation for thumb-friendly access
- **User Profile**: Avatar and logout in rail footer
- **Responsive**: Breakpoint-aware layout (md:flex, hidden md:flex, etc.)

#### Props
```typescript
export let navItems: AssistantNavItem[] = [];
export let currentPath = '';
export let user: { full_name?: string; email?: string } | null = null;
export let onLogout: (() => void | Promise<void>) | null = null;
```

### 2. Assistant Tab (`/frontend/src/routes/dashboard/+page.svelte`)

Primary landing page integrating UnifiedCanvas from Track 3.

#### Key Changes
- **UnifiedCanvas Integration**: Replaced `AssistantConversation` with `UnifiedCanvas`
- **assistantStore Integration**: Uses centralized state from Track 3
- **II-Agent Support**: Handles session initialization and WebSocket events
- **Workflow Management**: Approve/revise workflow decisions via API
- **Execution Feed**: Displays recent tasks/knowledge with "Send to Assistant" CTAs

#### Event Handlers
```typescript
// II-Agent session initialization
async function handleRequestIIAgentSession()

// Workflow decision handlers
async function handleWorkflowApprove(event: CustomEvent)
async function handleWorkflowRevise(event: CustomEvent)

// Execution entry save
async function handleExecutionSave(event: CustomEvent)

// Deterministic/Orchestrated fallback
async function handleSend(event: CustomEvent)
```

#### State Management
```typescript
// Reactive bindings to assistantStore
$: composerMode = $assistantStore.composerState.mode;
$: useOrchestrator = composerMode === 'orchestrated';
```

### 3. Work Tab (`/frontend/src/routes/dashboard/work/+page.svelte`)

Multi-tab view for knowledge, tasks, and calendar management.

#### Tabs
1. **Knowledge Tab**
   - Type-based filtering (All, Notes, Ideas, Plans, etc.)
   - Inline item creation and editing
   - "Send to Assistant" for each item
   - Clipboard copy for context sharing

2. **Tasks Tab**
   - Grid layout (1/2/3 columns responsive)
   - Status/priority color coding
   - Quick send-to-assistant action
   - Links to full tasks page

3. **Calendar Tab**
   - Placeholder with link to `/dashboard/calendar`
   - Future: Embed calendar widget

#### Integration Points
```typescript
import { knowledgeStore } from '$lib/stores/knowledge';
import { tasksStore } from '$lib/stores/tasks';

// Load data on mount
onMount(async () => {
  await knowledgeStore.loadItemTypes();
  await knowledgeStore.loadKnowledgeItems();
  await tasksStore.loadTasks();
});
```

### 4. Insights Tab (`/frontend/src/routes/dashboard/insights/+page.svelte`)

Enhanced telemetry dashboard with BYOK status.

#### Enhancements
- **Quick Stats Summary Bar**: Gradient banner with Account/BYOK/Orchestrations
- **Visual Loading State**: Spinner with descriptive text
- **Assistant Integration**: All sections have "Ask assistant" buttons
- **Data Visualization**: Usage, subscription, orchestration metrics

#### Data Sources
```typescript
const [usage, subscription, telemetry] = await Promise.all([
  api.settings.getUsageStats(),
  api.billing.subscriptionStatus(),
  api.ai.telemetrySummary()
]);
```

### 5. MobileTabBar (`/frontend/src/lib/components/assistant/MobileTabBar.svelte`)

Bottom navigation for mobile devices.

#### Features
- Fixed positioning at bottom
- Icon + label for each nav item
- Active state highlighting
- Swipe-friendly targets (44px+)

## Responsive Design

### Breakpoints
- **Mobile**: 0-767px (single column, bottom tabs)
- **Tablet**: 768px-1279px (slim rail, adjusted grid)
- **Desktop**: 1280px+ (full rail, side-by-side panels)

### Mobile Optimizations
1. **AssistantShell**
   - Hide desktop rail (`hidden md:flex`)
   - Show mobile tab bar (`block md:hidden`)
   - Full-width content padding

2. **UnifiedCanvas**
   - Stacked layout (no side panels on mobile)
   - Bottom-sheet composer
   - Full-screen drawers

3. **Work Tab**
   - Tabs scroll horizontally on overflow
   - Grid collapses to single column
   - Touch-friendly tap targets

4. **Insights Tab**
   - Stats summary wraps on mobile
   - Cards stack vertically
   - Charts adapt to width

## Integration with Track 3

### UnifiedCanvas Usage
```svelte
<UnifiedCanvas
  bind:this={unifiedCanvasRef}
  bind:inputMessage
  {quickPrompts}
  {isRecording}
  {isProcessingAudio}
  {supportsRecording}
  {voiceProvider}
  {voiceStatus}
  {recordingError}
  {uploadError}
  {models}
  on:send={handleSend}
  on:record={startRecording}
  on:stop={() => stopRecording()}
  on:upload={(event) => handleFileChange(event.detail)}
  on:provider={(event) => handleVoiceProviderChange(event.detail)}
  on:requestIIAgentSession={handleRequestIIAgentSession}
  on:workflowApprove={handleWorkflowApprove}
  on:workflowRevise={handleWorkflowRevise}
  on:executionSave={handleExecutionSave}
/>
```

### Workflow & Execution Drawers
- Managed internally by UnifiedCanvas
- State stored in `assistantStore.drawerState`
- Events dispatched to parent for API calls

## Data Flow

### 1. Message Flow (II-Agent)
```
User Input → UnifiedCanvas → IIAgentClient → WebSocket
                ↓
          assistantStore.addMessage()
                ↓
          UnifiedCanvas re-renders
                ↓
          Auto-scroll to bottom
```

### 2. Workflow Flow (Orchestrated)
```
User Input → handleSend → api.ai.orchestrateTask()
                ↓
          assistantStore.addWorkflow()
                ↓
          Workflow displayed in sidebar
                ↓
          User clicks "Approve" → handleWorkflowApprove
                ↓
          api.ai.recordWorkflowDecision()
```

### 3. Execution Flow
```
Tool Call (create_task) → IIAgentClient extracts
                ↓
          assistantStore.addExecutionEntry()
                ↓
          Displayed in execution feed
                ↓
          User clicks entry → assistantStore.openExecutionDrawer()
                ↓
          ExecutionDrawer shows details
```

## Testing Checklist

### Manual Testing
- [ ] Assistant tab loads with UnifiedCanvas
- [ ] II-Agent mode connects and streams responses
- [ ] Orchestrated mode creates workflows
- [ ] Deterministic mode calls /ai/chat
- [ ] Voice recording works (if browser supports)
- [ ] Workflow drawer opens on "View Details"
- [ ] Workflow approval/revision updates state
- [ ] Execution drawer opens from feed entries
- [ ] Task editing saves via drawer
- [ ] Knowledge editing saves via drawer
- [ ] Work tab switches between Knowledge/Tasks/Calendar
- [ ] Insights tab displays usage/subscription/telemetry
- [ ] BYOK status shows correctly
- [ ] Mobile layout uses bottom tabs
- [ ] Desktop layout uses side rail
- [ ] Responsive grid adjusts columns

### Automated Testing (Future)
```typescript
// Example Playwright test
test('Command Center loads Assistant tab', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.locator('text=Command Center')).toBeVisible();
  await expect(page.locator('[data-testid="unified-canvas"]')).toBeVisible();
});

test('Work tab switches views', async ({ page }) => {
  await page.goto('/dashboard/work');
  await page.click('text=Tasks');
  await expect(page.locator('text=Loading tasks')).toBeVisible();
});
```

## Performance Considerations

### Store Optimization
- Messages limited to last 20 in `recentMessages` derived store
- Execution feed capped at 8 entries in dashboard
- Workflows stored by ID for O(1) lookup

### Rendering Optimization
- Svelte reactive statements minimize re-renders
- `{#key}` blocks ensure proper list updates
- Lazy-loaded Markdown renderer
- Debounced search inputs

### Network Optimization
- Parallel data fetching (`Promise.all`)
- Single WebSocket connection per session
- Heartbeat every 30 seconds
- Auto-reconnect with exponential backoff

## Troubleshooting

### UnifiedCanvas Not Rendering
**Symptom**: Blank screen or error in console
**Solution**: Verify `assistantStore.initSession()` called in `onMount`

### Workflow Drawer Not Opening
**Symptom**: Clicking "View Details" does nothing
**Solution**: Check `assistantStore.openWorkflowDrawer(workflowId)` called

### II-Agent Connection Fails
**Symptom**: "WebSocket connection error"
**Solution**: Verify backend II-Agent server running and `handleRequestIIAgentSession` implemented

### Mobile Tabs Not Showing
**Symptom**: Bottom navigation missing on mobile
**Solution**: Check `MobileTabBar` component imported in layout and viewport width < 768px

## Future Enhancements

1. **Persistent Conversations**: Save to IndexedDB for history recall
2. **Multi-Workspace Support**: Switch between workspaces from shell
3. **Keyboard Shortcuts**: Cmd+K for command palette, Cmd+1/2/3 for tabs
4. **Search**: Global search across tasks, knowledge, messages
5. **Notifications**: Desktop notifications for workflow completions
6. **Collaboration**: Share workflows and executions with team
7. **Calendar Widget**: Embed full calendar in Work tab
8. **Analytics Dashboard**: Visual charts for telemetry data

## API Reference

### assistantStore Methods
```typescript
// Session
assistantStore.initSession(sessionId?: string)
assistantStore.clearSession()

// Messages
assistantStore.addMessage(message: Omit<AssistantMessage, 'id' | 'timestamp'>)
assistantStore.updateMessage(messageId: string, updates: Partial<AssistantMessage>)
assistantStore.clearMessages()

// Workflows
assistantStore.addWorkflow(workflow: Omit<WorkflowPlan, 'id' | 'timestamp'>)
assistantStore.updateWorkflowDecision(workflowId: string, status: 'approved' | 'revise' | 'rejected')

// Execution Feed
assistantStore.addExecutionEntry(entry: Omit<ExecutionEntry, 'id' | 'timestamp'>)
assistantStore.updateExecutionEntry(entryId: string, updates: Partial<ExecutionEntry>)

// Drawers
assistantStore.openWorkflowDrawer(workflowId: string)
assistantStore.closeWorkflowDrawer()
assistantStore.openExecutionDrawer(executionId: string)
assistantStore.closeExecutionDrawer()

// II-Agent
assistantStore.setIIAgentConnection(isConnected: boolean, sessionUuid?: string, agentToken?: string)
assistantStore.setIIAgentProcessing(isProcessing: boolean)
```

### Backend API Endpoints
```typescript
// Assistant
POST /api/assistant/create-agent-session → { sessionUuid, agentToken }
POST /api/ai/chat → { response }
POST /api/ai/orchestrate-task → { telemetryId, mainTask, workflow, confidence }
POST /api/ai/record-workflow-decision → { decisionStatus, decisionAt }

// Tasks & Knowledge
GET /api/tasks/list → { tasks }
PUT /api/tasks/:id → { task }
GET /api/knowledge/items → { items }
PUT /api/knowledge/items/:id → { item }

// Analytics & Billing
GET /api/settings/usage → { usageCount, remainingUsage, hasCustomKey, isPremium }
GET /api/billing/subscription-status → { status, currentPeriodEnd }
GET /api/ai/telemetry-summary → { orchestratedCount, deterministicCount, averageConfidence }
```

## Support

For issues or questions:
1. Check console for error messages
2. Verify assistantStore state in Svelte DevTools
3. Review event log in `$assistantStore.iiAgentState.eventLog`
4. Test with deterministic mode to isolate II-Agent issues
5. Check responsive design in browser DevTools (Device Toolbar)

---

**Track 7 Status**: ✅ Complete
**Next**: Testing & Production Deployment
