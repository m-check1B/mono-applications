/**
 * Unified Telephony Provider Interface
 * Supports multiple telephony providers (Twilio, Vonage, etc.)
 */

// Supported telephony providers
export type TelephonyProvider = 
  | 'twilio'
  | 'vonage'
  | 'aws-connect'
  | 'azure-communication'
  | 'plivo'
  | 'bandwidth'
  | 'signalwire';

// Call direction
export type CallDirection = 'inbound' | 'outbound';

// Call status
export type CallStatus = 
  | 'queued'
  | 'ringing'
  | 'in-progress'
  | 'completed'
  | 'failed'
  | 'busy'
  | 'no-answer';

// Common call object
export interface Call {
  id: string;
  from: string;
  to: string;
  direction: CallDirection;
  status: CallStatus;
  duration?: number;
  recordingUrl?: string;
  transcriptionUrl?: string;
  metadata?: Record<string, any>;
}

// SMS/Message object
export interface Message {
  id: string;
  from: string;
  to: string;
  body: string;
  status: 'queued' | 'sent' | 'delivered' | 'failed';
  direction: 'inbound' | 'outbound';
  mediaUrls?: string[];
  metadata?: Record<string, any>;
}

// WebRTC/Real-time connection
export interface RealtimeConnection {
  connectionId: string;
  callId: string;
  websocketUrl: string;
  token?: string;
  iceServers?: RTCIceServer[];
}

// Voice configuration
export interface VoiceConfig {
  voice?: string;
  language?: string;
  engine?: 'standard' | 'neural' | 'wavenet';
}

// Recording configuration
export interface RecordingConfig {
  enabled: boolean;
  channels?: 'mono' | 'dual';
  format?: 'mp3' | 'wav';
  transcribe?: boolean;
}

// Main telephony client interface
export interface TelephonyClient {
  provider: TelephonyProvider;
  
  // Voice calls
  makeCall(to: string, from: string, options?: {
    url?: string; // TwiML/NCCO URL
    statusCallback?: string;
    record?: RecordingConfig;
    machineDetection?: boolean;
  }): Promise<Call>;
  
  getCall(callId: string): Promise<Call>;
  
  updateCall(callId: string, options: {
    status?: 'completed';
    url?: string;
  }): Promise<Call>;
  
  // SMS/Messaging
  sendMessage(to: string, from: string, body: string, mediaUrls?: string[]): Promise<Message>;
  
  getMessage(messageId: string): Promise<Message>;
  
  // Real-time/WebRTC
  createRealtimeConnection?(callId: string): Promise<RealtimeConnection>;
  
  closeRealtimeConnection?(connectionId: string): Promise<void>;
  
  // Streaming audio (for live transcription/interaction)
  streamAudio?(callId: string, audioStream: AsyncIterable<Uint8Array>): Promise<void>;
  
  // Phone numbers
  listPhoneNumbers?(): Promise<Array<{
    phoneNumber: string;
    capabilities: {
      voice: boolean;
      sms: boolean;
      mms: boolean;
    };
  }>>;
  
  // Webhooks
  validateWebhook?(signature: string, body: string, url: string): boolean;
}

// Base implementation
export abstract class BaseTelephonyClient implements TelephonyClient {
  abstract provider: TelephonyProvider;
  
  constructor(protected config: {
    accountSid?: string;
    authToken?: string;
    apiKey?: string;
    apiSecret?: string;
    baseUrl?: string;
  }) {}
  
  abstract makeCall(to: string, from: string, options?: any): Promise<Call>;
  abstract getCall(callId: string): Promise<Call>;
  abstract updateCall(callId: string, options: any): Promise<Call>;
  abstract sendMessage(to: string, from: string, body: string, mediaUrls?: string[]): Promise<Message>;
  abstract getMessage(messageId: string): Promise<Message>;
}

// Factory for creating clients
export class TelephonyProviderFactory {
  private static providers = new Map<TelephonyProvider, typeof BaseTelephonyClient>();
  
  static register(provider: TelephonyProvider, clientClass: typeof BaseTelephonyClient) {
    this.providers.set(provider, clientClass);
  }
  
  static create(provider: TelephonyProvider, config: any): TelephonyClient {
    const ClientClass = this.providers.get(provider);
    if (!ClientClass) {
      throw new Error(`Provider ${provider} not registered`);
    }
    return new (ClientClass as any)(config);
  }
}

// RTCIceServer for WebRTC
interface RTCIceServer {
  urls: string | string[];
  username?: string;
  credential?: string;
}