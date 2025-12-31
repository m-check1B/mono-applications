# Mac Computer Use Cookbook: CLI-Toris

**App:** cli-toris  
**Description:** Multi-agent orchestration toolkit (CLI + web cockpit)  
**Created:** 2025-12-22  
**Linear:** VD-169

---

## Purpose

Provide step-by-step visual and manual checks for CLI-Toris on macOS using Computer Use. Focus on verifying the local dev experience, web cockpit UI, and core orchestration endpoints.

---

## Access

### Local Dev (Recommended)

| Component | URL | Notes |
|----------|-----|------|
| Backend API | http://127.0.0.1:5001 | FastAPI |
| Frontend cockpit | http://127.0.0.1:5173 | Svelte dev server |
| API docs | http://127.0.0.1:5001/docs | Swagger UI |

### Demo (If Available)

- URL: https://cli-toris-demo.ocelot.ai (legacy, may be offline)

### Repo Location

- `/home/adminmatej/github/applications/prototypes/cli-toris`

---

## Credentials

- No test accounts found in `/home/adminmatej/github/secrets/test-accounts/`.
- If login is required, request a test account from the owner.

---

## Visual Checks

### 1. Frontend Cockpit Loads

1. Open http://127.0.0.1:5173
2. Verify the app shell renders without blank screen or errors.

Checklist:
- [ ] Page loads in under 5 seconds
- [ ] Navigation sidebar visible
- [ ] Main content area renders without console errors

### 2. Workflows UI

1. Navigate to the Workflows section.
2. Start a new workflow draft.

Checklist:
- [ ] "New Workflow" action exists
- [ ] Canvas/editor loads
- [ ] Nodes can be added to the canvas
- [ ] Save or execute buttons are visible

### 3. Orchestration Health

Open http://127.0.0.1:5001/api/health in the browser.

Checklist:
- [ ] JSON response
- [ ] status shows healthy

---

## API Checks (Quick Manual)

### Health

```bash
curl http://127.0.0.1:5001/api/health
```

Expected:
```json
{"status":"healthy","version":"1.0.0"}
```

### List Agents

```bash
curl http://127.0.0.1:5001/api/orchestration/agents
```

Expected:
- JSON response with "agents" array.

### Parallel Execution (If agents configured)

```bash
curl -X POST http://127.0.0.1:5001/api/orchestration/parallel \
  -H "Content-Type: application/json" \
  -d '{"topic":"Summarize this in one sentence","agent_ids":["matej","alex"]}'
```

Expected:
- Request completes with a result payload (non-empty).

---

## Payment Flow

- Not implemented for CLI-Toris at this time.
- If a billing UI exists, confirm it renders but do not attempt real payments.

---

## OAuth/Identity Setup

- No OAuth flow documented for local testing.
- If login is required, capture the error state and request credentials.

---

## Expected States (Screenshots)

Capture screenshots of:

1. Frontend landing/dashboard screen.
2. Workflows canvas with at least one node added.
3. API health response in browser or terminal.

---

## Troubleshooting

### Frontend not loading

- Confirm `pnpm dev` is running in `frontend/`.
- Check http://127.0.0.1:5173 for Vite error page.

### Backend not responding

- Confirm backend is running:
  - `CLI_TORIS_DEBUG=true python backend/app.py`
- Verify port 5001 is listening on 127.0.0.1.

---

## Quick Start (For Tester)

```bash
cd /home/adminmatej/github/applications/prototypes/cli-toris

# Backend
source .venv/bin/activate
CLI_TORIS_DEBUG=true python backend/app.py

# Frontend (new terminal)
cd frontend
pnpm dev
```

---

*Cookbook Version: 1.0*
