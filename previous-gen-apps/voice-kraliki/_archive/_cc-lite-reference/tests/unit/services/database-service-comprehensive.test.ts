import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { DatabaseService } from '@server/database/database-service';
import { PrismaClient, UserRole, UserStatus } from '@prisma/client';
import bcrypt from 'bcrypt';

// Mock Prisma Client
const mockPrisma = {
  $connect: vi.fn(),
  $disconnect: vi.fn(),
  organization: {
    findFirst: vi.fn(),
    create: vi.fn(),
    findUnique: vi.fn()
  },
  user: {
    count: vi.fn(),
    create: vi.fn(),
    createMany: vi.fn(),
    findUnique: vi.fn(),
    update: vi.fn()
  }
};

vi.mock('@prisma/client', () => ({
  PrismaClient: vi.fn(() => mockPrisma),
  UserRole: {
    ADMIN: 'ADMIN',
    SUPERVISOR: 'SUPERVISOR',
    AGENT: 'AGENT'
  },
  UserStatus: {
    ACTIVE: 'ACTIVE',
    INACTIVE: 'INACTIVE'
  }
}));

// Mock bcrypt
vi.mock('bcrypt', () => ({
  hash: vi.fn().mockResolvedValue('hashed-password'),
  default: {
    hash: vi.fn().mockResolvedValue('hashed-password')
  }
}));

// Mock logger
vi.mock('@server/services/logger-service', () => ({
  systemLogger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn()
  }
}));

// Mock crypto
vi.mock('node:crypto', () => ({
  randomBytes: vi.fn().mockReturnValue(Buffer.from('random-bytes')),
  createHash: vi.fn().mockReturnValue({
    update: vi.fn().mockReturnThis(),
    digest: vi.fn().mockReturnValue('generated-id')
  })
}));

describe('DatabaseService', () => {
  let databaseService: DatabaseService;
  let originalEnv: any;

  beforeEach(() => {
    // Save original environment
    originalEnv = {
      NODE_ENV: process.env.NODE_ENV,
      ENABLE_DEMO_USERS: process.env.ENABLE_DEMO_USERS,
      SEED_DEMO_USERS: process.env.SEED_DEMO_USERS,
      DEFAULT_ADMIN_PASSWORD: process.env.DEFAULT_ADMIN_PASSWORD,
      DEFAULT_ORG_ID: process.env.DEFAULT_ORG_ID,
      ADMIN_EMAIL: process.env.ADMIN_EMAIL,
      ADMIN_PASSWORD: process.env.ADMIN_PASSWORD,
      TEST_PASSWORD: process.env.TEST_PASSWORD,
      NONEXISTENT_VAR: process.env.NONEXISTENT_VAR,
      EMPTY_PASSWORD: process.env.EMPTY_PASSWORD
    };

    vi.clearAllMocks();

    // Set up successful database connection by default
    mockPrisma.$connect.mockResolvedValue(undefined);
    mockPrisma.organization.findFirst.mockResolvedValue(null);
    mockPrisma.organization.create.mockResolvedValue({
      id: 'org-cc-light-default',
      name: 'CC-Light Default Organization',
      domain: 'cc-light.local',
      settings: {
        timezone: 'UTC',
        language: 'en',
        features: ['voice', 'chat', 'analytics']
      }
    });
    mockPrisma.user.count.mockResolvedValue(0);
    mockPrisma.user.create.mockResolvedValue({
      id: 'user-id',
      email: 'created@cc-light.local',
      role: UserRole.ADMIN
    });
    mockPrisma.user.createMany.mockResolvedValue({ count: 2 });

    databaseService = new DatabaseService();
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
    it('should initialize with PrismaClient', () => {
      expect(databaseService).toBeDefined();
      expect(databaseService.client).toBeDefined();
    });

    it('should configure logging based on environment', () => {
      process.env.NODE_ENV = 'development';
      const devService = new DatabaseService();
      expect(devService.client).toBeDefined();

      process.env.NODE_ENV = 'production';
      const prodService = new DatabaseService();
      expect(prodService.client).toBeDefined();
    });
  });

  describe('initialize', () => {
    it('should connect to database and set up defaults', async () => {
      mockPrisma.user.count.mockResolvedValue(0);

      await databaseService.initialize();

      expect(mockPrisma.$connect).toHaveBeenCalled();
      expect(mockPrisma.organization.findFirst).toHaveBeenCalledWith({
        where: { domain: 'cc-light.local' }
      });
    });

    it('should handle database connection failures gracefully', async () => {
      mockPrisma.$connect.mockRejectedValue(new Error('Connection failed'));

      // Should not throw - service should continue without database
      await expect(databaseService.initialize()).resolves.not.toThrow();
    });

    it('should skip setup if organization already exists', async () => {
      const existingOrg = {
        id: 'existing-org',
        name: 'Existing Organization',
        domain: 'cc-light.local'
      };
      mockPrisma.organization.findFirst.mockResolvedValue(existingOrg);

      await databaseService.initialize();

      expect(mockPrisma.organization.create).not.toHaveBeenCalled();
    });
  });

  describe('ensureDefaultOrganization', () => {
    it('should create default organization if none exists', async () => {
      mockPrisma.organization.findFirst.mockResolvedValue(null);

      await databaseService.initialize();

      expect(mockPrisma.organization.create).toHaveBeenCalledWith({
        data: {
          id: expect.any(String),
          name: 'CC-Light Default Organization',
          domain: 'cc-light.local',
          settings: {
            timezone: 'UTC',
            language: 'en',
            features: ['voice', 'chat', 'analytics']
          }
        }
      });
    });

    it('should return existing organization if found', async () => {
      const existingOrg = {
        id: 'existing-org',
        name: 'Existing Organization',
        domain: 'cc-light.local'
      };
      mockPrisma.organization.findFirst.mockResolvedValue(existingOrg);

      await databaseService.initialize();

      expect(mockPrisma.organization.create).not.toHaveBeenCalled();
    });
  });

  describe('ensureDefaultUsers - Development Environment', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'development';
      mockPrisma.organization.findFirst.mockResolvedValue({
        id: 'org-cc-light-default',
        name: 'Default Org',
        domain: 'cc-light.local'
      });
    });

    it('should not seed users when SEED_DEMO_USERS is false', async () => {
      process.env.SEED_DEMO_USERS = 'false';
      mockPrisma.user.count.mockResolvedValue(0);

      await databaseService.initialize();

      expect(mockPrisma.user.createMany).not.toHaveBeenCalled();
    });

    it('should not seed users when SEED_DEMO_USERS is not set', async () => {
      delete process.env.SEED_DEMO_USERS;
      mockPrisma.user.count.mockResolvedValue(0);

      await databaseService.initialize();

      expect(mockPrisma.user.createMany).not.toHaveBeenCalled();
    });

    it('should seed demo users when SEED_DEMO_USERS is true', async () => {
      process.env.SEED_DEMO_USERS = 'true';
      mockPrisma.user.count.mockResolvedValue(0);
      mockPrisma.user.createMany.mockResolvedValue({ count: 3 });

      await databaseService.initialize();

      expect(bcrypt.hash).toHaveBeenCalledTimes(3);

      const createCalls = mockPrisma.user.create.mock.calls.map(([args]) => args);
      expect(createCalls).toEqual(expect.arrayContaining([
        expect.objectContaining({
          data: expect.objectContaining({
            email: 'admin@cc-light.local',
            role: UserRole.ADMIN
          })
        }),
        expect.objectContaining({
          data: expect.objectContaining({
            email: 'supervisor@cc-light.local',
            role: UserRole.SUPERVISOR
          })
        })
      ]));

      expect(mockPrisma.user.createMany).toHaveBeenCalledTimes(1);
      const createManyArgs = mockPrisma.user.createMany.mock.calls[0]?.[0];
      expect(createManyArgs?.data).toEqual(expect.arrayContaining([
        expect.objectContaining({
          email: 'agent1@cc-light.local',
          role: UserRole.AGENT
        }),
        expect.objectContaining({
          email: 'agent2@cc-light.local',
          role: UserRole.AGENT
        })
      ]));
    });

    it('should skip seeding if users already exist', async () => {
      process.env.SEED_DEMO_USERS = 'true';
      mockPrisma.user.count.mockResolvedValue(5);

      await databaseService.initialize();

      expect(mockPrisma.user.createMany).not.toHaveBeenCalled();
    });

    it('should use environment variable passwords when provided', async () => {
      process.env.SEED_DEMO_USERS = 'true';
      process.env.DEFAULT_ADMIN_PASSWORD = 'custom-admin-password';
      process.env.DEFAULT_SUPERVISOR_PASSWORD = 'custom-supervisor-password';
      process.env.DEFAULT_AGENT_PASSWORD = 'custom-agent-password';
      mockPrisma.user.count.mockResolvedValue(0);
      mockPrisma.user.createMany.mockResolvedValue({ count: 3 });

      await databaseService.initialize();

      expect(bcrypt.hash).toHaveBeenCalledWith('custom-admin-password', 12);
      expect(bcrypt.hash).toHaveBeenCalledWith('custom-supervisor-password', 12);
      expect(bcrypt.hash).toHaveBeenCalledWith('custom-agent-password', 12);
    });

    it('should generate random passwords when env vars not set', async () => {
      process.env.SEED_DEMO_USERS = 'true';
      delete process.env.DEFAULT_ADMIN_PASSWORD;
      delete process.env.DEFAULT_SUPERVISOR_PASSWORD;
      delete process.env.DEFAULT_AGENT_PASSWORD;
      mockPrisma.user.count.mockResolvedValue(0);
      mockPrisma.user.createMany.mockResolvedValue({ count: 3 });

      await databaseService.initialize();

      // Should have generated random passwords
      expect(bcrypt.hash).toHaveBeenCalledWith(expect.any(String), 12);
    });

    it('should handle organization not found error', async () => {
      process.env.SEED_DEMO_USERS = 'true';
      mockPrisma.organization.findFirst.mockResolvedValue(null);
      mockPrisma.organization.create.mockRejectedValue(new Error('Failed to create org'));

      await expect(databaseService.initialize()).rejects.toThrow();
    });
  });

  describe('ensureDefaultUsers - Production Environment', () => {
    beforeEach(() => {
      process.env.NODE_ENV = 'production';
      mockPrisma.organization.findFirst.mockResolvedValue({
        id: 'org-cc-light-default',
        name: 'Default Org',
        domain: 'cc-light.local'
      });
    });

    it('should create production admin from environment variables', async () => {
      process.env.ADMIN_EMAIL = 'admin@company.com';
      process.env.ADMIN_PASSWORD = 'secure-admin-password';
      mockPrisma.user.findUnique.mockResolvedValue(null);
      mockPrisma.user.create.mockResolvedValue({
        id: 'admin-id',
        email: 'admin@company.com',
        role: UserRole.ADMIN
      });

      await databaseService.initialize();

      expect(mockPrisma.user.findUnique).toHaveBeenCalledWith({
        where: { email: 'admin@company.com' }
      });
      expect(bcrypt.hash).toHaveBeenCalledWith('secure-admin-password', 12);
      expect(mockPrisma.user.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          email: 'admin@company.com',
          role: UserRole.ADMIN,
          status: UserStatus.ACTIVE
        })
      });
    });

    it('should skip admin creation if admin already exists', async () => {
      process.env.ADMIN_EMAIL = 'admin@company.com';
      process.env.ADMIN_PASSWORD = 'secure-admin-password';
      mockPrisma.user.findUnique.mockResolvedValue({
        id: 'existing-admin',
        email: 'admin@company.com',
        role: UserRole.ADMIN
      });

      await databaseService.initialize();

      expect(mockPrisma.user.create).not.toHaveBeenCalled();
    });

    it('should throw error if production admin credentials missing', async () => {
      delete process.env.ADMIN_EMAIL;
      delete process.env.ADMIN_PASSWORD;

      await expect(databaseService.initialize()).rejects.toThrow(
        'ADMIN_EMAIL and ADMIN_PASSWORD environment variables are required in production'
      );
    });

    it('should never seed demo users in production', async () => {
      process.env.SEED_DEMO_USERS = 'true';
      process.env.ADMIN_EMAIL = 'admin@company.com';
      process.env.ADMIN_PASSWORD = 'secure-password';
      mockPrisma.user.findUnique.mockResolvedValue(null);
      mockPrisma.user.create.mockResolvedValue({
        id: 'admin-id',
        email: 'admin@company.com',
        role: UserRole.ADMIN
      });

      await databaseService.initialize();

      // Should only create one admin user, not demo users
      expect(mockPrisma.user.create).toHaveBeenCalledTimes(1);
      expect(mockPrisma.user.createMany).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should handle bcrypt errors gracefully', async () => {
      process.env.NODE_ENV = 'development';
      process.env.SEED_DEMO_USERS = 'true';
      mockPrisma.user.count.mockResolvedValue(0);
      (bcrypt.hash as any).mockRejectedValue(new Error('Bcrypt error'));

      await expect(databaseService.initialize()).rejects.toThrow('Bcrypt error');
    });

    it('should handle database errors during user creation', async () => {
      process.env.NODE_ENV = 'development';
      process.env.SEED_DEMO_USERS = 'true';
      mockPrisma.user.count.mockResolvedValue(0);
      mockPrisma.user.createMany.mockRejectedValue(new Error('Database error'));

      await expect(databaseService.initialize()).rejects.toThrow('Database error');
    });

    it('should handle organization creation errors', async () => {
      mockPrisma.organization.findFirst.mockResolvedValue(null);
      mockPrisma.organization.create.mockRejectedValue(new Error('Org creation failed'));

      await expect(databaseService.initialize()).rejects.toThrow('Org creation failed');
    });
  });

  describe('Password Generation', () => {
    it('should generate secure random passwords when env vars not set', async () => {
      process.env.NODE_ENV = 'development';
      process.env.SEED_DEMO_USERS = 'true';
      delete process.env.DEFAULT_ADMIN_PASSWORD;

      const service = new DatabaseService();

      // Access private method for testing
      const password = (service as any).resolveSeedPassword('NONEXISTENT_VAR', 'default');

      expect(password).toMatch(/^[A-Za-z0-9_-]{16,}$/); // Base64url pattern
    });

    it('should use environment variable when provided', async () => {
      process.env.TEST_PASSWORD = 'custom-password';

      const service = new DatabaseService();
      const password = (service as any).resolveSeedPassword('TEST_PASSWORD', 'default');

      expect(password).toBe('custom-password');
    });

    it('should use fallback when env var is empty', async () => {
      process.env.EMPTY_PASSWORD = '';

      const service = new DatabaseService();
      const password = (service as any).resolveSeedPassword('EMPTY_PASSWORD', 'fallback');

      expect(password).toMatch(/^[A-Za-z0-9_-]{16,}$/); // Should generate random password
    });
  });

  describe('Database Client Access', () => {
    it('should provide access to Prisma client', () => {
      const client = databaseService.client;
      expect(client).toBeDefined();
      expect(client).toBe(mockPrisma);
    });
  });

  describe('Security Compliance', () => {
    it('should use secure password hashing in production', async () => {
      process.env.NODE_ENV = 'production';
      process.env.ADMIN_EMAIL = 'admin@company.com';
      process.env.ADMIN_PASSWORD = 'secure-password';
      mockPrisma.user.findUnique.mockResolvedValue(null);
      mockPrisma.user.create.mockResolvedValue({ id: 'admin-id' });

      await databaseService.initialize();

      expect(bcrypt.hash).toHaveBeenCalledWith('secure-password', 12);
    });

    it('should not log sensitive information', async () => {
      const { systemLogger } = await import('@server/services/logger-service');

      process.env.NODE_ENV = 'development';
      process.env.SEED_DEMO_USERS = 'true';
      process.env.DEFAULT_ADMIN_PASSWORD = 'secret-password';
      mockPrisma.user.count.mockResolvedValue(0);
      mockPrisma.user.createMany.mockResolvedValue({ count: 3 });

      await databaseService.initialize();

      // Check that logger calls don't contain sensitive data
      const logCalls = (systemLogger.info as any).mock.calls;
      logCalls.forEach((call: any[]) => {
        const logMessage = JSON.stringify(call);
        expect(logMessage).not.toContain('secret-password');
        expect(logMessage).not.toContain('hashed-password');
      });
    });

    it('should enforce production security restrictions', async () => {
      process.env.NODE_ENV = 'production';
      process.env.SEED_DEMO_USERS = 'true'; // This should be ignored in production

      await expect(databaseService.initialize()).rejects.toThrow(
        'ADMIN_EMAIL and ADMIN_PASSWORD environment variables are required in production'
      );
    });
  });
});
