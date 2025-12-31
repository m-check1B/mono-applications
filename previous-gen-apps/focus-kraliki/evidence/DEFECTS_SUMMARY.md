# Defects Summary - Testing Agent 2

**Date**: 2025-11-16
**Personas Tested**: Operations Lead, Offline-First Analyst
**Total Defects**: 7

---

## Critical (1)

### CRIT-001: Google OAuth Not Configured
- **Component**: Calendar Sync / OAuth
- **Endpoint**: `POST /calendar-sync/oauth/init`
- **Error**: 503 Service Unavailable - "Google OAuth not configured"
- **Impact**: Blocks all calendar sync testing for Operations Lead persona
- **Root Cause**: Missing `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `/backend/.env`
- **Evidence**: `/evidence/logs/operations-lead_http.jsonl`
- **Repro Steps**:
  1. Authenticate as any user
  2. POST to `/calendar-sync/oauth/init` with `{"redirect_uri": "http://localhost:5173/calendar/callback"}`
  3. Observe 503 error
- **Recommendation**:
  - **Option A**: Add Google OAuth test credentials to backend/.env
  - **Option B**: Create OAuth mock for automated testing
  - **Option C**: Document manual OAuth setup for calendar testing

---

## High (3)

### HIGH-001: Onboarding Flow Incomplete - Missing Step 3
- **Component**: Onboarding API
- **Impact**: Cannot complete onboarding for any persona via API
- **Root Cause**: 4-step flow not documented, step 3 (`/onboarding/feature-toggles`) missing from test
- **Evidence**: Onboarding complete returns "Please complete all onboarding steps first"
- **Required Sequence**:
  1. ✅ `POST /onboarding/select-persona` {"personaId": "freelancer"}
  2. ✅ `POST /onboarding/privacy-preferences` {"geminiFileSearchEnabled": false, ...}
  3. ❌ `POST /onboarding/feature-toggles` (NOT CALLED - undocumented)
  4. ❌ `POST /onboarding/complete` {} (FAILS - missing step 3)
- **Repro Steps**:
  1. Select persona (step 1) - succeeds
  2. Set privacy preferences (step 2) - succeeds
  3. Attempt to complete onboarding - fails with "Please complete all onboarding steps first"
  4. Missing: POST to `/onboarding/feature-toggles`
- **Recommendation**:
  - Update API documentation to clearly list all 4 required steps in sequence
  - Or add validation error message: "Missing step 3: feature-toggles configuration"
  - Or allow skipping feature-toggles with defaults applied

### HIGH-002: Operations Lead Persona Not Available
- **Component**: Onboarding / Personas
- **Impact**: Handoff document references non-existent persona
- **Available Personas**:
  - ✅ `solo-developer`
  - ✅ `freelancer`
  - ✅ `explorer`
  - ❌ `operations-lead` (referenced in handoff doc)
- **Workaround**: Used `freelancer` persona (has `calendarIntegration: true` feature)
- **Evidence**: `GET /onboarding/personas` returns 3 personas (no operations-lead)
- **Recommendation**:
  - **Option A**: Add "operations-lead" persona to backend with calendar-focused defaults
  - **Option B**: Update handoff document to specify "freelancer" for calendar testing
  - **Option C**: Alias "operations-lead" to "freelancer" in persona selection

### HIGH-003: Offline Testing Requires Browser Environment
- **Component**: Testing Tooling / Offline-First Analyst Persona
- **Impact**: Cannot test core offline requirements (disconnect detection, graceful degradation, recovery) via CLI
- **Black-Box CLI Limitations**:
  - ❌ Cannot simulate browser offline mode (requires browser APIs)
  - ❌ Cannot test WebSocket connections (requires WebSocket client or browser)
  - ❌ Cannot validate UI offline indicators (requires browser rendering)
  - ❌ Cannot check LocalStorage/IndexedDB (browser-only storage)
  - ❌ Cannot monitor network state transitions (browser Network API)
- **Evidence**: Documented in `/evidence/scorecards/offline-analyst_scorecard.md`
- **Recommendation**:
  - **Option A**: Create Playwright/Selenium E2E test for offline scenarios
  - **Option B**: Provide manual testing checklist for QA team
  - **Option C**: Use Browser MCP tool for interactive offline testing
  - **Example Playwright Test**: See offline-analyst_scorecard.md for code example

---

## Medium (2)

### MED-001: Calendar Sync Error Message Unclear
- **Component**: Calendar Sync Error Handling
- **Endpoint**: `POST /calendar-sync/sync`
- **Current Error**: "Calendar sync not enabled or not connected" (400)
- **Issue**: Doesn't distinguish between:
  1. OAuth not configured (backend config issue)
  2. User hasn't connected calendar yet (OAuth not completed)
  3. Sync disabled in user settings (feature toggle)
- **Impact**: User/tester unclear what action to take
- **Recommendation**: Separate error messages:
  - 503 "Google OAuth not configured" (backend config missing)
  - 400 "Calendar not connected. Please complete OAuth flow first"
  - 400 "Calendar sync disabled in settings"

### MED-002: II-Agent Session Endpoint Unclear
- **Component**: II-Agent Sessions
- **Endpoint**: `GET /agent/sessions`
- **Observation**: Returns empty array `[]` even with II-Agent enabled in preferences
- **Impact**: Cannot start II-Agent session to test offline behavior
- **Possible Causes**:
  - Sessions created via WebSocket handshake, not HTTP endpoint
  - Sessions only created via frontend, not directly via API
  - Endpoint lists sessions but requires active WebSocket connection first
- **Evidence**: `/evidence/logs/offline-analyst_http.jsonl`
- **Recommendation**:
  - Document II-Agent session lifecycle (HTTP vs WebSocket)
  - Provide API example for creating agent session
  - Or document as "frontend-only" feature

---

## Low (0)
None identified

---

## Defects by Component

### Onboarding (2)
- HIGH-001: Onboarding flow incomplete (missing step 3)
- HIGH-002: Operations Lead persona not available

### Calendar Sync (2)
- CRIT-001: Google OAuth not configured
- MED-001: Calendar sync error messages unclear

### II-Agent (1)
- MED-002: II-Agent session endpoint unclear

### Testing Tooling (2)
- HIGH-003: Offline testing requires browser environment

---

## Priority Fix Order

**Week 1 (P0 - Blockers):**
1. HIGH-001: Document complete onboarding flow (API docs update - 1 hour)
2. CRIT-001: Configure Google OAuth OR document workaround (environment setup - 2 hours)

**Week 2 (P1 - Important):**
3. HIGH-002: Add Operations Lead persona OR update handoff doc (backend change or doc update - 1 hour)
4. HIGH-003: Create browser E2E test for offline scenarios (Playwright test - 4 hours)

**Week 3 (P2 - Improvements):**
5. MED-001: Improve calendar error messages (backend change - 1 hour)
6. MED-002: Document II-Agent session creation (documentation - 30 min)

---

## Test Coverage Gaps (11 Total)

See `/evidence/TESTING_AGENT_2_SUMMARY.md` for full list, including:
- Complete E2E onboarding flow (4 steps)
- Google Calendar OAuth with test credentials
- Offline mode browser E2E testing
- WebSocket reconnection logic
- Calendar bidirectional sync
- Webhook delivery and signature validation
- Conflict resolution scenarios
- And 4 more...

---

## Evidence Locations

All evidence files are in: `/home/adminmatej/github/applications/focus-kraliki/evidence/`

- **Scorecards**: `scorecards/operations-lead_scorecard.md`, `scorecards/offline-analyst_scorecard.md`
- **HTTP Logs**: `logs/operations-lead_http.jsonl`, `logs/offline-analyst_http.jsonl`
- **Calendar Logs**: `logs/operations-lead_calendar_sync.log`
- **Metrics**: `metrics/timing_summary.csv`, `metrics/network_summary.json`
- **Full Summary**: `TESTING_AGENT_2_SUMMARY.md`
