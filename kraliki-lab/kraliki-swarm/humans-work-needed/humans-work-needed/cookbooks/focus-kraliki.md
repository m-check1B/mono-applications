# Mac Computer Use Cookbook: Focus by Kraliki

**App:** focus-kraliki  
**Description:** AI-first productivity system with Stripe billing  
**Created:** 2025-12-23  
**Linear:** VD-161

---

## Purpose

Provide step-by-step visual and manual checks for Focus by Kraliki on macOS using Computer Use. Focus on verifying login, dashboard workflows, and Stripe billing.

---

## Access

### Local Dev (Recommended)

| Component | URL | Notes |
|----------|-----|------|
| Backend API | http://127.0.0.1:8000 | FastAPI |
| Frontend | http://127.0.0.1:5173 | SvelteKit dev server |
| API docs | http://127.0.0.1:8000/docs | Swagger UI |

### Repo Location

- `/home/adminmatej/github/applications/focus-kraliki`

---

## Credentials

- No test accounts found in `/home/adminmatej/github/secrets/test-accounts/`.
- If login is required, request a test account from the owner.
- For billing tests, Stripe test keys are required in `applications/focus-kraliki/backend/.env`.

---

## Visual Checks

### 1. Landing + Auth

1. Open http://127.0.0.1:5173
2. Verify the landing/login screen renders.
3. Create a new account or log in.

Checklist:
- [ ] No blank screen or console errors
- [ ] Login and register screens are reachable
- [ ] Auth redirects to dashboard on success

### 2. Dashboard Shell

1. Confirm the main dashboard loads after login.
2. Navigate between dashboard tabs (Tasks, Work, Insights if present).

Checklist:
- [ ] Navigation renders and routes change without errors
- [ ] Primary panels load (no "loading forever")

### 3. Tasks Workflow

1. Create a new task.
2. Mark a task complete or move its status.
3. Refresh the page.

Checklist:
- [ ] Task creation works
- [ ] Status changes persist after reload

### 4. Insights/Billing Surface

1. Navigate to Settings/Billing or Insights.
2. Look for subscription status, upgrade CTA, or billing portal link.

Checklist:
- [ ] Billing UI renders
- [ ] CTA or status indicator is visible

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

### Subscription Status (Requires Auth)

```bash
curl http://127.0.0.1:8000/billing/subscription-status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Expected:
- JSON response with subscription fields or a helpful error message.

---

## Payment Flow (Stripe Test Mode)

1. Ensure Stripe test keys are set in `backend/.env`.
2. Open the Billing/Upgrade flow in the UI.
3. Proceed to Stripe Checkout.
4. Use test card `4242 4242 4242 4242` with any future expiry/CVC.

Checklist:
- [ ] Checkout page loads in test mode
- [ ] Success redirects back to app
- [ ] Subscription status updates in UI or via API

Optional (Webhook forwarding):
```bash
stripe listen --forward-to http://127.0.0.1:8000/billing/webhook
```

---

## OAuth/Identity Setup

- Email/password auth should work in local dev.
- If Google OAuth is enabled, verify the consent screen loads and returns to the app.

---

## Expected States (Screenshots)

Capture screenshots of:

1. Login or register screen
2. Dashboard home after login
3. Tasks list with at least one task
4. Billing/Upgrade screen or Stripe Checkout

---

## Troubleshooting

### Frontend not loading

- Confirm `./dev-start.sh` is running.
- Check http://127.0.0.1:5173 for Vite error output.

### Backend not responding

- Confirm backend is running on port 8000.
- Check http://127.0.0.1:8000/docs for Swagger UI.

### Stripe checkout missing

- Verify `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, and `STRIPE_PRICE_ID_*` are set.
- Make sure Stripe is in test mode.

---

## Quick Start (For Tester)

```bash
cd /home/adminmatej/github/applications/focus-kraliki

# Start dev servers
./dev-start.sh

# Stop dev servers
./dev-stop.sh
```

---

*Cookbook Version: 1.0*
