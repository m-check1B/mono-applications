# CC-Lite 2026 Audit Report

## Executive Summary
The audit found critical exposure of real API/DB credentials in repository `.env` files and a critical RCE vulnerability in `happy-dom`. High-risk issues include an authentication model mismatch (UUID vs integer user IDs), missing rate limiting on auth endpoints, a high-severity `glob` CLI vulnerability, and weak staging credentials. Several medium issues affect security hardening (headers/CSP), error disclosure, async performance, dependency hygiene, and configuration fallbacks. No direct SQL injection or XSS sinks were identified in the reviewed code (parameterized queries and no raw HTML rendering), but the current findings mean the app is not launch-ready.

## Issues by Severity

### Critical
- Files: `.env:29`, `.env:38`, `.env:43`, `.env:50`, `.env:64`, `.env:66`, `backend/.env:35`, `backend/.env:36`, `backend/.env:37`, `backend/.env:42`, `backend/.env:62` - Real API keys, DB passwords, and Redis credentials are present in repo `.env` files; this is a direct secret exposure and can enable account takeover or data loss if leaked. Fix: immediately rotate all exposed keys/passwords, delete these `.env` files from the repo, add placeholders in `.env.example`, enforce `.gitignore`, and add secret scanning (pre-commit + CI).
- Files: `frontend/pnpm-lock.yaml:1140`, `frontend/package.json:33` - `happy-dom@15.11.7` is flagged as a critical VM context escape (CVE-2025-61927), which can lead to RCE if untrusted content is executed in tests or SSR. Fix: upgrade to `happy-dom@>=20.0.0` (or remove it) and re-lock dependencies.

### High
- Files: `backend/app/auth/routes.py:100`, `backend/app/models/user.py:59`, `backend/app/auth/jwt_auth.py:65` - Auth storage and user model are inconsistent: auth routes create UUID users while SQLAlchemy `User.id` is an integer and JWT verification looks up by `User.id == payload["sub"]`. Tokens created by `/api/v1/auth` will not map to SQLAlchemy users, breaking authentication and authorization flows. Fix: unify on one user model and storage path (prefer SQLAlchemy) with a single ID type; migrate schema and token subject accordingly.
- Files: `backend/app/middleware/rate_limit.py:35`, `backend/app/main.py:118`, `backend/app/auth/routes.py:243` - Rate limiter is defined but not wired into the FastAPI app, and login/registration endpoints lack rate limit decorators. This leaves auth endpoints vulnerable to brute force. Fix: set `app.state.limiter`, register `RateLimitExceeded` handler, and apply `@limiter.limit(LOGIN_RATE_LIMIT)` on auth endpoints.
- File: `frontend/pnpm-lock.yaml:1129` - `glob@10.4.5` (via `@vitest/coverage-v8`) is vulnerable to command injection in the CLI `-c` option (CVE-2025-64756). Fix: upgrade to `glob@10.5.0+` (or 11.1.0+) and re-lock.
- File: `infra/docker/.env.staging:38` - Staging DB/Redis credentials are weak, static values in repo. If staging is exposed, this is easily brute-forced. Fix: remove credentials from repo, use placeholders with a secrets manager, and rotate staging secrets.

### Medium
- Files: `backend/app/middleware/security_headers.py:21`, `backend/app/main.py:118` - Security headers middleware exists but is never registered, so CSP/HSTS/anti-clickjacking are not enforced. Fix: add `SecurityHeadersMiddleware` in `create_app()`.
- File: `backend/app/middleware/security_headers.py:31` - CSP includes `unsafe-inline` and `unsafe-eval`, significantly weakening XSS protection if enabled. Fix: move to nonce/hash-based CSP and restrict script sources.
- File: `backend/app/config/settings.py:43` - Insecure defaults (host `0.0.0.0`, `debug=True`, `auth_cookie_secure=False`, insecure `secret_key`) can ship to production if env config is missing or misloaded. Fix: enforce secure defaults for production or validate and fail startup when unsafe values are used.
- Files: `backend/app/auth/routes.py:235`, `backend/app/api/analytics.py:138`, `backend/app/main.py:271` - Error responses include raw exception text, leaking internals to clients. Fix: return generic messages and log server-side details.
- Files: `backend/app/api/companies.py:28`, `backend/app/api/companies.py:344` - `async` endpoints use synchronous `psycopg2`, blocking the event loop and making the API vulnerable to slow queries or DoS under load. Fix: use SQLAlchemy async/`asyncpg` or run blocking DB calls in a threadpool.
- File: `backend/app/database.py:12` - `DATABASE_URL` uses `settings.database_url` without a fallback; when unset, `create_engine(None)` will crash on startup. Fix: fall back to env var or a safe default when `settings.database_url` is `None`.
- Files: `frontend/pnpm-lock.yaml:1622`, `frontend/pnpm-lock.yaml:1052` - `vite@5.4.20` and `esbuild@0.21.5` are flagged by `pnpm audit` (moderate). Fix: update to `vite@5.4.21+` and `esbuild@0.25.0+`, then re-lock.
- File: `backend/test.db:1` - Committed SQLite database file can contain PII/secrets and causes non-deterministic state. Fix: remove from repo and add to `.gitignore`.

### Low
- File: `frontend/pnpm-lock.yaml:948` - `cookie@0.6.0` has a low-severity cookie serialization issue (CVE-2024-47764). Fix: update to `cookie@>=0.7.0` via `@sveltejs/kit` update.
- File: `backend/app/api/chat.py:29` - Chat API uses a hard-coded user and in-memory storage; if enabled, it bypasses real authentication/authorization. Fix: wire real auth dependency and persistent storage before enabling the router.
- Files: `frontend/package-lock.json:1`, `frontend/pnpm-lock.yaml:1` - Mixed lockfiles (`package-lock.json` and `pnpm-lock.yaml`) can lead to inconsistent installs. Fix: choose one package manager and remove the other lockfile.

## Recommended Actions (Prioritized)
1. Rotate all exposed secrets immediately, remove `.env` files from the repo, and enforce secret scanning in CI/pre-commit.
2. Update frontend dependencies to address `happy-dom`, `glob`, `vite`, `esbuild`, and `cookie` vulnerabilities; regenerate `pnpm-lock.yaml`.
3. Unify auth storage and user ID types; migrate schema and token subject handling; add tests for login + authorization.
4. Wire rate limiting and security headers in the FastAPI app; enforce safe production defaults (no debug, secure cookies, non-0.0.0.0).
5. Convert blocking DB access in async endpoints to async drivers or threadpool execution; fix `DATABASE_URL` fallback; remove `backend/test.db` from repo.
6. Re-run dependency checks with the correct Node version (>=24) for `pnpm outdated`, and re-run `pip-audit` including local editable dependencies (voice-core, auth-core, ai-core, events-core).
