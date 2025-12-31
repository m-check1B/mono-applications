import * as Twilio from 'twilio';
import { Readable } from 'stream';
import { createHmac } from 'crypto';
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

export class TwilioProvider implements TelephonyProvider {
  private client: Twilio.Twilio;
  private authToken: string;
  private accountSid: string;
  private region?: string;
  private edge?: string;
  private webhookUrl?: string;
  private webhookMethod: 'GET' | 'POST';
  private statusCallbackUrl?: string;
  private statusCallbackMethod: 'GET' | 'POST';
  private statusEvents: Array<'initiated' | 'ringing' | 'answered' | 'completed'>;
  private recordingStatusUrl?: string;
  private recordingStatusMethod: 'GET' | 'POST';

  constructor(config: TelephonyConfig) {
    if (!config.twilio) {
      throw new TelephonyError('Twilio configuration is required');
    }

    const {
      accountSid,
      authToken,
      region,
      edge,
      webhookUrl,
      webhookMethod,
      statusWebhookUrl,
      statusWebhookMethod,
      statusEvents,
      recordingStatusUrl,
      recordingStatusMethod
    } = config.twilio;
    
    this.accountSid = accountSid;
    this.authToken = authToken;
    this.region = region || 'dublin'; // EU default
    this.edge = edge || 'dublin'; // EU default
    this.webhookUrl = webhookUrl || process.env.STACK_TWILIO_WEBHOOK_URL;
    this.webhookMethod = webhookMethod || 'POST';
    this.statusCallbackUrl = statusWebhookUrl || process.env.STACK_TWILIO_STATUS_CALLBACK_URL;
    this.statusCallbackMethod = statusWebhookMethod || 'POST';
    this.statusEvents = statusEvents || ['initiated', 'ringing', 'answered', 'completed'];
    this.recordingStatusUrl = recordingStatusUrl || process.env.STACK_TWILIO_RECORDING_STATUS_URL;
    this.recordingStatusMethod = recordingStatusMethod || 'POST';
    
    // Initialize Twilio client with EU region by default
    this.client = (Twilio as any).default(accountSid, authToken, {
      region: this.region as any,
      edge: this.edge as any
    });

    logger.log('Twilio provider initialized', { region: this.region, edge: this.edge });
  }

  verifySignature(rawBody: Buffer, headers: WebhookHeaders): boolean {
    const signature = headers['x-twilio-signature'];
    const url = headers['x-forwarded-proto'] + '://' + headers['host'] + headers['x-original-uri'];
    
    if (!signature || typeof signature !== 'string') {
      logger.warn('Missing or invalid X-Twilio-Signature header');
      return false;
    }

    try {
      // Twilio signature validation
      const authToken = this.authToken;
      const data = Object.keys(headers)
        .sort()
        .reduce((acc, key) => {
          if (key.startsWith('x-twilio-')) {
            return acc + key + headers[key];
          }
          return acc;
        }, url);

      const expectedSignature = createHmac('sha1', authToken)
        .update(Buffer.from(data, 'utf-8'))
        .digest('base64');

      const valid = signature === expectedSignature;
      
      if (!valid) {
        logger.warn('Invalid Twilio webhook signature');
      }
      
      return valid;
    } catch (error) {
      logger.error('Error verifying Twilio signature', error);
      return false;
    }
  }

  async createOutboundCall(input: OutboundCallInput): Promise<CallId> {
    try {
      // Mask phone numbers in logs
      const maskedFrom = this.maskPhoneNumber(input.from);
      const maskedTo = this.maskPhoneNumber(input.to);
      
      logger.log('Creating outbound call', { from: maskedFrom, to: maskedTo, metadata: input.metadata });

      const webhookUrl = this.resolveWebhookUrl(input.metadata);
      const callPayload = {
        from: input.from,
        to: input.to,
        url: webhookUrl,
        method: this.webhookMethod,
        statusCallback: this.statusCallbackUrl,
        statusCallbackMethod: this.statusCallbackMethod,
        statusCallbackEvent: this.statusEvents,
        record: false,
        machineDetection: 'DetectMessageEnd',
        recordingStatusCallback: this.recordingStatusUrl,
        recordingStatusCallbackMethod: this.recordingStatusMethod
      };

      const call = await this.client.calls.create(callPayload as any);

      logger.log('Outbound call created', { callSid: call.sid });
      return call.sid;
    } catch (error: any) {
      logger.error('Failed to create outbound call', error);
      throw new TelephonyError(
        `Failed to create call: ${error.message}`,
        error.code
      );
    }
  }

  async hangup(callId: CallId): Promise<void> {
    try {
      logger.log('Hanging up call', { callId });
      
      await this.client.calls(callId).update({
        status: 'completed'
      });
      
      logger.log('Call hung up', { callId });
    } catch (error: any) {
      logger.error('Failed to hangup call', { error, callId });
      throw new TelephonyError(
        `Failed to hangup call: ${error.message}`,
        error.code
      );
    }
  }

  async whisper(callId: CallId, text: string): Promise<void> {
    try {
      logger.log('Playing whisper message', { callId, textLength: text.length });
      
      // Use TwiML to play text-to-speech
      const twiml = `<?xml version="1.0" encoding="UTF-8"?>
        <Response>
          <Say language="en-US">${text}</Say>
        </Response>`;
      
      await this.client.calls(callId).update({
        twiml
      });
      
      logger.log('Whisper message played', { callId });
    } catch (error: any) {
      logger.error('Failed to play whisper', { error, callId });
      throw new TelephonyError(
        `Failed to play whisper: ${error.message}`,
        error.code
      );
    }
  }

  async transfer(callId: CallId, to: E164 | SipUri): Promise<void> {
    try {
      const maskedTo = to.startsWith('sip:') ? to : this.maskPhoneNumber(to as E164);
      logger.log('Transferring call', { callId, to: maskedTo });
      
      // Use TwiML to transfer the call
      const twiml = `<?xml version="1.0" encoding="UTF-8"?>
        <Response>
          <Dial>${to}</Dial>
        </Response>`;
      
      await this.client.calls(callId).update({
        twiml
      });
      
      logger.log('Call transferred', { callId, to: maskedTo });
    } catch (error: any) {
      logger.error('Failed to transfer call', { error, callId });
      throw new TelephonyError(
        `Failed to transfer call: ${error.message}`,
        error.code
      );
    }
  }

  async getRecording(callId: CallId): Promise<RecordingResult> {
    try {
      logger.log('Fetching call recording', { callId });
      
      // Get recordings for this call
      const recordings = await this.client.recordings.list({
        callSid: callId,
        limit: 1
      });
      
      if (recordings.length === 0) {
        throw new TelephonyError('No recording found for this call');
      }
      
      const recording = recordings[0];
      const recordingUrl = `https://api.twilio.com${recording.uri.replace('.json', '.mp3')}`;
      const response = await fetch(recordingUrl, {
        headers: {
          Authorization: 'Basic ' + Buffer.from(`${this.accountSid}:${this.authToken}`).toString('base64')
        }
      });

      if (!response.ok) {
        throw new TelephonyError(`Failed to fetch recording: ${response.statusText}`);
      }

      logger.log('Recording fetched', { callId, recordingSid: recording.sid });

      const nodeStream = Readable.from(response.body as any);
      return {
        type: 'stream',
        stream: nodeStream,
        contentType: response.headers.get('content-type') || 'audio/mpeg',
        filename: `${callId}.mp3`
      };
    } catch (error: any) {
      logger.error('Failed to get recording', { error, callId });
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

  private resolveWebhookUrl(metadata?: OutboundCallInput['metadata']): string {
    const baseUrl = this.webhookUrl || 'https://demo.twilio.com/welcome/voice/';
    if (!metadata || Object.keys(metadata).length === 0) {
      return baseUrl;
    }

    const params = new URLSearchParams(
      Object.entries(metadata).map(([key, value]) => [key, String(value)]) as [string, string][]
    );
    const separator = baseUrl.includes('?') ? '&' : '?';
    return `${baseUrl}${separator}${params.toString()}`;
  }
}
