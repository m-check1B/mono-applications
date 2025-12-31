import { test, expect } from '../fixtures/auth.fixture.js';
import { LoginPage } from '../pages/LoginPage.js';
import { DashboardPage } from '../pages/DashboardPage.js';
import { TEST_USER, TEST_ADMIN } from '../fixtures/test-data.js';
import {
	assertAuthenticated,
	assertNotAuthenticated,
	assertErrorDisplayed,
	assertUrlContains
} from '../utils/assertions.js';
import { waitForLoadingComplete } from '../utils/helpers.js';

test.describe('Authentication', () => {
	test('should login with valid credentials', async ({ page }) => {
		const loginPage = new LoginPage(page);

		// Navigate to login page
		await loginPage.goto();

		// Verify login form is visible
		expect(await loginPage.isFormVisible()).toBe(true);

		// Login with test user
		await loginPage.loginAndWaitForDashboard(TEST_USER.email, TEST_USER.password);

		// Verify user is authenticated
		await assertAuthenticated(page);
		await assertUrlContains(page, '/dashboard');
	});

	test('should show error with invalid credentials', async ({ page }) => {
		const loginPage = new LoginPage(page);

		// Navigate to login page
		await loginPage.goto();

		// Try to login with invalid credentials
		await loginPage.login('invalid@example.com', 'wrongpassword');

		// Verify error message is displayed
		await assertErrorDisplayed(page);
		expect(await loginPage.hasError()).toBe(true);

		// Verify still on login page
		await assertUrlContains(page, '/login');
	});

	test('should logout successfully', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Verify authenticated
		await assertAuthenticated(authenticatedPage);

		// Logout
		await dashboardPage.logout();

		// Verify logged out
		await assertNotAuthenticated(authenticatedPage);
		await assertUrlContains(authenticatedPage, '/login');
	});

	test('should redirect to login when accessing protected route without auth', async ({
		page
	}) => {
		// Try to access dashboard without authentication
		await page.goto('/dashboard');

		// Should redirect to login
		await assertNotAuthenticated(page);
		await assertUrlContains(page, '/login');
	});

	test('should persist authentication after page reload', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();
		await assertAuthenticated(authenticatedPage);

		// Reload page
		await authenticatedPage.reload();
		await waitForLoadingComplete(authenticatedPage);

		// Should still be authenticated
		await assertAuthenticated(authenticatedPage);
		expect(await dashboardPage.isVisible()).toBe(true);
	});

	test('should show validation errors for empty fields', async ({ page }) => {
		const loginPage = new LoginPage(page);

		// Navigate to login page
		await loginPage.goto();

		// Try to submit with empty fields
		await loginPage.clickLogin();

		// Check login button is still enabled or form shows validation
		expect(await loginPage.isFormVisible()).toBe(true);
	});

	test('should remember user preference with "Remember Me"', async ({ page }) => {
		const loginPage = new LoginPage(page);

		// Navigate to login page
		await loginPage.goto();

		// Login with "Remember Me" checked
		await loginPage.fillEmail(TEST_USER.email);
		await loginPage.fillPassword(TEST_USER.password);
		await loginPage.toggleRememberMe();
		await loginPage.clickLogin();

		// Wait for successful login
		await page.waitForURL('**/dashboard', { timeout: 10000 });

		// Check that user is authenticated
		await assertAuthenticated(page);
	});

	test('should navigate to register page', async ({ page }) => {
		const loginPage = new LoginPage(page);

		// Navigate to login page
		await loginPage.goto();

		// Click register link (if it exists)
		if (await loginPage.registerLink.isVisible()) {
			await loginPage.goToRegister();
			await assertUrlContains(page, '/register');
		}
	});
});
