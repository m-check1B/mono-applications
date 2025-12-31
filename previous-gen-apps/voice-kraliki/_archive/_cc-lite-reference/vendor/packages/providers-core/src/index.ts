/**
 * @stack-2025/providers-core
 * 
 * Unified provider interfaces for multi-vendor support.
 * Prevents vendor lock-in and enables easy provider switching.
 */

// LLM Providers
export * from './llm';

// Telephony Providers  
export {
  BaseTelephonyClient,
  TelephonyProviderFactory
} from './telephony';

// Voice Providers (STT/TTS)
export {
  BaseSTTClient,
  BaseTTSClient,
  STTProviderFactory,
  TTSProviderFactory
} from './voice';

// Storage Providers
export * from './storage';

// Import implementations to register providers
import './implementations';

// Re-export main types for convenience
export type {
  LLMProvider,
  LLMClient,
  ModelId,
  Message as LLMMessage,
  CompletionOptions,
  CompletionResponse
} from './llm';

export type {
  TelephonyProvider,
  TelephonyClient,
  Call,
  Message as TelephonyMessage,
  RealtimeConnection
} from './telephony';

export type {
  STTProvider,
  TTSProvider,
  STTClient,
  TTSClient,
  TranscriptionResult,
  AudioConfig
} from './voice';

export type {
  StorageProvider,
  StorageClient,
  StorageObject,
  QueryOptions,
  VectorSearchOptions
} from './storage';