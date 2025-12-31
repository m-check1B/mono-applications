import * as Telnyx from 'telnyx';
import { createPublicKey, verify as verifySignature } from 'crypto';
import {
  type TelephonyProvider,
  type E164,
  type SipUri,
  type CallId,
  type OutboundCallInput,
  type WebhookHeaders,
  TelephonyError,
  type TelephonyConfig,
  type RecordingResult
} from '../types.js';

const logger = console;

export class TelnyxProvider implements TelephonyProvider {
  private client: any; // Telnyx SDK types are not great
  private apiKey: string;
  private publicKey?: string;
  private connectionId?: string;
  private fromNumber?: E164;
  private webhookUrl?: string;
  private statusWebhookUrl?: string;
  private statusWebhookMethod: 'POST' | 'GET';

  constructor(config: TelephonyConfig) {
    if (!config.telnyx) {
      throw new TelephonyError('Telnyx configuration is required');
    }

    const {
      apiKey,
      publicKey,
      connectionId,
      fromNumber,
      webhookUrl,
      statusWebhookUrl,
      statusWebhookMethod
    } = config.telnyx;
    
    this.apiKey = apiKey;
    this.publicKey = publicKey;
    this.connectionId = connectionId;
    this.fromNumber = fromNumber;
    this.webhookUrl = webhookUrl;
    this.statusWebhookUrl = statusWebhookUrl;
    this.statusWebhookMethod = statusWebhookMethod || 'POST';
    
    // Initialize Telnyx client
    this.client = new (Telnyx as any)(apiKey);

    logger.info('Telnyx provider initialized');
  }

  verifySignature(rawBody: Buffer, headers: WebhookHeaders): boolean {
    const signature = headers['telnyx-signature-ed25519'];
    const timestamp = headers['telnyx-timestamp'];
    
    if (!signature || !timestamp || typeof signature !== 'string' || typeof timestamp !== 'string') {
      logger.warn('Missing or invalid Telnyx signature headers');
      return false;
    }

    try {
      // Telnyx uses Ed25519 signatures
      if (!this.publicKey) {
        logger.warn('Telnyx public key not configured, cannot verify signature');
        return false;
      }

      const message = Buffer.from(`${timestamp}|${rawBody.toString('utf8')}`);
      const key = createPublicKey(this.publicKey);
      const sigBuffer = Buffer.from(signature, 'base64');
      const valid = verifySignature(null, message, key, sigBuffer);
      
      if (!valid) {
        logger.warn('Invalid Telnyx webhook signature');
      }
      
      // Check timestamp to prevent replay attacks (5 minute window)
      const currentTime = Math.floor(Date.now() / 1000);
      const webhookTime = parseInt(timestamp, 10);
      
      if (Math.abs(currentTime - webhookTime) > 300) {
        logger.warn('Telnyx webhook timestamp outside acceptable window');
        return false;
      }
      
      return valid;
    } catch (error) {
      logger.error({ error }, 'Error verifying Telnyx signature');
      return false;
    }
  }

  async createOutboundCall(input: OutboundCallInput): Promise<CallId> {
    try {
      const maskedFrom = this.maskPhoneNumber(input.from);
      const maskedTo = this.maskPhoneNumber(input.to);
      
      logger.info(
        { from: maskedFrom, to: maskedTo, metadata: input.metadata },
        'Creating outbound call'
      );

      const connectionId = this.connectionId
        || process.env.TELNYX_CONNECTION_ID
        || process.env.STACK_TELNYX_CONNECTION_ID;
      if (!connectionId) {
        throw new TelephonyError('Telnyx connection ID is required to create calls');
      }

      const webhookUrl = this.webhookUrl
        || process.env.TELNYX_WEBHOOK_URL
        || process.env.STACK_TELNYX_WEBHOOK_URL;
      const statusWebhook = this.statusWebhookUrl
        || process.env.TELNYX_STATUS_WEBHOOK_URL
        || process.env.STACK_TELNYX_STATUS_WEBHOOK_URL;

      const callPayload: Record<string, unknown> = {
        connection_id: connectionId,
        from: input.from,
        to: input.to,
        record: 'do-not-record', // Recording off by default (EU compliance)
        webhook_url: webhookUrl,
        webhook_url_method: webhookUrl ? 'POST' : undefined,
        status_callback_url: statusWebhook,
        status_callback_method: statusWebhook ? this.statusWebhookMethod : undefined,
        custom_headers: input.metadata
          ? [{ name: 'X-Metadata', value: JSON.stringify(input.metadata) }]
          : undefined
      };

      const call = await this.client.calls.create(callPayload);

      logger.info({ callControlId: call.data.call_control_id }, 'Outbound call created');
      return call.data.call_control_id;
    } catch (error: any) {
      logger.error({ error }, 'Failed to create outbound call');
      throw new TelephonyError(
        `Failed to create call: ${error.message}`,
        error.code
      );
    }
  }

  async hangup(callId: CallId): Promise<void> {
    try {
      logger.info({ callId }, 'Hanging up call');
      
      await this.client.calls.hangup(callId);
      
      logger.info({ callId }, 'Call hung up');
    } catch (error: any) {
      logger.error({ error, callId }, 'Failed to hangup call');
      throw new TelephonyError(
        `Failed to hangup call: ${error.message}`,
        error.code
      );
    }
  }

  async whisper(callId: CallId, text: string): Promise<void> {
    try {
      logger.info({ callId, textLength: text.length }, 'Playing whisper message');
      
      // Telnyx speak command for text-to-speech
      await this.client.calls.speak(callId, {
        payload: text,
        voice: 'female',
        language: 'en-US'
      });
      
      logger.info({ callId }, 'Whisper message played');
    } catch (error: any) {
      logger.error({ error, callId }, 'Failed to play whisper');
      throw new TelephonyError(
        `Failed to play whisper: ${error.message}`,
        error.code
      );
    }
  }

  async transfer(callId: CallId, to: E164 | SipUri): Promise<void> {
    try {
      const maskedTo = to.startsWith('sip:') ? to : this.maskPhoneNumber(to as E164);
      logger.info({ callId, to: maskedTo }, 'Transferring call');
      
      const transferPayload: Record<string, unknown> = {
        to
      };

      const fromNumber = this.fromNumber
        || process.env.TELNYX_PHONE_NUMBER
        || process.env.STACK_TELNYX_FROM_NUMBER;
      if (fromNumber) {
        transferPayload.from = fromNumber;
      }

      await this.client.calls.transfer(callId, transferPayload);
      
      logger.info({ callId, to: maskedTo }, 'Call transferred');
    } catch (error: any) {
      logger.error({ error, callId }, 'Failed to transfer call');
      throw new TelephonyError(
        `Failed to transfer call: ${error.message}`,
        error.code
      );
    }
  }

  async getRecording(callId: CallId): Promise<RecordingResult> {
    try {
      logger.info({ callId }, 'Fetching call recording');
      
      // List recordings for this call
      const recordings = await this.client.recordings.list({
        filter: { call_control_id: callId }
      });
      
      if (!recordings.data || recordings.data.length === 0) {
        throw new TelephonyError('No recording found for this call');
      }
      
      const recording = recordings.data[0];
      const recordingUrl = recording.download_url;

      if (!recordingUrl) {
        throw new TelephonyError('Recording download URL missing');
      }

      logger.info({ callId, recordingId: recording.id }, 'Recording fetched');

      return {
        type: 'url',
        url: recordingUrl
      };
    } catch (error: any) {
      logger.error({ error, callId }, 'Failed to get recording');
      throw new TelephonyError(
        `Failed to get recording: ${error.message}`,
        error.code
      );
    }
  }

  private maskPhoneNumber(phone: E164): string {
    // Mask middle digits, keep country code and last 4 digits
    if (phone.length <= 7) return phone;
    const countryCode = phone.substring(0, 3);
    const lastFour = phone.substring(phone.length - 4);
    const masked = '*'.repeat(phone.length - 7);
    return `${countryCode}${masked}${lastFour}`;
  }
}
