import { describe, it, expect, vi } from 'vitest';
import { SecureCookieManager } from '../../../server/utils/secure-cookie-manager';

function createReplyMock() {
  return {
    setCookie: vi.fn(),
    clearCookie: vi.fn(),
  } as any;
}

describe('SecureCookieManager', () => {
  it('sets, gets, and clears signed+encrypted cookie', () => {
    process.env.NODE_ENV = 'development';
    process.env.COOKIE_SECRET = 'dev-cookie-secret-please-change';
    const mgr = new SecureCookieManager();
    const reply = createReplyMock();

    mgr.setCookie(reply, 'session', 'hello', { encrypted: true });
    expect(reply.setCookie).toHaveBeenCalled();
    const [name, value] = reply.setCookie.mock.calls[0];
    expect(name).toBe('session');
    expect(typeof value).toBe('string');
    expect(value.includes('.')).toBe(true); // signed format

    const request = { cookies: { session: value } } as any;
    const got = mgr.getCookie(request, 'session', { encrypted: true });
    expect(got).toBe('hello');

    mgr.clearCookie(reply, 'session');
    expect(reply.clearCookie).toHaveBeenCalled();
  });
});

