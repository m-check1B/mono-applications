# Speak by Kraliki Audit Report

## Executive Summary
Reviewed the full repository (backend FastAPI, frontend Svelte, platform packages, scripts, and docs) for security, bugs, quality, and dependency risk. No direct SQL injection or XSS sinks were found, and pip-audit reports no known Python vulnerabilities, but the application is not launch-ready due to a critical missing webhook verification and several high-severity auth and access-control gaps (default secrets, missing role scoping, and magic-link expiry bypass). NPM audit reports low-severity frontend vulnerabilities and multiple outdated frontend dependencies that should be updated and revalidated.

## Issues by Severity

### Critical
- `backend/app/routers/telephony.py:40` - Webhook signature validation is commented out and `/audio-stream` accepts unauthenticated POSTs, allowing forged Telnyx events and audio injection. Fix: enforce Telnyx signature validation on all webhook/audio endpoints (reject unsigned requests) and consider IP allowlisting.

### High
- `backend/app/core/config.py:23` - Insecure default secrets/credentials (DB URL, JWT secret) are hardcoded, and `validate_production_security()` in `backend/app/core/auth.py:203` is never invoked. Fix: remove defaults for secrets, require env vars, and call `validate_production_security()` on startup; also update `docker-compose.yml:20` to require non-default credentials in production.
- `backend/app/core/auth.py:179` - JWT payload omits `department_id`, but `backend/app/routers/alerts.py:40` relies on it; managers can see all alerts. Insights endpoints (`backend/app/routers/insights.py:37`) also lack department scoping. Fix: include `department_id` in the token or query it per request (e.g., `CompanyService.get_user_with_department_filter`) and apply department filters in alerts/insights.
- `backend/app/routers/conversations.py:128` - Magic-link expiry is not checked for redact/consent/delete; `backend/app/routers/actions.py:90` and `backend/app/routers/voice.py:332` also skip expiry. Fix: enforce `magic_link_expires` checks on every magic-link endpoint and return 410 when expired.
- `backend/app/routers/auth.py:37` - No rate limiting or lockout on login/registration enables brute-force attempts. Fix: add rate limiting (per IP/user) and exponential backoff/lockout, plus audit logging.
- `backend/app/routers/employees.py:74` - Sensitive admin actions (employee CRUD/import) have no role checks even though roles exist. Fix: enforce role gates (e.g., owner/HR only) across employee, survey launch, and action management routes.
- `backend/app/models/employee.py:55` - Magic-link tokens are stored in plaintext; a DB leak grants direct access to employee data. Fix: store a hashed token (e.g., SHA-256) and compare hashes, or use short-lived one-time tokens.

### Medium
- `backend/app/models/conversation.py:54` - `transcript`/`redacted_sections` JSONB fields are mutated in-place in `backend/app/routers/voice.py:136` and `backend/app/routers/conversations.py:175`, but SQLAlchemy will not track in-place JSON changes without mutable types. Fix: use `MutableList/MutableDict` or reassign/`flag_modified` before commit.
- `backend/app/routers/conversations.py:187` - Consent is not persisted; endpoint only returns a message, which is a compliance gap. Fix: store consent records with timestamp, employee_id, and token metadata.
- `backend/app/services/email.py:151` - Resend client is synchronous but called in async paths; `backend/app/routers/surveys.py:210` sends emails inside a transaction loop, risking event-loop blocking and long transactions. Fix: move email sending to background jobs/queue and commit DB changes before dispatch.
- `backend/app/routers/surveys.py:231` - Magic-link URL should be derived from a configurable frontend base URL (now uses `settings.frontend_base_url`).
- `frontend/src/lib/stores/auth.ts:25` - Access/refresh tokens are stored in localStorage, increasing XSS blast radius. Fix: prefer httpOnly cookies with CSRF protection, or add strict CSP and avoid inline scripts.

### Low
- `backend/app/routers/alerts.py:56` - N+1 queries and no pagination in list endpoints (`alerts`, `actions`, `surveys`, `employees`) will degrade performance at scale. Fix: paginate and join/aggregate server-side.
- `backend/app/core/auth.py:36` - `get_current_user_optional` is not actually optional because `HTTPBearer()` auto-errors; missing credentials still 403. Fix: use `HTTPBearer(auto_error=False)` and handle None explicitly.
- `backend/app/routers/voice.py:320` - WebSocket sends raw exception text to clients, leaking internal details. Fix: log server-side and return a generic error message.
- `backend/app/routers/telephony.py:115` - `/status` exposes internal service info without auth. Fix: restrict to internal network or require authentication.
- `frontend/package-lock.json:988` - `npm audit` reports low-severity cookie vulnerability via `@sveltejs/kit`. Fix: upgrade SvelteKit/cookie when feasible and rerun `npm audit fix`.
- `frontend/package.json:13` - Several frontend deps are outdated per `npm outdated`. Fix: bump devDependencies to latest compatible versions and retest.
- `backend/requirements-prod.txt:5` - Python deps are unpinned (`>=` only), reducing reproducibility and making auditing harder. Fix: pin versions with hashes (pip-compile or similar).

## Recommended Actions (prioritized)
1. Re-enable and enforce Telnyx webhook/audio signature validation; block unauthenticated requests.
2. Eliminate default secrets and enforce production config validation on startup; rotate any existing secrets.
3. Fix RBAC and department scoping (include department_id or query per request) and apply filters to alerts/insights/employee actions.
4. Enforce magic-link expiry on all token endpoints and hash stored tokens.
5. Add rate limiting and login protection (lockout/backoff), and improve audit logging.
6. Correct JSONB mutation tracking for transcripts/redactions and persist consent records.
7. Update frontend dependencies (address npm audit findings) and consider moving tokens to httpOnly cookies.
