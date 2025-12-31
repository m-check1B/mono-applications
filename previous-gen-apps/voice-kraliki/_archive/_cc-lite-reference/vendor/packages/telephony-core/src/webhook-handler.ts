/**
 * Unified Webhook Handler for Telephony Providers
 * Handles incoming calls, status updates, and media streams
 */

import { EventEmitter } from 'events';

type RequestLike = {
  body: any;
};

type ReplyLike = {
  type: (contentType: string) => ReplyLike;
  status: (code: number) => ReplyLike;
  send: (payload: any) => unknown;
};

export interface WebhookConfig {
  provider: 'twilio' | 'telnyx';
  baseUrl: string;
  validateSignatures: boolean;
  mediaStreamPath?: string;
}

export interface IncomingCallData {
  callSid: string;
  from: string;
  to: string;
  direction: 'inbound' | 'outbound';
  status: string;
  accountSid?: string;
  callId?: string; // Telnyx uses callId
}

export interface CallStatusUpdate {
  callSid: string;
  status: 'initiated' | 'ringing' | 'answered' | 'completed' | 'failed';
  duration?: number;
  recordingUrl?: string;
  errorCode?: string;
  errorMessage?: string;
}

export class WebhookHandler extends EventEmitter {
  private config: WebhookConfig;

  constructor(config: WebhookConfig) {
    super();
    this.config = config;
  }

  /**
   * Handle incoming call webhook
   */
  public async handleIncomingCall(
    request: RequestLike,
    reply: ReplyLike
  ): Promise<string> {
    try {
      const callData = this.parseIncomingCall(request.body);
      
      // Emit event for processing
      this.emit('incoming-call', callData);

      // Generate TwiML/TeXML response based on provider
      const response = this.generateCallResponse(callData);
      
      reply.type('text/xml');
      return response;
    } catch (error) {
      console.error('Error handling incoming call:', error);
      return this.generateErrorResponse();
    }
  }

  /**
   * Handle call status updates
   */
  public async handleCallStatus(
    request: RequestLike,
    reply: ReplyLike
  ): Promise<void> {
    try {
      const statusUpdate = this.parseCallStatus(request.body);
      
      // Emit status update event
      this.emit('call-status', statusUpdate);
      
      reply.status(200).send({ received: true });
    } catch (error) {
      console.error('Error handling call status:', error);
      reply.status(500).send({ error: 'Failed to process status update' });
    }
  }

  /**
   * Parse incoming call data based on provider
   */
  private parseIncomingCall(body: any): IncomingCallData {
    if (this.config.provider === 'twilio') {
      return {
        callSid: body.CallSid,
        from: body.From,
        to: body.To,
        direction: body.Direction === 'outbound-api' ? 'outbound' : 'inbound',
        status: body.CallStatus,
        accountSid: body.AccountSid
      };
    } else {
      // Telnyx format
      return {
        callSid: body.data?.call_control_id || body.data?.call_leg_id,
        callId: body.data?.call_control_id,
        from: body.data?.from,
        to: body.data?.to,
        direction: body.data?.direction === 'outgoing' ? 'outbound' : 'inbound',
        status: body.data?.state || 'initiated'
      };
    }
  }

  /**
   * Parse call status update based on provider
   */
  private parseCallStatus(body: any): CallStatusUpdate {
    if (this.config.provider === 'twilio') {
      return {
        callSid: body.CallSid,
        status: this.mapTwilioStatus(body.CallStatus),
        duration: parseInt(body.CallDuration || '0'),
        recordingUrl: body.RecordingUrl,
        errorCode: body.ErrorCode,
        errorMessage: body.ErrorMessage
      };
    } else {
      // Telnyx format
      const event = body.data?.event_type;
      return {
        callSid: body.data?.call_control_id || body.data?.call_leg_id,
        status: this.mapTelnyxStatus(event),
        duration: body.data?.call_duration,
        recordingUrl: body.data?.recording_urls?.[0]
      };
    }
  }

  /**
   * Generate call response XML based on provider
   */
  private generateCallResponse(callData: IncomingCallData): string {
    const wsUrl = this.getWebSocketUrl(callData.callSid);
    
    if (this.config.provider === 'twilio') {
      return this.generateTwiML(wsUrl);
    } else {
      return this.generateTeXML(wsUrl);
    }
  }

  /**
   * Generate TwiML response for Twilio
   */
  private generateTwiML(wsUrl: string): string {
    return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="${this.escapeXml(wsUrl)}" />
    </Connect>
</Response>`;
  }

  /**
   * Generate TeXML response for Telnyx
   */
  private generateTeXML(wsUrl: string): string {
    return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="${this.escapeXml(wsUrl)}" />
    </Connect>
</Response>`;
  }

  /**
   * Generate error response
   */
  private generateErrorResponse(): string {
    if (this.config.provider === 'twilio') {
      return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>We're sorry, but we're unable to process your call at this time. Please try again later.</Say>
    <Hangup/>
</Response>`;
    } else {
      return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>We're sorry, but we're unable to process your call at this time. Please try again later.</Speak>
    <Hangup/>
</Response>`;
    }
  }

  /**
   * Get WebSocket URL for media streaming
   */
  private getWebSocketUrl(callSid: string): string {
    const protocol = this.config.baseUrl.startsWith('https') ? 'wss' : 'ws';
    const baseUrl = this.config.baseUrl.replace(/^https?/, protocol);
    const path = this.config.mediaStreamPath || '/media-stream';
    return `${baseUrl}${path}?callSid=${callSid}`;
  }

  /**
   * Map Twilio status to unified status
   */
  private mapTwilioStatus(status: string): CallStatusUpdate['status'] {
    const statusMap: Record<string, CallStatusUpdate['status']> = {
      'queued': 'initiated',
      'initiated': 'initiated',
      'ringing': 'ringing',
      'in-progress': 'answered',
      'completed': 'completed',
      'failed': 'failed',
      'busy': 'failed',
      'no-answer': 'failed'
    };
    return statusMap[status] || 'failed';
  }

  /**
   * Map Telnyx status to unified status
   */
  private mapTelnyxStatus(event: string): CallStatusUpdate['status'] {
    const statusMap: Record<string, CallStatusUpdate['status']> = {
      'call.initiated': 'initiated',
      'call.ringing': 'ringing',
      'call.answered': 'answered',
      'call.hangup': 'completed',
      'call.failed': 'failed'
    };
    return statusMap[event] || 'failed';
  }

  /**
   * Escape XML special characters
   */
  private escapeXml(str: string): string {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }
}

/**
 * Factory function to create provider-specific webhook handlers
 */
export function createWebhookHandler(config: WebhookConfig): WebhookHandler {
  return new WebhookHandler(config);
}
