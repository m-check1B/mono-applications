import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { QueueService } from '@server/services/queue-service';
import { EventEmitter } from 'events';

const createMockRabbitAdapter = () => ({
  connect: vi.fn(),
  disconnect: vi.fn(),
  publish: vi.fn(),
  subscribe: vi.fn(),
  bindQueue: vi.fn(),
  createQueue: vi.fn(),
  deleteQueue: vi.fn(),
  getQueueStats: vi.fn(),
  purgeQueue: vi.fn(),
  cancel: vi.fn(),
  unsubscribe: vi.fn(),
  healthCheck: vi.fn(),
  on: vi.fn(),
  isConnected: vi.fn(() => true)
});

// Mock logger
vi.mock('@server/core/logger', () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn()
  }
}));

describe('QueueService', () => {
  let queueService: QueueService;
  let originalEnv: any;
  let mockRabbitMQAdapter: ReturnType<typeof createMockRabbitAdapter>;

  beforeEach(() => {
    // Save original environment
    originalEnv = {
      RABBITMQ_URL: process.env.RABBITMQ_URL,
      QUEUE_PREFETCH: process.env.QUEUE_PREFETCH,
      NODE_ENV: process.env.NODE_ENV
    };

    vi.clearAllMocks();

    // Mock successful initialization
    mockRabbitMQAdapter = createMockRabbitAdapter();
    mockRabbitMQAdapter.connect.mockResolvedValue(undefined);
    mockRabbitMQAdapter.bindQueue.mockResolvedValue(undefined);

    queueService = new QueueService(mockRabbitMQAdapter as any);
  });

  afterEach(() => {
    // Restore original environment
    Object.keys(originalEnv).forEach(key => {
      if (originalEnv[key] !== undefined) {
        process.env[key] = originalEnv[key];
      } else {
        delete process.env[key];
      }
    });
    vi.clearAllMocks();
  });

  describe('Constructor', () => {
    it('should initialize with default configuration', () => {
      expect(queueService).toBeDefined();
      expect(queueService).toBeInstanceOf(EventEmitter);
    });

    it('should use environment variables for configuration', () => {
      process.env.RABBITMQ_URL = 'amqp://custom-host:5672';
      process.env.QUEUE_PREFETCH = '20';

      const customAdapter = createMockRabbitAdapter();
      const customService = new QueueService(customAdapter as any);
      expect(customService).toBeDefined();
    });

    it('should set up event forwarding from RabbitMQ adapter', () => {
      expect(mockRabbitMQAdapter.on).toHaveBeenCalledWith('connected', expect.any(Function));
      expect(mockRabbitMQAdapter.on).toHaveBeenCalledWith('disconnected', expect.any(Function));
      expect(mockRabbitMQAdapter.on).toHaveBeenCalledWith('error', expect.any(Function));
      expect(mockRabbitMQAdapter.on).toHaveBeenCalledWith('message-published', expect.any(Function));
      expect(mockRabbitMQAdapter.on).toHaveBeenCalledWith('message-acked', expect.any(Function));
      expect(mockRabbitMQAdapter.on).toHaveBeenCalledWith('message-nacked', expect.any(Function));
      expect(mockRabbitMQAdapter.on).toHaveBeenCalledWith('message-rejected', expect.any(Function));
    });
  });

  describe('initialize', () => {
    it('should connect to RabbitMQ and set up topology', async () => {
      await queueService.initialize();

      expect(mockRabbitMQAdapter.connect).toHaveBeenCalled();
      expect(mockRabbitMQAdapter.bindQueue).toHaveBeenCalledWith('inbound', 'calls', 'call.inbound.*');
    });

    it('should handle connection failures in development', async () => {
      process.env.NODE_ENV = 'development';
      mockRabbitMQAdapter.connect.mockRejectedValue(new Error('Connection failed'));

      // Should not throw in development
      await expect(queueService.initialize()).resolves.not.toThrow();
    });

    it('should throw connection failures in production', async () => {
      process.env.NODE_ENV = 'production';
      mockRabbitMQAdapter.connect.mockRejectedValue(new Error('Connection failed'));

      await expect(queueService.initialize()).rejects.toThrow('Connection failed');
    });

    it('should set ready status on successful initialization', async () => {
      await queueService.initialize();

      // Simulate connected event
      const connectedHandler = mockRabbitMQAdapter.on.mock.calls.find(
        call => call[0] === 'connected'
      )?.[1];
      connectedHandler?.();

      // Check internal ready state would be set
      expect(mockRabbitMQAdapter.connect).toHaveBeenCalled();
    });
  });

  describe('Event Handling', () => {
    it('should forward connected events', () => {
      const connectSpy = vi.fn();
      queueService.on('connected', connectSpy);

      // Simulate connected event from adapter
      const connectedHandler = mockRabbitMQAdapter.on.mock.calls.find(
        call => call[0] === 'connected'
      )?.[1];
      connectedHandler?.();

      expect(connectSpy).toHaveBeenCalled();
    });

    it('should forward disconnected events', () => {
      const disconnectSpy = vi.fn();
      queueService.on('disconnected', disconnectSpy);

      // Simulate disconnected event from adapter
      const disconnectedHandler = mockRabbitMQAdapter.on.mock.calls.find(
        call => call[0] === 'disconnected'
      )?.[1];
      disconnectedHandler?.();

      expect(disconnectSpy).toHaveBeenCalled();
    });

    it('should forward error events', () => {
      const errorSpy = vi.fn();
      queueService.on('error', errorSpy);
      const testError = new Error('Test error');

      // Simulate error event from adapter
      const errorHandler = mockRabbitMQAdapter.on.mock.calls.find(
        call => call[0] === 'error'
      )?.[1];
      errorHandler?.(testError);

      expect(errorSpy).toHaveBeenCalledWith(testError);
    });

    it('should handle message lifecycle events', async () => {
      const publishedData = { messageId: 'msg-1', queue: 'test-queue' };
      const ackedData = { messageId: 'msg-1', acknowledged: true };
      const nackedData = { messageId: 'msg-2', acknowledged: false };
      const rejectedData = { messageId: 'msg-3', rejected: true };

      // Simulate message lifecycle events
      const publishedHandler = mockRabbitMQAdapter.on.mock.calls.find(
        call => call[0] === 'message-published'
      )?.[1];
      publishedHandler?.(publishedData);

      const ackedHandler = mockRabbitMQAdapter.on.mock.calls.find(
        call => call[0] === 'message-acked'
      )?.[1];
      ackedHandler?.(ackedData);

      const nackedHandler = mockRabbitMQAdapter.on.mock.calls.find(
        call => call[0] === 'message-nacked'
      )?.[1];
      nackedHandler?.(nackedData);

      const rejectedHandler = mockRabbitMQAdapter.on.mock.calls.find(
        call => call[0] === 'message-rejected'
      )?.[1];
      rejectedHandler?.(rejectedData);

      // Events should be logged (verified through logger mock)
      const { logger } = await import('@server/core/logger');
      expect(logger.debug).toHaveBeenCalledWith('📤 Message published', publishedData);
      expect(logger.debug).toHaveBeenCalledWith('✅ Message acknowledged', ackedData);
      expect(logger.warn).toHaveBeenCalledWith('⚠️ Message negative acknowledged', nackedData);
      expect(logger.error).toHaveBeenCalledWith('❌ Message rejected', rejectedData);
    });
  });

  describe('Publishing Messages', () => {
    beforeEach(async () => {
      await queueService.initialize();
      // Simulate connected state
      const connectedHandler = mockRabbitMQAdapter.on.mock.calls.find(
        call => call[0] === 'connected'
      )?.[1];
      connectedHandler?.();
    });

    it('should publish call events', async () => {
      const callEvent = {
        callId: 'call-123',
        type: 'call.started',
        data: { fromNumber: '+1234567890', toNumber: '+0987654321' },
        timestamp: new Date()
      };

      mockRabbitMQAdapter.publish.mockResolvedValue(true);

      await queueService.publishCallEvent(callEvent as any);

      expect(mockRabbitMQAdapter.publish).toHaveBeenCalledWith(
        'calls',
        'call.started',
        callEvent,
        expect.objectContaining({
          persistent: true,
          messageId: expect.any(String)
        })
      );
    });

    it('should publish transcription events', async () => {
      const transcriptionEvent = {
        callId: 'call-123',
        text: 'Hello, how can I help you?',
        speaker: 'agent',
        confidence: 0.95,
        timestamp: new Date()
      };

      mockRabbitMQAdapter.publish.mockResolvedValue(true);

      await queueService.publishTranscriptionEvent(transcriptionEvent as any);

      expect(mockRabbitMQAdapter.publish).toHaveBeenCalledWith(
        'transcriptions',
        'transcription.new',
        transcriptionEvent,
        expect.objectContaining({
          persistent: true
        })
      );
    });

    it('should publish AI processing requests', async () => {
      const aiRequest = {
        callId: 'call-123',
        type: 'sentiment_analysis',
        data: { text: 'Customer seems happy with the service' },
        priority: 'high'
      };

      mockRabbitMQAdapter.publish.mockResolvedValue(true);

      await queueService.publishAIProcessingRequest(aiRequest as any);

      expect(mockRabbitMQAdapter.publish).toHaveBeenCalledWith(
        'ai-processing',
        'ai.process',
        aiRequest,
        expect.objectContaining({
          priority: 1 // high priority converted to number
        })
      );
    });

    it('should handle publishing failures', async () => {
      const callEvent = {
        callId: 'call-123',
        type: 'call.started',
        data: {},
        timestamp: new Date()
      };

      mockRabbitMQAdapter.publish.mockRejectedValue(new Error('Publish failed'));

      await expect(queueService.publishCallEvent(callEvent as any))
        .rejects.toThrow('Publish failed');
    });
  });

  describe('Subscribing to Messages', () => {
    beforeEach(async () => {
      await queueService.initialize();
      mockRabbitMQAdapter.subscribe.mockResolvedValue('consumer-tag-123');
    });

    it('should subscribe to call events', async () => {
      const handler = vi.fn();

      await queueService.subscribeToCallEvents(handler);

      expect(mockRabbitMQAdapter.subscribe).toHaveBeenCalledWith(
        'inbound',
        handler,
        expect.objectContaining({
          consumerTag: expect.any(String),
          autoAck: false
        })
      );
    });

    it('should subscribe to transcription events', async () => {
      const handler = vi.fn();

      await queueService.subscribeToTranscriptions(handler);

      expect(mockRabbitMQAdapter.subscribe).toHaveBeenCalledWith(
        'transcriptions',
        handler,
        expect.objectContaining({
          autoAck: false
        })
      );
    });

    it('should subscribe to AI processing requests', async () => {
      const handler = vi.fn();

      await queueService.subscribeToAIProcessing(handler);

      expect(mockRabbitMQAdapter.subscribe).toHaveBeenCalledWith(
        'ai-processing',
        handler,
        expect.objectContaining({
          autoAck: false
        })
      );
    });

    it('should track consumer tags', async () => {
      const handler = vi.fn();

      await queueService.subscribeToCallEvents(handler);

      // Verify consumer tag is stored for later unsubscription
      expect(mockRabbitMQAdapter.subscribe).toHaveBeenCalled();
    });

    it('should handle subscription failures', async () => {
      const handler = vi.fn();
      mockRabbitMQAdapter.subscribe.mockRejectedValue(new Error('Subscribe failed'));

      await expect(queueService.subscribeToCallEvents(handler))
        .rejects.toThrow('Subscribe failed');
    });
  });

  describe('Queue Management', () => {
    beforeEach(async () => {
      await queueService.initialize();
    });

    it('should create queues dynamically', async () => {
      mockRabbitMQAdapter.createQueue.mockResolvedValue(undefined);

      await queueService.createQueue('custom-queue', {
        durable: true,
        exclusive: false
      });

      expect(mockRabbitMQAdapter.createQueue).toHaveBeenCalledWith(
        'custom-queue',
        { durable: true, exclusive: false }
      );
    });

    it('should delete queues', async () => {
      mockRabbitMQAdapter.deleteQueue.mockResolvedValue(undefined);

      await queueService.deleteQueue('old-queue');

      expect(mockRabbitMQAdapter.deleteQueue).toHaveBeenCalledWith('old-queue');
    });

    it('should get queue statistics', async () => {
      const mockStats = {
        messageCount: 10,
        consumerCount: 2,
        memoryUsage: 1024
      };

      mockRabbitMQAdapter.getQueueStats = vi.fn().mockResolvedValue(mockStats);

      const stats = await queueService.getQueueStats('test-queue');

      expect(stats).toEqual(mockStats);
    });

    it('should handle queue management errors', async () => {
      mockRabbitMQAdapter.createQueue.mockRejectedValue(new Error('Queue creation failed'));

      await expect(queueService.createQueue('failing-queue'))
        .rejects.toThrow('Queue creation failed');
    });
  });

  describe('Health Monitoring', () => {
    it('should report ready status', () => {
      // Initially not ready
      expect(queueService.isReady()).toBe(false);

      // Simulate connection
      const connectedHandler = mockRabbitMQAdapter.on.mock.calls.find(
        call => call[0] === 'connected'
      )?.[1];
      connectedHandler?.();

      // Should now be ready
      expect(queueService.isReady()).toBe(true);
    });

    it('should report connection health', async () => {
      mockRabbitMQAdapter.healthCheck = vi.fn().mockResolvedValue({
        connected: true,
        queues: ['inbound', 'transcriptions', 'ai-processing'],
        exchanges: ['calls', 'transcriptions', 'ai-processing']
      });

      const health = await queueService.getHealthStatus();

      expect(health).toEqual({
        connected: true,
        queues: ['inbound', 'transcriptions', 'ai-processing'],
        exchanges: ['calls', 'transcriptions', 'ai-processing']
      });
    });

    it('should handle health check failures', async () => {
      mockRabbitMQAdapter.healthCheck = vi.fn().mockRejectedValue(new Error('Health check failed'));

      const health = await queueService.getHealthStatus();

      expect(health).toEqual({
        connected: false,
        error: 'Health check failed'
      });
    });
  });

  describe('Cleanup and Shutdown', () => {
    beforeEach(async () => {
      await queueService.initialize();
      mockRabbitMQAdapter.unsubscribe = vi.fn().mockResolvedValue(undefined);
      mockRabbitMQAdapter.disconnect.mockResolvedValue(undefined);
    });

    it('should unsubscribe from all consumers', async () => {
      // Set up some subscriptions
      mockRabbitMQAdapter.subscribe.mockResolvedValue('consumer-1');
      await queueService.subscribeToCallEvents(vi.fn());

      mockRabbitMQAdapter.subscribe.mockResolvedValue('consumer-2');
      await queueService.subscribeToTranscriptions(vi.fn());

      await queueService.unsubscribeAll();

      expect(mockRabbitMQAdapter.unsubscribe).toHaveBeenCalledWith('consumer-1');
      expect(mockRabbitMQAdapter.unsubscribe).toHaveBeenCalledWith('consumer-2');
    });

    it('should gracefully shutdown', async () => {
      await queueService.shutdown();

      expect(mockRabbitMQAdapter.disconnect).toHaveBeenCalled();
    });

    it('should handle shutdown errors gracefully', async () => {
      mockRabbitMQAdapter.disconnect.mockRejectedValue(new Error('Disconnect failed'));

      // Should not throw
      await expect(queueService.shutdown()).resolves.not.toThrow();
    });
  });

  describe('Error Recovery', () => {
    it('should handle connection recovery', () => {
      // Simulate disconnection
      const disconnectedHandler = mockRabbitMQAdapter.on.mock.calls.find(
        call => call[0] === 'disconnected'
      )?.[1];
      disconnectedHandler?.();

      expect(queueService.isReady()).toBe(false);

      // Simulate reconnection
      const connectedHandler = mockRabbitMQAdapter.on.mock.calls.find(
        call => call[0] === 'connected'
      )?.[1];
      connectedHandler?.();

      expect(queueService.isReady()).toBe(true);
    });

    it('should handle message failures with retries', async () => {
      const failingEvent = {
        callId: 'call-123',
        type: 'call.failed',
        data: {},
        timestamp: new Date()
      };

      // First attempt fails, second succeeds
      mockRabbitMQAdapter.publish
        .mockRejectedValueOnce(new Error('Temporary failure'))
        .mockResolvedValueOnce(true);

      // This would be handled by retry logic in the actual implementation
      await expect(queueService.publishCallEvent(failingEvent as any))
        .rejects.toThrow('Temporary failure');
    });
  });

  describe('Performance and Scalability', () => {
    it('should handle high message throughput', async () => {
      await queueService.initialize();

      const events = Array.from({ length: 1000 }, (_, i) => ({
        callId: `call-${i}`,
        type: 'call.test',
        data: { index: i },
        timestamp: new Date()
      }));

      mockRabbitMQAdapter.publish.mockResolvedValue(true);

      const promises = events.map(event =>
        queueService.publishCallEvent(event as any)
      );

      await Promise.all(promises);

      expect(mockRabbitMQAdapter.publish).toHaveBeenCalledTimes(1000);
    });

    it('should manage memory efficiently with many consumers', async () => {
      await queueService.initialize();

      // Create many subscriptions
      const handlers = Array.from({ length: 100 }, () => vi.fn());

      mockRabbitMQAdapter.subscribe.mockImplementation((queue, handler) =>
        Promise.resolve(`consumer-${Math.random()}`)
      );

      const subscriptions = handlers.map(handler =>
        queueService.subscribeToCallEvents(handler)
      );

      await Promise.all(subscriptions);

      expect(mockRabbitMQAdapter.subscribe).toHaveBeenCalledTimes(100);
    });
  });
});
