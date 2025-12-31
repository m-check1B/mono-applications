import type { Readable } from 'stream';

export type E164 = `+${string}`;
export type SipUri = `sip:${string}`;
export type CallId = string;

export interface CallMetadata {
  [key: string]: string | number | boolean;
}

export interface OutboundCallInput {
  from: E164;
  to: E164;
  metadata?: CallMetadata;
}

export interface WebhookHeaders {
  [key: string]: string | string[] | undefined;
}

export interface RecordingUrlResult {
  type: 'url';
  url: string;
  /** Optional expiration metadata if URL is pre-signed */
  expiresAt?: Date;
}

export interface RecordingStreamResult {
  type: 'stream';
  stream: Readable;
  /** MIME type of the stream payload */
  contentType?: string;
  /** Suggested filename for downstream persistence */
  filename?: string;
}

export type RecordingResult = RecordingUrlResult | RecordingStreamResult;

export interface TelephonyProvider {
  /**
   * Verify webhook signature to ensure request is from the provider
   */
  verifySignature(rawBody: Buffer, headers: WebhookHeaders): boolean;
  
  /**
   * Create an outbound call
   */
  createOutboundCall(input: OutboundCallInput): Promise<CallId>;
  
  /**
   * Hangup an active call
   */
  hangup(callId: CallId): Promise<void>;
  
  /**
   * Play text-to-speech to the caller (whisper)
   */
  whisper(callId: CallId, text: string): Promise<void>;
  
  /**
   * Transfer call to another number or SIP endpoint
   */
  transfer(callId: CallId, to: E164 | SipUri): Promise<void>;
  
  /**
   * Get call recording as a stream
   */
  getRecording(callId: CallId): Promise<RecordingResult>;
}

export class NotSupportedError extends Error {
  constructor(feature: string, provider: string) {
    super(`Feature "${feature}" is not supported by ${provider} provider`);
    this.name = 'NotSupportedError';
  }
}

export class TelephonyError extends Error {
  constructor(message: string, public readonly code?: string) {
    super(message);
    this.name = 'TelephonyError';
  }
}

export interface TelephonyConfig {
  provider: 'twilio' | 'telnyx';
  region?: 'eu' | 'us';
  twilio?: {
    accountSid: string;
    authToken: string;
    region?: 'dublin' | 'sydney' | 'sao-paulo' | 'singapore' | 'tokyo' | 'virginia';
    edge?: 'dublin' | 'sydney' | 'sao-paulo' | 'singapore' | 'tokyo' | 'ashburn' | 'umatilla';
    /** Default caller ID */
    fromNumber?: E164;
    /** Voice webhook for call control */
    webhookUrl?: string;
    /** Status callback webhook */
    statusWebhookUrl?: string;
    /** Optional subset of Twilio events to subscribe to */
    statusEvents?: Array<'initiated' | 'ringing' | 'answered' | 'completed'>;
    /** Recording status callback webhook */
    recordingStatusUrl?: string;
    /** HTTPS method used for callbacks */
    webhookMethod?: 'POST' | 'GET';
    statusWebhookMethod?: 'POST' | 'GET';
    recordingStatusMethod?: 'POST' | 'GET';
  };
  telnyx?: {
    apiKey: string;
    publicKey?: string;
    connectionId?: string;
    fromNumber?: E164;
    webhookUrl?: string;
    statusWebhookUrl?: string;
    statusWebhookMethod?: 'POST' | 'GET';
    sipRegion?: 'us' | 'eu';
  };
}
