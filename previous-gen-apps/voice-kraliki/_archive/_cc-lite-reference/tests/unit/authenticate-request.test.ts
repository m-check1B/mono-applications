import { describe, it, expect, vi } from 'vitest';
import type { FastifyReply, FastifyRequest } from 'fastify';


import { authenticateRequest, secureCompare } from '../../server/utils/authenticate-request';

const fakeServer = () => ({
  authService: {
    verifySession: vi.fn().mockResolvedValue({ sub: 'user-1', email: 'user@example.com' })
  },
  databaseService: {
    client: {
      user: {
        findUnique: vi.fn().mockResolvedValue({
          id: 'user-1',
          email: 'user@example.com',
          role: 'ADMIN',
          organizationId: 'org-1',
          firstName: 'Test',
          lastName: 'User',
          status: 'ACTIVE'
        })
      }
    }
  }
});

describe('secureCompare utility', () => {
  it('returns false for strings with unequal byte lengths without throwing', () => {
    expect(secureCompare('ä', 'a')).toBe(false);
  });

  it('returns true for identical unicode strings', () => {
    expect(secureCompare('ä', 'ä')).toBe(true);
  });
});

describe('authenticateRequest utility', () => {
  it('returns null when no token is provided', async () => {
    const result = await authenticateRequest({
      cookies: {},
      headers: {},
      server: {}
    } as unknown as FastifyRequest);

    expect(result).toBeNull();
  });

  it('resolves user context when session is valid', async () => {
    const context = await authenticateRequest({
      cookies: { vd_session: 'session-token' },
      headers: {},
      server: fakeServer()
    } as unknown as FastifyRequest);

    expect(context?.user.id).toBe('user-1');
    expect(context?.user.role).toBe('ADMIN');
  });

  it('supports bearer authorization headers regardless of casing', async () => {
    const context = await authenticateRequest({
      cookies: {},
      headers: { authorization: 'bearer session-token' },
      server: fakeServer()
    } as unknown as FastifyRequest);

    expect(context?.user.id).toBe('user-1');
  });

  it('returns null if database lookup fails', async () => {
    const server = fakeServer();
    server.databaseService.client.user.findUnique.mockResolvedValue(null);

    const context = await authenticateRequest({
      cookies: { vd_session: 'session-token' },
      headers: {},
      server
    } as unknown as FastifyRequest);

    expect(context).toBeNull();
  });
});

describe('secureCompare', () => {
  it('returns false for empty or mismatched values', () => {
    expect(secureCompare(undefined, 'token')).toBe(false);
    expect(secureCompare('token', undefined)).toBe(false);
    expect(secureCompare('token', 'other')).toBe(false);
  });

  it('handles multibyte strings without throwing', () => {
    expect(() => secureCompare('ä', 'a')).not.toThrow();
    expect(secureCompare('ä', 'ä')).toBe(true);
  });
});
