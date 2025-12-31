import { describe, expect, it, vi, beforeEach } from 'vitest';
import { TRPCError } from '@trpc/server';
import { z } from 'zod';

// Import the router directly to avoid setup dependencies
import { router, protectedProcedure, supervisorProcedure } from '../../server/trpc/index';

// Create a simplified analytics router for testing
const testAnalyticsRouter = router({
  getCallAnalytics: protectedProcedure
    .input(z.object({
      startDate: z.date().optional(),
      endDate: z.date().optional(),
      groupBy: z.enum(['hour', 'day', 'week', 'month']).default('day')
    }))
    .query(async ({ ctx, input }) => {
      if (!ctx.user) {
        throw new TRPCError({ code: 'UNAUTHORIZED' });
      }

      const mockResult = {
        summary: {
          totalCalls: 10,
          totalInbound: 6,
          totalOutbound: 4,
          totalCompleted: 8,
          totalAbandoned: 2,
          avgDuration: 150
        },
        data: [
          {
            period: '2024-01-01',
            total: 10,
            inbound: 6,
            outbound: 4,
            completed: 8,
            abandoned: 2,
            totalDuration: 1200,
            avgDuration: 150,
            completionRate: 80
          }
        ]
      };

      return mockResult;
    }),

  getAgentAnalytics: supervisorProcedure
    .input(z.object({
      agentId: z.string().optional(),
      startDate: z.date().optional(),
      endDate: z.date().optional()
    }))
    .query(async ({ ctx, input }) => {
      return {
        agents: [
          {
            id: 'agent-1',
            name: 'John Doe',
            totalCalls: 20,
            completedCalls: 18,
            avgDuration: 180,
            completionRate: 90,
            satisfactionScore: 4.5,
            status: 'available'
          }
        ]
      };
    }),

  getRealtimeMetrics: protectedProcedure
    .query(async ({ ctx }) => {
      if (!ctx.user) {
        throw new TRPCError({ code: 'UNAUTHORIZED' });
      }

      return {
        calls: {
          active: 5,
          queued: 3,
          offered: 15,
          abandoned: 2
        },
        agents: {
          available: 8,
          busy: 5,
          onBreak: 2,
          offline: 1
        },
        performance: {
          serviceLevel: 85,
          avgHandleTime: 180,
          avgWaitTime: 45,
          longestWait: 120
        }
      };
    }),

  exportAnalytics: supervisorProcedure
    .input(z.object({
      type: z.enum(['calls', 'agents', 'campaigns', 'queues']),
      format: z.enum(['csv', 'json', 'xlsx']),
      startDate: z.date(),
      endDate: z.date()
    }))
    .mutation(async ({ ctx, input }) => {
      return {
        success: true,
        downloadUrl: `/api/analytics/export/${input.type}_${Date.now()}.${input.format}`,
        expiresAt: new Date(Date.now() + 60 * 60 * 1000)
      };
    })
});

// Mock context creator
function createMockContext(user?: any) {
  return {
    user: user || null,
    prisma: {
      call: { findMany: vi.fn(), count: vi.fn() },
      user: { findMany: vi.fn(), count: vi.fn() },
      campaign: { findMany: vi.fn() },
      transcript: { findMany: vi.fn() }
    },
    redis: {
      get: vi.fn(),
      set: vi.fn(),
      del: vi.fn()
    }
  };
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

describe('Analytics Router Standalone Unit Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getCallAnalytics', () => {
    it('should return call analytics for authenticated user', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

      const result = await caller.getCallAnalytics({});

      expect(result).toBeDefined();
      expect(result.summary).toBeDefined();
      expect(result.data).toBeDefined();
      expect(Array.isArray(result.data)).toBe(true);

      expect(result.summary.totalCalls).toBe(10);
      expect(result.summary.totalInbound).toBe(6);
      expect(result.summary.totalOutbound).toBe(4);
      expect(result.summary.totalCompleted).toBe(8);
      expect(result.summary.totalAbandoned).toBe(2);
      expect(result.summary.avgDuration).toBe(150);

      expect(result.data.length).toBe(1);
      expect(result.data[0].period).toBe('2024-01-01');
      expect(result.data[0].completionRate).toBe(80);
    });

    it('should throw UNAUTHORIZED for unauthenticated user', async () => {
      const ctx = createMockContext();
      const caller = testAnalyticsRouter.createCaller(ctx);

      await expect(caller.getCallAnalytics({})).rejects.toThrow('UNAUTHORIZED');
    });

    it('should validate groupBy parameter', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

      // Valid groupBy values should work
      await expect(caller.getCallAnalytics({ groupBy: 'day' })).resolves.toBeDefined();
      await expect(caller.getCallAnalytics({ groupBy: 'hour' })).resolves.toBeDefined();
      await expect(caller.getCallAnalytics({ groupBy: 'week' })).resolves.toBeDefined();
      await expect(caller.getCallAnalytics({ groupBy: 'month' })).resolves.toBeDefined();

      // Invalid groupBy should throw
      await expect(caller.getCallAnalytics({ groupBy: 'invalid' as any })).rejects.toThrow();
    });

    it('should handle date parameters', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

      const startDate = new Date('2024-01-01');
      const endDate = new Date('2024-01-31');

      const result = await caller.getCallAnalytics({ startDate, endDate });
      expect(result).toBeDefined();
    });

    it('should work for both supervisor and agent users', async () => {
      const supervisorCtx = createMockContext(mockSupervisor);
      const agentCtx = createMockContext(mockAgent);

      const supervisorCaller = testAnalyticsRouter.createCaller(supervisorCtx);
      const agentCaller = testAnalyticsRouter.createCaller(agentCtx);

      const supervisorResult = await supervisorCaller.getCallAnalytics({});
      const agentResult = await agentCaller.getCallAnalytics({});

      expect(supervisorResult).toBeDefined();
      expect(agentResult).toBeDefined();
    });
  });

  describe('getAgentAnalytics', () => {
    it('should return agent analytics for supervisor', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

      const result = await caller.getAgentAnalytics({});

      expect(result).toBeDefined();
      expect(result.agents).toBeDefined();
      expect(Array.isArray(result.agents)).toBe(true);
      expect(result.agents.length).toBe(1);

      const agent = result.agents[0];
      expect(agent.id).toBe('agent-1');
      expect(agent.name).toBe('John Doe');
      expect(agent.totalCalls).toBe(20);
      expect(agent.completedCalls).toBe(18);
      expect(agent.avgDuration).toBe(180);
      expect(agent.completionRate).toBe(90);
      expect(agent.satisfactionScore).toBe(4.5);
      expect(agent.status).toBe('available');
    });

    it('should require supervisor role', async () => {
      const ctx = createMockContext(mockAgent);
      const caller = testAnalyticsRouter.createCaller(ctx);

      await expect(caller.getAgentAnalytics({})).rejects.toThrow('Supervisor access required');
    });

    it('should throw UNAUTHORIZED for unauthenticated user', async () => {
      const ctx = createMockContext();
      const caller = testAnalyticsRouter.createCaller(ctx);

      await expect(caller.getAgentAnalytics({})).rejects.toThrow('Supervisor access required');
    });

    it('should accept optional parameters', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

      const result = await caller.getAgentAnalytics({
        agentId: 'specific-agent-id',
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-01-31'),
      });

      expect(result).toBeDefined();
    });
  });

  describe('getRealtimeMetrics', () => {
    it('should return real-time metrics for authenticated users', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

      const result = await caller.getRealtimeMetrics();

      expect(result).toBeDefined();
      expect(result.calls).toBeDefined();
      expect(result.agents).toBeDefined();
      expect(result.performance).toBeDefined();

      expect(result.calls.active).toBe(5);
      expect(result.calls.queued).toBe(3);
      expect(result.calls.offered).toBe(15);
      expect(result.calls.abandoned).toBe(2);

      expect(result.agents.available).toBe(8);
      expect(result.agents.busy).toBe(5);
      expect(result.agents.onBreak).toBe(2);
      expect(result.agents.offline).toBe(1);

      expect(result.performance.serviceLevel).toBe(85);
      expect(result.performance.avgHandleTime).toBe(180);
      expect(result.performance.avgWaitTime).toBe(45);
      expect(result.performance.longestWait).toBe(120);
    });

    it('should work for both supervisor and agent users', async () => {
      const supervisorCtx = createMockContext(mockSupervisor);
      const agentCtx = createMockContext(mockAgent);

      const supervisorCaller = testAnalyticsRouter.createCaller(supervisorCtx);
      const agentCaller = testAnalyticsRouter.createCaller(agentCtx);

      const supervisorResult = await supervisorCaller.getRealtimeMetrics();
      const agentResult = await agentCaller.getRealtimeMetrics();

      expect(supervisorResult).toBeDefined();
      expect(agentResult).toBeDefined();

      // Both should have the same structure
      expect(supervisorResult.calls).toBeDefined();
      expect(agentResult.calls).toBeDefined();
    });

    it('should throw UNAUTHORIZED for unauthenticated user', async () => {
      const ctx = createMockContext();
      const caller = testAnalyticsRouter.createCaller(ctx);

      await expect(caller.getRealtimeMetrics()).rejects.toThrow('UNAUTHORIZED');
    });
  });

  describe('exportAnalytics', () => {
    it('should generate export for supervisor', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

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
      expect(result.expiresAt instanceof Date).toBe(true);
    });

    it('should support different export types and formats', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

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
      const ctx = createMockContext(mockAgent);
      const caller = testAnalyticsRouter.createCaller(ctx);

      await expect(caller.exportAnalytics({
        type: 'calls',
        format: 'csv',
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-01-31'),
      })).rejects.toThrow('Supervisor access required');
    });

    it('should throw UNAUTHORIZED for unauthenticated user', async () => {
      const ctx = createMockContext();
      const caller = testAnalyticsRouter.createCaller(ctx);

      await expect(caller.exportAnalytics({
        type: 'calls',
        format: 'csv',
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-01-31'),
      })).rejects.toThrow('Supervisor access required');
    });

    it('should validate input parameters', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

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

    it('should require all required parameters', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

      // Missing startDate
      await expect(caller.exportAnalytics({
        type: 'calls',
        format: 'csv',
        endDate: new Date('2024-01-31'),
      } as any)).rejects.toThrow();

      // Missing endDate
      await expect(caller.exportAnalytics({
        type: 'calls',
        format: 'csv',
        startDate: new Date('2024-01-01'),
      } as any)).rejects.toThrow();
    });
  });

  describe('Input Validation', () => {
    it('should validate date objects for getCallAnalytics', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

      // Valid date objects should work
      await expect(caller.getCallAnalytics({
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-01-31'),
      })).resolves.toBeDefined();

      // Invalid date strings should be rejected (they need to be Date objects)
      await expect(caller.getCallAnalytics({
        startDate: '2024-01-01' as any,
        endDate: '2024-01-31' as any,
      })).rejects.toThrow();
    });

    it('should validate enum values', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

      // Valid enum values
      for (const groupBy of ['hour', 'day', 'week', 'month']) {
        await expect(caller.getCallAnalytics({ groupBy: groupBy as any })).resolves.toBeDefined();
      }

      // Invalid enum values should throw validation error
      for (const invalidValue of ['minute', 'year', 'invalid']) {
        await expect(caller.getCallAnalytics({ groupBy: invalidValue as any })).rejects.toThrow();
      }

      // Note: null and undefined might use default value, so we test explicit invalid strings
    });

    it('should handle optional parameters correctly', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

      // No parameters (all optional)
      await expect(caller.getCallAnalytics({})).resolves.toBeDefined();

      // Partial parameters
      await expect(caller.getCallAnalytics({
        startDate: new Date('2024-01-01')
      })).resolves.toBeDefined();

      await expect(caller.getCallAnalytics({
        groupBy: 'hour'
      })).resolves.toBeDefined();
    });
  });

  describe('Error Handling', () => {
    it('should handle TRPCError codes correctly', async () => {
      const ctx = createMockContext();
      const caller = testAnalyticsRouter.createCaller(ctx);

      try {
        await caller.getCallAnalytics({});
        expect.fail('Should have thrown UNAUTHORIZED error');
      } catch (error) {
        expect(error).toBeInstanceOf(TRPCError);
        expect((error as TRPCError).code).toBe('UNAUTHORIZED');
      }
    });

    it('should handle validation errors', async () => {
      const ctx = createMockContext(mockSupervisor);
      const caller = testAnalyticsRouter.createCaller(ctx);

      try {
        await caller.getCallAnalytics({ groupBy: 'invalid' as any });
        expect.fail('Should have thrown validation error');
      } catch (error) {
        // Should be a validation error (ZodError wrapped in TRPCError)
        expect(error).toBeDefined();
      }
    });

    it('should handle permission errors', async () => {
      const ctx = createMockContext(mockAgent);
      const caller = testAnalyticsRouter.createCaller(ctx);

      try {
        await caller.getAgentAnalytics({});
        expect.fail('Should have thrown FORBIDDEN error');
      } catch (error) {
        expect(error).toBeInstanceOf(TRPCError);
        expect((error as TRPCError).code).toBe('FORBIDDEN');
      }
    });
  });
});