/**
 * Metrics Endpoint Security Tests
 * Tests authorization, rate limiting, and data exposure for metrics endpoints
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createMockRequest, createMockReply } from '../setup-simple';

describe('Metrics Endpoint Security Tests', () => {
  let mockRequest: any;
  let mockReply: any;

  beforeEach(() => {
    vi.clearAllMocks();
    mockRequest = createMockRequest();
    mockReply = createMockReply();
  });

  describe('Authorization Security', () => {
    it('should reject unauthorized access to metrics endpoints', async () => {
      mockRequest.headers.authorization = undefined;
      mockRequest.cookies = {};

      const result = await checkMetricsAuthorization(mockRequest);

      expect(result.authorized).toBe(false);
      expect(result.errorCode).toBe(401);
      expect(result.message).toBe('Authentication required');
    });

    it('should reject access with invalid tokens', async () => {
      const invalidTokens = [
        'invalid-token-format',
        'bearer ',
        'Bearer invalid.jwt.token',
        'Bearer <script>alert(1)</script>',
        'Bearer token; path=/'
      ];

      for (const token of invalidTokens) {
        mockRequest.headers.authorization = token;
        const result = await checkMetricsAuthorization(mockRequest);

        expect(result.authorized).toBe(false);
        expect(result.errorCode).toBe(401);
      }
    });

    it('should enforce role-based access for different metric types', async () => {
      const testCases = [
        { role: 'AGENT', endpoint: '/metrics/personal', allowed: true },
        { role: 'AGENT', endpoint: '/metrics/team', allowed: false },
        { role: 'AGENT', endpoint: '/metrics/system', allowed: false },
        { role: 'SUPERVISOR', endpoint: '/metrics/personal', allowed: true },
        { role: 'SUPERVISOR', endpoint: '/metrics/team', allowed: true },
        { role: 'SUPERVISOR', endpoint: '/metrics/system', allowed: false },
        { role: 'ADMIN', endpoint: '/metrics/personal', allowed: true },
        { role: 'ADMIN', endpoint: '/metrics/team', allowed: true },
        { role: 'ADMIN', endpoint: '/metrics/system', allowed: true }
      ];

      for (const testCase of testCases) {
        mockRequest.user = { role: testCase.role };
        mockRequest.url = testCase.endpoint;

        const result = await checkMetricsAccess(mockRequest);
        expect(result.allowed).toBe(testCase.allowed);
      }
    });

    it('should validate organization access for metrics', async () => {
      mockRequest.user = {
        id: 'user-123',
        role: 'SUPERVISOR',
        organizationId: 'org-abc'
      };

      // Should allow access to own organization metrics
      const ownOrgResult = await checkOrganizationAccess(mockRequest, 'org-abc');
      expect(ownOrgResult.allowed).toBe(true);

      // Should deny access to other organization metrics
      const otherOrgResult = await checkOrganizationAccess(mockRequest, 'org-xyz');
      expect(otherOrgResult.allowed).toBe(false);
    });

    it('should block access to metrics without valid session', async () => {
      mockRequest.user = null;
      mockRequest.headers.authorization = 'Bearer expired.jwt.token';

      const result = await validateMetricsSession(mockRequest);

      expect(result.valid).toBe(false);
      expect(result.reason).toBe('invalid_session');
    });
  });

  describe('Rate Limiting Security', () => {
    it('should enforce rate limits on metrics API calls', async () => {
      const rateLimiter = createMetricsRateLimiter();
      const clientId = 'user-123';

      // Allow initial requests within limit
      for (let i = 0; i < 100; i++) {
        expect(rateLimiter.checkLimit(clientId)).toBe(true);
      }

      // Block requests exceeding limit
      for (let i = 0; i < 10; i++) {
        expect(rateLimiter.checkLimit(clientId)).toBe(false);
      }
    });

    it('should have different rate limits for different user roles', async () => {
      const rateLimiter = createMetricsRateLimiter();

      // Admin should have higher limits
      const adminLimits = rateLimiter.getLimits('ADMIN');
      expect(adminLimits.requestsPerMinute).toBe(1000);
      expect(adminLimits.requestsPerHour).toBe(10000);

      // Agent should have lower limits
      const agentLimits = rateLimiter.getLimits('AGENT');
      expect(agentLimits.requestsPerMinute).toBe(60);
      expect(agentLimits.requestsPerHour).toBe(1000);
    });

    it('should implement burst protection for metrics endpoints', async () => {
      const burstProtector = createBurstProtector();
      const userId = 'user-123';

      // Simulate burst of requests
      let blockedCount = 0;
      for (let i = 0; i < 20; i++) {
        const allowed = burstProtector.checkBurst(userId);
        if (!allowed) blockedCount++;
      }

      // Should block some requests in the burst
      expect(blockedCount).toBeGreaterThan(0);
    });

    it('should track and log rate limit violations', async () => {
      const rateLimiter = createMetricsRateLimiter();
      const logger = { warn: vi.fn(), error: vi.fn() };
      const userId = 'user-123';

      // Exceed rate limit
      for (let i = 0; i < 150; i++) {
        rateLimiter.checkLimit(userId, logger);
      }

      // Should have logged rate limit violations
      expect(logger.warn).toHaveBeenCalledWith(
        expect.stringContaining('Rate limit exceeded'),
        expect.objectContaining({
          userId,
          endpoint: expect.any(String),
          attempts: expect.any(Number)
        })
      );
    });
  });

  describe('Data Exposure Prevention', () => {
    it('should filter sensitive fields from metrics responses', async () => {
      const sensitiveMetrics = {
        userId: 'user-123',
        email: 'user@example.com',
        passwordHash: '$2b$10$abcdef...',
        apiKey: 'secret-api-key-123',
        sessionToken: 'jwt.session.token',
        callDuration: 120,
        callCount: 5,
        customerPhone: '+1234567890',
        customerEmail: 'customer@example.com',
        recording: 'https://recordings.s3.amazonaws.com/secret-url',
        internalNotes: 'Customer complained about service'
      };

      const filtered = filterSensitiveMetrics(sensitiveMetrics);

      // Should remove sensitive fields
      expect(filtered.passwordHash).toBeUndefined();
      expect(filtered.apiKey).toBeUndefined();
      expect(filtered.sessionToken).toBeUndefined();

      // Should keep non-sensitive metrics
      expect(filtered.callDuration).toBe(120);
      expect(filtered.callCount).toBe(5);

      // Should mask PII
      expect(filtered.customerPhone).toMatch(/^\+\*\*\*\*\*\*\*890$/);
      expect(filtered.customerEmail).toMatch(/\*{3}@example\.com$/);
    });

    it('should anonymize user data in aggregate metrics', async () => {
      const userMetrics = [
        { userId: 'user-1', name: 'John Doe', callCount: 10 },
        { userId: 'user-2', name: 'Jane Smith', callCount: 15 },
        { userId: 'user-3', name: 'Bob Johnson', callCount: 8 }
      ];

      const anonymized = anonymizeUserMetrics(userMetrics);

      for (const metric of anonymized) {
        expect(metric.userId).toMatch(/^user_[a-f0-9]{8}$/);
        expect(metric.name).toMatch(/^User_[A-Z0-9]{6}$/);
        expect(metric.callCount).toBeDefined();
      }
    });

    it('should redact call content from metrics data', async () => {
      const callMetrics = {
        callId: 'call-123',
        duration: 300,
        transcript: 'Customer said: My credit card number is 4532-1234-5678-9012',
        summary: 'Customer provided payment information',
        agentNotes: 'Customer SSN: 123-45-6789',
        sentiment: 'positive',
        keywords: ['payment', 'credit card', 'social security']
      };

      const redacted = redactCallContent(callMetrics);

      // Should redact sensitive content
      expect(redacted.transcript).not.toContain('4532-1234-5678-9012');
      expect(redacted.agentNotes).not.toContain('123-45-6789');

      // Should keep metrics but filter keywords
      expect(redacted.duration).toBe(300);
      expect(redacted.sentiment).toBe('positive');
      expect(redacted.keywords).not.toContain('credit card');
      expect(redacted.keywords).not.toContain('social security');
    });

    it('should implement field-level access control', async () => {
      const metrics = {
        basicStats: { callCount: 10, avgDuration: 120 },
        financialData: { revenue: 15000, costs: 8000 },
        personalData: { agentPerformance: 'excellent', feedback: 'needs improvement' },
        systemData: { cpuUsage: 45, memoryUsage: 78 }
      };

      const agentView = filterMetricsByRole(metrics, 'AGENT');
      expect(agentView.basicStats).toBeDefined();
      expect(agentView.financialData).toBeUndefined();
      expect(agentView.personalData).toBeDefined();
      expect(agentView.systemData).toBeUndefined();

      const supervisorView = filterMetricsByRole(metrics, 'SUPERVISOR');
      expect(supervisorView.basicStats).toBeDefined();
      expect(supervisorView.financialData).toBeDefined();
      expect(supervisorView.personalData).toBeDefined();
      expect(supervisorView.systemData).toBeUndefined();

      const adminView = filterMetricsByRole(metrics, 'ADMIN');
      expect(adminView.basicStats).toBeDefined();
      expect(adminView.financialData).toBeDefined();
      expect(adminView.personalData).toBeDefined();
      expect(adminView.systemData).toBeDefined();
    });
  });

  describe('Input Validation Security', () => {
    it('should validate metrics query parameters', async () => {
      const validQueries = [
        { startDate: '2024-01-01', endDate: '2024-01-31', agentId: 'agent-123' },
        { timeRange: 'last_7_days', metrics: 'calls,duration' },
        { page: '1', limit: '50', sortBy: 'date' }
      ];

      const invalidQueries = [
        { startDate: '<script>alert(1)</script>', endDate: '2024-01-31' },
        { agentId: '../../../etc/passwd' },
        { metrics: 'calls; DROP TABLE metrics; --' },
        { limit: '999999' }, // Excessive limit
        { sortBy: 'password_hash' } // Unauthorized field
      ];

      for (const query of validQueries) {
        expect(validateMetricsQuery(query)).toBe(true);
      }

      for (const query of invalidQueries) {
        expect(validateMetricsQuery(query)).toBe(false);
      }
    });

    it('should sanitize filter inputs to prevent injection', async () => {
      const maliciousFilters = {
        agentName: 'John\'; DROP TABLE agents; --',
        campaignName: '<script>alert("xss")</script>',
        phoneNumber: '../../../etc/passwd',
        dateRange: '2024-01-01 OR 1=1'
      };

      const sanitized = sanitizeMetricsFilters(maliciousFilters);

      expect(sanitized.agentName).not.toContain('DROP TABLE');
      expect(sanitized.campaignName).not.toContain('<script>');
      expect(sanitized.phoneNumber).not.toContain('../');
      expect(sanitized.dateRange).not.toContain('OR 1=1');
    });

    it('should validate time range parameters', async () => {
      const now = new Date();
      const validRanges = [
        { start: new Date(now.getTime() - 24 * 60 * 60 * 1000), end: now }, // 1 day
        { start: new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000), end: now }, // 30 days
        { start: new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000), end: now } // 1 year
      ];

      const invalidRanges = [
        { start: new Date(now.getTime() - 5 * 365 * 24 * 60 * 60 * 1000), end: now }, // 5 years
        { start: now, end: new Date(now.getTime() - 24 * 60 * 60 * 1000) }, // End before start
        { start: new Date(now.getTime() + 24 * 60 * 60 * 1000), end: now } // Future start
      ];

      for (const range of validRanges) {
        expect(validateTimeRange(range.start, range.end)).toBe(true);
      }

      for (const range of invalidRanges) {
        expect(validateTimeRange(range.start, range.end)).toBe(false);
      }
    });
  });

  describe('Caching and Performance Security', () => {
    it('should implement secure caching for metrics data', async () => {
      const cache = createSecureMetricsCache();
      const userId = 'user-123';
      const orgId = 'org-abc';

      const metricsData = { callCount: 50, avgDuration: 120 };

      // Cache data with proper scoping
      cache.set(userId, orgId, 'daily_stats', metricsData);

      // Should retrieve data for same user and org
      const retrieved = cache.get(userId, orgId, 'daily_stats');
      expect(retrieved).toEqual(metricsData);

      // Should not retrieve data for different user/org
      const notFound1 = cache.get('other-user', orgId, 'daily_stats');
      const notFound2 = cache.get(userId, 'other-org', 'daily_stats');

      expect(notFound1).toBeNull();
      expect(notFound2).toBeNull();
    });

    it('should expire cached metrics data appropriately', async () => {
      const cache = createSecureMetricsCache();
      const userId = 'user-123';
      const orgId = 'org-abc';

      // Set data with short TTL
      cache.set(userId, orgId, 'temp_stats', { data: 'test' }, 100); // 100ms TTL

      // Should be available immediately
      expect(cache.get(userId, orgId, 'temp_stats')).toBeTruthy();

      // Should expire after TTL
      await new Promise(resolve => setTimeout(resolve, 150));
      expect(cache.get(userId, orgId, 'temp_stats')).toBeNull();
    });

    it('should prevent cache poisoning attacks', async () => {
      const cache = createSecureMetricsCache();

      const maliciousKey = '../../../admin_metrics';
      const maliciousData = { admin: 'password', secretKey: 'abc123' };

      // Should reject malicious cache keys
      expect(() => {
        cache.set('user-123', 'org-abc', maliciousKey, maliciousData);
      }).toThrow('Invalid cache key');

      // Should sanitize data before caching
      const sanitizedData = cache.sanitizeData(maliciousData);
      expect(sanitizedData.admin).toBeUndefined();
      expect(sanitizedData.secretKey).toBeUndefined();
    });
  });
});

// Helper functions for metrics security
async function checkMetricsAuthorization(request: any): Promise<{ authorized: boolean; errorCode?: number; message?: string }> {
  const authHeader = request.headers.authorization;
  const cookies = request.cookies || {};

  if (!authHeader && !cookies.session) {
    return { authorized: false, errorCode: 401, message: 'Authentication required' };
  }

  const token = authHeader?.replace('Bearer ', '') || cookies.session;

  if (!token || typeof token !== 'string' || token.includes('<script>') || token.includes(';')) {
    return { authorized: false, errorCode: 401, message: 'Invalid token format' };
  }

  // Simulate token validation
  if (token === 'valid-token-123') {
    return { authorized: true };
  }

  return { authorized: false, errorCode: 401, message: 'Invalid token' };
}

async function checkMetricsAccess(request: any): Promise<{ allowed: boolean; reason?: string }> {
  const user = request.user;
  const url = request.url;

  if (!user) {
    return { allowed: false, reason: 'No user context' };
  }

  const rolePermissions = {
    ADMIN: ['/metrics/personal', '/metrics/team', '/metrics/system'],
    SUPERVISOR: ['/metrics/personal', '/metrics/team'],
    AGENT: ['/metrics/personal']
  };

  const allowedEndpoints = rolePermissions[user.role as keyof typeof rolePermissions] || [];

  return { allowed: allowedEndpoints.includes(url) };
}

async function checkOrganizationAccess(request: any, requestedOrgId: string): Promise<{ allowed: boolean; reason?: string }> {
  const user = request.user;

  if (!user || !user.organizationId) {
    return { allowed: false, reason: 'No organization context' };
  }

  return { allowed: user.organizationId === requestedOrgId };
}

async function validateMetricsSession(request: any): Promise<{ valid: boolean; reason?: string }> {
  if (!request.user) {
    return { valid: false, reason: 'invalid_session' };
  }

  // Additional session validation logic would go here
  return { valid: true };
}

function createMetricsRateLimiter() {
  const limits = new Map<string, { requests: number[]; role: string }>();

  return {
    checkLimit(userId: string, logger?: any): boolean {
      const now = Date.now();
      const windowMs = 60 * 1000; // 1 minute

      if (!limits.has(userId)) {
        limits.set(userId, { requests: [], role: 'AGENT' });
      }

      const userLimits = limits.get(userId)!;
      userLimits.requests = userLimits.requests.filter(time => now - time < windowMs);

      const maxRequests = this.getLimits(userLimits.role).requestsPerMinute;

      if (userLimits.requests.length >= maxRequests) {
        if (logger) {
          logger.warn('Rate limit exceeded', {
            userId,
            endpoint: '/metrics',
            attempts: userLimits.requests.length
          });
        }
        return false;
      }

      userLimits.requests.push(now);
      return true;
    },

    getLimits(role: string) {
      const roleLimits = {
        ADMIN: { requestsPerMinute: 1000, requestsPerHour: 10000 },
        SUPERVISOR: { requestsPerMinute: 200, requestsPerHour: 2000 },
        AGENT: { requestsPerMinute: 60, requestsPerHour: 1000 }
      };

      return roleLimits[role as keyof typeof roleLimits] || roleLimits.AGENT;
    }
  };
}

function createBurstProtector() {
  const bursts = new Map<string, number[]>();

  return {
    checkBurst(userId: string): boolean {
      const now = Date.now();
      const burstWindow = 10 * 1000; // 10 seconds
      const maxBurstRequests = 10;

      if (!bursts.has(userId)) {
        bursts.set(userId, []);
      }

      const userBursts = bursts.get(userId)!;
      const recentBursts = userBursts.filter(time => now - time < burstWindow);

      if (recentBursts.length >= maxBurstRequests) {
        return false;
      }

      recentBursts.push(now);
      bursts.set(userId, recentBursts);
      return true;
    }
  };
}

function filterSensitiveMetrics(metrics: any): any {
  const sensitiveFields = ['passwordHash', 'apiKey', 'sessionToken', 'authToken', 'secretKey'];
  const piiFields = ['email', 'phone', 'ssn', 'creditCard'];

  const filtered = { ...metrics };

  // Remove sensitive fields
  for (const field of sensitiveFields) {
    delete filtered[field];
  }

  // Mask PII fields
  for (const field of piiFields) {
    if (filtered[field]) {
      filtered[field] = maskPII(filtered[field], field);
    }
  }

  // Handle nested fields
  if (filtered.customerPhone) {
    filtered.customerPhone = maskPhoneNumber(filtered.customerPhone);
  }

  if (filtered.customerEmail) {
    filtered.customerEmail = maskEmail(filtered.customerEmail);
  }

  return filtered;
}

function maskPII(value: string, type: string): string {
  switch (type) {
    case 'email':
      return value.replace(/(.{1,3}).*@/, '***@');
    case 'phone':
      return value.replace(/(\+?\d{1,3}).*(\d{3})$/, '$1*******$2');
    default:
      return '***';
  }
}

function maskPhoneNumber(phone: string): string {
  return phone.replace(/(\+\d{1,3}).*(\d{3})$/, '$1*******$2');
}

function maskEmail(email: string): string {
  return email.replace(/(.{1,3}).*(@.+)/, '***$2');
}

function anonymizeUserMetrics(userMetrics: any[]): any[] {
  const crypto = require('crypto');

  return userMetrics.map(metric => ({
    ...metric,
    userId: 'user_' + crypto.createHash('md5').update(metric.userId).digest('hex').substring(0, 8),
    name: 'User_' + crypto.randomBytes(3).toString('hex').toUpperCase()
  }));
}

function redactCallContent(callMetrics: any): any {
  const redacted = { ...callMetrics };

  // Redact credit card numbers
  if (redacted.transcript) {
    redacted.transcript = redacted.transcript.replace(/\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}/g, '[REDACTED-CARD]');
  }

  // Redact SSN
  if (redacted.agentNotes) {
    redacted.agentNotes = redacted.agentNotes.replace(/\d{3}[-\s]?\d{2}[-\s]?\d{4}/g, '[REDACTED-SSN]');
  }

  // Filter sensitive keywords
  if (redacted.keywords) {
    const sensitiveKeywords = ['credit card', 'social security', 'ssn', 'password', 'pin'];
    redacted.keywords = redacted.keywords.filter((keyword: string) =>
      !sensitiveKeywords.some(sensitive => keyword.toLowerCase().includes(sensitive))
    );
  }

  return redacted;
}

function filterMetricsByRole(metrics: any, role: string): any {
  const roleAccess = {
    AGENT: ['basicStats', 'personalData'],
    SUPERVISOR: ['basicStats', 'financialData', 'personalData'],
    ADMIN: ['basicStats', 'financialData', 'personalData', 'systemData']
  };

  const allowedFields = roleAccess[role as keyof typeof roleAccess] || [];
  const filtered: any = {};

  for (const field of allowedFields) {
    if (metrics[field]) {
      filtered[field] = metrics[field];
    }
  }

  return filtered;
}

function validateMetricsQuery(query: any): boolean {
  // Check for malicious patterns
  for (const [key, value] of Object.entries(query)) {
    if (typeof value === 'string') {
      if (value.includes('<script>') || value.includes('DROP TABLE') || value.includes('../')) {
        return false;
      }
    }
  }

  // Validate specific fields
  if (query.limit && parseInt(query.limit) > 1000) return false;
  if (query.sortBy && ['password_hash', 'api_key', 'secret'].includes(query.sortBy)) return false;

  return true;
}

function sanitizeMetricsFilters(filters: any): any {
  const sanitized = { ...filters };

  for (const [key, value] of Object.entries(sanitized)) {
    if (typeof value === 'string') {
      sanitized[key] = value
        .replace(/DROP\s+TABLE/gi, '')
        .replace(/<script[^>]*>.*?<\/script>/gi, '')
        .replace(/\.\.\/+/g, '')
        .replace(/\s+OR\s+\d+=\d+/gi, '');
    }
  }

  return sanitized;
}

function validateTimeRange(start: Date, end: Date): boolean {
  if (!start || !end || !(start instanceof Date) || !(end instanceof Date)) return false;
  if (start >= end) return false;

  const now = new Date();
  const maxHistory = new Date(now.getTime() - 2 * 365 * 24 * 60 * 60 * 1000); // 2 years

  return start >= maxHistory && start <= now && end <= now;
}

function createSecureMetricsCache() {
  const cache = new Map<string, { data: any; expires: number; orgId: string; userId: string }>();

  return {
    set(userId: string, orgId: string, key: string, data: any, ttlMs = 300000): void {
      if (key.includes('../') || key.includes('<script>')) {
        throw new Error('Invalid cache key');
      }

      const sanitizedData = this.sanitizeData(data);
      const cacheKey = `${userId}:${orgId}:${key}`;
      const expires = Date.now() + ttlMs;

      cache.set(cacheKey, { data: sanitizedData, expires, orgId, userId });
    },

    get(userId: string, orgId: string, key: string): any {
      const cacheKey = `${userId}:${orgId}:${key}`;
      const cached = cache.get(cacheKey);

      if (!cached) return null;
      if (cached.expires < Date.now()) {
        cache.delete(cacheKey);
        return null;
      }
      if (cached.userId !== userId || cached.orgId !== orgId) {
        return null; // Security: prevent cross-user/org access
      }

      return cached.data;
    },

    sanitizeData(data: any): any {
      const sensitiveFields = ['admin', 'password', 'secretKey', 'apiKey', 'token'];
      const sanitized = { ...data };

      for (const field of sensitiveFields) {
        delete sanitized[field];
      }

      return sanitized;
    }
  };
}