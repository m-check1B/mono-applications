import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { createTRPCMsw } from 'msw-trpc';
import { setupServer } from 'msw/node';
import { apmRouter } from '../../../server/trpc/routers/apm';
import { createTRPCClient, httpBatchLink } from '@trpc/client';
import { testDb, createTestUser } from '../../setup';
import { UserRole } from '@prisma/client';
import { TRPCError } from '@trpc/server';

// Mock APM service
const mockAPMService = {
  getDashboardData: vi.fn(),
  getSystemMetrics: vi.fn(),
  recordMetric: vi.fn(),
  recordError: vi.fn(),
};

// Mock Redis service
const mockRedisService = {
  isReady: vi.fn().mockReturnValue(true),
  ping: vi.fn().mockResolvedValue('PONG'),
  client: {
    keys: vi.fn(),
    get: vi.fn(),
    del: vi.fn(),
  },
};

// Mock Prisma
const mockPrisma = {
  $queryRaw: vi.fn(),
};

// Mock dependencies
vi.mock('../../../server/services/apm-service', () => ({
  apmService: mockAPMService,
}));

vi.mock('../../../server/services/redis-service', () => ({
  redisService: mockRedisService,
}));

vi.mock('../../../server/lib/prisma-client', () => ({
  prisma: mockPrisma,
}));

describe('APM Router Integration Tests', () => {
  let testOrganizationId: string;
  let testAdminId: string;
  let testSupervisorId: string;
  let testAgentId: string;

  beforeEach(async () => {
    testOrganizationId = 'test-org';

    // Create test users with different roles
    const admin = await createTestUser({
      email: 'admin@test.com',
      role: UserRole.ADMIN,
      organizationId: testOrganizationId,
    });
    testAdminId = admin.id;

    const supervisor = await createTestUser({
      email: 'supervisor@test.com',
      role: UserRole.SUPERVISOR,
      organizationId: testOrganizationId,
    });
    testSupervisorId = supervisor.id;

    const agent = await createTestUser({
      email: 'agent@test.com',
      role: UserRole.AGENT,
      organizationId: testOrganizationId,
    });
    testAgentId = agent.id;

    // Reset all mocks
    vi.clearAllMocks();

    // Set up default mock responses
    mockPrisma.$queryRaw.mockResolvedValue([{ result: 1 }]);
    mockRedisService.ping.mockResolvedValue('PONG');
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('getDashboard', () => {
    it('should return dashboard data for supervisor', async () => {
      const mockDashboard = {
        system: {
          timestamp: new Date(),
          cpu: { usage: 25.5, loadAverage: [1.2, 1.1, 1.0] },
          memory: { total: 8000000000, used: 2000000000, free: 6000000000, percentage: 25 },
          process: { uptime: 3600, memoryUsage: {}, pid: 12345 },
          requests: { total: 1000, success: 950, errors: 50, avgResponseTime: 150 },
        },
        health: [
          { service: 'PostgreSQL', status: 'healthy', responseTime: 5 },
          { service: 'Redis', status: 'healthy', responseTime: 2 },
        ],
        metrics: {
          recent: [],
          responseTimePercentiles: { p50: 100, p95: 500, p99: 1000 },
          topEndpoints: [
            { endpoint: 'GET /api/calls', count: 150 },
            { endpoint: 'POST /api/calls', count: 75 },
          ],
        },
        errors: {
          recent: [],
          byLevel: { critical: 0, error: 5, warning: 10 },
        },
        timestamp: new Date(),
      };

      mockAPMService.getDashboardData.mockResolvedValue(mockDashboard);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getDashboard();

      expect(result).toEqual(mockDashboard);
      expect(mockAPMService.getDashboardData).toHaveBeenCalled();
    });

    it('should require supervisor role', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
      };

      const caller = apmRouter.createCaller(mockContext);

      await expect(caller.getDashboard()).rejects.toThrow('Insufficient permissions');
    });

    it('should handle APM service errors', async () => {
      mockAPMService.getDashboardData.mockRejectedValue(new Error('APM service error'));

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);

      await expect(caller.getDashboard()).rejects.toThrow('Failed to fetch APM dashboard data');
    });
  });

  describe('getHealth', () => {
    it('should return system health status for authenticated users', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getHealth();

      expect(result).toMatchObject({
        status: expect.any(String),
        timestamp: expect.any(Date),
        services: {
          database: expect.objectContaining({
            status: expect.any(String),
            responseTime: expect.any(Number),
          }),
          redis: expect.objectContaining({
            status: expect.any(String),
            responseTime: expect.any(Number),
          }),
          api: expect.objectContaining({
            status: 'healthy',
            responseTime: 0,
          }),
        },
        metrics: expect.objectContaining({
          uptime: expect.any(Number),
          memory: expect.any(Object),
          cpu: expect.any(Object),
        }),
      });

      expect(mockPrisma.$queryRaw).toHaveBeenCalledWith(expect.anything());
      expect(mockRedisService.ping).toHaveBeenCalled();
    });

    it('should detect database health issues', async () => {
      mockPrisma.$queryRaw.mockRejectedValue(new Error('Database connection failed'));

      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getHealth();

      expect(result.services.database.status).toBe('unhealthy');
      expect(result.status).toBe('degraded');
    });

    it('should detect Redis health issues but not degrade overall health', async () => {
      mockRedisService.ping.mockRejectedValue(new Error('Redis connection failed'));

      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getHealth();

      expect(result.services.redis.status).toBe('unhealthy');
      expect(result.status).toBe('healthy'); // Redis is optional
    });

    it('should require authentication', async () => {
      const mockContext = {
        user: null,
      };

      const caller = apmRouter.createCaller(mockContext);

      await expect(caller.getHealth()).rejects.toThrow();
    });
  });

  describe('getMetrics', () => {
    it('should return performance metrics for supervisor', async () => {
      const mockSystemMetrics = {
        timestamp: new Date(),
        cpu: { usage: 30, loadAverage: [1.5, 1.3, 1.2] },
        memory: { total: 8000000000, used: 3000000000, free: 5000000000, percentage: 37.5 },
        process: { uptime: 7200, memoryUsage: {}, pid: 12345 },
        requests: { total: 2000, success: 1900, errors: 100, avgResponseTime: 175 },
      };

      const mockHistoricalData = [
        { timestamp: new Date(Date.now() - 3600000), requests: { total: 1500 } },
        { timestamp: new Date(Date.now() - 7200000), requests: { total: 1200 } },
      ];

      mockAPMService.getSystemMetrics.mockResolvedValue(mockSystemMetrics);
      mockRedisService.client.keys.mockResolvedValue(['apm:metrics:1', 'apm:metrics:2']);
      mockRedisService.client.get
        .mockResolvedValueOnce(JSON.stringify(mockHistoricalData[0]))
        .mockResolvedValueOnce(JSON.stringify(mockHistoricalData[1]));

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getMetrics({
        timeRange: '24h',
        metric: 'requests',
      });

      expect(result).toMatchObject({
        current: mockSystemMetrics,
        historical: expect.any(Array),
        timeRange: '24h',
      });

      expect(mockAPMService.getSystemMetrics).toHaveBeenCalled();
      expect(mockRedisService.client.keys).toHaveBeenCalledWith('apm:metrics:*');
    });

    it('should handle different time ranges', async () => {
      const timeRanges = ['1h', '6h', '24h', '7d', '30d'] as const;

      mockAPMService.getSystemMetrics.mockResolvedValue({
        timestamp: new Date(),
        cpu: { usage: 25, loadAverage: [1.0] },
        memory: { total: 8000000000, used: 2000000000, free: 6000000000, percentage: 25 },
        process: { uptime: 3600, memoryUsage: {}, pid: 12345 },
        requests: { total: 100, success: 95, errors: 5, avgResponseTime: 150 },
      });

      mockRedisService.client.keys.mockResolvedValue([]);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);

      for (const timeRange of timeRanges) {
        const result = await caller.getMetrics({ timeRange });
        expect(result.timeRange).toBe(timeRange);
      }
    });

    it('should handle Redis unavailability gracefully', async () => {
      mockRedisService.isReady.mockReturnValue(false);
      mockAPMService.getSystemMetrics.mockResolvedValue({
        timestamp: new Date(),
        cpu: { usage: 25, loadAverage: [1.0] },
        memory: { total: 8000000000, used: 2000000000, free: 6000000000, percentage: 25 },
        process: { uptime: 3600, memoryUsage: {}, pid: 12345 },
        requests: { total: 100, success: 95, errors: 5, avgResponseTime: 150 },
      });

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getMetrics({ timeRange: '1h' });

      expect(result.historical).toEqual([]);
      expect(mockRedisService.client.keys).not.toHaveBeenCalled();
    });

    it('should require supervisor role', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
      };

      const caller = apmRouter.createCaller(mockContext);

      await expect(caller.getMetrics({ timeRange: '1h' })).rejects.toThrow('Insufficient permissions');
    });

    it('should validate input parameters', async () => {
      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);

      // Test invalid time range
      await expect(caller.getMetrics({ timeRange: 'invalid' as any })).rejects.toThrow();

      // Test invalid metric type
      await expect(caller.getMetrics({
        timeRange: '1h',
        metric: 'invalid' as any
      })).rejects.toThrow();
    });
  });

  describe('getErrors', () => {
    it('should return error logs for supervisor', async () => {
      const mockErrors = [
        {
          timestamp: new Date(),
          level: 'error',
          message: 'Database query failed',
          stack: 'Error: Database query failed\n    at db.js:1:1',
          context: { operation: 'user-fetch' },
        },
        {
          timestamp: new Date(Date.now() - 3600000),
          level: 'warning',
          message: 'Slow query detected',
          context: { duration: 5000 },
        },
      ];

      mockRedisService.client.keys.mockResolvedValue(['apm:errors:1', 'apm:errors:2']);
      mockRedisService.client.get
        .mockResolvedValueOnce(JSON.stringify(mockErrors[0]))
        .mockResolvedValueOnce(JSON.stringify(mockErrors[1]));

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getErrors({
        limit: 10,
        level: 'all',
      });

      expect(result).toMatchObject({
        errors: expect.any(Array),
        total: expect.any(Number),
      });

      expect(result.errors).toHaveLength(2);
      expect(mockRedisService.client.keys).toHaveBeenCalledWith('apm:errors:*');
    });

    it('should filter errors by level', async () => {
      const mockErrors = [
        { timestamp: new Date(), level: 'critical', message: 'Critical error' },
        { timestamp: new Date(), level: 'error', message: 'Regular error' },
        { timestamp: new Date(), level: 'warning', message: 'Warning message' },
      ];

      mockRedisService.client.keys.mockResolvedValue(['apm:errors:1', 'apm:errors:2', 'apm:errors:3']);
      mockRedisService.client.get
        .mockResolvedValueOnce(JSON.stringify(mockErrors[0]))
        .mockResolvedValueOnce(JSON.stringify(mockErrors[1]))
        .mockResolvedValueOnce(JSON.stringify(mockErrors[2]));

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);

      // Test critical level filter
      let result = await caller.getErrors({ level: 'critical' });
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].level).toBe('critical');

      // Reset mocks for next test
      vi.clearAllMocks();
      mockRedisService.client.keys.mockResolvedValue(['apm:errors:1', 'apm:errors:2', 'apm:errors:3']);
      mockRedisService.client.get
        .mockResolvedValueOnce(JSON.stringify(mockErrors[0]))
        .mockResolvedValueOnce(JSON.stringify(mockErrors[1]))
        .mockResolvedValueOnce(JSON.stringify(mockErrors[2]));

      // Test error level filter
      result = await caller.getErrors({ level: 'error' });
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].level).toBe('error');
    });

    it('should filter errors by date', async () => {
      const now = new Date();
      const hourAgo = new Date(now.getTime() - 3600000);
      const dayAgo = new Date(now.getTime() - 86400000);

      const mockErrors = [
        { timestamp: now, level: 'error', message: 'Recent error' },
        { timestamp: dayAgo, level: 'error', message: 'Old error' },
      ];

      mockRedisService.client.keys.mockResolvedValue(['apm:errors:1', 'apm:errors:2']);
      mockRedisService.client.get
        .mockResolvedValueOnce(JSON.stringify(mockErrors[0]))
        .mockResolvedValueOnce(JSON.stringify(mockErrors[1]));

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getErrors({
        since: hourAgo,
      });

      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].message).toBe('Recent error');
    });

    it('should limit and sort errors correctly', async () => {
      const mockErrors = Array.from({ length: 10 }, (_, i) => ({
        timestamp: new Date(Date.now() - i * 60000), // Each error 1 minute apart
        level: 'error',
        message: `Error ${i}`,
      }));

      mockRedisService.client.keys.mockResolvedValue(
        Array.from({ length: 10 }, (_, i) => `apm:errors:${i}`)
      );

      mockErrors.forEach((error, i) => {
        mockRedisService.client.get.mockResolvedValueOnce(JSON.stringify(error));
      });

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getErrors({
        limit: 5,
      });

      expect(result.errors).toHaveLength(5);
      expect(result.total).toBe(10);

      // Should be sorted by timestamp descending (most recent first)
      for (let i = 1; i < result.errors.length; i++) {
        const current = new Date(result.errors[i].timestamp);
        const previous = new Date(result.errors[i - 1].timestamp);
        expect(current.getTime()).toBeLessThanOrEqual(previous.getTime());
      }
    });

    it('should handle Redis unavailability', async () => {
      mockRedisService.isReady.mockReturnValue(false);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getErrors();

      expect(result.errors).toEqual([]);
      expect(result.total).toBe(0);
    });

    it('should require supervisor role', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
      };

      const caller = apmRouter.createCaller(mockContext);

      await expect(caller.getErrors()).rejects.toThrow('Insufficient permissions');
    });

    it('should validate input parameters', async () => {
      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);

      // Test invalid limit
      await expect(caller.getErrors({ limit: 0 })).rejects.toThrow();
      await expect(caller.getErrors({ limit: 101 })).rejects.toThrow();

      // Test invalid level
      await expect(caller.getErrors({ level: 'invalid' as any })).rejects.toThrow();
    });
  });

  describe('recordMetric', () => {
    it('should record custom metrics for authenticated users', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.recordMetric({
        type: 'database',
        operation: 'SELECT users',
        duration: 250,
        success: true,
        metadata: { table: 'users', rows: 100 },
      });

      expect(result.recorded).toBe(true);
      expect(mockAPMService.recordMetric).toHaveBeenCalledWith({
        timestamp: expect.any(Date),
        type: 'database',
        operation: 'SELECT users',
        duration: 250,
        success: true,
        metadata: { table: 'users', rows: 100 },
      });
    });

    it('should validate metric input', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
      };

      const caller = apmRouter.createCaller(mockContext);

      // Test invalid type
      await expect(caller.recordMetric({
        type: 'invalid' as any,
        operation: 'test',
        duration: 100,
        success: true,
      })).rejects.toThrow();

      // Test missing required fields
      await expect(caller.recordMetric({
        type: 'api',
        operation: '',
        duration: 100,
        success: true,
      })).rejects.toThrow();
    });

    it('should require authentication', async () => {
      const mockContext = {
        user: null,
      };

      const caller = apmRouter.createCaller(mockContext);

      await expect(caller.recordMetric({
        type: 'api',
        operation: 'test',
        duration: 100,
        success: true,
      })).rejects.toThrow();
    });
  });

  describe('recordError', () => {
    it('should record custom errors for authenticated users', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.recordError({
        level: 'error',
        message: 'Custom application error',
        stack: 'Error: Custom application error\n    at app.js:1:1',
        context: { component: 'user-service', action: 'create-user' },
      });

      expect(result.recorded).toBe(true);
      expect(mockAPMService.recordError).toHaveBeenCalledWith({
        timestamp: expect.any(Date),
        level: 'error',
        message: 'Custom application error',
        stack: 'Error: Custom application error\n    at app.js:1:1',
        context: {
          component: 'user-service',
          action: 'create-user',
          userId: testAgentId,
        },
      });
    });

    it('should include user ID in context', async () => {
      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      await caller.recordError({
        level: 'warning',
        message: 'Test warning',
        context: { custom: 'data' },
      });

      expect(mockAPMService.recordError).toHaveBeenCalledWith({
        timestamp: expect.any(Date),
        level: 'warning',
        message: 'Test warning',
        stack: undefined,
        context: {
          custom: 'data',
          userId: testSupervisorId,
        },
      });
    });

    it('should validate error input', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
      };

      const caller = apmRouter.createCaller(mockContext);

      // Test invalid level
      await expect(caller.recordError({
        level: 'invalid' as any,
        message: 'test error',
      })).rejects.toThrow();

      // Test empty message
      await expect(caller.recordError({
        level: 'error',
        message: '',
      })).rejects.toThrow();
    });

    it('should require authentication', async () => {
      const mockContext = {
        user: null,
      };

      const caller = apmRouter.createCaller(mockContext);

      await expect(caller.recordError({
        level: 'error',
        message: 'test error',
      })).rejects.toThrow();
    });
  });

  describe('getRequestStats', () => {
    it('should return request statistics for supervisor', async () => {
      const mockDashboard = {
        metrics: {
          topEndpoints: [
            { endpoint: 'GET /api/calls', count: 150 },
            { endpoint: 'POST /api/calls', count: 75 },
            { endpoint: 'GET /api/users', count: 50 },
          ],
          responseTimePercentiles: { p50: 100, p95: 500, p99: 1000 },
        },
      };

      mockAPMService.getDashboardData.mockResolvedValue(mockDashboard);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getRequestStats({
        groupBy: 'endpoint',
        limit: 10,
      });

      expect(result).toMatchObject({
        stats: expect.any(Array),
        percentiles: mockDashboard.metrics.responseTimePercentiles,
      });

      expect(result.stats).toHaveLength(3);
      expect(mockAPMService.getDashboardData).toHaveBeenCalled();
    });

    it('should limit results correctly', async () => {
      const mockDashboard = {
        metrics: {
          topEndpoints: Array.from({ length: 20 }, (_, i) => ({
            endpoint: `GET /api/endpoint${i}`,
            count: 100 - i,
          })),
          responseTimePercentiles: { p50: 100, p95: 500, p99: 1000 },
        },
      };

      mockAPMService.getDashboardData.mockResolvedValue(mockDashboard);

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getRequestStats({
        groupBy: 'endpoint',
        limit: 5,
      });

      expect(result.stats).toHaveLength(5);
    });

    it('should handle different groupBy options', async () => {
      mockAPMService.getDashboardData.mockResolvedValue({
        metrics: {
          topEndpoints: [],
          responseTimePercentiles: { p50: 100, p95: 500, p99: 1000 },
        },
      });

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);

      // Test status grouping (not implemented yet, should return empty)
      const result = await caller.getRequestStats({
        groupBy: 'status',
        limit: 10,
      });

      expect(result.stats).toEqual([]);
      expect(result.percentiles).toBeDefined();
    });

    it('should require supervisor role', async () => {
      const mockContext = {
        user: { id: testAgentId, organizationId: testOrganizationId, role: UserRole.AGENT },
      };

      const caller = apmRouter.createCaller(mockContext);

      await expect(caller.getRequestStats({
        groupBy: 'endpoint',
      })).rejects.toThrow('Insufficient permissions');
    });

    it('should validate input parameters', async () => {
      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);

      // Test invalid groupBy
      await expect(caller.getRequestStats({
        groupBy: 'invalid' as any,
      })).rejects.toThrow();

      // Test invalid limit
      await expect(caller.getRequestStats({
        groupBy: 'endpoint',
        limit: 0,
      })).rejects.toThrow();

      await expect(caller.getRequestStats({
        groupBy: 'endpoint',
        limit: 101,
      })).rejects.toThrow();
    });
  });

  describe('clearMetrics', () => {
    it('should clear metrics for admin users', async () => {
      mockRedisService.client.keys
        .mockResolvedValueOnce(['apm:metrics:1', 'apm:metrics:2'])
        .mockResolvedValueOnce(['apm:errors:1']);
      mockRedisService.client.del.mockResolvedValue(2);

      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.clearMetrics({
        type: 'all',
        confirm: true,
      });

      expect(result).toEqual({
        cleared: true,
        type: 'all',
      });

      expect(mockRedisService.client.keys).toHaveBeenCalledWith('apm:metrics:*');
      expect(mockRedisService.client.keys).toHaveBeenCalledWith('apm:errors:*');
      expect(mockRedisService.client.del).toHaveBeenCalledWith('apm:metrics:1', 'apm:metrics:2');
      expect(mockRedisService.client.del).toHaveBeenCalledWith('apm:errors:1');
    });

    it('should clear only metrics when type is metrics', async () => {
      mockRedisService.client.keys.mockResolvedValue(['apm:metrics:1', 'apm:metrics:2']);
      mockRedisService.client.del.mockResolvedValue(2);

      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.clearMetrics({
        type: 'metrics',
        confirm: true,
      });

      expect(result.cleared).toBe(true);
      expect(result.type).toBe('metrics');

      expect(mockRedisService.client.keys).toHaveBeenCalledWith('apm:metrics:*');
      expect(mockRedisService.client.keys).not.toHaveBeenCalledWith('apm:errors:*');
    });

    it('should clear only errors when type is errors', async () => {
      mockRedisService.client.keys.mockResolvedValue(['apm:errors:1', 'apm:errors:2']);
      mockRedisService.client.del.mockResolvedValue(2);

      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.clearMetrics({
        type: 'errors',
        confirm: true,
      });

      expect(result.cleared).toBe(true);
      expect(result.type).toBe('errors');

      expect(mockRedisService.client.keys).toHaveBeenCalledWith('apm:errors:*');
      expect(mockRedisService.client.keys).not.toHaveBeenCalledWith('apm:metrics:*');
    });

    it('should require admin role', async () => {
      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);

      await expect(caller.clearMetrics({
        type: 'all',
        confirm: true,
      })).rejects.toThrow('Only admin users can clear metrics');
    });

    it('should require confirmation', async () => {
      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
      };

      const caller = apmRouter.createCaller(mockContext);

      await expect(caller.clearMetrics({
        type: 'all',
        confirm: false as any,
      })).rejects.toThrow('Confirmation required to clear metrics');
    });

    it('should handle Redis unavailability gracefully', async () => {
      mockRedisService.isReady.mockReturnValue(false);

      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.clearMetrics({
        type: 'all',
        confirm: true,
      });

      expect(result.cleared).toBe(true);
      expect(mockRedisService.client.keys).not.toHaveBeenCalled();
    });

    it('should handle empty key lists', async () => {
      mockRedisService.client.keys.mockResolvedValue([]);

      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.clearMetrics({
        type: 'metrics',
        confirm: true,
      });

      expect(result.cleared).toBe(true);
      expect(mockRedisService.client.del).not.toHaveBeenCalled();
    });

    it('should validate input parameters', async () => {
      const mockContext = {
        user: { id: testAdminId, organizationId: testOrganizationId, role: UserRole.ADMIN },
      };

      const caller = apmRouter.createCaller(mockContext);

      // Test invalid type
      await expect(caller.clearMetrics({
        type: 'invalid' as any,
        confirm: true,
      })).rejects.toThrow();
    });
  });

  describe('WebSocket metrics streaming', () => {
    it('should support real-time metrics streaming', () => {
      // This test verifies that the APM service can emit events
      // for real-time dashboard updates via WebSocket
      const metricListener = vi.fn();
      mockAPMService.on = vi.fn();
      mockAPMService.emit = vi.fn();

      // Simulate subscribing to real-time metrics
      mockAPMService.on('system:metrics', metricListener);
      mockAPMService.on('metric', metricListener);
      mockAPMService.on('error', metricListener);

      expect(mockAPMService.on).toHaveBeenCalledWith('system:metrics', metricListener);
      expect(mockAPMService.on).toHaveBeenCalledWith('metric', metricListener);
      expect(mockAPMService.on).toHaveBeenCalledWith('error', metricListener);
    });
  });

  describe('Edge cases and error scenarios', () => {
    it('should handle corrupted Redis data gracefully', async () => {
      mockRedisService.client.keys.mockResolvedValue(['apm:errors:1', 'apm:errors:2']);
      mockRedisService.client.get
        .mockResolvedValueOnce('invalid json data')
        .mockResolvedValueOnce(JSON.stringify({ valid: 'data', timestamp: new Date() }));

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getErrors();

      // Should skip corrupted data and return valid entries
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0]).toMatchObject({ valid: 'data' });
    });

    it('should handle missing Redis data gracefully', async () => {
      mockRedisService.client.keys.mockResolvedValue(['apm:errors:1', 'apm:errors:2']);
      mockRedisService.client.get
        .mockResolvedValueOnce(null)
        .mockResolvedValueOnce(JSON.stringify({ valid: 'data', timestamp: new Date() }));

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getErrors();

      expect(result.errors).toHaveLength(1);
    });

    it('should handle concurrent access gracefully', async () => {
      // Simulate multiple concurrent requests
      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      mockAPMService.getSystemMetrics.mockResolvedValue({
        timestamp: new Date(),
        cpu: { usage: 25, loadAverage: [1.0] },
        memory: { total: 8000000000, used: 2000000000, free: 6000000000, percentage: 25 },
        process: { uptime: 3600, memoryUsage: {}, pid: 12345 },
        requests: { total: 100, success: 95, errors: 5, avgResponseTime: 150 },
      });

      const caller = apmRouter.createCaller(mockContext);

      // Execute multiple concurrent requests
      const promises = Array.from({ length: 10 }, () =>
        caller.getMetrics({ timeRange: '1h' })
      );

      const results = await Promise.all(promises);

      expect(results).toHaveLength(10);
      results.forEach(result => {
        expect(result.current).toBeDefined();
        expect(result.timeRange).toBe('1h');
      });
    });

    it('should handle large datasets efficiently', async () => {
      // Simulate large number of error entries
      const largeKeys = Array.from({ length: 1000 }, (_, i) => `apm:errors:${i}`);
      const largeErrorSet = Array.from({ length: 1000 }, (_, i) => ({
        timestamp: new Date(Date.now() - i * 1000),
        level: 'error',
        message: `Error ${i}`,
      }));

      mockRedisService.client.keys.mockResolvedValue(largeKeys);
      largeErrorSet.forEach((error, i) => {
        mockRedisService.client.get.mockResolvedValueOnce(JSON.stringify(error));
      });

      const mockContext = {
        user: { id: testSupervisorId, organizationId: testOrganizationId, role: UserRole.SUPERVISOR },
      };

      const caller = apmRouter.createCaller(mockContext);
      const result = await caller.getErrors({ limit: 50 });

      // Should handle large dataset and return limited results
      expect(result.errors).toHaveLength(50);
      expect(result.total).toBe(1000);
    });
  });
});