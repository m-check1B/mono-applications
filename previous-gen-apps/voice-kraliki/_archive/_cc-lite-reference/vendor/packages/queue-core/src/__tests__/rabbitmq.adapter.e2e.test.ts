/**
 * RabbitMQ Adapter End-to-End Tests
 *
 * Tests full integration flows including:
 * - Auth-core integration
 * - Events-core integration
 * - Error handling and retries
 * - Dead letter queue scenarios
 * - Multi-step workflows
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import { RabbitMQAdapter } from '../adapters/rabbitmq.adapter';
import type { QueueMessage, CallEvent, TranscriptionEvent, AIProcessingRequest } from '../types/queue.types';

// Test configuration
const TEST_RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://localhost:5672';
const TEST_TIMEOUT = 30000;

describe('RabbitMQ Adapter E2E Tests', () => {
  let adapter: RabbitMQAdapter;

  beforeAll(async () => {
    adapter = new RabbitMQAdapter({
      url: TEST_RABBITMQ_URL,
      prefetch: 5,
      heartbeat: 30,
      connectionName: 'e2e-test-adapter',
      retryAttempts: 3,
      retryDelay: 1000,
    });

    await adapter.connect();
  }, TEST_TIMEOUT);

  afterAll(async () => {
    await adapter.close();
  });

  beforeEach(async () => {
    // Clean up test queues before each test
    try {
      await adapter.purgeQueue('inbound');
      await adapter.purgeQueue('outbound');
      await adapter.purgeQueue('priority');
      await adapter.purgeQueue('ai-processing');
      await adapter.purgeQueue('deadLetter');
    } catch (error) {
      // Ignore errors if queues don't exist yet
    }
  });

  describe('Basic Connectivity and Setup', () => {
    it('should establish connection to RabbitMQ', () => {
      expect(adapter.isConnected()).toBe(true);
    });

    it('should create default exchanges and queues', async () => {
      const stats = await adapter.getQueueStats('inbound');
      expect(stats.name).toBe('inbound');
      expect(stats.messageCount).toBeGreaterThanOrEqual(0);
    });

    it('should support multiple connections', async () => {
      const adapter2 = new RabbitMQAdapter({
        url: TEST_RABBITMQ_URL,
        connectionName: 'e2e-test-adapter-2',
      });

      await adapter2.connect();
      expect(adapter2.isConnected()).toBe(true);
      await adapter2.close();
    });
  });

  describe('Message Publishing and Consumption', () => {
    it('should publish and consume messages via exchange', async () => {
      const testPayload = {
        type: 'test',
        data: 'Hello World',
        timestamp: new Date().toISOString(),
      };

      let receivedMessage: QueueMessage | null = null;

      // Start consumer
      const consumerTag = await adapter.consume(
        'inbound',
        async (message, ack) => {
          receivedMessage = message;
          ack();
        }
      );

      // Publish message
      await adapter.publish('calls', 'call.inbound.test', testPayload);

      // Wait for message processing
      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(receivedMessage).not.toBeNull();
      expect(receivedMessage?.payload).toEqual(testPayload);
      expect(receivedMessage?.metadata.source).toBe('e2e-test-adapter');

      await adapter.cancel(consumerTag);
    }, TEST_TIMEOUT);

    it('should send and receive messages directly to queue', async () => {
      const testPayload = { message: 'Direct queue message' };
      let receivedMessage: QueueMessage | null = null;

      const consumerTag = await adapter.consume(
        'inbound',
        async (message, ack) => {
          receivedMessage = message;
          ack();
        }
      );

      await adapter.sendToQueue('inbound', testPayload);
      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(receivedMessage?.payload).toEqual(testPayload);

      await adapter.cancel(consumerTag);
    });

    it('should handle message priorities', async () => {
      const messages: QueueMessage[] = [];

      const consumerTag = await adapter.consume(
        'priority',
        async (message, ack) => {
          messages.push(message);
          ack();
        }
      );

      // Send messages with different priorities
      await adapter.sendToQueue('priority', { order: 1 }, { priority: 1 });
      await adapter.sendToQueue('priority', { order: 2 }, { priority: 10 });
      await adapter.sendToQueue('priority', { order: 3 }, { priority: 5 });

      await new Promise(resolve => setTimeout(resolve, 1500));

      // Higher priority messages should be processed first
      expect(messages.length).toBe(3);
      expect(messages[0].payload.order).toBe(2); // Priority 10
      expect(messages[1].payload.order).toBe(3); // Priority 5
      expect(messages[2].payload.order).toBe(1); // Priority 1

      await adapter.cancel(consumerTag);
    }, TEST_TIMEOUT);
  });

  describe('Call Center Workflow Integration', () => {
    it('should process inbound call workflow', async () => {
      const callEvent: CallEvent = {
        type: 'call.started',
        callId: 'call-123',
        customerId: 'customer-456',
        timestamp: new Date(),
        data: {
          fromNumber: '+1234567890',
          toNumber: '+0987654321',
        },
      };

      let processedCall: CallEvent | null = null;

      const consumerTag = await adapter.consume(
        'inbound',
        async (message, ack) => {
          processedCall = message.payload as CallEvent;
          ack();
        }
      );

      await adapter.publish('calls', 'call.inbound.started', callEvent);
      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(processedCall).not.toBeNull();
      expect(processedCall?.callId).toBe('call-123');
      expect(processedCall?.type).toBe('call.started');

      await adapter.cancel(consumerTag);
    });

    it('should process transcription events', async () => {
      const transcription: TranscriptionEvent = {
        type: 'transcription.partial',
        callId: 'call-123',
        sessionId: 'session-456',
        speaker: 'customer',
        text: 'I need help with my account',
        confidence: 0.95,
        timestamp: new Date(),
        language: 'en-US',
      };

      let processedTranscription: TranscriptionEvent | null = null;

      await adapter.createQueue('transcriptions', { durable: true });
      await adapter.bindQueue('transcriptions', 'ai', 'transcription.#');

      const consumerTag = await adapter.consume(
        'transcriptions',
        async (message, ack) => {
          processedTranscription = message.payload as TranscriptionEvent;
          ack();
        }
      );

      await adapter.publish('ai', 'transcription.partial', transcription);
      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(processedTranscription).not.toBeNull();
      expect(processedTranscription?.text).toBe('I need help with my account');
      expect(processedTranscription?.confidence).toBe(0.95);

      await adapter.cancel(consumerTag);
    });

    it('should process AI processing requests', async () => {
      const aiRequest: AIProcessingRequest = {
        type: 'sentiment',
        callId: 'call-123',
        input: 'Customer seems frustrated',
        priority: 'high',
        context: {
          agentId: 'agent-789',
          duration: 120,
        },
      };

      let processedRequest: AIProcessingRequest | null = null;

      const consumerTag = await adapter.consume(
        'ai-processing',
        async (message, ack) => {
          processedRequest = message.payload as AIProcessingRequest;
          ack();
        }
      );

      await adapter.publish('ai', 'ai.sentiment.request', aiRequest);
      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(processedRequest).not.toBeNull();
      expect(processedRequest?.type).toBe('sentiment');
      expect(processedRequest?.priority).toBe('high');

      await adapter.cancel(consumerTag);
    });
  });

  describe('Error Handling and Retries', () => {
    it('should handle consumer errors and reject messages', async () => {
      const testPayload = { shouldFail: true };
      let errorHandled = false;

      adapter.on('handler-error', () => {
        errorHandled = true;
      });

      const consumerTag = await adapter.consume(
        'inbound',
        async (message, ack, nack, reject) => {
          if (message.payload.shouldFail) {
            throw new Error('Simulated processing error');
          }
          ack();
        }
      );

      await adapter.sendToQueue('inbound', testPayload);
      await new Promise(resolve => setTimeout(resolve, 1500));

      expect(errorHandled).toBe(true);

      await adapter.cancel(consumerTag);
    });

    it('should nack and requeue messages on failure', async () => {
      let processCount = 0;
      const testPayload = { attempt: 0 };

      const consumerTag = await adapter.consume(
        'inbound',
        async (message, ack, nack) => {
          processCount++;

          if (processCount === 1) {
            // First attempt fails
            nack(true); // Requeue
          } else {
            // Second attempt succeeds
            ack();
          }
        }
      );

      await adapter.sendToQueue('inbound', testPayload);
      await new Promise(resolve => setTimeout(resolve, 2000));

      expect(processCount).toBe(2);

      await adapter.cancel(consumerTag);
    }, TEST_TIMEOUT);

    it('should send failed messages to dead letter queue', async () => {
      // Create a test queue with DLX
      await adapter.createQueue('test-dlx-queue', {
        durable: true,
        deadLetterExchange: 'dlx',
        deadLetterRoutingKey: 'test.failed',
        messageTtl: 5000,
      });

      await adapter.bindQueue('deadLetter', 'dlx', 'test.failed');

      let dlqMessage: QueueMessage | null = null;

      const dlqConsumer = await adapter.consume(
        'deadLetter',
        async (message, ack) => {
          dlqMessage = message;
          ack();
        }
      );

      // Send message that will fail
      const testConsumer = await adapter.consume(
        'test-dlx-queue',
        async (message, ack, nack, reject) => {
          reject(false); // Reject without requeue -> goes to DLX
        }
      );

      await adapter.sendToQueue('test-dlx-queue', { test: 'dlx' });
      await new Promise(resolve => setTimeout(resolve, 2000));

      expect(dlqMessage).not.toBeNull();
      expect(dlqMessage?.payload.test).toBe('dlx');

      await adapter.cancel(testConsumer);
      await adapter.cancel(dlqConsumer);
    }, TEST_TIMEOUT);
  });

  describe('Multi-Step Workflows', () => {
    it('should execute multi-step call processing workflow', async () => {
      const workflow = {
        callId: 'workflow-call-123',
        steps: [] as string[],
      };

      // Step 1: Call received
      await adapter.createQueue('step1-receive', { durable: true });
      await adapter.bindQueue('step1-receive', 'calls', 'workflow.step1');

      const step1Consumer = await adapter.consume(
        'step1-receive',
        async (message, ack) => {
          workflow.steps.push('received');
          // Forward to next step
          await adapter.publish('calls', 'workflow.step2', {
            ...message.payload,
            step1Complete: true,
          });
          ack();
        }
      );

      // Step 2: Call routed
      await adapter.createQueue('step2-route', { durable: true });
      await adapter.bindQueue('step2-route', 'calls', 'workflow.step2');

      const step2Consumer = await adapter.consume(
        'step2-route',
        async (message, ack) => {
          workflow.steps.push('routed');
          // Forward to next step
          await adapter.publish('calls', 'workflow.step3', {
            ...message.payload,
            step2Complete: true,
          });
          ack();
        }
      );

      // Step 3: Call connected
      await adapter.createQueue('step3-connect', { durable: true });
      await adapter.bindQueue('step3-connect', 'calls', 'workflow.step3');

      const step3Consumer = await adapter.consume(
        'step3-connect',
        async (message, ack) => {
          workflow.steps.push('connected');
          ack();
        }
      );

      // Initiate workflow
      await adapter.publish('calls', 'workflow.step1', {
        callId: workflow.callId,
        timestamp: new Date(),
      });

      // Wait for all steps to complete
      await new Promise(resolve => setTimeout(resolve, 3000));

      expect(workflow.steps).toEqual(['received', 'routed', 'connected']);

      await adapter.cancel(step1Consumer);
      await adapter.cancel(step2Consumer);
      await adapter.cancel(step3Consumer);
    }, TEST_TIMEOUT);

    it('should handle parallel processing with fanout exchange', async () => {
      const results: string[] = [];

      // Create fanout exchange for broadcasting
      await adapter.createExchange('broadcast', { type: 'fanout', durable: true });

      // Create multiple queues bound to fanout
      await adapter.createQueue('listener1', { durable: false, autoDelete: true });
      await adapter.createQueue('listener2', { durable: false, autoDelete: true });
      await adapter.createQueue('listener3', { durable: false, autoDelete: true });

      await adapter.bindQueue('listener1', 'broadcast', '');
      await adapter.bindQueue('listener2', 'broadcast', '');
      await adapter.bindQueue('listener3', 'broadcast', '');

      // Setup consumers
      const consumer1 = await adapter.consume('listener1', async (msg, ack) => {
        results.push('listener1');
        ack();
      });

      const consumer2 = await adapter.consume('listener2', async (msg, ack) => {
        results.push('listener2');
        ack();
      });

      const consumer3 = await adapter.consume('listener3', async (msg, ack) => {
        results.push('listener3');
        ack();
      });

      // Publish to fanout - should reach all listeners
      await adapter.publish('broadcast', '', { event: 'broadcast-test' });

      await new Promise(resolve => setTimeout(resolve, 2000));

      expect(results).toContain('listener1');
      expect(results).toContain('listener2');
      expect(results).toContain('listener3');
      expect(results.length).toBe(3);

      await adapter.cancel(consumer1);
      await adapter.cancel(consumer2);
      await adapter.cancel(consumer3);
    }, TEST_TIMEOUT);
  });

  describe('Performance and Reliability', () => {
    it('should handle high message throughput', async () => {
      const messageCount = 100;
      let receivedCount = 0;

      const consumerTag = await adapter.consume(
        'inbound',
        async (message, ack) => {
          receivedCount++;
          ack();
        },
        { prefetchCount: 20 }
      );

      // Send many messages quickly
      const promises = [];
      for (let i = 0; i < messageCount; i++) {
        promises.push(
          adapter.sendToQueue('inbound', { index: i, timestamp: Date.now() })
        );
      }

      await Promise.all(promises);
      await new Promise(resolve => setTimeout(resolve, 5000));

      expect(receivedCount).toBe(messageCount);

      await adapter.cancel(consumerTag);
    }, TEST_TIMEOUT);

    it('should maintain message order in sequential processing', async () => {
      const receivedOrder: number[] = [];

      const consumerTag = await adapter.consume(
        'inbound',
        async (message, ack) => {
          receivedOrder.push(message.payload.order);
          ack();
        },
        { prefetchCount: 1 } // Process one at a time
      );

      // Send messages in order
      for (let i = 0; i < 10; i++) {
        await adapter.sendToQueue('inbound', { order: i });
      }

      await new Promise(resolve => setTimeout(resolve, 3000));

      expect(receivedOrder).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]);

      await adapter.cancel(consumerTag);
    }, TEST_TIMEOUT);

    it('should get accurate queue statistics', async () => {
      // Add some messages
      for (let i = 0; i < 5; i++) {
        await adapter.sendToQueue('inbound', { test: i });
      }

      const stats = await adapter.getQueueStats('inbound');

      expect(stats.name).toBe('inbound');
      expect(stats.messageCount).toBe(5);
      expect(stats.consumerCount).toBe(0);
    });
  });

  describe('Correlation and Tracking', () => {
    it('should preserve correlation IDs across workflow steps', async () => {
      const correlationId = 'workflow-correlation-123';
      let receivedCorrelationId: string | undefined;

      const consumerTag = await adapter.consume(
        'inbound',
        async (message, ack) => {
          receivedCorrelationId = message.correlationId;
          ack();
        }
      );

      await adapter.sendToQueue('inbound', { test: 'correlation' }, {
        correlationId,
      });

      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(receivedCorrelationId).toBe(correlationId);

      await adapter.cancel(consumerTag);
    });

    it('should track message metadata through processing', async () => {
      let receivedMetadata: any;

      const consumerTag = await adapter.consume(
        'inbound',
        async (message, ack) => {
          receivedMetadata = message.metadata;
          ack();
        }
      );

      await adapter.sendToQueue('inbound', { test: 'metadata' }, {
        priority: 5,
        headers: { 'x-custom-header': 'test-value' },
      });

      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(receivedMetadata.source).toBe('e2e-test-adapter');
      expect(receivedMetadata.priority).toBe(5);
      expect(receivedMetadata.timestamp).toBeDefined();

      await adapter.cancel(consumerTag);
    });
  });

  describe('Event Integration', () => {
    it('should emit events for message lifecycle', async () => {
      const events: string[] = [];

      adapter.on('message-sent', () => events.push('sent'));
      adapter.on('message-acked', () => events.push('acked'));

      const consumerTag = await adapter.consume(
        'inbound',
        async (message, ack) => {
          ack();
        }
      );

      await adapter.sendToQueue('inbound', { test: 'events' });
      await new Promise(resolve => setTimeout(resolve, 1000));

      expect(events).toContain('sent');
      expect(events).toContain('acked');

      await adapter.cancel(consumerTag);
    });

    it('should emit consumer lifecycle events', async () => {
      const events: string[] = [];

      adapter.on('consumer-started', () => events.push('started'));
      adapter.on('consumer-cancelled', () => events.push('cancelled'));

      const consumerTag = await adapter.consume(
        'inbound',
        async (message, ack) => {
          ack();
        }
      );

      await adapter.cancel(consumerTag);

      expect(events).toContain('started');
      expect(events).toContain('cancelled');
    });
  });
});
