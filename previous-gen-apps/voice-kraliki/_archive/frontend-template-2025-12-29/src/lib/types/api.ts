/** Shared TypeScript typings for API contracts.
 * 
 * This file contains the normalized response schemas and shared types
 * used across the frontend and backend for contract alignment.
 */

// Base API response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
}

// Session types
export interface SessionStatus {
  PENDING: 'pending';
  ACTIVE: 'active';
  COMPLETED: 'completed';
  FAILED: 'failed';
  CANCELLED: 'cancelled';
}

export type SessionStatusValue = SessionStatus[keyof SessionStatus];

export interface SessionMetadata {
  phone_number?: string;
  from_number?: string;
  call_sid?: string;
    company_id?: number;
  script_id?: number;
  campaign_id?: number;
  provider_config?: Record<string, unknown>;
  telephony_config?: Record<string, unknown>;
  [key: string]: unknown;
}

// Provider types
export interface ProviderType {
  OPENAI: 'openai';
  GEMINI: 'gemini';
  DEEPGRAM: 'deepgram';
}

export type ProviderTypeValue = ProviderType[keyof ProviderType];

export interface TelephonyProvider {
  TWILIO: 'twilio';
  TELNYX: 'telnyx';
}

export type TelephonyProviderValue = TelephonyProvider[keyof TelephonyProvider];

export interface ProviderCapabilities {
  supports_realtime: boolean;
  supports_text: boolean;
  supports_audio: boolean;
  supports_multimodal: boolean;
  supports_function_calling: boolean;
  supports_streaming: boolean;
  audio_formats: string[];
  max_session_duration?: number;
  sample_rates: number[];
  channels: number[];
}

export interface ProviderInfo {
  id: string;
  name: string;
  type: ProviderTypeValue;
  is_configured: boolean;
  capabilities: ProviderCapabilities;
  is_primary: boolean;
  models: string[];
  default_model?: string;
}

// Call types
export interface CallDirection {
  INBOUND: 'inbound';
  OUTBOUND: 'outbound';
}

export type CallDirectionValue = CallDirection[keyof CallDirection];

export interface CallStatus {
  QUEUED: 'queued';
  RINGING: 'ringing';
  IN_PROGRESS: 'in_progress';
  COMPLETED: 'completed';
  FAILED: 'failed';
  BUSY: 'busy';
  NO_ANSWER: 'no_answer';
  CANCELLED: 'cancelled';
}

export type CallStatusValue = CallStatus[keyof CallStatus];

export interface CallRecord {
  id: string;
  session_id: string;
  from_number: string;
  to_number: string;
  status: CallStatusValue;
  direction: CallDirectionValue;
  provider: TelephonyProviderValue;
  script_id?: number;
  company_id?: number;
  duration?: number;
  recording_url?: string;
  transcription?: string;
  cost?: number;
  created_at: string;
  answered_at?: string;
  ended_at?: string;
  metadata: Record<string, unknown>;
}

export interface CallRequest {
  to_number: string;
  from_number?: string;
  provider?: TelephonyProviderValue;
  script_id?: number;
  company_id?: number;
  metadata?: Record<string, unknown>;
}

export interface CallResponse {
  success: boolean;
  call_id?: string;
  status?: string;
  error?: string;
  provider: TelephonyProviderValue;
  metadata: Record<string, unknown>;
}

// Campaign types
export interface CampaignScript {
  id: number;
  name: string;
  language: string;
  description?: string;
  steps: CampaignStep[];
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CampaignStep {
  id: string;
  type: 'message' | 'question' | 'action' | 'condition';
  content: string;
  next_step_id?: string;
  conditions?: Record<string, unknown>;
  actions?: CampaignAction[];
  metadata: Record<string, unknown>;
}

export interface CampaignAction {
  type: 'send_message' | 'call_function' | 'transfer_call' | 'end_call';
  parameters: Record<string, unknown>;
  delay?: number;
}

export interface CampaignSummary {
  id: number;
  name: string;
  language?: string;
  description?: string;
  steps_count?: number;
  status: 'active' | 'inactive' | 'draft';
  created_at: string;
  updated_at: string;
}

// Company types
export interface Company {
  id: number;
  name: string;
  phone: string;
  email?: string;
  address?: string;
  status: 'active' | 'inactive';
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CompanySummary {
  id: number;
  name: string;
  phone: string;
  status?: string;
  [key: string]: unknown;
}

// Audio types
export interface AudioFormat {
  PCM16: 'pcm16';
  ULAW: 'ulaw';
  OPUS: 'opus';
  MP3: 'mp3';
}

export type AudioFormatValue = AudioFormat[keyof AudioFormat];

export interface AudioConfig {
  sample_rate: number;
  channels: number;
  format: AudioFormatValue;
  bit_rate?: number;
  frame_size?: number;
}

export interface VoiceConfig {
  voice_id: string;
  name: string;
  gender: 'male' | 'female' | 'neutral';
  language: string;
  provider: ProviderTypeValue;
  capabilities: string[];
  sample_rate?: number;
}

// WebSocket message types
export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  session_id?: string;
  metadata?: Record<string, unknown>;
}

export interface AudioMessage extends WebSocketMessage {
  type: 'audio';
  data: ArrayBuffer;
  format: AudioFormatValue;
  sample_rate: number;
  channels: number;
}

export interface TextMessage extends WebSocketMessage {
  type: 'text';
  data: string;
  role: 'user' | 'assistant' | 'system';
}

export interface TranscriptMessage extends WebSocketMessage {
  type: 'transcript';
  data: {
    text: string;
    confidence?: number;
    speaker?: 'user' | 'assistant';
    timestamp: number;
  };
}

export interface FunctionCallMessage extends WebSocketMessage {
  type: 'function_call';
  data: {
    name: string;
    arguments: Record<string, unknown>;
    call_id?: string;
  };
}

export interface FunctionResponseMessage extends WebSocketMessage {
  type: 'function_response';
  data: {
    call_id?: string;
    result: any;
    error?: string;
  };
}

// Error types
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
  request_id?: string;
}

export interface ValidationError extends ApiError {
  field: string;
  value: any;
  constraint: string;
}

// Health check types
export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  timestamp: string;
  version: string;
  uptime: number;
  checks: HealthCheck[];
}

export interface HealthCheck {
  name: string;
  status: 'pass' | 'fail' | 'warn';
  duration_ms?: number;
  message?: string;
  details?: Record<string, unknown>;
}

// Metrics types
export interface SessionMetrics {
  total_sessions: number;
  active_sessions: number;
  completed_sessions: number;
  failed_sessions: number;
  average_duration: number;
  sessions_by_provider: Record<ProviderTypeValue, number>;
  sessions_by_status: Record<SessionStatusValue, number>;
}

export interface TelephonyMetrics {
  total_calls: number;
  active_calls: number;
  completed_calls: number;
  failed_calls: number;
  average_duration: number;
  calls_by_provider: Record<TelephonyProviderValue, number>;
  calls_by_status: Record<CallStatusValue, number>;
}

// Configuration types
export interface ProviderConfig {
  provider: ProviderTypeValue;
  model: string;
  parameters: Record<string, unknown>;
  capabilities: ProviderCapabilities;
}

export interface TelephonyConfig {
  provider: TelephonyProviderValue;
  phone_numbers: string[];
  webhook_url: string;
  region?: string;
  capabilities: string[];
}

export interface SystemConfig {
  providers: ProviderConfig[];
  telephony: TelephonyConfig[];
  features: Record<string, boolean>;
  limits: {
    max_sessions: number;
    max_calls_per_minute: number;
    max_duration: number;
  };
}