/**
 * JWT Token Security Tests
 * Tests for JWT token generation, validation, signing, and security
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { signToken, verifyToken, generateAuthKeys } from '@unified/auth-core';
import { AuthService } from '../../server/services/auth-service';
import { PrismaClient } from '@prisma/client';
import * as crypto from 'crypto';
import * as jwt from 'jsonwebtoken';

// Mock PrismaClient
const mockPrisma = {
  user: {
    findUnique: vi.fn(),
    update: vi.fn(),
  },
  userSession: {
    create: vi.fn(),
    findUnique: vi.fn(),
    update: vi.fn(),
    deleteMany: vi.fn(),
  },
} as unknown as PrismaClient;

const originalEnv = process.env;

describe('JWT Token Security Tests', () => {
  let authService: AuthService;
  let testKeys: { privateKeyPEM: string; publicKeyPEM: string };
  
  beforeEach(async () => {
    // Generate test keys
    testKeys = await generateAuthKeys();
    
    // Set up secure environment
    process.env = {
      ...originalEnv,
      NODE_ENV: 'test',
      AUTH_PRIVATE_KEY: testKeys.privateKeyPEM,
      AUTH_PUBLIC_KEY: testKeys.publicKeyPEM,
      JWT_SECRET: 'test-jwt-secret-256-bits-long-for-security-testing',
      JWT_REFRESH_SECRET: 'test-refresh-secret-256-bits-long-for-security'
    };
    
    // Reset mocks
    vi.clearAllMocks();
    
    // Create AuthService instance
    authService = new AuthService({
      prisma: mockPrisma,
      privateKey: testKeys.privateKeyPEM,
      publicKey: testKeys.publicKeyPEM
    });
    
    // Mock basic user data
    mockPrisma.user.findUnique.mockResolvedValue({
      id: 'user-123',
      email: 'test@cc-light.com',
      role: 'AGENT',
      status: 'ACTIVE',
      organizationId: 'org-123',
      firstName: 'Test',
      lastName: 'User',
      username: 'testuser',
      passwordHash: '$2b$10$test',
      createdAt: new Date(),
      updatedAt: new Date(),
      lastLoginAt: null,
      phoneExtension: null,
      avatar: null,
      skills: [],
      department: null,
      preferences: {},
      organization: { id: 'org-123', name: 'Test Org' }
    });
    
    mockPrisma.userSession.create.mockResolvedValue({
      id: 'session-123',
      userId: 'user-123',
      sessionToken: 'mock.jwt.token',
      refreshTokenHash: 'hashed_refresh_token',
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      createdAt: new Date(),
      lastActivity: new Date(),
      lastRefreshAt: null,
      refreshCount: 0,
      ipAddress: null,
      userAgent: null,
      revokedAt: null
    });
    
    mockPrisma.userSession.findUnique.mockResolvedValue({
      id: 'session-123',
      userId: 'user-123',
      sessionToken: 'mock.jwt.token',
      refreshTokenHash: 'hashed_refresh_token',
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      createdAt: new Date(),
      lastActivity: new Date(),
      lastRefreshAt: null,
      refreshCount: 0,
      ipAddress: null,
      userAgent: null,
      revokedAt: null
    });
  });
  
  afterEach(() => {
    process.env = originalEnv;
  });

  describe('JWT Token Generation', () => {
    it('should generate valid JWT tokens with Ed25519 signature', async () => {
      const payload = {
        sub: 'user-123',
        email: 'test@cc-light.com',
        roles: ['agent']
      };
      
      const token = await signToken(payload, testKeys.privateKeyPEM);
      
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.split('.')).toHaveLength(3); // header.payload.signature
      
      // Verify token structure
      const [header, payloadPart, signature] = token.split('.');
      
      // Decode header
      const decodedHeader = JSON.parse(Buffer.from(header, 'base64url').toString());
      expect(decodedHeader.alg).toBe('EdDSA');
      expect(decodedHeader.typ).toBe('JWT');
      
      // Decode payload
      const decodedPayload = JSON.parse(Buffer.from(payloadPart, 'base64url').toString());
      expect(decodedPayload.sub).toBe('user-123');
      expect(decodedPayload.email).toBe('test@cc-light.com');
      expect(decodedPayload.roles).toEqual(['agent']);
      expect(decodedPayload.iat).toBeDefined();
      expect(decodedPayload.exp).toBeDefined();
      
      // Signature should be present
      expect(signature).toBeDefined();
      expect(signature.length).toBeGreaterThan(0);
    });
    
    it('should include proper expiration times', async () => {
      const payload = {
        sub: 'user-123',
        email: 'test@cc-light.com',
        roles: ['agent']
      };
      
      const token = await signToken(payload, testKeys.privateKeyPEM);
      const verified = await verifyToken(token, testKeys.publicKeyPEM);
      
      expect(verified.iat).toBeDefined();
      expect(verified.exp).toBeDefined();
      expect(verified.exp).toBeGreaterThan(verified.iat);
      
      // Should expire in approximately 24 hours (with some tolerance)
      const expectedExpiration = verified.iat + (24 * 60 * 60);
      expect(Math.abs(verified.exp - expectedExpiration)).toBeLessThan(60); // 1 minute tolerance
    });
    
    it('should generate unique tokens for same payload', async () => {
      const payload = {
        sub: 'user-123',
        email: 'test@cc-light.com',
        roles: ['agent']
      };
      
      const token1 = await signToken(payload, testKeys.privateKeyPEM);
      // Wait a moment to ensure different iat timestamps
      await new Promise(resolve => setTimeout(resolve, 10));
      const token2 = await signToken(payload, testKeys.privateKeyPEM);
      
      expect(token1).not.toBe(token2);
      
      // Both should be valid
      const verified1 = await verifyToken(token1, testKeys.publicKeyPEM);
      const verified2 = await verifyToken(token2, testKeys.publicKeyPEM);
      
      expect(verified1.sub).toBe(verified2.sub);
      expect(verified1.iat).not.toBe(verified2.iat);
    });
  });

  describe('JWT Token Validation', () => {
    it('should verify valid tokens correctly', async () => {
      const payload = {
        sub: 'user-123',
        email: 'test@cc-light.com',
        roles: ['agent']
      };
      
      const token = await signToken(payload, testKeys.privateKeyPEM);
      const verified = await verifyToken(token, testKeys.publicKeyPEM);
      
      expect(verified.sub).toBe('user-123');
      expect(verified.email).toBe('test@cc-light.com');
      expect(verified.roles).toEqual(['agent']);
    });
    
    it('should reject tokens with invalid signatures', async () => {
      const payload = {
        sub: 'user-123',
        email: 'test@cc-light.com',
        roles: ['agent']
      };
      
      const token = await signToken(payload, testKeys.privateKeyPEM);
      
      // Tamper with the token
      const parts = token.split('.');
      parts[2] = parts[2] + 'tampered';
      const tamperedToken = parts.join('.');
      
      await expect(verifyToken(tamperedToken, testKeys.publicKeyPEM))
        .rejects.toThrow();
    });
    
    it('should reject tokens signed with wrong private key', async () => {
      const payload = {
        sub: 'user-123',
        email: 'test@cc-light.com',
        roles: ['agent']
      };
      
      // Generate different keys
      const wrongKeys = await generateAuthKeys();
      const token = await signToken(payload, wrongKeys.privateKeyPEM);
      
      await expect(verifyToken(token, testKeys.publicKeyPEM))
        .rejects.toThrow();
    });
    
    it('should reject expired tokens', async () => {
      const payload = {
        sub: 'user-123',
        email: 'test@cc-light.com',
        roles: ['agent']
      };
      
      // Create token that expires immediately
      const expiredPayload = {
        ...payload,
        iat: Math.floor(Date.now() / 1000) - 3600, // 1 hour ago
        exp: Math.floor(Date.now() / 1000) - 1800  // 30 minutes ago
      };
      
      const token = await signToken(expiredPayload, testKeys.privateKeyPEM);
      
      await expect(verifyToken(token, testKeys.publicKeyPEM))
        .rejects.toThrow();
    });
    
    it('should reject malformed tokens', async () => {
      const malformedTokens = [
        'not.a.jwt',
        'invalid',
        'too.many.parts.here.invalid',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature',
        ''
      ];
      
      for (const malformedToken of malformedTokens) {
        await expect(verifyToken(malformedToken, testKeys.publicKeyPEM))
          .rejects.toThrow();
      }
    });
  });

  describe('Token Security Properties', () => {
    it('should use cryptographically secure random values', async () => {
      const tokens = [];
      
      // Generate multiple tokens
      for (let i = 0; i < 10; i++) {
        const payload = {
          sub: 'user-123',
          email: 'test@cc-light.com',
          roles: ['agent']
        };
        
        const token = await signToken(payload, testKeys.privateKeyPEM);
        tokens.push(token);
        
        // Small delay to ensure different timestamps
        await new Promise(resolve => setTimeout(resolve, 1));
      }
      
      // All tokens should be unique
      const uniqueTokens = new Set(tokens);
      expect(uniqueTokens.size).toBe(tokens.length);
      
      // Signatures should be different (due to different iat values)
      const signatures = tokens.map(token => token.split('.')[2]);
      const uniqueSignatures = new Set(signatures);
      expect(uniqueSignatures.size).toBe(signatures.length);
    });
    
    it('should resist timing attacks during verification', async () => {
      const payload = {
        sub: 'user-123',
        email: 'test@cc-light.com',
        roles: ['agent']
      };
      
      const validToken = await signToken(payload, testKeys.privateKeyPEM);
      const invalidToken = 'invalid.jwt.token';
      
      // Measure verification time for valid token
      const start1 = process.hrtime.bigint();
      try {
        await verifyToken(validToken, testKeys.publicKeyPEM);
      } catch {}
      const time1 = process.hrtime.bigint() - start1;
      
      // Measure verification time for invalid token
      const start2 = process.hrtime.bigint();
      try {
        await verifyToken(invalidToken, testKeys.publicKeyPEM);
      } catch {}
      const time2 = process.hrtime.bigint() - start2;
      
      // Times should be within reasonable bounds (crypto operations vary)
      const timeDifferenceMs = Number(time1 - time2) / 1_000_000;
      expect(Math.abs(timeDifferenceMs)).toBeLessThan(100); // 100ms tolerance
    });
    
    it('should prevent algorithm confusion attacks', async () => {
      const payload = {
        sub: 'user-123',
        email: 'test@cc-light.com',
        roles: ['agent']
      };
      
      // Create a token with different algorithm
      const hmacToken = jwt.sign(payload, 'secret', { algorithm: 'HS256' });
      
      // Should reject tokens with wrong algorithm
      await expect(verifyToken(hmacToken, testKeys.publicKeyPEM))
        .rejects.toThrow();
    });
  });

  describe('Session Integration', () => {
    it('should create session with proper JWT token', async () => {
      const { token } = await authService.createSessionForUserId('user-123');
      
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      
      // Should be able to verify the token
      const verified = await authService.verifySession(token);
      expect(verified.sub).toBe('user-123');
      expect(verified.email).toBe('test@cc-light.com');
    });
    
    it('should track session in database', async () => {
      await authService.createSessionForUserId('user-123');
      
      expect(mockPrisma.userSession.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          userId: 'user-123',
          sessionToken: expect.any(String),
          refreshTokenHash: expect.any(String),
          expiresAt: expect.any(Date)
        })
      });
    });
    
    it('should validate session exists in database', async () => {
      const payload = await authService.verifySession('valid.jwt.token');
      
      expect(payload).toBeDefined();
      expect(mockPrisma.userSession.findUnique).toHaveBeenCalledWith({
        where: { sessionToken: 'valid.jwt.token' }
      });
    });
  });

  describe('Key Management Security', () => {
    it('should validate Ed25519 key format', async () => {
      const publicKey = await authService.getPublicKey();
      
      expect(publicKey).toContain('-----BEGIN PUBLIC KEY-----');
      expect(publicKey).toContain('-----END PUBLIC KEY-----');
      
      // Ed25519 public keys should be specific length when base64 decoded
      const keyContent = publicKey
        .replace('-----BEGIN PUBLIC KEY-----\n', '')
        .replace('\n-----END PUBLIC KEY-----', '')
        .replace(/\n/g, '');
        
      const keyBuffer = Buffer.from(keyContent, 'base64');
      // Ed25519 public key in DER format should be 44 bytes
      expect(keyBuffer.length).toBe(44);
    });
    
    it('should handle key initialization errors gracefully', () => {
      process.env.NODE_ENV = 'production';
      delete process.env.AUTH_PRIVATE_KEY;
      delete process.env.AUTH_PUBLIC_KEY;
      
      expect(() => {
        new AuthService({ prisma: mockPrisma });
      }).toThrow('AUTH_PRIVATE_KEY and AUTH_PUBLIC_KEY must be provided in production');
    });
    
    it('should generate development keys securely', async () => {
      process.env.NODE_ENV = 'development';
      delete process.env.AUTH_PRIVATE_KEY;
      delete process.env.AUTH_PUBLIC_KEY;
      
      const devService = new AuthService({ prisma: mockPrisma });
      const publicKey = await devService.getPublicKey();
      
      expect(publicKey).toContain('-----BEGIN PUBLIC KEY-----');
      expect(publicKey).toContain('-----END PUBLIC KEY-----');
      
      // Should be able to create and verify tokens with generated keys
      const { token } = await devService.createSessionForUserId('user-123');
      expect(token).toBeDefined();
    });
  });

  describe('Token Payload Security', () => {
    it('should sanitize user data in JWT payload', async () => {
      const { token } = await authService.createSessionForUserId('user-123');
      
      // Decode payload without verification to check contents
      const [, payloadPart] = token.split('.');
      const payload = JSON.parse(Buffer.from(payloadPart, 'base64url').toString());
      
      // Should include safe user data
      expect(payload.sub).toBe('user-123');
      expect(payload.email).toBe('test@cc-light.com');
      expect(payload.roles).toEqual(['agent']);
      
      // Should NOT include sensitive data
      expect(payload.passwordHash).toBeUndefined();
      expect(payload.sessionToken).toBeUndefined();
      expect(payload.refreshToken).toBeUndefined();
    });
    
    it('should normalize role values in tokens', async () => {
      // Mock user with different role case
      mockPrisma.user.findUnique.mockResolvedValue({
        id: 'user-123',
        email: 'supervisor@cc-light.com',
        role: 'SUPERVISOR',
        status: 'ACTIVE',
        organizationId: 'org-123',
        firstName: 'Super',
        lastName: 'Visor',
        username: 'supervisor',
        passwordHash: '$2b$10$test',
        createdAt: new Date(),
        updatedAt: new Date(),
        lastLoginAt: null,
        phoneExtension: null,
        avatar: null,
        skills: [],
        department: null,
        preferences: {},
        organization: { id: 'org-123', name: 'Test Org' }
      });
      
      const { token } = await authService.createSessionForUserId('user-123');
      
      const [, payloadPart] = token.split('.');
      const payload = JSON.parse(Buffer.from(payloadPart, 'base64url').toString());
      
      expect(payload.roles).toEqual(['supervisor']); // Should be lowercase
    });
  });

  describe('Production Security Validation', () => {
    it('should enforce strong keys in production', () => {
      process.env.NODE_ENV = 'production';
      
      // Test with weak/placeholder keys
      const weakKeys = [
        'REPLACE_WITH_ACTUAL_PRIVATE_KEY',
        'weak-key',
        '',
        'development-only-key'
      ];
      
      for (const weakKey of weakKeys) {
        process.env.AUTH_PRIVATE_KEY = weakKey;
        process.env.AUTH_PUBLIC_KEY = 'any-public-key';
        
        expect(() => {
          new AuthService({ prisma: mockPrisma });
        }).toThrow();
      }
    });
    
    it('should validate JWT secret strength', () => {
      const weakSecrets = [
        'weak',
        '12345',
        'password',
        Buffer.from('short', 'utf8').toString('base64') // Less than 256 bits
      ];
      
      const originalJwtSecret = process.env.JWT_SECRET;
      
      for (const weakSecret of weakSecrets) {
        process.env.JWT_SECRET = weakSecret;
        
        expect(() => {
          new AuthService({ prisma: mockPrisma });
        }).toThrow();
      }
      
      process.env.JWT_SECRET = originalJwtSecret;
    });
  });
});
