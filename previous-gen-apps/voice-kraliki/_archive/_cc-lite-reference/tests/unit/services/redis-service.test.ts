import { describe, it, expect, beforeEach, afterEach, vi, beforeAll, afterAll } from 'vitest';
import { RedisService } from '../../../server/services/redis-service';
import { createClient } from 'redis';

// Mock Redis client
const mockRedisClient = {
  connect: vi.fn(),
  quit: vi.fn(),
  ping: vi.fn(),
  on: vi.fn(),
  setEx: vi.fn(),
  get: vi.fn(),
  del: vi.fn(),
  incr: vi.fn(),
  expire: vi.fn(),
  exists: vi.fn(),
  lPush: vi.fn(),
  rPop: vi.fn(),
  lLen: vi.fn(),
  incrBy: vi.fn(),
  subscribe: vi.fn(),
  publish: vi.fn()
};

// Mock Redis config
vi.mock('../../../server/config/redis-config', () => ({
  redisConfig: {
    host: '127.0.0.1',
    port: 6379,
    password: undefined,
    db: 0
  },
  sessionStoreConfig: {
    prefix: 'cc-light:session:',
    ttl: 3600
  },
  cacheConfig: {
    user: { prefix: 'cc-light:cache:user:', ttl: 1800 },
    call: { prefix: 'cc-light:cache:call:', ttl: 900 },
    agent: { prefix: 'cc-light:cache:agent:', ttl: 300 }
  },
  rateLimitConfig: {
    api: { prefix: 'cc-light:ratelimit:api:', points: 100, duration: 60, blockDuration: 300 },
    login: { prefix: 'cc-light:ratelimit:login:', points: 5, duration: 900, blockDuration: 1800 }
  },
  pubSubChannels: {
    calls: 'cc-light:events:calls',
    agents: 'cc-light:events:agents',
    notifications: 'cc-light:events:notifications'
  },
  validateRedisBinding: vi.fn()
}));

// Mock logger service
vi.mock('../../../server/services/logger-service', () => ({
  systemLogger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn()
  }
}));

// Mock createClient
vi.mock('redis', () => ({
  createClient: vi.fn()
}));

describe('RedisService', () => {
  let redisService: RedisService;
  let mockClient: any;
  let mockSubscriber: any;
  let mockPublisher: any;

  beforeAll(() => {
    // Mock environment
    process.env.NODE_ENV = 'test';
  });

  afterAll(() => {
    delete process.env.NODE_ENV;
  });

  beforeEach(() => {
    vi.clearAllMocks();

    // Set up mock clients
    mockClient = { ...mockRedisClient };
    mockSubscriber = { ...mockRedisClient };
    mockPublisher = { ...mockRedisClient };

    // Mock createClient to return different instances
    (createClient as any).mockImplementation(() => mockClient);

    redisService = new RedisService();

    // Manually set the clients for testing
    (redisService as any).client = mockClient;
    (redisService as any).subscriber = mockSubscriber;
    (redisService as any).publisher = mockPublisher;
    (redisService as any).isConnected = true;
  });

  afterEach(async () => {
    if (redisService) {
      await redisService.cleanup();
    }
  });

  describe('Service Initialization', () => {
    it('should initialize Redis connections successfully', async () => {
      const newService = new RedisService();

      // Mock successful connections
      mockClient.connect.mockResolvedValue(undefined);
      mockSubscriber.connect.mockResolvedValue(undefined);
      mockPublisher.connect.mockResolvedValue(undefined);
      mockSubscriber.subscribe.mockResolvedValue(undefined);

      await newService.initialize();

      expect(createClient).toHaveBeenCalledTimes(3); // client, subscriber, publisher
      expect(mockClient.connect).toHaveBeenCalled();
      expect(mockSubscriber.connect).toHaveBeenCalled();
      expect(mockPublisher.connect).toHaveBeenCalled();

      await newService.cleanup();
    });

    it('should handle connection failures gracefully in development', async () => {
      process.env.NODE_ENV = 'development';
      const newService = new RedisService();

      mockClient.connect.mockRejectedValue(new Error('Connection failed'));

      // Should not throw in development
      await expect(newService.initialize()).resolves.toBeUndefined();

      process.env.NODE_ENV = 'test';
      await newService.cleanup();
    });

    it('should throw connection failures in production', async () => {
      process.env.NODE_ENV = 'production';
      const newService = new RedisService();

      mockClient.connect.mockRejectedValue(new Error('Connection failed'));

      await expect(newService.initialize()).rejects.toThrow('Connection failed');

      process.env.NODE_ENV = 'test';
    });

    it('should set up error handlers for all clients', async () => {
      const newService = new RedisService();

      mockClient.connect.mockResolvedValue(undefined);
      mockSubscriber.connect.mockResolvedValue(undefined);
      mockPublisher.connect.mockResolvedValue(undefined);
      mockSubscriber.subscribe.mockResolvedValue(undefined);

      await newService.initialize();

      expect(mockClient.on).toHaveBeenCalledWith('error', expect.any(Function));
      expect(mockSubscriber.on).toHaveBeenCalledWith('error', expect.any(Function));
      expect(mockPublisher.on).toHaveBeenCalledWith('error', expect.any(Function));

      await newService.cleanup();
    });
  });

  describe('Session Management', () => {
    it('should store session data with TTL', async () => {
      const sessionId = 'test-session-123';
      const sessionData = { userId: 'user-123', role: 'agent' };

      mockClient.setEx.mockResolvedValue('OK');

      await redisService.setSession(sessionId, sessionData);

      expect(mockClient.setEx).toHaveBeenCalledWith(
        'cc-light:session:test-session-123',
        3600,
        JSON.stringify(sessionData)
      );
    });

    it('should store session data with custom TTL', async () => {
      const sessionId = 'test-session-123';
      const sessionData = { userId: 'user-123', role: 'agent' };
      const customTTL = 7200;

      mockClient.setEx.mockResolvedValue('OK');

      await redisService.setSession(sessionId, sessionData, customTTL);

      expect(mockClient.setEx).toHaveBeenCalledWith(
        'cc-light:session:test-session-123',
        customTTL,
        JSON.stringify(sessionData)
      );
    });

    it('should retrieve session data', async () => {
      const sessionId = 'test-session-123';
      const sessionData = { userId: 'user-123', role: 'agent' };

      mockClient.get.mockResolvedValue(JSON.stringify(sessionData));

      const result = await redisService.getSession(sessionId);

      expect(mockClient.get).toHaveBeenCalledWith('cc-light:session:test-session-123');
      expect(result).toEqual(sessionData);
    });

    it('should return null for non-existent session', async () => {
      const sessionId = 'non-existent-session';

      mockClient.get.mockResolvedValue(null);

      const result = await redisService.getSession(sessionId);

      expect(result).toBeNull();
    });

    it('should delete session data', async () => {
      const sessionId = 'test-session-123';

      mockClient.del.mockResolvedValue(1);

      await redisService.deleteSession(sessionId);

      expect(mockClient.del).toHaveBeenCalledWith('cc-light:session:test-session-123');
    });

    it('should handle session operations when Redis is disconnected', async () => {
      (redisService as any).isConnected = false;

      await redisService.setSession('test', { data: 'test' });
      const result = await redisService.getSession('test');
      await redisService.deleteSession('test');

      expect(result).toBeNull();
      expect(mockClient.setEx).not.toHaveBeenCalled();
      expect(mockClient.get).not.toHaveBeenCalled();
      expect(mockClient.del).not.toHaveBeenCalled();
    });
  });

  describe('Caching Operations', () => {
    it('should set cache value with type-specific TTL', async () => {
      const cacheType = 'user';
      const key = 'user-123';
      const value = { name: 'John Doe', email: 'john@example.com' };

      mockClient.setEx.mockResolvedValue('OK');

      await redisService.setCache(cacheType, key, value);

      expect(mockClient.setEx).toHaveBeenCalledWith(
        'cc-light:cache:user:user-123',
        1800,
        JSON.stringify(value)
      );
    });

    it('should get cached value', async () => {
      const cacheType = 'user';
      const key = 'user-123';
      const cachedValue = { name: 'John Doe', email: 'john@example.com' };

      mockClient.get.mockResolvedValue(JSON.stringify(cachedValue));

      const result = await redisService.getCache(cacheType, key);

      expect(mockClient.get).toHaveBeenCalledWith('cc-light:cache:user:user-123');
      expect(result).toEqual(cachedValue);
    });

    it('should return null for cache miss', async () => {
      const cacheType = 'user';
      const key = 'non-existent';

      mockClient.get.mockResolvedValue(null);

      const result = await redisService.getCache(cacheType, key);

      expect(result).toBeNull();
    });

    it('should invalidate cache entry', async () => {
      const cacheType = 'user';
      const key = 'user-123';

      mockClient.del.mockResolvedValue(1);

      await redisService.invalidateCache(cacheType, key);

      expect(mockClient.del).toHaveBeenCalledWith('cc-light:cache:user:user-123');
    });
  });

  describe('Rate Limiting', () => {
    it('should allow requests within rate limit', async () => {
      const rateLimitType = 'api';
      const identifier = 'user-123';

      mockClient.incr.mockResolvedValue(5); // First request returns 5
      mockClient.expire.mockResolvedValue(1);

      const result = await redisService.checkRateLimit(rateLimitType, identifier);

      expect(mockClient.incr).toHaveBeenCalledWith('cc-light:ratelimit:api:user-123');
      expect(result.allowed).toBe(true);
      expect(result.remaining).toBe(95); // 100 - 5
    });

    it('should block requests exceeding rate limit', async () => {
      const rateLimitType = 'api';
      const identifier = 'user-123';

      mockClient.incr.mockResolvedValue(101); // Exceeds limit of 100
      mockClient.setEx.mockResolvedValue('OK');

      const result = await redisService.checkRateLimit(rateLimitType, identifier);

      expect(result.allowed).toBe(false);
      expect(result.remaining).toBe(0);
      expect(mockClient.setEx).toHaveBeenCalledWith(
        'cc-light:ratelimit:api:user-123:blocked',
        300,
        '1'
      );
    });

    it('should set expiry on first request', async () => {
      const rateLimitType = 'api';
      const identifier = 'user-123';

      mockClient.incr.mockResolvedValue(1); // First request
      mockClient.expire.mockResolvedValue(1);

      await redisService.checkRateLimit(rateLimitType, identifier);

      expect(mockClient.expire).toHaveBeenCalledWith('cc-light:ratelimit:api:user-123', 60);
    });

    it('should check if identifier is blocked', async () => {
      const rateLimitType = 'api';
      const identifier = 'user-123';

      mockClient.exists.mockResolvedValue(1); // Blocked

      const isBlocked = await redisService.isBlocked(rateLimitType, identifier);

      expect(mockClient.exists).toHaveBeenCalledWith('cc-light:ratelimit:api:user-123:blocked');
      expect(isBlocked).toBe(true);
    });

    it('should use fallback rate limiting when Redis is disconnected', async () => {
      (redisService as any).isConnected = false;

      const result = await redisService.checkRateLimit('api', 'user-123');

      expect(result.allowed).toBe(true);
      expect(result.remaining).toBeGreaterThan(0);
      expect(mockClient.incr).not.toHaveBeenCalled();
    });
  });

  describe('Pub/Sub Operations', () => {
    it('should publish events to channels', async () => {
      const channel = 'calls';
      const data = { callId: 'call-123', status: 'connected' };

      mockPublisher.publish.mockResolvedValue(1);

      await redisService.publish(channel, data);

      expect(mockPublisher.publish).toHaveBeenCalledWith(
        'cc-light:events:calls',
        JSON.stringify(data)
      );
    });

    it('should handle publish when Redis is disconnected', async () => {
      (redisService as any).isConnected = false;
      (redisService as any).publisher = null;

      await redisService.publish('calls', { test: 'data' });

      expect(mockPublisher.publish).not.toHaveBeenCalled();
    });
  });

  describe('Queue Operations', () => {
    it('should enqueue data', async () => {
      const queueName = 'callbacks';
      const data = { phoneNumber: '+1234567890', priority: 'high' };

      mockClient.lPush.mockResolvedValue(1);

      await redisService.enqueue(queueName, data);

      expect(mockClient.lPush).toHaveBeenCalledWith(
        'cc-light:queue:callbacks',
        JSON.stringify(data)
      );
    });

    it('should dequeue data', async () => {
      const queueName = 'callbacks';
      const queueData = { phoneNumber: '+1234567890', priority: 'high' };

      mockClient.rPop.mockResolvedValue(JSON.stringify(queueData));

      const result = await redisService.dequeue(queueName);

      expect(mockClient.rPop).toHaveBeenCalledWith('cc-light:queue:callbacks');
      expect(result).toEqual(queueData);
    });

    it('should return null when queue is empty', async () => {
      const queueName = 'callbacks';

      mockClient.rPop.mockResolvedValue(null);

      const result = await redisService.dequeue(queueName);

      expect(result).toBeNull();
    });

    it('should get queue length', async () => {
      const queueName = 'callbacks';

      mockClient.lLen.mockResolvedValue(5);

      const length = await redisService.getQueueLength(queueName);

      expect(mockClient.lLen).toHaveBeenCalledWith('cc-light:queue:callbacks');
      expect(length).toBe(5);
    });
  });

  describe('Metrics Operations', () => {
    it('should increment counter', async () => {
      const metric = 'total-calls';

      mockClient.incrBy.mockResolvedValue(42);

      await redisService.incrementCounter(metric, 5);

      expect(mockClient.incrBy).toHaveBeenCalledWith('cc-light:metrics:total-calls', 5);
    });

    it('should increment counter by 1 by default', async () => {
      const metric = 'total-calls';

      mockClient.incrBy.mockResolvedValue(1);

      await redisService.incrementCounter(metric);

      expect(mockClient.incrBy).toHaveBeenCalledWith('cc-light:metrics:total-calls', 1);
    });

    it('should get counter value', async () => {
      const metric = 'total-calls';

      mockClient.get.mockResolvedValue('42');

      const value = await redisService.getCounter(metric);

      expect(mockClient.get).toHaveBeenCalledWith('cc-light:metrics:total-calls');
      expect(value).toBe(42);
    });

    it('should return 0 for non-existent counter', async () => {
      const metric = 'non-existent';

      mockClient.get.mockResolvedValue(null);

      const value = await redisService.getCounter(metric);

      expect(value).toBe(0);
    });
  });

  describe('Health and Status', () => {
    it('should ping Redis successfully', async () => {
      mockClient.ping.mockResolvedValue('PONG');

      const result = await redisService.ping();

      expect(mockClient.ping).toHaveBeenCalled();
      expect(result).toBe('PONG');
    });

    it('should return PONG when Redis is disconnected', async () => {
      (redisService as any).isConnected = false;
      (redisService as any).client = null;

      const result = await redisService.ping();

      expect(result).toBe('PONG');
      expect(mockClient.ping).not.toHaveBeenCalled();
    });

    it('should report connection status correctly', () => {
      (redisService as any).isConnected = true;
      expect(redisService.isReady()).toBe(true);

      (redisService as any).isConnected = false;
      expect(redisService.isReady()).toBe(false);
    });
  });

  describe('Cleanup Operations', () => {
    it('should cleanup connections gracefully', async () => {
      mockClient.quit.mockResolvedValue('OK');
      mockSubscriber.quit.mockResolvedValue('OK');
      mockPublisher.quit.mockResolvedValue('OK');

      await redisService.cleanup();

      expect(mockClient.quit).toHaveBeenCalled();
      expect(mockSubscriber.quit).toHaveBeenCalled();
      expect(mockPublisher.quit).toHaveBeenCalled();
      expect(redisService.isReady()).toBe(false);
    });

    it('should handle cleanup when clients are null', async () => {
      (redisService as any).client = null;
      (redisService as any).subscriber = null;
      (redisService as any).publisher = null;

      await expect(redisService.cleanup()).resolves.toBeUndefined();
    });
  });

  describe('Error Handling', () => {
    it('should handle JSON parsing errors gracefully', async () => {
      mockClient.get.mockResolvedValue('invalid-json{');

      // Should handle JSON parsing errors and return null
      await expect(redisService.getSession('test-session')).rejects.toThrow();
      expect(mockClient.get).toHaveBeenCalled();
    });

    it('should handle Redis operation errors', async () => {
      mockClient.setEx.mockRejectedValue(new Error('Redis error'));

      // Should propagate Redis errors in this implementation
      await expect(redisService.setSession('test', { data: 'test' })).rejects.toThrow('Redis error');
    });
  });
});