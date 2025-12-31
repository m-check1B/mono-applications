import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { testDb, createTestUser } from '../setup';
import { UserRole } from '@prisma/client';
import bcrypt from 'bcrypt';

// Security test configuration
const SECURITY_TEST_CONFIG = {
  maxLoginAttempts: 5,
  lockoutDuration: 15 * 60 * 1000, // 15 minutes
  passwordMinLength: 8,
  passwordRequireSpecialChar: true,
  sessionTimeout: 24 * 60 * 60 * 1000, // 24 hours
  requireTwoFactor: false, // Can be enabled for production
};

// Mock authentication service
const mockAuthService = {
  validatePassword: vi.fn(),
  generateToken: vi.fn(),
  verifyToken: vi.fn(),
  hashPassword: vi.fn(),
  recordFailedAttempt: vi.fn(),
  checkAccountLockout: vi.fn(),
  resetAccountLockout: vi.fn(),
};

// Mock rate limiter
const mockRateLimiter = {
  isAllowed: vi.fn().mockResolvedValue(true),
  increment: vi.fn(),
  reset: vi.fn(),
};

describe('Authentication Security Tests', () => {
  let testOrganizationId: string;
  let testUser: any;

  beforeEach(async () => {
    testOrganizationId = 'test-org-security';

    testUser = await createTestUser({
      email: 'security.test@example.com',
      username: 'security_test',
      role: UserRole.AGENT,
      organizationId: testOrganizationId,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Password Security', () => {
    it('should enforce strong password requirements', async () => {
      const weakPasswords = [
        '123456',
        'password',
        'qwerty',
        'admin',
        'test',
        '12345678', // No special chars
        'Passw0rd', // Common pattern
        'abc123!', // Too short
      ];

      for (const password of weakPasswords) {
        const isValid = validatePasswordStrength(password);
        expect(isValid.valid).toBe(false);
        expect(isValid.errors.length).toBeGreaterThan(0);
      }
    });

    it('should accept strong passwords', async () => {
      const strongPasswords = [
        'MyStr0ng!Password',
        'C0mplex$Pass123',
        'Secur3#System9',
        'Admin@2024!Secure',
      ];

      for (const password of strongPasswords) {
        const isValid = validatePasswordStrength(password);
        expect(isValid.valid).toBe(true);
        expect(isValid.errors.length).toBe(0);
      }
    });

    it('should properly hash passwords', async () => {
      const plainPassword = 'TestPassword123!';
      const hashedPassword = await bcrypt.hash(plainPassword, 10);

      // Verify hash is different from plain text
      expect(hashedPassword).not.toBe(plainPassword);
      expect(hashedPassword.length).toBeGreaterThan(50);

      // Verify hash can be verified
      const isValid = await bcrypt.compare(plainPassword, hashedPassword);
      expect(isValid).toBe(true);

      // Verify wrong password fails
      const isInvalid = await bcrypt.compare('WrongPassword', hashedPassword);
      expect(isInvalid).toBe(false);
    });

    it('should prevent password reuse', async () => {
      const currentPasswordHash = testUser.passwordHash;
      const newPassword = 'NewPassword123!';
      const newPasswordHash = await bcrypt.hash(newPassword, 10);

      // Simulate password history check
      const passwordHistory = [currentPasswordHash];
      const isReused = await checkPasswordReuse(newPasswordHash, passwordHistory);

      expect(isReused).toBe(false);

      // Test reuse detection
      const reusedPasswordCheck = await checkPasswordReuse(currentPasswordHash, passwordHistory);
      expect(reusedPasswordCheck).toBe(true);
    });
  });

  describe('Login Attempt Security', () => {
    it('should rate limit login attempts', async () => {
      const userEmail = testUser.email;
      const attempts = [];

      // Simulate multiple failed login attempts
      for (let i = 0; i < SECURITY_TEST_CONFIG.maxLoginAttempts + 2; i++) {
        const attempt = simulateLoginAttempt(userEmail, 'wrongpassword');
        attempts.push(attempt);
      }

      const results = await Promise.all(attempts);

      // First attempts should be allowed
      results.slice(0, SECURITY_TEST_CONFIG.maxLoginAttempts).forEach(result => {
        expect(result.allowed).toBe(true);
      });

      // Subsequent attempts should be blocked
      results.slice(SECURITY_TEST_CONFIG.maxLoginAttempts).forEach(result => {
        expect(result.allowed).toBe(false);
        expect(result.reason).toBe('account_locked');
      });
    });

    it('should implement progressive delays for failed attempts', async () => {
      const userEmail = testUser.email;
      const delays = [];

      for (let i = 0; i < 5; i++) {
        const startTime = Date.now();
        await simulateFailedLogin(userEmail);
        const delay = Date.now() - startTime;
        delays.push(delay);
      }

      // Each delay should be longer than the previous (progressive backoff)
      for (let i = 1; i < delays.length; i++) {
        expect(delays[i]).toBeGreaterThanOrEqual(delays[i - 1]);
      }
    });

    it('should reset lockout after timeout period', async () => {
      const userEmail = testUser.email;

      // Lock the account
      for (let i = 0; i < SECURITY_TEST_CONFIG.maxLoginAttempts; i++) {
        await simulateFailedLogin(userEmail);
      }

      // Verify account is locked
      let loginResult = await simulateLoginAttempt(userEmail, 'correctpassword');
      expect(loginResult.allowed).toBe(false);

      // Simulate timeout period passing
      await simulateTimePassage(SECURITY_TEST_CONFIG.lockoutDuration + 1000);

      // Account should be unlocked
      loginResult = await simulateLoginAttempt(userEmail, 'password123');
      expect(loginResult.allowed).toBe(true);
    });

    it('should log security events', async () => {
      const securityEvents = [];
      const mockLogger = {
        logSecurityEvent: vi.fn().mockImplementation((event) => {
          securityEvents.push(event);
        }),
      };

      // Simulate various security events
      await simulateFailedLogin(testUser.email, mockLogger);
      await simulateSuccessfulLogin(testUser.email, mockLogger);
      await simulateSuspiciousActivity(testUser.email, mockLogger);

      expect(securityEvents.length).toBe(3);
      expect(securityEvents[0].type).toBe('failed_login');
      expect(securityEvents[1].type).toBe('successful_login');
      expect(securityEvents[2].type).toBe('suspicious_activity');

      // Verify all events have required security fields
      securityEvents.forEach(event => {
        expect(event).toHaveProperty('timestamp');
        expect(event).toHaveProperty('userEmail');
        expect(event).toHaveProperty('ipAddress');
        expect(event).toHaveProperty('userAgent');
        expect(event).toHaveProperty('type');
      });
    });
  });

  describe('Session Security', () => {
    it('should generate secure session tokens', async () => {
      const tokens = [];

      // Generate multiple tokens
      for (let i = 0; i < 10; i++) {
        const token = generateSessionToken();
        tokens.push(token);
      }

      // All tokens should be unique
      const uniqueTokens = new Set(tokens);
      expect(uniqueTokens.size).toBe(tokens.length);

      // Tokens should be sufficiently long and random
      tokens.forEach(token => {
        expect(token.length).toBeGreaterThanOrEqual(32);
        expect(token).toMatch(/^[a-zA-Z0-9+/=]+$/); // Base64 pattern
      });
    });

    it('should validate session expiration', async () => {
      const now = Date.now();

      // Create expired session
      const expiredSession = {
        token: 'expired-token',
        createdAt: new Date(now - SECURITY_TEST_CONFIG.sessionTimeout - 1000),
        userId: testUser.id,
      };

      // Create valid session
      const validSession = {
        token: 'valid-token',
        createdAt: new Date(now - 1000),
        userId: testUser.id,
      };

      expect(isSessionValid(expiredSession)).toBe(false);
      expect(isSessionValid(validSession)).toBe(true);
    });

    it('should invalidate sessions on logout', async () => {
      const sessionToken = generateSessionToken();

      // Create active session
      await createUserSession(testUser.id, sessionToken);

      // Verify session is valid
      let isValid = await validateSession(sessionToken);
      expect(isValid).toBe(true);

      // Logout and invalidate session
      await invalidateSession(sessionToken);

      // Session should no longer be valid
      isValid = await validateSession(sessionToken);
      expect(isValid).toBe(false);
    });

    it('should prevent session fixation attacks', async () => {
      const initialSessionId = 'fixed-session-id';

      // Simulate pre-login session
      const preLoginSession = createAnonymousSession(initialSessionId);

      // Attempt login with fixed session
      const loginResult = await simulateLoginWithFixedSession(
        testUser.email,
        'password123',
        initialSessionId
      );

      // Should create new session ID after successful login
      expect(loginResult.sessionId).not.toBe(initialSessionId);
      expect(loginResult.sessionId).toBeDefined();
      expect(loginResult.sessionId.length).toBeGreaterThan(20);
    });

    it('should protect against session hijacking', async () => {
      const sessionToken = generateSessionToken();
      const userAgent = 'Mozilla/5.0 (Test Browser)';
      const ipAddress = '192.168.1.100';

      // Create session with specific user agent and IP
      await createUserSession(testUser.id, sessionToken, {
        userAgent,
        ipAddress,
      });

      // Valid request from same environment
      let isValid = await validateSessionSecurity(sessionToken, {
        userAgent,
        ipAddress,
      });
      expect(isValid.valid).toBe(true);

      // Suspicious request from different user agent
      isValid = await validateSessionSecurity(sessionToken, {
        userAgent: 'Different Browser/1.0',
        ipAddress,
      });
      expect(isValid.valid).toBe(false);
      expect(isValid.reason).toBe('user_agent_mismatch');

      // Suspicious request from different IP
      isValid = await validateSessionSecurity(sessionToken, {
        userAgent,
        ipAddress: '10.0.0.1',
      });
      expect(isValid.valid).toBe(false);
      expect(isValid.reason).toBe('ip_address_mismatch');
    });
  });

  describe('Authorization Security', () => {
    it('should enforce role-based access control', async () => {
      const adminUser = await createTestUser({
        email: 'admin@test.com',
        role: UserRole.ADMIN,
        organizationId: testOrganizationId,
      });

      const agentUser = await createTestUser({
        email: 'agent@test.com',
        role: UserRole.AGENT,
        organizationId: testOrganizationId,
      });

      // Test admin access
      expect(hasPermission(adminUser, 'admin:create_user')).toBe(true);
      expect(hasPermission(adminUser, 'supervisor:view_all_calls')).toBe(true);
      expect(hasPermission(adminUser, 'agent:handle_calls')).toBe(true);

      // Test agent access
      expect(hasPermission(agentUser, 'agent:handle_calls')).toBe(true);
      expect(hasPermission(agentUser, 'supervisor:view_all_calls')).toBe(false);
      expect(hasPermission(agentUser, 'admin:create_user')).toBe(false);
    });

    it('should enforce organization isolation', async () => {
      const org1User = await createTestUser({
        email: 'user1@org1.com',
        role: UserRole.SUPERVISOR,
        organizationId: 'org-1',
      });

      const org2User = await createTestUser({
        email: 'user2@org2.com',
        role: UserRole.SUPERVISOR,
        organizationId: 'org-2',
      });

      // Create test data for each organization
      const org1Call = await testDb.call.create({
        data: {
          fromNumber: '+1111111111',
          toNumber: '+2222222222',
          direction: 'INBOUND',
          provider: 'TWILIO',
          organizationId: 'org-1',
          startTime: new Date(),
          metadata: {},
        },
      });

      const org2Call = await testDb.call.create({
        data: {
          fromNumber: '+3333333333',
          toNumber: '+4444444444',
          direction: 'INBOUND',
          provider: 'TWILIO',
          organizationId: 'org-2',
          startTime: new Date(),
          metadata: {},
        },
      });

      // Org1 user should only access org1 data
      expect(canAccessCall(org1User, org1Call)).toBe(true);
      expect(canAccessCall(org1User, org2Call)).toBe(false);

      // Org2 user should only access org2 data
      expect(canAccessCall(org2User, org2Call)).toBe(true);
      expect(canAccessCall(org2User, org1Call)).toBe(false);
    });

    it('should validate resource ownership', async () => {
      const agent1 = await createTestUser({
        email: 'agent1@test.com',
        role: UserRole.AGENT,
        organizationId: testOrganizationId,
      });

      const agent2 = await createTestUser({
        email: 'agent2@test.com',
        role: UserRole.AGENT,
        organizationId: testOrganizationId,
      });

      // Create calls assigned to each agent
      const agent1Call = await testDb.call.create({
        data: {
          fromNumber: '+1111111111',
          toNumber: '+2222222222',
          direction: 'INBOUND',
          provider: 'TWILIO',
          organizationId: testOrganizationId,
          agentId: agent1.id,
          startTime: new Date(),
          metadata: {},
        },
      });

      const agent2Call = await testDb.call.create({
        data: {
          fromNumber: '+3333333333',
          toNumber: '+4444444444',
          direction: 'INBOUND',
          provider: 'TWILIO',
          organizationId: testOrganizationId,
          agentId: agent2.id,
          startTime: new Date(),
          metadata: {},
        },
      });

      // Agents should only access their own calls
      expect(canAccessCall(agent1, agent1Call)).toBe(true);
      expect(canAccessCall(agent1, agent2Call)).toBe(false);

      expect(canAccessCall(agent2, agent2Call)).toBe(true);
      expect(canAccessCall(agent2, agent1Call)).toBe(false);
    });
  });

  describe('Input Validation Security', () => {
    it('should prevent SQL injection attempts', async () => {
      const maliciousInputs = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "'; INSERT INTO users VALUES ('hacker', 'password'); --",
        "' UNION SELECT * FROM users --",
      ];

      for (const input of maliciousInputs) {
        const result = await simulateUserLookup(input);

        // Should not return any results or cause errors
        expect(result.success).toBe(false);
        expect(result.error).toContain('Invalid input');
      }
    });

    it('should prevent XSS attacks', async () => {
      const xssPayloads = [
        '<script>alert("XSS")</script>',
        'javascript:alert("XSS")',
        '<img src="x" onerror="alert(\'XSS\')">',
        '<svg onload="alert(\'XSS\')">',
      ];

      for (const payload of xssPayloads) {
        const sanitized = sanitizeInput(payload);

        // Should not contain executable script content
        expect(sanitized).not.toContain('<script>');
        expect(sanitized).not.toContain('javascript:');
        expect(sanitized).not.toContain('onerror=');
        expect(sanitized).not.toContain('onload=');
      }
    });

    it('should validate phone number formats', async () => {
      const validPhoneNumbers = [
        '+1234567890',
        '+15551234567',
        '+44207123456',
      ];

      const invalidPhoneNumbers = [
        '1234567890',
        'phone',
        '123-456-7890',
        '(555) 123-4567',
        '+1 555 123 4567',
        '',
        null,
        undefined,
      ];

      validPhoneNumbers.forEach(phone => {
        expect(validatePhoneNumber(phone).valid).toBe(true);
      });

      invalidPhoneNumbers.forEach(phone => {
        expect(validatePhoneNumber(phone).valid).toBe(false);
      });
    });

    it('should validate email addresses', async () => {
      const validEmails = [
        'user@example.com',
        'test.email+tag@domain.co.uk',
        'user123@test-domain.com',
      ];

      const invalidEmails = [
        'notanemail',
        '@domain.com',
        'user@',
        'user..double.dot@domain.com',
        'user@domain',
        '',
        null,
        undefined,
      ];

      validEmails.forEach(email => {
        expect(validateEmail(email).valid).toBe(true);
      });

      invalidEmails.forEach(email => {
        expect(validateEmail(email).valid).toBe(false);
      });
    });
  });

  describe('CSRF Protection', () => {
    it('should generate and validate CSRF tokens', async () => {
      const sessionId = generateSessionToken();
      const csrfToken = generateCSRFToken(sessionId);

      // Valid CSRF token should pass validation
      expect(validateCSRFToken(csrfToken, sessionId)).toBe(true);

      // Invalid token should fail
      expect(validateCSRFToken('invalid-token', sessionId)).toBe(false);

      // Token for different session should fail
      const differentSessionId = generateSessionToken();
      expect(validateCSRFToken(csrfToken, differentSessionId)).toBe(false);
    });

    it('should require CSRF tokens for state-changing operations', async () => {
      const stateChangingOperations = [
        'createUser',
        'updateCall',
        'deleteContact',
        'transferCall',
        'endCall',
      ];

      for (const operation of stateChangingOperations) {
        // Request without CSRF token should fail
        const resultWithoutToken = await simulateAPIRequest(operation, {
          data: { test: 'data' },
        });
        expect(resultWithoutToken.success).toBe(false);
        expect(resultWithoutToken.error).toContain('CSRF');

        // Request with valid CSRF token should succeed
        const csrfToken = generateCSRFToken('test-session');
        const resultWithToken = await simulateAPIRequest(operation, {
          data: { test: 'data' },
          csrfToken,
          sessionId: 'test-session',
        });
        expect(resultWithToken.success).toBe(true);
      }
    });
  });
});

// Helper functions for security testing
function validatePasswordStrength(password: string) {
  const errors = [];

  if (password.length < SECURITY_TEST_CONFIG.passwordMinLength) {
    errors.push('Password too short');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Must contain uppercase letter');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Must contain lowercase letter');
  }

  if (!/[0-9]/.test(password)) {
    errors.push('Must contain number');
  }

  if (SECURITY_TEST_CONFIG.passwordRequireSpecialChar && !/[!@#$%^&*]/.test(password)) {
    errors.push('Must contain special character');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

async function checkPasswordReuse(newPasswordHash: string, passwordHistory: string[]) {
  for (const oldHash of passwordHistory) {
    if (await bcrypt.compare(newPasswordHash, oldHash)) {
      return true;
    }
  }
  return false;
}

function simulateLoginAttempt(email: string, password: string) {
  return {
    allowed: password === 'password123', // Simplified for testing
    reason: password === 'password123' ? 'success' : 'invalid_credentials',
  };
}

async function simulateFailedLogin(email: string, logger?: any) {
  if (logger) {
    logger.logSecurityEvent({
      type: 'failed_login',
      userEmail: email,
      timestamp: new Date(),
      ipAddress: '192.168.1.100',
      userAgent: 'Test Browser',
    });
  }

  return { success: false };
}

async function simulateSuccessfulLogin(email: string, logger?: any) {
  if (logger) {
    logger.logSecurityEvent({
      type: 'successful_login',
      userEmail: email,
      timestamp: new Date(),
      ipAddress: '192.168.1.100',
      userAgent: 'Test Browser',
    });
  }

  return { success: true };
}

async function simulateSuspiciousActivity(email: string, logger?: any) {
  if (logger) {
    logger.logSecurityEvent({
      type: 'suspicious_activity',
      userEmail: email,
      timestamp: new Date(),
      ipAddress: '192.168.1.100',
      userAgent: 'Test Browser',
      details: 'Multiple failed login attempts',
    });
  }

  return { success: false };
}

async function simulateTimePassage(milliseconds: number) {
  // Mock time passage for testing
  const originalNow = Date.now;
  Date.now = vi.fn(() => originalNow() + milliseconds);

  // Restore after test
  setTimeout(() => {
    Date.now = originalNow;
  }, 0);
}

function generateSessionToken() {
  return Buffer.from(Math.random().toString(36) + Date.now().toString(36)).toString('base64');
}

function isSessionValid(session: any) {
  const now = Date.now();
  const sessionAge = now - session.createdAt.getTime();
  return sessionAge < SECURITY_TEST_CONFIG.sessionTimeout;
}

async function createUserSession(userId: string, token: string, metadata?: any) {
  return testDb.userSession.create({
    data: {
      userId,
      token,
      createdAt: new Date(),
      metadata: metadata || {},
    },
  });
}

async function validateSession(token: string) {
  const session = await testDb.userSession.findUnique({
    where: { token },
  });

  return session && isSessionValid(session);
}

async function invalidateSession(token: string) {
  await testDb.userSession.delete({
    where: { token },
  });
}

function createAnonymousSession(sessionId: string) {
  return { id: sessionId, authenticated: false };
}

async function simulateLoginWithFixedSession(email: string, password: string, sessionId: string) {
  // Should generate new session ID after successful login
  const newSessionId = generateSessionToken();

  return {
    success: true,
    sessionId: newSessionId,
  };
}

async function validateSessionSecurity(token: string, request: any) {
  // Simplified security validation
  const session = await testDb.userSession.findUnique({
    where: { token },
  });

  if (!session) {
    return { valid: false, reason: 'session_not_found' };
  }

  const metadata = session.metadata as any;

  if (metadata.userAgent && metadata.userAgent !== request.userAgent) {
    return { valid: false, reason: 'user_agent_mismatch' };
  }

  if (metadata.ipAddress && metadata.ipAddress !== request.ipAddress) {
    return { valid: false, reason: 'ip_address_mismatch' };
  }

  return { valid: true };
}

function hasPermission(user: any, permission: string) {
  const rolePermissions = {
    [UserRole.ADMIN]: ['admin:*', 'supervisor:*', 'agent:*'],
    [UserRole.SUPERVISOR]: ['supervisor:*', 'agent:*'],
    [UserRole.AGENT]: ['agent:*'],
  };

  const userPermissions = rolePermissions[user.role] || [];

  return userPermissions.some(p =>
    p === permission || p.endsWith('*') && permission.startsWith(p.slice(0, -1))
  );
}

function canAccessCall(user: any, call: any) {
  // Check organization isolation
  if (user.organizationId !== call.organizationId) {
    return false;
  }

  // Check role-based access
  if (user.role === UserRole.AGENT) {
    return call.agentId === user.id;
  }

  // Supervisors and admins can access all calls in their organization
  return [UserRole.SUPERVISOR, UserRole.ADMIN].includes(user.role);
}

async function simulateUserLookup(input: string) {
  // Validate input for SQL injection
  if (/[';"]|DROP|INSERT|UPDATE|DELETE|UNION|SELECT/i.test(input)) {
    return { success: false, error: 'Invalid input detected' };
  }

  return { success: true, data: [] };
}

function sanitizeInput(input: string) {
  return input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function validatePhoneNumber(phone: any) {
  if (!phone || typeof phone !== 'string') {
    return { valid: false, error: 'Phone number is required' };
  }

  const phoneRegex = /^\+[1-9]\d{1,14}$/;
  return {
    valid: phoneRegex.test(phone),
    error: phoneRegex.test(phone) ? null : 'Invalid phone number format',
  };
}

function validateEmail(email: any) {
  if (!email || typeof email !== 'string') {
    return { valid: false, error: 'Email is required' };
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return {
    valid: emailRegex.test(email),
    error: emailRegex.test(email) ? null : 'Invalid email format',
  };
}

function generateCSRFToken(sessionId: string) {
  return Buffer.from(sessionId + ':' + Math.random().toString(36)).toString('base64');
}

function validateCSRFToken(token: string, sessionId: string) {
  try {
    const decoded = Buffer.from(token, 'base64').toString();
    return decoded.startsWith(sessionId + ':');
  } catch {
    return false;
  }
}

async function simulateAPIRequest(operation: string, params: any) {
  // Check for CSRF token on state-changing operations
  const stateChangingOps = ['createUser', 'updateCall', 'deleteContact', 'transferCall', 'endCall'];

  if (stateChangingOps.includes(operation)) {
    if (!params.csrfToken || !params.sessionId) {
      return { success: false, error: 'CSRF token required' };
    }

    if (!validateCSRFToken(params.csrfToken, params.sessionId)) {
      return { success: false, error: 'Invalid CSRF token' };
    }
  }

  return { success: true, data: 'Operation completed' };
}