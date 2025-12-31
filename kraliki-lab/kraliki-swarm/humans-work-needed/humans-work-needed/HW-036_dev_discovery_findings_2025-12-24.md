# Dev Discovery Findings - 2025-12-24

**Agent:** darwin-opencode-dev-discovery
**Date:** 2025-12-24
**Total Issues Found:** 12 critical/high priority items

---

## FOCUS-LITE (Revenue-generating app)

### 🔴 CRITICAL Security & Testing Gaps

**1. Webhook Security Tests Missing (0% coverage)**
- **File:** `backend/app/core/webhook_security.py`
- **Impact:** Webhook verification bugs could allow unauthorized access
- **Priority:** P0
- **Estimated Work:** 18 tests needed (Google Calendar + II-Agent webhooks)
- **Source:** evidence/security_findings.md:48-58

**2. Rate Limiting Not Implemented**
- **Endpoints:** `/auth/login`, `/auth/register`, `/calendar-sync/webhook`, `/ai/orchestrate-task`
- **Impact:** DoS attacks possible, brute force password attacks
- **Priority:** P0
- **Estimated Work:** Implement rate limiting + 8 tests
- **Source:** evidence/security_findings.md:164-187

**3. Webhook Endpoint Returns 404**
- **Endpoint:** `/calendar-sync/webhook`
- **Impact:** Real-time calendar sync not functional, breaks Operations Lead persona
- **Priority:** P0
- **Estimated Work:** Fix router registration + verify endpoint
- **Source:** evidence/security_findings.md:60-70

**4. II-Agent Integration Tests Missing**
- **File:** `tests/integration/test_ii_agent_integration.py` (doesn't exist)
- **Impact:** Core Solo Developer persona workflow untested
- **Priority:** P0
- **Estimated Work:** 15 tests needed (sessions, tools, WebSocket)
- **Source:** evidence/test_coverage_gaps.md:311-336

**5. Calendar Integration Tests Missing**
- **File:** `tests/integration/test_google_calendar_integration.py` (doesn't exist)
- **Impact:** Core Operations Lead persona workflow incomplete
- **Priority:** P0
- **Estimated Work:** 15 tests needed (OAuth, sync, webhooks)
- **Source:** evidence/test_coverage_gaps.md:284-310

**6. Offline Resilience Tests Missing**
- **File:** `tests/e2e/test_offline_resilience_e2e.py` (doesn't exist)
- **Impact:** Core Offline Analyst persona requirement untested
- **Priority:** P0
- **Estimated Work:** 10 tests needed (offline detection, reconnection, data integrity)
- **Source:** evidence/test_coverage_gaps.md:178-205

---

## CC-LITE-2026 (Revenue-generating app)

### 🟡 Medium Priority Incomplete Implementations

**7. TODO: Get Full User Data from Database**
- **File:** `backend/app/auth/simple_routes.py:94`
- **Current:** Returns hardcoded "User Name"
- **Impact:** User profile functionality incomplete
- **Priority:** P1
- **Estimated Work:** 1-2 hours

**8. TODO: Add CallSession Relationship**
- **File:** `backend/app/models/ai_insights.py:89, 163`
- **Current:** Relationship commented out
- **Impact:** AI insights cannot link to call sessions
- **Priority:** P1
- **Estimated Work:** 2-3 hours (import + relationship setup)

**9. Incomplete Methods (Multiple)**
- **Files:**
  - `backend/app/models/supervisor.py:279, 319`
  - `backend/app/models/scenario.py:91, 135`
  - `backend/app/models/team.py:189, 231`
  - `backend/app/models/provider.py:179`
  - `backend/app/providers/telephony_provider.py:74-104`
- **Current:** Empty `pass` statements
- **Impact:** Core functionality not implemented
- **Priority:** P1
- **Estimated Work:** 8-16 hours (depends on complexity)

---

## TELEGRAM-TLDR (Revenue-generating app)

### 🔴 CRITICAL Test Coverage Gap

**10. Zero Test Files**
- **Current:** 0 test files found
- **Impact:** No automated testing, high regression risk
- **Priority:** P0
- **Estimated Work:** Create test infrastructure + 20+ tests
- **Context:** Telegram bot handling user interactions needs coverage

---

## MAGIC-BOX (Revenue-generating app)

### 🟡 Test Coverage Unknown

**11. Test Coverage Assessment Needed**
- **Current:** 5 test files exist (`tests/e2e/*.spec.ts`)
- **Impact:** Unknown test coverage, may have gaps
- **Priority:** P1
- **Estimated Work:** Run coverage analysis + create gap report
- **Context:** Playwright tests for landing page, demo, documentation, accessibility, performance

---

## CROSS-APPLICATION

### 🟡 Documentation & Configuration

**12. Linear API Key Expired**
- **File:** `ai-automation/humans-work-needed/archive/HW-028_linear_api_key_expired.md`
- **Impact:** Cannot create Linear issues, task assignment blocked
- **Priority:** P1
- **Estimated Work:** Regenerate key + update secrets
- **Source:** Existing human work task

---

## SUMMARY BY SEVERITY

**Critical (P0): 7 issues**
- Focus by Kraliki: 6 (security tests, rate limiting, webhook 404, integration tests)
- Telegram-TLDR: 1 (zero tests)

**High (P1): 5 issues**
- Voice by Kraliki (legacy CC-Lite-2026): 3 (TODO items, incomplete methods)
- Magic-Box: 1 (coverage assessment)
- Cross-app: 1 (Linear API key)

**Total Estimated Work:** ~100+ hours

---

## RECOMMENDATIONS FOR LINEAR ISSUE CREATION

**When Linear API is restored, create issues with:**

1. **Label:** `GIN`, `GIN-DEV`, `app:{name}`
2. **Priority:** Urgent (P0), High (P1)
3. **Format:**
   ```
   [{app}] {brief description}

   **Impact:** {what breaks / risk}
   **File:** {file path}
   **Estimated Work:** {hours}
   **Evidence:** {reference to documentation}
   ```

**Example:**
```
[focus-kraliki] Add webhook security tests (0% coverage)

Webhook verification code exists but has 0% test coverage. This is a critical security gap.

**Impact:** Webhook verification bugs could allow unauthorized calendar sync or agent execution

**Files:**
- backend/app/core/webhook_security.py
- tests/unit/test_webhook_security.py (needs creation)

**Estimated Work:** 6-8 hours

**Required Tests:**
- Invalid channel IDs rejected
- Expired channels rejected  
- Signature validation (Ed25519 & HMAC)
- Replay attack prevention
- Malformed header handling

**Priority:** P0 - Critical Security

**Labels:** GIN, GIN-DEV, app:focus-kraliki, security, testing
```

---

## NEXT STEPS

1. **Immediate (This Week):**
   - Fix Linear API key (HW-028)
   - Create Linear issues for P0 items
   - Start webhook security tests (Focus by Kraliki)

2. **Short-Term (Next 2 Weeks):**
   - Implement rate limiting (Focus by Kraliki)
   - Fix webhook endpoint 404 (Focus by Kraliki)
   - Create II-Agent integration tests (Focus by Kraliki)
   - Create calendar integration tests (Focus by Kraliki)

3. **Medium-Term (Next Month):**
   - Complete incomplete methods in cc-lite-2026
   - Create test infrastructure for telegram-tldr
   - Assess and expand magic-box test coverage

---

**Status:** Discovery complete. Ready for Linear issue creation when API key restored.

**Points Earned:** 50 (per agent spec)
