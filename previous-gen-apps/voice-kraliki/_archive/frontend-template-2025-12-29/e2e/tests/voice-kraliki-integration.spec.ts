import { test, expect } from '../fixtures/auth.fixture.js';
import { LoginPage } from '../pages/LoginPage.js';
import { DashboardPage } from '../pages/DashboardPage.js';
import { CampaignsPage } from '../pages/CampaignsPage.js';
import { VoiceCallsPage } from '../pages/VoiceCallsPage.js';
import { AnalyticsPage } from '../pages/AnalyticsPage.js';
import { VOICE_TEST_DATA } from '../fixtures/test-data.js';

/**
 * Voice by Kraliki Integration Tests
 *
 * These tests verify complete user flows across multiple pages
 * to ensure the application works as an integrated system.
 */
test.describe('Voice by Kraliki Integration Tests', () => {
	test.describe('Full Application Navigation Flow', () => {
		test('should navigate through all main sections', async ({ authenticatedPage }) => {
			// Start at dashboard
			const dashboardPage = new DashboardPage(authenticatedPage);
			await dashboardPage.goto();
			expect(await dashboardPage.isVisible()).toBe(true);

			// Navigate to Campaigns
			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();
			expect(await campaignsPage.isVisible()).toBe(true);

			// Navigate to Voice Calls
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();
			expect(await voiceCallsPage.isVisible()).toBe(true);

			// Navigate to Analytics
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();
			expect(await analyticsPage.isVisible()).toBe(true);
		});

		test('should maintain authentication across navigation', async ({ authenticatedPage }) => {
			const pages = ['/dashboard', '/campaigns', '/calls/outbound', '/analytics'];

			for (const path of pages) {
				await authenticatedPage.goto(path);

				// Should not be redirected to login
				await expect(authenticatedPage).not.toHaveURL(/.*login.*/);

				// Should have access token
				const hasToken = await authenticatedPage.evaluate(() => {
					return localStorage.getItem('accessToken') !== null;
				});
				expect(hasToken).toBe(true);
			}
		});
	});

	test.describe('Campaign to Voice Call Flow', () => {
		test('should configure voice call with campaign data', async ({ authenticatedPage }) => {
			// First view campaigns
			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();
			await campaignsPage.waitForCampaignsLoad();

			// Then configure a voice call
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			// Set up call configuration
			await voiceCallsPage.selectCountry('US');
			await voiceCallsPage.setAIInstructions(VOICE_TEST_DATA.testAIInstructions);
			await voiceCallsPage.setCompanyDetails(
				0,
				VOICE_TEST_DATA.testCompany.name,
				VOICE_TEST_DATA.testCompany.phone
			);

			// Verify configuration is set
			const instructions = await voiceCallsPage.getAIInstructions();
			expect(instructions).toBe(VOICE_TEST_DATA.testAIInstructions);

			const companyInput = authenticatedPage.locator('#company-0');
			await expect(companyInput).toHaveValue(VOICE_TEST_DATA.testCompany.name);
		});
	});

	test.describe('Analytics Dashboard Flow', () => {
		test('should view all analytics tabs', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			// Check Overview tab (default)
			expect(await analyticsPage.isOverviewTabActive()).toBe(true);

			// Switch to Metrics tab
			await analyticsPage.clickMetricsTab();
			expect(await analyticsPage.isMetricsTabActive()).toBe(true);

			// Switch to Health tab
			await analyticsPage.clickHealthTab();
			expect(await analyticsPage.isHealthTabActive()).toBe(true);

			// Switch back to Overview
			await analyticsPage.clickOverviewTab();
			expect(await analyticsPage.isOverviewTabActive()).toBe(true);
		});

		test('should navigate from analytics to agent operations', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			// Click on Agent Operations link
			await analyticsPage.clickAgentOperationsLink();

			// Should be on the agent operations page
			await expect(authenticatedPage).toHaveURL(/.*calls\/agent.*/);
		});
	});

	test.describe('Voice Call Configuration Flow', () => {
		test('should configure all call settings', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();
			await voiceCallsPage.waitForConfigurationLoad();

			// Select country
			await voiceCallsPage.selectCountry('CZ');
			const phoneNumber = await voiceCallsPage.getFromPhoneNumber();
			expect(phoneNumber).toBeTruthy();

			// Select language
			await voiceCallsPage.selectLanguage('en');

			// Set audio mode
			await voiceCallsPage.selectAudioMode('twilio');

			// Toggle de-essing
			await voiceCallsPage.toggleDeEssing();
			expect(await voiceCallsPage.isDeEssingEnabled()).toBe(true);

			// Set AI instructions
			await voiceCallsPage.setAIInstructions('Test instructions');
			expect(await voiceCallsPage.getAIInstructions()).toBe('Test instructions');
		});

		test('should manage multiple target companies', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			// Initially should have 1 company
			const initialCount = await voiceCallsPage.getCompanyCount();
			expect(initialCount).toBeGreaterThanOrEqual(1);

			// Add a company
			await voiceCallsPage.addCompany();
			const afterAddCount = await voiceCallsPage.getCompanyCount();
			expect(afterAddCount).toBe(initialCount + 1);

			// Set details for first company
			await voiceCallsPage.setCompanyDetails(0, 'Company A', '+15551111111');

			// Set details for second company
			await voiceCallsPage.setCompanyDetails(1, 'Company B', '+15552222222');

			// Verify both are set
			const companyA = authenticatedPage.locator('#company-0');
			const companyB = authenticatedPage.locator('#company-1');

			await expect(companyA).toHaveValue('Company A');
			await expect(companyB).toHaveValue('Company B');
		});
	});

	test.describe('Error Recovery Flow', () => {
		test('should recover from campaign load error', async ({ authenticatedPage }) => {
			let callCount = 0;

			// Mock API failure then success
			await authenticatedPage.route('**/api/v1/campaigns**', (route) => {
				callCount++;
				if (callCount === 1) {
					route.fulfill({
						status: 500,
						contentType: 'application/json',
						body: JSON.stringify({ error: 'Server Error' })
					});
				} else {
					route.fulfill({
						status: 200,
						contentType: 'application/json',
						body: JSON.stringify(VOICE_TEST_DATA.campaigns)
					});
				}
			});

			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();

			// Wait for error
			await authenticatedPage.waitForTimeout(2000);

			// Should show error
			const hasError = await campaignsPage.hasError();
			if (hasError) {
				// Click retry
				await campaignsPage.clickRetry();

				// Wait for successful load
				await authenticatedPage.waitForTimeout(2000);

				// Should now show campaigns or empty state (not error)
				const stillHasError = await campaignsPage.hasError();
				expect(stillHasError).toBe(false);
			}
		});

		test('should show validation errors for voice call', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			// Clear all required fields
			await voiceCallsPage.setAIInstructions('');
			await voiceCallsPage.setCompanyDetails(0, '', '');

			// Try to launch call
			await voiceCallsPage.launchCall(0);

			// Should show error
			await authenticatedPage.waitForTimeout(1000);
			const hasError = await voiceCallsPage.hasError();
			expect(hasError).toBe(true);
		});
	});

	test.describe('Responsive Design Flow', () => {
		const viewports = [
			{ name: 'mobile', width: 375, height: 667 },
			{ name: 'tablet', width: 768, height: 1024 },
			{ name: 'desktop', width: 1920, height: 1080 }
		];

		for (const viewport of viewports) {
			test(`should work correctly on ${viewport.name}`, async ({ authenticatedPage }) => {
				await authenticatedPage.setViewportSize({
					width: viewport.width,
					height: viewport.height
				});

				// Test dashboard
				const dashboardPage = new DashboardPage(authenticatedPage);
				await dashboardPage.goto();
				expect(await dashboardPage.isVisible()).toBe(true);

				// Test campaigns
				const campaignsPage = new CampaignsPage(authenticatedPage);
				await campaignsPage.goto();
				expect(await campaignsPage.isVisible()).toBe(true);

				// Test analytics
				const analyticsPage = new AnalyticsPage(authenticatedPage);
				await analyticsPage.goto();
				expect(await analyticsPage.isVisible()).toBe(true);
			});
		}
	});

	test.describe('Data Persistence Flow', () => {
		test('should persist company data across page reloads', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			// Set company details
			const testName = 'Persistent Test Company';
			const testPhone = '+15559999999';
			await voiceCallsPage.setCompanyDetails(0, testName, testPhone);

			// Wait for localStorage save
			await authenticatedPage.waitForTimeout(500);

			// Reload page
			await authenticatedPage.reload();
			await voiceCallsPage.waitForPageLoad();

			// Wait for hydration
			await authenticatedPage.waitForTimeout(500);

			// Verify data is restored
			const companyInput = authenticatedPage.locator('#company-0');
			const phoneInput = authenticatedPage.locator('#phone-0');

			await expect(companyInput).toHaveValue(testName);
			await expect(phoneInput).toHaveValue(testPhone);
		});
	});

	test.describe('Session State Flow', () => {
		test('should show correct session status on voice calls page', async ({
			authenticatedPage
		}) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			// Session should be in idle/disconnected state initially
			const status = await voiceCallsPage.getSessionStatus();
			expect(status).toBeTruthy();

			// Provider should be shown
			const provider = await voiceCallsPage.getCurrentProvider();
			expect(provider).toBeTruthy();
		});

		test('should display call status description', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const description = await voiceCallsPage.getCallStatusDescription();
			expect(description).toBeTruthy();
		});
	});

	test.describe('Complete User Journey', () => {
		test('should complete a full user session flow', async ({ authenticatedPage }) => {
			// 1. Start at dashboard
			const dashboardPage = new DashboardPage(authenticatedPage);
			await dashboardPage.goto();
			expect(await dashboardPage.isVisible()).toBe(true);

			// 2. View campaigns
			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();
			expect(await campaignsPage.isVisible()).toBe(true);

			// 3. Go to voice calls and configure
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await voiceCallsPage.selectCountry('US');
			await voiceCallsPage.setAIInstructions('Professional sales call');
			await voiceCallsPage.setCompanyDetails(0, 'Test Company', '+15551234567');

			// Verify configuration
			expect(await voiceCallsPage.getAIInstructions()).toBe('Professional sales call');

			// 4. Check analytics
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			// View all tabs
			await analyticsPage.clickOverviewTab();
			await analyticsPage.clickMetricsTab();
			await analyticsPage.clickHealthTab();

			// 5. Return to dashboard
			await dashboardPage.goto();
			expect(await dashboardPage.isVisible()).toBe(true);
		});
	});
});
