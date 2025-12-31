/**
 * Authentication Middleware Integration Tests
 * Tests complete auth flow integration with middleware, cookies, sessions, and security
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import Fastify from 'fastify';
import { AuthService } from '../../server/services/auth-service';
import { PrismaClient } from '@prisma/client';
import { SecureCookieManager } from '../../server/utils/secure-cookie-manager';
import { RateLimiters } from '../../server/middleware/rate-limiter';
import * as crypto from 'crypto';

// Mock PrismaClient
const mockPrisma = {
  user: {
    findUnique: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
  userSession: {
    findUnique: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    deleteMany: vi.fn(),
    updateMany: vi.fn(),
    findMany: vi.fn(),
  },
  organization: {
    findUnique: vi.fn(),
  },
} as unknown as PrismaClient;

const originalEnv = process.env;

const mockEnvSecure = {
  NODE_ENV: 'test',
  AUTH_PRIVATE_KEY: '-----BEGIN PRIVATE KEY-----\nMC4CAQAwBQYDK2VwBCIEIC8v...\n-----END PRIVATE KEY-----',
  AUTH_PUBLIC_KEY: '-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEA...\n-----END PUBLIC KEY-----',
  JWT_SECRET: 'test-jwt-secret-256-bits-long-for-security-testing',
  JWT_REFRESH_SECRET: 'test-refresh-secret-256-bits-long-for-security',
  COOKIE_SECRET: crypto.randomBytes(32).toString('hex'),
  COOKIE_ENCRYPTION_KEY: crypto.randomBytes(32).toString('hex'),
  SESSION_ENCRYPTION_KEY: crypto.randomBytes(32).toString('hex')
};

describe('Auth Middleware Integration Tests', () => {
  let app: FastifyInstance;
  let authService: AuthService;
  let cookieManager: SecureCookieManager;
  
  const mockUser = {
    id: 'user-123',
    email: 'test@cc-light.com',
    username: 'testuser',
    firstName: 'Test',
    lastName: 'User',
    passwordHash: '$2b$10$abcdefghijklmnopqrstuvwxyz123456789',
    role: 'AGENT',
    status: 'ACTIVE',
    organizationId: 'org-123',
    phoneExtension: '1234',
    avatar: null,
    lastLoginAt: null,
    createdAt: new Date(),
    updatedAt: new Date(),
    skills: ['customer-service'],
    department: 'Support',
    preferences: {},
    organization: {
      id: 'org-123',
      name: 'Test Organization'
    }
  };

  const mockSession = {
    id: 'session-123',
    userId: 'user-123',
    sessionToken: 'valid.jwt.token',
    refreshTokenHash: 'hashed_refresh_token',
    expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    createdAt: new Date(),
    lastActivity: new Date(),
    lastRefreshAt: null,
    refreshCount: 0,
    ipAddress: '127.0.0.1',
    userAgent: 'Test Browser',
    revokedAt: null
  };

  beforeEach(async () => {
    // Setup secure environment
    process.env = { ...originalEnv, ...mockEnvSecure };
    
    // Reset mocks
    vi.clearAllMocks();
    
    // Create services
    authService = new AuthService({ prisma: mockPrisma });
    cookieManager = new SecureCookieManager();
    
    // Setup default mock responses
    mockPrisma.user.findUnique.mockResolvedValue(mockUser);
    mockPrisma.userSession.create.mockResolvedValue(mockSession);
    mockPrisma.userSession.findUnique.mockResolvedValue(mockSession);
    mockPrisma.userSession.update.mockResolvedValue(mockSession);
    mockPrisma.userSession.deleteMany.mockResolvedValue({ count: 1 });
    
    // Create Fastify app with middleware
    app = Fastify({ logger: false });
    
    // Register auth middleware
    app.addHook('preHandler', async (request, reply) => {
      // Add auth service to request context
      (request as any).authService = authService;
      (request as any).cookieManager = cookieManager;
    });
    
    // Authentication middleware
    const authenticateRequest = async (request: FastifyRequest, reply: FastifyReply) => {
      const authCookie = cookieManager.getAuthCookie(request);
      
      if (!authCookie) {
        return reply.code(401).send({
          error: 'Authentication required',
          code: 'UNAUTHORIZED'
        });
      }
      
      try {
        const payload = await authService.verifySession(authCookie);
        (request as any).user = {
          id: payload.sub,
          email: payload.email,
          roles: payload.roles
        };
      } catch (error) {
        return reply.code(401).send({
          error: 'Invalid or expired session',
          code: 'UNAUTHORIZED'
        });
      }
    };
    
    // Protected route
    app.get('/api/protected', {
      preHandler: [RateLimiters.api, authenticateRequest]
    }, async (request, reply) => {
      return {
        message: 'Protected resource accessed',
        user: (request as any).user
      };
    });
    
    // Auth endpoints
    app.post('/api/auth/login', {
      preHandler: [RateLimiters.auth]
    }, async (request, reply) => {
      const { email, password } = request.body as { email: string; password: string };
      
      try {
        const result = await authService.login(email, password);
        
        // Set secure cookie
        cookieManager.setAuthCookie(reply, result.token);
        
        return {
          user: result.user,
          message: 'Login successful'
        };
      } catch (error: any) {
        return reply.code(401).send({
          error: error.message,
          code: 'UNAUTHORIZED'
        });
      }
    });
    
    app.post('/api/auth/logout', {
      preHandler: [authenticateRequest]
    }, async (request, reply) => {
      const authCookie = cookieManager.getAuthCookie(request);
      
      if (authCookie) {
        await authService.logout(authCookie);
      }
      
      cookieManager.clearAuthCookies(reply);
      
      return {
        message: 'Logged out successfully'
      };
    });
    
    app.post('/api/auth/refresh', {
      preHandler: [RateLimiters.auth]
    }, async (request, reply) => {
      const { refreshToken } = request.body as { refreshToken: string };
      
      try {
        const result = await authService.refreshSession(refreshToken);
        
        cookieManager.setAuthCookie(reply, result.token);
        
        return {
          message: 'Token refreshed successfully'
        };
      } catch (error: any) {
        return reply.code(401).send({
          error: error.message,
          code: 'UNAUTHORIZED'
        });
      }
    });
    
    // Public health endpoint
    app.get('/health', {
      preHandler: [RateLimiters.health]
    }, async () => {
      return { status: 'ok' };
    });
    
    await app.ready();
  });
  
  afterEach(async () => {
    if (app) {
      await app.close();
    }
    process.env = originalEnv;
  });

  describe('Authentication Flow Integration', () => {
    it('should complete full login flow with cookie setting', async () => {
      vi.spyOn(require('bcrypt'), 'compare').mockResolvedValue(true);
      
      const response = await app.inject({
        method: 'POST',
        url: '/api/auth/login',
        payload: {
          email: 'test@cc-light.com',
          password: 'password123'
        }
      });
      
      expect(response.statusCode).toBe(200);
      
      const result = JSON.parse(response.body);
      expect(result.user.email).toBe('test@cc-light.com');
      expect(result.message).toBe('Login successful');
      
      // Should set secure auth cookies
      const cookies = response.cookies;
      expect(cookies).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            name: 'vd_session',
            httpOnly: true,
            secure: false, // false in test environment
            sameSite: 'Strict'
          }),
          expect.objectContaining({
            name: 'cc_light_session',
            httpOnly: true,
            secure: false,
            sameSite: 'Strict'
          })
        ])
      );
    });
    
    it('should access protected resources with valid session', async () => {
      // Mock session creation first
      const { token } = await authService.createSessionForUserId('user-123');
      
      // Create cookie value
      const cookieValue = cookieManager.setCookie(
        { setCookie: vi.fn() } as any,
        'vd_session',
        token
      );
      
      const response = await app.inject({
        method: 'GET',
        url: '/api/protected',
        cookies: {
          vd_session: token // Use raw token for test
        }
      });
      
      expect(response.statusCode).toBe(200);
      
      const result = JSON.parse(response.body);
      expect(result.message).toBe('Protected resource accessed');
      expect(result.user.id).toBe('user-123');
    });
    
    it('should reject access without authentication', async () => {
      const response = await app.inject({
        method: 'GET',
        url: '/api/protected'
      });
      
      expect(response.statusCode).toBe(401);
      
      const result = JSON.parse(response.body);
      expect(result.error).toBe('Authentication required');
      expect(result.code).toBe('UNAUTHORIZED');
    });
    
    it('should complete logout flow and clear cookies', async () => {
      const { token } = await authService.createSessionForUserId('user-123');
      
      const response = await app.inject({
        method: 'POST',
        url: '/api/auth/logout',
        cookies: {
          vd_session: token
        }
      });
      
      expect(response.statusCode).toBe(200);
      
      const result = JSON.parse(response.body);
      expect(result.message).toBe('Logged out successfully');
      
      // Should clear auth cookies
      const cookies = response.cookies;
      expect(cookies).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            name: 'vd_session',
            value: '', // Cleared cookie has empty value
            expires: expect.any(Date)
          }),
          expect.objectContaining({
            name: 'cc_light_session',
            value: '',
            expires: expect.any(Date)
          })
        ])
      );
      
      // Verify session was deleted
      expect(mockPrisma.userSession.deleteMany).toHaveBeenCalledWith({
        where: { sessionToken: token }
      });
    });
  });

  describe('Rate Limiting Integration', () => {
    it('should apply rate limits to auth endpoints', async () => {
      vi.spyOn(require('bcrypt'), 'compare').mockResolvedValue(false);
      
      // Make multiple failed login attempts (auth rate limit is 5 per 15 minutes)
      const requests = [];
      for (let i = 0; i < 6; i++) {
        requests.push(
          app.inject({
            method: 'POST',
            url: '/api/auth/login',
            payload: {
              email: 'test@cc-light.com',
              password: 'wrongpassword'
            }
          })
        );
      }
      
      const responses = await Promise.all(requests);
      
      // First 5 should be rate limit allowed (but auth failed)
      const authFailures = responses.slice(0, 5);
      authFailures.forEach(response => {
        expect(response.statusCode).toBe(401); // Auth failed, not rate limited
      });
      
      // 6th should be rate limited
      const rateLimited = responses[5];
      expect(rateLimited.statusCode).toBe(429);
      
      const result = JSON.parse(rateLimited.body);
      expect(result.error.message).toContain('Authentication rate limit exceeded');
    });
    
    it('should apply rate limits to API endpoints', async () => {
      const { token } = await authService.createSessionForUserId('user-123');
      
      // Make multiple API requests (limit is 100 per 15 minutes)
      const requests = [];
      for (let i = 0; i < 102; i++) {
        requests.push(
          app.inject({
            method: 'GET',
            url: '/api/protected',
            cookies: {
              vd_session: token
            }
          })
        );
      }
      
      const responses = await Promise.all(requests);
      
      // First 100 should succeed
      const successful = responses.slice(0, 100);
      successful.forEach(response => {
        expect(response.statusCode).toBe(200);
      });
      
      // 101st and 102nd should be rate limited
      const rateLimited = responses.slice(100);
      rateLimited.forEach(response => {
        expect(response.statusCode).toBe(429);
      });
    });
    
    it('should include rate limit headers in responses', async () => {
      const response = await app.inject({
        method: 'GET',
        url: '/health'
      });
      
      expect(response.statusCode).toBe(200);
      expect(response.headers['x-ratelimit-limit']).toBeDefined();
      expect(response.headers['x-ratelimit-remaining']).toBeDefined();
      expect(response.headers['x-ratelimit-reset']).toBeDefined();
    });
  });

  describe('Session Security Integration', () => {
    it('should reject expired sessions', async () => {
      // Mock expired session
      mockPrisma.userSession.findUnique.mockResolvedValue({
        ...mockSession,
        expiresAt: new Date(Date.now() - 1000) // Expired 1 second ago
      });
      
      const response = await app.inject({
        method: 'GET',
        url: '/api/protected',
        cookies: {
          vd_session: 'expired.jwt.token'
        }
      });
      
      expect(response.statusCode).toBe(401);
      
      const result = JSON.parse(response.body);
      expect(result.error).toBe('Invalid or expired session');
    });
    
    it('should reject revoked sessions', async () => {
      // Mock revoked session
      mockPrisma.userSession.findUnique.mockResolvedValue({
        ...mockSession,
        revokedAt: new Date()
      });
      
      const response = await app.inject({
        method: 'GET',
        url: '/api/protected',
        cookies: {
          vd_session: 'revoked.jwt.token'
        }
      });
      
      expect(response.statusCode).toBe(401);
      
      const result = JSON.parse(response.body);
      expect(result.error).toBe('Invalid or expired session');
    });
    
    it('should update session activity on access', async () => {
      const { token } = await authService.createSessionForUserId('user-123');
      
      await app.inject({
        method: 'GET',
        url: '/api/protected',
        cookies: {
          vd_session: token
        }
      });
      
      // Should update last activity
      expect(mockPrisma.userSession.update).toHaveBeenCalledWith({
        where: { id: 'session-123' },
        data: { lastActivity: expect.any(Date) }
      });
    });
    
    it('should handle token refresh flow', async () => {
      mockPrisma.userSession.findUnique.mockResolvedValue({
        ...mockSession,
        user: mockUser
      });
      
      const response = await app.inject({
        method: 'POST',
        url: '/api/auth/refresh',
        payload: {
          refreshToken: 'valid_refresh_token'
        }
      });
      
      expect(response.statusCode).toBe(200);
      
      const result = JSON.parse(response.body);
      expect(result.message).toBe('Token refreshed successfully');
      
      // Should set new auth cookies
      const cookies = response.cookies;
      expect(cookies).toEqual(
        expect.arrayContaining([
          expect.objectContaining({
            name: 'vd_session'
          })
        ])
      );
    });
  });

  describe('Cookie Security Integration', () => {
    it('should set secure cookie attributes', async () => {
      vi.spyOn(require('bcrypt'), 'compare').mockResolvedValue(true);
      
      const response = await app.inject({
        method: 'POST',
        url: '/api/auth/login',
        payload: {
          email: 'test@cc-light.com',
          password: 'password123'
        }
      });
      
      const cookies = response.cookies;
      cookies.forEach(cookie => {
        if (cookie.name.includes('session')) {
          expect(cookie.httpOnly).toBe(true);
          expect(cookie.sameSite).toBe('Strict');
          expect(cookie.path).toBe('/');
          expect(cookie.maxAge).toBeGreaterThan(0);
        }
      });
    });
    
    it('should support cookie fallback mechanisms', async () => {
      const { token } = await authService.createSessionForUserId('user-123');
      
      // Test with backup cookie only
      const response = await app.inject({
        method: 'GET',
        url: '/api/protected',
        cookies: {
          cc_light_session: token // Using backup cookie
        }
      });
      
      expect(response.statusCode).toBe(200);
      
      const result = JSON.parse(response.body);
      expect(result.user.id).toBe('user-123');
    });
    
    it('should clear all session cookies on logout', async () => {
      const { token } = await authService.createSessionForUserId('user-123');
      
      const response = await app.inject({
        method: 'POST',
        url: '/api/auth/logout',
        cookies: {
          vd_session: token,
          cc_light_session: token
        }
      });
      
      const cookies = response.cookies;
      const clearedCookies = cookies.filter(cookie => 
        cookie.name === 'vd_session' || cookie.name === 'cc_light_session'
      );
      
      expect(clearedCookies).toHaveLength(2);
      clearedCookies.forEach(cookie => {
        expect(cookie.value).toBe('');
        expect(cookie.expires).toBeInstanceOf(Date);
      });
    });
  });

  describe('Error Handling Integration', () => {
    it('should handle database errors gracefully', async () => {
      mockPrisma.user.findUnique.mockRejectedValue(new Error('Database connection failed'));
      
      const response = await app.inject({
        method: 'POST',
        url: '/api/auth/login',
        payload: {
          email: 'test@cc-light.com',
          password: 'password123'
        }
      });
      
      expect(response.statusCode).toBe(401);
      
      const result = JSON.parse(response.body);
      expect(result.error).toContain('Database connection failed');
    });
    
    it('should handle malformed auth cookies', async () => {
      const response = await app.inject({
        method: 'GET',
        url: '/api/protected',
        cookies: {
          vd_session: 'malformed.cookie.value'
        }
      });
      
      expect(response.statusCode).toBe(401);
      
      const result = JSON.parse(response.body);
      expect(result.error).toBe('Invalid or expired session');
    });
    
    it('should handle missing session in database', async () => {
      mockPrisma.userSession.findUnique.mockResolvedValue(null);
      
      const response = await app.inject({
        method: 'GET',
        url: '/api/protected',
        cookies: {
          vd_session: 'valid.jwt.token'
        }
      });
      
      expect(response.statusCode).toBe(401);
      
      const result = JSON.parse(response.body);
      expect(result.error).toBe('Invalid or expired session');
    });
  });

  describe('Security Headers Integration', () => {
    it('should include security headers in responses', async () => {
      const response = await app.inject({
        method: 'GET',
        url: '/health'
      });
      
      // Rate limiting headers should be present
      expect(response.headers['x-ratelimit-limit']).toBeDefined();
      expect(response.headers['x-ratelimit-remaining']).toBeDefined();
      expect(response.headers['x-ratelimit-reset']).toBeDefined();
    });
    
    it('should handle concurrent authentication requests safely', async () => {
      const { token } = await authService.createSessionForUserId('user-123');
      
      // Make multiple concurrent requests
      const requests = [];
      for (let i = 0; i < 10; i++) {
        requests.push(
          app.inject({
            method: 'GET',
            url: '/api/protected',
            cookies: {
              vd_session: token
            }
          })
        );
      }
      
      const responses = await Promise.all(requests);
      
      // All should succeed
      responses.forEach(response => {
        expect(response.statusCode).toBe(200);
      });
      
      // Should update session activity for each request
      expect(mockPrisma.userSession.update).toHaveBeenCalledTimes(10);
    });
  });
});
