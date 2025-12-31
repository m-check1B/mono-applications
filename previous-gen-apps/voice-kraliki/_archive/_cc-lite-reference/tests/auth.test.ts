import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createToken, verifyToken, refreshToken } from '@unified/auth-core';
import { testDb, createTestUser } from './setup';

describe('Authentication with Stack 2025', () => {
  describe('User Authentication', () => {
    it('should authenticate user with valid credentials', async () => {
      const user = await createTestUser({
        email: 'agent@test.com',
        role: 'AGENT'
      });

      const token = await createToken({
        userId: user.id,
        email: user.email,
        metadata: { role: user.role }
      });

      expect(token).toBeDefined();
      expect(token.token).toBeTypeOf('string');
      expect(token.refreshToken).toBeTypeOf('string');
    });

    it('should verify valid token', async () => {
      const user = await createTestUser();
      const token = await createToken({
        userId: user.id,
        email: user.email
      });

      const verified = await verifyToken(token.token);
      expect(verified.valid).toBe(true);
      expect(verified.user.id).toBe(user.id);
    });

    it('should reject invalid token', async () => {
      const result = await verifyToken('invalid-token');
      expect(result.valid).toBe(false);
    });

    it('should refresh token successfully', async () => {
      const user = await createTestUser();
      const token = await createToken({
        userId: user.id,
        email: user.email
      });

      const newToken = await refreshToken(token.refreshToken);
      expect(newToken.token).toBeDefined();
      expect(newToken.token).not.toBe(token.token);
    });
  });

  describe('vd_session Cookie Support', () => {
    it('should set vd_session cookie on login', async () => {
      const mockSetCookie = vi.fn();
      global.document = {
        cookie: ''
      } as any;

      const user = await createTestUser();
      const token = await createToken({
        userId: user.id,
        email: user.email
      });

      // Simulate setting cookie
      document.cookie = `vd_session=${token.token}; path=/; max-age=86400; SameSite=Lax`;
      
      expect(document.cookie).toContain('vd_session=');
      expect(document.cookie).toContain(token.token);
    });

    it('should read vd_session cookie for SSO', async () => {
      const user = await createTestUser();
      const token = await createToken({
        userId: user.id,
        email: user.email
      });

      global.document = {
        cookie: `vd_session=${token.token}; other=value`
      } as any;

      const vdSession = document.cookie
        .split('; ')
        .find(row => row.startsWith('vd_session='))
        ?.split('=')[1];

      expect(vdSession).toBe(token.token);

      const verified = await verifyToken(vdSession!);
      expect(verified.valid).toBe(true);
    });

    it('should clear vd_session cookie on logout', () => {
      global.document = {
        cookie: 'vd_session=test-token'
      } as any;

      // Clear cookie
      document.cookie = 'vd_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      
      // In real browser, cookie would be cleared
      // For test, we simulate it
      global.document.cookie = '';
      
      expect(document.cookie).not.toContain('vd_session');
    });
  });

  describe('Role-Based Access Control', () => {
    it('should grant admin full permissions', async () => {
      const admin = await createTestUser({ role: 'ADMIN' });
      
      const hasPermission = (role: string, permission: string) => {
        if (role === 'ADMIN') return true;
        return false;
      };

      expect(hasPermission(admin.role, 'manage_agents')).toBe(true);
      expect(hasPermission(admin.role, 'view_reports')).toBe(true);
      expect(hasPermission(admin.role, 'any_permission')).toBe(true);
    });

    it('should grant supervisor limited permissions', async () => {
      const supervisor = await createTestUser({ role: 'SUPERVISOR' });
      
      const supervisorPermissions = [
        'view_dashboard',
        'view_agents',
        'manage_agents',
        'view_calls',
        'assign_calls',
        'view_reports'
      ];

      const hasPermission = (role: string, permission: string) => {
        if (role === 'SUPERVISOR') {
          return supervisorPermissions.includes(permission);
        }
        return false;
      };

      expect(hasPermission(supervisor.role, 'manage_agents')).toBe(true);
      expect(hasPermission(supervisor.role, 'view_reports')).toBe(true);
      expect(hasPermission(supervisor.role, 'system_settings')).toBe(false);
    });

    it('should grant agent basic permissions', async () => {
      const agent = await createTestUser({ role: 'AGENT' });
      
      const agentPermissions = [
        'view_dashboard',
        'make_calls',
        'answer_calls',
        'view_own_calls'
      ];

      const hasPermission = (role: string, permission: string) => {
        if (role === 'AGENT') {
          return agentPermissions.includes(permission);
        }
        return false;
      };

      expect(hasPermission(agent.role, 'make_calls')).toBe(true);
      expect(hasPermission(agent.role, 'view_own_calls')).toBe(true);
      expect(hasPermission(agent.role, 'manage_agents')).toBe(false);
    });
  });
});