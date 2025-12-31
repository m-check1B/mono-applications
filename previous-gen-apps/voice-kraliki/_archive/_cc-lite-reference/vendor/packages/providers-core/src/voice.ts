/**
 * Unified Voice Provider Interface
 * Supports STT (Speech-to-Text) and TTS (Text-to-Speech) providers
 */

// STT Providers
export type STTProvider = 
  | 'openai-whisper'
  | 'google-speech'
  | 'aws-transcribe'
  | 'azure-speech'
  | 'deepgram'
  | 'assemblyai'
  | 'rev.ai';

// TTS Providers  
export type TTSProvider =
  | 'openai-tts'
  | 'google-tts'
  | 'aws-polly'
  | 'azure-speech'
  | 'elevenlabs'
  | 'play.ht'
  | 'murf.ai';

// Audio formats
export type AudioFormat = 'pcm' | 'mp3' | 'wav' | 'opus' | 'ogg' | 'flac';

// Audio configuration
export interface AudioConfig {
  sampleRate?: number; // e.g., 16000, 44100
  channels?: number; // 1 (mono) or 2 (stereo)
  bitDepth?: number; // 8, 16, 24, 32
  format?: AudioFormat;
}

// STT Options
export interface TranscriptionOptions {
  language?: string; // ISO 639-1 code
  model?: string; // Provider-specific model
  punctuate?: boolean;
  profanityFilter?: boolean;
  enableSpeakerDiarization?: boolean;
  maxSpeakers?: number;
  keywords?: string[]; // Boost certain words
  interim?: boolean; // For streaming - return partial results
}

// TTS Options
export interface SynthesisOptions {
  voice?: string; // Provider-specific voice ID
  language?: string; // ISO 639-1 code
  speed?: number; // 0.5 to 2.0
  pitch?: number; // -20 to 20
  volume?: number; // 0 to 100
  emotion?: string; // Provider-specific emotions
  style?: string; // Provider-specific styles
}

// Transcription result
export interface TranscriptionResult {
  text: string;
  confidence?: number;
  words?: Array<{
    word: string;
    start: number;
    end: number;
    confidence?: number;
  }>;
  speakers?: Array<{
    speaker: string;
    segments: Array<{
      text: string;
      start: number;
      end: number;
    }>;
  }>;
}

// STT Client interface
export interface STTClient {
  provider: STTProvider;
  
  // Single audio transcription
  transcribe(
    audio: Uint8Array | ArrayBuffer,
    options?: TranscriptionOptions
  ): Promise<TranscriptionResult>;
  
  // Streaming transcription
  transcribeStream(
    audioStream: AsyncIterable<Uint8Array>,
    options?: TranscriptionOptions
  ): AsyncIterable<TranscriptionResult>;
  
  // Get supported languages
  getSupportedLanguages(): Promise<string[]>;
  
  // Get available models
  getModels?(): Promise<string[]>;
}

// TTS Client interface
export interface TTSClient {
  provider: TTSProvider;
  
  // Single text synthesis
  synthesize(
    text: string,
    options?: SynthesisOptions
  ): Promise<Uint8Array>;
  
  // Streaming synthesis
  synthesizeStream(
    text: string,
    options?: SynthesisOptions
  ): AsyncIterable<Uint8Array>;
  
  // Get available voices
  getVoices(language?: string): Promise<Array<{
    id: string;
    name: string;
    language: string;
    gender?: 'male' | 'female' | 'neutral';
    styles?: string[];
  }>>;
  
  // Get supported languages
  getSupportedLanguages(): Promise<string[]>;
}

// Base STT implementation
export abstract class BaseSTTClient implements STTClient {
  abstract provider: STTProvider;
  
  constructor(protected config: {
    apiKey?: string;
    apiSecret?: string;
    baseUrl?: string;
    region?: string;
    audioConfig?: AudioConfig;
  }) {}
  
  abstract transcribe(
    audio: Uint8Array | ArrayBuffer,
    options?: TranscriptionOptions
  ): Promise<TranscriptionResult>;
  
  abstract transcribeStream(
    audioStream: AsyncIterable<Uint8Array>,
    options?: TranscriptionOptions
  ): AsyncIterable<TranscriptionResult>;
  
  abstract getSupportedLanguages(): Promise<string[]>;
}

// Base TTS implementation
export abstract class BaseTTSClient implements TTSClient {
  abstract provider: TTSProvider;
  
  constructor(protected config: {
    apiKey?: string;
    apiSecret?: string;
    baseUrl?: string;
    region?: string;
    audioConfig?: AudioConfig;
  }) {}
  
  abstract synthesize(
    text: string,
    options?: SynthesisOptions
  ): Promise<Uint8Array>;
  
  abstract synthesizeStream(
    text: string,
    options?: SynthesisOptions
  ): AsyncIterable<Uint8Array>;
  
  abstract getVoices(language?: string): Promise<any[]>;
  
  abstract getSupportedLanguages(): Promise<string[]>;
}

// Factory for STT clients
export class STTProviderFactory {
  private static providers = new Map<STTProvider, typeof BaseSTTClient>();
  
  static register(provider: STTProvider, clientClass: typeof BaseSTTClient) {
    this.providers.set(provider, clientClass);
  }
  
  static create(provider: STTProvider, config: any): STTClient {
    const ClientClass = this.providers.get(provider);
    if (!ClientClass) {
      throw new Error(`STT Provider ${provider} not registered`);
    }
    return new (ClientClass as any)(config);
  }
}

// Factory for TTS clients
export class TTSProviderFactory {
  private static providers = new Map<TTSProvider, typeof BaseTTSClient>();
  
  static register(provider: TTSProvider, clientClass: typeof BaseTTSClient) {
    this.providers.set(provider, clientClass);
  }
  
  static create(provider: TTSProvider, config: any): TTSClient {
    const ClientClass = this.providers.get(provider);
    if (!ClientClass) {
      throw new Error(`TTS Provider ${provider} not registered`);
    }
    return new (ClientClass as any)(config);
  }
}