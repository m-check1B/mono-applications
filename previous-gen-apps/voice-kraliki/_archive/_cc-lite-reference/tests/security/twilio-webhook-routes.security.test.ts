import { describe, it, expect, beforeEach, vi, type Mock } from 'vitest';

vi.mock('../../server/utils/twilio-security', () => ({
  verifyTwilioWebhookRequest: vi.fn(),
  logSecurityEvent: vi.fn(),
}));

import { registerTwilioWebhookRoutes } from '../../server/routes/twilio-webhooks';
import { verifyTwilioWebhookRequest, logSecurityEvent } from '../../server/utils/twilio-security';

type RouteHandler = (request: any, reply: any) => Promise<void> | void;

describe('Twilio webhook routes', () => {
  const mockLogger = {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  };

  const createReply = () => {
    const reply: any = {
      statusCode: 200,
      payload: undefined as unknown,
      contentType: undefined as string | undefined,
    };

    reply.code = vi.fn((status: number) => {
      reply.statusCode = status;
      return reply;
    });

    reply.send = vi.fn((body: unknown) => {
      reply.payload = body;
      return reply;
    });

    reply.type = vi.fn((contentType: string) => {
      reply.contentType = contentType;
      return reply;
    });

    return reply;
  };

  let routes: Record<string, RouteHandler>;
  let databaseClient: { updateMany: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    routes = {};
    databaseClient = {
      updateMany: vi.fn().mockResolvedValue({ count: 1 }),
    };

    const server = {
      post: vi.fn((path: string, handler: RouteHandler) => {
        routes[path] = handler;
      }),
    } as any;

    registerTwilioWebhookRoutes(server, {
      logger: mockLogger,
      databaseClient,
    });

    vi.clearAllMocks();
  });

  it('rejects status webhook when signature verification fails', async () => {
    const reply = createReply();
    const request = {
      body: { CallSid: 'CA123', CallStatus: 'failed' },
    };

    (verifyTwilioWebhookRequest as unknown as Mock).mockResolvedValueOnce(false);

    await routes['/webhooks/twilio/status'](request, reply);

    expect(databaseClient.updateMany).not.toHaveBeenCalled();
    expect(reply.send).not.toHaveBeenCalled();
    expect(logSecurityEvent).toHaveBeenCalledWith('INVALID_SIGNATURE', request, { endpoint: 'status' });
  });

  it('updates call status and responds when signature is valid', async () => {
    const reply = createReply();
    const request = {
      body: { CallSid: 'CA999', CallStatus: 'completed' },
    };

    (verifyTwilioWebhookRequest as unknown as Mock).mockResolvedValueOnce(true);

    await routes['/webhooks/twilio/status'](request, reply);

    expect(verifyTwilioWebhookRequest).toHaveBeenCalledWith(request, reply);
    expect(databaseClient.updateMany).toHaveBeenCalledWith({
      where: { providerCallId: 'CA999' },
      data: { status: 'COMPLETED' },
    });
    expect(reply.send).toHaveBeenCalledWith({ success: true });
  });
});
