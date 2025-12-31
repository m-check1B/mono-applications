# Final Validation & Risk Checklist – Operator Demo 2026

## Status Snapshot
- **Backend**: unified SQLAlchemy metadata, auth/permissions persisted, Deepgram Nova 3 Live provider wired; AI insights persistence now scoped per request.
- **Frontend**: provider sessions bootstrap via `/api/v1/sessions/bootstrap`, auto-start/end backend sessions, expose `sessionId`/metadata to UI; agent workspace & controls use session state manager, enhanced connection banner, retry hook.
- **Pending**: real AI provider keys, WebRTC audio streaming, full production hardening (secrets, CI/CD, HA, load/security tests).

## Validation Checklist

### 1. Environment & Dependencies
- [ ] `pip install -r backend/requirements.txt`
- [ ] `npm install` in `frontend/`
- [ ] Confirm `.env` / secrets (API keys, DB URL, JWT keys) populated.

### 2. Database & Migrations
- [ ] `cd backend && alembic upgrade head`
- [ ] Verify `users` table now has `permissions` column and uppercase `role` values.
- [ ] Smoke-load SQLAlchemy models (`python -m app.scripts.check_models`) if available.

### 3. Backend Smoke Tests
- [ ] `pytest` (or targeted suites) – focus on auth, sessions, AI services.
- [ ] Manual API checks (curl/Postman):
  - `POST /api/v1/auth/login`
  - `POST /api/v1/sessions/bootstrap` (note returned `session_id`/`websocket_url`)
  - `POST /api/v1/sessions/{id}/start` + verify provider connection logs.
- [ ] Confirm `/api/v1/providers` lists Deepgram Nova 3 with `supports_realtime = true`.

### 4. Frontend Smoke Tests
- [ ] `npm run check` and `npm run build`.
- [ ] Launch dev server (`npm run dev`), ensure:
  - Agent workspace shows live connection banner and session metadata.
  - “Start Demo Call” bootstraps session (observe backend logs for start).
  - Retry button triggers reconnection without page reload.
- [ ] Validate session state persists across refresh (call status preserved, AI panels recover).

### 5. End-to-End Call Flow (Staging/Test Keys)
- [ ] Provide real provider credentials (Gemini/OpenAI/Deepgram/Twilio/Telnyx).
- [ ] Start session, ensure:
  - WebSocket `/ws/sessions/{id}` shows streaming events.
  - Transcription & AI panels populate with provider data (no placeholder JSON).
  - `start-session` payload accepted by backend provider (logs show handshake).

### 6. Observability & Operations
- [ ] Verify Prometheus `/metrics` and `/health` endpoints respond.
- [ ] Ensure Sentry DSN configured, test exception to confirm capture.
- [ ] Confirm rate limiting middleware active (429 observed after threshold).

### 7. Remaining Risks & TODOs
- **Audio/WebRTC**: implement real-time audio capture/playback via `webrtcManager`, integrate jitter/quality pipeline.
- **AI Providers**: replace fallback logic with live summarisation, sentiment, assistance (requires keys, error handling, tests).
- **Secrets/CI/CD**: move from `.env` to managed secrets store, add automated pipelines, load/security tests, HA DB setup.
- **Auth UX**: email verification + password flows still stubbed; wire endpoints & UI.
- **Docs**: produce runbooks for session troubleshooting, provider onboarding, AI error taxonomy.

### 8. Recommended Next Steps
1. Configure staging environment with live provider credentials, run full E2E call with audio.
2. Implement WebRTC audio path and tie into new provider session orchestration.
3. Stand up CI/CD (tests + alembic + lint) and secrets management.
4. Layer production hardening (load, failover, monitoring dashboards).

When all checklist items are satisfied, the app is ready for a “feature-complete” demo; remaining risks should be tracked in the delivery plan for production launch.
