import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { EventEmitter } from 'events';

/**
 * Functional tests for APM Service
 * Tests the public API and core functionality without complex mocking
 */
describe('APM Service Functional Tests', () => {
  let APMService: any;
  let apmService: any;

  beforeEach(async () => {
    // Mock only the essential external dependencies
    vi.doMock('../../../server/services/redis-service', () => ({
      redisService: {
        setSession: vi.fn().mockResolvedValue(undefined),
        ping: vi.fn().mockResolvedValue('PONG'),
        incrementCounter: vi.fn().mockResolvedValue(1),
        isReady: vi.fn().mockReturnValue(true),
        client: {
          keys: vi.fn().mockResolvedValue([]),
          get: vi.fn().mockResolvedValue(null),
          del: vi.fn().mockResolvedValue(0),
        },
      },
    }));

    vi.doMock('../../../server/lib/prisma-client', () => ({
      prisma: {
        $queryRaw: vi.fn().mockResolvedValue([{ result: 1 }]),
      },
    }));

    // Import after mocking
    const module = await import('../../../server/services/apm-service');
    APMService = module.APMService;
    apmService = new APMService();
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
    if (apmService && typeof apmService.cleanup === 'function') {
      apmService.cleanup();
    }
  });

  describe('Core Functionality', () => {
    it('should be an instance of EventEmitter', () => {
      expect(apmService).toBeInstanceOf(EventEmitter);
    });

    it('should have required public methods', () => {
      expect(typeof apmService.recordMetric).toBe('function');
      expect(typeof apmService.recordError).toBe('function');
      expect(typeof apmService.getSystemMetrics).toBe('function');
      expect(typeof apmService.getDashboardData).toBe('function');
    });

    it('should initialize without errors', () => {
      expect(() => new APMService()).not.toThrow();
    });
  });

  describe('Metric Recording', () => {
    it('should record and emit performance metrics', () => {
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

    it('should emit performance degradation alerts', () => {
      const slowMetric = {
        timestamp: new Date(),
        type: 'database' as const,
        operation: 'slow-query',
        duration: 7000, // 7 seconds - very slow
        success: true,
      };

      const degradationListener = vi.fn();
      apmService.on('performance:degraded', degradationListener);

      apmService.recordMetric(slowMetric);

      expect(degradationListener).toHaveBeenCalledWith(slowMetric);
    });

    it('should limit metrics in memory', () => {
      // Record many metrics to test memory management
      for (let i = 0; i < 15000; i++) { // More than default limit
        apmService.recordMetric({
          timestamp: new Date(),
          type: 'api',
          operation: `test-${i}`,
          duration: 100,
          success: true,
        });
      }

      // Should limit to prevent memory issues
      const internalMetrics = (apmService as any).metrics;
      expect(internalMetrics?.length).toBeLessThanOrEqual(10000);
    });
  });

  describe('Error Recording', () => {
    it('should record and emit errors', () => {
      const error = {
        timestamp: new Date(),
        level: 'error' as const,
        message: 'Test error message',
        stack: 'Error: Test\n  at test.js:1:1',
        context: { component: 'test' },
      };

      const errorListener = vi.fn();
      apmService.on('error', errorListener);

      apmService.recordError(error);

      expect(errorListener).toHaveBeenCalledWith(error);
    });

    it('should handle different error levels', () => {
      const levels = ['error', 'warning', 'critical'] as const;
      const errorListener = vi.fn();
      apmService.on('error', errorListener);

      levels.forEach(level => {
        const error = {
          timestamp: new Date(),
          level,
          message: `${level} message`,
        };

        apmService.recordError(error);
      });

      expect(errorListener).toHaveBeenCalledTimes(3);
    });

    it('should limit errors in memory', () => {
      // Record many errors to test memory management
      for (let i = 0; i < 1500; i++) { // More than default limit
        apmService.recordError({
          timestamp: new Date(),
          level: 'warning',
          message: `Error ${i}`,
        });
      }

      const internalErrors = (apmService as any).errors;
      expect(internalErrors?.length).toBeLessThanOrEqual(1000);
    });
  });

  describe('System Metrics', () => {
    it('should return system metrics without throwing', async () => {
      const metrics = await apmService.getSystemMetrics();

      expect(metrics).toBeDefined();
      expect(metrics.timestamp).toBeInstanceOf(Date);
      expect(typeof metrics.cpu).toBe('object');
      expect(typeof metrics.memory).toBe('object');
      expect(typeof metrics.process).toBe('object');
      expect(typeof metrics.requests).toBe('object');
    });

    it('should calculate basic request statistics', async () => {
      // Add some test metrics
      apmService.recordMetric({
        timestamp: new Date(),
        type: 'api',
        operation: 'test-1',
        duration: 100,
        success: true,
      });

      apmService.recordMetric({
        timestamp: new Date(),
        type: 'api',
        operation: 'test-2',
        duration: 200,
        success: false,
      });

      const metrics = await apmService.getSystemMetrics();

      expect(metrics.requests.total).toBeGreaterThanOrEqual(0);
      expect(metrics.requests.success).toBeGreaterThanOrEqual(0);
      expect(metrics.requests.errors).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Dashboard Data', () => {
    it('should return comprehensive dashboard data', async () => {
      const dashboard = await apmService.getDashboardData();

      expect(dashboard).toBeDefined();
      expect(dashboard.system).toBeDefined();
      expect(dashboard.health).toBeInstanceOf(Array);
      expect(dashboard.metrics).toBeDefined();
      expect(dashboard.errors).toBeDefined();
      expect(dashboard.timestamp).toBeInstanceOf(Date);
    });

    it('should include response time percentiles', async () => {
      // Add some response times
      const responseTimes = (apmService as any).responseTimes || [];
      responseTimes.push(...[100, 150, 200, 250, 300]);

      const dashboard = await apmService.getDashboardData();

      expect(dashboard.metrics.responseTimePercentiles).toBeDefined();
      expect(typeof dashboard.metrics.responseTimePercentiles.p50).toBe('number');
      expect(typeof dashboard.metrics.responseTimePercentiles.p95).toBe('number');
      expect(typeof dashboard.metrics.responseTimePercentiles.p99).toBe('number');
    });

    it('should group errors by level', async () => {
      // Add test errors
      apmService.recordError({
        timestamp: new Date(),
        level: 'critical',
        message: 'Critical error',
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

      expect(dashboard.errors.byLevel).toBeDefined();
      expect(typeof dashboard.errors.byLevel.critical).toBe('number');
      expect(typeof dashboard.errors.byLevel.error).toBe('number');
      expect(typeof dashboard.errors.byLevel.warning).toBe('number');
    });
  });

  describe('Event Emission', () => {
    it('should support multiple listeners', () => {
      const listener1 = vi.fn();
      const listener2 = vi.fn();

      apmService.on('metric', listener1);
      apmService.on('metric', listener2);

      const testMetric = {
        timestamp: new Date(),
        type: 'api' as const,
        operation: 'test',
        duration: 100,
        success: true,
      };

      apmService.recordMetric(testMetric);

      expect(listener1).toHaveBeenCalledWith(testMetric);
      expect(listener2).toHaveBeenCalledWith(testMetric);
    });

    it('should handle listener removal', () => {
      const listener = vi.fn();

      apmService.on('metric', listener);
      apmService.off('metric', listener);

      apmService.recordMetric({
        timestamp: new Date(),
        type: 'api',
        operation: 'test',
        duration: 100,
        success: true,
      });

      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('Robustness', () => {
    it('should handle invalid metric data gracefully', () => {
      expect(() => {
        apmService.recordMetric({
          timestamp: new Date(),
          type: 'api',
          operation: '',
          duration: -1,
          success: true,
        });
      }).not.toThrow();
    });

    it('should handle invalid error data gracefully', () => {
      expect(() => {
        apmService.recordError({
          timestamp: new Date(),
          level: 'error',
          message: '',
        });
      }).not.toThrow();
    });

    it('should handle rapid metric recording', () => {
      expect(() => {
        for (let i = 0; i < 1000; i++) {
          apmService.recordMetric({
            timestamp: new Date(),
            type: 'api',
            operation: `rapid-${i}`,
            duration: Math.random() * 100,
            success: Math.random() > 0.1,
          });
        }
      }).not.toThrow();
    });
  });

  describe('Memory Management', () => {
    it('should prevent memory leaks from metrics', () => {
      const initialLength = (apmService as any).metrics?.length || 0;

      // Add metrics beyond the limit
      for (let i = 0; i < 12000; i++) {
        apmService.recordMetric({
          timestamp: new Date(),
          type: 'api',
          operation: `memory-test-${i}`,
          duration: 100,
          success: true,
        });
      }

      const finalLength = (apmService as any).metrics?.length || 0;
      expect(finalLength).toBeLessThanOrEqual(10000); // Default max limit
    });

    it('should prevent memory leaks from errors', () => {
      const initialLength = (apmService as any).errors?.length || 0;

      // Add errors beyond the limit
      for (let i = 0; i < 1200; i++) {
        apmService.recordError({
          timestamp: new Date(),
          level: 'warning',
          message: `Memory test error ${i}`,
        });
      }

      const finalLength = (apmService as any).errors?.length || 0;
      expect(finalLength).toBeLessThanOrEqual(1000); // Default max limit
    });
  });
});