import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import twilio from 'twilio';
import { verifyTwilioWebhookRequest } from '../../server/utils/twilio-security';

const createMockReply = () => {
  const reply: any = {
    statusCode: undefined as number | undefined,
    payload: undefined as unknown,
  };

  reply.code = vi.fn((status: number) => {
    reply.statusCode = status;
    return reply;
  });

  reply.send = vi.fn((payload: unknown) => {
    reply.payload = payload;
    return reply;
  });

  return reply;
};

describe('Twilio Webhook Security', () => {
  const originalEnv = process.env.NODE_ENV;
  const originalAuthToken = process.env.TWILIO_AUTH_TOKEN;

  beforeEach(() => {
    process.env.NODE_ENV = 'production';
    process.env.TWILIO_AUTH_TOKEN = 'test-auth-token';
  });

  afterEach(() => {
    process.env.NODE_ENV = originalEnv;
    process.env.TWILIO_AUTH_TOKEN = originalAuthToken;
    vi.restoreAllMocks();
  });

  it('rejects webhook requests missing the X-Twilio-Signature header', async () => {
    const reply = createMockReply();
    const request = {
      headers: {
        host: 'cc.example.com',
        'x-forwarded-proto': 'https'
      },
      url: '/webhooks/twilio/voice',
      ip: '203.0.113.10',
      body: {}
    } as any;

    const isValid = await verifyTwilioWebhookRequest(request, reply as any);

    expect(isValid).toBe(false);
    expect(reply.code).toHaveBeenCalledWith(403);
    expect(reply.send).toHaveBeenCalledWith(
      expect.objectContaining({ error: 'Missing Twilio signature' })
    );
  });

  it('rejects webhook requests with an invalid signature', async () => {
    vi.spyOn(twilio, 'validateRequest').mockReturnValue(false);

    const reply = createMockReply();
    const request = {
      headers: {
        host: 'cc.example.com',
        'x-forwarded-proto': 'https',
        'x-twilio-signature': 'invalid-signature'
      },
      url: '/webhooks/twilio/status',
      ip: '203.0.113.11',
      body: { CallSid: 'CA123', CallStatus: 'completed' }
    } as any;

    const isValid = await verifyTwilioWebhookRequest(request, reply as any);

    expect(isValid).toBe(false);
    expect(reply.code).toHaveBeenCalledWith(403);
    expect(reply.send).toHaveBeenCalledWith(
      expect.objectContaining({ error: 'Invalid Twilio signature' })
    );
  });

  it('accepts webhook requests with a valid signature', async () => {
    vi.spyOn(twilio, 'validateRequest').mockReturnValue(true);

    const reply = createMockReply();
    const request = {
      headers: {
        host: 'cc.example.com',
        'x-forwarded-proto': 'https',
        'x-twilio-signature': 'valid-signature'
      },
      url: '/webhooks/twilio/status',
      ip: '203.0.113.50',
      body: { CallSid: 'CA321', CallStatus: 'in-progress' }
    } as any;

    const isValid = await verifyTwilioWebhookRequest(request, reply as any);

    expect(isValid).toBe(true);
    expect(reply.code).not.toHaveBeenCalledWith(403);
    expect(reply.send).not.toHaveBeenCalledWith(
      expect.objectContaining({ error: expect.any(String) })
    );
  });
});
