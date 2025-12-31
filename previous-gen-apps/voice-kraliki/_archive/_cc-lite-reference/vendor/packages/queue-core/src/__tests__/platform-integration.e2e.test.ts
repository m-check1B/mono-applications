/**
 * Platform Integration E2E Tests
 *
 * Tests adapter integration with other platform services:
 * - Auth-core authentication flows
 * - Events-core event publishing
 * - Error handling across service boundaries
 * - Service mesh communication patterns
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import { RabbitMQAdapter } from '../adapters/rabbitmq.adapter';
import type { QueueMessage } from '../types/queue.types';

const TEST_RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://localhost:5672';
const TEST_TIMEOUT = 30000;

describe('Platform Service Integration E2E Tests', () => {
  let adapter: RabbitMQAdapter;

  beforeAll(async () => {
    adapter = new RabbitMQAdapter({
      url: TEST_RABBITMQ_URL,
      connectionName: 'platform-integration-test',
      prefetch: 10,
    });

    await adapter.connect();
  }, TEST_TIMEOUT);

  afterAll(async () => {
    await adapter.close();
  });

  beforeEach(async () => {
    // Clean test queues
    try {
      await adapter.purgeQueue('auth-events');
      await adapter.purgeQueue('platform-events');
      await adapter.purgeQueue('error-queue');
    } catch (error) {
      // Ignore if queues don't exist
    }
  });

  describe('Auth-Core Integration', () => {
    it('should process authentication events', async () => {
      const authEvent = {
        type: 'user.login',
        userId: 'user-123',
        sessionId: 'session-456',
        timestamp: new Date().toISOString(),
        ipAddress: '192.168.1.1',
        userAgent: 'Test Browser',
      };

      let receivedEvent: any = null;

      await adapter.createQueue('auth-events', { durable: true });
      await adapter.createExchange('auth', { type: 'topic', durable: true });
      await adapter.bindQueue('auth-events', 'auth', 'user.#');

      const consumerTag = await adapter.consume(
        'auth-events',
        async (message, ack) => {
          receivedEvent = message.payload;
          ack();
        }
      );

      await adapter.publish('auth', 'user.login', authEvent);
      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(receivedEvent).not.toBeNull();
      expect(receivedEvent.type).toBe('user.login');
      expect(receivedEvent.userId).toBe('user-123');

      await adapter.cancel(consumerTag);
    });

    it('should handle JWT token validation events', async () => {
      const tokenValidation = {
        type: 'token.validate',
        token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
        result: 'valid',
        userId: 'user-123',
        expiresAt: new Date(Date.now() + 3600000).toISOString(),
      };

      let validationResult: any = null;

      await adapter.createQueue('token-validations', { durable: true });
      await adapter.bindQueue('token-validations', 'auth', 'token.#');

      const consumerTag = await adapter.consume(
        'token-validations',
        async (message, ack) => {
          validationResult = message.payload;
          ack();
        }
      );

      await adapter.publish('auth', 'token.validate', tokenValidation);
      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(validationResult.result).toBe('valid');
      expect(validationResult.userId).toBe('user-123');

      await adapter.cancel(consumerTag);
    });

    it('should handle authorization failure events', async () => {
      const authFailure = {
        type: 'auth.failed',
        reason: 'invalid_credentials',
        attemptCount: 3,
        userId: 'user-456',
        timestamp: new Date().toISOString(),
      };

      let failureHandled = false;

      await adapter.createQueue('auth-failures', { durable: true });
      await adapter.bindQueue('auth-failures', 'auth', 'auth.failed');

      const consumerTag = await adapter.consume(
        'auth-failures',
        async (message, ack) => {
          failureHandled = true;
          // Trigger security alert
          expect(message.payload.attemptCount).toBe(3);
          ack();
        }
      );

      await adapter.publish('auth', 'auth.failed', authFailure);
      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(failureHandled).toBe(true);

      await adapter.cancel(consumerTag);
    });

    it('should correlate auth events with call events', async () => {
      const correlationId = 'auth-call-correlation-789';
      const events: any[] = [];

      await adapter.createQueue('correlated-events', { durable: true });
      await adapter.bindQueue('correlated-events', 'auth', 'user.#');
      await adapter.bindQueue('correlated-events', 'calls', 'call.#');

      const consumerTag = await adapter.consume(
        'correlated-events',
        async (message, ack) => {
          if (message.correlationId === correlationId) {
            events.push(message.payload);
          }
          ack();
        }
      );

      // User logs in
      await adapter.publish('auth', 'user.login', {
        type: 'user.login',
        userId: 'user-123',
      }, { correlationId });

      // User makes a call
      await adapter.publish('calls', 'call.inbound.started', {
        type: 'call.started',
        userId: 'user-123',
        callId: 'call-456',
      }, { correlationId });

      await new Promise(resolve => setTimeout(resolve, 1500));

      expect(events.length).toBe(2);
      expect(events[0].type).toBe('user.login');
      expect(events[1].type).toBe('call.started');

      await adapter.cancel(consumerTag);
    });
  });

  describe('Events-Core Integration', () => {
    it('should publish platform-wide events', async () => {
      const platformEvent = {
        type: 'system.config.updated',
        component: 'telephony',
        changes: {
          maxConcurrentCalls: 100,
          recordingEnabled: true,
        },
        timestamp: new Date().toISOString(),
      };

      let receivedEvent: any = null;

      await adapter.createQueue('platform-events', { durable: true });
      await adapter.bindQueue('platform-events', 'events', '');

      const consumerTag = await adapter.consume(
        'platform-events',
        async (message, ack) => {
          receivedEvent = message.payload;
          ack();
        }
      );

      await adapter.publish('events', '', platformEvent);
      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(receivedEvent).not.toBeNull();
      expect(receivedEvent.type).toBe('system.config.updated');
      expect(receivedEvent.component).toBe('telephony');

      await adapter.cancel(consumerTag);
    });

    it('should handle event fan-out to multiple services', async () => {
      const services = ['analytics', 'logging', 'monitoring'];
      const receivedByServices = new Set<string>();

      // Setup queues for each service
      for (const service of services) {
        await adapter.createQueue(`${service}-events`, { durable: true });
        await adapter.bindQueue(`${service}-events`, 'events', '');

        await adapter.consume(
          `${service}-events`,
          async (message, ack) => {
            receivedByServices.add(service);
            ack();
          }
        );
      }

      // Publish event that should reach all services
      await adapter.publish('events', '', {
        type: 'call.ended',
        callId: 'call-789',
        duration: 120,
      });

      await new Promise(resolve => setTimeout(resolve, 2000));

      expect(receivedByServices.size).toBe(3);
      expect(receivedByServices.has('analytics')).toBe(true);
      expect(receivedByServices.has('logging')).toBe(true);
      expect(receivedByServices.has('monitoring')).toBe(true);
    }, TEST_TIMEOUT);

    it('should handle event replay for failed consumers', async () => {
      const events: any[] = [];
      let failFirst = true;

      await adapter.createQueue('replay-test', {
        durable: true,
        deadLetterExchange: 'dlx',
        deadLetterRoutingKey: 'replay.failed',
      });

      await adapter.bindQueue('replay-test', 'events', '');

      const consumerTag = await adapter.consume(
        'replay-test',
        async (message, ack, nack) => {
          if (failFirst) {
            failFirst = false;
            nack(true); // Requeue for retry
          } else {
            events.push(message.payload);
            ack();
          }
        }
      );

      await adapter.publish('events', '', {
        type: 'test.replay',
        data: 'replay test data',
      });

      await new Promise(resolve => setTimeout(resolve, 2000));

      expect(events.length).toBe(1);
      expect(events[0].type).toBe('test.replay');

      await adapter.cancel(consumerTag);
    });
  });

  describe('Cross-Service Error Handling', () => {
    it('should handle service unavailability gracefully', async () => {
      const errorEvents: any[] = [];

      await adapter.createQueue('error-queue', { durable: true });

      const consumerTag = await adapter.consume(
        'error-queue',
        async (message, ack, nack, reject) => {
          try {
            // Simulate service call failure
            if (message.payload.simulateFailure) {
              throw new Error('Service unavailable');
            }
            ack();
          } catch (error) {
            errorEvents.push({ error, message: message.payload });
            reject(false); // Send to DLQ
          }
        }
      );

      await adapter.sendToQueue('error-queue', {
        simulateFailure: true,
        operation: 'process-call',
      });

      await new Promise(resolve => setTimeout(resolve, 1500));

      expect(errorEvents.length).toBe(1);
      expect(errorEvents[0].message.operation).toBe('process-call');

      await adapter.cancel(consumerTag);
    });

    it('should implement circuit breaker pattern', async () => {
      let failureCount = 0;
      let circuitOpen = false;
      const FAILURE_THRESHOLD = 3;

      await adapter.createQueue('circuit-test', { durable: true });

      const consumerTag = await adapter.consume(
        'circuit-test',
        async (message, ack, nack, reject) => {
          if (circuitOpen) {
            // Circuit is open, reject immediately
            reject(false);
            return;
          }

          try {
            // Simulate random failures
            if (Math.random() < 0.5) {
              throw new Error('Service failure');
            }
            ack();
            failureCount = 0; // Reset on success
          } catch (error) {
            failureCount++;
            if (failureCount >= FAILURE_THRESHOLD) {
              circuitOpen = true;
              // In real implementation, would set timer to half-open state
            }
            nack(true);
          }
        }
      );

      // Send multiple messages to trigger circuit breaker
      for (let i = 0; i < 10; i++) {
        await adapter.sendToQueue('circuit-test', { attempt: i });
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      await new Promise(resolve => setTimeout(resolve, 1500));

      // Circuit should have opened after threshold failures
      expect(failureCount).toBeGreaterThanOrEqual(FAILURE_THRESHOLD);

      await adapter.cancel(consumerTag);
    }, TEST_TIMEOUT);

    it('should implement retry with exponential backoff', async () => {
      const retryAttempts: number[] = [];

      await adapter.createQueue('retry-test', { durable: true });

      const consumerTag = await adapter.consume(
        'retry-test',
        async (message, ack, nack) => {
          const retryCount = message.metadata.retryCount || 0;
          retryAttempts.push(retryCount);

          if (retryCount < 3) {
            // Simulate failure and requeue with metadata
            const backoffMs = Math.pow(2, retryCount) * 1000;
            setTimeout(async () => {
              await adapter.sendToQueue('retry-test', message.payload, {
                headers: {
                  ...message.headers,
                  retryCount: retryCount + 1,
                },
              });
            }, backoffMs);
            ack(); // Ack original to prevent requeue
          } else {
            // Success after retries
            ack();
          }
        }
      );

      await adapter.sendToQueue('retry-test', {
        operation: 'retry-test',
      });

      await new Promise(resolve => setTimeout(resolve, 10000));

      // Should have attempted 0, 1, 2, 3 (4 total attempts)
      expect(retryAttempts.length).toBeGreaterThanOrEqual(3);

      await adapter.cancel(consumerTag);
    }, 15000);
  });

  describe('Service Mesh Communication', () => {
    it('should route messages between microservices', async () => {
      const services = {
        telephony: [] as any[],
        analytics: [] as any[],
        storage: [] as any[],
      };

      // Setup service queues
      await adapter.createExchange('service-mesh', { type: 'topic', durable: true });

      for (const [serviceName] of Object.entries(services)) {
        await adapter.createQueue(`service-${serviceName}`, { durable: true });
        await adapter.bindQueue(`service-${serviceName}`, 'service-mesh', `${serviceName}.#`);

        await adapter.consume(
          `service-${serviceName}`,
          async (message, ack) => {
            services[serviceName as keyof typeof services].push(message.payload);
            ack();
          }
        );
      }

      // Send targeted messages
      await adapter.publish('service-mesh', 'telephony.call.start', {
        operation: 'start-call',
      });

      await adapter.publish('service-mesh', 'analytics.track', {
        operation: 'track-event',
      });

      await adapter.publish('service-mesh', 'storage.save', {
        operation: 'save-recording',
      });

      await new Promise(resolve => setTimeout(resolve, 2000));

      expect(services.telephony.length).toBe(1);
      expect(services.analytics.length).toBe(1);
      expect(services.storage.length).toBe(1);
    }, TEST_TIMEOUT);

    it('should handle request-reply pattern', async () => {
      const replyQueue = 'reply-queue-' + Date.now();
      let replyReceived: any = null;

      // Setup reply queue
      await adapter.createQueue(replyQueue, {
        durable: false,
        autoDelete: true,
        exclusive: true,
      });

      // Setup reply consumer
      const replyConsumer = await adapter.consume(
        replyQueue,
        async (message, ack) => {
          replyReceived = message.payload;
          ack();
        }
      );

      // Setup request processor
      await adapter.createQueue('request-queue', { durable: true });
      const requestConsumer = await adapter.consume(
        'request-queue',
        async (message, ack) => {
          // Process request and send reply
          const response = {
            requestId: message.id,
            result: 'processed',
            data: message.payload,
          };

          if (message.headers?.replyTo) {
            await adapter.sendToQueue(message.headers.replyTo, response, {
              correlationId: message.correlationId,
            });
          }
          ack();
        }
      );

      // Send request with reply-to
      const correlationId = 'request-' + Date.now();
      await adapter.sendToQueue('request-queue', {
        operation: 'process-data',
        data: { test: 'value' },
      }, {
        correlationId,
        headers: { replyTo: replyQueue },
      });

      await new Promise(resolve => setTimeout(resolve, 2000));

      expect(replyReceived).not.toBeNull();
      expect(replyReceived.result).toBe('processed');

      await adapter.cancel(replyConsumer);
      await adapter.cancel(requestConsumer);
    });
  });

  describe('Monitoring and Observability', () => {
    it('should track message processing metrics', async () => {
      const metrics = {
        messagesProcessed: 0,
        processingTimes: [] as number[],
        errors: 0,
      };

      await adapter.createQueue('metrics-test', { durable: true });

      const consumerTag = await adapter.consume(
        'metrics-test',
        async (message, ack, nack, reject) => {
          const startTime = Date.now();

          try {
            // Simulate processing
            await new Promise(resolve => setTimeout(resolve, 50));

            metrics.messagesProcessed++;
            metrics.processingTimes.push(Date.now() - startTime);
            ack();
          } catch (error) {
            metrics.errors++;
            reject(false);
          }
        }
      );

      // Send test messages
      for (let i = 0; i < 10; i++) {
        await adapter.sendToQueue('metrics-test', { index: i });
      }

      await new Promise(resolve => setTimeout(resolve, 2000));

      expect(metrics.messagesProcessed).toBe(10);
      expect(metrics.processingTimes.length).toBe(10);
      expect(metrics.errors).toBe(0);

      const avgProcessingTime =
        metrics.processingTimes.reduce((a, b) => a + b, 0) / metrics.processingTimes.length;
      expect(avgProcessingTime).toBeGreaterThan(0);

      await adapter.cancel(consumerTag);
    });

    it('should emit monitoring events for dashboards', async () => {
      const monitoringEvents: any[] = [];

      adapter.on('message-published', (event) => {
        monitoringEvents.push({ type: 'published', ...event });
      });

      adapter.on('message-acked', (event) => {
        monitoringEvents.push({ type: 'acked', ...event });
      });

      await adapter.createQueue('monitor-test', { durable: true });

      const consumerTag = await adapter.consume(
        'monitor-test',
        async (message, ack) => {
          ack();
        }
      );

      await adapter.sendToQueue('monitor-test', { test: 'monitoring' });
      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(monitoringEvents.length).toBeGreaterThanOrEqual(2);
      expect(monitoringEvents.some(e => e.type === 'published')).toBe(true);
      expect(monitoringEvents.some(e => e.type === 'acked')).toBe(true);

      await adapter.cancel(consumerTag);
    });
  });
});
