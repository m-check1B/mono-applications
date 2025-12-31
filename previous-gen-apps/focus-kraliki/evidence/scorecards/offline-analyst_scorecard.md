# Offline-First Analyst - Simulation Scorecard

**Date**: 2025-11-16
**Simulated By**: Testing Agent 2
**Duration**: 30 minutes
**User Account**: sim.offline.analyst@example.com
**User ID**: LYfAJTVZCzo5VUdo-cL_Hg

## Journey Outcomes

| Journey | Target | Achieved | Status | Notes |
|---------|--------|----------|--------|-------|
| Onboarding | <3 min | Unable to complete | 🔴 | Missing step 3 (feature-toggles), same as Operations Lead |
| II-Agent Session Start | <5 sec | Not tested | 🟡 | No sessions endpoint available, requires frontend |
| Network Disconnect Detection | <5 sec | Not tested | 🟡 | Requires browser environment for offline simulation |
| Offline Mode Graceful Degradation | N/A | Not tested | 🟡 | Requires browser DevTools offline mode |
| Reconnection & Recovery | <5 sec | Not tested | 🟡 | Requires browser environment |

## Metrics

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Onboarding Time | <180 sec | N/A (incomplete) | 🔴 |
| Offline Detection Time | <5 sec | Not tested | 🟡 |
| Reconnection Time | <5 sec | Not tested | 🟡 |
| Data Integrity (offline/online) | 100% | Not tested | 🟡 |
| WebSocket Reconnect Attempts | >0 | Not tested | 🟡 |

## Findings

### Issues Found (3 total)

**Critical (0):**
- None

**High (1):**
- **HIGH-003**: Offline testing requires browser environment - Black-box CLI testing cannot simulate browser offline mode
  - **Evidence**: WebSocket connections, offline mode, and network state require browser APIs
  - **Impact**: Cannot validate core Offline Analyst persona requirements (offline detection, graceful degradation, recovery)
  - **Testing Gap**: This persona requires:
    1. Browser DevTools Network tab → Offline mode
    2. WebSocket connection monitoring
    3. Frontend offline state indicators (UI elements)
    4. LocalStorage/IndexedDB data persistence validation
  - **Repro Steps**: N/A - this is a tooling limitation
  - **Recommendation**: 
    - Create Playwright/Selenium E2E test for offline scenario
    - Or provide manual testing checklist for QA team
    - Or use Browser MCP tool if available for interactive testing

**Medium (2):**
- **MED-002**: II-Agent session endpoint not accessible - GET /agent/sessions returns empty array
  - **Evidence**: `/home/adminmatej/github/applications/focus-kraliki/evidence/logs/offline-analyst_http.jsonl`
  - **Impact**: Cannot start II-Agent session to test offline behavior
  - **Possible Causes**: 
    - Sessions may require WebSocket connection first (not HTTP endpoint)
    - Sessions may be created via frontend only
    - API endpoint may not list sessions (only WebSocket protocol)
  - **Recommendation**: Document II-Agent session creation flow (WebSocket handshake vs HTTP endpoint)

- **MED-003**: Onboarding flow incomplete (same as Operations Lead)
  - **Evidence**: Same as HIGH-001 in Operations Lead scorecard
  - **Impact**: Unable to complete onboarding for Offline Analyst persona
  - **Recommendation**: Add feature-toggles step to onboarding test

**Low (0):**
- None

### Positive Observations
- **Persona selection works**: Explorer persona selected successfully with II-Agent enabled
- **Privacy preferences flexible**: Can enable/disable II-Agent, Gemini independently
- **API documentation clear**: OpenAPI spec helpful for discovering endpoints
- **User isolation working**: Separate user accounts maintain separate state
- **Feature toggle persistence**: Privacy preferences saved successfully (iiAgentEnabled: true)

## Evidence Links
- **HTTP Logs**: `/home/adminmatej/github/applications/focus-kraliki/evidence/logs/offline-analyst_http.jsonl`
- **WebSocket Logs**: Not collected (requires browser environment)
- **Metrics**: `/home/adminmatej/github/applications/focus-kraliki/evidence/metrics/timing_summary.csv`
- **Test Credentials**: `/tmp/test_credentials.txt`

## Test Coverage Gaps

Based on this simulation, the following test scenarios are **completely missing** and require different testing approach:

1. **CRITICAL PRIORITY**: Offline mode detection and handling
   - **Requires**: Browser-based E2E test with DevTools offline simulation
   - **Scenario**: Start WebSocket → Enable offline mode → Verify error handling
   
2. **CRITICAL PRIORITY**: WebSocket reconnection logic
   - **Requires**: Browser-based E2E test or WebSocket client
   - **Scenario**: Disconnect → Wait → Reconnect → Verify session recovery

3. **HIGH PRIORITY**: Offline data persistence
   - **Requires**: Browser E2E test with LocalStorage/IndexedDB inspection
   - **Scenario**: Create data offline → Reconnect → Verify sync to backend

4. **HIGH PRIORITY**: Offline UI indicators
   - **Requires**: Browser E2E test with visual regression testing
   - **Scenario**: Enable offline mode → Verify offline badge/banner appears

5. **MEDIUM PRIORITY**: II-Agent offline fallback behavior
   - **Requires**: WebSocket testing with network interruption
   - **Scenario**: Start agent task → Disconnect → Verify queuing or error message

## Recommendations

### Immediate Actions (P0)
1. **Create browser-based E2E test for offline scenarios**:
   - Use Playwright or Selenium
   - Simulate offline mode via `context.setOffline(true)`
   - Test WebSocket disconnect/reconnect
   - Validate offline UI indicators

2. **Document offline testing manual checklist**:
   - If automated testing blocked, provide QA manual test script
   - Include screenshots of expected offline UI states
   - Define acceptance criteria for offline mode

3. **Clarify II-Agent session creation**:
   - Document whether sessions are HTTP or WebSocket-only
   - Provide API example for starting agent session
   - Or indicate frontend-only feature

### Future Enhancements (P1)
1. **Add offline mode indicator to API**: Backend endpoint to check if user in offline mode
2. **Implement offline queue**: Allow backend to queue requests when offline detected
3. **Service Worker for PWA**: Enhance offline capabilities with service worker caching

## Black-Box Testing Limitations

This persona simulation exposed **critical limitations of CLI-based black-box testing**:

### What CLI Testing Can Do:
- ✅ Test HTTP API endpoints (REST)
- ✅ Validate authentication and authorization
- ✅ Check API response times and errors
- ✅ Verify data persistence via API calls
- ✅ Test backend logic and business rules

### What CLI Testing Cannot Do:
- ❌ Simulate browser offline mode (requires browser APIs)
- ❌ Test WebSocket connections (requires client implementation or browser)
- ❌ Validate UI indicators (requires browser rendering)
- ❌ Check LocalStorage/IndexedDB (browser-only storage)
- ❌ Monitor network state transitions (browser Network API)

### Recommended Approach:
For **Offline-First Analyst persona**, black-box testing should be:
- **70% Browser E2E tests** (Playwright/Selenium) - offline scenarios, WebSocket, UI
- **30% API tests** (CLI/Postman) - backend logic, data persistence, error handling

## Summary

**What Worked:**
- User registration and authentication
- Persona selection (Explorer persona)
- Privacy preferences with II-Agent enabled
- API response times

**What Didn't Work:**
- Complete onboarding flow (missing step 3)
- II-Agent session creation (endpoint unclear)
- Offline behavior testing (requires browser)

**Blockers:**
- Offline testing requires browser environment (tooling limitation)
- II-Agent WebSocket testing requires different approach
- Onboarding flow incomplete (missing feature-toggles step)

**Simulated User Experience:**
Unable to simulate Offline-First Analyst persona's core requirements (offline detection, graceful degradation, recovery) due to CLI testing limitations. The backend APIs are functional, but the offline experience is entirely frontend/browser-based and cannot be validated via HTTP API calls alone.

**Verdict**: 🟡 INCOMPLETE - Backend APIs functional but core offline features untestable via CLI black-box approach

## Alternative Testing Recommendation

For future Offline Analyst persona testing:

```javascript
// Recommended Playwright test structure
test('Offline-First Analyst: Network disconnect handling', async ({ page, context }) => {
  // 1. Login and start II-Agent session
  await page.goto('http://localhost:5173/login');
  await page.fill('[name=email]', 'sim.offline.analyst@example.com');
  await page.fill('[name=password]', 'TestPass123!');
  await page.click('button[type=submit]');
  
  // 2. Navigate to Assistant and start task
  await page.goto('http://localhost:5173/assistant');
  await page.fill('[name=message]', 'Analyze my tasks');
  await page.click('button[type=submit]');
  
  // 3. Wait for WebSocket connection
  await page.waitForSelector('.agent-status:has-text("Connected")');
  
  // 4. Simulate offline mode
  const startTime = Date.now();
  await context.setOffline(true);
  
  // 5. Verify offline detection
  await page.waitForSelector('.offline-indicator', { timeout: 5000 });
  const detectionTime = Date.now() - startTime;
  expect(detectionTime).toBeLessThan(5000);
  
  // 6. Verify graceful degradation (error message or queue)
  const errorMessage = await page.textContent('.error-message');
  expect(errorMessage).toContain('offline');
  
  // 7. Reconnect
  await context.setOffline(false);
  
  // 8. Verify recovery
  await page.waitForSelector('.agent-status:has-text("Connected")');
  const reconnectTime = Date.now() - startTime;
  expect(reconnectTime).toBeLessThan(10000);
});
```

This test would provide the evidence required for Offline Analyst scorecard completion.
