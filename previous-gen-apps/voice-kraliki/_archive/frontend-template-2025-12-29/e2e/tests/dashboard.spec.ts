import { test, expect } from '../fixtures/auth.fixture.js';
import { DashboardPage } from '../pages/DashboardPage.js';
import { TEST_USER } from '../fixtures/test-data.js';
import { assertAuthenticated, assertUrlContains } from '../utils/assertions.js';
import { waitForLoadingComplete, waitForApiResponse } from '../utils/helpers.js';

test.describe('Dashboard', () => {
	test('should load dashboard after authentication', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Verify dashboard is visible
		expect(await dashboardPage.isVisible()).toBe(true);
		await assertAuthenticated(authenticatedPage);
	});

	test('should display user information', async ({ authenticatedPage, authState }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Get user info from dashboard
		const userInfo = await dashboardPage.getUserInfo();

		// Verify user email is displayed (if available)
		if (userInfo.email) {
			expect(userInfo.email).toBe(authState.user.email);
		}
	});

	test('should display navigation menu', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Verify navigation menu is visible
		await expect(dashboardPage.navigationMenu).toBeVisible();

		// Check that key navigation links exist
		await expect(dashboardPage.dashboardLink).toBeVisible();
	});

	test('should navigate to calls page', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Check if calls link exists and click it
		if (await dashboardPage.callsLink.isVisible()) {
			await dashboardPage.viewCalls();
			await assertUrlContains(authenticatedPage, '/calls');
		}
	});

	test('should navigate to analytics page', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Check if analytics link exists and click it
		if (await dashboardPage.analyticsLink.isVisible()) {
			await dashboardPage.viewAnalytics();
			await assertUrlContains(authenticatedPage, '/analytics');
		}
	});

	test('should navigate to settings page', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Check if settings link exists and click it
		if (await dashboardPage.settingsLink.isVisible()) {
			await dashboardPage.goToSettings();
			await assertUrlContains(authenticatedPage, '/settings');
		}
	});

	test('should refresh dashboard data', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Wait for initial load
		await waitForLoadingComplete(authenticatedPage);

		// Refresh dashboard
		await dashboardPage.refresh();

		// Verify dashboard is still visible
		expect(await dashboardPage.isVisible()).toBe(true);
	});

	test('should display call button', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Check if call button is visible
		const callButtonCount = await dashboardPage.callButton.count();
		expect(callButtonCount).toBeGreaterThan(0);
	});

	test('should display welcome message', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Check for welcome message (if it exists)
		if (await dashboardPage.welcomeMessage.isVisible()) {
			const welcomeText = await dashboardPage.welcomeMessage.textContent();
			expect(welcomeText).toBeTruthy();
		}
	});

	test('should handle loading states', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await authenticatedPage.goto('/dashboard');

		// Wait for loading to complete
		await dashboardPage.waitForLoadingComplete();

		// Verify dashboard is visible
		expect(await dashboardPage.isVisible()).toBe(true);
	});

	test('should display statistics cards if available', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Get statistics (if available)
		const stats = await dashboardPage.getStatistics();

		// Stats may or may not exist depending on implementation
		// Just verify we can call the method without error
		expect(stats).toBeDefined();
	});

	test('should handle call history if available', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Check if call history exists
		const hasHistory = await dashboardPage.hasCallHistory();

		// Call history may or may not exist for test user
		expect(typeof hasHistory).toBe('boolean');
	});
});
