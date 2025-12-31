# Sunday Completion – Audit Checklist

Use this checklist to verify the app end-to-end before calling it “done”. Each item links to the AI-first requirement: a single assistant canvas that can hear/clarify/execute.

## Environment & Tooling
- [ ] `pnpm install` in `frontend/` and `pip install -r requirements.txt` (or `uv pip sync`) in `backend/` succeed without warnings.
- [ ] `pnpm check` passes (Svelte + TypeScript) and `pytest` (or at least `pytest backend/tests`) passes.
- [ ] Alembic heads converge (`alembic heads` shows one head). Run `alembic upgrade head` after pulling.

## Assistant Shell & Queue Loop
- [ ] `/dashboard` renders the assistant canvas with conversation, composer, workflow drawer, execution drawer.
- [ ] The localStorage queue drains when you open `/dashboard` and the toast appears on sending commands from other routes (calendar, time, settings, team, projects, analytics).
- [ ] Workflow approve/revise buttons both enqueue context **and** persist a decision via `/ai/telemetry/{id}/decision`.

## Voice & Recording
- [ ] `/dashboard/voice` initializes a voice session (providers endpoint reachable) and records/upload flows hit `/assistant/voice/*`.
- [ ] Audio submissions propagate messages back to the conversation history.
- [ ] Permission fallbacks surface errors (microphone/API) in the UI.

## Deterministic Data Surfaces
- [ ] Calendar/time/tasks/projects/team/analytics pages load via their REST stores (no stray 404s).
- [ ] Each screen offers at least one “Send to assistant” CTA wired to `enqueueAssistantCommand`.
- [ ] Execution drawer can edit a task + knowledge item without reloading.

## Orchestration Back-End
- [ ] `/ai/orchestrate-task` returns `telemetryId`, workflow steps, and is called by the assistant (deterministic vs orchestrator toggle works).
- [ ] Telemetry summary responds with recent runs and shows decision metadata.
- [ ] `/ai/telemetry/{id}/decision` returns the updated record; the dashboard renders status + timestamp.

## Testing & Observability
- [ ] Playwright suites (`frontend/tests/e2e/*.spec.ts`) run green in CI (requires local `.env` with a seeded user).
- [ ] Logs for backend/worker show both deterministic and orchestrated routes being recorded.
- [ ] Error boundaries exist: assistant send/voice upload/queue draining all display user-facing errors.

