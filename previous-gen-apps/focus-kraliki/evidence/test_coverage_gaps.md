# Test Coverage Gaps Analysis
**Date:** 2025-11-16
**Analyst:** Quality Lead (User Simulation Swarm)
**Mission:** Identify and prioritize test coverage gaps

---

## Executive Summary

Comprehensive analysis of test coverage across Focus by Kraliki application, identifying gaps between current test coverage (50%) and target coverage (80%). This report builds on existing TESTING_COVERAGE_REPORT.md to provide actionable recommendations for user simulation findings.

**Current Coverage:** 50%
**Target Coverage:** 80%
**Gap:** 30 percentage points
**Priority Test Scenarios Identified:** 47

---

## 1. Coverage Overview

### 1.1 Current State by Module

| Module | Coverage | Status | Priority |
|--------|----------|--------|----------|
| **Models** | 94-100% | ✅ Excellent | Maintain |
| **Onboarding** | 95%+ | ✅ Excellent | Maintain |
| **Events** | 60%+ | 🟡 Good | Improve to 80% |
| **Calendar Sync** | 40%+ | 🟡 Fair | Critical for Operations Lead persona |
| **Webhook Security** | 0% | 🔴 None | Critical security gap |
| **Agent Sessions** | 0% | 🔴 None | Critical for Solo Developer persona |
| **Services Layer** | 10-30% | 🔴 Poor | High impact |
| **AI Routers** | 26-44% | 🟡 Fair | Critical for all personas |

### 1.2 Gap Classification

**Critical Gaps (0-40% coverage):**
- Webhook security: 0%
- Agent sessions: 0%
- Calendar sync: 40%
- Services layer: 10-30%

**Important Gaps (40-70% coverage):**
- AI routers: 26-44%
- Events: 60%
- Assistant: 44%

**Minor Gaps (70-80% coverage):**
- Core security: 79%
- Voice services: 65%

---

## 2. Persona-Specific Coverage Gaps

### 2.1 Solo Developer (AI Enthusiast) Persona

**Key Workflows:**
- Onboarding with all AI features enabled ✅ (95% coverage)
- II-Agent session creation and execution 🔴 (0% coverage)
- Voice-to-agent workflow 🟡 (65% voice, 0% agent)
- Static site deployment 🔴 (0% coverage)
- Tool execution monitoring 🔴 (0% coverage)

**Missing Test Scenarios:**

1. **II-Agent Workflow** (Priority: P0)
   - [ ] Create agent session with user_id
   - [ ] Send voice command → agent planning
   - [ ] Agent tool execution (markdown converter)
   - [ ] Agent tool execution (static deploy)
   - [ ] WebSocket message streaming
   - [ ] Session cleanup on disconnect
   - [ ] Token budget enforcement
   - [ ] Error handling (network drop, timeout)

2. **Voice Integration** (Priority: P1)
   - [ ] Voice transcription with Gemini enabled
   - [ ] Voice button visibility when enabled
   - [ ] Voice endpoint blocked when disabled
   - [ ] Voice-to-agent handoff

3. **Deployment** (Priority: P1)
   - [ ] Static site deploy tool success
   - [ ] Deploy tool failure handling
   - [ ] Deployment URL generation
   - [ ] Post-deploy verification

**Coverage Gap Impact:** HIGH - Core persona workflow untested

---

### 2.2 Privacy-Sensitive Freelancer Persona

**Key Workflows:**
- Onboarding with all AI disabled ✅ (95% coverage)
- Feature toggle persistence ✅ (85% coverage)
- SQL fallback when Gemini disabled ✅ (85% coverage)
- BYOK messaging visibility 🟡 (tested but UI coverage unclear)
- Network call verification 🔴 (0% coverage)

**Missing Test Scenarios:**

1. **Network Monitoring** (Priority: P0)
   - [ ] No Gemini API calls when disabled
   - [ ] No II-Agent connections when disabled
   - [ ] No voice API calls when disabled
   - [ ] SQL fallback produces correct results
   - [ ] File search works without Gemini

2. **BYOK Integration** (Priority: P1)
   - [ ] BYOK messaging shown when AI disabled
   - [ ] BYOK users can enable features with own keys
   - [ ] BYOK users not charged for AI usage
   - [ ] BYOK key validation

3. **Privacy Compliance** (Priority: P1)
   - [ ] Data export includes all user data
   - [ ] Privacy acknowledgment required before enabling AI
   - [ ] User data not sent to third parties when AI disabled

**Coverage Gap Impact:** MEDIUM - Privacy validation needed

---

### 2.3 Operations Lead (Calendar Power User) Persona

**Key Workflows:**
- Onboarding ✅ (95% coverage)
- Google OAuth flow 🟡 (90% OAuth, 0% integration)
- Calendar sync (manual) 🟡 (40% coverage)
- Webhook notifications 🔴 (0% coverage)
- Conflict resolution ✅ (100% unit, 0% integration)

**Missing Test Scenarios:**

1. **Google Calendar OAuth E2E** (Priority: P0)
   - [ ] OAuth init → authorization → callback → token exchange
   - [ ] OAuth with real Google API (or mock)
   - [ ] Token storage in user preferences
   - [ ] Token refresh when expired
   - [ ] OAuth error handling (user denial, network error)

2. **Calendar Sync Integration** (Priority: P0)
   - [ ] Manual sync creates events in Focus from Google
   - [ ] Manual sync pushes Focus tasks to Google
   - [ ] Bidirectional sync consistency
   - [ ] Sync latency measurement (<10s target)
   - [ ] Sync with large event counts (100+ events)

3. **Webhook Integration** (Priority: CRITICAL)
   - [ ] Webhook endpoint accessible (currently 404)
   - [ ] Webhook signature verification
   - [ ] Webhook triggers background sync
   - [ ] Webhook delivery tracking
   - [ ] Webhook channel expiration handling
   - [ ] Webhook resource states (sync, exists, not_exists)

4. **Conflict Resolution E2E** (Priority: P1)
   - [ ] Simultaneous edits in both systems detected
   - [ ] Last modified wins policy applied
   - [ ] Calendar wins policy applied
   - [ ] Focus wins policy applied
   - [ ] Manual resolution UI presented
   - [ ] Merged data applied correctly

**Coverage Gap Impact:** CRITICAL - Core persona workflow broken (webhook 404)

---

### 2.4 Offline-First Analyst Persona

**Key Workflows:**
- Onboarding ✅ (95% coverage)
- II-Agent offline behavior 🔴 (0% coverage)
- WebSocket disconnect handling 🔴 (0% coverage)
- Offline detection 🔴 (0% coverage)
- Reconnection and sync 🔴 (0% coverage)

**Missing Test Scenarios:**

1. **Offline Detection** (Priority: P0)
   - [ ] Network disconnect detected within 5 seconds
   - [ ] Offline indicator shown in UI
   - [ ] WebSocket disconnect event handled
   - [ ] Agent session state preserved

2. **Offline Behavior** (Priority: P0)
   - [ ] Agent session queues work when offline
   - [ ] Clear error message if cannot continue offline
   - [ ] No data loss on disconnect
   - [ ] Partial work not corrupted

3. **Reconnection** (Priority: P0)
   - [ ] Reconnection detected within 5 seconds
   - [ ] Queued work auto-syncs on reconnect
   - [ ] User prompted to retry if needed
   - [ ] Session resumes correctly

4. **Data Integrity** (Priority: CRITICAL)
   - [ ] No partial/corrupted state after disconnect
   - [ ] Idempotent operations (retry safe)
   - [ ] Transaction rollback on failure

**Coverage Gap Impact:** CRITICAL - Core persona requirement untested

---

## 3. Security Test Coverage Gaps

Based on `/evidence/security_findings.md` analysis:

### 3.1 Webhook Security (Priority: CRITICAL)

**Current Coverage:** 0%

**Missing Tests:**

1. **Google Calendar Webhook** (8 tests needed)
   - [ ] Invalid channel ID rejected (401)
   - [ ] Expired channel rejected (401)
   - [ ] Missing X-Goog-Channel-Id header rejected (401)
   - [ ] Missing X-Goog-Resource-State header rejected (401)
   - [ ] Invalid token rejected (401)
   - [ ] Malformed expiration timestamp handled gracefully
   - [ ] Channel ID format validation (user_{id}_calendar_{cal})
   - [ ] User ID extracted from channel ID correctly

2. **II-Agent Webhook** (10 tests needed)
   - [ ] Invalid Ed25519 signature rejected (401)
   - [ ] Invalid HMAC signature rejected (401)
   - [ ] Missing X-II-Agent-Signature header rejected (401)
   - [ ] Missing X-II-Agent-Timestamp header rejected (401)
   - [ ] Expired timestamp rejected (> 5 min old) (401)
   - [ ] Replay attack prevented (same timestamp reused)
   - [ ] Malformed signature base64 handled gracefully
   - [ ] Signature type validation (ed25519 vs hmac-sha256)
   - [ ] Fallback to HMAC when Ed25519 unavailable
   - [ ] JSON body parsing errors handled (400)

### 3.2 Rate Limiting (Priority: CRITICAL)

**Current Coverage:** 0% (test exists but skipped)

**Missing Tests:**

1. **Authentication Endpoints** (3 tests needed)
   - [ ] Login rate limit enforced (5/15min per IP)
   - [ ] Register rate limit enforced (10/hour per IP)
   - [ ] Token refresh rate limit enforced (20/hour per user)

2. **Calendar/Webhook Endpoints** (2 tests needed)
   - [ ] Webhook rate limit enforced (100/min per channel)
   - [ ] Manual sync rate limit enforced (10/hour per user)

3. **AI Endpoints** (3 tests needed)
   - [ ] AI orchestrate rate limit enforced (50/hour per user)
   - [ ] File search rate limit enforced (100/hour per user)
   - [ ] Token budget enforced (5k tokens per request)

### 3.3 Permission Boundaries (Priority: HIGH)

**Current Coverage:** 60% (some tests exist)

**Missing Tests:**

1. **Calendar User Isolation** (3 tests needed)
   - [ ] User A cannot access User B's calendar events
   - [ ] User A cannot sync to User B's calendar
   - [ ] Webhook with User A's channel cannot modify User B's data

2. **Agent Session Isolation** (3 tests needed)
   - [ ] User A cannot access User B's agent sessions
   - [ ] User A cannot execute tools in User B's session
   - [ ] Agent results not leaked between users

3. **Feature Toggle Isolation** (2 tests needed)
   - [ ] User A cannot see User B's feature toggles
   - [ ] User A cannot modify User B's feature toggles

---

## 4. Integration Test Gaps

### 4.1 Calendar Integration (Priority: CRITICAL)

**File to Create:** `tests/integration/test_google_calendar_integration.py`

**Test Scenarios:**

1. **OAuth Flow** (5 tests)
   - [ ] Complete OAuth flow end-to-end
   - [ ] Token storage and retrieval
   - [ ] Token refresh on expiration
   - [ ] OAuth error handling
   - [ ] Multiple calendar selection

2. **Sync Functionality** (6 tests)
   - [ ] Sync from Google creates Focus events
   - [ ] Sync to Google creates calendar events
   - [ ] Bidirectional sync consistency
   - [ ] Sync with date range filtering
   - [ ] Sync performance (<10s for 50 events)
   - [ ] Sync with large datasets (1000+ events)

3. **Webhook Integration** (4 tests)
   - [ ] Webhook triggers sync automatically
   - [ ] Webhook delivery tracked
   - [ ] Webhook channel management
   - [ ] Webhook error recovery

### 4.2 II-Agent Integration (Priority: CRITICAL)

**File to Create:** `tests/integration/test_ii_agent_integration.py`

**Test Scenarios:**

1. **Session Management** (5 tests)
   - [ ] Create session with user authentication
   - [ ] Session persists across requests
   - [ ] Session cleanup on disconnect
   - [ ] Multiple concurrent sessions per user
   - [ ] Session timeout after inactivity

2. **Tool Execution** (6 tests)
   - [ ] Markdown converter tool execution
   - [ ] Static deploy tool execution
   - [ ] File tool execution with user isolation
   - [ ] Tool execution authorization
   - [ ] Tool execution error handling
   - [ ] Tool execution telemetry

3. **WebSocket Communication** (4 tests)
   - [ ] WebSocket connection with authentication
   - [ ] Message streaming bidirectional
   - [ ] WebSocket disconnect handling
   - [ ] WebSocket reconnection

### 4.3 Gemini File Search Integration (Priority: HIGH)

**File to Create:** `tests/integration/test_gemini_file_search.py`

**Test Scenarios:**

1. **File Search** (4 tests)
   - [ ] Gemini search with API key
   - [ ] SQL fallback when Gemini disabled
   - [ ] Search result relevance
   - [ ] Search performance (<2s)

2. **BYOK Integration** (2 tests)
   - [ ] BYOK user search uses own key
   - [ ] BYOK user not charged

---

## 5. E2E Test Gaps

### 5.1 Complete User Journeys (Priority: HIGH)

**File to Create:** `tests/e2e/test_user_journeys_e2e.py`

**Test Scenarios:**

1. **Solo Developer Journey** (1 end-to-end test)
   - [ ] Onboarding → Enable all AI → Voice command → Agent execution → Deploy → Verify URL

2. **Freelancer Journey** (1 end-to-end test)
   - [ ] Onboarding → Disable all AI → File search (SQL fallback) → Verify no external calls

3. **Operations Lead Journey** (1 end-to-end test)
   - [ ] Onboarding → OAuth → Sync events → Webhook notification → Conflict resolution

4. **Offline Analyst Journey** (1 end-to-end test)
   - [ ] Onboarding → Start agent → Network disconnect → Offline handling → Reconnect → Resume

### 5.2 Cross-Feature Integration (Priority: MEDIUM)

**Test Scenarios:**

1. **Calendar + AI** (2 tests)
   - [ ] AI generates events, syncs to calendar
   - [ ] Calendar events trigger AI task suggestions

2. **Voice + Agent + Deploy** (1 test)
   - [ ] Voice → Agent → Deploy full workflow

3. **BYOK + All Features** (1 test)
   - [ ] BYOK user with all features enabled

---

## 6. Performance Test Gaps

### 6.1 Load Testing (Priority: MEDIUM)

**File:** `tests/performance/test_load.py` (exists but expand)

**Missing Scenarios:**

1. **Calendar Sync Performance** (3 tests)
   - [ ] Sync 100 events (<10s)
   - [ ] Sync 1000 events (<60s)
   - [ ] Concurrent syncs (10 users)

2. **AI Endpoint Performance** (3 tests)
   - [ ] AI orchestrate response time (<5s)
   - [ ] File search response time (<2s)
   - [ ] Agent session creation (<1s)

3. **Dashboard Load** (2 tests)
   - [ ] Dashboard page load (<2s)
   - [ ] Dashboard with 100+ tasks (<3s)

---

## 7. Prioritized Test Scenarios by Risk

### Critical Risk (Must Test)

1. **Webhook endpoint 404** (Operations Lead persona broken)
2. **Webhook security verification** (Security vulnerability)
3. **Rate limiting missing** (DoS vulnerability)
4. **II-Agent session creation** (Solo Developer persona broken)
5. **Calendar sync integration** (Operations Lead persona incomplete)
6. **Offline detection** (Offline Analyst persona broken)

### High Risk (Should Test)

7. **Calendar user isolation**
8. **Agent session isolation**
9. **OAuth token refresh**
10. **WebSocket disconnect handling**
11. **Conflict resolution E2E**
12. **Voice-to-agent workflow**

### Medium Risk (Nice to Test)

13. **BYOK messaging visibility**
14. **Network call verification (no AI)**
15. **Agent tool execution**
16. **Deploy tool success/failure**
17. **Calendar sync performance**
18. **Dashboard load performance**

### Low Risk (Future)

19. **Security headers**
20. **Weak password rejection**
21. **Performance under load**
22. **Mobile PWA support**

---

## 8. Test File Creation Plan

### Week 1 (Critical)

1. **tests/unit/test_webhook_security.py**
   - 18 tests (Google + II-Agent webhook verification)
   - Target: 80% coverage of webhook_security.py

2. **tests/integration/test_rate_limiting.py**
   - 8 tests (auth, calendar, AI endpoints)
   - Implement rate limiting middleware first

3. **tests/integration/test_google_calendar_integration.py**
   - 15 tests (OAuth, sync, webhooks)
   - Fix webhook endpoint 404 first

### Week 2 (High Priority)

4. **tests/integration/test_ii_agent_integration.py**
   - 15 tests (sessions, tools, WebSocket)
   - Core for Solo Developer persona

5. **tests/e2e/test_calendar_security_e2e.py**
   - 8 tests (user isolation, webhook validation)
   - Core for Operations Lead persona

6. **tests/e2e/test_offline_resilience_e2e.py**
   - 10 tests (offline detection, reconnection)
   - Core for Offline Analyst persona

### Week 3 (Medium Priority)

7. **tests/integration/test_gemini_file_search.py**
   - 6 tests (search, fallback, BYOK)
   - Core for Freelancer persona validation

8. **tests/e2e/test_user_journeys_e2e.py**
   - 4 tests (one per persona)
   - Complete user journey validation

9. **tests/integration/test_agent_session_security.py**
   - 6 tests (session isolation, authorization)
   - Security validation

### Week 4 (Polish)

10. **tests/performance/test_calendar_performance.py**
    - 6 tests (sync latency, load)
    - Meet <10s sync target

11. **tests/performance/test_dashboard_performance.py**
    - 4 tests (page load, rendering)
    - Meet <2s load target

12. **Raise coverage threshold:** 50% → 60% → 70% → 80%

---

## 9. Automated Test Scenarios from Manual Simulations

**When persona scorecards are available**, extract test scenarios from:

### From Solo Developer Scorecard:
- Onboarding time (<3 min)
- AI feature enablement
- Voice-to-agent workflow
- Deploy tool success
- Token usage tracking

### From Freelancer Scorecard:
- Onboarding time (<3 min)
- AI feature disablement
- SQL fallback verification
- No external API calls
- BYOK messaging visibility

### From Operations Lead Scorecard:
- Onboarding time (<3 min)
- OAuth flow time (<30s)
- Sync latency (<10s)
- Webhook delivery time
- Conflict resolution accuracy

### From Offline Analyst Scorecard:
- Onboarding time (<3 min)
- Offline detection time (<5s)
- Reconnection time (<5s)
- Data integrity verification
- Error message clarity

---

## 10. Coverage Roadmap

### Current: 50%

**Breakdown:**
- Models: 94-100% (maintain)
- Onboarding: 95%+ (maintain)
- Events: 60% (raise to 80%)
- Calendar: 40% (raise to 80%)
- AI: 26-44% (raise to 80%)
- Services: 10-30% (raise to 80%)

### Week 2: 60% Target

**Focus:**
- Webhook security: 0% → 80% (+3%)
- Calendar integration: 40% → 70% (+5%)
- Agent sessions: 0% → 60% (+4%)
- AI routers: 30% → 50% (+3%)

### Week 4: 70% Target

**Focus:**
- Calendar integration: 70% → 80% (+2%)
- Agent sessions: 60% → 80% (+3%)
- Services layer: 20% → 60% (+8%)
- AI routers: 50% → 70% (+3%)

### Week 6: 80% Target (GOAL)

**Focus:**
- Services layer: 60% → 80% (+3%)
- AI routers: 70% → 80% (+2%)
- E2E coverage: 50% → 80% (+5%)
- Performance tests: new (+1%)

---

## 11. Recommendations

### Immediate (This Week)

1. **Fix webhook endpoint 404** - Blocking Operations Lead persona
2. **Create webhook security tests** - Critical security gap
3. **Implement rate limiting** - Critical security gap
4. **Create II-Agent integration tests** - Blocking Solo Developer persona

### Short-Term (Next 2 Weeks)

5. **Create calendar integration tests** - Complete Operations Lead persona
6. **Create offline resilience tests** - Complete Offline Analyst persona
7. **Add security isolation tests** - Validate user boundaries
8. **Add BYOK/privacy tests** - Complete Freelancer persona

### Medium-Term (Next Month)

9. **Performance benchmarking** - Meet latency targets
10. **E2E user journey tests** - Validate complete flows
11. **Security audit** - Professional penetration testing
12. **Coverage to 80%** - Quality gate completion

---

## 12. Metrics & Tracking

### Test Creation Metrics

| Week | New Tests | Coverage | Status |
|------|-----------|----------|--------|
| Baseline | 100+ | 50% | ✅ Complete |
| Week 1 | 40+ | 60% | 🎯 Target |
| Week 2 | 30+ | 70% | 🎯 Target |
| Week 3 | 20+ | 80% | 🎯 Target |

### Test Execution Metrics

| Metric | Target | Track |
|--------|--------|-------|
| Unit test time | <30s | ✅ Currently 30s |
| Integration test time | <2min | 🎯 TBD |
| E2E test time | <5min | 🎯 TBD |
| Total test time | <10min | 🎯 TBD |

---

## 13. Conclusion

**Summary:**
- **47 priority test scenarios identified** across security, integration, and E2E
- **12 new test files needed** to close coverage gap (50% → 80%)
- **Critical gaps block 3 of 4 personas:** Solo Developer, Operations Lead, Offline Analyst
- **Security gaps pose risk:** Webhook verification (0%), rate limiting (0%)

**Next Steps:**
1. Wait for Testing Agent persona simulations
2. Extract additional test scenarios from scorecards
3. Prioritize test creation based on persona impact
4. Create consolidated findings report with defect list

**Status:** ✅ Coverage gap analysis complete, awaiting persona scorecards for final synthesis

---

**Report Author:** Quality Lead
**Date:** 2025-11-16
**Next Update:** After persona scorecards available
