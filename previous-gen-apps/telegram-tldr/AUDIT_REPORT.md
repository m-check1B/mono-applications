# Security and Code Audit Report: telegram-tldr

**Audit Date:** 2025-12-21 (Updated)
**Previous Audit:** 2025-12-20
**Auditor:** Claude Code (Opus 4.5)

---

## Executive Summary

Full codebase audit of the TL;DR Telegram bot covering security vulnerabilities, bugs, code quality, and error handling. The application is a FastAPI-based Telegram bot that summarizes group chat messages using Google's Gemini AI.

**Critical Finding:** Exposed credentials in `.env` file (Telegram bot token and Gemini API key are present).

**High Severity:** Unauthenticated webhook endpoint allows spoofed updates including forged payment events. Docker entrypoint misconfiguration runs polling mode instead of webhook server.

**Overall Risk Level:** HIGH - The application should not be deployed to production without addressing critical and high-severity issues.

---

## Codebase Structure

```
telegram-tldr/
├── app/
│   ├── __init__.py          # Empty
│   ├── main.py               # FastAPI app, webhook endpoint, lifespan
│   ├── core/
│   │   ├── __init__.py       # Empty
│   │   └── config.py         # Pydantic settings
│   ├── services/
│   │   ├── __init__.py       # Empty
│   │   ├── bot.py            # Aiogram handlers, payment logic
│   │   ├── buffer.py         # Redis message buffer, usage tracking
│   │   └── summarizer.py     # Gemini integration
│   ├── api/__init__.py       # Empty (unused)
│   ├── models/__init__.py    # Empty (unused)
│   └── schemas/__init__.py   # Empty (unused)
├── tests/                    # Empty directory
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── .env                      # Contains real credentials!
├── .env.example
└── .gitignore
```

---

## Issues by Severity

### CRITICAL

#### C1. Exposed Credentials in .env File
**File:** `.env:1-2`
**Status:** CONFIRMED - ACTIVE CREDENTIALS PRESENT

The `.env` file contains real, active credentials:
- Telegram Bot Token: `[REDACTED]`
- Gemini API Key: `[REDACTED]`

**Impact:** Complete bot takeover, unauthorized API usage, billing fraud.

**Immediate Action Required:**
1. Rotate Telegram bot token via @BotFather immediately
2. Rotate Gemini API key in Google AI Studio immediately
3. Verify `.env` has never been committed to any repository
4. Add `.env` to `.gitignore` if not already present (it is present)
5. Use environment variables from deployment environment instead

---

### HIGH

#### H1. Webhook Endpoint Lacks Authentication
**File:** `app/main.py:85-94`
**Status:** CONFIRMED

```python
@app.post("/webhook")
async def telegram_webhook(request: Request):
    update_data = await request.json()
    await process_update(update_data)
    return {"ok": True}
```

The webhook accepts any POST request without validating `X-Telegram-Bot-Api-Secret-Token`. Attackers can forge updates including payment confirmations.

**Impact:**
- Forged message updates
- Fake subscription payments (grant unlimited access without payment)
- Denial of service through malformed updates

**Fix:**
1. Add `telegram_webhook_secret` to settings
2. Pass `secret_token=` to `bot.set_webhook()`
3. Validate header in webhook handler or reject
4. Consider IP allowlisting for Telegram (149.154.160.0/20, 91.108.4.0/22)

---

#### H2. Docker Entrypoint Misconfiguration
**File:** `Dockerfile:42`

```dockerfile
CMD ["python", "-m", "app.main"]
```

This runs `app/main.py` as `__main__`, which triggers the polling fallback (lines 115-134) instead of starting the FastAPI webhook server.

**Impact:** Webhook deployments will not work. The bot will try to poll but fail since the webhook URL is set.

**Fix:**
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
```

Note: Use `127.0.0.1` per security policy, not `0.0.0.0`.

---

### MEDIUM

#### M1. Admin Check Fails Open
**File:** `app/services/bot.py:91-97`

```python
try:
    member = await bot.get_chat_member(chat_id, user_id)
    if member.status not in ("administrator", "creator"):
        await message.answer("Only admins can request summaries.")
        return
except Exception:
    pass  # Allow if can't check
```

Any exception (network error, rate limit, permissions) allows non-admins to request summaries.

**Impact:** Access control bypass, potential abuse of free tier by non-admins.

**Fix:** Fail closed - deny summary on admin check errors:
```python
except Exception as e:
    logger.warning(f"Admin check failed for {user_id}: {e}")
    await message.answer("Could not verify admin status. Please try again.")
    return
```

---

#### M2. Usage Limit Race Condition
**Files:** `app/services/bot.py:99-101`, `app/services/buffer.py:97-108`

```python
# Check (separate operation)
can_use, reason = await buffer.can_summarize(chat_id)

# ... generate summary ...

# Increment (separate operation)
usage = await buffer.increment_usage(chat_id)
```

Concurrent requests can exceed the free tier limit due to TOCTOU (time-of-check-time-of-use) race condition.

**Impact:** Free tier abuse, revenue loss.

**Fix:** Atomic check-and-increment using Redis Lua script or `WATCH`/`MULTI`/`EXEC` transaction.

---

#### M3. Summarization Failures Consume Usage
**Files:** `app/services/bot.py:133-142`, `app/services/summarizer.py:79-96`

The summarizer returns error strings instead of raising exceptions:
```python
except Exception as e:
    return f"Error generating summary: {str(e)}"
```

The caller cannot distinguish success from failure and charges usage regardless.

**Impact:** Users lose free tier quota on failed API calls.

**Fix:** Raise exceptions on failure, only increment usage after confirmed successful summary delivery.

---

#### M4. Payment Payload Parsing Can Crash
**File:** `app/services/bot.py:179-183`

```python
payload = message.successful_payment.invoice_payload
if payload.startswith("sub:"):
    chat_id = int(payload.split(":")[1])  # Can throw
    await buffer.set_subscribed(chat_id, months=1)
```

Malformed payloads like `"sub:"` or `"sub:abc"` will crash with `IndexError` or `ValueError`.

**Impact:** Payment processing failures, potential loss of legitimate subscriptions.

**Fix:**
```python
try:
    if payload.startswith("sub:"):
        parts = payload.split(":")
        if len(parts) >= 2:
            chat_id = int(parts[1])
            await buffer.set_subscribed(chat_id, months=1)
except (IndexError, ValueError) as e:
    logger.error(f"Invalid payment payload: {payload}")
```

---

#### M5. No Markdown Escaping / Message Length Limits
**Files:** `app/services/bot.py:142`, `app/services/summarizer.py:64-70`

User names and LLM output are injected directly into Markdown:
```python
formatted.append(f"[{user}]: {text}")  # No escaping
await message.answer(summary, parse_mode=ParseMode.MARKDOWN)
```

**Impact:**
- Markdown injection via malicious usernames (e.g., `*bold*`, `_italic_`, `[link](url)`)
- Message send failures if output exceeds Telegram's 4096 character limit
- Potential formatting corruption

**Fix:**
1. Escape Markdown special characters: `*`, `_`, `[`, `]`, `(`, `)`, `` ` ``
2. Switch to `ParseMode.HTML` with proper escaping (more robust)
3. Truncate/split messages exceeding 4096 chars

---

#### M6. Silent Redis Failures
**Files:** `app/services/buffer.py:48-49`, `app/services/buffer.py:75-76`

```python
if not self.redis:
    return  # Silent skip
```

When Redis is unavailable, operations silently skip. No logging, no indication to users.

**Impact:**
- Messages not stored, summaries show incomplete data
- Usage tracking fails, billing inconsistencies
- Users see "no messages found" without explanation

**Fix:** Log failures, add health checks, provide user feedback when in degraded mode.

---

#### M7. No Rate Limiting
**Files:** `app/main.py:85`, `app/services/bot.py:79`

No rate limiting on webhook endpoint or `/summary` command.

**Impact:**
- Denial of service via webhook flooding
- LLM cost explosion via summary spam
- Resource exhaustion

**Fix:** Add Redis-backed rate limiting per chat/user:
- Webhook: 100 updates/second per chat
- Summary: 1 request per chat per minute

---

### LOW

#### L1. Required Settings Default to Empty
**File:** `app/core/config.py:7-11`

```python
telegram_bot_token: str = ""
gemini_api_key: str = ""
```

App can start with empty credentials, failing at runtime instead of startup.

**Fix:** Add Pydantic validators or use `Field(min_length=1)` to fail fast.

---

#### L2. Naive UTC Timestamps
**File:** `app/services/buffer.py:51`

```python
ts = timestamp or datetime.utcnow()  # Naive datetime
```

`datetime.utcnow()` returns timezone-naive datetimes.

**Fix:** Use `datetime.now(timezone.utc)` for timezone-aware datetimes.

---

#### L3. Monthly Reset Logic Mismatch
**File:** `app/services/buffer.py:105-106`

```python
# Reset monthly (set expiry to end of month)
await self.redis.expire(key, 30 * 24 * 3600)
```

Comment says "end of month" but implementation uses 30-day sliding window. Users who subscribe on day 15 get until day 45.

**Fix:** Clarify intent. Either:
- Use sliding 30-day window (current behavior, update comment)
- Calculate actual end-of-month for billing alignment

---

#### L4. Webhook Error Details Leak
**File:** `app/main.py:92-94`

```python
except Exception as e:
    logger.error(f"Webhook error: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

Internal error details (stack traces, paths, internal state) exposed to attackers.

**Fix:** Return generic message, use `logger.exception()` for full traceback server-side.

---

#### L5. LLM Error Details Leak
**File:** `app/services/summarizer.py:95-96`

```python
except Exception as e:
    return f"Error generating summary: {str(e)}"
```

Gemini API errors (auth failures, quota exceeded, internal errors) shown to users.

**Fix:** Log details internally, return generic user-facing message.

---

#### L6. Dead Code: estimate_cost Function
**File:** `app/services/summarizer.py:99-114`

`estimate_cost()` is defined but never used.

**Fix:** Remove it or integrate into telemetry/observability.

---

#### L7. No Automated Tests
**File:** `tests/` (empty directory)

Zero test coverage. Critical payment and access control logic untested.

**Fix:** Add unit tests for:
- Buffer operations (add/get messages, usage tracking)
- Webhook authentication
- Admin permission checks
- Payment payload parsing
- Summarizer error handling

---

#### L8. Outdated Dependencies
**File:** `pyproject.toml`

Multiple dependencies behind current releases (as of audit date):
- aiogram 3.22.0 → 3.23.0
- fastapi 0.124.0 → 0.126.0
- google-generativeai 0.8.5 → 0.8.6
- pydantic 2.11.10 → 2.12.5

**Fix:** Run `uv lock --upgrade && uv sync`, then re-audit.

---

#### L9. Empty Module Placeholders
**Files:** `app/api/__init__.py`, `app/models/__init__.py`, `app/schemas/__init__.py`

These modules are empty and unused, suggesting incomplete refactoring.

**Fix:** Remove empty placeholder modules or document future intent.

---

#### L10. Global Mutable State
**Files:** `app/services/buffer.py:145`, `app/services/summarizer.py:7`

```python
buffer = MessageBuffer()  # Global instance
_model = None  # Global mutable state
```

Global state can cause issues in testing and multiprocessing.

**Impact:** Low, but complicates testing and can cause subtle bugs.

**Fix:** Consider dependency injection pattern for better testability.

---

## Code Quality Summary

| Category | Score | Notes |
|----------|-------|-------|
| **Security** | 2/5 | Critical credential exposure, missing auth |
| **Error Handling** | 2/5 | Fails open, leaks details, silent failures |
| **Code Structure** | 3/5 | Clean separation, but unused modules |
| **Type Safety** | 3/5 | Type hints present but incomplete |
| **Testing** | 1/5 | No tests |
| **Documentation** | 2/5 | Minimal inline docs, no README |
| **Dependencies** | 3/5 | Modern stack, slightly outdated |

---

## Recommended Actions (Priority Order)

### Immediate (Before Any Deployment)

1. **Rotate credentials** - Telegram token and Gemini API key are exposed
2. **Add webhook authentication** - Prevent forged updates/payments
3. **Fix Dockerfile entrypoint** - Run uvicorn, not polling mode

### Before Production

4. **Fix admin check** to fail closed
5. **Add atomic usage enforcement** (Redis transaction)
6. **Add rate limiting** on webhook and commands
7. **Escape Markdown / handle message length**

### Technical Debt

8. Add automated tests
9. Update dependencies
10. Clean up unused modules
11. Improve error handling (no detail leaks, proper logging)
12. Add startup validation for required settings

---

## Appendix: Files Reviewed

| File | Lines | Issues Found |
|------|-------|--------------|
| `app/main.py` | 135 | H1, L4 |
| `app/core/config.py` | 40 | L1 |
| `app/services/bot.py` | 233 | M1, M2, M3, M4, M5 |
| `app/services/buffer.py` | 146 | M2, M6, L2, L3, L10 |
| `app/services/summarizer.py` | 115 | M3, M5, L5, L6, L10 |
| `Dockerfile` | 43 | H2 |
| `.env` | 8 | C1 |
| `pyproject.toml` | 42 | L8 |

---

*Report generated by Claude Code (Opus 4.5) for feature W4-001*
