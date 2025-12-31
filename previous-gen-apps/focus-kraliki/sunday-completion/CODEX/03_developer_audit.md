# CODEX Audit 03 – Developer Perspective

## Architecture Snapshot
- **Frontend:** Route-per-surface, assistant state local to `/dashboard`. Queue uses `localStorage` to hand off prompts.
- **Backend:** FastAPI + Postgres. `/ai/orchestrate-task` is the only orchestration path used, yet legacy stacks (`/agent-tools`, `/swarm-tools`, ii-agent WebSocket) linger.
- **Voice:** `/assistant/voice/*` integrates providers, but `/dashboard/voice` doesn’t reuse the main assistant store.

## Key Disconnects
1. **Multiple orchestration stacks** – need consolidation; unused routers add maintenance burden without user value.
2. **Queue durability** – no backend store; cross-device history impossible, conflicting with research requirement “What did I ask last week?”.
3. **Execution engine absent** – approvals aren’t tied to deterministic APIs, so the “assistant” can’t act.
4. **Telemetry underused** – decisions saved but only partially surfaced; no analytics filtering by status, no workflow history API.

## Technical Debt
- LocalStorage queue w/out reconciliation.
- Orchestrator outputs unstructured markdown; should persist structured JSON for retrieval and analytics.
- Missing integration tests for voice/orchestrator/telemetry flows.
- Alembic branching needs governance (recent multi-head issue).

## Developer Actions (to satisfy research-driven UX)
1. **Implement clarification & execution loop:** extend `/ai/orchestrate-task` to ask follow-ups, then trigger deterministic tasks/events/knowledge updates via background jobs.
2. **Unify voice + text:** share the assistant store; voice transcripts should appear in conversation and accept follow-ups.
3. **Persist queue/history server-side:** add `/assistant/commands` API storing CTAs per workspace/user to support “What did I work on last week?”.
4. **Expose telemetry timeline:** add `/ai/telemetry/history` + UI table with decision status, enabling Team Leads to audit approvals.
5. **Prune unused stacks:** deprecate `/agent-tools` & `/swarm-tools` (or wire them in) to avoid confusion.

With these, the platform can evolve from “AI-flavored dashboard” to the AI-first assistant described in user research.

