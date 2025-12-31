import { describe, it, expect, beforeEach, vi, type Mock } from 'vitest';
import type { FastifyInstance } from 'fastify';

vi.mock('../../server/services/deepgram-agent-service', () => {
  class MockDeepgramAgentService {
    on() {
      return this;
    }

    getActiveSessions() {
      return [];
    }

    async destroy() {
      // no-op for tests
    }
  }

  return { DeepgramAgentService: MockDeepgramAgentService };
});

vi.mock('../../server/audio/twilio-agent-handler', () => {
  class MockTwilioAgentHandler {
    on() {
      return this;
    }

    handleWebSocketConnection() {
      // no-op for tests
    }
  }

  return { TwilioAgentHandler: MockTwilioAgentHandler };
});

vi.mock('../../server/utils/authenticate-request', () => ({
  authenticateRequest: vi.fn(),
}));

import websocketAgentHandler from '../../server/plugins/websocket-agent';
import { authenticateRequest } from '../../server/utils/authenticate-request';

describe('Voice Agent WebSocket security', () => {
  let fastify: Partial<FastifyInstance> & {
    capturedWsHandler?: (connection: any, request: any) => Promise<void> | void;
  };
  let wsHandler: ((connection: any, request: any) => Promise<void>) | undefined;

  beforeEach(async () => {
    wsHandler = undefined;

    fastify = {
      log: {
        info: vi.fn(),
        warn: vi.fn(),
        error: vi.fn(),
      },
      decorate: vi.fn(),
      addHook: vi.fn(),
      get: vi.fn((path: string, _options: any, handler: any) => {
        if (path === '/ws') {
          wsHandler = handler;
        }
      }) as any,
    };

    await websocketAgentHandler(fastify as FastifyInstance, { coreSystem: {} as any });
  });

  it('rejects unauthenticated WebSocket connections with 4401 code', async () => {
    const mockedAuth = authenticateRequest as unknown as Mock;
    mockedAuth.mockResolvedValueOnce(null);

    const close = vi.fn();
    const send = vi.fn();
    const on = vi.fn();

    const connection = { close, send, on, readyState: 1 };

    await wsHandler!(connection, { headers: {}, cookies: {}, server: {} });

    expect(close).toHaveBeenCalledWith(4401, 'Authentication required');
    expect(send).not.toHaveBeenCalled();
  });

  it('sends connected event for authenticated users with organization', async () => {
    const mockedAuth = authenticateRequest as unknown as Mock;
    mockedAuth.mockResolvedValueOnce({
      token: 'token',
      payload: { sub: 'user-1', email: 'user@example.com' },
      user: {
        id: 'user-1',
        email: 'user@example.com',
        role: 'SUPERVISOR',
        organizationId: 'org-123',
        firstName: 'Test',
        lastName: 'User',
        status: 'ACTIVE',
      },
    });

    const close = vi.fn();
    const send = vi.fn();
    const on = vi.fn();

    const connection = { close, send, on, readyState: 1 };

    await wsHandler!(connection, { headers: {}, cookies: {}, server: {} });

    expect(close).not.toHaveBeenCalled();
    expect(send).toHaveBeenCalledTimes(1);

    const payload = JSON.parse(send.mock.calls[0][0]);
    expect(payload.event).toBe('connected');
    expect(payload.data.orgId).toBe('org-123');
    expect(payload.data.voiceAgentEnabled).toBe(true);
  });
});
