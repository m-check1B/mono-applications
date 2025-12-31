# Focus Integration Plan - UnifiedCanvas Architecture

**Date:** 2025-12-28
**Approach:** Incremental, one page at a time
**Status:** Ready to implement

---

## Critical Rule: Don't Break Other Pages

✅ **Keep everything else intact** - All other dashboard pages stay untouched
✅ **Only modify `/focus` page** - Single page replacement
✅ **One page at a time** - Get Focus working, then move to next app
❌ **Don't touch:** Speak, Learn, Lab, Agents, Brain, Memory, Jobs, etc.

---

## Goal

Replace the current "half-featured" Focus page (1881 lines, 5 tabs) with the **actual Focus app architecture**:
- **UnifiedCanvas** - AI command center (the core interface)
- **ContextPanel** - Sliding panels for CRUD operations
- **Preserve AI-first UX** - Don't break it into tabs

---

## Phase 1: Extract Components

### 1.1 Create Directory Structure

```bash
mkdir -p /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/components/focus/
mkdir -p /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/components/focus/assistant/
mkdir -p /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/components/focus/panels/
mkdir -p /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/components/focus/ui/
mkdir -p /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/stores/focus/
mkdir -p /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/api/
mkdir -p /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/utils/
```

### 1.2 Extract Core Components

**Source:** `/home/adminmatej/github/applications/focus-kraliki/frontend/src/lib/components/`

**Core Architecture (MUST HAVE):**
```
assistant/
├── UnifiedCanvas.svelte           # AI command center (main interface)
├── AssistantComposer.svelte       # AI input area
├── AssistantConversation.svelte   # AI response display
├── ExecutionDrawer.svelte         # Workflow results
├── WorkflowDrawer.svelte          # Workflow approval
└── MobileTabBar.svelte            # Mobile navigation

ContextPanel.svelte                # Sliding panel container
```

**Panel Components (CRUD Views):**
```
dashboard/
├── TasksView.svelte               # Task management
├── ProjectsView.svelte            # Projects
├── KnowledgeView.svelte           # Knowledge base
├── CalendarView.svelte            # Calendar sync
├── TimeTrackingView.svelte        # Time logs
├── AnalyticsView.svelte           # Insights
├── VoiceView.svelte               # Voice transcription
├── CapturesView.svelte            # File captures
├── WorkflowTemplatesView.svelte   # Automations
├── ShadowView.svelte              # Jungian analysis
├── SettingsView.svelte            # Settings
└── PomodoroView.svelte            # Timer
```

**UI Components (Shared):**
```
├── PomodoroTimer.svelte           # Timer widget
├── LoadingSpinner.svelte          # Loading states
├── MarkdownRenderer.svelte        # Markdown display
├── ModelPicker.svelte             # LLM selector
├── ToastStack.svelte              # Notifications
├── ToastNotification.svelte       # Toast items
└── ThemeToggle.svelte             # Theme switcher
```

**Knowledge Components:**
```
knowledge/
├── KnowledgeGrid.svelte           # Grid view
├── KnowledgeChat.svelte           # Chat interface
└── KnowledgeItemModal.svelte      # Detail modal
```

### 1.3 Copy Stores

**Source:** `/home/adminmatej/github/applications/focus-kraliki/frontend/src/lib/stores/`

**Required Stores:**
```
focus/
├── assistant.ts                   # AI state
├── tasks.ts                       # Task management
├── knowledge.ts                   # Knowledge state
├── projects.ts                    # Project state
├── calendar.ts                    # Calendar sync
├── time.ts                        # Time tracking
├── analytics.ts                   # Analytics
├── workflow.ts                    # Workflows
├── shadow.ts                      # Shadow work
├── contextPanel.ts                # Panel state
├── toast.ts                       # Notifications
├── auth.ts                        # Authentication
├── workspaces.ts                  # Workspace state
└── settings.ts                    # User settings
```

### 1.4 Copy Utils

**Source:** `/home/adminmatej/github/applications/focus-kraliki/frontend/src/lib/utils/`

**Required Utils:**
```
utils/
├── assistantQueue.ts              # AI request queue
├── iiAgentIntegration.ts          # ii-agent integration
├── logger.ts                      # Logging
├── offlineStorage.ts              # Offline sync
└── pendingEscalation.ts           # Escalation handling
```

### 1.5 Copy API Client (Optional)

**Source:** `/home/adminmatej/github/applications/focus-kraliki/frontend/src/lib/api/client.ts`

**Destination:** `/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/api/focusClient.ts`

**Note:** May not be needed if we use existing `/api/focus/*` proxy routes.

---

## Phase 2: Adapt Imports

### 2.1 Update Component Imports

Run this script to fix all import paths:

```bash
#!/bin/bash
# Fix imports in all copied components

FOCUS_DIR="/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/components/focus"

# Update component imports
find "$FOCUS_DIR" -name "*.svelte" -exec sed -i \
  -e "s|from '\$lib/components/|from '\$lib/components/focus/|g" \
  -e "s|from '\$lib/stores/|from '\$lib/stores/focus/|g" \
  -e "s|from '\$lib/utils|from '\$lib/utils|g" \
  -e "s|from '\$lib/api|from '\$lib/api|g" \
  {} \;

# Fix shared component references
find "$FOCUS_DIR" -name "*.svelte" -exec sed -i \
  -e "s|from '\$lib/components/focus/LoadingSpinner.svelte|from '\$lib/components/focus/ui/LoadingSpinner.svelte|g" \
  -e "s|from '\$lib/components/focus/MarkdownRenderer.svelte|from '\$lib/components/focus/ui/MarkdownRenderer.svelte|g" \
  {} \;
```

### 2.2 Update Store Imports

```bash
STORE_DIR="/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/stores/focus"

# Update store imports
find "$STORE_DIR" -name "*.ts" -exec sed -i \
  -e "s|from '\$lib/stores/|from '\$lib/stores/focus/|g" \
  -e "s|from '\$lib/utils|from '\$lib/utils|g" \
  {} \;
```

### 2.3 Update API Endpoints

**Critical:** Change all API calls to use Kraliki proxy:

```bash
# Update API endpoints in stores
find "$STORE_DIR" -name "*.ts" -exec sed -i \
  -e "s|fetch('/api/tasks|fetch('/api/focus/tasks|g" \
  -e "s|fetch('/api/projects|fetch('/api/focus/projects|g" \
  -e "s|fetch('/api/knowledge|fetch('/api/focus/knowledge|g" \
  -e "s|fetch('/api/calendar|fetch('/api/focus/calendar|g" \
  -e "s|fetch('/api/time|fetch('/api/focus/time|g" \
  -e "s|fetch('/api/analytics|fetch('/api/focus/analytics|g" \
  -e "s|fetch('/api/workflow|fetch('/api/focus/workflow|g" \
  -e "s|fetch('/api/shadow|fetch('/api/focus/shadow|g" \
  -e "s|fetch('/api/pomodoro|fetch('/api/focus/pomodoro|g" \
  -e "s|fetch('/api/captures|fetch('/api/focus/captures|g" \
  -e "s|fetch('/api/voice|fetch('/api/focus/voice|g" \
  {} \;
```

---

## Phase 3: Rebuild Focus Page

### 3.1 Backup Original

```bash
cp /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/routes/focus/+page.svelte \
   /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/routes/focus/+page.svelte.backup-v2
```

### 3.2 New Focus Page Structure

**File:** `/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/routes/focus/+page.svelte`

**New implementation (~100-150 lines):**

```svelte
<script lang="ts">
	import UnifiedCanvas from '$lib/components/focus/assistant/UnifiedCanvas.svelte';
	import ContextPanel from '$lib/components/focus/ContextPanel.svelte';
	import ToastStack from '$lib/components/focus/ui/ToastStack.svelte';

	// This is the ENTIRE Focus integration
	// No more 1881 lines of hardcoded UI!
</script>

<div class="focus-integration">
	<!-- Central AI command center (the core!) -->
	<UnifiedCanvas />

	<!-- CRUD panels slide in from right -->
	<ContextPanel />

	<!-- Notifications -->
	<ToastStack />
</div>

<style>
	.focus-integration {
		height: 100vh;
		display: flex;
		flex-direction: column;
		background: var(--void, #0a0e27);
		color: var(--text-main, #e0e6ff);
		font-family: 'JetBrains Mono', monospace;
		overflow: hidden;
	}
</style>
```

**Key Points:**
- ✅ Just component composition
- ✅ No business logic
- ✅ No demo data
- ✅ Rely on Focus backend
- ✅ Preserve AI-first UX

---

## Phase 4: Install Dependencies

Check if these npm packages are needed:

```bash
cd /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard

# Check what Focus uses
grep -r "import.*from" /home/adminmatej/github/applications/focus-kraliki/frontend/package.json

# Install if missing (likely needed):
npm install svelte-dnd-action      # Drag & drop
npm install lucide-svelte          # Icons
npm install bits-ui                # UI primitives (maybe)
```

---

## Phase 5: Extend API Proxy

### 5.1 Current Proxy Endpoints

**Existing:** `/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/routes/api/focus/`

```
GET  /api/focus/tasks              ✓ Exists
POST /api/focus/tasks              ✓ Exists
PUT  /api/focus/tasks?id=...       ✓ Exists
DELETE /api/focus/tasks?id=...     ✓ Exists

GET  /api/focus/projects           ✓ Exists
POST /api/focus/projects           ✓ Exists
PUT  /api/focus/projects?id=...    ✓ Exists
DELETE /api/focus/projects?id=...  ✓ Exists

GET  /api/focus/brain?action=...   ✓ Exists
POST /api/focus/brain              ✓ Exists
```

### 5.2 Missing Endpoints (Need to Add)

**Create these new route files:**

```
/api/focus/knowledge/+server.ts    # Knowledge CRUD
/api/focus/calendar/+server.ts     # Calendar sync
/api/focus/time/+server.ts         # Time tracking
/api/focus/analytics/+server.ts    # Analytics data
/api/focus/workflow/+server.ts     # Workflows
/api/focus/shadow/+server.ts       # Shadow work
/api/focus/pomodoro/+server.ts     # Timer
/api/focus/captures/+server.ts     # File uploads
/api/focus/voice/+server.ts        # Voice transcription
/api/focus/settings/+server.ts     # User settings
```

**Pattern (copy from `/api/focus/tasks/+server.ts`):**

```typescript
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const FOCUS_URL = process.env.FOCUS_URL || 'http://172.28.0.4:3017';

function getKralikiHeaders(cookies) {
	// ... (same as tasks)
}

export const GET: RequestHandler = async ({ url, cookies }) => {
	const response = await fetch(`${FOCUS_URL}/knowledge/`, {
		headers: getKralikiHeaders(cookies),
		signal: AbortSignal.timeout(10000)
	});

	if (!response.ok) return json([], { status: 200 });
	return json(await response.json());
};

export const POST: RequestHandler = async ({ request, cookies }) => {
	const body = await request.json();
	const response = await fetch(`${FOCUS_URL}/knowledge/`, {
		method: 'POST',
		headers: getKralikiHeaders(cookies),
		body: JSON.stringify(body),
		signal: AbortSignal.timeout(10000)
	});

	if (!response.ok) return json({ error: 'API error' }, { status: response.status });
	return json(await response.json());
};

// ... PUT, DELETE same pattern
```

---

## Phase 6: Testing

### 6.1 Build Test

```bash
cd /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard
npm run build
```

**Expected:** No TypeScript or import errors

### 6.2 Dev Server Test

```bash
npm run dev
```

**Navigate to:** `http://localhost:5173/focus`

**Test checklist:**
- [ ] UnifiedCanvas renders
- [ ] AI input area visible
- [ ] Can type in AI chat
- [ ] ContextPanel slides in when triggered
- [ ] Tasks panel opens
- [ ] Projects panel opens
- [ ] Knowledge panel opens
- [ ] Theme toggle works
- [ ] Notifications work

### 6.3 Backend Connection Test

**Verify Focus backend is running:**

```bash
curl http://172.28.0.4:3017/health
# Expected: 200 OK

curl -H "X-Kraliki-Session: test" http://172.28.0.4:3017/tasks/
# Expected: [] or task data
```

### 6.4 E2E Test

```bash
/home/adminmatej/github/tools/playwright-env/bin/python \
  /home/adminmatej/github/tools/playwright-env/e2e_runner.py \
  "http://127.0.0.1:8099/focus" \
  "focus-integration" \
  "/tmp/kraliki-focus-e2e"
```

---

## Phase 7: Deploy to Production

### 7.1 Build Production

```bash
npm run build
```

### 7.2 Restart Dashboard

```bash
pm2 restart kraliki-swarm-dashboard
```

### 7.3 Verify Production

```bash
curl https://kraliki.verduona.dev/focus
# Should return 200 OK
```

---

## Phase 8: Next Apps (One at a Time)

**After Focus works**, repeat this pattern for:

### 8.1 Speak by Kraliki (`/speak`)
- Extract feedback collection UI
- Extract sentiment dashboard
- 5-8 components
- Similar pattern to Focus

### 8.2 Learn by Kraliki (`/learn`)
- Extract course viewer
- Extract catalog browser
- 5-8 components
- Similar pattern to Focus

### 8.3 Lab by Kraliki (`/lab`)
- Monitoring UI only
- Deployment status
- 3-5 components
- Simpler than Focus

### 8.4 Voice by Kraliki (if needed)
- Call monitoring
- Status dashboard
- 3-5 components

---

## Rollback Plan

If anything goes wrong:

```bash
# Restore original Focus page
cp /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/routes/focus/+page.svelte.backup-v2 \
   /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/routes/focus/+page.svelte

# Remove extracted components
rm -rf /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/components/focus
rm -rf /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/stores/focus
rm -rf /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/dashboard/src/lib/utils

# Rebuild
npm run build
pm2 restart kraliki-swarm-dashboard
```

---

## Success Criteria

### Focus Page Integration Success

- ✅ UnifiedCanvas (AI chat) embedded and functional
- ✅ ContextPanel with all CRUD views working
- ✅ Task/Project/Knowledge management operational
- ✅ Voice input working
- ✅ Command palette (CMD+K) functional
- ✅ Settings and preferences synced
- ✅ E2E tests passing
- ✅ No regressions on other pages

### Code Quality

- ✅ Focus page reduced from 1881 lines to ~100 lines
- ✅ Demo data removed (rely on real backend)
- ✅ Code duplication eliminated (shared components)
- ✅ Maintainability improved
- ✅ TypeScript errors: 0
- ✅ Build warnings: 0

---

## Timeline Estimate

**Phase 1-3:** Component extraction and adaptation - **4-6 hours**
**Phase 4-5:** Dependencies and API routes - **2-3 hours**
**Phase 6:** Testing and debugging - **3-4 hours**
**Phase 7:** Production deployment - **1 hour**

**Total:** ~10-14 hours for complete Focus integration

**Each subsequent app:** ~6-8 hours (simpler than Focus)

---

## Notes

- ✅ **Incremental:** One page at a time
- ✅ **Safe:** Keep backups, easy rollback
- ✅ **Tested:** E2E tests before production
- ✅ **Focused:** Only modify what's needed
- ✅ **Reversible:** Can revert at any step

---

**Status:** READY TO IMPLEMENT

**Next step:** Phase 1 - Extract UnifiedCanvas and ContextPanel components
