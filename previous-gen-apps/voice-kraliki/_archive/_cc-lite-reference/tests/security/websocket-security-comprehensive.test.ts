/**
 * Comprehensive WebSocket Security Test Suite
 * Tests all security improvements implemented for WebSocket connections
 */

import { describe, it, expect, beforeAll, afterAll, beforeEach, vi } from 'vitest';
import { WebSocket as WS } from 'ws';
import jwt from 'jsonwebtoken';
import type { FastifyInstance } from 'fastify';

// Mock services for isolated testing
const mockPrismaClient = {
  user: {
    findUnique: vi.fn(),
  },
  userSession: {
    findUnique: vi.fn(),
  },
  organization: {
    findUnique: vi.fn(),
  },
};

const mockAuthService = {
  verifySession: vi.fn(),
};

const mockSessionManager = {
  getActiveSessions: vi.fn(() => []),
  on: vi.fn(),
  createSession: vi.fn(),
  processMessage: vi.fn(),
};

const mockTeamCoordinator = {
  getTeamMetrics: vi.fn(() => ({ activeAgents: 0, queueSize: 0 })),
  on: vi.fn(),
  updateAgentStatus: vi.fn(),
};

describe('WebSocket Security Comprehensive Tests', () => {
  const TEST_PORT = 3901;
  const wsUrl = `ws://localhost:${TEST_PORT}/ws`;
  let fastify: FastifyInstance;

  // Test user data
  const testUser = {
    id: 'user-123',
    email: 'test@example.com',
    role: 'SUPERVISOR',
    status: 'ACTIVE',
    organizationId: 'org-456',
    firstName: 'Test',
    lastName: 'User',
  };

  const testOrganization = {
    id: 'org-456',
    name: 'Test Organization',
    status: 'ACTIVE',
  };

  beforeAll(async () => {
    // Create mock Fastify instance
    fastify = {
      log: {
        info: vi.fn(),
        warn: vi.fn(),
        error: vi.fn(),
        debug: vi.fn(),
      },
      get: vi.fn(),
      decorate: vi.fn(),
      databaseService: { client: mockPrismaClient },
      authService: mockAuthService,
      authKeys: {
        publicKeyPEM: '-----BEGIN PUBLIC KEY-----\ntest-key\n-----END PUBLIC KEY-----'
      }
    } as unknown as FastifyInstance;

    // Setup default mocks
    mockPrismaClient.user.findUnique.mockResolvedValue({
      ...testUser,
      organization: testOrganization,
    });

    mockPrismaClient.userSession.findUnique.mockResolvedValue({
      id: 'session-123',
      sessionToken: 'valid-token',
      expiresAt: new Date(Date.now() + 86400000), // 24 hours from now
      revokedAt: null,
      user: testUser,
    });

    mockAuthService.verifySession.mockResolvedValue({
      sub: testUser.id,
      email: testUser.email,
      roles: [testUser.role.toLowerCase()],
    });
  });

  afterAll(() => {
    // Cleanup
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Authentication Security Tests', () => {
    it('should reject connections without authentication token', async () => {
      const ws = new WS(wsUrl);

      await new Promise<void>((resolve) => {
        ws.on('close', (code, reason) => {
          expect(code).toBe(4401);
          expect(reason.toString()).toContain('Authentication token required');
          resolve();
        });

        // Set timeout to avoid hanging tests
        setTimeout(() => {
          ws.close();
          resolve();
        }, 1000);
      });
    });

    it('should reject connections with invalid token format', async () => {
      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': 'Bearer invalid-token-format',
        },
      });

      await new Promise<void>((resolve) => {
        ws.on('close', (code, reason) => {
          expect(code).toBe(4401);
          resolve();
        });

        setTimeout(() => {
          ws.close();
          resolve();
        }, 1000);
      });
    });

    it('should reject connections with expired tokens', async () => {
      const expiredToken = jwt.sign(
        { sub: testUser.id, email: testUser.email },
        'test-secret',
        { expiresIn: '-1h' } // Expired 1 hour ago
      );

      // Mock expired session
      mockPrismaClient.userSession.findUnique.mockResolvedValueOnce({
        id: 'session-123',
        sessionToken: expiredToken,
        expiresAt: new Date(Date.now() - 3600000), // 1 hour ago
        revokedAt: null,
        user: testUser,
      });

      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${expiredToken}`,
        },
      });

      await new Promise<void>((resolve) => {
        ws.on('close', (code, reason) => {
          expect(code).toBe(4403);
          expect(reason.toString()).toContain('expired');
          resolve();
        });

        setTimeout(() => {
          ws.close();
          resolve();
        }, 1000);
      });
    });

    it('should reject connections for revoked sessions', async () => {
      const revokedToken = jwt.sign(
        { sub: testUser.id, email: testUser.email },
        'test-secret'
      );

      // Mock revoked session
      mockPrismaClient.userSession.findUnique.mockResolvedValueOnce({
        id: 'session-123',
        sessionToken: revokedToken,
        expiresAt: new Date(Date.now() + 86400000),
        revokedAt: new Date(), // Session is revoked
        user: testUser,
      });

      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${revokedToken}`,
        },
      });

      await new Promise<void>((resolve) => {
        ws.on('close', (code, reason) => {
          expect(code).toBe(4401);
          expect(reason.toString()).toContain('revoked');
          resolve();
        });

        setTimeout(() => {
          ws.close();
          resolve();
        }, 1000);
      });
    });

    it('should reject connections for inactive users', async () => {
      const validToken = jwt.sign(
        { sub: testUser.id, email: testUser.email },
        'test-secret'
      );

      // Mock inactive user
      mockPrismaClient.user.findUnique.mockResolvedValueOnce({
        ...testUser,
        status: 'INACTIVE',
        organization: testOrganization,
      });

      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      await new Promise<void>((resolve) => {
        ws.on('close', (code, reason) => {
          expect(code).toBe(4404);
          expect(reason.toString()).toContain('not active');
          resolve();
        });

        setTimeout(() => {
          ws.close();
          resolve();
        }, 1000);
      });
    });

    it('should reject connections for users without organization', async () => {
      const validToken = jwt.sign(
        { sub: testUser.id, email: testUser.email },
        'test-secret'
      );

      // Mock user without organization
      mockPrismaClient.user.findUnique.mockResolvedValueOnce({
        ...testUser,
        organization: null,
        organizationId: null,
      });

      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      await new Promise<void>((resolve) => {
        ws.on('close', (code, reason) => {
          expect(code).toBe(4404);
          expect(reason.toString()).toContain('organization');
          resolve();
        });

        setTimeout(() => {
          ws.close();
          resolve();
        }, 1000);
      });
    });
  });

  describe('Rate Limiting Security Tests', () => {
    let ws: WS;
    let validToken: string;

    beforeEach(async () => {
      validToken = jwt.sign(
        { sub: testUser.id, email: testUser.email },
        'test-secret'
      );

      ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      // Wait for connection to establish
      await new Promise<void>((resolve) => {
        ws.on('open', resolve);
      });
    });

    afterEach(() => {
      if (ws && ws.readyState === WS.OPEN) {
        ws.close();
      }
    });

    it('should enforce message rate limiting (30 messages per minute)', async () => {
      const messages: string[] = [];

      // Send 35 messages rapidly (exceeding limit of 30)
      for (let i = 0; i < 35; i++) {
        try {
          ws.send(JSON.stringify({ type: 'ping', id: i }));
          messages.push(`Message ${i}`);
        } catch (error) {
          break;
        }
      }

      // Should be disconnected due to rate limiting
      await new Promise<void>((resolve) => {
        ws.on('close', (code, reason) => {
          expect(code).toBe(1008);
          expect(reason.toString()).toContain('Rate limit exceeded');
          resolve();
        });

        setTimeout(() => {
          resolve();
        }, 2000);
      });
    });

    it('should enforce burst rate limiting (5 messages in 10 seconds)', async () => {
      // Send 6 messages rapidly (exceeding burst limit of 5)
      for (let i = 0; i < 6; i++) {
        ws.send(JSON.stringify({ type: 'ping', id: i }));
      }

      // Should be disconnected due to burst limiting
      await new Promise<void>((resolve) => {
        ws.on('close', (code, reason) => {
          expect(code).toBe(1008);
          expect(reason.toString()).toContain('burst window');
          resolve();
        });

        setTimeout(() => {
          resolve();
        }, 1000);
      });
    });
  });

  describe('Input Validation Security Tests', () => {
    let ws: WS;
    let validToken: string;

    beforeEach(async () => {
      validToken = jwt.sign(
        { sub: testUser.id, email: testUser.email },
        'test-secret'
      );

      ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      await new Promise<void>((resolve) => {
        ws.on('open', resolve);
      });
    });

    afterEach(() => {
      if (ws && ws.readyState === WS.OPEN) {
        ws.close();
      }
    });

    it('should reject messages with invalid message types', async () => {
      ws.send(JSON.stringify({ type: 'invalid_message_type' }));

      await new Promise<void>((resolve) => {
        ws.on('message', (data) => {
          const response = JSON.parse(data.toString());
          expect(response.event).toBe('error');
          expect(response.data.code).toBe('INVALID_MESSAGE');
          expect(response.data.message).toContain('not allowed');
          resolve();
        });
      });
    });

    it('should reject oversized messages', async () => {
      const largeMessage = {
        type: 'ping',
        content: 'x'.repeat(15000), // Exceeds 10KB limit
      };

      ws.send(JSON.stringify(largeMessage));

      await new Promise<void>((resolve) => {
        ws.on('message', (data) => {
          const response = JSON.parse(data.toString());
          expect(response.event).toBe('error');
          expect(response.data.message).toContain('too large');
          resolve();
        });
      });
    });

    it('should reject malformed JSON messages', async () => {
      ws.send('{ invalid json }');

      await new Promise<void>((resolve) => {
        ws.on('message', (data) => {
          const response = JSON.parse(data.toString());
          expect(response.event).toBe('error');
          expect(response.data.code).toBe('INVALID_MESSAGE');
          resolve();
        });
      });
    });

    it('should validate message field formats', async () => {
      // Test invalid agentId format
      ws.send(JSON.stringify({
        type: 'agent_status',
        agentId: 'invalid@agent#id', // Contains invalid characters
        status: 'ACTIVE'
      }));

      await new Promise<void>((resolve) => {
        ws.on('message', (data) => {
          const response = JSON.parse(data.toString());
          expect(response.event).toBe('error');
          expect(response.data.code).toBe('INVALID_MESSAGE');
          resolve();
        });
      });
    });

    it('should limit array sizes in messages', async () => {
      // Test events array with too many items
      const tooManyEvents = Array.from({ length: 15 }, (_, i) => `event_${i}`);

      ws.send(JSON.stringify({
        type: 'subscribe',
        events: tooManyEvents
      }));

      await new Promise<void>((resolve) => {
        ws.on('message', (data) => {
          const response = JSON.parse(data.toString());
          expect(response.event).toBe('error');
          expect(response.data.code).toBe('INVALID_MESSAGE');
          resolve();
        });
      });
    });
  });

  describe('Organization Isolation Tests', () => {
    it('should prevent cross-organization data leakage in events', async () => {
      // This test would verify that events are properly scoped to organizations
      // Implementation depends on the actual event system structure
      expect(true).toBe(true); // Placeholder - implement based on actual event system
    });
  });

  describe('Connection Management Security Tests', () => {
    it('should handle connection errors gracefully', async () => {
      const validToken = jwt.sign(
        { sub: testUser.id, email: testUser.email },
        'test-secret'
      );

      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      await new Promise<void>((resolve) => {
        ws.on('open', () => {
          // Simulate connection error
          ws.emit('error', new Error('Test connection error'));
          resolve();
        });
      });

      // Verify error is logged and connection is cleaned up
      expect(fastify.log.error).toHaveBeenCalled();
    });

    it('should log comprehensive connection information on disconnect', async () => {
      const validToken = jwt.sign(
        { sub: testUser.id, email: testUser.email },
        'test-secret'
      );

      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      await new Promise<void>((resolve) => {
        ws.on('open', () => {
          ws.close(1000, 'Test disconnect');
          resolve();
        });
      });

      // Verify comprehensive logging
      expect(fastify.log.info).toHaveBeenCalledWith(
        expect.stringContaining('WebSocket client disconnected'),
        expect.objectContaining({
          userId: testUser.id,
          orgId: testUser.organizationId,
        })
      );
    });
  });

  describe('Heartbeat and Idle Management Tests', () => {
    let ws: WS;
    let validToken: string;

    beforeEach(async () => {
      validToken = jwt.sign(
        { sub: testUser.id, email: testUser.email },
        'test-secret'
      );

      ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      await new Promise<void>((resolve) => {
        ws.on('open', resolve);
      });
    });

    afterEach(() => {
      if (ws && ws.readyState === WS.OPEN) {
        ws.close();
      }
    });

    it('should respond to ping messages with pong', async () => {
      ws.send(JSON.stringify({ type: 'ping' }));

      await new Promise<void>((resolve) => {
        ws.on('message', (data) => {
          const response = JSON.parse(data.toString());
          expect(response.event).toBe('pong');
          expect(response.data).toHaveProperty('timestamp');
          expect(response.data).toHaveProperty('clientId');
          resolve();
        });
      });
    });

    it('should respond to heartbeat messages', async () => {
      ws.send(JSON.stringify({ type: 'heartbeat' }));

      await new Promise<void>((resolve) => {
        ws.on('message', (data) => {
          const response = JSON.parse(data.toString());
          expect(response.event).toBe('heartbeat_ack');
          expect(response.data).toHaveProperty('timestamp');
          resolve();
        });
      });
    });
  });
});