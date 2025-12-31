# Track 3: Assistant/Voice Unification - Architecture

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Dashboard Page (+page.svelte)                        │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                           UnifiedCanvas                                 │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │                     Message Stream                                │  │ │
│  │  │  ┌──────────────────────────────────────────────────────────┐   │  │ │
│  │  │  │ User Message (text/voice)                                │   │  │ │
│  │  │  │   "Create a task for deploying the new feature"          │   │  │ │
│  │  │  └──────────────────────────────────────────────────────────┘   │  │ │
│  │  │  ┌──────────────────────────────────────────────────────────┐   │  │ │
│  │  │  │ [Thinking] Analyzing request and planning workflow...    │   │  │ │
│  │  │  └──────────────────────────────────────────────────────────┘   │  │ │
│  │  │  ┌──────────────────────────────────────────────────────────┐   │  │ │
│  │  │  │ [Tool] create_task (running)                             │   │  │ │
│  │  │  │   args: { title: "Deploy new feature", ... }             │   │  │ │
│  │  │  └──────────────────────────────────────────────────────────┘   │  │ │
│  │  │  ┌──────────────────────────────────────────────────────────┐   │  │ │
│  │  │  │ Assistant Response (streaming)                           │   │  │ │
│  │  │  │   "I've created a deployment task. Here's the plan..."   │   │  │ │
│  │  │  └──────────────────────────────────────────────────────────┘   │  │ │
│  │  │  ┌──────────────────────────────────────────────────────────┐   │  │ │
│  │  │  │ [Workflow Preview]                                       │   │  │ │
│  │  │  │   Deploy Feature (95% confidence)                        │   │  │ │
│  │  │  │   [View Details] →                                       │   │  │ │
│  │  │  └──────────────────────────────────────────────────────────┘   │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    AssistantComposer                              │  │ │
│  │  │  [Text Input] [🎤 Record] [Mode: II-Agent ▼] [Model ▼]          │  │ │
│  │  │  Quick: [Summarize tasks] [Plan week] [Schedule meeting]         │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌────────────────────────┐              ┌───────────────────────────┐      │
│  │   WorkflowDrawer       │              │   ExecutionDrawer         │      │
│  │  (overlay, z-50)       │              │   (overlay, z-50)         │      │
│  │                        │              │                           │      │
│  │  Deploy Feature        │              │  Task: Deploy to Prod     │      │
│  │  ──────────────        │              │  ────────────────────     │      │
│  │  Step 1: Run tests ✓   │              │  Status: Pending          │      │
│  │  Step 2: Build (●) ... │              │  Due: Friday 3pm          │      │
│  │  Step 3: Deploy ...    │              │                           │      │
│  │                        │              │  [Edit] [Complete]        │      │
│  │  Artifacts:            │              │  [Send to Assistant]      │      │
│  │  - Docker image        │              │  [Delete]                 │      │
│  │  - Deploy script       │              │                           │      │
│  │                        │              │  [Close]                  │      │
│  │  [Approve] [Revise]    │              │                           │      │
│  │  [Send to Assistant]   │              │                           │      │
│  └────────────────────────┘              └───────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
              ┌─────────────────────────────────────────┐
              │         assistantStore (Svelte)         │
              │  ┌───────────────────────────────────┐  │
              │  │ messages: AssistantMessage[]      │  │
              │  │   [user, assistant, system, ...]  │  │
              │  ├───────────────────────────────────┤  │
              │  │ workflows: Record<id, Workflow>   │  │
              │  │   { wf1: {...}, wf2: {...} }      │  │
              │  ├───────────────────────────────────┤  │
              │  │ executionFeed: ExecutionEntry[]   │  │
              │  │   [task1, knowledge1, event1, ...]│  │
              │  ├───────────────────────────────────┤  │
              │  │ composerState: {                  │  │
              │  │   mode: 'ii-agent',               │  │
              │  │   isRecording: false,             │  │
              │  │   isProcessing: false             │  │
              │  │ }                                 │  │
              │  ├───────────────────────────────────┤  │
              │  │ iiAgentState: {                   │  │
              │  │   isConnected: true,              │  │
              │  │   isInitialized: true,            │  │
              │  │   eventLog: [...]                 │  │
              │  │ }                                 │  │
              │  ├───────────────────────────────────┤  │
              │  │ drawerState: {                    │  │
              │  │   workflowDrawerOpen: false,      │  │
              │  │   executionDrawerOpen: false      │  │
              │  │ }                                 │  │
              │  └───────────────────────────────────┘  │
              │                                         │
              │  Derived Stores:                        │
              │  - activeWorkflow                       │
              │  - latestWorkflow                       │
              │  - isProcessing                         │
              └─────────────────────────────────────────┘
                          │                 │
        ┌─────────────────┘                 └──────────────────┐
        ▼                                                       ▼
┌─────────────────────────┐                     ┌──────────────────────────┐
│  IIAgentIntegration     │                     │  API Client (REST)       │
│  ┌───────────────────┐  │                     │  ┌────────────────────┐  │
│  │ IIAgentClient     │  │                     │  │ /ai/chat           │  │
│  │  (WebSocket)      │  │                     │  │ /ai/orchestrate    │  │
│  │                   │  │                     │  │ /assistant/voice   │  │
│  │ Event Handlers:   │  │                     │  │ /tasks/*           │  │
│  │ - onEvent()       │  │                     │  │ /knowledge/*       │  │
│  │ - onError()       │  │                     │  │ /calendar/*        │  │
│  │ - onClose()       │  │                     │  └────────────────────┘  │
│  │                   │  │                     │                          │
│  │ Methods:          │  │                     │  Focus by Kraliki Backend API  │
│  │ - connect()       │  │                     │                          │
│  │ - sendQuery()     │  │                     └──────────────────────────┘
│  │ - cancel()        │  │                                  │
│  └───────────────────┘  │                                  ▼
│                         │                     ┌──────────────────────────┐
│  Tool Extraction:       │                     │  PostgreSQL Database     │
│  - create_task          │                     │  - tasks                 │
│  - create_knowledge     │                     │  - knowledge_items       │
│  - create_event         │                     │  - calendar_events       │
│  → executionFeed        │                     │  - telemetry             │
└─────────────────────────┘                     └──────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│   II-Agent Server (Python)          │
│   ws://127.0.0.1:8765/ws            │
│  ┌───────────────────────────────┐  │
│  │ Events:                       │  │
│  │ - connection_established      │  │
│  │ - agent_initialized           │  │
│  │ - processing                  │  │
│  │ - agent_thinking              │  │
│  │ - tool_call                   │  │
│  │ - tool_result                 │  │
│  │ - agent_response (streaming)  │  │
│  │ - stream_complete             │  │
│  │ - error                       │  │
│  └───────────────────────────────┘  │
│                                     │
│  Focus Tools:                       │
│  - create_task()                    │
│  - update_task()                    │
│  - create_knowledge_item()          │
│  - create_calendar_event()          │
│  - search_knowledge()               │
└─────────────────────────────────────┘
```

## Data Flow Diagram

### 1. User Sends Message (Text)

```
User Input
    │
    ▼
UnifiedCanvas.handleSend()
    │
    ├──→ assistantStore.addMessage({ role: 'user', ... })
    │
    └──→ Check mode
            │
            ├─ II-Agent Mode
            │     │
            │     ▼
            │  IIAgentIntegration.sendQuery()
            │     │
            │     ▼
            │  IIAgentClient.sendQuery() → WebSocket
            │
            ├─ Orchestrated Mode
            │     │
            │     ▼
            │  api.ai.orchestrateTask()
            │     │
            │     └──→ assistantStore.addWorkflow()
            │
            └─ Deterministic Mode
                  │
                  ▼
               api.ai.chat()
                  │
                  └──→ assistantStore.addMessage({ role: 'assistant', ... })
```

### 2. II-Agent Streaming Response

```
II-Agent Server
    │
    ▼
WebSocket Event
    │
    ▼
IIAgentClient.onmessage()
    │
    ▼
IIAgentIntegration.handleEvent()
    │
    ├─ AGENT_THINKING
    │     │
    │     └──→ assistantStore.addMessage({ metadata: { thinking: '...' } })
    │
    ├─ TOOL_CALL
    │     │
    │     ├──→ assistantStore.updateMessage({ metadata: { toolCalls: [...] } })
    │     │
    │     └──→ extractExecutionFromToolCall()
    │              │
    │              └──→ assistantStore.addExecutionEntry()
    │
    ├─ AGENT_RESPONSE
    │     │
    │     └──→ assistantStore.updateMessage({ content: content + newText })
    │
    ├─ TOOL_RESULT
    │     │
    │     └──→ assistantStore.updateMessage({
    │               metadata: {
    │                   toolCalls: [{ ...tc, status: 'completed', result }]
    │               }
    │           })
    │
    └─ STREAM_COMPLETE
          │
          └──→ assistantStore.setIIAgentProcessing(false)
```

### 3. Voice Recording Flow

```
User Presses Record
    │
    ▼
UnifiedCanvas emits 'record'
    │
    ▼
Parent Component (Dashboard)
    │
    ├──→ navigator.mediaDevices.getUserMedia()
    │         │
    │         └──→ MediaRecorder.start()
    │
    └──→ assistantStore.setRecording(true)

User Stops Recording
    │
    ▼
UnifiedCanvas emits 'stop'
    │
    ▼
Parent Component
    │
    ├──→ MediaRecorder.stop()
    │         │
    │         └──→ ondataavailable → audioChunks[]
    │
    ├──→ Blob(audioChunks)
    │         │
    │         └──→ blobToBase64()
    │
    ├──→ api.assistant.processVoice({ audioData, mimetype })
    │         │
    │         └──→ { transcript, response }
    │
    └──→ assistantStore.addMessage({ content: transcript, source: 'voice' })
          assistantStore.addMessage({ content: response, source: 'voice' })
```

### 4. Workflow Approval Flow

```
User Clicks "View Details" on Workflow Preview
    │
    ▼
assistantStore.openWorkflowDrawer(workflowId)
    │
    └──→ $assistantStore.drawerState.workflowDrawerOpen = true
              $assistantStore.drawerState.selectedWorkflowId = workflowId

WorkflowDrawer Opens
    │
    ├──→ Displays: steps, artifacts, confidence, decision status
    │
    └──→ User clicks "Approve"
              │
              ▼
         WorkflowDrawer emits 'approve'
              │
              ▼
         UnifiedCanvas handles event
              │
              ├──→ assistantStore.updateWorkflowDecision(workflowId, 'approved')
              │
              └──→ Parent component calls api.ai.recordWorkflowDecision()
```

### 5. Execution Entry Editing Flow

```
User Clicks Execution Entry in Feed
    │
    ▼
assistantStore.openExecutionDrawer(entryId)
    │
    └──→ $assistantStore.drawerState.executionDrawerOpen = true
              $assistantStore.drawerState.selectedExecutionId = entryId

ExecutionDrawer Opens
    │
    ├──→ Loads entry details
    │
    └──→ User clicks "Edit"
              │
              ├──→ Shows edit form
              │
              └──→ User modifies fields and clicks "Save"
                        │
                        ▼
                   ExecutionDrawer emits 'save'
                        │
                        ├──→ assistantStore.updateExecutionEntry(entryId, updates)
                        │
                        └──→ Parent calls api.tasks.update(entryId, updates)
```

## State Synchronization

### Store → UI (Reactive)

```
assistantStore ($assistantStore)
    │
    ├──→ UnifiedCanvas
    │      ├─ messages → Message list
    │      ├─ composerState.isProcessing → Loading indicator
    │      ├─ iiAgentState.isConnected → Connection badge
    │      └─ drawerState.* → Drawer visibility
    │
    ├──→ WorkflowDrawer
    │      └─ workflows[selectedWorkflowId] → Workflow details
    │
    └──→ ExecutionDrawer
           └─ executionFeed[selectedExecutionId] → Entry details
```

### UI → Store (Actions)

```
Component Actions
    │
    ├──→ assistantStore.addMessage()
    ├──→ assistantStore.updateMessage()
    ├──→ assistantStore.addWorkflow()
    ├──→ assistantStore.updateWorkflowDecision()
    ├──→ assistantStore.addExecutionEntry()
    ├──→ assistantStore.updateExecutionEntry()
    ├──→ assistantStore.setIIAgentConnection()
    ├──→ assistantStore.setIIAgentProcessing()
    ├──→ assistantStore.openWorkflowDrawer()
    └──→ assistantStore.openExecutionDrawer()
```

## Component Lifecycle

### UnifiedCanvas

```
onMount()
    │
    ├──→ Create IIAgentClient instance
    ├──→ Register event listeners
    ├──→ scrollToBottom()
    └──→ Auto-connect if II-Agent mode

User Interaction
    │
    ├──→ Type message → handleSend()
    ├──→ Click record → handleVoiceRecord()
    ├──→ Switch mode → handleModeChange()
    └──→ Select model → handleModelChange()

onDestroy()
    │
    ├──→ Unsubscribe event listeners
    └──→ iiAgentClient.disconnect()
```

### WorkflowDrawer

```
open = true
    │
    ├──→ Load workflow from store ($assistantStore.workflows[workflowId])
    ├──→ Render steps with status icons
    ├──→ Display artifacts
    └──→ Show decision controls

User Actions
    │
    ├──→ Approve → emit 'approve' event
    ├──→ Revise → emit 'revise' event
    ├──→ Inspect artifact → emit 'inspectArtifact' event
    └──→ Send to assistant → emit 'sendToAssistant' event

close()
    │
    └──→ assistantStore.closeWorkflowDrawer()
```

### ExecutionDrawer

```
open = true
    │
    ├──→ Load entry from store ($assistantStore.executionFeed[entryId])
    ├──→ Initialize edit form
    └──→ Display entry details

Edit Flow
    │
    ├──→ startEdit() → show form
    ├──→ User modifies fields
    ├──→ saveEdit()
    │      ├──→ Validate
    │      ├──→ Update store
    │      └──→ Emit 'save' event
    └──→ cancelEdit() → reset form

close()
    │
    └──→ assistantStore.closeExecutionDrawer()
```

## Error Handling

```
Error Source
    │
    ├─ WebSocket Connection Error
    │     │
    │     ├──→ IIAgentClient.onerror
    │     ├──→ IIAgentIntegration.handleError()
    │     ├──→ assistantStore.setIIAgentError(message)
    │     └──→ UnifiedCanvas displays error badge
    │
    ├─ II-Agent Event Error
    │     │
    │     ├──→ EventType.ERROR
    │     ├──→ assistantStore.addMessage({ role: 'system', content: error })
    │     └──→ UnifiedCanvas displays error message
    │
    ├─ API Call Error
    │     │
    │     ├──→ try/catch in parent component
    │     └──→ Display toast/notification
    │
    └─ Form Validation Error
          │
          ├──→ ExecutionDrawer shows inline error
          └──→ Prevents save
```

## Performance Optimizations

### 1. Derived Stores (Memoization)

```typescript
// Only recomputes when workflows change
export const latestWorkflow = derived(
  assistantStore,
  $state => {
    const workflows = Object.values($state.workflows);
    return workflows.sort(...)[0];
  }
);
```

### 2. Message Limiting

```typescript
// Only show recent messages to reduce DOM size
export const recentMessages = derived(
  assistantStore,
  $state => $state.messages.slice(-20)
);
```

### 3. Lazy Loading

```svelte
{#if open}
  <WorkflowDrawer ... />
{/if}
```

### 4. Event Batching

```typescript
// Debounce auto-scroll
let scrollTimeout;
function scrollToBottom() {
  clearTimeout(scrollTimeout);
  scrollTimeout = setTimeout(() => {
    container.scrollTop = container.scrollHeight;
  }, 50);
}
```

---

**Architecture Status**: ✅ Complete
**Next**: Dashboard integration and end-to-end testing
