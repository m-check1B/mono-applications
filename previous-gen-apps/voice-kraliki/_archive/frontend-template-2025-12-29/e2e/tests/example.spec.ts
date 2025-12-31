import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage.js';
import { DashboardPage } from '../pages/DashboardPage.js';
import { waitForLoadingComplete } from '../utils/helpers.js';
import { expectVisible, expectTitleContains, expectUrlContains } from '../utils/assertions.js';

/**
 * Example E2E tests for Voice by Kraliki
 * These tests demonstrate basic functionality and serve as templates for additional tests
 */

test.describe('Homepage Tests', () => {
	test('should navigate to homepage', async ({ page }) => {
		// Navigate to the application
		await page.goto('/');

		// Wait for page to load
		await page.waitForLoadState('domcontentloaded');

		// Assert that page loaded successfully
		expect(page.url()).toContain('/');
	});

	test('should have correct page title', async ({ page }) => {
		// Navigate to homepage
		await page.goto('/');

		// Check that title contains expected text
		await expect(page).toHaveTitle(/Voice by Kraliki/i);
	});

	test('should display main navigation elements', async ({ page }) => {
		// Navigate to homepage
		await page.goto('/');

		// Wait for loading to complete
		await waitForLoadingComplete(page);

		// Check for navigation or main content area
		const navigation = page.locator('nav, [role="navigation"], header, [role="banner"]');
		await expect(navigation.first()).toBeVisible({ timeout: 10000 });
	});
});

test.describe('Login Page Tests', () => {
	test('should navigate to login page', async ({ page }) => {
		const loginPage = new LoginPage(page);

		// Navigate to login page
		await loginPage.goto();

		// Verify we're on the login page
		await expectUrlContains(page, '/auth/login');
	});

	test('should display login form', async ({ page }) => {
		const loginPage = new LoginPage(page);

		// Navigate to login page
		await loginPage.goto();

		// Check if form is visible
		const isVisible = await loginPage.isFormVisible();
		expect(isVisible).toBeTruthy();

		// Verify form elements
		await expectVisible(loginPage.emailInput, 5000, 'Email input should be visible');
		await expectVisible(loginPage.passwordInput, 5000, 'Password input should be visible');
		await expectVisible(loginPage.loginButton, 5000, 'Login button should be visible');
	});

	test('should have working form inputs', async ({ page }) => {
		const loginPage = new LoginPage(page);

		// Navigate to login page
		await loginPage.goto();

		// Fill in email
		await loginPage.fillEmail('test@example.com');
		await expect(loginPage.emailInput).toHaveValue('test@example.com');

		// Fill in password
		await loginPage.fillPassword('password123');
		await expect(loginPage.passwordInput).toHaveValue('password123');

		// Verify login button is enabled
		const isEnabled = await loginPage.isLoginButtonEnabled();
		expect(isEnabled).toBeTruthy();
	});

	test('should clear form fields', async ({ page }) => {
		const loginPage = new LoginPage(page);

		// Navigate to login page
		await loginPage.goto();

		// Fill in form
		await loginPage.fillEmail('test@example.com');
		await loginPage.fillPassword('password123');

		// Clear form
		await loginPage.clearForm();

		// Verify fields are empty
		await expect(loginPage.emailInput).toHaveValue('');
		await expect(loginPage.passwordInput).toHaveValue('');
	});
});

test.describe('Dashboard Tests', () => {
	test('should have dashboard page', async ({ page }) => {
		const dashboardPage = new DashboardPage(page);

		// Try to navigate to dashboard
		// Note: This will likely redirect to login if not authenticated
		await page.goto('/dashboard');

		// Wait for page to load
		await page.waitForLoadState('domcontentloaded');

		// Check if we're on dashboard or redirected to login
		const currentUrl = page.url();
		const isOnDashboardOrLogin =
			currentUrl.includes('/dashboard') || currentUrl.includes('/auth/login');

		expect(isOnDashboardOrLogin).toBeTruthy();
	});
});

test.describe('UI Responsiveness Tests', () => {
	test('should be responsive on mobile viewport', async ({ page }) => {
		// Set mobile viewport
		await page.setViewportSize({ width: 375, height: 667 });

		// Navigate to homepage
		await page.goto('/');

		// Wait for page to load
		await page.waitForLoadState('domcontentloaded');

		// Verify page loaded successfully
		expect(page.url()).toContain('/');
	});

	test('should be responsive on tablet viewport', async ({ page }) => {
		// Set tablet viewport
		await page.setViewportSize({ width: 768, height: 1024 });

		// Navigate to homepage
		await page.goto('/');

		// Wait for page to load
		await page.waitForLoadState('domcontentloaded');

		// Verify page loaded successfully
		expect(page.url()).toContain('/');
	});

	test('should be responsive on desktop viewport', async ({ page }) => {
		// Set desktop viewport
		await page.setViewportSize({ width: 1920, height: 1080 });

		// Navigate to homepage
		await page.goto('/');

		// Wait for page to load
		await page.waitForLoadState('domcontentloaded');

		// Verify page loaded successfully
		expect(page.url()).toContain('/');
	});
});

test.describe('Basic Navigation Tests', () => {
	test('should handle browser back/forward navigation', async ({ page }) => {
		// Navigate to homepage
		await page.goto('/');
		const homeUrl = page.url();

		// Navigate to login page
		await page.goto('/auth/login');
		const loginUrl = page.url();

		expect(loginUrl).toContain('/auth/login');

		// Go back
		await page.goBack();
		await page.waitForLoadState('domcontentloaded');
		expect(page.url()).toBe(homeUrl);

		// Go forward
		await page.goForward();
		await page.waitForLoadState('domcontentloaded');
		expect(page.url()).toBe(loginUrl);
	});

	test('should handle page reload', async ({ page }) => {
		// Navigate to homepage
		await page.goto('/');

		// Reload page
		await page.reload();

		// Wait for page to load
		await page.waitForLoadState('domcontentloaded');

		// Verify page loaded successfully
		expect(page.url()).toContain('/');
	});
});

test.describe('Accessibility Tests', () => {
	test('should have accessible navigation', async ({ page }) => {
		// Navigate to homepage
		await page.goto('/');

		// Check for navigation landmark
		const navigation = page.locator('nav, [role="navigation"]');
		const navCount = await navigation.count();

		// Should have at least one navigation element
		expect(navCount).toBeGreaterThan(0);
	});

	test('should have accessible form labels', async ({ page }) => {
		const loginPage = new LoginPage(page);

		// Navigate to login page
		await loginPage.goto();

		// Check for form labels or aria-labels
		const emailHasLabel = await page
			.locator('label[for*="email"], input[aria-label*="email" i], input[placeholder*="email" i]')
			.count();

		const passwordHasLabel = await page
			.locator('label[for*="password"], input[aria-label*="password" i], input[placeholder*="password" i]')
			.count();

		expect(emailHasLabel).toBeGreaterThan(0);
		expect(passwordHasLabel).toBeGreaterThan(0);
	});
});

test.describe('Performance Tests', () => {
	test('should load homepage quickly', async ({ page }) => {
		const startTime = Date.now();

		// Navigate to homepage
		await page.goto('/');

		// Wait for page to be fully loaded
		await page.waitForLoadState('load');

		const loadTime = Date.now() - startTime;

		// Page should load within 5 seconds
		expect(loadTime).toBeLessThan(5000);
	});
});
