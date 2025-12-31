# Mac Computer Use Cookbook: Voice by Kraliki

**App:** voice-kraliki  
**Description:** AI-powered call center platform with voice workflows  
**Created:** 2025-12-23  
**Linear:** VD-160

---

## Purpose

Provide step-by-step visual and manual checks for Voice by Kraliki on macOS using Computer Use. Focus on login, core operations pages, and call/voicemail workflows.

---

## Access

### Local Dev (Recommended)

| Component | URL | Notes |
|----------|-----|------|
| Backend API | http://127.0.0.1:8000 | FastAPI |
| Frontend | http://127.0.0.1:3000 | SvelteKit dev server |
| API docs | http://127.0.0.1:8000/docs | Swagger UI |

### Repo Location

- `/home/adminmatej/github/applications/voice-kraliki`

---

## Credentials

- No test accounts found in `/home/adminmatej/github/secrets/test-accounts/`.
- If login is required, request a test account from the owner.

---

## Visual Checks

### 1. Landing + Auth

1. Open http://127.0.0.1:3000
2. Verify the landing/login screen renders.
3. Create a new account or log in.

Checklist:
- [ ] No blank screen or console errors
- [ ] Login and register screens are reachable
- [ ] Auth redirects to dashboard on success

### 2. Dashboard Shell

1. Confirm the main dashboard loads after login.
2. Navigate between primary areas (Campaigns, IVR, Routing, Recordings, Voicemail).

Checklist:
- [ ] Navigation renders and routes change without errors
- [ ] Primary panels load (no "loading forever")

### 3. Campaigns + Call Lists

1. Open Campaigns or Call Lists.
2. Create a new campaign/call list (minimal fields).
3. Refresh the page.

Checklist:
- [ ] Create actions succeed without errors
- [ ] Newly created item persists after reload

### 4. IVR + Routing

1. Open IVR flows.
2. Open an IVR flow or create a simple one if UI supports it.
3. Open Routing Rules.

Checklist:
- [ ] IVR flow UI renders
- [ ] Routing rules list loads

### 5. Recordings + Voicemail

1. Open Recordings page.
2. Open Voicemail page.

Checklist:
- [ ] Lists render without errors
- [ ] Item detail views open if present

---

## API Checks (Quick Manual)

### Health

```bash
curl http://127.0.0.1:8000/health
```

Expected:
```json
{"status":"ok"}
```

### Auth (If login required)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"YOUR_EMAIL","password":"YOUR_PASSWORD"}'
```

Expected:
- JSON response with access token or helpful error message.

---

## Payment Flow (If Applicable)

- No billing flow documented in Voice by Kraliki docs.
- If a payment flow appears in UI, verify it loads and request Stripe test credentials.

---

## OAuth/Identity Setup

- Email/password auth should work in local dev.
- If SSO/OAuth is enabled, verify consent screen loads and returns to app.

---

## Expected States (Screenshots)

Capture screenshots of:

1. Login or register screen
2. Dashboard home after login
3. Campaigns or Call Lists screen
4. IVR or Routing screen
5. Recordings or Voicemail screen

---

## Troubleshooting

### Frontend not loading

- Check `pnpm dev` is running in `/frontend`.
- Confirm http://127.0.0.1:3000 is reachable.

### Backend not responding

- Check `uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
- Confirm http://127.0.0.1:8000/docs loads.

---

## Quick Start (For Tester)

```bash
cd /home/adminmatej/github/applications/voice-kraliki

# Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Frontend (new terminal)
cd ../frontend
pnpm install
pnpm dev -- --host 127.0.0.1 --port 3000
```

---

*Cookbook Version: 1.0*
