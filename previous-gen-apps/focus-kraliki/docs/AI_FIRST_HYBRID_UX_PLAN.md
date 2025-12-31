# AI-First Hybrid UX Plan (Updated)

**Date**: 2025-11-21
**Refinement**: Best of Both Worlds - AI for creation, gestures for manipulation

---

## The Refined Vision

**Original concern from audit:**
> "Users bypass AI by using traditional CRUD forms"

**Critical user insights:**
> "It takes 1 second to swipe and delete an item. Users prefer fingers for quick actions, not plain language."

> "In-the-fly display of context - NOT a Boeing cockpit (too much), but a fighter jet helmet view (minimal, HUD)."

**The Solution: Task Complexity-Based Interaction + Dynamic Context HUD**

```
╔════════════════════════════════════════════════════════════════╗
║  COMPLEX/CREATIVE → AI Conversation (thinking, multi-field)   ║
║  SIMPLE/MECHANICAL → Direct Manipulation (muscle memory, fast)║
║  CONTEXT → Appears dynamically when needed (HUD, not cockpit) ║
╚════════════════════════════════════════════════════════════════╝
```

**Fighter Jet HUD Principle:**
```
Boeing Cockpit (❌ AVOID):
┌─────────────────────────────────────────┐
│ [Dashboard] [Widgets] [Stats] [Graphs] │ ← Always visible
│ [Sidebar] [Panels] [Lists] [Settings]  │ ← Information overload
│ [Notifications] [Badges] [Alerts] [•••]│ ← Cognitive burden
└─────────────────────────────────────────┘

Fighter Jet HUD (✅ TARGET):
┌─────────────────────────────────────────┐
│                                         │
│   🎯 Active context only                │ ← Appears when relevant
│                                         │
│   💬 Conversation                        │ ← Primary focus
│                                         │
│   ⚡ Task: [Creating...]               │ ← Status when working
│                                         │
└─────────────────────────────────────────┘
     ↓ Panel slides in ONLY when needed
┌─────────────────────────┐
│ [Task created] ✓        │
│ Review design docs      │
│ Priority: HIGH          │
└─────────────────────────┘
```

---

## Interaction Matrix

| Task | Best Interaction | Why |
|------|------------------|-----|
| **Create task with context** | 🎤 AI: "Create a task for design review, high priority, due tomorrow" | Multiple fields, requires thinking |
| **Mark task complete** | ☝️ Tap checkbox | Single action, visual, immediate |
| **Delete completed tasks** | ☝️ Swipe gesture | Fast, muscle memory, no thinking |
| **Reorder priority** | ☝️ Drag and drop | Visual feedback, spatial reasoning |
| **Search old notes** | 🎤 AI: "Find my notes about project X from last month" | Semantic search, fuzzy memory |
| **Apply filter** | ☝️ Tap filter button | Quick toggle, visual state |
| **Bulk operations** | 🎤 AI: "Archive all completed tasks from Q3" | Complex criteria, multiple items |
| **Update task details** | ☝️ Inline edit field | Single field, quick correction |
| **Plan weekly schedule** | 🎤 AI: "Schedule my tasks for this week based on deadlines and energy levels" | Complex orchestration, AI reasoning |

**Key Principle:**
- **1-2 fields/actions** → Direct manipulation (tap, swipe, drag)
- **3+ fields or semantic reasoning** → AI conversation

---

## Updated Architecture

### What Changes (from audit)

**BEFORE (Audit Recommendation):**
```
❌ Remove CRUD pages entirely
❌ Forms only via AI
❌ No direct access to lists
```

**AFTER (Hybrid Approach):**
```
✅ Convert CRUD pages to Context Panels
✅ Keep interactive lists (swipe, tap, drag)
✅ Remove/de-emphasize multi-field FORMS
✅ Emphasize: "Create via AI, manage via gestures"
```

### Route Structure (Fighter Jet HUD)

```
/dashboard (CLEAN, MINIMAL - 90% empty space)
│
├─ UnifiedCanvas (center, primary focus)
│  ├─ Conversation input (always visible)
│  ├─ Message history (scrollable)
│  └─ Inline status indicators (when AI is working)
│
├─ Dynamic HUD Elements (appear only when relevant)
│  ├─ 🎯 Current task status ("Creating task...", "Searching...")
│  ├─ 💡 AI suggestions (when confident)
│  ├─ ⚠️  Warnings/errors (when needed)
│  └─ ✓ Success confirmations (brief, then fade)
│
└─ Context Panels (HIDDEN by default, slide in on demand)
   ├─ Tasks Panel
   │  ├─ Opens: AI calls create_task tool, or manual open
   │  ├─ Shows: ONLY tasks, no chrome, no navigation
   │  ├─ ✅ Tap to complete/uncomplete
   │  ├─ ✅ Swipe to delete
   │  ├─ ✅ Drag to reorder
   │  ├─ ✅ Filter buttons (minimal, bottom)
   │  └─ ❌ Remove "New Task" form button
   │
   ├─ Knowledge Panel (same pattern)
   ├─ Projects Panel (same pattern)
   └─ Calendar Panel (same pattern)
```

**Key Difference:**
- Boeing cockpit: All panels visible, navigation bars, sidebars, always-on widgets
- Fighter jet HUD: Clean canvas + conversation, context appears dynamically when AI calls tools

### What Gets Removed

**Only the multi-field creation forms:**
- ❌ "New Task" button → 8-field modal
- ❌ "Add Knowledge Item" button → form modal
- ❌ "Create Project" button → form modal

**What stays (enhanced):**
- ✅ All list views with items
- ✅ All quick actions (tap, swipe, drag)
- ✅ Filter/search UI elements
- ✅ Inline editing (single fields)
- ✅ Status toggles, priority badges

---

## User Journey Examples

### Example 1: Create + Manage Tasks

**Flow:**
```
1. User types in UnifiedCanvas:
   "Create 3 tasks: review design docs (high priority, due tomorrow),
    update API endpoints (medium priority), write tests (low priority)"

2. AI orchestrator calls create_task tool 3 times
   → Tasks panel slides open
   → 3 tasks appear in list

3. User sees list with brutalist cards:
   ┌─────────────────────────────────────┐
   │ ☑️ Review design docs          [⋮] │  ← Tap to complete
   │ Priority: HIGH | Due: Tomorrow     │
   ├─────────────────────────────────────┤
   │ ○ Update API endpoints         [⋮] │  ← Swipe left to delete
   │ Priority: MEDIUM                   │
   ├─────────────────────────────────────┤
   │ ○ Write tests                  [⋮] │  ← Drag to reorder
   │ Priority: LOW                      │
   └─────────────────────────────────────┘

4. User taps checkbox on "Review design docs" → marked complete (instant)
5. User swipes "Write tests" left → delete confirmation → deleted (instant)
6. User drags "Update API endpoints" to top → reordered (instant)

7. Later, user types:
   "What's blocking me today?"
   AI scans tasks, responds with insights
```

**Result:** AI for creation (3 tasks, complex intent), gestures for management (complete, delete, reorder).

### Example 2: Knowledge Base

**Flow:**
```
1. User says via voice:
   "Create an idea: Use WebSockets for real-time collaboration"

2. AI creates knowledge item
   → Knowledge panel opens
   → New "Idea" item appears

3. User sees list:
   ┌─────────────────────────────────────┐
   │ 💡 Use WebSockets for real-time... │  ← Tap to expand
   │ Type: Idea | Today                 │
   ├─────────────────────────────────────┤
   │ 📝 Meeting notes: Q4 planning      │  ← Swipe to delete
   │ Type: Note | Yesterday             │
   └─────────────────────────────────────┘

4. User taps top item → inline view/edit
5. User clicks type filter "Ideas" → shows only ideas
6. User swipes old note → deleted

7. Later, user asks:
   "Find my notes about websockets"
   AI performs semantic search, shows results
```

**Result:** AI for semantic operations, gestures for quick actions.

---

## Implementation Plan (Updated)

### Phase 1: Route Refactoring ✅ Keep

**Goal:** Make /dashboard primary, but preserve panel access

**Changes:**
```typescript
// /dashboard/tasks/+page.svelte
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { contextPanelStore } from '$lib/stores/contextPanel';

  onMount(() => {
    // Redirect to dashboard with panel open
    contextPanelStore.open('tasks');
    goto('/dashboard');
  });
</script>

<!-- No UI needed, just redirect -->
```

**Result:** Deep links work (`/dashboard/tasks` → opens dashboard + tasks panel)

### Phase 2: Remove Form Modals ✅ NEW

**Goal:** Remove multi-field creation forms, keep list interactions

**Tasks Panel Changes:**
```svelte
<!-- REMOVE THIS -->
<button on:click={() => showCreateModal = true}>
  <Plus /> New Task
</button>

<!-- REMOVE THIS -->
{#if showCreateModal}
  <div class="modal">
    <form>...</form> <!-- 8-field form -->
  </div>
{/if}

<!-- KEEP THIS (all list interactions) -->
<div class="task-list">
  {#each tasks as task}
    <div class="brutal-card">
      <!-- ✅ Keep: Tap to complete -->
      <button on:click={() => toggleTask(task.id)}>
        <svelte:component this={getIcon(task.status)} />
      </button>

      <!-- ✅ Keep: Inline title editing -->
      <input bind:value={task.title} on:blur={() => updateTask(task)} />

      <!-- ✅ Keep: Swipe actions (use svelte-gesture or similar) -->
      <div use:swipe on:swipeleft={() => deleteTask(task.id)}>
        {task.title}
      </div>

      <!-- ✅ Keep: Quick actions menu -->
      <button on:click={() => showMenu(task.id)}>
        <MoreVertical />
      </button>
    </div>
  {/each}
</div>

<!-- ✅ Keep: Filters and search -->
<div class="filters">
  <button on:click={() => filterStatus('ALL')}>All</button>
  <button on:click={() => filterStatus('PENDING')}>Pending</button>
  <input type="text" bind:value={searchQuery} placeholder="Search..." />
</div>
```

**Same pattern for Knowledge Panel, Projects Panel, etc.**

### Phase 3: Add Creation Hints ✅ NEW

**Goal:** Guide users to AI for creation without blocking manual access

**Add to panel headers:**
```svelte
<div class="panel-header">
  <h2>Tasks</h2>

  <!-- Subtle AI hint (not blocking) -->
  <div class="ai-hint">
    <Sparkles class="w-3 h-3" />
    <span class="text-xs opacity-60">
      Try: "Create a task for..."
    </span>
  </div>
</div>
```

**Empty state with AI emphasis:**
```svelte
{#if tasks.length === 0}
  <div class="empty-state">
    <p class="font-bold">No tasks yet</p>

    <!-- Primary: AI creation -->
    <div class="brutal-card bg-accent text-accent-foreground p-4">
      <Sparkles class="w-6 h-6 mb-2" />
      <p class="font-bold">Try talking to me:</p>
      <code>"Create a task for design review, high priority, due tomorrow"</code>
    </div>

    <!-- Secondary: Manual fallback (small, low contrast) -->
    <button
      class="mt-4 text-xs opacity-40 hover:opacity-100"
      on:click={() => showQuickAddForm = true}
    >
      Or add manually (advanced)
    </button>
  </div>
{/if}
```

### Phase 4: Enhance Gestures ✅ NEW

**Goal:** Make direct manipulation delightful

**Add swipe gestures library:**
```bash
cd frontend
pnpm add svelte-gestures
```

**Implement swipe-to-delete:**
```svelte
<script>
  import { swipe } from 'svelte-gestures';
</script>

<div
  use:swipe={{ timeframe: 300, minSwipeDistance: 60 }}
  on:swipe={(e) => {
    if (e.detail.direction === 'left') {
      deleteTask(task.id);
    }
  }}
  class="task-card"
>
  {task.title}
</div>
```

**Add drag-to-reorder:**
```svelte
<script>
  import { dndzone } from 'svelte-dnd-action';

  function handleSort(e) {
    tasks = e.detail.items;
    // Persist order to backend
    updateTaskOrder(tasks.map(t => t.id));
  }
</script>

<div use:dndzone={{items: tasks}} on:consider={handleSort} on:finalize={handleSort}>
  {#each tasks as task (task.id)}
    <div class="task-card">...</div>
  {/each}
</div>
```

**Brutalist animation (hard snap, no spring):**
```css
/* app.css */
.task-card {
  transition: transform 0.15s cubic-bezier(0, 0, 1, 1); /* Hard ease-out */
}

.task-card.deleting {
  transform: translateX(-100%);
  transition: transform 0.2s cubic-bezier(0, 0, 1, 1);
}
```

### Phase 5: Dashboard Visual Hierarchy ✅ Fighter Jet HUD

**Goal:** Minimal interface, context appears dynamically

**Dashboard layout (CLEAN, NO SIDEBARS):**
```svelte
<div class="dashboard min-h-screen bg-background relative">
  <!-- Absolute: Dynamic HUD status (top center, appears only when AI is working) -->
  {#if isProcessing}
    <div class="fixed top-4 left-1/2 -translate-x-1/2 z-30 brutal-card px-4 py-2 bg-accent text-accent-foreground">
      <span class="font-bold uppercase text-xs">{currentAction}</span>
    </div>
  {/if}

  <!-- Absolute: Quick panel shortcuts (bottom right, minimal) -->
  <div class="fixed bottom-4 right-4 z-20 flex flex-col gap-2">
    <button
      class="w-10 h-10 brutal-btn bg-white text-black flex items-center justify-center"
      on:click={() => contextPanelStore.open('tasks')}
      title="Tasks"
    >
      📋
    </button>
    <button
      class="w-10 h-10 brutal-btn bg-white text-black flex items-center justify-center"
      on:click={() => contextPanelStore.open('knowledge')}
      title="Knowledge"
    >
      📚
    </button>
  </div>

  <!-- Main: Centered AI canvas (80% width, max 900px) -->
  <div class="flex items-center justify-center min-h-screen p-8">
    <div class="w-full max-w-[900px]">
      <!-- Minimal branding (top) -->
      <div class="mb-8 text-center">
        <h1 class="text-4xl font-black uppercase tracking-tighter mb-2">Focus by Kraliki</h1>
        <p class="text-xs uppercase font-bold text-muted-foreground tracking-widest">
          AI-First Command Center
        </p>
      </div>

      <!-- Unified Canvas (full width) -->
      <UnifiedCanvas />

      <!-- Quick prompts (below canvas, minimal) -->
      <div class="mt-4 flex flex-wrap gap-2 justify-center">
        <button class="brutal-btn bg-accent text-accent-foreground text-xs">
          Show urgent
        </button>
        <button class="brutal-btn bg-white text-black text-xs">
          Plan week
        </button>
      </div>
    </div>
  </div>
</div>

<!-- Context panels slide in from right (HIDDEN by default) -->
<ContextPanel />
```

**Key HUD Principles:**
1. **90% empty space** - clean, focused
2. **No persistent sidebars** - panels only when needed
3. **Floating action buttons** - minimal, bottom right (like Figma)
4. **Status HUD at top center** - appears only when AI is working
5. **Conversation is THE interface** - everything else is secondary

---

## Key Principles (Updated)

### 1. Respect Task Complexity

**Simple → Direct Manipulation:**
- Single field changes (title, status, priority)
- Visual operations (drag, swipe, tap)
- Quick filters and search

**Complex → AI Conversation:**
- Multi-field creation
- Semantic search
- Bulk operations
- Planning and insights

### 2. Progressive Enhancement

**Path 1 (Beginner → AI-first):**
```
User: "Create a task for..."
AI: Creates task → panel opens
User: Sees interactive list → discovers gestures
User: Taps/swipes to manage
User: Gains confidence → uses AI for complex operations
```

**Path 2 (Advanced → Direct manipulation):**
```
User: Opens panel manually (quick access button)
User: Uses filters, search, gestures for management
User: Discovers AI hints in empty states/headers
User: Tries AI for complex bulk operations
```

**Both paths are valid and supported!**

### 3. Brutalist Ergonomics

**Gestures must be:**
- ✅ Fast (< 300ms response)
- ✅ Obvious (visual affordances)
- ✅ Forgiving (undo/confirm dangerous actions)
- ✅ Brutal (hard animations, no springs)

**Example: Swipe to delete**
```
1. User swipes left
2. Card slides 100% left instantly (no spring)
3. Confirm button appears: "DELETE" (brutal-btn, red)
4. Tap confirm → card disappears (no fade, just gone)
5. Toast: "Task deleted" (3s, then disappears)
```

---

## Success Metrics (Updated)

| Metric | Target | Why |
|--------|--------|-----|
| **Creation via AI** | 70%+ | Complex operations should use AI |
| **Quick actions via gestures** | 80%+ | Complete, delete, reorder should be fast |
| **Panel opens per session** | 3+ | Users should access panels frequently |
| **AI queries per session** | 5+ | Users should talk to AI regularly |
| **Time to complete task** | < 1s | Tap should be instant |
| **Time to create task** | < 5s | AI should be fast for creation |

**The balance:** High AI usage for creation/complex queries, high gesture usage for management.

---

## Migration Checklist

### Phase 1: Route Refactoring
- [ ] Convert /tasks route to panel opener + redirect
- [ ] Convert /knowledge route to panel opener + redirect
- [ ] Convert /projects route to panel opener + redirect
- [ ] Add query param support: `/dashboard?panel=tasks`
- [ ] Test deep links work correctly

### Phase 2: Remove Form Modals
- [ ] Remove "New Task" button and modal from TasksView
- [ ] Remove "Add Item" button and modal from KnowledgeView
- [ ] Remove "Create Project" button and modal from ProjectsView
- [ ] Keep all list UI and interactions

### Phase 3: Add Creation Hints
- [ ] Add AI hint to panel headers ("Try: Create a task for...")
- [ ] Update empty states with AI emphasis
- [ ] Add optional manual fallback (small, low contrast)

### Phase 4: Enhance Gestures
- [ ] Install svelte-gestures or similar library
- [ ] Implement swipe-to-delete for tasks
- [ ] Implement swipe-to-delete for knowledge items
- [ ] Add drag-to-reorder for tasks (optional, nice to have)
- [ ] Add brutalist animations (hard snap, no spring)
- [ ] Test gestures on mobile (touch events)

### Phase 5: Dashboard Visual Hierarchy
- [ ] Add "AI Command Center" heading
- [ ] Add prominent quick action buttons
- [ ] Add "Quick Access" sidebar with panel shortcuts
- [ ] Add "Create via AI, manage via gestures" tagline
- [ ] Test responsive layout (desktop + mobile)

### Phase 6: Polish
- [ ] Add keyboard shortcuts (e.g., Ctrl+K to focus AI input)
- [ ] Add inline editing for single fields
- [ ] Add undo for dangerous actions (delete, archive)
- [ ] Add loading states for AI operations
- [ ] Test entire flow end-to-end

---

## Timeline

**Phase 1-2 (Critical):** 4-6 hours
- Route refactoring + form removal
- Gets us to AI-first routing

**Phase 3-4 (Important):** 6-8 hours
- Creation hints + gesture enhancements
- Makes direct manipulation delightful

**Phase 5-6 (Polish):** 4-6 hours
- Visual hierarchy + polish
- Professional finish

**Total:** 14-20 hours (~2-3 days)

---

## Conclusion

**The Hybrid Approach:** Best of both worlds
- 🎤 **AI for creation** (complex, multi-field, semantic)
- ☝️ **Gestures for management** (fast, mechanical, visual)

**Key Changes from Audit:**
- ✅ Keep interactive lists in panels
- ✅ Keep quick actions (tap, swipe, drag)
- ❌ Remove multi-field creation forms
- ✅ Add AI hints and progressive guidance

**Result:** A truly AI-first app that respects user ergonomics and task complexity.

---

**Updated**: 2025-11-21
**Status**: Ready for implementation
**Next**: Start Phase 1 (route refactoring)
