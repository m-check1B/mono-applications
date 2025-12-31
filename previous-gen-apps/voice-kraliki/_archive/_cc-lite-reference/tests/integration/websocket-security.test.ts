/**
 * WebSocket Security Tests for Voice by Kraliki
 * Tests rate limiting, organization isolation, and authentication flow
 */
import { test, expect } from '@playwright/test';
import WebSocket from 'ws';
import { createWebSocketServer } from '../utils/test-helpers';

describe('WebSocket Security Tests', () => {
  let testPort: number;
  let baseUrl: string;

  beforeAll(async () => {
    testPort = 3901;
    baseUrl = `ws://127.0.0.1:${testPort}`;
  });

  afterAll(async () => {
    // Cleanup test server
    await new Promise(resolve => setTimeout(resolve, 100));
  });

  describe('Rate Limiting Validation', () => {
    test('should enforce rate limits on WebSocket connections', async () => {
      const maxConnections = 5;
      const connections: WebSocket[] = [];
      const connectPromises: Promise<any>[] = [];

      // Attempt to create more connections than allowed
      for (let i = 0; i < maxConnections + 2; i++) {
        const ws = new WebSocket(`${baseUrl}/ws`);
        connections.push(ws);

        connectPromises.push(
          new Promise((resolve) => {
            ws.on('open', () => resolve({ success: true, index: i }));
            ws.on('error', (error) => resolve({ success: false, error, index: i }));
          })
        );
      }

      const results = await Promise.all(connectPromises);
      const successfulConnections = results.filter(r => r.success).length;
      const failedConnections = results.filter(r => !r.success).length;

      expect(successfulConnections).toBeLessThanOrEqual(maxConnections);
      expect(failedConnections).toBeGreaterThan(0);

      // Cleanup connections
      connections.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      });
    });

    test('should rate limit message frequency per connection', async () => {
      const ws = new WebSocket(`${baseUrl}/ws`);
      const responses: any[] = [];

      await new Promise(resolve => {
        ws.on('open', resolve);
      });

      // Send messages rapidly to trigger rate limiting
      const messageCount = 50;
      for (let i = 0; i < messageCount; i++) {
        ws.send(JSON.stringify({
          type: 'test_message',
          data: `Message ${i}`,
          timestamp: Date.now()
        }));
      }

      // Listen for rate limit responses
      ws.on('message', (data) => {
        const message = JSON.parse(data.toString());
        responses.push(message);
      });

      await new Promise(resolve => setTimeout(resolve, 1000));

      // Should receive rate limit warnings
      const rateLimitWarnings = responses.filter(r =>
        r.type === 'rate_limit_warning' || r.type === 'rate_limit_exceeded'
      );

      expect(rateLimitWarnings.length).toBeGreaterThan(0);
      ws.close();
    });
  });

  describe('Organization Isolation Tests', () => {
    test('should isolate WebSocket messages between organizations', async () => {
      const org1Token = 'org1_test_token';
      const org2Token = 'org2_test_token';

      const ws1 = new WebSocket(`${baseUrl}/ws`, {
        headers: { 'Authorization': `Bearer ${org1Token}` }
      });

      const ws2 = new WebSocket(`${baseUrl}/ws`, {
        headers: { 'Authorization': `Bearer ${org2Token}` }
      });

      const org1Messages: any[] = [];
      const org2Messages: any[] = [];

      await Promise.all([
        new Promise(resolve => ws1.on('open', resolve)),
        new Promise(resolve => ws2.on('open', resolve))
      ]);

      ws1.on('message', (data) => {
        const message = JSON.parse(data.toString());
        org1Messages.push(message);
      });

      ws2.on('message', (data) => {
        const message = JSON.parse(data.toString());
        org2Messages.push(message);
      });

      // Send organization-specific messages
      ws1.send(JSON.stringify({
        type: 'org_broadcast',
        orgId: 'org1',
        data: 'Org 1 sensitive data'
      }));

      ws2.send(JSON.stringify({
        type: 'org_broadcast',
        orgId: 'org2',
        data: 'Org 2 sensitive data'
      }));

      await new Promise(resolve => setTimeout(resolve, 500));

      // Verify isolation - org1 should not receive org2 messages
      const org1SensitiveMessages = org1Messages.filter(m =>
        m.data && m.data.includes('Org 2 sensitive')
      );
      const org2SensitiveMessages = org2Messages.filter(m =>
        m.data && m.data.includes('Org 1 sensitive')
      );

      expect(org1SensitiveMessages.length).toBe(0);
      expect(org2SensitiveMessages.length).toBe(0);

      ws1.close();
      ws2.close();
    });

    test('should prevent unauthorized organization access', async () => {
      const invalidToken = 'invalid_org_token';
      let connectionRejected = false;

      const ws = new WebSocket(`${baseUrl}/ws`, {
        headers: { 'Authorization': `Bearer ${invalidToken}` }
      });

      ws.on('error', (error) => {
        connectionRejected = true;
        expect(error.message).toContain('401');
      });

      ws.on('close', (code) => {
        if (code === 401 || code === 403) {
          connectionRejected = true;
        }
      });

      await new Promise(resolve => setTimeout(resolve, 1000));
      expect(connectionRejected).toBe(true);
    });
  });

  describe('Authentication Flow Tests', () => {
    test('should authenticate valid JWT tokens', async () => {
      const validToken = generateTestToken('user123', 'org456');
      let authSuccess = false;

      const ws = new WebSocket(`${baseUrl}/ws`, {
        headers: { 'Authorization': `Bearer ${validToken}` }
      });

      ws.on('open', () => {
        authSuccess = true;
      });

      await new Promise(resolve => {
        ws.on('open', resolve);
        ws.on('error', resolve);
      });

      expect(authSuccess).toBe(true);
      ws.close();
    });

    test('should reject expired tokens', async () => {
      const expiredToken = generateExpiredTestToken();
      let authFailed = false;

      const ws = new WebSocket(`${baseUrl}/ws`, {
        headers: { 'Authorization': `Bearer ${expiredToken}` }
      });

      ws.on('error', () => {
        authFailed = true;
      });

      ws.on('close', (code) => {
        if (code === 401) {
          authFailed = true;
        }
      });

      await new Promise(resolve => setTimeout(resolve, 1000));
      expect(authFailed).toBe(true);
    });

    test('should handle token refresh gracefully', async () => {
      const initialToken = generateTestToken('user123', 'org456');
      const refreshedToken = generateTestToken('user123', 'org456', Date.now() + 3600000);

      const ws = new WebSocket(`${baseUrl}/ws`, {
        headers: { 'Authorization': `Bearer ${initialToken}` }
      });

      await new Promise(resolve => ws.on('open', resolve));

      // Simulate token refresh
      ws.send(JSON.stringify({
        type: 'refresh_token',
        token: refreshedToken
      }));

      let refreshResponse: any = null;
      ws.on('message', (data) => {
        const message = JSON.parse(data.toString());
        if (message.type === 'token_refreshed') {
          refreshResponse = message;
        }
      });

      await new Promise(resolve => setTimeout(resolve, 500));

      expect(refreshResponse).not.toBeNull();
      expect(refreshResponse.success).toBe(true);
      ws.close();
    });
  });

  describe('Security Headers and CORS', () => {
    test('should enforce proper CORS policies', async () => {
      const response = await fetch(`http://127.0.0.1:${testPort}/ws`, {
        method: 'OPTIONS',
        headers: {
          'Origin': 'http://malicious-site.com',
          'Access-Control-Request-Method': 'GET'
        }
      });

      expect(response.headers.get('Access-Control-Allow-Origin')).not.toBe('*');
    });

    test('should include security headers', async () => {
      const response = await fetch(`http://127.0.0.1:${testPort}/health`);

      expect(response.headers.get('X-Content-Type-Options')).toBe('nosniff');
      expect(response.headers.get('X-Frame-Options')).toBe('DENY');
      expect(response.headers.get('X-XSS-Protection')).toBe('1; mode=block');
    });
  });

  describe('Message Validation and Sanitization', () => {
    test('should sanitize WebSocket messages', async () => {
      const validToken = generateTestToken('user123', 'org456');
      const ws = new WebSocket(`${baseUrl}/ws`, {
        headers: { 'Authorization': `Bearer ${validToken}` }
      });

      await new Promise(resolve => ws.on('open', resolve));

      const maliciousPayloads = [
        '<script>alert("xss")</script>',
        '${7*7}',
        '../../../etc/passwd',
        'DROP TABLE users;',
        '\x00\x01\x02'
      ];

      const responses: any[] = [];
      ws.on('message', (data) => {
        responses.push(JSON.parse(data.toString()));
      });

      // Send malicious payloads
      for (const payload of maliciousPayloads) {
        ws.send(JSON.stringify({
          type: 'test_message',
          data: payload
        }));
      }

      await new Promise(resolve => setTimeout(resolve, 1000));

      // Check that responses are sanitized
      const sanitizedResponses = responses.filter(r =>
        r.type === 'sanitization_warning' ||
        r.type === 'message_blocked'
      );

      expect(sanitizedResponses.length).toBeGreaterThan(0);
      ws.close();
    });
  });
});

// Helper functions
function generateTestToken(userId: string, orgId: string, exp?: number): string {
  // Mock JWT token generation for testing
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64');
  const payload = Buffer.from(JSON.stringify({
    userId,
    orgId,
    exp: exp || Math.floor(Date.now() / 1000) + 3600,
    iat: Math.floor(Date.now() / 1000)
  })).toString('base64');
  const signature = 'mock_signature';

  return `${header}.${payload}.${signature}`;
}

function generateExpiredTestToken(): string {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64');
  const payload = Buffer.from(JSON.stringify({
    userId: 'user123',
    orgId: 'org456',
    exp: Math.floor(Date.now() / 1000) - 3600, // Expired 1 hour ago
    iat: Math.floor(Date.now() / 1000) - 7200
  })).toString('base64');
  const signature = 'mock_signature';

  return `${header}.${payload}.${signature}`;
}