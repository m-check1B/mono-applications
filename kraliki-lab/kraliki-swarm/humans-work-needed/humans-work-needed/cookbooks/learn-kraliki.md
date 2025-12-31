# Mac Computer Use Cookbook: Learn by Kraliki

**App:** learn-kraliki  
**Description:** AI Academy + onboarding LMS for business training  
**Created:** 2025-12-23  
**Linear:** VD-163

---

## Purpose

Provide step-by-step visual and manual checks for Learn by Kraliki on macOS using Computer Use. Focus on verifying the frontend shell, login flow, and course browsing.

---

## Access

### Local Dev (Recommended)

| Component | URL | Notes |
|----------|-----|------|
| Frontend | http://127.0.0.1:5173 | SvelteKit dev server |
| Backend API | http://127.0.0.1:8000 | FastAPI |
| API docs | http://127.0.0.1:8000/docs | Swagger UI |
| Health | http://127.0.0.1:8000/health | JSON health check |

### Docker Compose (Optional)

- App URL: http://127.0.0.1:8030 (requires local port forwarding if remote host)

### Beta/Prod (If Available)

- Beta: https://learn.verduona.dev
- Prod: https://learn.kraliki.com

### Repo Location

- `/home/adminmatej/github/applications/learn-kraliki`

---

## Credentials

- No test accounts found in `/home/adminmatej/github/secrets/test-accounts/`.
- Zitadel login is required. Request a test account if needed.

---

## Visual Checks

### 1. Frontend Shell Loads

1. Open http://127.0.0.1:5173
2. Verify the app shell renders without a blank screen.

Checklist:
- [ ] Page loads in under 5 seconds
- [ ] Top-level navigation or header is visible
- [ ] No obvious console errors

### 2. Login Flow (Zitadel)

1. Click the login/sign-in action (if present).
2. Confirm redirect to Zitadel domain.
3. If credentials are available, complete login.

Checklist:
- [ ] Redirect to Zitadel occurs
- [ ] Login page renders (no 404)
- [ ] After login, user returns to app

### 3. Course Catalog (Post-Login)

If logged in successfully:

Checklist:
- [ ] Course list loads
- [ ] At least one course card is visible
- [ ] Opening a course shows lesson list

### 4. Lesson View (Post-Login)

If logged in successfully:

Checklist:
- [ ] Lesson content renders without broken layout
- [ ] Navigation (previous/next) works if available

---

## API Checks (Quick Manual)

### Health

```bash
curl http://127.0.0.1:8000/health
```

Expected:
```json
{"status":"healthy","app":"Learn by Kraliki"}
```

### Courses (Auth Required)

```bash
curl http://127.0.0.1:8000/api/courses
```

Expected:
- JSON response (may require auth; if 401, capture response).

---

## Payment Flow

- Not implemented. If any billing UI appears, confirm it renders only.

---

## OAuth/Identity Setup

- Zitadel OIDC is required for login.
- If login fails, capture the error screen and request credentials.

---

## Expected States (Screenshots)

Capture screenshots of:

1. Frontend landing screen (logged out).
2. Zitadel login page.
3. Worksheet templates list (logged in).
4. Worksheet detail view with content visible.

---

## Troubleshooting

### Frontend not loading

- Confirm `npm run dev` is running in `frontend/`.
- Check http://127.0.0.1:5173 for a Vite error page.

### Backend not responding

- Confirm `uvicorn app.main:app --reload --port 8000` is running.
- Verify http://127.0.0.1:8000/health returns JSON.

### Login redirect fails

- Confirm Zitadel env vars exist in `backend/.env`.
- Check backend logs for OIDC errors.

---

## Quick Start (For Tester)

```bash
cd /home/adminmatej/github/applications/learn-kraliki

# Database
docker compose up db -d

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd ../frontend
npm install
npm run dev
```

---

*Cookbook Version: 1.0*
