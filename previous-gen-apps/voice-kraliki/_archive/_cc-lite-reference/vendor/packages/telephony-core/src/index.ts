import { TwilioProvider } from './providers/twilio.js';
import { TelnyxProvider } from './providers/telnyx.js';
import type { TelephonyProvider, TelephonyConfig } from './types.js';

export * from './types.js';
export { TwilioProvider } from './providers/twilio.js';
export { TelnyxProvider } from './providers/telnyx.js';
export { MediaStreamHandler, createMediaStreamHandler } from './media-stream.js';
export { WebhookHandler, createWebhookHandler } from './webhook-handler.js';
export type { 
  MediaStreamConfig,
  MediaMessage,
  AudioChunk
} from './media-stream.js';
export type {
  WebhookConfig,
  IncomingCallData,
  CallStatusUpdate
} from './webhook-handler.js';
export type { TelephonyProvider };

let provider: TelephonyProvider | null = null;

/**
 * Initialize the telephony provider
 */
export function initTelephony(config: TelephonyConfig): void {
  switch (config.provider) {
    case 'twilio':
      provider = new TwilioProvider(config);
      break;
    case 'telnyx':
      provider = new TelnyxProvider(config);
      break;
    default:
      throw new Error(`Unknown telephony provider: ${config.provider}`);
  }
}

/**
 * Get the current telephony provider instance
 */
export function telephony(): TelephonyProvider {
  if (!provider) {
    throw new Error('Telephony provider not initialized. Call initTelephony() first.');
  }
  return provider;
}

/**
 * Provider feature parity documentation
 */
export const FEATURE_PARITY = {
  twilio: {
    verifySignature: true,
    createOutboundCall: true,
    hangup: true,
    whisper: true,
    transfer: true,
    getRecording: true,
    webRTC: 'Twilio Voice SDK',
    regions: ['dublin', 'sydney', 'sao-paulo', 'singapore', 'tokyo', 'virginia'],
    compliance: {
      gdpr: true,
      dataResidency: true,
      recordingConsent: true
    }
  },
  telnyx: {
    verifySignature: true,
    createOutboundCall: true,
    hangup: true,
    whisper: true,
    transfer: true,
    getRecording: true,
    webRTC: 'Telnyx WebRTC SDK',
    regions: ['us', 'eu'],
    compliance: {
      gdpr: true,
      dataResidency: true,
      recordingConsent: true
    }
  }
} as const;