/** Session API service with versioned endpoints.
 * 
 * This service provides the correct API endpoints for session management
 * following the Milestone 1 contract alignment requirements.
 */

import { apiGet, apiPost, apiDelete } from '$lib/utils/api';

export interface SessionCreateRequest {
  provider_type?: 'openai' | 'gemini' | 'deepgram' | 'deepgram_nova3';
  provider?: 'openai' | 'gemini' | 'deepgram' | 'deepgram_nova3';
  provider_model?: string;
  strategy?: 'direct' | 'fallback' | 'loadbalance';
  telephony_provider?: 'twilio' | 'telnyx';
  phone_number?: string;
  metadata?: Record<string, unknown>;
}

export interface SessionResponse {
  id: string;
  provider_type: string;
  provider_model: string;
  strategy: string;
  telephony_provider?: string;
  status: 'pending' | 'active' | 'paused' | 'completed' | 'error' | 'terminated';
  created_at: string;
  updated_at: string;
  ended_at?: string;
  metadata: Record<string, unknown>;
}

export interface SessionBootstrapResponse {
  session_id: string;
  websocket_url: string;
  provider_type: string;
  status: string;
  metadata: Record<string, unknown>;
}

export interface SessionListResponse {
  sessions: SessionResponse[];
}

export interface SessionStatsResponse {
  total_sessions: number;
  active_sessions: number;
  completed_sessions: number;
  failed_sessions: number;
  sessions_by_provider: Record<string, number>;
  sessions_by_status: Record<string, number>;
}

/** Create a new session */
export function createSession(request: SessionCreateRequest): Promise<SessionResponse> {
  return apiPost<SessionResponse>('/api/v1/sessions', request);
}

/** Bootstrap a session (returns websocket URL + session ID) */
export function bootstrapSession(request: SessionCreateRequest): Promise<SessionBootstrapResponse> {
  return apiPost<SessionBootstrapResponse>('/api/v1/sessions/bootstrap', request);
}

/** Get session details by ID */
export function getSession(sessionId: string): Promise<SessionResponse> {
  return apiGet<SessionResponse>(`/api/v1/sessions/${sessionId}`);
}

/** List all sessions, optionally filtered by status */
export function listSessions(status?: string): Promise<SessionListResponse> {
  const params = status ? `?status=${status}` : '';
  return apiGet<SessionListResponse>(`/api/v1/sessions${params}`);
}

/** Start a session */
export function startSession(sessionId: string): Promise<{ message: string }> {
  return apiPost<{ message: string }>(`/api/v1/sessions/${sessionId}/start`, {});
}

/** End a session */
export function endSession(sessionId: string): Promise<{ message: string }> {
  return apiPost<{ message: string }>(`/api/v1/sessions/${sessionId}/end`, {});
}

/** Delete a session */
export function deleteSession(sessionId: string): Promise<{ message: string }> {
  return apiDelete<{ message: string }>(`/api/v1/sessions/${sessionId}`);
}

/** Get session statistics */
export function getSessionStats(): Promise<SessionStatsResponse> {
  return apiGet<SessionStatsResponse>('/api/v1/sessions/stats');
}

/** Get WebSocket URL for a session */
export function getWebSocketUrl(sessionId: string): string {
  const baseUrl = import.meta.env.VITE_WS_URL || window.location.origin.replace('http', 'ws');
  return `${baseUrl}/ws/sessions/${sessionId}`;
}

/** Legacy endpoint mappings for backward compatibility */
export const LEGACY_ENDPOINTS = {
  // Map legacy endpoints to new versioned endpoints
  '/make-call': '/api/telephony/call',
  '/update-session-config': '/api/v1/sessions/{sessionId}/config',
  '/call-results/{callSid}': '/api/telephony/call/{callId}',
  '/campaigns': '/api/v1/campaigns',
  '/companies': '/api/v1/companies',
  '/available-voices': '/api/v1/providers/voices',
  '/available-models': '/api/v1/providers/models',
  '/api/voice-config': '/api/v1/providers/voice-config',
} as const;

/** Helper to migrate legacy endpoint calls to versioned endpoints */
export function migrateEndpoint(legacyEndpoint: string, params?: Record<string, string>): string {
  let migrated: string = LEGACY_ENDPOINTS[legacyEndpoint as keyof typeof LEGACY_ENDPOINTS] || legacyEndpoint;
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      migrated = migrated.replace(`{${key}}`, value);
    });
  }
  
  return migrated;
}
