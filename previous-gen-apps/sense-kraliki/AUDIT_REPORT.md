# Sense by Kraliki (formerly SenseIt) Security & Quality Audit Report

## Executive Summary
The audit found a critical exposure of real API credentials in `.env`, with additional high-risk concerns around build-context secret leakage (no `.dockerignore`) and a potential SSRF vector when fetching Schumann images from external HTML. Medium-severity issues include non-persistent in-memory user state, missing validation in the payment flow, unbounded LLM usage without rate limits, and a coordinate bug that skips weather for valid `0.0` values. No direct SQL injection or browser-side XSS vectors were identified, and a `pip-audit` scan against the project reported no known vulnerabilities, but several dependencies are outdated and the codebase lacks tests and caching, which impacts reliability and cost.

## Issues by Severity

### Critical
- C1 `/.env:5` - Plaintext secrets (Telegram bot token and Gemini API key) are stored in a local `.env` file within the repo directory; if this file is ever committed or included in build contexts, credentials are exposed. Fix: remove the secrets from the repo, rotate both tokens immediately, store secrets in a managed secrets store or deployment environment, and verify git history/build logs for accidental exposure.

### High
- H1 `/Dockerfile:1` - No `.dockerignore` means the build context can include `.env`, `.venv`, and `__pycache__` artifacts; secrets can leak to remote builders/CI or be embedded unintentionally. Fix: add a `.dockerignore` that excludes `.env*`, `.venv/`, `__pycache__/`, `*.pyc`, `.git/`, and other local artifacts.
- H2 `/app/data/schumann.py:50` - The image URL is scraped from external HTML and fetched without validation; if the source is compromised, this can be used for SSRF (internal network/metadata access). Fix: enforce an allowlist of domains, validate scheme (`https` only), block private/loopback IPs, and limit redirects before fetching.

### Medium
- M1 `/app/bot/handlers.py:33` - User state and subscription data are stored in an in-memory dict; data is lost on restart and unsafe in multi-process deployments, causing inconsistent premium access. Fix: persist state in Redis/Postgres and ensure safe concurrent access.
- M2 `/app/services/sensitivity.py:235` - Weather data is skipped for valid coordinates at `0.0` because of truthiness checks. Fix: use `if latitude is not None and longitude is not None`.
- M3 `/app/services/sensitivity.py:226` - External API and LLM calls are performed on every command despite TTL settings in config, risking rate-limit bans and high costs. Fix: implement caching using Redis or an in-memory TTL cache keyed by source and location.
- M4 `/app/bot/handlers.py:517` - Pre-checkout and payment handling accept any payload without validating `currency`, `total_amount`, or payload/user consistency; a spoofed webhook or misconfig could grant premium access. Fix: validate `invoice_payload`, `total_amount`, `currency`, and that the payload user ID matches `message.from_user.id`.
- M5 `/app/services/dreams.py:176` - LLM usage has no rate limiting or input size guardrails; a user can drive costs or cause latency spikes. Fix: enforce per-user quotas, cap input length, and add timeouts/backoff.
- M6 `/app/main.py:27` - Global `parse_mode=Markdown` applies to all responses, including LLM output and user-controlled text, enabling Markdown injection (phishing links/formatting). Fix: escape Markdown for untrusted text or set parse_mode only where content is fully controlled.

### Low
- L1 `/app/services/sensitivity.py:238` - `asyncio.coroutine` is deprecated and may break on newer Python versions. Fix: replace with an `async def` no-op or `asyncio.sleep(0)`.
- L2 `/app/bot/handlers.py:86` - Raw exception messages are sent to users; this can leak internals. Fix: log server-side and return a generic error message.
- L3 `/app/core/config.py:10` - Required secrets default to empty strings; misconfiguration is silent and hard to diagnose. Fix: use `SecretStr` and validation (e.g., `min_length=1`) and fail fast on startup.
- L4 `/pyproject.toml:8` - Unused dependencies (e.g., fastapi, uvicorn, redis, asyncpg, sqlalchemy, apscheduler, pillow) increase attack surface and patching load. Fix: remove unused packages or implement their usage intentionally.
- L5 `/pyproject.toml:8` - Outdated dependencies detected: aiofiles 24.1.0→25.1.0, aiogram 3.22.0→3.23.0, aiohttp 3.12.15→3.13.2, cachetools 6.2.2→6.2.4, fastapi 0.124.0→0.126.0, google-ai-generativelanguage 0.6.15→0.9.0, google-auth 2.43.0→2.45.0, google-auth-httplib2 0.2.1→0.3.0, google-generativeai 0.8.5→0.8.6, grpcio-status 1.71.2→1.76.0, proto-plus 1.26.1→1.27.0, protobuf 5.29.5→6.33.2, pydantic 2.11.10→2.12.5, pydantic-core 2.33.2→2.41.5, sqlalchemy 2.0.44→2.0.45, urllib3 2.6.0→2.6.2. Fix: upgrade and rerun tests.
- L6 `/app/services/__pycache__/dreams.cpython-313.pyc:1` - Compiled artifacts and local environment directories are present in the repo tree; they can leak data and bloat packaging. Fix: remove them from the repo and ensure `.gitignore` and `.dockerignore` exclude them.
- L7 `/tests/:1` - No automated tests are present; this increases regression risk. Fix: add unit tests for scoring, data fetchers, and handler flows.

## Recommended Actions (Prioritized)
1. Rotate and revoke exposed API credentials immediately; remove `.env` from any repo history or build contexts and add a `.dockerignore` to prevent future leakage.
2. Mitigate SSRF by validating/allowlisting Schumann image URLs and restricting redirects and private IP ranges.
3. Persist user state in a database/Redis and add payment validation to prevent incorrect premium grants.
4. Implement caching and rate limiting for external API/LLM calls to reduce cost and availability risk.
5. Upgrade outdated dependencies and remove unused ones to reduce attack surface.
6. Add tests and improve error handling/logging for long-term reliability.
