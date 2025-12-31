import path from 'node:path';
import crypto from 'node:crypto';
import { config as loadEnv } from 'dotenv';
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { UserRole, CallStatus } from '@prisma/client';
import { TRPCError } from '@trpc/server';
import { appRouter } from '../../server/trpc/app.router';
import { redisService } from '../../server/services/redis-service';
import { testDb, createTestUser, createTestCampaign, createTestCall } from '../setup';

loadEnv({ path: path.resolve(__dirname, '../..', '.env'), override: true });

const { privateKey, publicKey } = crypto.generateKeyPairSync('ed25519', {
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
  publicKeyEncoding: { type: 'spki', format: 'pem' },
});
process.env.AUTH_PRIVATE_KEY = privateKey;
process.env.AUTH_PUBLIC_KEY = publicKey;

if (typeof global.TextEncoder === "undefined") {
  const { TextEncoder, TextDecoder } = require("util");
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;
}

const redisMock = {
  setSession: vi.fn().mockResolvedValue(undefined),
  getCounter: vi.fn().mockResolvedValue(0),
  getQueueLength: vi.fn().mockResolvedValue(0),
};

vi.spyOn(redisService, 'setSession').mockImplementation(redisMock.setSession as any);

const fastifyStub = {
  log: console,
  databaseService: { client: testDb },
  redisService: redisMock,
};

const toCtxUser = (dbUser: any) => ({
  id: dbUser.id,
  sub: dbUser.id,
  email: dbUser.email,
  role: dbUser.role.toLowerCase(),
  roles: [dbUser.role.toLowerCase()],
  organizationId: dbUser.organizationId,
  orgId: dbUser.organizationId,
  name: `${dbUser.firstName ?? ''} ${dbUser.lastName ?? ''}`.trim() || dbUser.email,
});

function createCaller(user?: ReturnType<typeof toCtxUser>) {
  const req = {
    cookies: { cc_csrf_token: 'test-csrf-token' },
    headers: { 'x-csrf-token': 'test-csrf-token' },
    ip: '127.0.0.1',
    server: fastifyStub,
    user: user ?? null,
  } as any;

  const res = {
    setCookie: vi.fn(),
    clearCookie: vi.fn(),
  } as any;

  const ctx = {
    req,
    res,
    user: user ?? null,
    prisma: testDb,
    fastify: fastifyStub as any,
    redis: redisMock,
  } as any;

  return { caller: appRouter.createCaller(ctx), ctx };
}

const maybeDescribe = process.env.SKIP_DB_TEST_SETUP === 'true' ? describe.skip : describe;

maybeDescribe('tRPC API Integration (real DB)', () => {
  let supervisor: any;
  let supervisorCaller: ReturnType<typeof createCaller>['caller'];

  beforeAll(() => {
    process.env.NODE_ENV = 'test';
  });

  beforeEach(async () => {
    supervisor = await createTestUser({
      role: UserRole.SUPERVISOR,
      email: 'supervisor@example.com',
      username: 'supervisor',
      password: 'password123',
    });
    supervisorCaller = createCaller(toCtxUser(supervisor)).caller;
    redisMock.setSession.mockClear();
  });

  describe('dashboard', () => {
    it('returns overview statistics for supervisor', async () => {
      const campaign = await createTestCampaign({ organizationId: supervisor.organizationId, active: true });
      await createTestCall({
        agentId: supervisor.id,
        campaignId: campaign.id,
        organizationId: supervisor.organizationId,
        status: CallStatus.IN_PROGRESS,
      });
      await createTestCall({
        agentId: supervisor.id,
        campaignId: campaign.id,
        organizationId: supervisor.organizationId,
        status: CallStatus.COMPLETED,
        duration: 240,
      });

      const overview = await supervisorCaller.dashboard.getOverview();
      expect(overview.callStats.totalCalls).toBeGreaterThanOrEqual(2);
      expect(overview.teamStatus.members.length).toBeGreaterThan(0);
    });

    it('requires authentication', async () => {
      const { caller } = createCaller();
      await expect(caller.dashboard.getOverview()).rejects.toThrow('UNAUTHORIZED');
    });
  });

  describe('calls', () => {
    it('lists recent calls', async () => {
      const campaign = await createTestCampaign({ organizationId: supervisor.organizationId, active: true });
      await createTestCall({
        agentId: supervisor.id,
        campaignId: campaign.id,
        organizationId: supervisor.organizationId,
        status: CallStatus.IN_PROGRESS,
      });

      const result = await supervisorCaller.callApi.list({ limit: 5, offset: 0 });
      expect(result.calls.length).toBeGreaterThan(0);
      expect(result.total).toBeGreaterThan(0);
    });
  });
});
