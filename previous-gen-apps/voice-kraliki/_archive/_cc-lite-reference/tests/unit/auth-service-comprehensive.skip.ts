/**
 * Comprehensive Authentication Service Tests
 * Updated to match current auth-service.ts implementation
 * Covers JWT, sessions, cookies, security, and all auth flows
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';

vi.mock('bcrypt', () => {
  const compare = vi.fn(async () => true);
  const hash = vi.fn(async () => '$2b$10$hashed_password');
  return {
    __esModule: true,
    default: { compare, hash },
    compare,
    hash
  };
});

import { AuthService } from '../../server/services/auth-service';
import { PrismaClient, UserRole, UserStatus } from '@prisma/client';
import bcrypt from 'bcrypt';
import { TRPCError } from '@trpc/server';
import * as crypto from 'crypto';

const bcryptCompareMock = vi.mocked(bcrypt.compare);
const bcryptHashMock = vi.mocked(bcrypt.hash);

// Mock PrismaClient with proper typing
const mockPrisma = {
  user: {
    findUnique: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    findMany: vi.fn(),
  },
  userSession: {
    findUnique: vi.fn(),
    findMany: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    updateMany: vi.fn(),
    deleteMany: vi.fn(),
  },
  organization: {
    findUnique: vi.fn(),
  },
} as unknown as PrismaClient;

// Mock environment variables
const originalEnv = process.env;

const mockEnvSecure = {
  NODE_ENV: 'test',
  AUTH_PRIVATE_KEY: '-----BEGIN PRIVATE KEY-----\nMC4CAQAwBQYDK2VwBCIEIC8v...\n-----END PRIVATE KEY-----',
  AUTH_PUBLIC_KEY: '-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEA...\n-----END PUBLIC KEY-----',
  JWT_SECRET: 'test-jwt-secret-256-bits-long-for-security',
  JWT_REFRESH_SECRET: 'test-refresh-secret-256-bits-long-for-security',
  SESSION_ENCRYPTION_KEY: crypto.randomBytes(32).toString('hex'),
  COOKIE_SECRET: 'test-cookie-secret-32-chars-long'
};

describe('AuthService - Comprehensive Tests', () => {
  let authService: AuthService;
  
  const mockUser = {
    id: 'user-123',
    email: 'test@cc-light.com',
    username: 'testuser',
    firstName: 'Test',
    lastName: 'User',
    passwordHash: '$2b$10$abcdefghijklmnopqrstuvwxyz123456789', // Mock bcrypt hash
    role: UserRole.AGENT,
    status: UserStatus.ACTIVE,
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
    sessionToken: 'jwt.token.here',
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

  beforeEach(() => {
    // Reset environment
    process.env = { ...originalEnv, ...mockEnvSecure };
    
    // Reset mocks
    vi.clearAllMocks();
    
    // Create fresh AuthService instance
    authService = new AuthService({ prisma: mockPrisma });
    
    // Default mock responses
    mockPrisma.user.findUnique.mockResolvedValue(mockUser);
    mockPrisma.userSession.create.mockResolvedValue(mockSession);
    mockPrisma.userSession.findUnique.mockResolvedValue(mockSession);
    mockPrisma.userSession.deleteMany.mockResolvedValue({ count: 1 });
  });

  afterEach(() => {
    vi.clearAllMocks();
    process.env = originalEnv;
  });

  describe('Key Initialization', () => {
    it('should initialize with provided keys', async () => {
      const service = new AuthService({
        prisma: mockPrisma,
        privateKey: mockEnvSecure.AUTH_PRIVATE_KEY,
        publicKey: mockEnvSecure.AUTH_PUBLIC_KEY
      });
      
      const publicKey = await service.getPublicKey();
      expect(publicKey).toBe(mockEnvSecure.AUTH_PUBLIC_KEY);
    });

    it('should generate development keys when not provided', async () => {
      process.env.NODE_ENV = 'development';
      delete process.env.AUTH_PRIVATE_KEY;
      delete process.env.AUTH_PUBLIC_KEY;
      
      const service = new AuthService({ prisma: mockPrisma });
      const publicKey = await service.getPublicKey();
      
      expect(publicKey).toContain('-----BEGIN PUBLIC KEY-----');
      expect(publicKey).toContain('-----END PUBLIC KEY-----');
    });

    it('should throw error in production without keys', async () => {
      process.env.NODE_ENV = 'production';
      delete process.env.AUTH_PRIVATE_KEY;
      delete process.env.AUTH_PUBLIC_KEY;
      
      expect(() => {
        new AuthService({ prisma: mockPrisma });
      }).toThrow('AUTH_PRIVATE_KEY and AUTH_PUBLIC_KEY must be provided in production');
    });
  });

  describe('Login', () => {
    it('should successfully login with valid credentials', async () => {
      bcryptCompareMock.mockResolvedValue(true);
      
      const result = await authService.login('test@cc-light.com', 'password123');
      
      expect(result).toHaveProperty('user');
      expect(result).toHaveProperty('token');
      expect(result).toHaveProperty('refreshToken');
      expect(result.user.email).toBe('test@cc-light.com');
      expect(result.user.id).toBe('user-123');
      
      // Verify session was created
      expect(mockPrisma.userSession.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          userId: 'user-123',
          sessionToken: expect.any(String),
          refreshTokenHash: expect.any(String),
          expiresAt: expect.any(Date)
        })
      });
    });

    it('should throw error for non-existent user', async () => {
      mockPrisma.user.findUnique.mockResolvedValue(null);
      
      await expect(authService.login('nonexistent@test.com', 'password'))
        .rejects.toThrow('Invalid credentials');
    });

    it('should throw error for user without password hash', async () => {
      mockPrisma.user.findUnique.mockResolvedValue({
        ...mockUser,
        passwordHash: null
      });
      
      await expect(authService.login('test@cc-light.com', 'password'))
        .rejects.toThrow('Password authentication not available');
    });

    it('should throw error for invalid password', async () => {
      bcryptCompareMock.mockResolvedValue(false);
      
      await expect(authService.login('test@cc-light.com', 'wrongpassword'))
        .rejects.toThrow('Invalid credentials');
    });

    it('should track login metadata', async () => {
      bcryptCompareMock.mockResolvedValue(true);
      
      await authService.createSessionForUserId('user-123', {
        ipAddress: '192.168.1.1',
        userAgent: 'Mozilla/5.0 Test Browser'
      });
      
      expect(mockPrisma.userSession.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          ipAddress: '192.168.1.1',
          userAgent: 'Mozilla/5.0 Test Browser'
        })
      });
    });
  });

  describe('Session Management', () => {
    it('should verify valid session token', async () => {
      const payload = await authService.verifySession('valid.jwt.token');
      
      expect(payload).toHaveProperty('sub');
      expect(payload).toHaveProperty('email');
      expect(payload).toHaveProperty('roles');
      
      // Verify session activity was updated
      expect(mockPrisma.userSession.update).toHaveBeenCalledWith({
        where: { id: 'session-123' },
        data: { lastActivity: expect.any(Date) }
      });
    });

    it('should reject expired session', async () => {
      mockPrisma.userSession.findUnique.mockResolvedValue({
        ...mockSession,
        expiresAt: new Date(Date.now() - 1000) // Expired 1 second ago
      });
      
      await expect(authService.verifySession('expired.token'))
        .rejects.toThrow('Invalid session');
    });

    it('should reject revoked session', async () => {
      mockPrisma.userSession.findUnique.mockResolvedValue({
        ...mockSession,
        revokedAt: new Date()
      });
      
      await expect(authService.verifySession('revoked.token'))
        .rejects.toThrow('Invalid session');
    });

    it('should cleanup expired sessions', async () => {
      mockPrisma.userSession.deleteMany.mockResolvedValue({ count: 5 });
      
      const cleanedCount = await authService.cleanupExpiredSessions();
      
      expect(cleanedCount).toBe(5);
      expect(mockPrisma.userSession.deleteMany).toHaveBeenCalledWith({
        where: {
          OR: [
            { expiresAt: { lt: expect.any(Date) } },
            { revokedAt: { not: null } }
          ]
        }
      });
    });
  });

  describe('Refresh Token Security', () => {
    it('should generate cryptographically secure refresh tokens', async () => {
      const { refreshToken: token1 } = await authService.createSessionForUserId('user-123');
      const { refreshToken: token2 } = await authService.createSessionForUserId('user-123');
      
      // Tokens should be different
      expect(token1).not.toBe(token2);
      
      // Should be base64url format
      expect(token1).toMatch(/^[A-Za-z0-9_-]+$/);
      expect(token2).toMatch(/^[A-Za-z0-9_-]+$/);
      
      // Should be at least 32 bytes (256 bits)
      const decoded1 = Buffer.from(token1, 'base64url');
      const decoded2 = Buffer.from(token2, 'base64url');
      
      expect(decoded1.length).toBeGreaterThanOrEqual(32);
      expect(decoded2.length).toBeGreaterThanOrEqual(32);
    });

    it('should store refresh tokens as hashes', async () => {
      const { refreshToken } = await authService.createSessionForUserId('user-123');
      
      // The stored hash should be different from the original token
      const createCall = mockPrisma.userSession.create.mock.calls[0][0];
      expect(createCall.data.refreshTokenHash).not.toBe(refreshToken);
      expect(createCall.data.refreshTokenHash).toMatch(/^[a-f0-9]{64}$/); // SHA-256 hex
    });

    it('should implement token rotation on refresh', async () => {
      mockPrisma.userSession.findUnique.mockResolvedValue({
        ...mockSession,
        user: mockUser
      });
      
      const { token: newToken, refreshToken: newRefreshToken } = 
        await authService.refreshSession('old_refresh_token');
      
      expect(newToken).toBeDefined();
      expect(newRefreshToken).toBeDefined();
      
      // Verify session was updated with new tokens
      expect(mockPrisma.userSession.update).toHaveBeenCalledWith({
        where: { id: 'session-123' },
        data: expect.objectContaining({
          sessionToken: newToken,
          refreshTokenHash: expect.any(String),
          lastActivity: expect.any(Date),
          lastRefreshAt: expect.any(Date),
          refreshCount: 1
        })
      });
    });

    it('should reject invalid refresh token', async () => {
      mockPrisma.userSession.findUnique.mockResolvedValue(null);
      
      await expect(authService.refreshSession('invalid_token'))
        .rejects.toThrow('Invalid or expired refresh token');
    });
  });

  describe('Password Security', () => {
    it('should hash passwords with bcrypt', async () => {
      bcryptHashMock.mockResolvedValue('$2b$10$hashed_password');
      
      await authService.createUser({
        email: 'newuser@test.com',
        password: 'SecurePassword123!',
        username: 'newuser',
        firstName: 'New',
        lastName: 'User',
        role: 'AGENT',
        organizationId: 'org-123'
      });
      
      expect(bcryptHashMock).toHaveBeenCalledWith('SecurePassword123!', 10);
      expect(mockPrisma.user.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          passwordHash: '$2b$10$hashed_password'
        })
      });
    });

    it('should validate current password when updating', async () => {
      bcryptCompareMock
        .mockResolvedValueOnce(false) // Wrong current password
        .mockResolvedValueOnce(true);  // Correct current password
      
      // Should fail with wrong current password
      await expect(authService.updatePassword('user-123', 'wrongpassword', 'newpassword'))
        .rejects.toThrow('Current password is incorrect');
      
      // Should succeed with correct password
      bcryptHashMock.mockResolvedValue('$2b$10$new_hashed_password');
      
      await authService.updatePassword('user-123', 'correctpassword', 'newpassword');
      
      expect(mockPrisma.user.update).toHaveBeenCalledWith({
        where: { id: 'user-123' },
        data: { passwordHash: '$2b$10$new_hashed_password' }
      });
      
      // Should invalidate all sessions after password change
      expect(mockPrisma.userSession.deleteMany).toHaveBeenCalledWith({
        where: { userId: 'user-123' }
      });
    });
  });

  describe('Logout Operations', () => {
    it('should logout by session token', async () => {
      await authService.logout('session.token.here');
      
      expect(mockPrisma.userSession.deleteMany).toHaveBeenCalledWith({
        where: { sessionToken: 'session.token.here' }
      });
    });

    it('should logout by refresh token', async () => {
      await authService.logoutByRefreshToken('refresh_token');
      
      expect(mockPrisma.userSession.deleteMany).toHaveBeenCalledWith({
        where: { refreshTokenHash: expect.any(String) }
      });
    });

    it('should revoke session without deleting', async () => {
      await authService.revokeSession('refresh_token');
      
      expect(mockPrisma.userSession.updateMany).toHaveBeenCalledWith({
        where: { refreshTokenHash: expect.any(String) },
        data: { revokedAt: expect.any(Date) }
      });
    });

    it('should invalidate all user sessions', async () => {
      await authService.invalidateAllUserSessions('user-123');
      
      expect(mockPrisma.userSession.deleteMany).toHaveBeenCalledWith({
        where: { userId: 'user-123' }
      });
    });
  });

  describe('User Management', () => {
    it('should create user with proper validation', async () => {
      bcryptHashMock.mockResolvedValue('$2b$10$hashed_password');
      
      const userData = {
        email: 'newuser@test.com',
        password: 'SecurePassword123!',
        username: 'newuser',
        firstName: 'New',
        lastName: 'User',
        role: 'agent' as const, // Test case normalization
        organizationId: 'org-123',
        phoneExtension: '5678',
        skills: ['support', 'billing'],
        department: 'Customer Service'
      };
      
      await authService.createUser(userData);
      
      expect(mockPrisma.user.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          email: 'newuser@test.com',
          role: 'AGENT', // Should be normalized to uppercase
          status: UserStatus.ACTIVE,
          skills: ['support', 'billing'],
          department: 'Customer Service'
        })
      });
    });

    it('should validate role values', async () => {
      await expect(authService.createUser({
        email: 'test@test.com',
        password: 'password',
        username: 'test',
        firstName: 'Test',
        lastName: 'User',
        role: 'INVALID_ROLE' as any,
        organizationId: 'org-123'
      })).rejects.toThrow('Invalid role');
    });

    it('should update user information', async () => {
      const updates = {
        firstName: 'Updated',
        lastName: 'Name',
        role: 'supervisor',
        skills: ['leadership', 'training']
      };
      
      await authService.updateUser('user-123', updates);
      
      expect(mockPrisma.user.update).toHaveBeenCalledWith({
        where: { id: 'user-123' },
        data: expect.objectContaining({
          firstName: 'Updated',
          lastName: 'Name',
          role: 'SUPERVISOR', // Should be normalized
          skills: ['leadership', 'training']
        }),
        select: expect.any(Object)
      });
    });
  });

  describe('Security Monitoring', () => {
    it('should detect suspicious refresh activity', async () => {
      const suspiciousSessions = [
        { ...mockSession, refreshCount: 150 }, // Excessive refreshes
        { ...mockSession, id: 'session-2', refreshCount: 200 }
      ];
      
      mockPrisma.userSession.findMany.mockResolvedValue(suspiciousSessions);
      
      const analysis = await authService.detectSuspiciousActivity('user-123');
      
      expect(analysis.suspiciousRefreshes).toBe(true);
      expect(analysis.riskLevel).toBe('high');
      expect(analysis.recommendations).toContain(
        expect.stringContaining('excessive token refreshes')
      );
    });

    it('should detect multiple active devices', async () => {
      const multipleSessions = Array.from({ length: 6 }, (_, i) => ({
        ...mockSession,
        id: `session-${i}`,
        userAgent: `Browser ${i}`
      }));
      
      mockPrisma.userSession.findMany.mockResolvedValue(multipleSessions);
      
      const analysis = await authService.detectSuspiciousActivity('user-123');
      
      expect(analysis.multipleActiveDevices).toBe(true);
      expect(analysis.sessionCount).toBe(6);
      expect(analysis.recommendations).toContain(
        expect.stringContaining('6 active sessions')
      );
    });

    it('should get active user sessions', async () => {
      const activeSessions = [
        {
          id: 'session-1',
          createdAt: new Date(),
          lastActivity: new Date(),
          refreshCount: 5,
          ipAddress: '192.168.1.1',
          userAgent: 'Chrome Browser'
        }
      ];
      
      mockPrisma.userSession.findMany.mockResolvedValue(activeSessions);
      
      const sessions = await authService.getUserActiveSessions('user-123');
      
      expect(sessions).toHaveLength(1);
      expect(sessions[0]).toMatchObject({
        id: 'session-1',
        refreshCount: 5,
        ipAddress: '192.168.1.1',
        userAgent: 'Chrome Browser'
      });
      
      expect(mockPrisma.userSession.findMany).toHaveBeenCalledWith({
        where: {
          userId: 'user-123',
          expiresAt: { gt: expect.any(Date) },
          revokedAt: null
        },
        select: expect.any(Object),
        orderBy: { lastActivity: 'desc' }
      });
    });
  });

  describe('Cookie Integration', () => {
    it('should set session cookies securely', () => {
      const mockReply = {
        setCookie: vi.fn()
      };
      
      // Mock the secure cookie manager import
      const mockSecureCookieManager = {
        setAuthCookie: vi.fn()
      };
      
      vi.doMock('../../server/utils/secure-cookie-manager', () => ({
        secureCookieManager: mockSecureCookieManager
      }));
      
      authService.setSessionCookie(mockReply, 'jwt.token.here');
      
      expect(mockSecureCookieManager.setAuthCookie).toHaveBeenCalledWith(
        mockReply,
        'jwt.token.here'
      );
    });

    it('should clear session cookies securely', () => {
      const mockReply = {
        clearCookie: vi.fn()
      };
      
      const mockSecureCookieManager = {
        clearAuthCookies: vi.fn()
      };
      
      vi.doMock('../../server/utils/secure-cookie-manager', () => ({
        secureCookieManager: mockSecureCookieManager
      }));
      
      authService.clearSessionCookie(mockReply);
      
      expect(mockSecureCookieManager.clearAuthCookies).toHaveBeenCalledWith(mockReply);
    });
  });

  describe('Access Token Verification', () => {
    it('should verify access token and return user metadata', async () => {
      const result = await authService.verifyAccessToken('valid.jwt.token');
      
      expect(result).toMatchObject({
        id: 'user-123',
        email: 'test@cc-light.com',
        role: 'AGENT',
        organizationId: 'org-123',
        roles: ['agent']
      });
    });

    it('should return null for invalid token', async () => {
      // Mock verifySession to throw error
      vi.spyOn(authService, 'verifySession').mockRejectedValue(new Error('Invalid token'));
      
      const result = await authService.verifyAccessToken('invalid.token');
      
      expect(result).toBeNull();
    });

    it('should return null for non-existent user', async () => {
      mockPrisma.user.findUnique.mockResolvedValue(null);
      
      const result = await authService.verifyAccessToken('valid.token');
      
      expect(result).toBeNull();
    });
  });

  describe('Error Handling', () => {
    it('should handle database errors gracefully', async () => {
      mockPrisma.user.findUnique.mockRejectedValue(new Error('Database connection failed'));
      
      await expect(authService.login('test@test.com', 'password'))
        .rejects.toThrow('Database connection failed');
    });

    it('should handle malformed JWT tokens', async () => {
      await expect(authService.verifySession('malformed.jwt.token'))
        .rejects.toThrow('Invalid session');
    });

    it('should handle bcrypt errors gracefully', async () => {
      bcryptCompareMock.mockRejectedValue(new Error('Bcrypt error'));
      
      await expect(authService.login('test@test.com', 'password'))
        .rejects.toThrow('Bcrypt error');
    });
  });

  describe('Timing Attack Prevention', () => {
    it('should have consistent response times for user lookup', async () => {
      const validEmail = 'test@cc-light.com';
      const invalidEmail = 'nonexistent@test.com';
      
      // Mock responses
      mockPrisma.user.findUnique
        .mockResolvedValueOnce(mockUser)  // Valid user
        .mockResolvedValueOnce(null);     // Invalid user
      
      bcryptCompareMock.mockResolvedValue(false); // Wrong password
      
      // Measure timing for valid user with wrong password
      const start1 = Date.now();
      try {
        await authService.login(validEmail, 'wrongpassword');
      } catch {}
      const time1 = Date.now() - start1;
      
      // Measure timing for invalid user
      const start2 = Date.now();
      try {
        await authService.login(invalidEmail, 'anypassword');
      } catch {}
      const time2 = Date.now() - start2;
      
      // Times should be reasonably similar (within reasonable bounds)
      const timeDifference = Math.abs(time1 - time2);
      expect(timeDifference).toBeLessThan(50); // 50ms tolerance for test environment
    });
  });
});
