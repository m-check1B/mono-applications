# Fighter Jet HUD - Workflow Validation

**Date**: 2025-11-21
**Purpose**: Validate that HUD concept supports ALL expected workflows

---

## Design Principle Recap

```
Fighter Jet HUD:
- 90% empty space (clean canvas + conversation)
- Context appears ONLY when needed
- Floating action buttons (minimal, bottom-right)
- Panels slide in on-demand (AI-triggered or manual)
- No persistent sidebars/navigation
```

---

## Workflow Scenario Matrix

### Category 1: Information Retrieval (Read Operations)

#### Scenario 1.1: "Show me my tasks for tomorrow"

**User Intent:** View filtered task list

**Flow:**
```
1. User types: "Show me my tasks for tomorrow"

2. AI processes query → calls get_tasks tool with date filter

3. HUD status appears (top center): ⚡ "Loading tasks..."

4. Tasks panel slides in from right:
   ┌─────────────────────────────┐
   │ Tasks - Tomorrow            │
   ├─────────────────────────────┤
   │ ☐ Review design docs        │
   │   Priority: HIGH            │
   ├─────────────────────────────┤
   │ ☐ Team sync at 2pm          │
   │   Priority: MEDIUM          │
   └─────────────────────────────┘

5. User can now:
   - Tap checkboxes to complete
   - Swipe to delete
   - Drag to reorder
   - Close panel (ESC or backdrop click)
```

**Result:** ✅ Works perfectly - panel appears on-demand with filtered data

---

#### Scenario 1.2: "What's blocking me today?"

**User Intent:** AI analyzes tasks and shows blockers

**Flow:**
```
1. User asks: "What's blocking me today?"

2. AI analyzes tasks in background

3. HUD status: ⚡ "Analyzing tasks..."

4. AI responds in conversation:
   "You have 2 blockers:
   1. Waiting for design approval (blocks 3 tasks)
   2. Missing API credentials (blocks deployment)"

5. AI asks: "Would you like to see the blocked tasks?"

6. If yes → Tasks panel opens with filter applied
   If no → conversation continues

7. User can click inline links in AI response:
   "See [blocked tasks] or [dependencies]"
   → Opens relevant panel on click
```

**Result:** ✅ Works - AI can analyze without panel, open panel if user wants details

---

#### Scenario 1.3: Quick calendar check (manual)

**User Intent:** User wants to glance at today's schedule

**Flow:**
```
1. User taps 📅 FAB (bottom-right)

2. Calendar panel slides in immediately:
   ┌─────────────────────────────┐
   │ Calendar - Today            │
   ├─────────────────────────────┤
   │ 10:00 AM - Team standup     │
   │ 2:00 PM - Design review     │
   │ 4:00 PM - Client call       │
   └─────────────────────────────┘

3. User glances → closes panel (ESC)

4. Total time: <2 seconds
```

**Result:** ✅ Works - FAB provides instant manual access

---

#### Scenario 1.4: "Find my notes about project Phoenix"

**User Intent:** Semantic search across knowledge base

**Flow:**
```
1. User: "Find my notes about project Phoenix"

2. AI performs semantic search

3. HUD status: ⚡ "Searching knowledge..."

4. AI responds:
   "Found 5 items related to Project Phoenix"

5. Knowledge panel opens with search results:
   ┌─────────────────────────────┐
   │ Knowledge - Search Results  │
   ├─────────────────────────────┤
   │ 💡 Phoenix architecture     │
   │    Type: Idea | 3 days ago  │
   ├─────────────────────────────┤
   │ 📝 Phoenix kickoff notes    │
   │    Type: Note | 1 week ago  │
   ├─────────────────────────────┤
   │ 🎯 Phoenix milestones       │
   │    Type: Goal | 2 weeks ago │
   └─────────────────────────────┘

6. User taps item → expands inline for reading
```

**Result:** ✅ Works - semantic search + panel with results

---

### Category 2: Creation Operations (Write)

#### Scenario 2.1: "Create a task for design review, high priority, due tomorrow"

**User Intent:** Create single task with multiple attributes

**Flow:**
```
1. User types command

2. AI parses intent → detects: create_task tool needed

3. HUD status: ⚡ "Creating task..."

4. AI calls create_task({
     title: "Design review",
     priority: "HIGH",
     due_date: "2025-11-22"
   })

5. Tasks panel slides in:
   ┌─────────────────────────────┐
   │ ✓ Task created              │
   ├─────────────────────────────┤
   │ ☐ Design review             │
   │   Priority: HIGH            │
   │   Due: Tomorrow             │
   └─────────────────────────────┘

6. Panel auto-closes after 3 seconds
   OR user closes manually
   OR user interacts with task (panel stays)
```

**Result:** ✅ Works - AI handles multi-field creation, panel shows confirmation

---

#### Scenario 2.2: "Create 5 tasks for this week's sprint"

**User Intent:** Bulk task creation

**Flow:**
```
1. User: "Create 5 tasks for this week's sprint:
   - Backend API endpoints
   - Frontend components
   - Write tests
   - Documentation
   - Deploy to staging"

2. AI parses list → calls create_task 5 times

3. HUD status: ⚡ "Creating 5 tasks..." (with progress)

4. Tasks panel opens showing new tasks:
   ┌─────────────────────────────┐
   │ ✓ Created 5 tasks           │
   ├─────────────────────────────┤
   │ ☐ Backend API endpoints     │
   │ ☐ Frontend components       │
   │ ☐ Write tests               │
   │ ☐ Documentation             │
   │ ☐ Deploy to staging         │
   └─────────────────────────────┘

5. User can immediately:
   - Tap to mark complete
   - Drag to reorder by priority
   - Swipe to delete if mistakes
```

**Result:** ✅ Works - bulk creation with panel showing results

---

#### Scenario 2.3: "Schedule a 30-minute sync with advisor tomorrow at 2pm"

**User Intent:** Create calendar event

**Flow:**
```
1. User types command

2. AI extracts: title="Sync with advisor", duration=30min, date=tomorrow, time=2pm

3. HUD status: ⚡ "Scheduling event..."

4. AI calls create_event tool

5. Calendar panel slides in:
   ┌─────────────────────────────┐
   │ ✓ Event scheduled           │
   ├─────────────────────────────┤
   │ 📅 Tomorrow 2:00 PM         │
   │ Sync with advisor (30 min)  │
   └─────────────────────────────┘

6. Panel shows day view with new event highlighted
```

**Result:** ✅ Works - event creation with confirmation panel

---

### Category 3: Quick Actions (Gestures)

#### Scenario 3.1: Mark task complete (fastest path)

**User Intent:** Complete a task in <1 second

**Option A (via panel):**
```
1. User taps 📋 FAB → Tasks panel opens
2. User taps checkbox → task marked complete
3. Total time: ~2 seconds
```

**Option B (via AI - slower but hands-free):**
```
1. User says: "Mark design review as complete"
2. AI calls update_task tool
3. HUD shows: ✓ "Task completed"
4. Total time: ~3 seconds
```

**Best for quick completion:** Option A (panel + tap)

**Issue:** ❗ User must open panel first - not ideal for urgent task completion

**Solution:** Add **quick action command bar**
```
User types: Ctrl+K (or Cmd+K)
→ Command palette appears:
  ┌────────────────────────┐
  │ > mark design review   │ ← Fuzzy search
  ├────────────────────────┤
  │ ✓ Mark "Design review" │
  │   as complete          │
  └────────────────────────┘
→ Select → done (no panel)
```

**Updated Result:** ✅ Works with command palette addition

---

#### Scenario 3.2: Delete completed tasks (cleanup)

**User Intent:** Batch delete

**Option A (via panel gestures):**
```
1. User opens Tasks panel
2. User swipes each completed task left
3. Confirms deletion
4. Time: ~5 seconds for 5 tasks
```

**Option B (via AI - better for bulk):**
```
1. User: "Delete all completed tasks from last week"
2. AI: "Found 8 completed tasks. Delete them?"
3. User: "Yes"
4. AI calls delete_task 8 times
5. HUD shows: ✓ "Deleted 8 tasks"
6. Time: ~3 seconds
```

**Best for bulk deletion:** Option B (AI)

**Result:** ✅ Works - gestures for individual, AI for bulk

---

### Category 4: Complex Workflows

#### Scenario 4.1: "Plan my week based on deadlines and energy"

**User Intent:** AI-assisted weekly planning

**Flow:**
```
1. User requests planning

2. AI analyzes:
   - All tasks with deadlines
   - User's energy patterns (if tracked)
   - Calendar availability

3. HUD status: ⚡ "Planning week..."

4. AI creates workflow plan

5. Workflow drawer slides in (bottom):
   ┌─────────────────────────────────────┐
   │ 📋 Weekly Plan                      │
   ├─────────────────────────────────────┤
   │ Monday (high energy):               │
   │   • Backend API work (3h)           │
   │   • Design review (1h)              │
   │ Tuesday (meetings):                 │
   │   • Team sync (10am)                │
   │   • Client call (2pm)               │
   │ Wednesday (deep work):              │
   │   • Testing & QA (4h)               │
   ├─────────────────────────────────────┤
   │ [Apply to Calendar] [Adjust Plan]   │
   └─────────────────────────────────────┘

6. User can:
   - Review plan in drawer
   - Click "Apply" → events created
   - Click "Adjust" → AI refines
```

**Result:** ✅ Works - workflow drawer for complex planning

---

#### Scenario 4.2: "Show me project status and next steps"

**User Intent:** Multi-panel context (tasks + projects + analytics)

**Flow:**
```
1. User requests status

2. AI analyzes project, tasks, progress

3. AI responds in conversation:
   "Project Phoenix is 60% complete.

   Completed: 12/20 tasks
   In Progress: 5 tasks
   Blocked: 3 tasks

   Next steps:
   1. Resolve API credential blocker
   2. Complete frontend components
   3. Schedule staging deployment"

4. AI shows inline action buttons:
   [View Tasks] [View Project] [View Blockers]

5. User clicks "View Tasks" → Tasks panel opens with project filter

6. Alternatively, AI asks:
   "Would you like to see:
   A) Task breakdown
   B) Timeline visualization
   C) Blocker details"

7. User selects → appropriate panel opens
```

**Result:** ✅ Works - AI can show multi-faceted data, user chooses what to drill into

---

### Category 5: Discovery & Exploration

#### Scenario 5.1: "What can I do here?" (new user)

**User Intent:** Discover capabilities

**Flow:**
```
1. New user types: "What can I do here?"

2. AI responds:
   "I can help you with:

   📋 Tasks: Create, organize, and track your work
   📚 Knowledge: Store notes, ideas, and references
   📅 Calendar: Schedule events and meetings
   ⏱️  Time: Track focus sessions
   📊 Insights: Analyze your productivity

   Try asking:
   • 'Create a task for...'
   • 'Show me my tasks for today'
   • 'Find my notes about...'
   • 'Plan my week'

   Or tap the icons (📋 📚) to explore!"

3. User can:
   - Try example commands
   - Tap FABs to see what's there
   - Ask follow-up questions
```

**Result:** ✅ Works - AI guides discovery through conversation

---

#### Scenario 5.2: "How do I organize tasks by project?"

**User Intent:** Learn feature

**Flow:**
```
1. User asks for help

2. AI responds with guidance:
   "To organize by project:

   Option 1: Tag tasks with project name
   'Create a task for API work, project Phoenix'

   Option 2: Filter by project
   'Show me all Phoenix tasks'

   Option 3: Create project-specific workspace
   'Create a workspace for Phoenix'

   Which would you prefer?"

3. User chooses approach

4. AI walks through example:
   "Let's try option 1. Say:
   'Create 3 tasks for Phoenix: API, frontend, tests'"

5. AI demonstrates by executing

6. Tasks panel shows result with project tags
```

**Result:** ✅ Works - AI provides interactive tutorials

---

### Category 6: Edge Cases & Problems

#### Scenario 6.1: "I accidentally deleted a task"

**User Intent:** Undo mistake

**Flow:**
```
1. User: "I accidentally deleted 'Design review' task"

2. AI checks recent deletions in history

3. AI responds:
   "Found 'Design review' deleted 30 seconds ago.

   Would you like to restore it?"

4. User: "Yes"

5. AI calls restore_task or create_task with same data

6. Tasks panel opens showing restored task:
   ┌─────────────────────────────┐
   │ ✓ Task restored             │
   ├─────────────────────────────┤
   │ ☐ Design review             │
   │   Priority: HIGH            │
   └─────────────────────────────┘
```

**Result:** ✅ Works - AI can handle undo via conversation

---

#### Scenario 6.2: User creates task but panel doesn't auto-open

**User Intent:** Manually check if task was created

**Flow:**
```
1. User creates task via AI but panel fails to open (network issue?)

2. User uncertain if task was created

3. User can:
   A) Ask AI: "Did that work?"
      → AI checks and confirms

   B) Tap 📋 FAB to manually open panel
      → See all tasks including new one

   C) Ask: "Show me tasks I created today"
      → AI filters and shows in panel
```

**Result:** ✅ Works - multiple fallback mechanisms

---

#### Scenario 6.3: "I prefer forms over conversation"

**User Intent:** Advanced user wants direct control

**Solution Options:**

**Option A: Command palette (recommended)**
```
User: Ctrl+K → "new task"
→ Minimal inline form appears:
  ┌────────────────────────┐
  │ Quick Add Task         │
  ├────────────────────────┤
  │ Title: [_________]     │
  │ Priority: [Medium ▼]   │
  │ Due: [Tomorrow]        │
  │ [Create] [Cancel]      │
  └────────────────────────┘
```

**Option B: Panel quick-add (escape hatch)**
```
User opens Tasks panel → clicks "+" icon (top-right)
→ Inline form appears at top of list:
  ┌────────────────────────┐
  │ + New task: [______]   │
  │   [⚡ Ask AI] [✓ Save] │
  └────────────────────────┘
```

**Option C: Settings toggle**
```
User goes to Settings → "Advanced Mode"
→ Enables "Show quick-add buttons in panels"
→ Panels now show small "+" buttons
```

**Result:** ✅ Works - multiple escape hatches for power users

---

## Workflow Coverage Summary

| Workflow Category | Coverage | Notes |
|-------------------|----------|-------|
| **Information Retrieval** | ✅ 100% | AI queries → panels appear with data |
| **Simple Creation** | ✅ 100% | AI parses intent → creates → shows panel |
| **Bulk Creation** | ✅ 100% | AI handles lists → panel shows results |
| **Quick Actions (gestures)** | ⚠️ 90% | Need command palette for truly instant actions |
| **Complex Workflows** | ✅ 100% | Workflow drawer + multi-panel support |
| **Discovery** | ✅ 100% | AI guides users through conversation |
| **Error Recovery** | ✅ 100% | AI can undo, retry, confirm actions |
| **Power User Escape Hatches** | ⚠️ 80% | Need command palette + panel quick-add |

---

## Required Additions for 100% Coverage

### 1. Command Palette (Critical for power users)

**Keyboard shortcut:** `Ctrl+K` or `Cmd+K`

**Features:**
- Fuzzy search across all actions
- Quick task completion (no panel)
- Quick navigation to panels
- Recent actions history

**Implementation:**
```svelte
<script>
  let showCommandPalette = false;
  let commandQuery = '';

  function handleKeydown(e: KeyboardEvent) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      showCommandPalette = true;
    }
  }
</script>

{#if showCommandPalette}
  <div class="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
    <div class="brutal-card w-full max-w-[600px] p-0">
      <input
        type="text"
        bind:value={commandQuery}
        placeholder="Type a command or search..."
        class="w-full px-4 py-3 border-b-2 border-black dark:border-white"
        autofocus
      />
      <div class="max-h-[400px] overflow-y-auto">
        {#each filteredCommands as command}
          <button class="w-full text-left px-4 py-2 hover:bg-accent">
            {command.label}
          </button>
        {/each}
      </div>
    </div>
  </div>
{/if}
```

---

### 2. Panel Quick-Add (Escape hatch)

**Location:** Top-right of each panel

**UI:**
```svelte
<!-- In TasksView panel -->
<div class="panel-header flex items-center justify-between">
  <h2>Tasks</h2>

  <!-- Small "+" button (subtle, not prominent) -->
  <button
    class="w-8 h-8 border border-black dark:border-white opacity-40 hover:opacity-100"
    on:click={() => showQuickAdd = true}
    title="Quick add (advanced)"
  >
    +
  </button>
</div>

{#if showQuickAdd}
  <div class="p-4 border-b-2 border-black dark:border-white">
    <input
      type="text"
      bind:value={quickTitle}
      placeholder="Task title..."
      class="w-full px-3 py-2 border-2 border-black dark:border-white"
    />
    <div class="flex gap-2 mt-2">
      <button class="brutal-btn bg-primary text-primary-foreground text-xs">
        Create
      </button>
      <button class="brutal-btn bg-white text-black text-xs">
        ⚡ Ask AI instead
      </button>
    </div>
  </div>
{/if}
```

---

### 3. Inline Action Links (in AI responses)

**Pattern:** AI responses include clickable actions

**Example:**
```typescript
// AI response with inline actions
const response = {
  text: "Found 8 completed tasks from last week.",
  actions: [
    { label: "View tasks", action: () => openPanel('tasks', { filter: 'completed-last-week' }) },
    { label: "Delete all", action: () => bulkDelete('completed-last-week') }
  ]
};
```

**UI rendering:**
```svelte
<div class="ai-message">
  <p>{response.text}</p>
  <div class="flex gap-2 mt-2">
    {#each response.actions as action}
      <button class="brutal-btn text-xs" on:click={action.action}>
        {action.label}
      </button>
    {/each}
  </div>
</div>
```

---

## Final Validation: All Scenarios Work ✅

**Summary:**
1. ✅ "Show me X" queries → Panels appear with filtered data
2. ✅ "Create X" commands → AI creates, panel confirms
3. ✅ Quick actions → FABs + gestures + command palette (new)
4. ✅ Complex workflows → Workflow drawer + multi-panel
5. ✅ Discovery → AI guides through conversation
6. ✅ Error recovery → AI can undo/retry
7. ✅ Power users → Command palette + panel quick-add (new)

**The fighter jet HUD concept is CONSISTENT and COMPLETE with these additions:**
- Command palette (Ctrl+K) for power users
- Panel quick-add buttons (subtle, not prominent)
- Inline action links in AI responses

**Design Integrity Maintained:**
- 90% empty space ✅
- No persistent sidebars ✅
- Context appears on-demand ✅
- AI-first, gestures-second ✅
- Escape hatches for edge cases ✅

---

**Status:** Ready for implementation
**Next:** Implement Phase 1 (route refactoring) + command palette
