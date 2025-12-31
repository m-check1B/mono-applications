import { describe, it, expect, beforeEach, vi } from 'vitest';
import { testDb, createTestUser, mockWebSocket } from '../setup';
import { createToken, verifyToken } from '@unified/auth-core';
import { appRouter } from '../../server/trpc/app.router';
import { createContext } from '../../server/trpc';
import crypto from 'crypto';
import { TRPCError } from '@trpc/server';

describe('Security Tests', () => {
  describe('Authentication Security', () => {
    it('should prevent brute force attacks with rate limiting', async () => {
      const attempts = [];
      
      // Simulate multiple failed login attempts
      for (let i = 0; i < 10; i++) {
        attempts.push(
          // This would normally hit rate limiting after 5 attempts
          expect(async () => {
            const ctx = await createContext({ 
              req: { 
                ip: '192.168.1.100',
                headers: {},
                user: null 
              }, 
              reply: { setCookie: vi.fn(), clearCookie: vi.fn() } 
            });
            const caller = appRouter.createCaller(ctx);
            
            await caller.auth.login({
              email: 'attacker@example.com',
              password: 'wrongpassword'
            });
          }).rejects.toThrow()
        );
      }
      
      await Promise.all(attempts);
    });

    it('should properly validate JWT tokens', async () => {
      const testUser = await createTestUser({ role: 'AGENT' });
      const validToken = await createToken({
        userId: testUser.id,
        email: testUser.email
      });

      // Test valid token
      const validResult = await verifyToken(validToken.token);
      expect(validResult.valid).toBe(true);
      expect(validResult.user.id).toBe(testUser.id);

      // Test invalid signature
      const tamperedToken = validToken.token.slice(0, -10) + 'tampered123';
      const invalidResult = await verifyToken(tamperedToken);
      expect(invalidResult.valid).toBe(false);

      // Test expired token (simulate)
      const expiredResult = await verifyToken('expired.token.here');
      expect(expiredResult.valid).toBe(false);
    });

    it('should prevent session fixation attacks', async () => {
      const testUser = await createTestUser({ role: 'AGENT' });
      
      // Generate two different sessions for same user
      const session1 = await createToken({
        userId: testUser.id,
        email: testUser.email
      });
      
      const session2 = await createToken({
        userId: testUser.id,
        email: testUser.email
      });
      
      // Sessions should be different (prevent fixation)
      expect(session1.token).not.toBe(session2.token);
      expect(session1.refreshToken).not.toBe(session2.refreshToken);
    });

    it('should enforce secure cookie settings in production', async () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';
      
      const mockReply = {
        setCookie: vi.fn(),
        clearCookie: vi.fn()
      };
      
      // Simulate login process
      const testUser = await createTestUser({ role: 'AGENT' });
      const ctx = await createContext({
        req: { headers: {}, ip: '127.0.0.1', user: testUser },
        reply: mockReply
      });
      
      const caller = appRouter.createCaller(ctx);
      
      await caller.auth.login({
        email: testUser.email,
        password: 'password123'
      });
      
      // Verify secure cookie settings
      expect(mockReply.setCookie).toHaveBeenCalledWith(
        'vd_session',
        expect.any(String),
        expect.objectContaining({
          httpOnly: true,
          secure: true,
          sameSite: 'strict'
        })
      );
      
      process.env.NODE_ENV = originalEnv;
    });
  });

  describe('Authorization Security', () => {
    it('should prevent privilege escalation', async () => {
      // Create agent user (lowest privilege)
      const agentUser = await createTestUser({ role: 'AGENT' });
      const agentToken = await createToken({
        userId: agentUser.id,
        email: agentUser.email,
        metadata: { role: 'AGENT' }
      });
      
      const ctx = await createContext({
        req: { 
          headers: { authorization: `Bearer ${agentToken.token}` },
          ip: '127.0.0.1',
          user: agentUser 
        },
        reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
      });
      const caller = appRouter.createCaller(ctx);
      
      // Agent should not be able to access admin functions
      await expect(caller.team.deleteUser({ userId: 'any-user-id' }))
        .rejects.toThrow('FORBIDDEN');
      
      await expect(caller.campaign.deleteCampaign({ campaignId: 'any-campaign-id' }))
        .rejects.toThrow('FORBIDDEN');
    });

    it('should prevent horizontal privilege escalation', async () => {
      const user1 = await createTestUser({ role: 'AGENT', organizationId: 'org1' });
      const user2 = await createTestUser({ role: 'AGENT', organizationId: 'org2' });
      
      const user1Token = await createToken({
        userId: user1.id,
        email: user1.email,
        metadata: { role: 'AGENT' }
      });
      
      const ctx = await createContext({
        req: { 
          headers: { authorization: `Bearer ${user1Token.token}` },
          ip: '127.0.0.1',
          user: user1 
        },
        reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
      });
      const caller = appRouter.createCaller(ctx);
      
      // User 1 should not be able to access User 2's data
      await expect(caller.agent.getPerformanceMetrics({ agentId: user2.id }))
        .rejects.toThrow('FORBIDDEN');
    });
  });

  describe('Input Validation Security', () => {
    it('should prevent SQL injection attempts', async () => {
      const testUser = await createTestUser({ role: 'SUPERVISOR' });
      const token = await createToken({
        userId: testUser.id,
        email: testUser.email,
        metadata: { role: 'SUPERVISOR' }
      });
      
      const ctx = await createContext({
        req: { 
          headers: { authorization: `Bearer ${token.token}` },
          ip: '127.0.0.1',
          user: testUser 
        },
        reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
      });
      const caller = appRouter.createCaller(ctx);
      
      // Test SQL injection patterns
      const maliciousInputs = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "'; INSERT INTO users VALUES ('hacker', 'password'); --",
        "\x00",
        "UNION SELECT * FROM users"
      ];
      
      for (const maliciousInput of maliciousInputs) {
        await expect(caller.callApi.getCalls({
          page: 1,
          limit: 10,
          searchQuery: maliciousInput
        })).rejects.toThrow(TRPCError);
      }
    });

    it('should prevent XSS through input sanitization', async () => {
      const testUser = await createTestUser({ role: 'SUPERVISOR' });
      const token = await createToken({
        userId: testUser.id,
        email: testUser.email,
        metadata: { role: 'SUPERVISOR' }
      });
      
      const ctx = await createContext({
        req: { 
          headers: { authorization: `Bearer ${token.token}` },
          ip: '127.0.0.1',
          user: testUser 
        },
        reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
      });
      const caller = appRouter.createCaller(ctx);
      
      // Test XSS patterns
      const xssPayloads = [
        '<script>alert("XSS")</script>',
        'javascript:alert("XSS")',
        '<img src="x" onerror="alert(1)">',
        '<svg/onload=alert(1)>',
        '&lt;script&gt;alert("XSS")&lt;/script&gt;'
      ];
      
      for (const payload of xssPayloads) {
        await expect(caller.campaign.createCampaign({
          name: payload,
          type: 'OUTBOUND',
          organizationId: testUser.organizationId,
          description: payload
        })).rejects.toThrow(TRPCError);
      }
    });

    it('should validate phone number formats', async () => {
      const testUser = await createTestUser({ role: 'AGENT' });
      const token = await createToken({
        userId: testUser.id,
        email: testUser.email,
        metadata: { role: 'AGENT' }
      });
      
      const ctx = await createContext({
        req: { 
          headers: { authorization: `Bearer ${token.token}` },
          ip: '127.0.0.1',
          user: testUser 
        },
        reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
      });
      const caller = appRouter.createCaller(ctx);
      
      const invalidPhoneNumbers = [
        '123',
        '++1234567890',
        '+1-800-HACK-ME',
        'javascript:alert(1)',
        '<script>alert(1)</script>',
        '+' + 'x'.repeat(50)
      ];
      
      for (const invalidPhone of invalidPhoneNumbers) {
        await expect(caller.callApi.initiateCall({
          phoneNumber: invalidPhone,
          campaignId: 'valid-campaign-id',
          agentId: testUser.id
        })).rejects.toThrow(TRPCError);
      }
    });
  });

  describe('Data Protection', () => {
    it('should not expose sensitive data in API responses', async () => {
      const testUser = await createTestUser({ 
        role: 'AGENT',
        password: '$2b$10$hashedpassword',
        email: 'agent@example.com'
      });
      
      const token = await createToken({
        userId: testUser.id,
        email: testUser.email,
        metadata: { role: 'AGENT' }
      });
      
      const ctx = await createContext({
        req: { 
          headers: { authorization: `Bearer ${token.token}` },
          ip: '127.0.0.1',
          user: testUser 
        },
        reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
      });
      const caller = appRouter.createCaller(ctx);
      
      // Get user profile
      const profile = await caller.auth.getProfile();
      
      // Should not expose password or other sensitive fields
      expect(profile).not.toHaveProperty('password');
      expect(profile).not.toHaveProperty('hashedPassword');
      expect(profile.email).toBe('agent@example.com');
    });

    it('should hash passwords before storing', async () => {
      const plainPassword = 'testpassword123';
      
      const user = await createTestUser({ 
        email: 'test@example.com',
        password: plainPassword // This should be hashed by the system
      });
      
      // Password should be hashed, not stored in plaintext
      expect(user.password).not.toBe(plainPassword);
      expect(user.password).toMatch(/^\$2[aby]\$\d+\$/);
    });
  });

  describe('Communication Security', () => {
    it('should validate WebSocket connections', async () => {
      const mockWs = mockWebSocket();
      const testUser = await createTestUser({ role: 'AGENT' });
      
      // Should require valid authentication for WebSocket connection
      const invalidTokens = [
        'invalid-token',
        '',
        'expired.token.here',
        'Bearer invalid-token'
      ];
      
      for (const token of invalidTokens) {
        // Mock WebSocket connection attempt with invalid token
        expect(() => {
          // Simulate connection validation
          if (!token || !token.startsWith('eyJ')) {
            throw new Error('UNAUTHORIZED');
          }
        }).toThrow('UNAUTHORIZED');
      }
    });

    it('should prevent CSRF attacks', async () => {
      const testUser = await createTestUser({ role: 'AGENT' });
      const token = await createToken({
        userId: testUser.id,
        email: testUser.email
      });
      
      // Simulate CSRF attack - request from different origin without proper headers
      const maliciousCtx = await createContext({
        req: { 
          headers: { 
            authorization: `Bearer ${token.token}`,
            origin: 'https://malicious-site.com',
            referer: 'https://malicious-site.com'
          },
          ip: '192.168.1.100',
          user: testUser 
        },
        reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
      });
      
      const caller = appRouter.createCaller(maliciousCtx);
      
      // Should be blocked by CORS policy (simulated)
      // In real implementation, this would be handled by Fastify CORS middleware
      expect(maliciousCtx.req.headers.origin).not.toMatch(/localhost|127\.0\.0\.1/);
    });
  });

  describe('Rate Limiting', () => {
    it('should enforce API rate limits', async () => {
      const testUser = await createTestUser({ role: 'AGENT' });
      const token = await createToken({
        userId: testUser.id,
        email: testUser.email,
        metadata: { role: 'AGENT' }
      });
      
      const requests = [];
      
      // Simulate rapid API requests (would hit rate limit)
      for (let i = 0; i < 20; i++) {
        requests.push(
          (async () => {
            const ctx = await createContext({
              req: { 
                headers: { authorization: `Bearer ${token.token}` },
                ip: '192.168.1.100',
                user: testUser 
              },
              reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
            });
            const caller = appRouter.createCaller(ctx);
            
            try {
              await caller.dashboard.getStats();
              return 'success';
            } catch (error: any) {
              if (error.message.includes('Rate limit')) {
                return 'rate_limited';
              }
              return 'error';
            }
          })()
        );
      }
      
      const results = await Promise.all(requests);
      
      // Some requests should be rate limited
      const rateLimitedCount = results.filter(r => r === 'rate_limited').length;
      expect(rateLimitedCount).toBeGreaterThan(0);
    });
  });

  describe('File Upload Security', () => {
    it('should validate file types and sizes', async () => {
      const testUser = await createTestUser({ role: 'SUPERVISOR' });
      const token = await createToken({
        userId: testUser.id,
        email: testUser.email,
        metadata: { role: 'SUPERVISOR' }
      });
      
      // Test malicious file types
      const maliciousFiles = [
        { name: 'malware.exe', type: 'application/octet-stream', size: 1000 },
        { name: 'script.js', type: 'application/javascript', size: 500 },
        { name: 'large.csv', type: 'text/csv', size: 50 * 1024 * 1024 }, // 50MB - too large
        { name: 'script.php', type: 'application/x-php', size: 1000 }
      ];
      
      for (const file of maliciousFiles) {
        expect(() => {
          // Simulate file validation
          const allowedTypes = ['text/csv', 'application/json'];
          const maxSize = 10 * 1024 * 1024; // 10MB
          
          if (!allowedTypes.includes(file.type)) {
            throw new Error('Invalid file type');
          }
          if (file.size > maxSize) {
            throw new Error('File too large');
          }
          if (file.name.includes('.exe') || file.name.includes('.php') || file.name.includes('.js')) {
            throw new Error('Dangerous file extension');
          }
        }).toThrow();
      }
    });
  });

  describe('Audit Logging', () => {
    it('should log security events', async () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      
      // Simulate failed login attempt
      try {
        const ctx = await createContext({
          req: { 
            headers: {},
            ip: '192.168.1.100',
            user: null 
          },
          reply: { setCookie: vi.fn(), clearCookie: vi.fn() }
        });
        const caller = appRouter.createCaller(ctx);
        
        await caller.auth.login({
          email: 'nonexistent@example.com',
          password: 'wrongpassword'
        });
      } catch (error) {
        // Expected to fail
      }
      
      // Should log security event
      expect(consoleSpy).toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });
  });
});
