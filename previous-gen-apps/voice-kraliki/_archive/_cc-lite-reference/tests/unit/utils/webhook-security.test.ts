import { describe, it, expect } from 'vitest';
import { verifyTwilioWebhookRequest, logSecurityEvent } from '../../../server/utils/webhook-security';

function makeReq(url: string, body: any, headers: Record<string,string> = {}) {
  return {
    url,
    ip: '127.0.0.1',
    method: 'POST',
    headers: {
      host: 'example.com',
      'x-forwarded-proto': 'https',
      ...headers,
    },
    body,
  } as any;
}

function makeReply() {
  return { code: () => ({ send: () => {} }) } as any;
}

describe('webhook-security', () => {
  it('skips twilio verification in development', async () => {
    process.env.NODE_ENV = 'development';
    process.env.TWILIO_AUTH_TOKEN = 'token';
    const ok = await verifyTwilioWebhookRequest(makeReq('/twilio', { a: '1' }, {}), makeReply());
    expect(ok).toBe(true);
  });

  it('logs security event without throwing', () => {
    const req = makeReq('/test', {});
    expect(() => logSecurityEvent('TEST_EVENT', req, { x: 1 })).not.toThrow();
  });
});

