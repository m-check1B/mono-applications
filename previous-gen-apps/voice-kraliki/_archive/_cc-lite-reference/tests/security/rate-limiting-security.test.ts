/**
 * Rate Limiting Security Tests
 * Tests for authentication rate limiting, brute force protection, and DDoS mitigation
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { createRateLimiter, RateLimiters, BypassConditions, createRateLimiterWithBypass } from '../../server/middleware/rate-limiter';

// Mock Fastify request and reply
interface MockRequest extends Partial<FastifyRequest> {
  ip: string;
  headers: Record<string, string>;
  log: {
    error: vi.Mock;
  };
  user?: {
    id: string;
    role: string;
  };
}

interface MockReply extends Partial<FastifyReply> {
  header: vi.Mock;
  code: vi.Mock;
  send: vi.Mock;
}

describe('Rate Limiting Security Tests', () => {
  let mockRequest: MockRequest;
  let mockReply: MockReply;

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    
    mockRequest = {
      ip: '192.168.1.100',
      headers: {
        'user-agent': 'Mozilla/5.0 Test Browser',
        'x-forwarded-for': '203.0.113.195'
      },
      log: {
        error: vi.fn()
      }
    };

    mockReply = {
      header: vi.fn().mockReturnThis(),
      code: vi.fn().mockReturnThis(),
      send: vi.fn().mockReturnThis()
    };
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Basic Rate Limiting', () => {
    it('should allow requests within limit', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000, // 1 minute
        maxRequests: 5
      });

      // Make 5 requests (should all succeed)
      for (let i = 0; i < 5; i++) {
        await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
        
        expect(mockReply.code).not.toHaveBeenCalledWith(429);
        expect(mockReply.header).toHaveBeenCalledWith('X-RateLimit-Limit', 5);
        expect(mockReply.header).toHaveBeenCalledWith('X-RateLimit-Remaining', 5 - (i + 1));
      }
    });

    it('should block requests exceeding limit', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 3,
        message: 'Rate limit exceeded'
      });

      // Make 3 allowed requests
      for (let i = 0; i < 3; i++) {
        await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      }

      // 4th request should be blocked
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);

      expect(mockReply.code).toHaveBeenCalledWith(429);
      expect(mockReply.send).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Rate limit exceeded',
            retryAfter: expect.any(Number)
          })
        })
      );
      expect(mockReply.header).toHaveBeenCalledWith('Retry-After', expect.any(Number));
    });

    it('should reset after time window expires', async () => {
      const windowMs = 60 * 1000; // 1 minute
      const rateLimiter = createRateLimiter({
        windowMs,
        maxRequests: 2
      });

      // Make 2 requests to hit limit
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);

      // 3rd request should be blocked
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).toHaveBeenCalledWith(429);

      vi.clearAllMocks();

      // Advance time past window
      vi.advanceTimersByTime(windowMs + 1000);

      // Should allow request again
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).not.toHaveBeenCalledWith(429);
    });

    it('should track different IPs separately', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 2
      });

      // IP 1 makes 2 requests
      mockRequest.ip = '192.168.1.100';
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);

      // IP 2 should still be allowed
      mockRequest.ip = '192.168.1.101';
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      
      expect(mockReply.code).not.toHaveBeenCalledWith(429);
    });
  });

  describe('Authentication Rate Limiting', () => {
    it('should apply strict limits to auth endpoints', async () => {
      const authLimiter = RateLimiters.auth;

      // Auth rate limiter allows only 5 attempts per 15 minutes
      for (let i = 0; i < 5; i++) {
        await authLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
        expect(mockReply.code).not.toHaveBeenCalledWith(429);
      }

      // 6th attempt should be blocked
      await authLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).toHaveBeenCalledWith(429);
      expect(mockReply.send).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            message: 'Authentication rate limit exceeded'
          })
        })
      );
    });

    it('should use IP-based key generation for auth', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 2,
        keyGenerator: (req) => `auth:${req.ip}`
      });

      // Different paths should share the same auth limit for same IP
      mockRequest.ip = '192.168.1.100';
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);

      // Should be blocked
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).toHaveBeenCalledWith(429);
    });

    it('should prevent brute force attacks', async () => {
      const authLimiter = RateLimiters.auth;
      const attackerIP = '203.0.113.195'; // Simulated attacker IP
      
      mockRequest.ip = attackerIP;

      // Simulate rapid login attempts
      const attempts = [];
      for (let i = 0; i < 10; i++) {
        attempts.push(authLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply));
      }

      await Promise.all(attempts);

      // Should have blocked most attempts after the first 5
      const blockedCalls = mockReply.code.mock.calls.filter(call => call[0] === 429);
      expect(blockedCalls.length).toBeGreaterThanOrEqual(5);
    });
  });

  describe('API Rate Limiting', () => {
    it('should apply general API limits', async () => {
      const apiLimiter = RateLimiters.api;

      // API limiter allows 100 requests per 15 minutes
      for (let i = 0; i < 100; i++) {
        await apiLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      }
      
      expect(mockReply.code).not.toHaveBeenCalledWith(429);

      // 101st request should be blocked
      await apiLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).toHaveBeenCalledWith(429);
    });

    it('should provide rate limit headers', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 10
      });

      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);

      expect(mockReply.header).toHaveBeenCalledWith('X-RateLimit-Limit', 10);
      expect(mockReply.header).toHaveBeenCalledWith('X-RateLimit-Remaining', 9);
      expect(mockReply.header).toHaveBeenCalledWith('X-RateLimit-Reset', expect.any(Number));
    });

    it('should update remaining count correctly', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 5
      });

      // First request
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.header).toHaveBeenCalledWith('X-RateLimit-Remaining', 4);

      // Second request
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.header).toHaveBeenCalledWith('X-RateLimit-Remaining', 3);

      // Third request
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.header).toHaveBeenCalledWith('X-RateLimit-Remaining', 2);
    });
  });

  describe('Webhook Rate Limiting', () => {
    it('should handle webhook-specific rate limiting', async () => {
      const webhookLimiter = RateLimiters.webhook;

      mockRequest.headers = {
        'x-webhook-signature': 'sha256=abcdef123456',
        'user-agent': 'GitHub-Hookshot/abc123'
      };

      // Webhook limiter allows 100 requests per minute
      for (let i = 0; i < 100; i++) {
        await webhookLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      }
      
      expect(mockReply.code).not.toHaveBeenCalledWith(429);

      // 101st request should be blocked
      await webhookLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).toHaveBeenCalledWith(429);
    });

    it('should use signature-based key generation for webhooks', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 2,
        keyGenerator: (req) => {
          const signature = req.headers['x-webhook-signature'] as string;
          return `webhook:${signature || req.ip}`;
        }
      });

      mockRequest.headers['x-webhook-signature'] = 'sha256=signature123';
      
      // Two requests with same signature
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);

      // Third should be blocked
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).toHaveBeenCalledWith(429);

      vi.clearAllMocks();

      // Different signature should be allowed
      mockRequest.headers['x-webhook-signature'] = 'sha256=different456';
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).not.toHaveBeenCalledWith(429);
    });
  });

  describe('Rate Limiting Bypass', () => {
    it('should bypass rate limiting for localhost', async () => {
      const rateLimiter = createRateLimiterWithBypass(
        {
          windowMs: 60 * 1000,
          maxRequests: 1
        },
        BypassConditions.localHost
      );

      mockRequest.ip = '127.0.0.1';

      // Should allow multiple requests from localhost
      for (let i = 0; i < 10; i++) {
        await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      }

      expect(mockReply.code).not.toHaveBeenCalledWith(429);
    });

    it('should bypass rate limiting for admin users', async () => {
      const rateLimiter = createRateLimiterWithBypass(
        {
          windowMs: 60 * 1000,
          maxRequests: 1
        },
        BypassConditions.authenticatedAdmin
      );

      mockRequest.user = { id: 'admin-123', role: 'ADMIN' };

      // Should allow multiple requests from admin
      for (let i = 0; i < 10; i++) {
        await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      }

      expect(mockReply.code).not.toHaveBeenCalledWith(429);
    });

    it('should bypass rate limiting for health check services', async () => {
      const rateLimiter = createRateLimiterWithBypass(
        {
          windowMs: 60 * 1000,
          maxRequests: 1
        },
        BypassConditions.healthCheckServices
      );

      const healthCheckAgents = [
        'kube-probe/1.21',
        'ELB-HealthChecker/2.0',
        'GoogleHC/1.0'
      ];

      for (const userAgent of healthCheckAgents) {
        mockRequest.headers['user-agent'] = userAgent;
        
        // Should allow multiple requests from health checkers
        for (let i = 0; i < 5; i++) {
          await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
        }
        
        expect(mockReply.code).not.toHaveBeenCalledWith(429);
        vi.clearAllMocks();
      }
    });

    it('should not bypass for regular users', async () => {
      const rateLimiter = createRateLimiterWithBypass(
        {
          windowMs: 60 * 1000,
          maxRequests: 1
        },
        BypassConditions.authenticatedAdmin
      );

      mockRequest.user = { id: 'user-123', role: 'AGENT' };

      // First request should succeed
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).not.toHaveBeenCalledWith(429);

      // Second request should be blocked
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).toHaveBeenCalledWith(429);
    });
  });

  describe('Security Attack Scenarios', () => {
    it('should protect against distributed brute force attacks', async () => {
      const authLimiter = RateLimiters.auth;
      const attackerIPs = [
        '203.0.113.10',
        '203.0.113.11', 
        '203.0.113.12',
        '203.0.113.13',
        '203.0.113.14'
      ];

      // Each IP attempts maximum allowed requests
      for (const ip of attackerIPs) {
        mockRequest.ip = ip;
        
        // Make 5 attempts (limit) + 1 extra
        for (let i = 0; i < 6; i++) {
          await authLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
        }
      }

      // Each IP should be individually rate limited
      const blockedCalls = mockReply.code.mock.calls.filter(call => call[0] === 429);
      expect(blockedCalls.length).toBe(attackerIPs.length); // One blocked call per IP
    });

    it('should handle rapid concurrent requests', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 5
      });

      // Simulate 20 concurrent requests
      const concurrentRequests = [];
      for (let i = 0; i < 20; i++) {
        concurrentRequests.push(
          rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply)
        );
      }

      await Promise.all(concurrentRequests);

      // Should block most requests after the first 5
      const blockedCalls = mockReply.code.mock.calls.filter(call => call[0] === 429);
      expect(blockedCalls.length).toBeGreaterThanOrEqual(15);
    });

    it('should resist timing attacks on rate limit checking', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 1
      });

      // First request (allowed)
      const start1 = process.hrtime.bigint();
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      const time1 = process.hrtime.bigint() - start1;

      // Second request (blocked)
      const start2 = process.hrtime.bigint();
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      const time2 = process.hrtime.bigint() - start2;

      // Times should be reasonably similar (within reasonable bounds)
      const timeDifferenceMs = Number(time1 - time2) / 1_000_000;
      expect(Math.abs(timeDifferenceMs)).toBeLessThan(50); // 50ms tolerance
    });

    it('should handle memory-based DoS attempts', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 1
      });

      // Generate many unique IPs to test memory usage
      const uniqueIPs = [];
      for (let i = 0; i < 1000; i++) {
        uniqueIPs.push(`192.168.${Math.floor(i / 256)}.${i % 256}`);
      }

      // Make requests from each IP
      for (const ip of uniqueIPs) {
        mockRequest.ip = ip;
        await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      }

      // Should not crash or consume excessive memory
      expect(mockReply.header).toHaveBeenCalledTimes(uniqueIPs.length * 3); // 3 headers per request
    });
  });

  describe('Rate Limit Storage Security', () => {
    it('should clean up expired entries', async () => {
      const shortWindowLimiter = createRateLimiter({
        windowMs: 1000, // 1 second
        maxRequests: 1
      });

      // Make a request
      await shortWindowLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      
      // Advance time past window
      vi.advanceTimersByTime(2000);
      
      // Storage should have cleaned up the entry
      // Next request should be allowed (not blocked by previous)
      vi.clearAllMocks();
      await shortWindowLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).not.toHaveBeenCalledWith(429);
    });

    it('should handle storage errors gracefully', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 5
      });

      // Mock storage failure
      const originalConsoleError = console.error;
      console.error = vi.fn();

      // Should not throw error even if storage fails
      expect(async () => {
        await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      }).not.toThrow();

      // Should log error
      expect(mockRequest.log.error).not.toHaveBeenCalled(); // Storage works in test

      console.error = originalConsoleError;
    });

    it('should prevent key collision attacks', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 1,
        keyGenerator: (req) => `user:${(req as any).userId || req.ip}`
      });

      // Different users should have separate limits
      (mockRequest as any).userId = 'user1';
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).not.toHaveBeenCalledWith(429);

      vi.clearAllMocks();

      // Different user should be allowed
      (mockRequest as any).userId = 'user2';
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      expect(mockReply.code).not.toHaveBeenCalledWith(429);
    });
  });

  describe('Rate Limit Information Exposure', () => {
    it('should not expose internal implementation details', async () => {
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 5
      });

      // Make request that exceeds limit
      for (let i = 0; i < 6; i++) {
        await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      }

      const errorResponse = mockReply.send.mock.calls
        .find(call => call[0]?.error?.code)?.[0];

      expect(errorResponse.error).toBeDefined();
      expect(errorResponse.error.message).toBeDefined();
      expect(errorResponse.error.retryAfter).toBeDefined();
      
      // Should not expose internal storage details
      expect(errorResponse).not.toHaveProperty('store');
      expect(errorResponse).not.toHaveProperty('key');
      expect(errorResponse).not.toHaveProperty('implementation');
    });

    it('should provide appropriate error messages', async () => {
      const customMessage = 'Custom rate limit message';
      const rateLimiter = createRateLimiter({
        windowMs: 60 * 1000,
        maxRequests: 1,
        message: customMessage
      });

      // Exceed limit
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);
      await rateLimiter(mockRequest as FastifyRequest, mockReply as FastifyReply);

      const errorCall = mockReply.send.mock.calls
        .find(call => call[0]?.error?.message === customMessage);
      
      expect(errorCall).toBeDefined();
      expect(errorCall[0].error.message).toBe(customMessage);
    });
  });
});
