/**
 * Tracing Service Unit Tests
 *
 * Tests the core tracing functionality in isolation
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { tracingService } from '../../server/services/tracing-service';

describe('TracingService', () => {
  beforeAll(async () => {
    // Initialize tracing for testing
    await tracingService.initialize({
      serviceName: 'cc-lite-test',
      serviceVersion: '2.0.0-test',
      environment: 'test',
      enableConsoleExporter: true,
      enablePrometheusMetrics: false,
      samplingRatio: 1.0
    });
  });

  afterAll(async () => {
    await tracingService.shutdown();
  });

  describe('Initialization', () => {
    it('should initialize successfully', () => {
      expect(tracingService.isHealthy()).toBe(true);
    });

    it('should return correct metrics', () => {
      const metrics = tracingService.getMetrics();
      expect(metrics.initialized).toBe(true);
      expect(metrics.serviceName).toBe('cc-lite-test');
      expect(metrics.serviceVersion).toBe('2.0.0-test');
      expect(metrics.environment).toBe('test');
    });
  });

  describe('Span Creation', () => {
    it('should create custom spans', () => {
      const span = tracingService.createSpan({
        name: 'test-span',
        attributes: {
          'test.attribute': 'test-value'
        }
      });

      expect(span).toBeDefined();
      span.end();
    });

    it('should create trace context', () => {
      const traceContext = tracingService.createTraceContext('user-123', 'session-456', 'org-789');

      expect(traceContext).toBeDefined();
      expect(traceContext.traceId).toBeDefined();
      expect(traceContext.spanId).toBeDefined();
      expect(traceContext.correlationId).toBeDefined();
      expect(traceContext.userId).toBe('user-123');
      expect(traceContext.sessionId).toBe('session-456');
      expect(traceContext.organizationId).toBe('org-789');
    });
  });

  describe('Function Tracing', () => {
    it('should trace successful function execution', async () => {
      const result = await tracingService.traceFunction(
        'test-function',
        async (span) => {
          span.setAttributes({
            'test.success': true
          });
          return 'success';
        },
        {
          'test.type': 'unit-test'
        }
      );

      expect(result).toBe('success');
    });

    it('should trace failed function execution', async () => {
      try {
        await tracingService.traceFunction(
          'test-error-function',
          async (span) => {
            span.setAttributes({
              'test.will_fail': true
            });
            throw new Error('Test error');
          }
        );
      } catch (error) {
        expect(error.message).toBe('Test error');
      }
    });
  });

  describe('Database Operation Tracing', () => {
    it('should trace database operations', async () => {
      const result = await tracingService.traceDatabaseOperation(
        'select',
        'users',
        async (span) => {
          span.setAttributes({
            'db.query': 'SELECT * FROM users WHERE id = ?'
          });
          return [{ id: 1, name: 'Test User' }];
        }
      );

      expect(result).toHaveLength(1);
      expect(result[0].name).toBe('Test User');
    });
  });

  describe('Redis Operation Tracing', () => {
    it('should trace Redis operations', async () => {
      const result = await tracingService.traceRedisOperation(
        'get',
        'test-key',
        async (span) => {
          span.setAttributes({
            'redis.ttl': 3600
          });
          return 'test-value';
        }
      );

      expect(result).toBe('test-value');
    });
  });

  describe('Call Flow Tracing', () => {
    it('should trace call center flows', async () => {
      const result = await tracingService.traceCallFlow(
        'incoming_call',
        'call-123',
        async (span) => {
          span.setAttributes({
            'call.from': '+1234567890',
            'call.to': '+0987654321',
            'call.agent_id': 'agent-456'
          });
          return { callId: 'call-123', status: 'connected' };
        }
      );

      expect(result.callId).toBe('call-123');
      expect(result.status).toBe('connected');
    });
  });

  describe('AI Operation Tracing', () => {
    it('should trace AI operations', async () => {
      const result = await tracingService.traceAiOperation(
        'openai',
        'completion',
        'gpt-3.5-turbo',
        async (span) => {
          span.setAttributes({
            'ai.prompt_tokens': 50,
            'ai.completion_tokens': 25,
            'ai.total_tokens': 75
          });
          return {
            text: 'AI generated response',
            usage: { total_tokens: 75 }
          };
        }
      );

      expect(result.text).toBe('AI generated response');
      expect(result.usage.total_tokens).toBe(75);
    });
  });

  describe('External API Tracing', () => {
    it('should trace external API calls', async () => {
      const result = await tracingService.traceExternalApiCall(
        'twilio',
        'POST',
        '/v1/calls',
        async (span) => {
          span.setAttributes({
            'http.status_code': 201,
            'twilio.call_sid': 'CA123456789'
          });
          return { sid: 'CA123456789', status: 'queued' };
        }
      );

      expect(result.sid).toBe('CA123456789');
      expect(result.status).toBe('queued');
    });
  });

  describe('tRPC Operation Tracing', () => {
    it('should trace tRPC operations', async () => {
      const result = await tracingService.traceTrpcOperation(
        'call',
        'list',
        async (span) => {
          span.setAttributes({
            'trpc.input.limit': 10,
            'trpc.input.offset': 0
          });
          return { calls: [], total: 0 };
        }
      );

      expect(result.calls).toEqual([]);
      expect(result.total).toBe(0);
    });
  });

  describe('Correlation', () => {
    it('should add correlation attributes', () => {
      tracingService.addCorrelationAttributes({
        'test.correlation': 'test-value',
        'test.timestamp': Date.now()
      });

      // This test mainly verifies the function doesn't throw
      expect(true).toBe(true);
    });

    it('should get trace headers', () => {
      const headers = tracingService.getTraceHeaders();
      expect(typeof headers).toBe('object');
    });
  });
});