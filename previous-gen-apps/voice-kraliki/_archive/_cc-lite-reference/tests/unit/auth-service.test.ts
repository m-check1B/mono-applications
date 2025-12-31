import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AuthService } from '../../server/auth/auth-service';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';

// Mock PrismaClient
const mockPrisma = {
  user: {
    findFirst: vi.fn(),
    findUnique: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
  userSession: {
    create: vi.fn(),
    findMany: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
  organization: {
    findFirst: vi.fn(),
  },
  $metrics: {
    json: vi.fn().mockResolvedValue({}),
  },
  $queryRaw: vi.fn().mockResolvedValue([1]),
} as unknown as PrismaClient;

// Mock environment variables
process.env.JWT_SECRET = 'test-jwt-secret';
process.env.JWT_REFRESH_SECRET = 'test-refresh-secret';
process.env.JWT_ACCESS_TOKEN_EXPIRES_IN = '15m';
process.env.JWT_REFRESH_TOKEN_EXPIRES_IN = '7d';

describe.skip('AuthService', () => {
  let authService: AuthService;

  beforeEach(() => {
    vi.clearAllMocks();
    authService = new AuthService(mockPrisma);
  });

  describe('login', () => {
    it('should successfully login with valid credentials', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        passwordHash: bcrypt.hashSync('password123', 10),
        role: 'USER',
        organizationId: 'org-1',
        status: 'ACTIVE',
      };

      mockPrisma.user.findFirst = vi.fn().mockResolvedValue(mockUser);
      mockPrisma.userSession.create = vi.fn().mockResolvedValue({});

      const result = await authService.login('test@example.com', 'password123');

      expect(result).toHaveProperty('user');
      expect(result).toHaveProperty('accessToken');
      expect(result).toHaveProperty('refreshToken');
      expect(result).toHaveProperty('expiresIn');
      expect(result.user.email).toBe('test@example.com');
      expect(result.user.role).toBe('USER');
    });

    it('should throw error for invalid email', async () => {
      mockPrisma.user.findFirst = vi.fn().mockResolvedValue(null);

      await expect(authService.login('invalid@example.com', 'password123'))
        .rejects.toThrow('Invalid credentials');
    });

    it('should throw error for invalid password', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        passwordHash: bcrypt.hashSync('password123', 10),
        role: 'USER',
        organizationId: 'org-1',
        status: 'ACTIVE',
      };

      mockPrisma.user.findFirst = vi.fn().mockResolvedValue(mockUser);

      await expect(authService.login('test@example.com', 'wrongpassword'))
        .rejects.toThrow('Invalid credentials');
    });

    it('should throw error for inactive user', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        passwordHash: bcrypt.hashSync('password123', 10),
        role: 'USER',
        organizationId: 'org-1',
        status: 'INACTIVE',
      };

      mockPrisma.user.findFirst = vi.fn().mockResolvedValue(mockUser);

      await expect(authService.login('test@example.com', 'password123'))
        .rejects.toThrow('Invalid credentials');
    });

    it('should throw error for user without password hash', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        passwordHash: null,
        role: 'USER',
        organizationId: 'org-1',
        status: 'ACTIVE',
      };

      mockPrisma.user.findFirst = vi.fn().mockResolvedValue(mockUser);

      await expect(authService.login('test@example.com', 'password123'))
        .rejects.toThrow('Invalid credentials');
    });
  });

  describe('register', () => {
    it('should successfully register a new user', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'newuser@example.com',
        passwordHash: bcrypt.hashSync('password123', 10),
        role: 'USER',
        organizationId: 'org-1',
        status: 'ACTIVE',
      };

      mockPrisma.user.findFirst = vi.fn().mockResolvedValue(null);
      mockPrisma.organization.findFirst = vi.fn().mockResolvedValue({ id: 'org-1' });
      mockPrisma.user.create = vi.fn().mockResolvedValue(mockUser);

      const result = await authService.register({
        email: 'newuser@example.com',
        password: 'password123',
        firstName: 'John',
        lastName: 'Doe',
        organizationId: 'org-1',
      });

      expect(result).toHaveProperty('user');
      expect(result).toHaveProperty('accessToken');
      expect(result).toHaveProperty('refreshToken');
      expect(result).toHaveProperty('expiresIn');
      expect(result.user.email).toBe('newuser@example.com');
    });

    it('should throw error for existing email', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'existing@example.com',
        passwordHash: bcrypt.hashSync('password123', 10),
        role: 'USER',
        organizationId: 'org-1',
        status: 'ACTIVE',
      };

      mockPrisma.user.findFirst = vi.fn().mockResolvedValue(mockUser);

      await expect(authService.register({
        email: 'existing@example.com',
        password: 'password123',
        firstName: 'John',
        lastName: 'Doe',
        organizationId: 'org-1',
      })).rejects.toThrow('User with this email already exists');
    });

    it('should throw error for non-existent organization', async () => {
      mockPrisma.user.findFirst = vi.fn().mockResolvedValue(null);
      mockPrisma.organization.findFirst = vi.fn().mockResolvedValue(null);

      await expect(authService.register({
        email: 'newuser@example.com',
        password: 'password123',
        firstName: 'John',
        lastName: 'Doe',
        organizationId: 'org-1',
      })).rejects.toThrow('Organization not found');
    });
  });

  describe('verifyToken', () => {
    it('should verify valid access token', async () => {
      const validToken = jwt.sign(
        { id: 'user-1', email: 'test@example.com', role: 'USER', organizationId: 'org-1' },
        process.env.JWT_SECRET!,
        { expiresIn: '15m' }
      );

      const result = await authService.verifyToken(validToken);

      expect(result).toHaveProperty('id', 'user-1');
      expect(result).toHaveProperty('email', 'test@example.com');
      expect(result).toHaveProperty('role', 'USER');
      expect(result).toHaveProperty('organizationId', 'org-1');
    });

    it('should verify valid refresh token', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        passwordHash: bcrypt.hashSync('password123', 10),
        role: 'USER',
        organizationId: 'org-1',
        status: 'ACTIVE',
      };

      const mockSession = {
        id: 'session-1',
        userId: 'user-1',
        sessionToken: 'refresh-token',
        refreshTokenHash: bcrypt.hashSync('refresh-token', 10),
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        revokedAt: null,
      };

      mockPrisma.user.findUnique = vi.fn().mockResolvedValue(mockUser);
      mockPrisma.userSession.findFirst = vi.fn().mockResolvedValue(mockSession);

      const result = await authService.verifyToken('refresh-token', 'refresh');

      expect(result).toHaveProperty('id', 'user-1');
      expect(result).toHaveProperty('email', 'test@example.com');
    });

    it('should throw error for invalid token', async () => {
      const invalidToken = 'invalid-token';

      await expect(authService.verifyToken(invalidToken))
        .rejects.toThrow('Invalid token');
    });

    it('should throw error for expired token', async () => {
      const expiredToken = jwt.sign(
        { id: 'user-1', email: 'test@example.com', role: 'USER', organizationId: 'org-1' },
        process.env.JWT_SECRET!,
        { expiresIn: '-1h' }
      );

      await expect(authService.verifyToken(expiredToken))
        .rejects.toThrow('Invalid token');
    });

    it('should throw error for non-existent user', async () => {
      const validToken = jwt.sign(
        { id: 'user-1', email: 'test@example.com', role: 'USER', organizationId: 'org-1' },
        process.env.JWT_SECRET!,
        { expiresIn: '15m' }
      );

      mockPrisma.user.findUnique = vi.fn().mockResolvedValue(null);

      await expect(authService.verifyToken(validToken))
        .rejects.toThrow('User not found');
    });

    it('should throw error for inactive user', async () => {
      const validToken = jwt.sign(
        { id: 'user-1', email: 'test@example.com', role: 'USER', organizationId: 'org-1' },
        process.env.JWT_SECRET!,
        { expiresIn: '15m' }
      );

      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        passwordHash: bcrypt.hashSync('password123', 10),
        role: 'USER',
        organizationId: 'org-1',
        status: 'INACTIVE',
      };

      mockPrisma.user.findUnique = vi.fn().mockResolvedValue(mockUser);

      await expect(authService.verifyToken(validToken))
        .rejects.toThrow('User account is inactive');
    });
  });

  describe('refreshToken', () => {
    it('should successfully refresh token', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        passwordHash: bcrypt.hashSync('password123', 10),
        role: 'USER',
        organizationId: 'org-1',
        status: 'ACTIVE',
      };

      const mockSession = {
        id: 'session-1',
        userId: 'user-1',
        sessionToken: 'refresh-token',
        refreshTokenHash: bcrypt.hashSync('refresh-token', 10),
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        revokedAt: null,
      };

      mockPrisma.user.findUnique = vi.fn().mockResolvedValue(mockUser);
      mockPrisma.userSession.findFirst = vi.fn().mockResolvedValue(mockSession);
      mockPrisma.userSession.create = vi.fn().mockResolvedValue({});

      const result = await authService.refreshToken('refresh-token');

      expect(result).toHaveProperty('user');
      expect(result).toHaveProperty('accessToken');
      expect(result).toHaveProperty('refreshToken');
      expect(result).toHaveProperty('expiresIn');
    });

    it('should throw error for invalid refresh token', async () => {
      mockPrisma.userSession.findFirst = vi.fn().mockResolvedValue(null);

      await expect(authService.refreshToken('invalid-refresh-token'))
        .rejects.toThrow('Invalid refresh token');
    });

    it('should throw error for expired refresh token', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        passwordHash: bcrypt.hashSync('password123', 10),
        role: 'USER',
        organizationId: 'org-1',
        status: 'ACTIVE',
      };

      const mockSession = {
        id: 'session-1',
        userId: 'user-1',
        sessionToken: 'refresh-token',
        refreshTokenHash: bcrypt.hashSync('refresh-token', 10),
        expiresAt: new Date(Date.now() - 1000),
        revokedAt: null,
      };

      mockPrisma.user.findUnique = vi.fn().mockResolvedValue(mockUser);
      mockPrisma.userSession.findFirst = vi.fn().mockResolvedValue(mockSession);

      await expect(authService.refreshToken('refresh-token'))
        .rejects.toThrow('Refresh token expired');
    });

    it('should throw error for revoked refresh token', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        passwordHash: bcrypt.hashSync('password123', 10),
        role: 'USER',
        organizationId: 'org-1',
        status: 'ACTIVE',
      };

      const mockSession = {
        id: 'session-1',
        userId: 'user-1',
        sessionToken: 'refresh-token',
        refreshTokenHash: bcrypt.hashSync('refresh-token', 10),
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        revokedAt: new Date(),
      };

      mockPrisma.user.findUnique = vi.fn().mockResolvedValue(mockUser);
      mockPrisma.userSession.findFirst = vi.fn().mockResolvedValue(mockSession);

      await expect(authService.refreshToken('refresh-token'))
        .rejects.toThrow('Refresh token revoked');
    });
  });

  describe('logout', () => {
    it('should successfully logout', async () => {
      const mockSession = {
        id: 'session-1',
        userId: 'user-1',
        sessionToken: 'refresh-token',
        refreshTokenHash: bcrypt.hashSync('refresh-token', 10),
        expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        revokedAt: null,
      };

      mockPrisma.userSession.findFirst = vi.fn().mockResolvedValue(mockSession);
      mockPrisma.userSession.update = vi.fn().mockResolvedValue({});

      await authService.logout('refresh-token');

      expect(mockPrisma.userSession.update).toHaveBeenCalledWith({
        where: { id: 'session-1' },
        data: { revokedAt: expect.any(Date) }
      });
    });

    it('should not throw error for non-existent session', async () => {
      mockPrisma.userSession.findFirst = vi.fn().mockResolvedValue(null);

      await authService.logout('non-existent-token');
    });
  });

  describe('cleanupExpiredSessions', () => {
    it('should clean up expired sessions', async () => {
      const expiredSessions = [
        { id: 'session-1', userId: 'user-1', expiresAt: new Date(Date.now() - 1000) },
        { id: 'session-2', userId: 'user-2', expiresAt: new Date(Date.now() - 2000) },
      ];

      mockPrisma.userSession.findMany = vi.fn().mockResolvedValue(expiredSessions);
      mockPrisma.userSession.deleteMany = vi.fn().mockResolvedValue({ count: 2 });

      const result = await authService.cleanupExpiredSessions();

      expect(result).toBe(2);
      expect(mockPrisma.userSession.deleteMany).toHaveBeenCalledWith({
        where: {
          id: {
            in: ['session-1', 'session-2']
          }
        }
      });
    });

    it('should return 0 if no expired sessions', async () => {
      mockPrisma.userSession.findMany = vi.fn().mockResolvedValue([]);

      const result = await authService.cleanupExpiredSessions();

      expect(result).toBe(0);
    });
  });
});
