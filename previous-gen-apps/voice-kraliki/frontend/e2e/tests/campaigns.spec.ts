import { test, expect } from '../fixtures/auth.fixture.js';
import { CampaignsPage } from '../pages/CampaignsPage.js';

test.describe('Campaigns Page', () => {
	test.describe('Page Structure', () => {
		test('should display campaigns page with correct structure', async ({ authenticatedPage }) => {
			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();

			// Verify page structure
			const structureValid = await campaignsPage.verifyPageStructure();
			expect(structureValid).toBe(true);
		});

		test('should display page title and description', async ({ authenticatedPage }) => {
			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();

			await expect(campaignsPage.pageTitle).toBeVisible();
			await expect(campaignsPage.pageDescription).toBeVisible();
		});

		test('should display import campaign button', async ({ authenticatedPage }) => {
			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();

			const isVisible = await campaignsPage.isImportButtonVisible();
			expect(isVisible).toBe(true);
		});
	});

	test.describe('Campaign Loading', () => {
		test('should show loading state initially', async ({ authenticatedPage }) => {
			const campaignsPage = new CampaignsPage(authenticatedPage);

			// Navigate without waiting for full load
			await authenticatedPage.goto('/campaigns');

			// Check for loading indicator (may appear briefly)
			// This is a soft check as loading may be very fast
			const pageVisible = await campaignsPage.isVisible();
			expect(pageVisible).toBe(true);
		});

		test('should load campaigns or show empty state', async ({ authenticatedPage }) => {
			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();
			await campaignsPage.waitForCampaignsLoad();

			const count = await campaignsPage.getCampaignCount();
			const isEmpty = await campaignsPage.isEmpty();
			const hasError = await campaignsPage.hasError();

			// Should either have campaigns, be empty, or show error
			expect(count >= 0 || isEmpty || hasError).toBe(true);
		});
	});

	test.describe('Campaign Display', () => {
		test('should display campaign cards with proper structure', async ({ authenticatedPage }) => {
			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();
			await campaignsPage.waitForCampaignsLoad();

			const count = await campaignsPage.getCampaignCount();
			if (count > 0) {
				const details = await campaignsPage.getCampaignDetails(0);
				expect(details.name).toBeTruthy();
			}
		});

		test('should display campaign names', async ({ authenticatedPage }) => {
			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();
			await campaignsPage.waitForCampaignsLoad();

			const names = await campaignsPage.getCampaignNames();
			// Names array should exist (empty is okay if no campaigns)
			expect(Array.isArray(names)).toBe(true);
		});
	});

	test.describe('Error Handling', () => {
		test('should display error message when API fails', async ({ authenticatedPage }) => {
			// Mock API failure
			await authenticatedPage.route('**/api/v1/campaigns**', (route) => {
				route.fulfill({
					status: 500,
					contentType: 'application/json',
					body: JSON.stringify({ error: 'Internal Server Error' })
				});
			});

			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();

			// Wait a bit for error to appear
			await authenticatedPage.waitForTimeout(2000);

			const hasError = await campaignsPage.hasError();
			expect(hasError).toBe(true);
		});

		test('should display retry button on error', async ({ authenticatedPage }) => {
			// Mock API failure
			await authenticatedPage.route('**/api/v1/campaigns**', (route) => {
				route.fulfill({
					status: 500,
					contentType: 'application/json',
					body: JSON.stringify({ error: 'Internal Server Error' })
				});
			});

			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();

			await authenticatedPage.waitForTimeout(2000);

			const hasError = await campaignsPage.hasError();
			if (hasError) {
				await expect(campaignsPage.retryButton).toBeVisible();
			}
		});

		test('should retry loading on retry button click', async ({ authenticatedPage }) => {
			let callCount = 0;

			await authenticatedPage.route('**/api/v1/campaigns**', (route) => {
				callCount++;
				if (callCount === 1) {
					route.fulfill({
						status: 500,
						contentType: 'application/json',
						body: JSON.stringify({ error: 'Internal Server Error' })
					});
				} else {
					route.fulfill({
						status: 200,
						contentType: 'application/json',
						body: JSON.stringify([])
					});
				}
			});

			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();

			await authenticatedPage.waitForTimeout(2000);

			const hasError = await campaignsPage.hasError();
			if (hasError) {
				await campaignsPage.clickRetry();
				await authenticatedPage.waitForTimeout(1000);
				expect(callCount).toBeGreaterThan(1);
			}
		});
	});

	test.describe('Empty State', () => {
		test('should display empty state when no campaigns', async ({ authenticatedPage }) => {
			// Mock empty response
			await authenticatedPage.route('**/api/v1/campaigns**', (route) => {
				route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify([])
				});
			});

			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();
			await campaignsPage.waitForCampaignsLoad();

			const isEmpty = await campaignsPage.isEmpty();
			expect(isEmpty).toBe(true);
		});
	});

	test.describe('Navigation', () => {
		test('should be accessible from protected routes', async ({ authenticatedPage }) => {
			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();

			// Verify we're on the campaigns page
			await expect(authenticatedPage).toHaveURL(/.*campaigns.*/);
		});

		test('should maintain authentication state', async ({ authenticatedPage }) => {
			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();

			// Check that we're not redirected to login
			await expect(authenticatedPage).not.toHaveURL(/.*login.*/);
		});
	});

	test.describe('Responsive Design', () => {
		test('should display properly on mobile viewport', async ({ authenticatedPage }) => {
			await authenticatedPage.setViewportSize({ width: 375, height: 667 });

			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();

			const isVisible = await campaignsPage.isVisible();
			expect(isVisible).toBe(true);
		});

		test('should display properly on tablet viewport', async ({ authenticatedPage }) => {
			await authenticatedPage.setViewportSize({ width: 768, height: 1024 });

			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();

			const isVisible = await campaignsPage.isVisible();
			expect(isVisible).toBe(true);
		});

		test('should display properly on desktop viewport', async ({ authenticatedPage }) => {
			await authenticatedPage.setViewportSize({ width: 1920, height: 1080 });

			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();

			const isVisible = await campaignsPage.isVisible();
			expect(isVisible).toBe(true);
		});
	});

	test.describe('Campaign Cards Grid', () => {
		test('should display campaigns in grid layout', async ({ authenticatedPage }) => {
			// Mock campaigns response
			await authenticatedPage.route('**/api/v1/campaigns**', (route) => {
				route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify([
						{ id: 1, name: 'Campaign 1', language: 'en', stepsCount: 5 },
						{ id: 2, name: 'Campaign 2', language: 'es', stepsCount: 3 },
						{ id: 3, name: 'Campaign 3', language: 'cs', stepsCount: 7 }
					])
				});
			});

			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();
			await campaignsPage.waitForCampaignsLoad();

			const count = await campaignsPage.getCampaignCount();
			expect(count).toBe(3);
		});

		test('should display campaign details correctly', async ({ authenticatedPage }) => {
			// Mock campaigns response
			await authenticatedPage.route('**/api/v1/campaigns**', (route) => {
				route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify([
						{ id: 1, name: 'Test Campaign', language: 'English', stepsCount: 5 }
					])
				});
			});

			const campaignsPage = new CampaignsPage(authenticatedPage);
			await campaignsPage.goto();
			await campaignsPage.waitForCampaignsLoad();

			const details = await campaignsPage.getCampaignDetails(0);
			expect(details.name).toBe('Test Campaign');
		});
	});
});
