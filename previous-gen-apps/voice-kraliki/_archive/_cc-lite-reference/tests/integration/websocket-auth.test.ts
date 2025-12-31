import { FastifyInstance } from 'fastify';
import { vi, describe, it, beforeAll, afterAll, beforeEach, expect } from 'vitest';
import { AuthService } from '../../server/auth/auth-service';
import { AIAgentManager } from '../../server/services/ai-agent-manager';
import { WebSocket as WS } from 'ws';
import jwt from 'jsonwebtoken';

// Mock services
const mockAuthService = {
  verifyToken: vi.fn(),
} as unknown as AuthService;

const mockAgentManager = {
  getState: vi.fn(),
  on: vi.fn(),
} as unknown as AIAgentManager;

const maybeDescribe = process.env.SKIP_DB_TEST_SETUP === 'true' ? describe.skip : describe;

maybeDescribe('WebSocket Authentication Integration', () => {
  let fastify: FastifyInstance;
  let server: any;
  let wsUrl: string;

  beforeAll(async () => {
    // Create a mock Fastify instance
    fastify = {
      log: {
        info: vi.fn(),
        error: vi.fn(),
        warn: vi.fn(),
      },
      decorate: vi.fn(),
      get: vi.fn(),
    } as unknown as FastifyInstance;

    // Mock the database service
    (fastify as any).databaseService = {
      client: {
        user: {
          findUnique: jest.fn(),
        },
      },
    };

    // Set up WebSocket server
    wsUrl = 'ws://localhost:3900/api/ws/supervisor';
  });

  afterAll(() => {
    if (server) {
      server.close();
    }
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Authentication', () => {
    it('should allow connection with valid JWT token', async () => {
      const validToken = jwt.sign(
        { id: 'user-1', email: 'supervisor@example.com', role: 'SUPERVISOR', organizationId: 'org-1' },
        'test-jwt-secret',
        { expiresIn: '15m' }
      );

      mockAuthService.verifyToken.mockResolvedValue({
        id: 'user-1',
        email: 'supervisor@example.com',
        role: 'SUPERVISOR',
        organizationId: 'org-1',
      });

      (fastify as any).databaseService.client.user.findUnique.mockResolvedValue({
        id: 'user-1',
        status: 'ACTIVE',
      });

      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      await new Promise<void>((resolve, reject) => {
        ws.on('open', () => {
          expect(ws.readyState).toBe(WS.OPEN);
          ws.close();
          resolve();
        });

        ws.on('error', reject);

        setTimeout(() => {
          ws.close();
          reject(new Error('Connection timeout'));
        }, 5000);
      });
    });

    it('should allow connection with valid session cookie', async () => {
      const validToken = jwt.sign(
        { id: 'user-1', email: 'supervisor@example.com', role: 'SUPERVISOR', organizationId: 'org-1' },
        'test-jwt-secret',
        { expiresIn: '15m' }
      );

      mockAuthService.verifyToken.mockResolvedValue({
        id: 'user-1',
        email: 'supervisor@example.com',
        role: 'SUPERVISOR',
        organizationId: 'org-1',
      });

      (fastify as any).databaseService.client.user.findUnique.mockResolvedValue({
        id: 'user-1',
        status: 'ACTIVE',
      });

      const ws = new WS(wsUrl, {
        headers: {
          'Cookie': `cc_light_session=${validToken}`,
        },
      });

      await new Promise<void>((resolve, reject) => {
        ws.on('open', () => {
          expect(ws.readyState).toBe(WS.OPEN);
          ws.close();
          resolve();
        });

        ws.on('error', reject);

        setTimeout(() => {
          ws.close();
          reject(new Error('Connection timeout'));
        }, 5000);
      });
    });

    it('should reject connection without authentication', async () => {
      const ws = new WS(wsUrl);

      await new Promise<void>((resolve, reject) => {
        ws.on('open', () => {
          // This shouldn't happen
          ws.close();
          reject(new Error('Connection should have been rejected'));
        });

        ws.on('close', (code, reason) => {
          expect(code).toBe(1008); // Policy Violation
          expect(reason.toString()).toContain('Authentication failed');
          resolve();
        });

        ws.on('error', reject);

        setTimeout(() => {
          ws.close();
          resolve();
        }, 1000);
      });
    });

    it('should reject connection with invalid token', async () => {
      const invalidToken = 'invalid-token';

      mockAuthService.verifyToken.mockRejectedValue(new Error('Invalid token'));

      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${invalidToken}`,
        },
      });

      await new Promise<void>((resolve, reject) => {
        ws.on('open', () => {
          // This shouldn't happen
          ws.close();
          reject(new Error('Connection should have been rejected'));
        });

        ws.on('close', (code, reason) => {
          expect(code).toBe(1008); // Policy Violation
          resolve();
        });

        ws.on('error', reject);

        setTimeout(() => {
          ws.close();
          resolve();
        }, 1000);
      });
    });

    it('should reject connection for non-supervisor role', async () => {
      const validToken = jwt.sign(
        { id: 'user-1', email: 'user@example.com', role: 'USER', organizationId: 'org-1' },
        'test-jwt-secret',
        { expiresIn: '15m' }
      );

      mockAuthService.verifyToken.mockResolvedValue({
        id: 'user-1',
        email: 'user@example.com',
        role: 'USER',
        organizationId: 'org-1',
      });

      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      await new Promise<void>((resolve, reject) => {
        ws.on('open', () => {
          // This shouldn't happen
          ws.close();
          reject(new Error('Connection should have been rejected'));
        });

        ws.on('close', (code, reason) => {
          expect(code).toBe(1008); // Policy Violation
          resolve();
        });

        ws.on('error', reject);

        setTimeout(() => {
          ws.close();
          resolve();
        }, 1000);
      });
    });

    it('should reject connection for inactive user', async () => {
      const validToken = jwt.sign(
        { id: 'user-1', email: 'supervisor@example.com', role: 'SUPERVISOR', organizationId: 'org-1' },
        'test-jwt-secret',
        { expiresIn: '15m' }
      );

      mockAuthService.verifyToken.mockResolvedValue({
        id: 'user-1',
        email: 'supervisor@example.com',
        role: 'SUPERVISOR',
        organizationId: 'org-1',
      });

      (fastify as any).databaseService.client.user.findUnique.mockResolvedValue(null);

      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      await new Promise<void>((resolve, reject) => {
        ws.on('open', () => {
          // This shouldn't happen
          ws.close();
          reject(new Error('Connection should have been rejected'));
        });

        ws.on('close', (code, reason) => {
          expect(code).toBe(1008); // Policy Violation
          resolve();
        });

        ws.on('error', reject);

        setTimeout(() => {
          ws.close();
          resolve();
        }, 1000);
      });
    });
  });

  describe('Message Handling', () => {
    let ws: WS;
    let validToken: string;

    beforeEach(async () => {
      validToken = jwt.sign(
        { id: 'user-1', email: 'supervisor@example.com', role: 'SUPERVISOR', organizationId: 'org-1' },
        'test-jwt-secret',
        { expiresIn: '15m' }
      );

      mockAuthService.verifyToken.mockResolvedValue({
        id: 'user-1',
        email: 'supervisor@example.com',
        role: 'SUPERVISOR',
        organizationId: 'org-1',
      });

      (fastify as any).databaseService.client.user.findUnique.mockResolvedValue({
        id: 'user-1',
        status: 'ACTIVE',
      });

      mockAgentManager.getState.mockReturnValue({
        activeAgents: {},
        totalCapacity: 5,
        health: 'healthy',
      });

      ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      await new Promise<void>((resolve, reject) => {
        ws.on('open', resolve);
        ws.on('error', reject);
      });
    });

    afterEach(() => {
      if (ws && ws.readyState === WS.OPEN) {
        ws.close();
      }
    });

    it('should handle intervention message', async () => {
      const message = {
        type: 'intervention',
        agentId: 'agent-1',
        action: 'assist',
      };

      mockAgentManager.handleIntervention = jest.fn().mockResolvedValue({
        success: true,
        message: 'Intervention successful',
      });

      ws.send(JSON.stringify(message));

      await new Promise<void>((resolve, reject) => {
        ws.on('message', (data) => {
          const response = JSON.parse(data.toString());
          expect(response.type).toBe('intervention_result');
          expect(response.success).toBe(true);
          resolve();
        });

        setTimeout(() => {
          reject(new Error('No response received'));
        }, 5000);
      });
    });

    it('should handle emergency stop message', async () => {
      const message = {
        type: 'emergency_stop',
      };

      mockAgentManager.emergencyStop = jest.fn();

      ws.send(JSON.stringify(message));

      await new Promise<void>((resolve, reject) => {
        ws.on('message', (data) => {
          const response = JSON.parse(data.toString());
          expect(response.type).toBe('emergency_stop_activated');
          resolve();
        });

        setTimeout(() => {
          reject(new Error('No response received'));
        }, 5000);
      });
    });

    it('should handle ping message', async () => {
      const message = {
        type: 'ping',
      };

      ws.send(JSON.stringify(message));

      await new Promise<void>((resolve, reject) => {
        ws.on('message', (data) => {
          const response = JSON.parse(data.toString());
          expect(response.type).toBe('pong');
          resolve();
        });

        setTimeout(() => {
          reject(new Error('No response received'));
        }, 5000);
      });
    });

    it('should reject unknown message type', async () => {
      const message = {
        type: 'unknown_type',
      };

      ws.send(JSON.stringify(message));

      await new Promise<void>((resolve, reject) => {
        ws.on('message', (data) => {
          const response = JSON.parse(data.toString());
          expect(response.type).toBe('error');
          expect(response.data.code).toBe('VAL_001');
          resolve();
        });

        setTimeout(() => {
          reject(new Error('No response received'));
        }, 5000);
      });
    });

    it('should reject malformed message', async () => {
      const malformedMessage = 'not a json object';

      ws.send(malformedMessage);

      await new Promise<void>((resolve, reject) => {
        ws.on('message', (data) => {
          const response = JSON.parse(data.toString());
          expect(response.type).toBe('error');
          expect(response.data.code).toBe('VAL_001');
          resolve();
        });

        setTimeout(() => {
          reject(new Error('No response received'));
        }, 5000);
      });
    });
  });

  describe('Connection Management', () => {
    it('should handle connection close gracefully', async () => {
      const validToken = jwt.sign(
        { id: 'user-1', email: 'supervisor@example.com', role: 'SUPERVISOR', organizationId: 'org-1' },
        'test-jwt-secret',
        { expiresIn: '15m' }
      );

      mockAuthService.verifyToken.mockResolvedValue({
        id: 'user-1',
        email: 'supervisor@example.com',
        role: 'SUPERVISOR',
        organizationId: 'org-1',
      });

      (fastify as any).databaseService.client.user.findUnique.mockResolvedValue({
        id: 'user-1',
        status: 'ACTIVE',
      });

      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      await new Promise<void>((resolve, reject) => {
        ws.on('open', () => {
          ws.close();
          resolve();
        });

        ws.on('error', reject);
      });

      expect(fastify.log.info).toHaveBeenCalledWith(
        expect.stringContaining('disconnected')
      );
    });

    it('should handle connection errors gracefully', async () => {
      const validToken = jwt.sign(
        { id: 'user-1', email: 'supervisor@example.com', role: 'SUPERVISOR', organizationId: 'org-1' },
        'test-jwt-secret',
        { expiresIn: '15m' }
      );

      mockAuthService.verifyToken.mockResolvedValue({
        id: 'user-1',
        email: 'supervisor@example.com',
        role: 'SUPERVISOR',
        organizationId: 'org-1',
      });

      (fastify as any).databaseService.client.user.findUnique.mockResolvedValue({
        id: 'user-1',
        status: 'ACTIVE',
      });

      const ws = new WS(wsUrl, {
        headers: {
          'Authorization': `Bearer ${validToken}`,
        },
      });

      await new Promise<void>((resolve, reject) => {
        ws.on('open', () => {
          // Simulate an error
          ws.emit('error', new Error('Connection error'));
          resolve();
        });

        ws.on('error', () => {
          // This is expected
          resolve();
        });
      });

      expect(fastify.log.error).toHaveBeenCalledWith(
        expect.stringContaining('Failed to handle WebSocket error')
      );
    });
  });
});
