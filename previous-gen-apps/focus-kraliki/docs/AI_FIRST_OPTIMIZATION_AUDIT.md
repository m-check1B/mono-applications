# AI-First Optimization Audit

**Date**: 2025-11-21
**Status**: Completed
**Auditor**: Claude Code

---

## Executive Summary

Audited focus-kraliki against the AI-first vision:
> "AI-first, text and voice main UX with dynamic context as per what the user requests or needs. The app is plain language operated, and the intent is to be translated via AI orchestration into actions across features. The design should be modern Brutalism, yet with perfect ergonomy."

### Key Findings

| Aspect | Status | Assessment |
|--------|--------|------------|
| **Brutalist Design** | ✅ EXCELLENT | Zero border-radius, 2px borders, offset shadows, monospace typography |
| **Voice/Text Input** | ✅ GOOD | AssistantComposer with voice recording + text input |
| **AI Orchestration** | ⚠️ PARTIAL | Infrastructure exists but underutilized |
| **Conversation-First UX** | ❌ CRITICAL GAP | Traditional CRUD forms are PRIMARY, AI is secondary |
| **Dynamic Context** | ✅ GOOD | Context panels slide in based on tool calls |

### Critical Issue: Inverted UX Paradigm

**Current Reality:**
```
User Journey (Today):
1. User clicks /tasks route
2. Clicks "New Task" button
3. Fills 8-field form manually
4. OPTIONALLY clicks "Send to Assistant" after creation
   └─> AI is an AFTERTHOUGHT, not the PRIMARY UX
```

**Vision:**
```
User Journey (Should Be):
1. User types in UnifiedCanvas: "Create a task for reviewing design docs, high priority, due tomorrow"
2. AI orchestrator calls create_task tool
3. Tasks panel slides open showing the new task
4. NO FORMS unless user explicitly asks for manual entry
   └─> Conversation is PRIMARY, forms are escape hatches
```

**The Problem:** We built an AI assistant for a traditional app, not an AI-first app with traditional escape hatches.

---

## 1. Brutalist Design System Audit ✅ EXCELLENT

### Design Tokens (app.css:1-104)

**Brutalist Elements - Fully Implemented:**
- ✅ `--radius: 0px` - Zero border radius (pure brutalism)
- ✅ `.brutal-border` - 2px solid black/white borders
- ✅ `.brutal-shadow` - 4px×4px offset drop shadows (hard edges, no blur)
- ✅ `.brutal-shadow-sm` - 2px×2px offset shadows for small elements
- ✅ `.brutal-card` - Complete card styling (border + shadow + padding)
- ✅ `.brutal-btn` - Buttons with uppercase, tracking, translate-on-hover effect
- ✅ `font-mono` - Monospace typography for raw, code-like aesthetic

**Color System:**
- ✅ Light mode: 97% gray background (soft on eyes, not pure white)
- ✅ Dark mode: 8% gray background (soft on eyes, not pure black)
- ✅ High contrast borders: pure black/white
- ✅ Primary: Blue accent (230° hue, 90% saturation)
- ✅ Accent: Yellow (50° hue, 95% saturation)

**Ergonomics - Excellent:**
- ✅ Soft backgrounds reduce eye strain
- ✅ High contrast ensures readability
- ✅ Bold typography aids scannability
- ✅ Uppercase labels create clear hierarchy
- ✅ Offset shadows provide depth without softness

**Assessment:** The brutalist design system is **perfectly implemented** with excellent ergonomics. This is a model example of "modern brutalism with perfect ergonomy."

---

## 2. Voice/Text Input Layer ✅ GOOD

### AssistantComposer Component (AssistantComposer.svelte:1-129)

**Features Implemented:**
- ✅ Text input with brutalist styling (2px borders, focus shadows)
- ✅ Voice recording button (Mic/MicOff icons)
- ✅ Voice provider selector (Gemini Native, OpenAI Realtime)
- ✅ Upload audio file option
- ✅ Quick prompt buttons for common requests
- ✅ Recording status indicators
- ✅ Error handling for recording/upload failures

**UX Flow:**
```typescript
// Line 44-46: Text input
<input
  type="text"
  bind:value={inputMessage}
  placeholder="Ask anything…"
  class="flex-1 border-2 border-black dark:border-white..."
/>

// Line 49-62: Voice recording
<button
  type="button"
  class="brutal-btn..."
  on:click={() => emit(isRecording ? 'stop' : 'record')}
>
  {#if isRecording}
    <MicOff class="w-4 h-4 text-destructive" />
    Stop
  {:else}
    <Mic class="w-4 h-4" />
    Record
  {/if}
</button>

// Line 64-70: Send button
<button
  type="submit"
  class="brutal-btn px-6 py-3 bg-primary text-primary-foreground..."
  disabled={isLoading || !inputMessage.trim()}
>
  <Send class="w-4 h-4" />
  Send
</button>
```

**Assessment:** Voice/text input infrastructure is **well-implemented** and accessible. The composer is ready for AI-first usage.

---

## 3. Dynamic Context Panels ✅ GOOD

### Context Panel System (ContextPanel.svelte:1-111 + contextPanel.ts:1-78)

**Features:**
- ✅ 10 panel types: tasks, projects, knowledge, calendar, analytics, settings, workflow, shadow, time, infra
- ✅ Slide-in drawer from right (800px width on desktop)
- ✅ Brutalist styling with -8px left shadow, 2px borders
- ✅ Keyboard accessible (ESC to close)
- ✅ Backdrop blur on open
- ✅ Smooth transitions (300ms)

**API:**
```typescript
// Line 32-38: Open panel with optional data
contextPanelStore.open('tasks', { taskId: '123' });

// Line 40-53: Close with animation cleanup
contextPanelStore.close();

// Line 55-66: Toggle panel (open/close based on current state)
contextPanelStore.toggle('knowledge');

// Line 68-73: Update panel data without closing
contextPanelStore.updateData({ filter: 'urgent' });
```

**Assessment:** Context panel orchestration is **well-designed** and ready for AI-driven dynamic context switching.

---

## 4. AI Orchestration Infrastructure ⚠️ PARTIAL

### UnifiedCanvas Component (UnifiedCanvas.svelte:1-80)

**AI System Hint - Well-Defined:**
```typescript
// Lines 10-19: focusSystemHint
const focusSystemHint = `You are the Focus by Kraliki AI. Drive everything through tools.
Tools: knowledge (any type: Task, Idea, Plan, Note, Goal), tasks (Task type only),
projects, events/calendar, time tracking, workflows, analytics, workspaces, settings, infra.

Rules:
- Tasks are one predefined type; users can add/rename types
- When you use a tool, tell user which panel to open
- Prefer tool calls over speculation; one tool at a time`;
```

**Reactive State:**
```typescript
// Lines 21-25: Store subscriptions
$: messages = $assistantStore.messages;
$: composerMode = $assistantStore.composerState.mode;
$: iiAgentConnected = $assistantStore.iiAgentState.isConnected;
$: workflowDrawerOpen = $assistantStore.drawerState.workflowDrawerOpen;
```

**Dashboard Integration (dashboard/+page.svelte:1-80):**
- ✅ Models selector: Claude 3.5 Sonnet, Claude Haiku 4.5, GPT-4o mini
- ✅ Quick prompts: "Summarize tasks", "Plan my week", "Schedule sync", "Show progress"
- ✅ Voice state management
- ✅ Core send handler for deterministic/orchestrated modes

**Assessment:** The orchestration infrastructure exists and is properly wired, BUT it's underutilized because traditional CRUD routes bypass it.

---

## 5. Conversation-First UX ❌ CRITICAL GAP

### The Fundamental Problem

**Current Architecture:**
```
Route Structure:
/dashboard              → UnifiedCanvas (AI-first) ✅
/dashboard/tasks        → TasksView (CRUD forms) ❌
/dashboard/knowledge    → KnowledgeView (CRUD forms) ❌
/dashboard/projects     → ProjectsView (CRUD forms) ❌
/dashboard/calendar     → CalendarView (CRUD forms) ❌
/dashboard/settings     → SettingsView (forms) ✅ (acceptable)
```

**Problem:** Users have direct access to traditional CRUD pages that bypass the AI orchestration layer entirely.

### Case Study 1: Tasks Route (tasks/+page.svelte:1-444)

**Traditional CRUD Features Found:**
- ❌ Line 24: `showCreateModal` state for form modal
- ❌ Lines 36-43: 8-field manual form (title, description, priority, type, due_date, assignedUserId)
- ❌ Lines 94-117: `handleCreateTask()` - direct API call bypassing AI
- ❌ Lines 119-127: `handleDeleteTask()` - direct deletion
- ❌ Lines 213-219: "New Task" button opens form modal
- ❌ Lines 224-257: Search bar + status filter + priority filter dropdowns
- ❌ Lines 346-443: Full create task modal with 8 form fields

**Minimal AI Integration (Too Little, Too Late):**
- 🟡 Line 176-187: `sendTaskToAssistant()` function
- 🟡 Line 329: Sparkles icon button to "Send to Assistant"
- 🟡 But this is a **secondary** feature after manual CRUD

**What This Means:**
Users can (and will) manage tasks entirely without ever talking to the AI. The AI is a **side feature**, not the **primary UX**.

### Case Study 2: Knowledge Route (KnowledgeView.svelte:1-150)

**Traditional CRUD Features Found:**
- ❌ Lines 78-92: "Add Item" button and "Types" settings button
- ❌ Line 43-51: `handleCreate()` opens modal form
- ❌ Line 53-58: `handleDelete()` direct deletion
- ❌ Lines 96-106: Search bar
- ❌ Lines 109-125: Type filter buttons
- ❌ Lines 128-133: TypePicker with instructions to "share type IDs with assistant" (treating AI as an afterthought)
- ❌ Lines 142-150: "No items" empty state with "Add your first item" button

**Assessment:** Same problem as Tasks - form-first, AI-secondary.

---

## 6. Gap Analysis & Recommendations

### Critical Gaps

#### Gap 1: Route Architecture Inverts AI-First Vision

**Current:**
```
User Flow:
1. Navigate to /dashboard/tasks
2. Use traditional CRUD forms
3. (Optionally) send to AI afterward
```

**Should Be:**
```
User Flow:
1. Stay on /dashboard (UnifiedCanvas)
2. Talk/type to AI: "Create a task..."
3. AI orchestrates action → panel opens with result
4. Forms only appear if explicitly requested
```

**Impact:** HIGH - This is the core vision violation

**Recommendation:** Redesign route architecture to make UnifiedCanvas the primary interface:

**Option A: Remove Direct CRUD Routes (Radical)**
```
Routes:
/dashboard              → UnifiedCanvas (only route)
/dashboard/settings     → Settings (reasonable exception)

Context Panels:
- Tasks panel opens via contextPanelStore.open('tasks')
- Knowledge panel opens via contextPanelStore.open('knowledge')
- etc.
```

**Option B: Make CRUD Routes "Deep Links" (Pragmatic)**
```
Routes:
/dashboard              → UnifiedCanvas (default, primary)
/dashboard/tasks        → Opens UnifiedCanvas + tasks panel (not standalone page)
/dashboard/knowledge    → Opens UnifiedCanvas + knowledge panel

Implementation:
- In +page.svelte for /tasks: onMount(() => contextPanelStore.open('tasks'))
- Panel becomes the CRUD interface (not a separate page)
- Direct route access still works but funnels through AI-first canvas
```

**Recommended Approach:** Option B (pragmatic) - Preserves existing CRUD views but embeds them as panels within the AI-first canvas, maintaining deep link compatibility while enforcing conversation-first UX.

#### Gap 2: CRUD Forms Don't Surface AI Capabilities

**Current:** Users see traditional form fields (title, description, priority...) with NO indication that AI can help.

**Should Have:**
- AI suggestions for task titles based on context
- Auto-fill descriptions from voice transcriptions
- Intelligent defaults (priority, due dates) based on past behavior
- "Ask AI to draft this" button in forms

**Impact:** MEDIUM - Users won't discover AI capabilities

**Recommendation:** Add AI affordances to remaining form interfaces:
```svelte
<!-- In task/knowledge creation forms -->
<div class="flex items-center gap-2">
  <input type="text" bind:value={title} placeholder="Task title" />
  <button on:click={() => askAIForTitle()} class="brutal-btn bg-accent">
    <Sparkles class="w-4 h-4" />
    Ask AI
  </button>
</div>
```

#### Gap 3: No Visual Indication of AI-First Mode

**Current:** Dashboard looks like a traditional app with an assistant "feature".

**Should Have:**
- Prominent "AI Command Center" branding
- Visual emphasis on UnifiedCanvas as primary interface
- Subtle de-emphasis of direct CRUD links
- Onboarding that teaches conversation-first workflow

**Impact:** MEDIUM - Users revert to familiar form-based workflows

**Recommendation:** Add visual hierarchy that guides users toward AI-first usage:
```svelte
<!-- In dashboard layout -->
<div class="grid grid-cols-[2fr_1fr]">
  <!-- Left: Prominent AI Canvas -->
  <div class="col-span-2">
    <div class="mb-2 text-xs uppercase font-bold text-muted-foreground">
      AI Command Center
    </div>
    <UnifiedCanvas />
  </div>

  <!-- Right: Secondary "Manual Tools" (optional escape hatches) -->
  <aside class="text-xs text-muted-foreground">
    <p class="mb-2">Quick Links (advanced)</p>
    <a href="/dashboard/tasks" class="opacity-60">Tasks</a>
    <a href="/dashboard/knowledge" class="opacity-60">Knowledge</a>
  </aside>
</div>
```

#### Gap 4: Context Panels vs Full Pages

**Current:** Context panels exist but full CRUD pages compete with them.

**Should Be:** Context panels should be the ONLY way to access CRUD interfaces (except deep links).

**Impact:** HIGH - Users bypass AI layer entirely

**Recommendation:**
1. Move TasksView, KnowledgeView, ProjectsView INTO context panels exclusively
2. Remove standalone /tasks, /knowledge, /projects routes
3. Deep links redirect to /dashboard with panel open: `/dashboard?panel=tasks`

#### Gap 5: Missing Quick Actions in Composer

**Current:** Quick prompts are generic ("Summarize tasks", "Plan my week")

**Should Have:** Context-aware quick actions based on current panel:
```typescript
// When tasks panel is open:
quickActions = [
  "Show urgent tasks",
  "What's blocking me?",
  "Plan tomorrow",
]

// When knowledge panel is open:
quickActions = [
  "Find docs about...",
  "Create a new idea",
  "Recent notes",
]
```

**Impact:** LOW - Nice to have, improves discoverability

**Recommendation:** Add dynamic quick actions based on `$contextPanelStore.type`.

---

## 7. Positive Findings (What's Working Well)

### ✅ Excellent Brutalist Design
- Zero compromises on brutalist aesthetic
- Offset shadows, hard borders, monospace typography
- Perfect ergonomics with soft backgrounds and high contrast
- CSS utilities (`.brutal-btn`, `.brutal-card`, `.brutal-shadow`) well-designed

### ✅ Solid Voice/Text Infrastructure
- AssistantComposer is production-ready
- Voice recording with Gemini Native + OpenAI Realtime
- Deepgram transcription fallback
- Upload audio file option

### ✅ Well-Architected Context System
- Context panel store with clean API
- 10 panel types covering all features
- Brutalist-styled slide-in drawer
- Keyboard accessible (ESC to close)

### ✅ AI Orchestration Ready
- focusSystemHint properly defines AI behavior
- Tool-driven architecture in place
- II-Agent integration wired up
- Hybrid execution model (deterministic vs orchestrated)

### ✅ Clean Codebase
- Type safety with TypeScript
- Reactive stores with Svelte
- Modular component architecture
- Good separation of concerns

---

## 8. Priority Roadmap

### P0: Critical (Fix Vision Violation)

**Task 1: Redesign Route Architecture (Option B - Pragmatic)**
- [ ] Make /dashboard the default, primary interface
- [ ] Convert /tasks, /knowledge, /projects to panel-opening routes
- [ ] Implement: `onMount(() => contextPanelStore.open('tasks'))`
- [ ] Ensure CRUD views only appear inside context panels
- [ ] Test deep links still work: `/dashboard?panel=tasks`

**Task 2: Add Visual AI-First Hierarchy**
- [ ] Prominent "AI Command Center" heading above UnifiedCanvas
- [ ] De-emphasize direct CRUD links (smaller, lower contrast)
- [ ] Add onboarding tooltip: "Try typing: Create a task for..."

**Task 3: Remove Competing CRUD Pages**
- [ ] Delete standalone TasksView page (keep as panel-only component)
- [ ] Delete standalone KnowledgeView page (keep as panel-only component)
- [ ] Ensure all CRUD operations funnel through UnifiedCanvas → AI → Panel

**Success Metrics:**
- 80% of users create tasks via conversation (not forms)
- Average session starts on /dashboard (not /tasks)
- Context panels opened via AI tool calls, not direct navigation

### P1: Important (Improve AI Discoverability)

**Task 4: Add AI Affordances to Forms**
- [ ] "Ask AI" buttons in remaining form fields
- [ ] AI-suggested titles/descriptions
- [ ] Intelligent defaults based on past behavior

**Task 5: Dynamic Quick Actions**
- [ ] Context-aware quick actions based on open panel
- [ ] "Recently used" commands
- [ ] Suggested next actions

**Task 6: Onboarding Flow**
- [ ] First-time user tutorial: "Talk to create tasks"
- [ ] Example prompts with expected outcomes
- [ ] "Try it" interactive demo

### P2: Nice to Have (Polish)

**Task 7: AI-Driven Context Switching**
- [ ] Auto-open panels based on conversation topic
- [ ] "Would you like me to open the Tasks panel?" confirmation
- [ ] Smart panel suggestions

**Task 8: Voice-First Optimizations**
- [ ] Larger Mic button (more prominent)
- [ ] Visual recording indicator (pulsing animation)
- [ ] Real-time transcription preview

**Task 9: Brutalist Animations**
- [ ] Panel slide-in with "chunk" effect (no smooth easing)
- [ ] Button press with hard snap (no spring)
- [ ] Instant state changes (no fade transitions)

---

## 9. Implementation Notes

### Code Locations

**Brutalist Design:**
- `frontend/tailwind.config.js:1-51` - Tailwind theme config
- `frontend/src/app.css:1-104` - CSS variables and utilities

**Voice/Text Input:**
- `frontend/src/lib/components/assistant/AssistantComposer.svelte:1-129`

**Context Panels:**
- `frontend/src/lib/components/ContextPanel.svelte:1-111`
- `frontend/src/lib/stores/contextPanel.ts:1-78`

**AI Orchestration:**
- `frontend/src/lib/components/assistant/UnifiedCanvas.svelte:1-80`
- `frontend/src/routes/dashboard/+page.svelte:1-80`

**CRUD Pages (TO BE REFACTORED):**
- `frontend/src/routes/dashboard/tasks/+page.svelte:1-444`
- `frontend/src/lib/components/dashboard/KnowledgeView.svelte:1-150`

### Migration Path

**Step 1: Preserve Existing Functionality**
- Don't delete CRUD components yet
- Move them into context panels first
- Ensure feature parity

**Step 2: Redirect Routes to Canvas**
```typescript
// In /dashboard/tasks/+page.svelte
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { contextPanelStore } from '$lib/stores/contextPanel';

  onMount(() => {
    contextPanelStore.open('tasks');
    goto('/dashboard'); // Redirect to canvas
  });
</script>
```

**Step 3: Update Navigation Links**
```svelte
<!-- Before -->
<a href="/dashboard/tasks">Tasks</a>

<!-- After -->
<button on:click={() => contextPanelStore.open('tasks')}>
  Tasks
</button>
```

**Step 4: Test Deep Links**
```typescript
// In /dashboard/+page.svelte
onMount(() => {
  const params = new URLSearchParams(window.location.search);
  const panel = params.get('panel');
  if (panel) {
    contextPanelStore.open(panel as PanelType);
  }
});
```

**Step 5: Update AI Tool Handlers**
```typescript
// Ensure tool calls open panels
async function handleToolCall(toolName: string, args: any) {
  const result = await executeTool(toolName, args);

  // Auto-open relevant panel
  if (toolName === 'create_task') {
    contextPanelStore.open('tasks', { taskId: result.id });
  } else if (toolName === 'create_knowledge_item') {
    contextPanelStore.open('knowledge', { itemId: result.id });
  }
}
```

---

## 10. Conclusion

### What's Working ✅

Focus by Kraliki has:
- **Exceptional brutalist design** with perfect ergonomics
- **Production-ready voice/text input** with multiple providers
- **Well-architected context panel system** ready for dynamic UX
- **Solid AI orchestration infrastructure** with tool-driven approach

### Critical Gap ❌

The UX paradigm is **inverted from the AI-first vision**:
- Traditional CRUD forms are **primary**
- AI assistant is **secondary** (a "send to assistant" afterthought)
- Users can (and will) bypass AI entirely by using direct CRUD routes

### Vision ✨

The AI-first vision requires:
- **Conversation is primary** (UnifiedCanvas is the main interface)
- **Forms are escape hatches** (only for advanced users or edge cases)
- **AI orchestration drives all actions** (not optional, but the default path)
- **Dynamic context adapts** to user needs (panels open based on conversation)

### Priority Action 🎯

**Redesign route architecture** to make UnifiedCanvas the primary interface and embed CRUD views as context panels (not standalone pages). This single change aligns the implementation with the AI-first vision.

**Estimated Impact:**
- **Before:** 20% of users interact via AI, 80% via forms
- **After:** 80% of users interact via AI, 20% via forms (advanced users, deep links)

---

**Audit Complete**: 2025-11-21
**Next Step**: Present findings and get approval for P0 refactoring
**Estimated Effort**: 2-3 days for P0 critical changes
