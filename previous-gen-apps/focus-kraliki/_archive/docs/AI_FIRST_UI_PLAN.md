# AI-First Command Center UI Plan

This document captures a concrete direction for turning Focus Lite into an AI-first productivity assistant where text/voice conversations are the primary way to operate the workspace and orchestrator insights are surfaced inline. It is structured so the team can iterate in vertical slices while always validating the experience with the integration suite.

## Experience Pillars

- **Single assistant surface:** Users should feel like they talk to one assistant that can hear, plan, and act. Whether the user types, records audio, or toggles orchestration, all flows should pass through the same conversation context.
- **Continuous context:** Conversation history, orchestrated workflows, and recent outcomes must stay visible without bouncing across tabs. Task/calendar/status views should feel like secondary canvases that react to the assistant, not separate apps.
- **Execution transparency:** Every plan that the orchestrator produces should show intent, steps, linked artifacts (tasks, events, automations), and live status. Users can approve, edit, or run them inline.
- **Quick escape hatches:** Even though the assistant drives, users need lightweight controls for history, manual task edits, integration auth, and troubleshooting.

## Proposed Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Command Rail (left)                                                         │
│ - Workspace switcher                                                        │
│ - Assistant status / availability (deterministic vs orchestrated)           │
│ - Quick actions (New task, Schedule, Summarize day)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ Conversation Canvas (center)                                                │
│ ┌──────────────────────────────┐ ┌────────────────────────────────────────┐ │
│ │ Transcript & Messages        │ │ Workflow Preview (when orchestration) │ │
│ │ - Rich markdown              │ │ - Steps, estimates, required inputs   │ │
│ │ - Inline controls (approve,  │ │ - Status chips                        │ │
│ │   stop recording, retry)     │ └────────────────────────────────────────┘ │
│ └──────────────────────────────┘                                            │
│ Command Composer (bottom): text input + record/stop + context toggles       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Execution Canvas (right)                                                    │
│ - Active tasks/events created via assistant                                 │
│ - Integration health + subscription status                                  │
│ - Activity log (latest automations, errors)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Minimal Surface Experience

- **Single canvas:** Keep only one visible surface on load—the chat/work canvas. Everything else (execution feed, plans, telemetry) opens as drawers or collapsible panels tied to individual messages so the core UI never overflows with cards.
- **Assistant-first controls:** Voice record, upload, quick prompts, and model toggles live inside the composer. No secondary toolbars or cards; the composer expands into a full bottom sheet on mobile so it feels like Focus Mind’s command dock.
- **Hidden orchestration:** Workflow details and execution logs appear only when requested (e.g., “View plan”) and slide over the conversation. On mobile, these drawers occupy the full screen and can be swiped away to return to the thread.
- **Navigation parity:** Replace the sidebar with an icon rail on desktop and a bottom tab bar on mobile. Tabs: Assistant, Work, Insights, Settings. Each tab opens a single stack of lists (tasks, calendar, analytics) with “Open in Assistant” CTAs instead of standalone forms.
- **Glassy aesthetic:** Adopt Focus Mind’s gradient mesh + frosted glass tokens globally so the UI reads as a cohesive mobile app even on desktop. Cards float with soft shadows; backgrounds subtly animate rather than relying on heavy borders.

### Primary Surfaces

1. **Conversation Canvas** (new route `dashboard/command` and default redirect):
   - A shared component (`<AssistantConversation>`) that merges current chat UI and upgraded voice panel.
   - Displays orchestrated plans inline in collapsible cards connected to messages.
   - Shows streaming responses, statuses (Thinking → Planning → Executing), and dynamic hints (“try recording a follow up”).

2. **Command Composer**:
   - Unified input with text field, hold-to-record button, quick suggestions, conversation settings (model, orchestration toggle, telemetry view).
   - MediaRecorder handles exist already; reuse them here with visual meters and fallback upload.

3. **Execution Canvas**:
   - Replaces scattered cards from dashboard/analytics/time with a live feed of the assistant’s output.
   - Each entry includes what command generated it, the resulting entities (tasks/events), CTA to inspect/edit, and status pills (Pending API, Success, Needs input).
   - Shows integration/billing state at the top so users know if actions are blocked.

4. **Command Rail**:
   - Slim nav that keeps “Assistant”, “Work Canvas”, “Settings”, and “History”. Legacy task/calendar views live under “Work Canvas” as split panes.
   - Houses session info (current model, orchestrator status) and BYOK/subscription indicators.

## Interaction Flows

| Flow | Steps | Notes |
| ---- | ----- | ----- |
| Text command | Type → Submit → Response streams → Optional plan approval → Execution log entry | Keep deterministic/orchestrated toggle inline with composer; show telemetry badge when orchestration handles the intent. |
| Voice command | Press/hold microphone → Visual feedback ring → Auto-send chunk → Transcript + response appear together | MediaRecorder chunking allows future live streaming; for now reuse `processVoice` endpoint triggered on stop. |
| Workflow inspection | Assistant surfaces workflow card → User expands steps → Approve/Cancel/Modify | Provide buttons that call backend endpoints (e.g., `api.ai.markTelemetryRoute`) to capture feedback. |
| Manual overrides | Execution card renders created task/event → CTA opens drawer (`<EntityInspector>`) | Drawer reuses existing forms but opens from conversation context so the chat remains visible. |
| Status/Subscription | Right column shows `/billing/subscription-status`, BYOK key, usage stats | Provide inline links to “Manage billing” (Stripe portal) and BYOK state toggles. |

## Implementation Plan

1. **Scaffold Command Center Route**
   - Create `frontend/src/routes/dashboard/command/+page.svelte` as new default landing (redirect `/dashboard` to this page).
   - Extract reusable conversation logic from `chat/+page.svelte` and `voice/+page.svelte` into `lib/components/assistant/`.
   - Introduce context store for conversation state (messages, workflows, processing state) to keep UI in sync across modules.

2. **Unify Composer**
   - Build `<AssistantComposer>` component with slots for text/voice controls.
   - Integrate existing MediaRecorder logic (from voice page) and orchestrator toggle; add session indicators and quick prompts.
   - Support advanced options popover (model selection, deterministic/orchestrated mode).

3. **Workflow & Execution Panels**
   - New `<WorkflowPreview>` to render orchestrator steps, confidence, metadata.
   - New `<ExecutionFeed>` that surfaces entities returned from backend (tasks, events, calendar status). Use `/integration/calendar/events`, `/tasks`, `/analytics` as data sources.
   - Each entry stores reference to originating message/telemetry ID for traceability.

4. **Command Rail & Layout Refresh**
   - Replace `dashboard/+layout.svelte` sidebar with slimmer rail emphasizing assistant entry point.
   - Add status chips (Online, Idle, Recording) and subscription/BYOK indicators in the rail header.
   - Keep existing routes (Tasks, Calendar, Time, etc.) accessible via drawers or tabs within Execution Canvas to avoid fragmenting the experience.

5. **Progressive Enhancements**
   - Voice streaming: once `processVoice` supports streaming, move from record-stop to push-to-talk loops.
   - Telemetry insights: show orchestrator stats (confidence, tool usage) inline with workflows.
   - Playwright smoke tests for conversation flows (text vs orchestrated vs voice) to ensure regressions are caught.

## Navigation Changes

- Redirect `/dashboard` → `/dashboard/command`.
- Sidebar order: `Assistant`, `Work Canvas`, `Insights`, `Settings`. Voice becomes part of Assistant, not a separate route.
- Provide “History” view listing past sessions (persisted in IndexedDB/localStorage) for rapid recall.

## Navigation & Flow Overhaul

- **Assistant tab:** Default landing screen; orchestrator plans and executions are drawers launched from each assistant response. Streaming text + push-to-talk mimic ChatGPT/Focus Mind.
- **Work tab:** Simple lists (tasks, calendar events, knowledge items) with swipe actions on mobile. Each row has one CTA: “Send to assistant” which opens a contextual drawer in the Assistant tab.
- **Insights tab:** Usage, subscription, BYOK, telemetry streaks, and recommended prompts. Buttons link directly to assistant commands (“Show billing status”, “Toggle BYOK”).
- **Settings tab:** Minimal list of toggles and links that open bottom-sheet forms (model picker, BYOK key, notification preferences, integration auth).
- **Bottom navigation:** Always visible on mobile; desktop shows an icon rail hugging the left edge. No nested nav or secondary tabs inside tabs.

## Mobile-First System

- **Unified layout tokens:** Treat the command center as a single-column stack by default (phones/tablets) that progressively enhances into split panes on desktop. Components must be designed with 360–768px width in mind first.
- **Bottom command dock:** On small screens move the composer + quick toggles into a bottom sheet controller (similar to mobile messengers) with floating record/send buttons. Hide the sidebar entirely and replace it with a tabbed bottom nav (Assistant, Work, Insights, Settings) to keep thumb reach manageable.
- **Full-height panels:** Conversation canvas, workflow details, execution feed, and settings modals should all occupy full-height sheets when opened on mobile—no nested scrollbars. Use swipe-to-close gestures for drawers.
- **Adaptive navigation rail:** At ≥768px reintroduce a slim command rail (icon-only) that expands on hover/click. At ≥1280px show the full left rail + execution pane to mirror desktop productivity apps while keeping the center conversation unchanged.
- **Touch-first gestures:** Large tap targets (44px+), sticky headers for status indicators, and momentum scrolling for conversation history. Keep haptics-ready affordances (press states, micro-animations) to mimic native app behavior.
- **Consistent theming:** Apply the same glass/gradient aesthetic across breakpoints so the app feels like a cohesive mobile product rather than a shrunk webpage. Borrow the “card timeline” look from the Focus Mind prototype for both mobile and desktop feeds.

## Familiar Interaction Model

- **ChatGPT baseline:** Anchor the overall experience in the recognizable OpenAI ChatGPT template—single conversation column, sticky bottom composer, left rail for history/settings. This gives users instant comfort while we layer orchestration, execution feeds, and voice controls on top.
- **Progressive enrichments:** Keep the base layout familiar but introduce differentiators (workflow preview pane, execution feed, right-side action rail) as optional panels that can collapse back into the classic ChatGPT single-column view on phones.
- **Shared micro-interactions:** Reuse well-known cues such as dotted “thinking” loaders, Markdown rendering, and inline feedback buttons (👍/👎) so users understand how to interact without onboarding.

## Phased Implementation

1. **Shell refactor**
   - Build `<AssistantShell>` with gradient background, top status bar, and icon rail.
   - Implement `<MobileTabBar>` for phones; hide the legacy sidebar.
2. **Conversation rewrite**
   - Create `<AssistantConversation>` + `<AssistantComposer>` components that combine chat and voice with drawers for workflows/execution.
   - Introduce `<WorkflowDrawer>` and `<ExecutionDrawer>` triggered via per-message buttons.
3. **Work & Insights tabs**
   - Move tasks/calendar/knowledge/time screens into simplified list tabs with “send to assistant” actions.
   - Build insights cards (usage, subscription, BYOK, orchestrator telemetry) with assistant shortcuts.
4. **State layer**
   - Ship an `assistantStore` handling session ID, messages, workflows, execution references, and UI state (drawer open, recording, etc.).
   - Normalize task/event data for reuse across tabs and drawers.
5. **Polish + automation**
   - Apply the gradient/glass token system everywhere; add icon badges, haptic-friendly button states, and micro interactions.
   - Add Playwright smoke tests (text-only, orchestrated workflow, voice recording) + per-breakpoint visual snapshots to keep the experience regression-free.

## Data & State Requirements

- Shared store for conversation + workflows (`assistantStore`) storing:
  ```ts
  {
    sessionId: string | null;
    messages: AssistantMessage[];
    workflows: Record<string, WorkflowPlan>; // keyed by telemetry/session
    executionFeed: ExecutionEntry[];
    composerState: { isRecording: boolean; isProcessing: boolean; provider: string; mode: 'deterministic' | 'orchestrated'; };
  }
  ```
- API additions already exist (`/assistant/voice/init`, `/ai/orchestrate-task`, `/billing/subscription-status`); expose them via typed helpers and fetch on mount.
- Execution feed subscriptions can piggyback off existing `tasks`/`events` endpoints until WebSocket push is available.

## Visual Notes

- Adopt “command palette” cues: dimmed background, glowing composer focus state, timeline dots for workflow progression.
- Keep color-coded statuses consistent (Primary = assistant responses, Secondary = pending, Destructive = errors, Accent = orchestration).
- Use condensed typography (e.g., `.text-sm tracking-tight`) inside workflow cards to display richer detail without overwhelming the user.

## Acceptance Criteria

- Users can open `/dashboard/command` and issue a text or voice instruction without leaving the page.
- Orchestrator workflows render inline with the triggering message, and execution artifacts appear in the right-hand feed.
- Billing/subscription/BYOK status are visible at all times within the command center.
- Legacy pages remain accessible but feel secondary and reactive to assistant output.

This plan balances ambition with incremental adoption: first consolidate conversation and voice, then layer workflows and execution feeds, followed by navigation refresh and automated tests.
