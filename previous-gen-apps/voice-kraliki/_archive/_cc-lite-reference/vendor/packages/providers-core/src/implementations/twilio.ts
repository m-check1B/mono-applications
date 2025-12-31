/**
 * Twilio telephony implementation
 */

import { 
  BaseTelephonyClient, 
  TelephonyProvider, 
  Call, 
  Message,
  RealtimeConnection 
} from '../telephony';

export class TwilioClient extends BaseTelephonyClient {
  provider: TelephonyProvider = 'twilio';
  
  private apiUrl = 'https://api.twilio.com/2010-04-01';
  
  private getAuthHeader(): string {
    const auth = Buffer.from(`${this.config.accountSid}:${this.config.authToken}`).toString('base64');
    return `Basic ${auth}`;
  }
  
  async makeCall(to: string, from: string, options?: any): Promise<Call> {
    const formData = new URLSearchParams();
    formData.append('To', to);
    formData.append('From', from);
    
    if (options?.url) {
      formData.append('Url', options.url);
    }
    if (options?.statusCallback) {
      formData.append('StatusCallback', options.statusCallback);
    }
    if (options?.record?.enabled) {
      formData.append('Record', 'true');
      if (options.record.channels) {
        formData.append('RecordingChannels', options.record.channels);
      }
    }
    if (options?.machineDetection) {
      formData.append('MachineDetection', 'Enable');
    }
    
    const response = await fetch(
      `${this.apiUrl}/Accounts/${this.config.accountSid}/Calls.json`,
      {
        method: 'POST',
        headers: {
          'Authorization': this.getAuthHeader(),
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      }
    );
    
    if (!response.ok) {
      throw new Error(`Twilio API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    return this.mapTwilioCall(data);
  }
  
  async getCall(callId: string): Promise<Call> {
    const response = await fetch(
      `${this.apiUrl}/Accounts/${this.config.accountSid}/Calls/${callId}.json`,
      {
        headers: {
          'Authorization': this.getAuthHeader(),
        },
      }
    );
    
    if (!response.ok) {
      throw new Error(`Twilio API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    return this.mapTwilioCall(data);
  }
  
  async updateCall(callId: string, options: any): Promise<Call> {
    const formData = new URLSearchParams();
    
    if (options.status === 'completed') {
      formData.append('Status', 'completed');
    }
    if (options.url) {
      formData.append('Url', options.url);
    }
    
    const response = await fetch(
      `${this.apiUrl}/Accounts/${this.config.accountSid}/Calls/${callId}.json`,
      {
        method: 'POST',
        headers: {
          'Authorization': this.getAuthHeader(),
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      }
    );
    
    if (!response.ok) {
      throw new Error(`Twilio API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    return this.mapTwilioCall(data);
  }
  
  async sendMessage(to: string, from: string, body: string, mediaUrls?: string[]): Promise<Message> {
    const formData = new URLSearchParams();
    formData.append('To', to);
    formData.append('From', from);
    formData.append('Body', body);
    
    if (mediaUrls) {
      mediaUrls.forEach(url => formData.append('MediaUrl', url));
    }
    
    const response = await fetch(
      `${this.apiUrl}/Accounts/${this.config.accountSid}/Messages.json`,
      {
        method: 'POST',
        headers: {
          'Authorization': this.getAuthHeader(),
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      }
    );
    
    if (!response.ok) {
      throw new Error(`Twilio API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    return this.mapTwilioMessage(data);
  }
  
  async getMessage(messageId: string): Promise<Message> {
    const response = await fetch(
      `${this.apiUrl}/Accounts/${this.config.accountSid}/Messages/${messageId}.json`,
      {
        headers: {
          'Authorization': this.getAuthHeader(),
        },
      }
    );
    
    if (!response.ok) {
      throw new Error(`Twilio API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    return this.mapTwilioMessage(data);
  }
  
  async createRealtimeConnection(callId: string): Promise<RealtimeConnection> {
    // For Twilio Media Streams
    return {
      connectionId: `conn_${callId}`,
      callId,
      websocketUrl: `wss://media.twilio.com/v1/MediaStreams/${callId}`,
      token: this.config.authToken,
    };
  }
  
  async listPhoneNumbers() {
    const response = await fetch(
      `${this.apiUrl}/Accounts/${this.config.accountSid}/IncomingPhoneNumbers.json`,
      {
        headers: {
          'Authorization': this.getAuthHeader(),
        },
      }
    );
    
    if (!response.ok) {
      throw new Error(`Twilio API error: ${response.statusText}`);
    }
    
    const data = await response.json() as any;
    
    return data.incoming_phone_numbers.map((number: any) => ({
      phoneNumber: number.phone_number,
      capabilities: {
        voice: number.capabilities.voice,
        sms: number.capabilities.sms,
        mms: number.capabilities.mms,
      },
    }));
  }
  
  validateWebhook(signature: string, body: string, url: string): boolean {
    // Implement Twilio webhook signature validation
    const crypto = require('crypto');
    const authToken = this.config.authToken;
    
    const data = url + body;
    const expectedSignature = crypto
      .createHmac('sha1', authToken)
      .update(data)
      .digest('base64');
    
    return signature === expectedSignature;
  }
  
  private mapTwilioCall(twilioCall: any): Call {
    return {
      id: twilioCall.sid,
      from: twilioCall.from,
      to: twilioCall.to,
      direction: twilioCall.direction as any,
      status: this.mapCallStatus(twilioCall.status),
      duration: twilioCall.duration ? parseInt(twilioCall.duration) : undefined,
    };
  }
  
  private mapTwilioMessage(twilioMessage: any): Message {
    return {
      id: twilioMessage.sid,
      from: twilioMessage.from,
      to: twilioMessage.to,
      body: twilioMessage.body,
      status: twilioMessage.status as any,
      direction: twilioMessage.direction as any,
      mediaUrls: twilioMessage.media_list?.map((m: any) => m.uri),
    };
  }
  
  private mapCallStatus(twilioStatus: string): any {
    const statusMap: Record<string, string> = {
      'queued': 'queued',
      'ringing': 'ringing',
      'in-progress': 'in-progress',
      'completed': 'completed',
      'failed': 'failed',
      'busy': 'busy',
      'no-answer': 'no-answer',
    };
    return statusMap[twilioStatus] || twilioStatus;
  }
}