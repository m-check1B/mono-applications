import { describe, expect, it, vi, beforeEach } from 'vitest';
import { TRPCError } from '@trpc/server';
import { analyticsRouter } from '../../server/trpc/routers/analytics';
import { UserRole, CallStatus } from '@prisma/client';

// Mock Prisma client
const mockPrisma = {
  call: {
    findMany: vi.fn(),
    count: vi.fn(),
  },
  user: {
    findMany: vi.fn(),
    count: vi.fn(),
  },
  campaign: {
    findMany: vi.fn(),
  },
  transcript: {
    findMany: vi.fn(),
  },
};

// Mock Redis
const mockRedis = {
  get: vi.fn(),
  set: vi.fn(),
  del: vi.fn(),
};

// Create tRPC caller with mocked context
function createCaller(user?: any) {
  const ctx = {
    user: user || null,
    prisma: mockPrisma,
    redis: mockRedis,
  };

  return analyticsRouter.createCaller(ctx as any);
}

// Test users
const mockSupervisor = {
  id: 'supervisor-123',
  sub: 'supervisor-123',
  email: 'supervisor@test.com',
  role: 'supervisor',
  roles: ['supervisor'],
  organizationId: 'org-123',
  name: 'Test Supervisor',
};

const mockAgent = {
  id: 'agent-123',
  sub: 'agent-123',
  email: 'agent@test.com',
  role: 'agent',
  roles: ['agent'],
  organizationId: 'org-123',
  name: 'Test Agent',
};

describe('Analytics Router Unit Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getCallAnalytics', () => {
    it('should return call analytics for authenticated user', async () => {
      const mockCalls = [
        {
          id: 'call-1',
          status: 'COMPLETED',
          direction: 'INBOUND',
          duration: 120,
          startTime: new Date('2024-01-01T10:00:00Z'),
          endTime: new Date('2024-01-01T10:02:00Z'),
          agentId: 'agent-123',
        },
        {
          id: 'call-2',
          status: 'CANCELED',
          direction: 'OUTBOUND',
          duration: null,
          startTime: new Date('2024-01-01T11:00:00Z'),
          endTime: null,
          agentId: 'agent-123',
        },
      ];

      mockPrisma.call.findMany.mockResolvedValue(mockCalls);

      const caller = createCaller(mockSupervisor);
      const result = await caller.getCallAnalytics({});

      expect(result).toBeDefined();
      expect(result.summary).toBeDefined();
      expect(result.data).toBeDefined();
      expect(Array.isArray(result.data)).toBe(true);

      expect(result.summary.totalCalls).toBe(2);
      expect(result.summary.totalInbound).toBe(1);
      expect(result.summary.totalOutbound).toBe(1);
      expect(result.summary.totalCompleted).toBe(1);
      expect(result.summary.totalAbandoned).toBe(1);

      expect(mockPrisma.call.findMany).toHaveBeenCalledWith({
        where: expect.objectContaining({
          organizationId: 'org-123',
        }),
        select: expect.objectContaining({
          id: true,
          status: true,
          direction: true,
          duration: true,
          startTime: true,
          endTime: true,
          agentId: true,
        }),
      });
    });

    it('should filter calls by agentId for non-supervisor users', async () => {
      mockPrisma.call.findMany.mockResolvedValue([]);

      const caller = createCaller(mockAgent);
      await caller.getCallAnalytics({});

      expect(mockPrisma.call.findMany).toHaveBeenCalledWith({
        where: expect.objectContaining({
          organizationId: 'org-123',
          agentId: 'agent-123',
        }),
        select: expect.any(Object),
      });
    });

    it('should throw UNAUTHORIZED for unauthenticated user', async () => {
      const caller = createCaller();

      await expect(caller.getCallAnalytics({})).rejects.toThrow('UNAUTHORIZED');
    });

    it('should validate groupBy parameter', async () => {
      mockPrisma.call.findMany.mockResolvedValue([]);

      const caller = createCaller(mockSupervisor);

      // Valid groupBy values should work
      await expect(caller.getCallAnalytics({ groupBy: 'day' })).resolves.toBeDefined();
      await expect(caller.getCallAnalytics({ groupBy: 'hour' })).resolves.toBeDefined();
      await expect(caller.getCallAnalytics({ groupBy: 'week' })).resolves.toBeDefined();
      await expect(caller.getCallAnalytics({ groupBy: 'month' })).resolves.toBeDefined();

      // Invalid groupBy should throw
      await expect(caller.getCallAnalytics({ groupBy: 'invalid' as any })).rejects.toThrow();
    });

    it('should handle date filtering', async () => {
      mockPrisma.call.findMany.mockResolvedValue([]);

      const caller = createCaller(mockSupervisor);
      const startDate = new Date('2024-01-01');
      const endDate = new Date('2024-01-31');

      await caller.getCallAnalytics({ startDate, endDate });

      expect(mockPrisma.call.findMany).toHaveBeenCalledWith({
        where: expect.objectContaining({
          startTime: {
            gte: startDate,
            lte: endDate,
          },
        }),
        select: expect.any(Object),
      });
    });

    it('should calculate completion rate correctly', async () => {
      const mockCalls = [
        { status: 'COMPLETED', direction: 'INBOUND', duration: 120, startTime: new Date(), endTime: new Date(), agentId: 'agent-1', id: '1' },
        { status: 'COMPLETED', direction: 'INBOUND', duration: 150, startTime: new Date(), endTime: new Date(), agentId: 'agent-1', id: '2' },
        { status: 'CANCELED', direction: 'INBOUND', duration: null, startTime: new Date(), endTime: null, agentId: 'agent-1', id: '3' },
        { status: 'CANCELED', direction: 'INBOUND', duration: null, startTime: new Date(), endTime: null, agentId: 'agent-1', id: '4' },
      ];

      mockPrisma.call.findMany.mockResolvedValue(mockCalls);

      const caller = createCaller(mockSupervisor);
      const result = await caller.getCallAnalytics({});

      expect(result.summary.totalCalls).toBe(4);
      expect(result.summary.totalCompleted).toBe(2);
      expect(result.summary.totalAbandoned).toBe(2);
      expect(result.summary.avgDuration).toBe(135); // (120 + 150) / 2
    });
  });

  describe('getAgentAnalytics', () => {
    it('should return agent analytics for supervisor', async () => {
      const mockAgents = [
        {
          id: 'agent-1',
          firstName: 'John',
          lastName: 'Doe',
          agentCalls: [
            { status: 'COMPLETED', duration: 120, direction: 'INBOUND', startTime: new Date(), endTime: new Date(), id: 'call-1' },
            { status: 'COMPLETED', duration: 180, direction: 'OUTBOUND', startTime: new Date(), endTime: new Date(), id: 'call-2' },
          ],
        },
      ];

      mockPrisma.user.findMany.mockResolvedValue(mockAgents);

      const caller = createCaller(mockSupervisor);
      const result = await caller.getAgentAnalytics({});

      expect(result).toBeDefined();
      expect(result.agents).toBeDefined();
      expect(Array.isArray(result.agents)).toBe(true);
      expect(result.agents.length).toBe(1);

      const agent = result.agents[0];
      expect(agent.id).toBe('agent-1');
      expect(agent.name).toBe('John Doe');
      expect(agent.totalCalls).toBe(2);
      expect(agent.completedCalls).toBe(2);
      expect(agent.avgDuration).toBe(150); // (120 + 180) / 2
      expect(agent.completionRate).toBe(100); // 2/2 * 100
    });

    it('should require supervisor role', async () => {
      const caller = createCaller(mockAgent);

      await expect(caller.getAgentAnalytics({})).rejects.toThrow('FORBIDDEN');
    });

    it('should throw UNAUTHORIZED for unauthenticated user', async () => {
      const caller = createCaller();

      await expect(caller.getAgentAnalytics({})).rejects.toThrow('UNAUTHORIZED');
    });

    it('should filter by agentId when provided', async () => {
      mockPrisma.user.findMany.mockResolvedValue([]);

      const caller = createCaller(mockSupervisor);
      await caller.getAgentAnalytics({ agentId: 'specific-agent-id' });

      expect(mockPrisma.user.findMany).toHaveBeenCalledWith({
        where: expect.objectContaining({
          id: 'specific-agent-id',
        }),
        include: expect.any(Object),
      });
    });
  });

  describe('getQueueAnalytics', () => {
    it('should return queue analytics', async () => {
      mockPrisma.call.findMany
        .mockResolvedValueOnce([{ id: 'queued-1' }]) // queued calls
        .mockResolvedValueOnce([{ id: 'answered-1' }, { id: 'answered-2' }]) // answered calls
        .mockResolvedValueOnce([{ id: 'abandoned-1' }]); // abandoned calls

      const caller = createCaller(mockSupervisor);
      const result = await caller.getQueueAnalytics({});

      expect(result).toBeDefined();
      expect(result.current).toBeDefined();
      expect(result.historical).toBeDefined();

      expect(result.current.inQueue).toBe(1);
      expect(result.historical.totalOffered).toBe(4); // 1 + 2 + 1
      expect(result.historical.totalAnswered).toBe(2);
      expect(result.historical.totalAbandoned).toBe(1);
      expect(result.historical.abandonRate).toBe(25); // 1/4 * 100
    });

    it('should handle different time periods', async () => {
      mockPrisma.call.findMany.mockResolvedValue([]);

      const caller = createCaller(mockSupervisor);

      await caller.getQueueAnalytics({ period: 'hour' });
      await caller.getQueueAnalytics({ period: 'day' });
      await caller.getQueueAnalytics({ period: 'week' });

      expect(mockPrisma.call.findMany).toHaveBeenCalledTimes(9); // 3 calls per period
    });

    it('should validate period parameter', async () => {
      const caller = createCaller(mockSupervisor);

      await expect(caller.getQueueAnalytics({ period: 'invalid' as any })).rejects.toThrow();
    });

    it('should throw UNAUTHORIZED for unauthenticated user', async () => {
      const caller = createCaller();

      await expect(caller.getQueueAnalytics({})).rejects.toThrow('UNAUTHORIZED');
    });
  });

  describe('getCampaignAnalytics', () => {
    it('should return campaign analytics', async () => {
      const mockCampaigns = [
        {
          id: 'campaign-1',
          name: 'Test Campaign',
          type: 'OUTBOUND',
          active: true,
          calls: [
            { status: 'COMPLETED', duration: 120 },
            { status: 'NO_ANSWER', duration: null },
            { status: 'COMPLETED', duration: 180 },
          ],
        },
      ];

      mockPrisma.campaign.findMany.mockResolvedValue(mockCampaigns);

      const caller = createCaller(mockSupervisor);
      const result = await caller.getCampaignAnalytics({});

      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBe(1);

      const campaign = result[0];
      expect(campaign.campaignId).toBe('campaign-1');
      expect(campaign.campaignName).toBe('Test Campaign');
      expect(campaign.metrics.totalCalls).toBe(3);
      expect(campaign.metrics.connectedCalls).toBe(2); // excluding NO_ANSWER
      expect(campaign.metrics.completedCalls).toBe(2);
      expect(campaign.metrics.connectRate).toBe(67); // 2/3 * 100, rounded
      expect(campaign.metrics.avgCallDuration).toBe(150); // (120 + 180) / 2
    });

    it('should filter by campaignId when provided', async () => {
      mockPrisma.campaign.findMany.mockResolvedValue([]);

      const caller = createCaller(mockSupervisor);
      await caller.getCampaignAnalytics({ campaignId: 'specific-campaign-id' });

      expect(mockPrisma.campaign.findMany).toHaveBeenCalledWith({
        where: expect.objectContaining({
          id: 'specific-campaign-id',
        }),
        include: expect.any(Object),
      });
    });

    it('should throw UNAUTHORIZED for unauthenticated user', async () => {
      const caller = createCaller();

      await expect(caller.getCampaignAnalytics({})).rejects.toThrow('UNAUTHORIZED');
    });
  });

  describe('getRealtimeMetrics', () => {
    it('should return real-time metrics', async () => {
      mockPrisma.call.count
        .mockResolvedValueOnce(5) // active calls
        .mockResolvedValueOnce(3); // queued calls

      mockPrisma.user.count
        .mockResolvedValueOnce(10) // available agents
        .mockResolvedValueOnce(2); // on break agents

      const caller = createCaller(mockSupervisor);
      const result = await caller.getRealtimeMetrics();

      expect(result).toBeDefined();
      expect(result.calls.active).toBe(5);
      expect(result.calls.queued).toBe(3);
      expect(result.agents.available).toBe(10);
      expect(result.agents.busy).toBe(5); // same as active calls
      expect(result.agents.onBreak).toBe(2);

      expect(typeof result.performance.serviceLevel).toBe('number');
      expect(typeof result.performance.avgHandleTime).toBe('number');
      expect(typeof result.performance.avgWaitTime).toBe('number');
    });

    it('should filter data for non-supervisor users', async () => {
      mockPrisma.call.count.mockResolvedValue(1);
      mockPrisma.user.count.mockResolvedValue(1);

      const supervisorCaller = createCaller(mockSupervisor);
      const agentCaller = createCaller(mockAgent);

      const supervisorResult = await supervisorCaller.getRealtimeMetrics();
      const agentResult = await agentCaller.getRealtimeMetrics();

      // Verify both calls were made with different filters
      expect(mockPrisma.call.count).toHaveBeenCalledWith({
        where: expect.objectContaining({
          organizationId: 'org-123',
          status: 'IN_PROGRESS',
        }),
      });

      expect(mockPrisma.call.count).toHaveBeenCalledWith({
        where: expect.objectContaining({
          organizationId: 'org-123',
          status: 'IN_PROGRESS',
          agentId: 'agent-123',
        }),
      });
    });

    it('should throw UNAUTHORIZED for unauthenticated user', async () => {
      const caller = createCaller();

      await expect(caller.getRealtimeMetrics()).rejects.toThrow('UNAUTHORIZED');
    });
  });

  describe('getSentimentAnalytics', () => {
    it('should return sentiment analytics', async () => {
      const mockTranscripts = [
        { id: '1', sentiment: { overall: 'positive' }, callId: 'call-1', createdAt: new Date() },
        { id: '2', sentiment: { overall: 'negative' }, callId: 'call-2', createdAt: new Date() },
        { id: '3', sentiment: { overall: 'positive' }, callId: 'call-3', createdAt: new Date() },
        { id: '4', sentiment: { overall: 'neutral' }, callId: 'call-4', createdAt: new Date() },
      ];

      mockPrisma.transcript.findMany.mockResolvedValue(mockTranscripts);

      const caller = createCaller(mockSupervisor);
      const result = await caller.getSentimentAnalytics({});

      expect(result).toBeDefined();
      expect(result.distribution.positive).toBe(2);
      expect(result.distribution.negative).toBe(1);
      expect(result.distribution.neutral).toBe(1);
      expect(result.total).toBe(4);
      expect(result.averageSentiment).toBe(0.25); // (2 - 1) / 4
    });

    it('should filter by date range', async () => {
      mockPrisma.transcript.findMany.mockResolvedValue([]);

      const caller = createCaller(mockSupervisor);
      const startDate = new Date('2024-01-01');
      const endDate = new Date('2024-01-31');

      await caller.getSentimentAnalytics({ startDate, endDate });

      expect(mockPrisma.transcript.findMany).toHaveBeenCalledWith({
        where: {
          createdAt: {
            gte: startDate,
            lte: endDate,
          },
        },
        select: expect.any(Object),
      });
    });

    it('should throw UNAUTHORIZED for unauthenticated user', async () => {
      const caller = createCaller();

      await expect(caller.getSentimentAnalytics({})).rejects.toThrow('UNAUTHORIZED');
    });
  });

  describe('getQualityMetrics', () => {
    it('should return quality metrics', async () => {
      const mockCalls = [
        { status: 'COMPLETED', duration: 300, transcripts: [{ id: 'transcript-1' }] },
        { status: 'COMPLETED', duration: 30, transcripts: [] },
        { status: 'CANCELED', duration: null, transcripts: [] },
      ];

      mockPrisma.call.findMany.mockResolvedValue(mockCalls);

      const caller = createCaller(mockSupervisor);
      const result = await caller.getQualityMetrics({});

      expect(result).toBeDefined();
      expect(typeof result.averageScore).toBe('number');
      expect(result.totalCalls).toBe(3);
      expect(result.scoreDistribution).toBeDefined();
      expect(result.scoreDistribution).toHaveProperty('excellent');
      expect(result.scoreDistribution).toHaveProperty('good');
      expect(result.scoreDistribution).toHaveProperty('average');
      expect(result.scoreDistribution).toHaveProperty('poor');
    });

    it('should filter by agentId when provided', async () => {
      mockPrisma.call.findMany.mockResolvedValue([]);

      const caller = createCaller(mockSupervisor);
      await caller.getQualityMetrics({ agentId: 'specific-agent-id' });

      expect(mockPrisma.call.findMany).toHaveBeenCalledWith({
        where: expect.objectContaining({
          agentId: 'specific-agent-id',
        }),
        include: expect.any(Object),
      });
    });

    it('should throw UNAUTHORIZED for unauthenticated user', async () => {
      const caller = createCaller();

      await expect(caller.getQualityMetrics({})).rejects.toThrow('UNAUTHORIZED');
    });
  });

  describe('exportAnalytics', () => {
    it('should generate export for supervisor', async () => {
      const caller = createCaller(mockSupervisor);
      const result = await caller.exportAnalytics({
        type: 'calls',
        format: 'csv',
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-01-31'),
      });

      expect(result).toBeDefined();
      expect(result.success).toBe(true);
      expect(result.downloadUrl).toBeDefined();
      expect(result.downloadUrl).toContain('calls');
      expect(result.downloadUrl).toContain('csv');
      expect(result.expiresAt).toBeDefined();
    });

    it('should support different export types and formats', async () => {
      const caller = createCaller(mockSupervisor);
      const types = ['calls', 'agents', 'campaigns', 'queues'] as const;
      const formats = ['csv', 'json', 'xlsx'] as const;

      for (const type of types) {
        for (const format of formats) {
          const result = await caller.exportAnalytics({
            type,
            format,
            startDate: new Date('2024-01-01'),
            endDate: new Date('2024-01-31'),
          });

          expect(result.success).toBe(true);
          expect(result.downloadUrl).toContain(type);
          expect(result.downloadUrl).toContain(format);
        }
      }
    });

    it('should require supervisor role', async () => {
      const caller = createCaller(mockAgent);

      await expect(caller.exportAnalytics({
        type: 'calls',
        format: 'csv',
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-01-31'),
      })).rejects.toThrow('FORBIDDEN');
    });

    it('should throw UNAUTHORIZED for unauthenticated user', async () => {
      const caller = createCaller();

      await expect(caller.exportAnalytics({
        type: 'calls',
        format: 'csv',
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-01-31'),
      })).rejects.toThrow('UNAUTHORIZED');
    });

    it('should validate input parameters', async () => {
      const caller = createCaller(mockSupervisor);

      // Test invalid type
      await expect(caller.exportAnalytics({
        type: 'invalid' as any,
        format: 'csv',
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-01-31'),
      })).rejects.toThrow();

      // Test invalid format
      await expect(caller.exportAnalytics({
        type: 'calls',
        format: 'invalid' as any,
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-01-31'),
      })).rejects.toThrow();
    });
  });
});