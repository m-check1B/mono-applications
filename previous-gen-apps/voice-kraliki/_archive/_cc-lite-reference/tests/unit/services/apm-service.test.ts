import { describe, it, expect, beforeEach, afterEach, vi, beforeAll, afterAll } from 'vitest';
import { EventEmitter } from 'events';
import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { APMService } from '../../../server/services/apm-service';
import { testDb } from '../../setup';

// Mock dependencies
vi.mock('../../../server/services/redis-service', () => ({
  redisService: {
    setSession: vi.fn(),
    getSession: vi.fn(),
    ping: vi.fn(),
    incrementCounter: vi.fn(),
    isReady: vi.fn().mockReturnValue(true),
    client: {
      keys: vi.fn(),
      get: vi.fn(),
      del: vi.fn(),
    },
  },
}));

vi.mock('../../../server/lib/prisma-client', () => ({
  prisma: {
    $queryRaw: vi.fn(),
  },
}));

// Mock process and os modules
const mockProcess = {
  cpuUsage: vi.fn().mockReturnValue({ user: 1000000, system: 500000 }),
  memoryUsage: vi.fn().mockReturnValue({
    rss: 50000000,
    heapTotal: 30000000,
    heapUsed: 20000000,
    external: 5000000,
    arrayBuffers: 1000000,
  }),
  uptime: vi.fn().mockReturnValue(3600),
  pid: 12345,
  env: { NODE_ENV: 'test' },
  on: vi.fn(),
  exit: vi.fn(),
};

// Move os mock to import level above

// Mock os module first
vi.mock('os', () => ({
  totalmem: vi.fn().mockReturnValue(8000000000),
  freemem: vi.fn().mockReturnValue(4000000000),
  loadavg: vi.fn().mockReturnValue([0.5, 0.7, 0.8]),
  cpus: vi.fn().mockReturnValue(Array(4).fill({})),
}));

// Mock Fastify instance
const mockFastify = {
  addHook: vi.fn(),
  log: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
} as unknown as FastifyInstance;

describe('APMService', () => {
  let apmService: APMService;
  let mockRedisService: any;
  let mockPrisma: any;

  beforeAll(() => {
    // Mock global.gc for heap statistics tests
    vi.stubGlobal('gc', vi.fn());

    // Set up process mocks after everything is loaded
    vi.stubGlobal('process', mockProcess);
  });

  beforeEach(async () => {
    // Reset all mocks
    vi.clearAllMocks();
    vi.clearAllTimers();
    vi.useFakeTimers();

    // Get mocked services
    const { redisService } = await import('../../../server/services/redis-service');
    const { prisma } = await import('../../../server/lib/prisma-client');
    mockRedisService = redisService;
    mockPrisma = prisma;

    // Create fresh APM service instance
    apmService = new APMService();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();

    // Use cleanup method
    if (apmService && typeof apmService.cleanup === 'function') {
      apmService.cleanup();
    }
  });

  afterAll(() => {
    vi.unstubAllGlobals();
  });

  describe('initialization', () => {
    it('should initialize APM service with default configuration', () => {
      expect(apmService).toBeInstanceOf(APMService);
      expect(apmService).toBeInstanceOf(EventEmitter);
    });

    it('should set up request tracking hooks when initialized with Fastify', async () => {
      await apmService.initialize(mockFastify);

      expect(mockFastify.addHook).toHaveBeenCalledWith('onRequest', expect.any(Function));
      expect(mockFastify.addHook).toHaveBeenCalledWith('onResponse', expect.any(Function));
      expect(mockFastify.addHook).toHaveBeenCalledWith('onError', expect.any(Function));
    });

    it('should start health checks and metrics collection on initialization', async () => {
      const startHealthChecksSpy = vi.spyOn(apmService as any, 'startHealthChecks');
      const startMetricsCollectionSpy = vi.spyOn(apmService as any, 'startMetricsCollection');

      await apmService.initialize(mockFastify);

      expect(startHealthChecksSpy).toHaveBeenCalled();
      expect(startMetricsCollectionSpy).toHaveBeenCalled();
    });
  });

  describe('recordMetric', () => {
    it('should record performance metrics', () => {
      const metric = {
        timestamp: new Date(),
        type: 'api' as const,
        operation: 'GET /test',
        duration: 150,
        success: true,
        metadata: { statusCode: 200 },
      };

      const metricListener = vi.fn();
      apmService.on('metric', metricListener);

      apmService.recordMetric(metric);

      expect(metricListener).toHaveBeenCalledWith(metric);
    });

    it('should emit performance degradation alert for slow operations', () => {
      const slowMetric = {
        timestamp: new Date(),
        type: 'database' as const,
        operation: 'SELECT * FROM users',
        duration: 8000, // 8 seconds (slow threshold * 2)
        success: true,
      };

      const degradationListener = vi.fn();
      apmService.on('performance:degraded', degradationListener);

      apmService.recordMetric(slowMetric);

      expect(degradationListener).toHaveBeenCalledWith(slowMetric);
    });

    it('should limit metrics in memory to prevent memory leaks', () => {
      const maxMetrics = (apmService as any).config.maxMetricsInMemory;

      // Add more metrics than the limit
      for (let i = 0; i < maxMetrics + 100; i++) {
        apmService.recordMetric({
          timestamp: new Date(),
          type: 'api',
          operation: `test-${i}`,
          duration: 100,
          success: true,
        });
      }

      const metrics = (apmService as any).metrics;
      expect(metrics.length).toBeLessThanOrEqual(maxMetrics);
    });
  });

  describe('recordError', () => {
    it('should record error events', () => {
      const error = {
        timestamp: new Date(),
        level: 'error' as const,
        message: 'Database connection failed',
        stack: 'Error: Database connection failed\n    at test.js:1:1',
        context: { operation: 'user-login' },
        requestId: 'req-123',
      };

      const errorListener = vi.fn();
      apmService.on('error', errorListener);

      apmService.recordError(error);

      expect(errorListener).toHaveBeenCalledWith(error);
    });

    it('should store critical errors in Redis', async () => {
      const criticalError = {
        timestamp: new Date(),
        level: 'critical' as const,
        message: 'System failure',
        context: { severity: 'high' },
      };

      apmService.recordError(criticalError);

      // Allow async operations to complete
      await new Promise(resolve => setTimeout(resolve, 0));

      expect(mockRedisService.setSession).toHaveBeenCalledWith(
        expect.stringMatching(/^apm:errors:/),
        criticalError,
        604800 // 7 days in seconds
      );
      expect(mockRedisService.incrementCounter).toHaveBeenCalledWith('apm:errors:critical:daily');
      expect(mockRedisService.incrementCounter).toHaveBeenCalledWith('apm:errors:total');
    });

    it('should store errors in production environment', async () => {
      // Temporarily set production environment
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      // Create new service instance for production
      const prodService = new APMService();

      const error = {
        timestamp: new Date(),
        level: 'error' as const,
        message: 'Production error',
      };

      prodService.recordError(error);

      // Allow async operations to complete
      await new Promise(resolve => setTimeout(resolve, 0));

      expect(mockRedisService.setSession).toHaveBeenCalled();

      // Restore environment
      process.env.NODE_ENV = originalEnv;
    });

    it('should limit errors in memory', () => {
      const maxErrors = (apmService as any).config.maxErrorsInMemory;

      for (let i = 0; i < maxErrors + 50; i++) {
        apmService.recordError({
          timestamp: new Date(),
          level: 'warning',
          message: `Error ${i}`,
        });
      }

      const errors = (apmService as any).errors;
      expect(errors.length).toBeLessThanOrEqual(maxErrors);
    });

    it('should handle Redis storage errors gracefully', async () => {
      mockRedisService.setSession.mockRejectedValue(new Error('Redis error'));

      const error = {
        timestamp: new Date(),
        level: 'critical' as const,
        message: 'Test error',
      };

      // Should not throw
      expect(() => apmService.recordError(error)).not.toThrow();

      await new Promise(resolve => setTimeout(resolve, 0));

      // Should still try to store
      expect(mockRedisService.setSession).toHaveBeenCalled();
    });
  });

  describe('getSystemMetrics', () => {
    it('should return comprehensive system metrics', async () => {
      // Add some metrics first
      apmService.recordMetric({
        timestamp: new Date(),
        type: 'api',
        operation: 'GET /test',
        duration: 100,
        success: true,
      });

      apmService.recordMetric({
        timestamp: new Date(),
        type: 'api',
        operation: 'POST /users',
        duration: 200,
        success: false,
      });

      const metrics = await apmService.getSystemMetrics();

      expect(metrics).toMatchObject({
        timestamp: expect.any(Date),
        cpu: {
          usage: expect.any(Number),
          loadAverage: expect.any(Array),
        },
        memory: {
          total: expect.any(Number),
          used: expect.any(Number),
          free: expect.any(Number),
          percentage: expect.any(Number),
        },
        process: {
          uptime: expect.any(Number),
          memoryUsage: expect.any(Object),
          pid: expect.any(Number),
        },
        requests: {
          total: expect.any(Number),
          success: expect.any(Number),
          errors: expect.any(Number),
          avgResponseTime: expect.any(Number),
        },
      });

      expect(metrics.memory.percentage).toBeGreaterThan(0);
      expect(metrics.memory.percentage).toBeLessThanOrEqual(100);
    });

    it('should emit memory alert when threshold exceeded', async () => {
      // Mock high memory usage
      mockOs.totalmem.mockReturnValue(1000000000); // 1GB
      mockOs.freemem.mockReturnValue(50000000);    // 50MB (95% used)

      const memoryAlertListener = vi.fn();
      apmService.on('alert:memory', memoryAlertListener);

      await apmService.getSystemMetrics();

      expect(memoryAlertListener).toHaveBeenCalledWith(
        expect.objectContaining({
          percentage: expect.any(Number),
        })
      );
    });

    it('should emit CPU alert when load average is high', async () => {
      // Mock high CPU load
      mockOs.loadavg.mockReturnValue([5.0, 4.5, 4.0]); // High load for 4 cores
      mockOs.cpus.mockReturnValue(Array(4).fill({}));

      const cpuAlertListener = vi.fn();
      apmService.on('alert:cpu', cpuAlertListener);

      await apmService.getSystemMetrics();

      expect(cpuAlertListener).toHaveBeenCalledWith(
        expect.objectContaining({
          loadAverage: expect.any(Array),
        })
      );
    });

    it('should calculate request statistics correctly', async () => {
      // Add mixed success/failure metrics
      for (let i = 0; i < 10; i++) {
        apmService.recordMetric({
          timestamp: new Date(),
          type: 'api',
          operation: `test-${i}`,
          duration: 100 + i * 10,
          success: i < 7, // 7 successful, 3 failed
        });
      }

      const metrics = await apmService.getSystemMetrics();

      expect(metrics.requests.success).toBe(7);
      expect(metrics.requests.errors).toBe(3);
      expect(metrics.requests.avgResponseTime).toBeGreaterThan(0);
    });
  });

  describe('health checks', () => {
    it('should perform database health check', async () => {
      mockPrisma.$queryRaw.mockResolvedValue([{ result: 1 }]);

      const healthChecks = await (apmService as any).performHealthChecks();

      expect(healthChecks.has('database')).toBe(true);
      const dbHealth = healthChecks.get('database');
      expect(dbHealth.service).toBe('PostgreSQL');
      expect(dbHealth.status).toBe('healthy');
      expect(dbHealth.responseTime).toBeGreaterThanOrEqual(0);
    });

    it('should detect unhealthy database', async () => {
      mockPrisma.$queryRaw.mockRejectedValue(new Error('Connection failed'));

      const healthChecks = await (apmService as any).performHealthChecks();

      const dbHealth = healthChecks.get('database');
      expect(dbHealth.status).toBe('unhealthy');
      expect(dbHealth.message).toBe('Connection failed');
    });

    it('should perform Redis health check', async () => {
      mockRedisService.ping.mockResolvedValue('PONG');

      const healthChecks = await (apmService as any).performHealthChecks();

      expect(healthChecks.has('redis')).toBe(true);
      const redisHealth = healthChecks.get('redis');
      expect(redisHealth.service).toBe('Redis');
      expect(redisHealth.status).toBe('healthy');
    });

    it('should detect unhealthy Redis', async () => {
      mockRedisService.ping.mockRejectedValue(new Error('Redis down'));

      const healthChecks = await (apmService as any).performHealthChecks();

      const redisHealth = healthChecks.get('redis');
      expect(redisHealth.status).toBe('unhealthy');
      expect(redisHealth.message).toBe('Redis down');
    });

    it('should assess memory health status', async () => {
      // Test healthy memory
      mockOs.totalmem.mockReturnValue(8000000000);
      mockOs.freemem.mockReturnValue(6000000000); // 25% used

      let healthChecks = await (apmService as any).performHealthChecks();
      expect(healthChecks.get('memory').status).toBe('healthy');

      // Test degraded memory
      mockOs.freemem.mockReturnValue(1600000000); // 80% used
      healthChecks = await (apmService as any).performHealthChecks();
      expect(healthChecks.get('memory').status).toBe('degraded');

      // Test unhealthy memory
      mockOs.freemem.mockReturnValue(400000000); // 95% used
      healthChecks = await (apmService as any).performHealthChecks();
      expect(healthChecks.get('memory').status).toBe('unhealthy');
    });

    it('should assess CPU health status', async () => {
      mockOs.cpus.mockReturnValue(Array(4).fill({}));

      // Test healthy CPU
      mockOs.loadavg.mockReturnValue([1.0, 1.2, 1.1]); // Low load
      let healthChecks = await (apmService as any).performHealthChecks();
      expect(healthChecks.get('cpu').status).toBe('healthy');

      // Test degraded CPU
      mockOs.loadavg.mockReturnValue([3.0, 2.8, 2.9]); // 70% of cores
      healthChecks = await (apmService as any).performHealthChecks();
      expect(healthChecks.get('cpu').status).toBe('degraded');

      // Test unhealthy CPU
      mockOs.loadavg.mockReturnValue([5.0, 4.8, 4.9]); // Over 100% of cores
      healthChecks = await (apmService as any).performHealthChecks();
      expect(healthChecks.get('cpu').status).toBe('unhealthy');
    });
  });

  describe('error rate monitoring', () => {
    it('should check error rate and emit alerts', () => {
      const alertListener = vi.fn();
      apmService.on('alert:errorRate', alertListener);

      // Add metrics with high error rate (60% errors)
      for (let i = 0; i < 10; i++) {
        apmService.recordMetric({
          timestamp: new Date(),
          type: 'api',
          operation: `test-${i}`,
          duration: 100,
          success: i < 4, // 4 success, 6 errors = 60% error rate
        });
      }

      // Trigger error rate check
      (apmService as any).checkErrorRate();

      expect(alertListener).toHaveBeenCalledWith(
        expect.objectContaining({
          rate: expect.any(Number),
          threshold: expect.any(Number),
          period: '5 minutes',
        })
      );
    });

    it('should not alert when error rate is below threshold', () => {
      const alertListener = vi.fn();
      apmService.on('alert:errorRate', alertListener);

      // Add metrics with low error rate (10% errors)
      for (let i = 0; i < 10; i++) {
        apmService.recordMetric({
          timestamp: new Date(),
          type: 'api',
          operation: `test-${i}`,
          duration: 100,
          success: i !== 0, // 1 error, 9 success = 10% error rate
        });
      }

      (apmService as any).checkErrorRate();

      expect(alertListener).not.toHaveBeenCalled();
    });

    it('should only consider recent metrics for error rate', () => {
      const alertListener = vi.fn();
      apmService.on('alert:errorRate', alertListener);

      // Add old metrics (should be ignored)
      for (let i = 0; i < 5; i++) {
        apmService.recordMetric({
          timestamp: new Date(Date.now() - 10 * 60 * 1000), // 10 minutes ago
          type: 'api',
          operation: `old-${i}`,
          duration: 100,
          success: false, // All errors
        });
      }

      // Add recent metrics with good success rate
      for (let i = 0; i < 10; i++) {
        apmService.recordMetric({
          timestamp: new Date(),
          type: 'api',
          operation: `recent-${i}`,
          duration: 100,
          success: true, // All success
        });
      }

      (apmService as any).checkErrorRate();

      expect(alertListener).not.toHaveBeenCalled();
    });
  });

  describe('request tracking', () => {
    it('should generate unique request IDs', () => {
      const id1 = (apmService as any).generateRequestId();
      const id2 = (apmService as any).generateRequestId();

      expect(id1).toMatch(/^req_\d+_[a-z0-9]+$/);
      expect(id2).toMatch(/^req_\d+_[a-z0-9]+$/);
      expect(id1).not.toBe(id2);
    });

    it('should track slow requests as warnings', async () => {
      await apmService.initialize(mockFastify);

      // Get the onResponse hook
      const onResponseHook = mockFastify.addHook.mock.calls
        .find(call => call[0] === 'onResponse')[1];

      const mockRequest = {
        id: 'test-req-1',
        method: 'GET',
        url: '/slow-endpoint',
        headers: { 'user-agent': 'test-agent' },
        startTime: Date.now() - 5000, // 5 seconds ago (slow)
      } as any;

      const mockReply = {
        statusCode: 200,
      } as any;

      const errorListener = vi.fn();
      apmService.on('error', errorListener);

      await onResponseHook(mockRequest, mockReply);

      expect(errorListener).toHaveBeenCalledWith(
        expect.objectContaining({
          level: 'warning',
          message: expect.stringContaining('Slow request detected'),
          context: expect.objectContaining({
            duration: expect.any(Number),
            threshold: expect.any(Number),
          }),
        })
      );
    });

    it('should track request counts by endpoint', async () => {
      await apmService.initialize(mockFastify);

      const onResponseHook = mockFastify.addHook.mock.calls
        .find(call => call[0] === 'onResponse')[1];

      // Simulate multiple requests to same endpoint
      for (let i = 0; i < 5; i++) {
        const mockRequest = {
          id: `test-req-${i}`,
          method: 'GET',
          url: '/api/users?page=1',
          headers: {},
          startTime: Date.now(),
        } as any;

        await onResponseHook(mockRequest, { statusCode: 200 } as any);
      }

      const requestCounts = (apmService as any).requestCounts;
      expect(requestCounts.get('GET /api/users')).toBe(5);
    });
  });

  describe('dashboard data', () => {
    it('should aggregate comprehensive dashboard data', async () => {
      // Add some test data
      apmService.recordMetric({
        timestamp: new Date(),
        type: 'api',
        operation: 'GET /users',
        duration: 150,
        success: true,
      });

      apmService.recordError({
        timestamp: new Date(),
        level: 'warning',
        message: 'Test warning',
      });

      const dashboard = await apmService.getDashboardData();

      expect(dashboard).toMatchObject({
        system: expect.objectContaining({
          cpu: expect.any(Object),
          memory: expect.any(Object),
          process: expect.any(Object),
          requests: expect.any(Object),
        }),
        health: expect.any(Array),
        metrics: expect.objectContaining({
          recent: expect.any(Array),
          responseTimePercentiles: expect.objectContaining({
            p50: expect.any(Number),
            p95: expect.any(Number),
            p99: expect.any(Number),
          }),
          topEndpoints: expect.any(Array),
        }),
        errors: expect.objectContaining({
          recent: expect.any(Array),
          byLevel: expect.objectContaining({
            critical: expect.any(Number),
            error: expect.any(Number),
            warning: expect.any(Number),
          }),
        }),
        timestamp: expect.any(Date),
      });
    });

    it('should calculate response time percentiles correctly', async () => {
      // Add response times: [100, 200, 300, 400, 500]
      const responseTimes = [100, 200, 300, 400, 500];
      responseTimes.forEach(time => {
        (apmService as any).responseTimes.push(time);
      });

      const dashboard = await apmService.getDashboardData();

      expect(dashboard.metrics.responseTimePercentiles.p50).toBe(300); // 50th percentile
      expect(dashboard.metrics.responseTimePercentiles.p95).toBe(500); // 95th percentile
      expect(dashboard.metrics.responseTimePercentiles.p99).toBe(500); // 99th percentile
    });

    it('should group errors by level', async () => {
      apmService.recordError({
        timestamp: new Date(),
        level: 'critical',
        message: 'Critical error 1',
      });

      apmService.recordError({
        timestamp: new Date(),
        level: 'critical',
        message: 'Critical error 2',
      });

      apmService.recordError({
        timestamp: new Date(),
        level: 'error',
        message: 'Regular error',
      });

      apmService.recordError({
        timestamp: new Date(),
        level: 'warning',
        message: 'Warning message',
      });

      const dashboard = await apmService.getDashboardData();

      expect(dashboard.errors.byLevel).toEqual({
        critical: 2,
        error: 1,
        warning: 1,
      });
    });
  });

  describe('error handlers', () => {
    it('should set up global error handlers', () => {
      expect(mockProcess.on).toHaveBeenCalledWith('uncaughtException', expect.any(Function));
      expect(mockProcess.on).toHaveBeenCalledWith('unhandledRejection', expect.any(Function));
      expect(mockProcess.on).toHaveBeenCalledWith('warning', expect.any(Function));
    });

    it('should record uncaught exceptions', () => {
      const errorListener = vi.fn();
      apmService.on('error', errorListener);

      // Get the uncaught exception handler
      const uncaughtHandler = mockProcess.on.mock.calls
        .find(call => call[0] === 'uncaughtException')[1];

      const testError = new Error('Uncaught test error');
      uncaughtHandler(testError);

      expect(errorListener).toHaveBeenCalledWith(
        expect.objectContaining({
          level: 'critical',
          message: expect.stringContaining('Uncaught Exception'),
          stack: expect.any(String),
          context: { type: 'uncaughtException' },
        })
      );
    });

    it('should record unhandled promise rejections', () => {
      const errorListener = vi.fn();
      apmService.on('error', errorListener);

      const rejectionHandler = mockProcess.on.mock.calls
        .find(call => call[0] === 'unhandledRejection')[1];

      const testReason = new Error('Promise rejection');
      rejectionHandler(testReason, Promise.resolve());

      expect(errorListener).toHaveBeenCalledWith(
        expect.objectContaining({
          level: 'critical',
          message: expect.stringContaining('Unhandled Rejection'),
          context: { type: 'unhandledRejection' },
        })
      );
    });

    it('should record process warnings', () => {
      const errorListener = vi.fn();
      apmService.on('error', errorListener);

      const warningHandler = mockProcess.on.mock.calls
        .find(call => call[0] === 'warning')[1];

      const testWarning = {
        name: 'DeprecationWarning',
        message: 'Feature is deprecated',
        stack: 'DeprecationWarning: Feature is deprecated\n    at test.js:1:1',
      };

      warningHandler(testWarning);

      expect(errorListener).toHaveBeenCalledWith(
        expect.objectContaining({
          level: 'warning',
          message: 'Feature is deprecated',
          context: { type: 'warning', name: 'DeprecationWarning' },
        })
      );
    });
  });

  describe('metrics collection intervals', () => {
    it('should start metrics collection interval', async () => {
      const setIntervalSpy = vi.spyOn(global, 'setInterval');

      await apmService.initialize(mockFastify);

      expect(setIntervalSpy).toHaveBeenCalledWith(
        expect.any(Function),
        60000 // 1 minute interval
      );
    });

    it('should emit system metrics events', async () => {
      const metricsListener = vi.fn();
      apmService.on('system:metrics', metricsListener);

      // Trigger metrics collection manually
      const metricsCollectionFn = (apmService as any).startMetricsCollection.bind(apmService);
      metricsCollectionFn();

      // Fast forward time to trigger interval
      vi.advanceTimersByTime(60000);

      await vi.runAllTimersAsync();

      expect(metricsListener).toHaveBeenCalledWith(
        expect.objectContaining({
          timestamp: expect.any(Date),
          cpu: expect.any(Object),
          memory: expect.any(Object),
        })
      );
    });

    it('should store metrics in Redis in production', async () => {
      // Set production environment
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      const prodService = new APMService();
      await prodService.initialize(mockFastify);

      // Trigger metrics collection
      vi.advanceTimersByTime(60000);
      await vi.runAllTimersAsync();

      expect(mockRedisService.setSession).toHaveBeenCalledWith(
        expect.stringMatching(/^apm:metrics:/),
        expect.any(Object),
        86400 // 24 hours
      );

      // Restore environment
      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('graceful shutdown', () => {
    it('should set up shutdown handlers', () => {
      expect(mockProcess.on).toHaveBeenCalledWith('SIGTERM', expect.any(Function));
      expect(mockProcess.on).toHaveBeenCalledWith('SIGINT', expect.any(Function));
    });

    it('should flush metrics on shutdown', async () => {
      // Add some metrics
      apmService.recordMetric({
        timestamp: new Date(),
        type: 'api',
        operation: 'test',
        duration: 100,
        success: true,
      });

      apmService.recordError({
        timestamp: new Date(),
        level: 'error',
        message: 'test error',
      });

      // Get shutdown handler
      const shutdownHandler = mockProcess.on.mock.calls
        .find(call => call[0] === 'SIGTERM')[1];

      await shutdownHandler('SIGTERM');

      expect(mockRedisService.setSession).toHaveBeenCalledWith(
        expect.stringMatching(/^apm:metrics:shutdown:/),
        expect.any(Array),
        86400
      );

      expect(mockRedisService.setSession).toHaveBeenCalledWith(
        expect.stringMatching(/^apm:errors:shutdown:/),
        expect.any(Array),
        604800
      );
    });

    it('should handle shutdown errors gracefully', async () => {
      mockRedisService.setSession.mockRejectedValue(new Error('Redis error'));

      const shutdownHandler = mockProcess.on.mock.calls
        .find(call => call[0] === 'SIGTERM')[1];

      // Should not throw
      await expect(shutdownHandler('SIGTERM')).resolves.toBeUndefined();
    });
  });

  describe('heap statistics collection', () => {
    it('should collect heap statistics when gc is available', () => {
      const setIntervalSpy = vi.spyOn(global, 'setInterval');

      // Create service that should detect global.gc
      new APMService();

      expect(setIntervalSpy).toHaveBeenCalledWith(
        expect.any(Function),
        60000 // 1 minute
      );
    });

    it('should record GC metrics', () => {
      const metricListener = vi.fn();
      apmService.on('metric', metricListener);

      // Trigger GC collection manually if the interval was set
      if (global.gc) {
        // Find the GC interval function from the constructor
        const gcInterval = vi.mocked(setInterval).mock.calls
          .find(call => call[1] === 60000); // GC runs every minute

        if (gcInterval) {
          const gcFunction = gcInterval[0] as Function;
          gcFunction();

          expect(metricListener).toHaveBeenCalledWith(
            expect.objectContaining({
              type: 'external',
              operation: 'gc',
              duration: 0,
              success: true,
              metadata: expect.objectContaining({
                rss: expect.any(Number),
                heapTotal: expect.any(Number),
                heapUsed: expect.any(Number),
              }),
            })
          );
        }
      }
    });
  });
});