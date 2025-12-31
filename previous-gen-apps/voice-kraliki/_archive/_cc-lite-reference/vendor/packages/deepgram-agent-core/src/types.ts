/**
 * @stack-2025/deepgram-agent-core - Types
 * TypeScript definitions for Deepgram Voice Agent API
 */

import { z } from 'zod';

// Provider Types
export type LLMProvider = 'openai' | 'anthropic' | 'deepgram' | 'openrouter';

// Voice Agent Configuration Schemas
export const VoiceConfigSchema = z.object({
  model: z.string().default('aura-asteria-en'),
  language: z.string().default('en'),
  smart_format: z.boolean().default(true),
  encoding: z.enum(['linear16', 'mulaw', 'alaw']).default('linear16'),
  sample_rate: z.number().default(16000),
  channels: z.number().default(1),
  container: z.enum(['wav', 'ogg', 'mp3']).optional(),
});

export const LLMConfigSchema = z.object({
  provider: z.enum(['openai', 'anthropic', 'deepgram', 'openrouter']),
  model: z.string(),
  max_tokens: z.number().default(1000),
  temperature: z.number().min(0).max(2).default(0.7),
  system_prompt: z.string().optional(),
  functions: z.array(z.any()).optional(),
  api_key: z.string().optional(),
  base_url: z.string().url().optional(),
  headers: z.record(z.string()).optional(),
});

export const AgentConfigSchema = z.object({
  listen: VoiceConfigSchema,
  think: LLMConfigSchema,
  speak: VoiceConfigSchema,
});

// Inferred Types
export type VoiceConfig = z.infer<typeof VoiceConfigSchema>;
export type LLMConfig = z.infer<typeof LLMConfigSchema>;
export type AgentConfig = z.infer<typeof AgentConfigSchema>;

// Event Types
export interface AgentEvent {
  type: string;
  timestamp: number;
  data?: any;
}

export interface UserStartedSpeakingEvent extends AgentEvent {
  type: 'UserStartedSpeaking';
}

export interface UserStoppedSpeakingEvent extends AgentEvent {
  type: 'UserStoppedSpeaking';
}

export interface SpeechStartedEvent extends AgentEvent {
  type: 'SpeechStarted';
  data: {
    timestamp: string;
  };
}

export interface UtteranceEndEvent extends AgentEvent {
  type: 'UtteranceEnd';
  data: {
    channel: number;
    alternatives: Array<{
      transcript: string;
      confidence: number;
      words: Array<{
        word: string;
        start: number;
        end: number;
        confidence: number;
      }>;
    }>;
  };
}

export interface AgentThinkingEvent extends AgentEvent {
  type: 'AgentThinking';
}

export interface AgentSpeakingEvent extends AgentEvent {
  type: 'AgentSpeaking';
}

export interface ConversationStartedEvent extends AgentEvent {
  type: 'ConversationStarted';
  data: {
    conversation_id: string;
  };
}

export interface FunctionCallEvent extends AgentEvent {
  type: 'FunctionCall';
  data: {
    function_name: string;
    parameters: Record<string, any>;
    call_id: string;
  };
}

export interface ErrorEvent extends AgentEvent {
  type: 'Error';
  data: {
    error: string;
    description?: string;
  };
}

export interface WarningEvent extends AgentEvent {
  type: 'Warning';
  data: {
    warning: string;
    description?: string;
  };
}

export interface MetadataEvent extends AgentEvent {
  type: 'Metadata';
  data: {
    request_id: string;
    sha256: string;
    created: string;
    model_info: {
      name: string;
      version: string;
      architecture: string;
      languages: string[];
    };
  };
}

// Union type for all events
export type VoiceAgentEvent = 
  | UserStartedSpeakingEvent
  | UserStoppedSpeakingEvent
  | SpeechStartedEvent
  | UtteranceEndEvent
  | AgentThinkingEvent
  | AgentSpeakingEvent
  | ConversationStartedEvent
  | FunctionCallEvent
  | ErrorEvent
  | WarningEvent
  | MetadataEvent;

// Connection States
export enum ConnectionState {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  FAILED = 'failed'
}

// Conversation Context
export interface ConversationContext {
  conversation_id: string;
  messages: Array<{
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: number;
  }>;
  functions_called: Array<{
    function_name: string;
    parameters: Record<string, any>;
    result?: any;
    timestamp: number;
  }>;
  metadata: {
    started_at: number;
    last_activity: number;
    total_turns: number;
  };
}

// Function Definition
export interface FunctionDefinition {
  name: string;
  description: string;
  parameters: {
    type: 'object';
    properties: Record<string, {
      type: string;
      description?: string;
      enum?: string[];
    }>;
    required?: string[];
  };
}

// Keep-alive Configuration
export interface KeepAliveConfig {
  enabled: boolean;
  interval: number; // milliseconds
  timeout: number; // milliseconds
  max_retries: number;
}

// Voice Agent Options
export interface VoiceAgentOptions {
  api_key: string;
  url?: string; // Custom WebSocket URL
  keep_alive?: KeepAliveConfig;
  auto_reconnect?: boolean;
  max_reconnect_attempts?: number;
  reconnect_interval?: number;
  conversation_context?: boolean; // Whether to maintain conversation history
}

// Provider-specific LLM Configurations
export interface OpenAIConfig extends Omit<LLMConfig, 'provider'> {
  provider: 'openai';
  model: 'gpt-4' | 'gpt-4-turbo' | 'gpt-3.5-turbo' | string;
  api_key?: string;
}

export interface AnthropicConfig extends Omit<LLMConfig, 'provider'> {
  provider: 'anthropic';
  model: 'claude-3-5-sonnet-20241022' | 'claude-3-haiku-20240307' | string;
  api_key?: string;
}

export interface DeepgramLLMConfig extends Omit<LLMConfig, 'provider'> {
  provider: 'deepgram';
  model: string;
}

export interface OpenRouterConfig extends Omit<LLMConfig, 'provider'> {
  provider: 'openrouter';
  model: string;
  api_key: string;
  base_url?: string;
  headers?: Record<string, string>;
}

export type ProviderLLMConfig = OpenAIConfig | AnthropicConfig | DeepgramLLMConfig | OpenRouterConfig;

// Audio Data Types
export interface AudioChunk {
  data: Buffer;
  timestamp: number;
  sample_rate: number;
  channels: number;
  encoding: string;
}

// Event Handler Types
export type EventHandler<T extends VoiceAgentEvent = VoiceAgentEvent> = (event: T) => void | Promise<void>;
export type FunctionCallHandler = (call: FunctionCallEvent['data']) => Promise<any>;

// Error Types
export class VoiceAgentError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'VoiceAgentError';
  }
}

export class ConnectionError extends VoiceAgentError {
  constructor(message: string, details?: any) {
    super(message, 'CONNECTION_ERROR', details);
    this.name = 'ConnectionError';
  }
}

export class ConfigurationError extends VoiceAgentError {
  constructor(message: string, details?: any) {
    super(message, 'CONFIGURATION_ERROR', details);
    this.name = 'ConfigurationError';
  }
}
