import path from 'node:path';
import crypto from 'node:crypto';
import { config as loadEnv } from 'dotenv';
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { UserRole, CallStatus, UserStatus } from '@prisma/client';
import { TRPCError } from '@trpc/server';
import { appRouter } from '../../../server/trpc/app.router';
import { redisService } from '../../../server/services/redis-service';
import { testDb, createTestUser, createTestCampaign, createTestCall } from '../../setup';

loadEnv({ path: path.resolve(__dirname, '../../..', '.env'), override: true });

// Setup test keys
const { privateKey, publicKey } = crypto.generateKeyPairSync('ed25519', {
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
  publicKeyEncoding: { type: 'spki', format: 'pem' },
});
process.env.AUTH_PRIVATE_KEY = privateKey;
process.env.AUTH_PUBLIC_KEY = publicKey;

// TextEncoder polyfill
if (typeof global.TextEncoder === "undefined") {
  const { TextEncoder, TextDecoder } = require("util");
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;
}

// Mock Redis service
const redisMock = {
  setSession: vi.fn().mockResolvedValue(undefined),
  getCounter: vi.fn().mockResolvedValue(0),
  getQueueLength: vi.fn().mockResolvedValue(0),
  get: vi.fn().mockResolvedValue(null),
  set: vi.fn().mockResolvedValue('OK'),
  del: vi.fn().mockResolvedValue(1),
  ping: vi.fn().mockResolvedValue('PONG'),
  quit: vi.fn().mockResolvedValue('OK'),
};

vi.spyOn(redisService, 'setSession').mockImplementation(redisMock.setSession as any);

// Mock Fastify instance
const fastifyStub = {
  log: console,
  databaseService: { client: testDb },
  redisService: redisMock,
};

// Helper to convert DB user to context user
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

// tRPC caller factory
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

// Conditional test runner based on environment
const maybeDescribe = process.env.SKIP_DB_TEST_SETUP === 'true' ? describe.skip : describe;

maybeDescribe('Analytics Router Integration Tests', () => {
  let supervisor: any;
  let agent: any;
  let supervisorCaller: ReturnType<typeof createCaller>['caller'];
  let agentCaller: ReturnType<typeof createCaller>['caller'];
  let unauthenticatedCaller: ReturnType<typeof createCaller>['caller'];

  beforeAll(() => {
    process.env.NODE_ENV = 'test';
  });

  beforeEach(async () => {
    // Create test users
    supervisor = await createTestUser({
      role: UserRole.SUPERVISOR,
      email: 'supervisor@analytics.test',
      username: 'analytics_supervisor',
      password: 'test123',
      firstName: 'Test',
      lastName: 'Supervisor',
      status: UserStatus.AVAILABLE,
    });

    agent = await createTestUser({
      role: UserRole.AGENT,
      email: 'agent@analytics.test',
      username: 'analytics_agent',
      password: 'test123',
      firstName: 'Test',
      lastName: 'Agent',
      status: UserStatus.AVAILABLE,
      organizationId: supervisor.organizationId,
    });

    // Create callers
    supervisorCaller = createCaller(toCtxUser(supervisor)).caller;
    agentCaller = createCaller(toCtxUser(agent)).caller;
    unauthenticatedCaller = createCaller().caller;

    // Clear mock calls
    Object.values(redisMock).forEach(mock => {
      if (typeof mock === 'function') mock.mockClear();
    });
  });

  describe('getCallAnalytics', () => {
    it('should return call analytics for supervisor with default parameters', async () => {
      // Create test campaigns and calls
      const campaign = await createTestCampaign({
        organizationId: supervisor.organizationId,
        active: true,
        name: 'Analytics Test Campaign',
      });

      // Create various call types
      const now = new Date();
      const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);

      await Promise.all([
        createTestCall({
          agentId: agent.id,
          campaignId: campaign.id,
          organizationId: supervisor.organizationId,
          status: CallStatus.COMPLETED,
          direction: 'INBOUND',
          duration: 120,
          startTime: yesterday,
        }),
        createTestCall({
          agentId: agent.id,
          campaignId: campaign.id,
          organizationId: supervisor.organizationId,
          status: CallStatus.COMPLETED,
          direction: 'OUTBOUND',
          duration: 180,
          startTime: now,
        }),
        createTestCall({
          agentId: agent.id,
          campaignId: campaign.id,
          organizationId: supervisor.organizationId,
          status: CallStatus.CANCELED,
          direction: 'INBOUND',
          startTime: now,
        }),
      ]);

      const result = await supervisorCaller.analytics.getCallAnalytics({});

      expect(result).toBeDefined();
      expect(result.summary).toBeDefined();
      expect(result.data).toBeDefined();
      expect(Array.isArray(result.data)).toBe(true);

      expect(result.summary.totalCalls).toBeGreaterThanOrEqual(3);
      expect(result.summary.totalInbound).toBeGreaterThanOrEqual(2);
      expect(result.summary.totalOutbound).toBeGreaterThanOrEqual(1);
      expect(result.summary.totalCompleted).toBeGreaterThanOrEqual(2);
      expect(result.summary.totalAbandoned).toBeGreaterThanOrEqual(1);
    });

    it('should filter calls by date range', async () => {
      const campaign = await createTestCampaign({
        organizationId: supervisor.organizationId,
        active: true,
      });

      const oldDate = new Date('2023-01-01');
      const recentDate = new Date();

      // Create old call (should be filtered out)
      await createTestCall({
        agentId: agent.id,
        campaignId: campaign.id,
        organizationId: supervisor.organizationId,
        status: CallStatus.COMPLETED,
        startTime: oldDate,
      });

      // Create recent call (should be included)
      await createTestCall({
        agentId: agent.id,
        campaignId: campaign.id,
        organizationId: supervisor.organizationId,
        status: CallStatus.COMPLETED,
        startTime: recentDate,
      });

      const startDate = new Date(recentDate.getTime() - 1000); // 1 second before recent call
      const endDate = new Date(recentDate.getTime() + 1000); // 1 second after recent call

      const result = await supervisorCaller.analytics.getCallAnalytics({
        startDate,
        endDate,
      });

      expect(result.summary.totalCalls).toBe(1);
    });

    it('should group calls by different periods', async () => {
      const campaign = await createTestCampaign({
        organizationId: supervisor.organizationId,
        active: true,
      });

      await createTestCall({
        agentId: agent.id,
        campaignId: campaign.id,
        organizationId: supervisor.organizationId,
        status: CallStatus.COMPLETED,
        startTime: new Date(),
      });

      // Test different grouping options
      for (const groupBy of ['hour', 'day', 'week', 'month']) {
        const result = await supervisorCaller.analytics.getCallAnalytics({
          groupBy: groupBy as any,
        });

        expect(result.data.length).toBeGreaterThan(0);
        expect(result.data[0]).toHaveProperty('period');
        expect(result.data[0]).toHaveProperty('total');
        expect(result.data[0]).toHaveProperty('completionRate');
      }
    });

    it('should restrict agent to their own calls', async () => {
      const campaign = await createTestCampaign({
        organizationId: supervisor.organizationId,
        active: true,
      });

      // Create call for agent
      await createTestCall({
        agentId: agent.id,
        campaignId: campaign.id,
        organizationId: supervisor.organizationId,
        status: CallStatus.COMPLETED,
      });

      // Create call for supervisor (should not be visible to agent)
      await createTestCall({
        agentId: supervisor.id,
        campaignId: campaign.id,
        organizationId: supervisor.organizationId,
        status: CallStatus.COMPLETED,
      });

      const agentResult = await agentCaller.analytics.getCallAnalytics({});
      const supervisorResult = await supervisorCaller.analytics.getCallAnalytics({});

      expect(agentResult.summary.totalCalls).toBe(1);
      expect(supervisorResult.summary.totalCalls).toBeGreaterThanOrEqual(2);
    });

    it('should require authentication', async () => {
      await expect(
        unauthenticatedCaller.analytics.getCallAnalytics({})
      ).rejects.toThrow('UNAUTHORIZED');
    });

    it('should validate input parameters', async () => {
      // Test invalid groupBy parameter
      await expect(
        supervisorCaller.analytics.getCallAnalytics({
          groupBy: 'invalid' as any,
        })
      ).rejects.toThrow();

      // Test valid parameters
      const result = await supervisorCaller.analytics.getCallAnalytics({
        startDate: new Date('2023-01-01'),
        endDate: new Date(),
        groupBy: 'day',
      });

      expect(result).toBeDefined();
    });
  });

  describe('getAgentAnalytics', () => {
    it('should return agent analytics for supervisor', async () => {
      const campaign = await createTestCampaign({
        organizationId: supervisor.organizationId,
        active: true,
      });

      await Promise.all([
        createTestCall({
          agentId: agent.id,
          campaignId: campaign.id,
          organizationId: supervisor.organizationId,
          status: CallStatus.COMPLETED,
          duration: 150,
          direction: 'INBOUND',
        }),
        createTestCall({
          agentId: agent.id,
          campaignId: campaign.id,
          organizationId: supervisor.organizationId,
          status: CallStatus.COMPLETED,
          duration: 200,
          direction: 'OUTBOUND',
        }),
      ]);

      const result = await supervisorCaller.analytics.getAgentAnalytics({});

      expect(result).toBeDefined();
      expect(result.agents).toBeDefined();
      expect(Array.isArray(result.agents)).toBe(true);
      expect(result.agents.length).toBeGreaterThan(0);

      const agentMetrics = result.agents.find(a => a.id === agent.id);
      expect(agentMetrics).toBeDefined();
      expect(agentMetrics?.totalCalls).toBeGreaterThanOrEqual(2);
      expect(agentMetrics?.completedCalls).toBeGreaterThanOrEqual(2);
      expect(agentMetrics?.avgDuration).toBeGreaterThan(0);
    });

    it('should filter by specific agent ID', async () => {
      const campaign = await createTestCampaign({
        organizationId: supervisor.organizationId,
        active: true,
      });

      await createTestCall({
        agentId: agent.id,
        campaignId: campaign.id,
        organizationId: supervisor.organizationId,
        status: CallStatus.COMPLETED,
      });

      const result = await supervisorCaller.analytics.getAgentAnalytics({
        agentId: agent.id,
      });

      expect(result.agents.length).toBe(1);
      expect(result.agents[0].id).toBe(agent.id);
    });

    it('should require supervisor role', async () => {
      await expect(
        agentCaller.analytics.getAgentAnalytics({})
      ).rejects.toThrow('FORBIDDEN');
    });

    it('should require authentication', async () => {
      await expect(
        unauthenticatedCaller.analytics.getAgentAnalytics({})
      ).rejects.toThrow('UNAUTHORIZED');
    });

    it('should validate date range parameters', async () => {
      const result = await supervisorCaller.analytics.getAgentAnalytics({
        startDate: new Date('2023-01-01'),
        endDate: new Date(),
      });

      expect(result).toBeDefined();
      expect(result.agents).toBeDefined();
    });
  });

  describe('getQueueAnalytics', () => {
    it('should return queue analytics with current and historical data', async () => {
      // Create some queued and completed calls
      const campaign = await createTestCampaign({
        organizationId: supervisor.organizationId,
        active: true,
      });

      await Promise.all([
        createTestCall({
          organizationId: supervisor.organizationId,
          status: CallStatus.QUEUED,
          startTime: new Date(),
        }),
        createTestCall({
          organizationId: supervisor.organizationId,
          status: CallStatus.COMPLETED,
          startTime: new Date(),
        }),
        createTestCall({
          organizationId: supervisor.organizationId,
          status: CallStatus.CANCELED,
          startTime: new Date(),
        }),
      ]);

      const result = await supervisorCaller.analytics.getQueueAnalytics({});

      expect(result).toBeDefined();
      expect(result.current).toBeDefined();
      expect(result.historical).toBeDefined();

      expect(result.current).toHaveProperty('inQueue');
      expect(result.current).toHaveProperty('longestWait');
      expect(result.current).toHaveProperty('avgWait');

      expect(result.historical).toHaveProperty('totalOffered');
      expect(result.historical).toHaveProperty('totalAnswered');
      expect(result.historical).toHaveProperty('totalAbandoned');
      expect(result.historical).toHaveProperty('abandonRate');
      expect(result.historical).toHaveProperty('serviceLevel');
    });

    it('should filter by time period', async () => {
      for (const period of ['hour', 'day', 'week']) {
        const result = await supervisorCaller.analytics.getQueueAnalytics({
          period: period as any,
        });

        expect(result).toBeDefined();
        expect(typeof result.current.inQueue).toBe('number');
        expect(typeof result.historical.serviceLevel).toBe('number');
      }
    });

    it('should require authentication', async () => {
      await expect(
        unauthenticatedCaller.analytics.getQueueAnalytics({})
      ).rejects.toThrow('UNAUTHORIZED');
    });

    it('should validate period parameter', async () => {
      await expect(
        supervisorCaller.analytics.getQueueAnalytics({
          period: 'invalid' as any,
        })
      ).rejects.toThrow();
    });
  });

  describe('getCampaignAnalytics', () => {
    it('should return campaign analytics', async () => {
      const campaign = await createTestCampaign({
        organizationId: supervisor.organizationId,
        active: true,
        name: 'Test Campaign Analytics',
      });

      await Promise.all([
        createTestCall({
          campaignId: campaign.id,
          organizationId: supervisor.organizationId,
          status: CallStatus.COMPLETED,
          duration: 120,
        }),
        createTestCall({
          campaignId: campaign.id,
          organizationId: supervisor.organizationId,
          status: CallStatus.NO_ANSWER,
        }),
      ]);

      const result = await supervisorCaller.analytics.getCampaignAnalytics({});

      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);

      const campaignMetrics = result.find(c => c.campaignId === campaign.id);
      expect(campaignMetrics).toBeDefined();
      expect(campaignMetrics?.campaignName).toBe('Test Campaign Analytics');
      expect(campaignMetrics?.metrics).toBeDefined();
      expect(campaignMetrics?.outcomes).toBeDefined();
    });

    it('should filter by campaign ID', async () => {
      const campaign = await createTestCampaign({
        organizationId: supervisor.organizationId,
        active: true,
      });

      await createTestCall({
        campaignId: campaign.id,
        organizationId: supervisor.organizationId,
        status: CallStatus.COMPLETED,
      });

      const result = await supervisorCaller.analytics.getCampaignAnalytics({
        campaignId: campaign.id,
      });

      expect(result.length).toBe(1);
      expect(result[0].campaignId).toBe(campaign.id);
    });

    it('should require authentication', async () => {
      await expect(
        unauthenticatedCaller.analytics.getCampaignAnalytics({})
      ).rejects.toThrow('UNAUTHORIZED');
    });
  });

  describe('getRealtimeMetrics', () => {
    it('should return real-time metrics for all users', async () => {
      const result = await supervisorCaller.analytics.getRealtimeMetrics();

      expect(result).toBeDefined();
      expect(result.calls).toBeDefined();
      expect(result.agents).toBeDefined();
      expect(result.performance).toBeDefined();

      expect(result.calls).toHaveProperty('active');
      expect(result.calls).toHaveProperty('queued');
      expect(result.calls).toHaveProperty('offered');
      expect(result.calls).toHaveProperty('abandoned');

      expect(result.agents).toHaveProperty('available');
      expect(result.agents).toHaveProperty('busy');
      expect(result.agents).toHaveProperty('onBreak');
      expect(result.agents).toHaveProperty('offline');

      expect(result.performance).toHaveProperty('serviceLevel');
      expect(result.performance).toHaveProperty('avgHandleTime');
      expect(result.performance).toHaveProperty('avgWaitTime');
    });

    it('should filter data for non-supervisor users', async () => {
      const supervisorResult = await supervisorCaller.analytics.getRealtimeMetrics();
      const agentResult = await agentCaller.analytics.getRealtimeMetrics();

      expect(supervisorResult).toBeDefined();
      expect(agentResult).toBeDefined();

      // Both should have the same structure but agent data might be filtered
      expect(supervisorResult.calls).toBeDefined();
      expect(agentResult.calls).toBeDefined();
    });

    it('should require authentication', async () => {
      await expect(
        unauthenticatedCaller.analytics.getRealtimeMetrics()
      ).rejects.toThrow('UNAUTHORIZED');
    });
  });

  describe('getSentimentAnalytics', () => {
    it('should return sentiment analytics', async () => {
      // Create test transcript with sentiment data
      const call = await createTestCall({
        organizationId: supervisor.organizationId,
        status: CallStatus.COMPLETED,
      });

      await testDb.transcript.create({
        data: {
          callId: call.id,
          content: 'Test transcript content',
          sentiment: { overall: 'positive' },
          language: 'en',
          createdAt: new Date(),
        },
      });

      const result = await supervisorCaller.analytics.getSentimentAnalytics({});

      expect(result).toBeDefined();
      expect(result.distribution).toBeDefined();
      expect(result.total).toBeGreaterThanOrEqual(1);
      expect(typeof result.averageSentiment).toBe('number');

      expect(result.distribution).toHaveProperty('positive');
      expect(result.distribution).toHaveProperty('neutral');
      expect(result.distribution).toHaveProperty('negative');
    });

    it('should filter by date range', async () => {
      const result = await supervisorCaller.analytics.getSentimentAnalytics({
        startDate: new Date('2023-01-01'),
        endDate: new Date(),
      });

      expect(result).toBeDefined();
      expect(typeof result.total).toBe('number');
    });

    it('should require authentication', async () => {
      await expect(
        unauthenticatedCaller.analytics.getSentimentAnalytics({})
      ).rejects.toThrow('UNAUTHORIZED');
    });
  });

  describe('getQualityMetrics', () => {
    it('should return quality metrics', async () => {
      const campaign = await createTestCampaign({
        organizationId: supervisor.organizationId,
        active: true,
      });

      await Promise.all([
        createTestCall({
          agentId: agent.id,
          campaignId: campaign.id,
          organizationId: supervisor.organizationId,
          status: CallStatus.COMPLETED,
          duration: 300, // Good duration
        }),
        createTestCall({
          agentId: agent.id,
          campaignId: campaign.id,
          organizationId: supervisor.organizationId,
          status: CallStatus.COMPLETED,
          duration: 30, // Short duration
        }),
      ]);

      const result = await supervisorCaller.analytics.getQualityMetrics({});

      expect(result).toBeDefined();
      expect(typeof result.averageScore).toBe('number');
      expect(typeof result.totalCalls).toBe('number');
      expect(result.scoreDistribution).toBeDefined();

      expect(result.scoreDistribution).toHaveProperty('excellent');
      expect(result.scoreDistribution).toHaveProperty('good');
      expect(result.scoreDistribution).toHaveProperty('average');
      expect(result.scoreDistribution).toHaveProperty('poor');
    });

    it('should filter by agent ID', async () => {
      const result = await supervisorCaller.analytics.getQualityMetrics({
        agentId: agent.id,
      });

      expect(result).toBeDefined();
      expect(typeof result.averageScore).toBe('number');
    });

    it('should require authentication', async () => {
      await expect(
        unauthenticatedCaller.analytics.getQualityMetrics({})
      ).rejects.toThrow('UNAUTHORIZED');
    });
  });

  describe('exportAnalytics', () => {
    it('should generate export for supervisor', async () => {
      const result = await supervisorCaller.analytics.exportAnalytics({
        type: 'calls',
        format: 'csv',
        startDate: new Date('2023-01-01'),
        endDate: new Date(),
      });

      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.downloadUrl).toBeDefined();
      expect(result.expiresAt).toBeDefined();
      expect(result.downloadUrl).toContain('calls');
      expect(result.downloadUrl).toContain('.csv');
    });

    it('should support different export types and formats', async () => {
      const types = ['calls', 'agents', 'campaigns', 'queues'] as const;
      const formats = ['csv', 'json', 'xlsx'] as const;

      for (const type of types) {
        for (const format of formats) {
          const result = await supervisorCaller.analytics.exportAnalytics({
            type,
            format,
            startDate: new Date('2023-01-01'),
            endDate: new Date(),
          });

          expect(result.success).toBe(true);
          expect(result.downloadUrl).toContain(type);
          expect(result.downloadUrl).toContain(format);
        }
      }
    });

    it('should require supervisor role', async () => {
      await expect(
        agentCaller.analytics.exportAnalytics({
          type: 'calls',
          format: 'csv',
          startDate: new Date('2023-01-01'),
          endDate: new Date(),
        })
      ).rejects.toThrow('FORBIDDEN');
    });

    it('should require authentication', async () => {
      await expect(
        unauthenticatedCaller.analytics.exportAnalytics({
          type: 'calls',
          format: 'csv',
          startDate: new Date('2023-01-01'),
          endDate: new Date(),
        })
      ).rejects.toThrow('UNAUTHORIZED');
    });

    it('should validate required parameters', async () => {
      await expect(
        supervisorCaller.analytics.exportAnalytics({
          type: 'invalid' as any,
          format: 'csv',
          startDate: new Date('2023-01-01'),
          endDate: new Date(),
        })
      ).rejects.toThrow();

      await expect(
        supervisorCaller.analytics.exportAnalytics({
          type: 'calls',
          format: 'invalid' as any,
          startDate: new Date('2023-01-01'),
          endDate: new Date(),
        })
      ).rejects.toThrow();
    });
  });

  describe('Performance and Edge Cases', () => {
    it('should handle empty data sets gracefully', async () => {
      // Test with no data
      const callResult = await supervisorCaller.analytics.getCallAnalytics({});
      expect(callResult.summary.totalCalls).toBe(0);
      expect(callResult.data).toEqual([]);

      const agentResult = await supervisorCaller.analytics.getAgentAnalytics({});
      expect(agentResult.agents).toEqual([]);

      const sentimentResult = await supervisorCaller.analytics.getSentimentAnalytics({});
      expect(sentimentResult.total).toBe(0);
    });

    it('should handle large date ranges', async () => {
      const result = await supervisorCaller.analytics.getCallAnalytics({
        startDate: new Date('2020-01-01'),
        endDate: new Date('2030-12-31'),
      });

      expect(result).toBeDefined();
      expect(Array.isArray(result.data)).toBe(true);
    });

    it('should calculate metrics correctly with mixed data', async () => {
      const campaign = await createTestCampaign({
        organizationId: supervisor.organizationId,
        active: true,
      });

      // Create varied call data
      await Promise.all([
        createTestCall({
          agentId: agent.id,
          campaignId: campaign.id,
          organizationId: supervisor.organizationId,
          status: CallStatus.COMPLETED,
          direction: 'INBOUND',
          duration: 0, // Edge case: zero duration
        }),
        createTestCall({
          agentId: agent.id,
          campaignId: campaign.id,
          organizationId: supervisor.organizationId,
          status: CallStatus.COMPLETED,
          direction: 'OUTBOUND',
          duration: null, // Edge case: null duration
        }),
        createTestCall({
          agentId: agent.id,
          campaignId: campaign.id,
          organizationId: supervisor.organizationId,
          status: CallStatus.IN_PROGRESS,
          direction: 'INBOUND',
          duration: 999999, // Edge case: very long duration
        }),
      ]);

      const result = await supervisorCaller.analytics.getCallAnalytics({});

      expect(result.summary.totalCalls).toBeGreaterThanOrEqual(3);
      expect(result.summary.avgDuration).toBeGreaterThanOrEqual(0);
    });
  });
});