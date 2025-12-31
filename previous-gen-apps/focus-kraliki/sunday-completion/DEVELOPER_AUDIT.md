# Developer Perspective Audit

## Architecture Snapshot (per user research personas)
- **Frontend:** SvelteKit routes reflect deterministic screens (tasks/time/projects/team/analytics) tailored to persona needs, but assistant state is local per route. There is no shared store enabling “Plan my day” to automatically pull tasks/time blocks.
- **Backend:** FastAPI exposes `/ai/*`, `/assistant/*`, deterministic CRUD, Postgres, and a local-orchestrator. There is no worker or job queue to execute multi-step plans (“Break down goal,” “Sync calendar and prep tasks”).
- **Queue pattern:** `localStorage`‐based; good for quick CTAs but insufficient for Freelancer/Team Lead personas who expect persistence across sessions/devices.

## Disconnects & Overlaps vs Research Workflows
1. **Multiple orchestration stacks** (ii-agent, swarm tools) are not integrated. If we plan to serve Power Users (automation seekers), we need one canonical orchestrator.
2. **Voice duplication** prevents “Simply In / Simply Out” behavior. `/assistant/voice/*` is wired to providers, but `/dashboard/voice` still acts as a standalone page—no shared conversation store.
3. **Knowledge/task automation** is manual. Research requests (“Add task: [natural language]”, “Break down goal into tasks”) can’t be satisfied because orchestrations don’t call deterministic APIs after approval.
4. **Telemetry decisions** are persisted but not surfaced beyond the latest card; analytics screens should filter by decision status so Team Leads can review “what was approved / rejected this week.”

## Technical Debt / Inefficiencies
- **Queue durability:** No server sync; losing tabs wipes CTAs. A backend queue or event log would let us replay commands and show history (“What did I ask yesterday?”).
- **Unstructured orchestration results:** Workflows are plain markdown text. To support “Generate weekly review” we need structured JSON stored in Postgres for retrieval and summarization.
- **Limited automated tests:** We now have Playwright smoke tests (queue, execution drawer), but backend behavior (voice, orchestration/decision flows) lacks integration tests.
- **Migration hygiene:** Multiple heads occurred (009 vs c1310994d158). Need to enforce single-head merges or use Alembic branches intentionally.

## Feature Gaps Blocking AI-First Vision
1. **Clarification loop** (research request #1 “Plan my day”, #9 “I’m overwhelmed”) requires multi-turn flows: capture user input, ask clarifications, apply deterministic actions. Backend currently returns static steps.
2. **Execution engine** is missing—there’s no worker to create tasks, schedule events, edit knowledge. Without automation, approvals give users false hope.
3. **Memory/RAG**: We ship file-search tables but don’t inject them into assistant responses (knowledge worker persona needs this).
4. **Observability & trust**: Need audit logs per workflow, progress bars, error states to address objections (“AI too slow”, “Don’t trust automation”).

## Recommendations (aligned with user research)
- Collapse orchestration paths into a single pipeline that can both clarify and execute (text + voice). Use structured outputs so we can run “daily planning” templates for Solo Developers.
- Introduce a background job runner (Celery/Dramatiq) or at least FastAPI background tasks to execute deterministic actions once workflow steps are approved.
- Move the assistant queue into a backend store to keep history across devices; expose “recent commands” per workspace to support Team Leads/Small Business Owners.
- Expand Playwright + backend integration tests to cover voice streaming, workflow decisions, and key user requests (plan day, break goal, weekly review).
