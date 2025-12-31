import { d as apiPost } from "./auth2.js";
function bootstrapSession(request) {
  return apiPost("/api/v1/sessions/bootstrap", request);
}
function endSession(sessionId) {
  return apiPost(`/api/v1/sessions/${sessionId}/end`, {});
}
const LEGACY_ENDPOINTS = {
  // Map legacy endpoints to new versioned endpoints
  "/make-call": "/api/telephony/call",
  "/update-session-config": "/api/v1/sessions/{sessionId}/config",
  "/call-results/{callSid}": "/api/telephony/call/{callId}",
  "/campaigns": "/api/v1/campaigns",
  "/companies": "/api/v1/companies",
  "/available-voices": "/api/v1/providers/voices",
  "/available-models": "/api/v1/providers/models",
  "/api/voice-config": "/api/v1/providers/voice-config"
};
function migrateEndpoint(legacyEndpoint, params) {
  let migrated = LEGACY_ENDPOINTS[legacyEndpoint] || legacyEndpoint;
  return migrated;
}
export {
  bootstrapSession as b,
  endSession as e,
  migrateEndpoint as m
};
