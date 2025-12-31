# Focus by Kraliki Security & Code Quality Audit Report

**Audit Date:** 2025-12-20
**Application:** focus-kraliki
**Type:** Fullstack (Python + Svelte)
**Priority:** MEDIUM
**Auditor:** Automated Security Audit

---

## Executive Summary

Focus by Kraliki demonstrates solid foundational security practices with proper .gitignore configuration, SQLAlchemy ORM usage preventing SQL injection, and no hardcoded production secrets. However, the audit identified **1 Critical**, **5 High**, **12 Medium**, and **8 Low** severity issues requiring attention before production launch. The most urgent concerns are: (1) XSS vulnerability in Markdown rendering without DOMPurify sanitization, (2) bare exception handlers silently swallowing errors, (3) potential race conditions with global state in async contexts, and (4) multiple resource leak risks with unclosed connections. The application requires approximately 2-3 weeks of focused remediation to be considered launch-ready.

---

## Issues by Severity

### Critical (1 issue)

| # | File:Line | Issue | Fix Suggestion |
|---|-----------|-------|----------------|
| C1 | `frontend/src/lib/components/MarkdownRenderer.svelte:72` | **XSS Vulnerability**: Uses `{@html renderedHtml}` to render Markdown without sanitization. Malicious user-controlled Markdown can execute arbitrary JavaScript. | Install DOMPurify: `pnpm add dompurify @types/dompurify`. Wrap output: `renderedHtml = DOMPurify.sanitize(marked.parse(content))`. Add CSP headers. |

---

### High (5 issues)

| # | File:Line | Issue | Fix Suggestion |
|---|-----------|-------|----------------|
| H1 | `backend/app/routers/calendar_sync.py:209,578` | **Silent Exception Swallowing**: Bare `except:` clauses without logging can hide critical authentication or network errors. | Replace with specific exceptions: `except CalendarSyncError as e: logger.error(f"Sync failed: {e}")` |
| H2 | `backend/app/routers/billing.py:104,133,163,186` | **Sensitive Data Exposure**: Stripe errors directly passed in HTTP responses may leak payment system internals to attackers. | Sanitize error messages: `detail="Payment processing failed"` instead of `detail=str(stripe_error)` |
| H3 | `backend/app/routers/time_entries.py:multiple` | **Boolean Logic Error**: Using string `"true"` instead of boolean `True` for billable comparisons: `if entry.billable == "true"`. | Fix type: Change to `if entry.billable is True` or ensure schema uses `bool` type |
| H4 | `backend/app/services/gemini_file_search.py:33` | **Race Condition Risk**: Global variables `_genai, _GEMINI_AVAILABLE` modified without synchronization in async context. | Use threading.Lock or asyncio.Lock for thread-safe initialization |
| H5 | `backend/app/core/event_bus.py:56-57` | **Non-Thread-Safe Singleton**: Global `_event_bus` lacks thread-safe initialization pattern. | Implement double-checked locking or use `functools.lru_cache` for singleton |

---

### Medium (12 issues)

| # | File:Line | Issue | Fix Suggestion |
|---|-----------|-------|----------------|
| M1 | `backend/app/core/cache.py:58,75,86` | **Resource Leak**: Redis connections created without explicit closure mechanism. | Wrap in context manager or implement `__aenter__/__aexit__` |
| M2 | `backend/app/core/events.py:81` | **Resource Leak**: RabbitMQ connection via `aio_pika.connect_robust()` without clear closure strategy. | Add connection.close() in shutdown handler or use async context manager |
| M3 | `backend/app/routers/flow_memory.py:37` | **Resource Leak**: `_redis_client` global without connection pool management. | Use connection pooling with proper lifecycle management |
| M4 | `backend/app/middleware/rate_limit.py:20` | **Resource Leak**: Synchronous Redis client without explicit cleanup. | Implement proper startup/shutdown handlers |
| M5 | `ii-agent/src/ii_agent/tools/clients/web_search_client.py` | **Unsafe Environment Access**: Uses `os.environ[]` which raises KeyError if variable missing. | Replace with `os.getenv('VAR', default)` with proper fallback |
| M6 | `backend/app/routers/ai.py` | **Unsafe Environment Access**: Multiple instances of `os.environ[]` without fallback. | Use `os.getenv()` with defaults throughout |
| M7 | `backend/app/routers/agent_tools.py:810-812` | **N+1 Query Problem**: Separate queries for memberships and workspaces in loop. | Use `joinedload()` or `selectinload()`: `db.query(WorkspaceMember).options(joinedload(WorkspaceMember.workspace))` |
| M8 | `backend/app/routers/swarm_tools.py:409` | **Missing Pagination**: All projects loaded without limit. | Add `limit` and `offset` parameters: `.limit(page_size).offset(page * page_size)` |
| M9 | `backend/app/routers/flow_memory.py:86,165` | **Poor Error Context**: Generic 500 errors with minimal debugging information. | Add structured error logging with request IDs and stack traces |
| M10 | `backend/app/services/calendar_adapter.py:14` | **Bare Exception**: `except Exception:` without specific handling. | Use specific exceptions: `except GoogleAPIError as e:` |
| M11 | `backend/app/core/security.py:86` | **Bare Exception**: Silent error handling in security-critical code. | Log and re-raise with appropriate HTTP status |
| M12 | `backend/app/services/shadow_analyzer.py` | **Non-Deterministic Logic**: Modulo-based logic `day % 3` could produce inconsistent results. | Document expected behavior or use deterministic mapping |

---

### Low (8 issues)

| # | File:Line | Issue | Fix Suggestion |
|---|-----------|-------|----------------|
| L1 | `backend/app/routers/shadow.py:24-35` | **Test Code in Production**: Mock Anthropic client classes appear to be test placeholders. | Move to test fixtures or conditional import |
| L2 | `backend/app/services/calendar_adapter.py:13` | **Type Ignore**: Bypasses type checking for import. | Add proper type stub or use `typing.TYPE_CHECKING` |
| L3 | `backend/app/routers/billing.py:13` | **Type Ignore**: Stripe library import bypasses type checking. | Install `types-stripe` or create local stub |
| L4 | `backend/app/core/events.py:13` | **Type Ignore**: Event bus import bypasses type checking. | Add type annotations to imported module |
| L5 | Multiple files | **Excessive Any Types**: Many core modules use `Any` instead of specific types. | Replace with `Union`, `Optional`, or custom TypedDict |
| L6 | `backend/app/routers/knowledge.py:377` | **Missing Pagination**: Unrestricted items query. | Add pagination parameters |
| L7 | `frontend/src/lib/api/client.ts:257` | **Minimal Error Handling**: Only checks `response.ok` without parsing. | Add comprehensive error parsing and user-friendly messages |
| L8 | `.github/workflows/ci-cd.yml` | **Test Keys in CI**: Uses `test-key` values instead of GitHub Secrets. | Move to repository secrets: `${{ secrets.ANTHROPIC_API_KEY }}` |

---

## Security Summary

### What's Working Well

| Area | Status | Notes |
|------|--------|-------|
| **Secret Management** | GOOD | .gitignore properly excludes .env files; .env.example uses placeholders |
| **SQL Injection Protection** | GOOD | SQLAlchemy ORM used consistently; no raw SQL concatenation found |
| **Git Hygiene** | GOOD | No production secrets committed; comprehensive .gitignore |
| **CORS Configuration** | GOOD | Configurable allowed origins via environment variables |
| **JWT Authentication** | GOOD | Proper token handling with bcrypt password hashing |
| **Input Validation** | GOOD | Pydantic schemas used for request validation |

### Areas Needing Improvement

| Area | Risk | Priority |
|------|------|----------|
| **XSS Prevention** | Critical | Immediate |
| **Error Handling** | High | This Sprint |
| **Resource Management** | Medium | Next Sprint |
| **Type Safety** | Low | Ongoing |

---

## Recommended Actions (Prioritized)

### Immediate (Before Launch)

1. **Fix XSS in Markdown Renderer**
   - Install DOMPurify: `cd frontend && pnpm add dompurify @types/dompurify`
   - Update `MarkdownRenderer.svelte` to sanitize output
   - Add Content-Security-Policy headers

2. **Fix Silent Exception Handlers**
   - Search for `except:` and `except Exception:` patterns
   - Replace with specific exception types
   - Add logging to all catch blocks

3. **Sanitize Billing Error Messages**
   - Review all `billing.py` HTTP exceptions
   - Remove internal error details from responses
   - Log full errors server-side only

### This Sprint (Week 1-2)

4. **Add Thread Safety to Globals**
   - Audit all `global` variable declarations
   - Add locks for concurrent access
   - Consider dependency injection instead

5. **Fix Resource Leaks**
   - Implement connection pooling for Redis
   - Add shutdown handlers for all persistent connections
   - Use async context managers consistently

6. **Fix Type Comparison Bug**
   - Change `billable == "true"` to proper boolean comparison
   - Audit for similar string/bool confusion

### Next Sprint (Week 3-4)

7. **Add Pagination to List Endpoints**
   - Audit all `.all()` queries
   - Add `limit` and `offset` parameters
   - Set reasonable default limits (50-100 items)

8. **Fix N+1 Queries**
   - Use SQLAlchemy eager loading
   - Add database indexes for common queries

9. **Improve Type Safety**
   - Reduce `Any` type usage
   - Remove unnecessary `type: ignore` comments
   - Add type stubs for external libraries

### Ongoing

10. **Dependency Updates**
    - Run `pip audit` weekly
    - Enable Dependabot for automated PRs
    - Monitor AI SDK libraries for security patches

---

## Test Coverage Notes

Current test coverage is at **50%** (target: 80%). Priority areas for additional testing:
- Calendar sync routes (0% → 80%)
- Service layer (shadow, flow_memory, ai_scheduler)
- Error handling paths
- Security boundary tests

---

## Files Requiring Immediate Review

| Priority | File | Reason |
|----------|------|--------|
| P0 | `frontend/src/lib/components/MarkdownRenderer.svelte` | XSS vulnerability |
| P0 | `backend/app/routers/billing.py` | Sensitive data exposure |
| P0 | `backend/app/routers/calendar_sync.py` | Silent exception handling |
| P1 | `backend/app/routers/time_entries.py` | Type comparison bug |
| P1 | `backend/app/services/gemini_file_search.py` | Race condition |
| P1 | `backend/app/core/event_bus.py` | Thread safety |
| P2 | `backend/app/core/cache.py` | Resource leak |
| P2 | `backend/app/core/events.py` | Resource leak |

---

## Verification Commands

```bash
# Check for bare except clauses
grep -rn "except:" backend/app --include="*.py"

# Check for os.environ[] usage
grep -rn "os.environ\[" backend/app --include="*.py"

# Check for type: ignore
grep -rn "type: ignore" backend/app --include="*.py"

# Check for @html in Svelte
grep -rn "{@html" frontend/src --include="*.svelte"

# Run security scan
cd backend && pip audit

# Check test coverage
cd backend && pytest --cov --cov-report=term-missing
```

---

## Conclusion

**Launch Readiness: NOT READY**

Focus by Kraliki has a solid security foundation but requires remediation of the identified issues before production deployment. The XSS vulnerability (C1) and silent exception handling (H1) are blocking issues. Estimated remediation time: **2-3 weeks** with focused effort.

**Priority Path:**
1. Week 1: Fix Critical (C1) and High (H1-H5) issues
2. Week 2: Fix Medium (M1-M12) issues
3. Week 3: Address Low issues and increase test coverage

After remediation, conduct a follow-up security review before launch.

---

*Report generated by automated audit system. Manual review recommended for all findings.*
