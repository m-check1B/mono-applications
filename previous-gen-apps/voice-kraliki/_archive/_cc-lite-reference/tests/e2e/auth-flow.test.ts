import { chromium, Browser, Page } from 'playwright';
import { AuthService } from '../../server/auth/auth-service';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

describe('Authentication End-to-End Flow', () => {
  let browser: Browser;
  let page: Page;
  let prisma: PrismaClient;
  let authService: AuthService;

  beforeAll(async () => {
    // Set up test environment
    process.env.NODE_ENV = 'test';
    process.env.JWT_SECRET = 'test-jwt-secret';
    process.env.JWT_REFRESH_SECRET = 'test-refresh-secret';
    process.env.DATABASE_URL = 'postgresql://test:test@localhost:5432/cc_lite_test';

    // Initialize services
    prisma = new PrismaClient();
    authService = new AuthService(prisma);

    // Launch browser
    browser = await chromium.launch();
    page = await browser.newPage();
  });

  afterAll(async () => {
    // Clean up
    await browser.close();
    await prisma.$disconnect();
  });

  beforeEach(async () => {
    // Clean database
    await prisma.user.deleteMany();
    await prisma.userSession.deleteMany();
    await prisma.organization.deleteMany();

    // Create test organization
    await prisma.organization.create({
      data: {
        id: 'test-org-1',
        name: 'Test Organization',
        slug: 'test-org',
        settings: {},
      },
    });
  });

  describe('User Registration and Login Flow', () => {
    it('should complete full registration to login flow', async () => {
      // Navigate to application
      await page.goto('http://localhost:5174');

      // Wait for page to load
      await page.waitForSelector('[data-testid="app-container"]');

      // Click on register link
      await page.click('[data-testid="register-link"]');

      // Fill registration form
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'password123');
      await page.fill('[data-testid="firstName-input"]', 'John');
      await page.fill('[data-testid="lastName-input"]', 'Doe');

      // Submit registration form
      await page.click('[data-testid="register-button"]');

      // Wait for success message
      await page.waitForSelector('[data-testid="registration-success"]');

      // Verify user was created in database
      const user = await prisma.user.findUnique({
        where: { email: 'test@example.com' },
      });
      expect(user).toBeTruthy();
      expect(user!.status).toBe('ACTIVE');

      // Navigate to login
      await page.click('[data-testid="login-link"]');

      // Fill login form
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'password123');

      // Submit login form
      await page.click('[data-testid="login-button"]');

      // Wait for successful login redirect
      await page.waitForSelector('[data-testid="dashboard"]');

      // Verify authentication cookies are set
      const cookies = await page.context().cookies();
      const authCookie = cookies.find(c => c.name === 'cc_light_session');
      expect(authCookie).toBeTruthy();
      expect(authCookie!.secure).toBe(true);
      expect(authCookie!.httpOnly).toBe(true);

      // Verify user is authenticated
      await page.waitForSelector('[data-testid="user-profile"]');
      const userProfile = await page.textContent('[data-testid="user-profile"]');
      expect(userProfile).toContain('John Doe');
    });

    it('should handle invalid login credentials', async () => {
      // Create a test user
      const hashedPassword = bcrypt.hashSync('password123', 10);
      await prisma.user.create({
        data: {
          id: 'test-user-1',
          email: 'test@example.com',
          passwordHash: hashedPassword,
          firstName: 'John',
          lastName: 'Doe',
          role: 'USER',
          organizationId: 'test-org-1',
          status: 'ACTIVE',
        },
      });

      // Navigate to login page
      await page.goto('http://localhost:5174/login');

      // Fill login form with wrong password
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'wrongpassword');

      // Submit login form
      await page.click('[data-testid="login-button"]');

      // Wait for error message
      await page.waitForSelector('[data-testid="login-error"]');

      // Verify error message
      const errorMessage = await page.textContent('[data-testid="login-error"]');
      expect(errorMessage).toContain('Invalid credentials');

      // Verify not redirected to dashboard
      expect(page.url()).toContain('/login');
    });

    it('should handle duplicate email registration', async () => {
      // Create existing user
      const hashedPassword = bcrypt.hashSync('password123', 10);
      await prisma.user.create({
        data: {
          id: 'existing-user-1',
          email: 'existing@example.com',
          passwordHash: hashedPassword,
          firstName: 'Jane',
          lastName: 'Doe',
          role: 'USER',
          organizationId: 'test-org-1',
          status: 'ACTIVE',
        },
      });

      // Navigate to registration page
      await page.goto('http://localhost:5174/register');

      // Fill registration form with existing email
      await page.fill('[data-testid="email-input"]', 'existing@example.com');
      await page.fill('[data-testid="password-input"]', 'password123');
      await page.fill('[data-testid="firstName-input"]', 'Jane');
      await page.fill('[data-testid="lastName-input"]', 'Doe');

      // Submit registration form
      await page.click('[data-testid="register-button"]');

      // Wait for error message
      await page.waitForSelector('[data-testid="registration-error"]');

      // Verify error message
      const errorMessage = await page.textContent('[data-testid="registration-error"]');
      expect(errorMessage).toContain('User with this email already exists');
    });
  });

  describe('Session Management', () => {
    it('should maintain session via httpOnly cookies', async () => {
      // Create test user
      const hashedPassword = bcrypt.hashSync('password123', 10);
      await prisma.user.create({
        data: {
          id: 'test-user-1',
          email: 'test@example.com',
          passwordHash: hashedPassword,
          firstName: 'John',
          lastName: 'Doe',
          role: 'USER',
          organizationId: 'test-org-1',
          status: 'ACTIVE',
        },
      });

      // Login
      await page.goto('http://localhost:5174/login');
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'password123');
      await page.click('[data-testid="login-button"]');

      // Wait for dashboard
      await page.waitForSelector('[data-testid="dashboard"]');

      // Ensure access tokens are not stored in localStorage
      const storedToken = await page.evaluate(() => {
        return localStorage.getItem('cc_light_access_token');
      });
      expect(storedToken).toBeFalsy();

      // Verify session is backed by secure cookie
      let cookies = await page.context().cookies();
      let authCookie = cookies.find(c => c.name === 'cc_light_session');
      expect(authCookie).toBeTruthy();
      expect(authCookie!.httpOnly).toBe(true);

      // Reload the page to ensure session persists with cookies only
      await page.reload();
      await page.waitForSelector('[data-testid="dashboard"]');

      // Cookie should still be present after reload
      cookies = await page.context().cookies();
      authCookie = cookies.find(c => c.name === 'cc_light_session');
      expect(authCookie).toBeTruthy();

      // Clearing cookies should force re-authentication
      await page.context().clearCookies();
      await page.reload();
      await page.waitForSelector('[data-testid="login-page"]');
    });

    it('should handle session logout', async () => {
      // Create test user and login
      const hashedPassword = bcrypt.hashSync('password123', 10);
      await prisma.user.create({
        data: {
          id: 'test-user-1',
          email: 'test@example.com',
          passwordHash: hashedPassword,
          firstName: 'John',
          lastName: 'Doe',
          role: 'USER',
          organizationId: 'test-org-1',
          status: 'ACTIVE',
        },
      });

      await page.goto('http://localhost:5174/login');
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'password123');
      await page.click('[data-testid="login-button"]');

      // Wait for dashboard
      await page.waitForSelector('[data-testid="dashboard"]');

      // Logout
      await page.click('[data-testid="logout-button"]');

      // Wait for redirect to login page
      await page.waitForSelector('[data-testid="login-page"]');

      // Verify authentication cookies are cleared
      const cookies = await page.context().cookies();
      const authCookie = cookies.find(c => c.name === 'cc_light_session');
      expect(authCookie).toBeFalsy();

      // Verify no tokens remain in localStorage
      const accessToken = await page.evaluate(() => {
        return localStorage.getItem('cc_light_access_token');
      });
      expect(accessToken).toBeFalsy();

      // Verify cannot access protected route
      await page.goto('http://localhost:5174/dashboard');
      await page.waitForSelector('[data-testid="login-page"]');
    });
  });

  describe('Security Features', () => {
    it('should enforce rate limiting on login attempts', async () => {
      // Create test user
      const hashedPassword = bcrypt.hashSync('password123', 10);
      await prisma.user.create({
        data: {
          id: 'test-user-1',
          email: 'test@example.com',
          passwordHash: hashedPassword,
          firstName: 'John',
          lastName: 'Doe',
          role: 'USER',
          organizationId: 'test-org-1',
          status: 'ACTIVE',
        },
      });

      // Navigate to login page
      await page.goto('http://localhost:5174/login');

      // Attempt multiple failed logins
      for (let i = 0; i < 6; i++) {
        await page.fill('[data-testid="email-input"]', 'test@example.com');
        await page.fill('[data-testid="password-input"]', 'wrongpassword');
        await page.click('[data-testid="login-button"]');

        // Wait for error message or rate limit message
        await page.waitForTimeout(1000);
      }

      // Verify rate limiting message appears
      const rateLimitMessage = await page.textContent('[data-testid="rate-limit-error"]');
      expect(rateLimitMessage).toBeTruthy();
      expect(rateLimitMessage).toContain('Too many attempts');
    });

    it('should handle CSRF protection', async () => {
      // Create test user
      const hashedPassword = bcrypt.hashSync('password123', 10);
      await prisma.user.create({
        data: {
          id: 'test-user-1',
          email: 'test@example.com',
          passwordHash: hashedPassword,
          firstName: 'John',
          lastName: 'Doe',
          role: 'USER',
          organizationId: 'test-org-1',
          status: 'ACTIVE',
        },
      });

      // Login normally
      await page.goto('http://localhost:5174/login');
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'password123');
      await page.click('[data-testid="login-button"]');

      // Wait for dashboard
      await page.waitForSelector('[data-testid="dashboard"]');

      // Try to make a POST request without CSRF token
      const response = await page.request.post('http://localhost:3900/api/user/update-profile', {
        data: {
          firstName: 'Updated',
          lastName: 'Name',
        },
        headers: {
          'Content-Type': 'application/json',
        },
      });

      // Verify request is rejected
      expect(response.status()).toBe(403);
    });

    it('should validate input on registration', async () => {
      // Navigate to registration page
      await page.goto('http://localhost:5174/register');

      // Submit form with invalid email
      await page.fill('[data-testid="email-input"]', 'invalid-email');
      await page.fill('[data-testid="password-input"]', 'password123');
      await page.fill('[data-testid="firstName-input"]', 'John');
      await page.fill('[data-testid="lastName-input"]', 'Doe');

      // Submit registration form
      await page.click('[data-testid="register-button"]');

      // Wait for validation error
      await page.waitForSelector('[data-testid="validation-error"]');

      // Verify validation error message
      const errorMessage = await page.textContent('[data-testid="validation-error"]');
      expect(errorMessage).toContain('Invalid email address');
    });
  });

  describe('API Integration', () => {
    it('should integrate authentication with API endpoints', async () => {
      // Create test user
      const hashedPassword = bcrypt.hashSync('password123', 10);
      await prisma.user.create({
        data: {
          id: 'test-user-1',
          email: 'test@example.com',
          passwordHash: hashedPassword,
          firstName: 'John',
          lastName: 'Doe',
          role: 'USER',
          organizationId: 'test-org-1',
          status: 'ACTIVE',
        },
      });

      // Login
      await page.goto('http://localhost:5174/login');
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'password123');
      await page.click('[data-testid="login-button"]');

      // Wait for dashboard
      await page.waitForSelector('[data-testid="dashboard"]');

      // Test API endpoint that requires authentication
      const response = await page.request.get('http://localhost:3900/api/user/profile');

      // Verify successful response
      expect(response.status()).toBe(200);
      const userProfile = await response.json();
      expect(userProfile.email).toBe('test@example.com');
      expect(userProfile.firstName).toBe('John');
      expect(userProfile.lastName).toBe('Doe');
    });

    it('should handle API authentication errors', async () => {
      // Try to access protected API endpoint without authentication
      const response = await page.request.get('http://localhost:3900/api/user/profile');

      // Verify unauthorized response
      expect(response.status()).toBe(401);
    });
  });
});
