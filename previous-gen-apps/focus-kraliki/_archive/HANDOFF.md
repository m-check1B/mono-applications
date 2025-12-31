## Focus Lite UI/Assistant Handoff

### Context Snapshot

- **Shell/UI direction**: Dashboard now uses a mobile-first assistant shell with a glass navigation rail plus bottom mobile tabs. The main `/dashboard` route renders the chat + voice surface via `<AssistantConversation>` and `<AssistantComposer>`, while `assistantQueue` handles cross-tab prompt handoffs. Work (`/dashboard/work`) reuses the knowledge store to list item types with Sparkles CTAs that enqueue prompts; Tasks (`/dashboard/tasks`) got assistant shortcuts; Insights (`/dashboard/insights`) shows usage/subscription/telemetry cards that also push commands into the assistant.
- **Execution drawer**: Feed cards (tasks + knowledge) open a detail drawer with completion toggles (`api.tasks.update`, `api.knowledge.updateKnowledgeItem`) and “Ask assistant” buttons. The feed fetches tasks and knowledge concurrently and labels entries with their type metadata.
- **Assistant queue**: `frontend/src/lib/utils/assistantQueue.ts` persists commands in localStorage; the assistant page drains the queue on mount/storage events. Work, Tasks, Insights, and the execution feed all call `enqueueAssistantCommand` so context flows back to chat.

### Key Decisions & Preferences

- UX mirrors Focus Mind/Vectal: single conversation canvas, glass aesthetic, unified mobile controls.
- Every route should leverage the assistant loop rather than bespoke flows.
- Known debt: Tailwind `@apply` warnings—keep `pnpm check` passing aside from those.
- Backend stayed untouched; UI queries rely on `/tasks`, `/knowledge`, `/ai/telemetry`, `/settings/usage-stats`, `/billing/subscription-status`.

### Remaining Work / Next Steps

1. **Execution drawer polish**: Add edit links (open Work modal for knowledge, inline form for tasks), surface workflow artifacts, and support approvals for orchestrated plans.
2. **Insights charts**: If telemetry exposes histories, render charts/sparklines, and raise alerts (usage nearing limit, orchestrator streaks).
3. **Additional assistant CTAs**: Extend the queue pattern to Calendar, Time, Settings (e.g., “Connect calendar”, “Toggle BYOK”) so every screen can send context back to chat.
4. **Voice streaming**: When backend streams audio, upgrade `<AssistantComposer>` for push-to-talk and live transcripts.

### References

- Main files: `frontend/src/routes/dashboard/+page.svelte`, `/work/+page.svelte`, `/tasks/+page.svelte`, `/insights/+page.svelte`, `frontend/src/lib/components/assistant/*`, `frontend/src/lib/utils/assistantQueue.ts`.
- Knowledge components live under `frontend/src/lib/components/knowledge/*`.
- Tailwind warning source: `frontend/src/lib/components/MarkdownRenderer.svelte`.
