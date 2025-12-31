# AI-First Gap Completion Plan

**Date**: 2025-11-21
**Status**: Implementation Roadmap
**Priority**: Complete AI-first transformation

---

## Gap Summary

| # | Gap | Priority | Status | Complexity |
|---|-----|----------|--------|------------|
| **P0 Gaps (Orchestration) - COMPLETE ✅** |
| 1 | Backend function calling | P0 | ✅ DONE | Medium |
| 2 | Frontend panel opening (text chat) | P0 | ✅ DONE | Medium |
| 3 | Workflow drawer opening | P0 | ✅ DONE | Low |
| 4 | II-Agent panel opening | P0 | ✅ DONE | Medium |
| 5 | WorkflowView component | P1 | ✅ EXISTS | N/A |
| **P2 Gaps (Infrastructure) - IN PROGRESS** |
| 6 | WebSocket real-time updates | P2 | 🟡 PARTIAL | Medium |
| 7 | Event bus notifications | P2 | ❌ TODO | Medium |
| **UX Gaps (AI-First Transformation) - TODO** |
| 8 | Route architecture (UX paradigm) | **CRITICAL** | ❌ TODO | High |
| 9 | Visual AI-first hierarchy | **CRITICAL** | ❌ TODO | Low |
| 10 | CRUD views → context panels | **CRITICAL** | ❌ TODO | High |
| 11 | AI affordances in forms | P1 | ❌ TODO | Medium |
| 12 | Feedback & visibility | P1 | ❌ TODO | Medium |
| 13 | Gesture manipulation | P2 | ❌ TODO | High |
| 14 | Context panel UX improvements | P2 | ❌ TODO | Medium |

---

## Gap #6: WebSocket Real-Time Updates 🟡 PARTIAL

### Current State
- ✅ Backend WebSocket router exists (`/app/routers/websocket.py`)
- ✅ ConnectionManager implemented
- ✅ JWT authentication working
- ✅ Helper functions: `notify_task_update()`, `notify_new_message()`
- ❌ NOT integrated with AI tool execution
- ❌ NO frontend WebSocket client
- ❌ NO toast notification system

### Implementation Tasks

#### Backend Integration (ai.py)
**File**: `/backend/app/routers/ai.py`

**Changes Needed:**
1. Import WebSocket notification helpers:
```python
from app.routers.websocket import manager as websocket_manager
```

2. Send notifications after tool execution:
```python
# After creating task (line ~210)
if function_name == "create_task":
    task = Task(...)
    db.add(task)
    db.commit()
    db.refresh(task)

    # ✨ Send WebSocket notification
    await websocket_manager.send_personal_message({
        "type": "item_created",
        "entity": "task",
        "data": {
            "id": task.id,
            "title": task.title,
            "status": task.status.value
        }
    }, current_user.id)

    result = {"id": task.id, "title": task.title, "type": "task"}
```

3. Repeat for `create_knowledge_item` and `create_event`

#### Frontend WebSocket Client
**File**: `/frontend/src/lib/api/websocket.ts` (NEW)

**Implementation:**
```typescript
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';
import { toastStore } from '$lib/stores/toast';
import { contextPanelStore } from '$lib/stores/contextPanel';

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect() {
    const auth = get(authStore);
    if (!auth.token || !auth.user) {
      console.warn('[WS] No auth token, skipping WebSocket connection');
      return;
    }

    const wsUrl = `ws://localhost:8000/ws/${auth.user.id}?token=${auth.token}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('[WS] Connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error('[WS] Error:', error);
    };

    this.ws.onclose = () => {
      console.log('[WS] Disconnected');
      this.attemptReconnect();
    };
  }

  private handleMessage(message: any) {
    console.log('[WS] Message:', message);

    switch (message.type) {
      case 'connected':
        console.log('[WS]', message.message);
        break;

      case 'item_created':
        this.handleItemCreated(message.data, message.entity);
        break;

      case 'task_update':
        this.handleTaskUpdate(message.data);
        break;

      case 'chat_message':
        this.handleChatMessage(message.data);
        break;

      case 'pong':
        // Heartbeat response
        break;

      default:
        console.log('[WS] Unknown message type:', message.type);
    }
  }

  private handleItemCreated(data: any, entity: string) {
    // Show toast notification
    toastStore.add({
      type: 'success',
      message: `${entity} created: ${data.title}`,
      duration: 3000
    });

    // Auto-refresh panel if open
    const panelType = entity === 'task' ? 'tasks' :
                     entity === 'knowledge' ? 'knowledge' :
                     entity === 'event' ? 'calendar' : null;

    if (panelType) {
      // Trigger panel refresh
      contextPanelStore.refresh(panelType);
    }
  }

  private handleTaskUpdate(data: any) {
    toastStore.add({
      type: 'info',
      message: `Task updated: ${data.title}`,
      duration: 2000
    });
  }

  private handleChatMessage(data: any) {
    // Handle new chat messages
    console.log('[WS] New chat message:', data);
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WS] Max reconnect attempts reached');
      return;
    }

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
    this.reconnectAttempts++;

    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    setTimeout(() => this.connect(), delay);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(message: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('[WS] Not connected, cannot send message');
    }
  }

  // Send ping to keep connection alive
  ping() {
    this.send({ type: 'ping' });
  }
}

// Singleton instance
export const websocketClient = new WebSocket Client();
```

#### Toast Notification Store
**File**: `/frontend/src/lib/stores/toast.ts` (NEW)

**Implementation:**
```typescript
import { writable } from 'svelte/store';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number;
}

function createToastStore() {
  const { subscribe, update } = writable<Toast[]>([]);

  return {
    subscribe,
    add: (toast: Omit<Toast, 'id'>) => {
      const id = `toast-${Date.now()}`;
      const newToast: Toast = { id, ...toast };

      update(toasts => [...toasts, newToast]);

      // Auto-remove after duration
      if (toast.duration) {
        setTimeout(() => {
          update(toasts => toasts.filter(t => t.id !== id));
        }, toast.duration);
      }
    },
    remove: (id: string) => {
      update(toasts => toasts.filter(t => t.id !== id));
    },
    clear: () => {
      update(() => []);
    }
  };
}

export const toastStore = createToastStore();
```

#### Toast Component
**File**: `/frontend/src/lib/components/ToastStack.svelte` (ALREADY EXISTS)

Integration in `/frontend/src/routes/dashboard/+layout.svelte`:
```svelte
<script>
  import ToastStack from '$lib/components/ToastStack.svelte';
  import { websocketClient } from '$lib/api/websocket';
  import { onMount, onDestroy } from 'svelte';

  onMount(() => {
    websocketClient.connect();

    // Keep connection alive with pings
    const pingInterval = setInterval(() => {
      websocketClient.ping();
    }, 30000); // Every 30 seconds

    return () => {
      clearInterval(pingInterval);
    };
  });

  onDestroy(() => {
    websocketClient.disconnect();
  });
</script>

<ToastStack />
<!-- Rest of layout -->
```

### Completion Criteria
- [x] WebSocket backend exists
- [ ] AI tool execution sends WebSocket notifications
- [ ] Frontend WebSocket client implemented
- [ ] Toast notification system working
- [ ] Real-time updates visible in UI

---

## Gap #7: Event Bus Notifications ❌ TODO

### Purpose
Allow backend services (agent-tools, scheduled tasks) to publish events that trigger frontend updates via WebSocket.

### Implementation

#### Backend Event Bus
**File**: `/backend/app/core/event_bus.py` (NEW)

```python
from typing import Callable, Dict, List
import asyncio
from datetime import datetime

class EventBus:
    """Simple in-memory event bus for internal notifications"""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def publish(self, event_type: str, data: dict):
        """Publish an event to all subscribers"""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    print(f"Error in event callback: {e}")

# Singleton instance
event_bus = EventBus()
```

#### Integration with WebSocket
**File**: `/backend/app/routers/websocket.py`

```python
from app.core.event_bus import event_bus

# Subscribe to events on startup
async def on_startup():
    # When task is created/updated, notify via WebSocket
    event_bus.subscribe('task.created', lambda data:
        manager.send_personal_message({
            "type": "task_update",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }, data.get('user_id'))
    )

    event_bus.subscribe('knowledge.created', lambda data:
        manager.send_personal_message({
            "type": "knowledge_update",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }, data.get('user_id'))
    )
```

#### Usage in Agent Tools
**File**: `/backend/app/routers/agent_tools.py`

```python
from app.core.event_bus import event_bus

@router.post("/tools/create-task")
async def create_task_tool(...):
    task = Task(...)
    db.add(task)
    db.commit()

    # Publish event
    await event_bus.publish('task.created', {
        'user_id': current_user.id,
        'task_id': task.id,
        'title': task.title,
        'status': task.status.value
    })

    return task
```

### Completion Criteria
- [ ] EventBus class implemented
- [ ] WebSocket subscribed to event bus
- [ ] Agent tools publish events
- [ ] Frontend receives notifications

---

## Gap #8: Route Architecture (CRITICAL UX) ❌ TODO

### Problem
Traditional CRUD pages (`/tasks`, `/knowledge`, `/projects`) compete with AI-first canvas, violating the core vision.

### Solution: Pragmatic Approach (Option B)

#### 1. Make /dashboard the Primary Interface

**File**: `/frontend/src/routes/dashboard/+layout.svelte`

Keep UnifiedCanvas always visible, CRUD panels slide in on top.

#### 2. Convert CRUD Routes to Panel Openers

**File**: `/frontend/src/routes/dashboard/tasks/+page.svelte`

**BEFORE** (444 lines of CRUD UI):
```svelte
<script>
  // Full TasksView component
</script>

<TasksView />
```

**AFTER** (redirect to dashboard + open panel):
```svelte
<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { contextPanelStore } from '$lib/stores/contextPanel';

  onMount(() => {
    // Open tasks panel
    contextPanelStore.open('tasks');

    // Redirect to main dashboard
    goto('/dashboard', { replaceState: true });
  });
</script>

<!-- No UI - just redirect logic -->
```

Repeat for:
- `/dashboard/knowledge/+page.svelte`
- `/dashboard/projects/+page.svelte`
- `/dashboard/calendar/+page.svelte`

#### 3. Update Navigation Links

**File**: `/frontend/src/routes/dashboard/+layout.svelte`

**BEFORE**:
```svelte
<a href="/dashboard/tasks">Tasks</a>
```

**AFTER**:
```svelte
<button on:click={() => contextPanelStore.open('tasks')}>
  Tasks
</button>
```

#### 4. Deep Link Support

**File**: `/frontend/src/routes/dashboard/+page.svelte`

```svelte
<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';

  onMount(() => {
    const panel = $page.url.searchParams.get('panel');
    if (panel) {
      contextPanelStore.open(panel as any);
    }
  });
</script>
```

Now `/dashboard?panel=tasks` opens the tasks panel.

### Completion Criteria
- [ ] /dashboard is the default route
- [ ] /tasks, /knowledge, /projects redirect + open panels
- [ ] Navigation uses `contextPanelStore.open()` instead of hrefs
- [ ] Deep links work: `/dashboard?panel=tasks`
- [ ] UnifiedCanvas always visible

---

## Gap #9: Visual AI-First Hierarchy ❌ TODO

### Implementation

**File**: `/frontend/src/routes/dashboard/+page.svelte`

**Add prominent AI Command Center branding:**

```svelte
<div class="min-h-screen bg-background p-6">
  <!-- AI Command Center Header -->
  <header class="mb-8 text-center">
    <div class="inline-block brutal-card px-6 py-3 bg-accent text-accent-foreground">
      <h1 class="text-2xl font-black uppercase tracking-tighter flex items-center gap-2">
        <Sparkles class="w-6 h-6" />
        AI Command Center
      </h1>
      <p class="text-xs uppercase font-bold opacity-80 tracking-widest mt-1">
        Create via AI · Manage via Gestures
      </p>
    </div>
  </header>

  <!-- UnifiedCanvas (PRIMARY) -->
  <div class="max-w-4xl mx-auto">
    <UnifiedCanvas ... />
  </div>

  <!-- Quick Links (SECONDARY, de-emphasized) -->
  <aside class="mt-12 text-center">
    <p class="text-[10px] uppercase font-bold text-muted-foreground tracking-widest mb-3 opacity-40">
      Advanced Tools (Optional)
    </p>
    <div class="flex gap-2 justify-center opacity-60">
      <button on:click={() => contextPanelStore.open('tasks')} class="brutal-btn text-xs">
        Tasks
      </button>
      <button on:click={() => contextPanelStore.open('knowledge')} class="brutal-btn text-xs">
        Knowledge
      </button>
      <button on:click={() => contextPanelStore.open('calendar')} class="brutal-btn text-xs">
        Calendar
      </button>
    </div>
  </aside>
</div>
```

### Completion Criteria
- [ ] "AI Command Center" header prominent
- [ ] "Create via AI · Manage via Gestures" tagline visible
- [ ] UnifiedCanvas is visually primary
- [ ] Quick links de-emphasized (small, low contrast)
- [ ] Onboarding tooltip: "Try typing: Create a task for..."

---

## Gap #10: CRUD Views → Context Panels ❌ TODO

### Implementation

Already partially done - CRUD views exist as components:
- `TasksView.svelte` - shown in tasks panel
- `KnowledgeView.svelte` - shown in knowledge panel
- `ProjectsView.svelte` - shown in projects panel

**What's needed:** Ensure they're ONLY shown in panels, never as standalone pages (Gap #8 handles this).

### Completion Criteria
- [x] TasksView exists as panel component
- [x] KnowledgeView exists as panel component
- [x] ProjectsView exists as panel component
- [ ] No standalone CRUD pages (removed by Gap #8)
- [ ] All CRUD only via context panels

---

## Gap #11: AI Affordances in Forms ❌ TODO

### Implementation

Add "Ask AI" buttons to form fields in TasksView, KnowledgeView, etc.

**File**: `/frontend/src/lib/components/dashboard/TasksView.svelte`

**Example for title field:**

```svelte
<div class="flex gap-2">
  <input
    type="text"
    bind:value={formData.title}
    placeholder="Task title"
    class="flex-1 brutal-border px-3 py-2"
  />
  <button
    on:click={async () => {
      const suggestion = await api.ai.suggestTaskTitle(formData.description);
      formData.title = suggestion;
    }}
    class="brutal-btn bg-accent text-accent-foreground px-4"
    title="Ask AI for title suggestion"
  >
    <Sparkles class="w-4 h-4" />
    Ask AI
  </button>
</div>
```

### Completion Criteria
- [ ] "Ask AI" buttons in task forms
- [ ] "Ask AI" buttons in knowledge forms
- [ ] AI suggestions for titles/descriptions
- [ ] Intelligent defaults (priority, due dates)

---

## Gap #12: Feedback & Visibility ❌ TODO

### Components Needed

#### 1. Loading States

**File**: `/frontend/src/lib/components/LoadingSpinner.svelte` (NEW)

```svelte
<script>
  export let size: 'sm' | 'md' | 'lg' = 'md';
</script>

<div class="loading-spinner {size}">
  <div class="brutal-border border-4 border-t-primary animate-spin"></div>
</div>

<style>
  .loading-spinner {
    display: inline-block;
  }
  .loading-spinner div {
    width: 24px;
    height: 24px;
  }
  .loading-spinner.sm div {
    width: 16px;
    height: 16px;
    border-width: 2px;
  }
  .loading-spinner.lg div {
    width: 32px;
    height: 32px;
  }
</style>
```

#### 2. Error Boundaries

Svelte doesn't have built-in error boundaries, but we can use try/catch:

```svelte
<script>
  let error: string | null = null;

  async function handleAction() {
    try {
      error = null;
      await performAction();
    } catch (e: any) {
      error = e.message;
      toastStore.add({ type: 'error', message: e.message, duration: 5000 });
    }
  }
</script>

{#if error}
  <div class="brutal-card bg-destructive text-destructive-foreground p-4">
    <p class="font-bold uppercase">Error</p>
    <p class="text-sm">{error}</p>
    <button on:click={() => error = null} class="brutal-btn mt-2">
      Dismiss
    </button>
  </div>
{/if}
```

#### 3. Undo/Redo

**File**: `/frontend/src/lib/stores/undo.ts` (NEW)

```typescript
import { writable } from 'svelte/store';

interface UndoAction {
  type: string;
  undo: () => Promise<void>;
  redo: () => Promise<void>;
  description: string;
}

function createUndoStore() {
  const { subscribe, update } = writable<{
    past: UndoAction[];
    future: UndoAction[];
  }>({ past: [], future: [] });

  return {
    subscribe,
    push: (action: UndoAction) => {
      update(state => ({
        past: [...state.past, action],
        future: [] // Clear redo stack
      }));

      // Show toast with undo option
      toastStore.add({
        type: 'info',
        message: `${action.description} - Click to undo`,
        duration: 5000,
        action: () => undoStore.undo()
      });
    },
    undo: async () => {
      let action: UndoAction | undefined;
      update(state => {
        action = state.past.pop();
        if (action) {
          return {
            past: state.past,
            future: [action, ...state.future]
          };
        }
        return state;
      });
      if (action) {
        await action.undo();
      }
    },
    redo: async () => {
      let action: UndoAction | undefined;
      update(state => {
        action = state.future.shift();
        if (action) {
          return {
            past: [...state.past, action],
            future: state.future
          };
        }
        return state;
      });
      if (action) {
        await action.redo();
      }
    }
  };
}

export const undoStore = createUndoStore();
```

### Completion Criteria
- [ ] Loading spinners during AI operations
- [ ] Error messages with retry/dismiss options
- [ ] Undo/redo for create/delete operations
- [ ] Toast notifications with action buttons

---

## Gap #13: Gesture Manipulation ❌ TODO

### Implementation

#### 1. Drag-and-Drop

**Library**: `@neodrag/svelte` (brutalist-friendly, no animations needed)

```bash
cd frontend && pnpm add @neodrag/svelte
```

**Usage in TasksView**:

```svelte
<script>
  import { useDraggable } from '@neodrag/svelte';

  function handleDragEnd(task: Task, newStatus: string) {
    api.tasks.update(task.id, { status: newStatus });
    toastStore.add({ type: 'success', message: `Task moved to ${newStatus}` });
  }
</script>

{#each tasks as task}
  <div
    use:draggable
    on:neodrag:end={(e) => handleDragEnd(task, getDropZone(e.detail.currentNode))}
    class="brutal-card p-4 cursor-move"
  >
    {task.title}
  </div>
{/each}
```

#### 2. Keyboard Shortcuts

**File**: `/frontend/src/lib/utils/keyboard.ts` (NEW)

```typescript
export function registerKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K: Open command palette
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      commandPaletteStore.toggle();
    }

    // Ctrl/Cmd + T: Open tasks
    if ((e.ctrlKey || e.metaKey) && e.key === 't') {
      e.preventDefault();
      contextPanelStore.open('tasks');
    }

    // Ctrl/Cmd + N: New task (when tasks panel open)
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
      e.preventDefault();
      const panelType = get(contextPanelStore).type;
      if (panelType === 'tasks') {
        // Open create modal
      }
    }

    // Ctrl/Cmd + Z: Undo
    if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
      e.preventDefault();
      undoStore.undo();
    }

    // Ctrl/Cmd + Shift + Z: Redo
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'z') {
      e.preventDefault();
      undoStore.redo();
    }
  });
}
```

#### 3. Bulk Operations

**File**: `/frontend/src/lib/components/dashboard/TasksView.svelte`

```svelte
<script>
  let selectedTasks: Set<string> = new Set();

  function toggleSelect(taskId: string) {
    if (selectedTasks.has(taskId)) {
      selectedTasks.delete(taskId);
    } else {
      selectedTasks.add(taskId);
    }
    selectedTasks = selectedTasks; // Trigger reactivity
  }

  async function bulkDelete() {
    const ids = Array.from(selectedTasks);
    await Promise.all(ids.map(id => api.tasks.delete(id)));
    selectedTasks.clear();
    toastStore.add({ type: 'success', message: `Deleted ${ids.length} tasks` });
  }

  async function bulkArchive() {
    const ids = Array.from(selectedTasks);
    await Promise.all(ids.map(id => api.tasks.update(id, { archived: true })));
    selectedTasks.clear();
    toastStore.add({ type: 'success', message: `Archived ${ids.length} tasks` });
  }
</script>

{#if selectedTasks.size > 0}
  <div class="brutal-card p-4 mb-4 bg-accent text-accent-foreground">
    <p class="font-bold uppercase">{selectedTasks.size} tasks selected</p>
    <div class="flex gap-2 mt-2">
      <button on:click={bulkDelete} class="brutal-btn bg-destructive">
        Delete
      </button>
      <button on:click={bulkArchive} class="brutal-btn">
        Archive
      </button>
      <button on:click={() => selectedTasks.clear()} class="brutal-btn">
        Cancel
      </button>
    </div>
  </div>
{/if}

{#each tasks as task}
  <div class="brutal-card p-4">
    <input
      type="checkbox"
      checked={selectedTasks.has(task.id)}
      on:change={() => toggleSelect(task.id)}
    />
    {task.title}
  </div>
{/each}
```

### Completion Criteria
- [ ] Drag-and-drop for tasks/knowledge items
- [ ] Keyboard shortcuts documented and working
- [ ] Bulk select + operations (delete, archive, change status)
- [ ] Inline editing (click title to edit)

---

## Gap #14: Context Panel UX Improvements ❌ TODO

### Implementation

#### 1. Scroll Position Memory

**File**: `/frontend/src/lib/stores/contextPanel.ts`

```typescript
interface PanelState {
  type: PanelType | null;
  data: any;
  scrollPosition: number; // NEW
  width: number; // NEW (for resize)
}

function createContextPanelStore() {
  const { subscribe, update } = writable<PanelState>({
    type: null,
    data: null,
    scrollPosition: 0,
    width: 800
  });

  return {
    subscribe,
    open: (type: PanelType, data?: any) => {
      update(state => ({
        ...state,
        type,
        data: data || null,
        scrollPosition: 0 // Reset on open
      }));
    },
    close: () => {
      update(state => ({ ...state, type: null, data: null }));
    },
    saveScrollPosition: (position: number) => {
      update(state => ({ ...state, scrollPosition: position }));
    },
    restoreScrollPosition: () => {
      // Called after panel content renders
    },
    setWidth: (width: number) => {
      update(state => ({ ...state, width }));
    }
  };
}
```

#### 2. Panel Resize

**File**: `/frontend/src/lib/components/ContextPanel.svelte`

```svelte
<script>
  let panelWidth = $contextPanelStore.width;
  let isResizing = false;

  function startResize(e: MouseEvent) {
    isResizing = true;
    document.addEventListener('mousemove', handleResize);
    document.addEventListener('mouseup', stopResize);
  }

  function handleResize(e: MouseEvent) {
    if (!isResizing) return;
    const newWidth = window.innerWidth - e.clientX;
    panelWidth = Math.max(400, Math.min(1200, newWidth));
  }

  function stopResize() {
    isResizing = false;
    contextPanelStore.setWidth(panelWidth);
    document.removeEventListener('mousemove', handleResize);
    document.removeEventListener('mouseup', stopResize);
  }
</script>

<div
  class="fixed right-0 top-0 h-full brutal-card"
  style="width: {panelWidth}px"
>
  <!-- Resize handle -->
  <div
    class="absolute left-0 top-0 h-full w-2 cursor-col-resize bg-border hover:bg-primary"
    on:mousedown={startResize}
  />

  <!-- Panel content -->
  <div class="pl-2 h-full overflow-auto">
    <ContextPanelContent />
  </div>
</div>
```

#### 3. Panel Pinning

**File**: `/frontend/src/lib/stores/contextPanel.ts`

```typescript
interface PanelState {
  type: PanelType | null;
  data: any;
  scrollPosition: number;
  width: number;
  isPinned: boolean; // NEW
}

function createContextPanelStore() {
  // ...
  return {
    // ...
    pin: () => {
      update(state => ({ ...state, isPinned: true }));
    },
    unpin: () => {
      update(state => ({ ...state, isPinned: false }));
    }
  };
}
```

#### 4. Multi-Panel View (Side-by-Side)

**Advanced feature** - Allow 2 panels open simultaneously:

```svelte
<div class="grid grid-cols-2 gap-4">
  <ContextPanel slot="left" type={leftPanelType} />
  <ContextPanel slot="right" type={rightPanelType} />
</div>
```

### Completion Criteria
- [ ] Scroll position remembered when closing/opening panels
- [ ] Panels can be resized by dragging edge
- [ ] Panels can be pinned (stay open, don't auto-close)
- [ ] Multi-panel view for side-by-side comparison (advanced)

---

## Implementation Priority

### Phase 1: Infrastructure (P2 Gaps)
**Timeline**: 1-2 days

1. ✅ WebSocket backend exists
2. ⏳ Integrate WebSocket with AI tool execution
3. ⏳ Create frontend WebSocket client
4. ⏳ Implement toast notification system
5. ⏳ Create event bus for backend services

**Deliverables**:
- Real-time updates working
- Toast notifications on item creation
- Event bus for future features

### Phase 2: UX Transformation (Gaps #8, #9, #10)
**Timeline**: 2-3 days

1. ⏳ Redesign route architecture
2. ⏳ Add AI Command Center branding
3. ⏳ Ensure CRUD only via panels
4. ⏳ Test deep links and navigation

**Deliverables**:
- AI-first UX paradigm enforced
- UnifiedCanvas is primary interface
- Forms are secondary escape hatches

### Phase 3: Feedback & Discoverability (Gaps #11, #12)
**Timeline**: 1-2 days

1. ⏳ Add "Ask AI" buttons to forms
2. ⏳ Implement loading states
3. ⏳ Add error recovery
4. ⏳ Implement undo/redo

**Deliverables**:
- AI capabilities discoverable in forms
- Better feedback during operations
- Undo support for safety

### Phase 4: Advanced UX (Gaps #13, #14)
**Timeline**: 2-3 days

1. ⏳ Implement drag-and-drop
2. ⏳ Add keyboard shortcuts
3. ⏳ Enable bulk operations
4. ⏳ Panel scroll memory
5. ⏳ Panel resize
6. ⏳ Panel pinning

**Deliverables**:
- Gesture-based manipulation working
- Keyboard power-user features
- Panel UX polished

---

## Success Metrics

### Before (Baseline)
- **AI Usage**: 20% of actions via AI, 80% via forms
- **Primary Interface**: Direct CRUD routes
- **Real-time Updates**: None (manual refresh)
- **Orchestration Score**: 4/10 (40%)

### After (Target)
- **AI Usage**: 80% of actions via AI, 20% via forms
- **Primary Interface**: UnifiedCanvas with dynamic panels
- **Real-time Updates**: WebSocket + toast notifications
- **Orchestration Score**: 10/10 (100%)

---

## Completion Checklist

### P2 Infrastructure
- [ ] WebSocket integrated with AI tool execution
- [ ] Frontend WebSocket client implemented
- [ ] Toast notification system working
- [ ] Event bus implemented and integrated

### UX Transformation (CRITICAL)
- [ ] /dashboard is primary route
- [ ] CRUD routes redirect + open panels
- [ ] AI Command Center branding visible
- [ ] UnifiedCanvas always in view
- [ ] Deep links working

### Feedback & Discoverability
- [ ] "Ask AI" buttons in forms
- [ ] Loading states during operations
- [ ] Error recovery with retry
- [ ] Undo/redo for safety

### Advanced UX
- [ ] Drag-and-drop working
- [ ] Keyboard shortcuts documented
- [ ] Bulk operations enabled
- [ ] Panel scroll memory
- [ ] Panel resize capability
- [ ] Panel pinning

---

**Document Status**: Implementation Roadmap
**Next Action**: Begin Phase 1 (Infrastructure)
**Owner**: Claude Code + User
**Target Completion**: 1-2 weeks for all gaps
