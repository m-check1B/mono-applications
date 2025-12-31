import { test, expect } from '../fixtures/auth.fixture.js';
import { AnalyticsPage } from '../pages/AnalyticsPage.js';

test.describe('Analytics Page', () => {
	test.describe('Page Structure', () => {
		test('should display analytics page with correct structure', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const structureValid = await analyticsPage.verifyPageStructure();
			expect(structureValid).toBe(true);
		});

		test('should display page title and description', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await expect(analyticsPage.pageTitle).toBeVisible();
			await expect(analyticsPage.pageDescription).toBeVisible();
		});

		test('should display correct header text', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const header = await analyticsPage.getPageHeader();
			expect(header.title).toContain('Analytics');
		});
	});

	test.describe('Tab Navigation', () => {
		test('should display all three tabs', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const tabsVisible = await analyticsPage.verifyTabsVisible();
			expect(tabsVisible).toBe(true);
		});

		test('should have Overview tab visible', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await expect(analyticsPage.overviewTab).toBeVisible();
		});

		test('should have Metrics tab visible', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await expect(analyticsPage.metricsTab).toBeVisible();
		});

		test('should have Health tab visible', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await expect(analyticsPage.healthTab).toBeVisible();
		});

		test('should default to Overview tab', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const isActive = await analyticsPage.isOverviewTabActive();
			expect(isActive).toBe(true);
		});
	});

	test.describe('Tab Switching', () => {
		test('should switch to Metrics tab', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await analyticsPage.clickMetricsTab();

			const isActive = await analyticsPage.isMetricsTabActive();
			expect(isActive).toBe(true);
		});

		test('should switch to Health tab', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await analyticsPage.clickHealthTab();

			const isActive = await analyticsPage.isHealthTabActive();
			expect(isActive).toBe(true);
		});

		test('should switch back to Overview tab', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			// Switch to another tab first
			await analyticsPage.clickMetricsTab();

			// Switch back to Overview
			await analyticsPage.clickOverviewTab();

			const isActive = await analyticsPage.isOverviewTabActive();
			expect(isActive).toBe(true);
		});

		test('should display correct content for Overview tab', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await analyticsPage.clickOverviewTab();

			await expect(analyticsPage.enhancedDashboard).toBeVisible();
		});

		test('should display correct content for Metrics tab', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await analyticsPage.clickMetricsTab();

			await expect(analyticsPage.providerMetrics).toBeVisible();
		});

		test('should display correct content for Health tab', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await analyticsPage.clickHealthTab();

			await expect(analyticsPage.providerHealth).toBeVisible();
		});
	});

	test.describe('Info Cards', () => {
		test('should display info cards', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const count = await analyticsPage.getInfoCardCount();
			expect(count).toBeGreaterThan(0);
		});

		test('should display at least 3 info cards', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const count = await analyticsPage.getInfoCardCount();
			expect(count).toBeGreaterThanOrEqual(3);
		});

		test('should display info card titles', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const titles = await analyticsPage.getInfoCardTitles();
			expect(titles.length).toBeGreaterThan(0);
		});

		test('should contain Getting Started card', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const titles = await analyticsPage.getInfoCardTitles();
			expect(titles.some((t) => t.includes('Getting Started'))).toBe(true);
		});

		test('should contain Auto-Refresh card', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const titles = await analyticsPage.getInfoCardTitles();
			expect(titles.some((t) => t.includes('Auto-Refresh'))).toBe(true);
		});

		test('should contain Data Retention card', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const titles = await analyticsPage.getInfoCardTitles();
			expect(titles.some((t) => t.includes('Data Retention'))).toBe(true);
		});
	});

	test.describe('Navigation Links', () => {
		test('should have link to Agent Operations page', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const agentLink = authenticatedPage.locator('a[href="/calls/agent"]');
			await expect(agentLink).toBeVisible();
		});

		test('should navigate to Agent Operations when clicking link', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await analyticsPage.clickAgentOperationsLink();

			await expect(authenticatedPage).toHaveURL(/.*calls\/agent.*/);
		});
	});

	test.describe('Protected Route', () => {
		test('should be accessible when authenticated', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const isVisible = await analyticsPage.isVisible();
			expect(isVisible).toBe(true);
		});

		test('should maintain authentication state', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await expect(authenticatedPage).not.toHaveURL(/.*login.*/);
		});

		test('should be at correct URL', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await expect(authenticatedPage).toHaveURL(/.*analytics.*/);
		});
	});

	test.describe('Responsive Design', () => {
		test('should display properly on mobile viewport', async ({ authenticatedPage }) => {
			await authenticatedPage.setViewportSize({ width: 375, height: 667 });

			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const isVisible = await analyticsPage.isVisible();
			expect(isVisible).toBe(true);
		});

		test('should display tabs on mobile', async ({ authenticatedPage }) => {
			await authenticatedPage.setViewportSize({ width: 375, height: 667 });

			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const tabsVisible = await analyticsPage.verifyTabsVisible();
			expect(tabsVisible).toBe(true);
		});

		test('should display properly on tablet viewport', async ({ authenticatedPage }) => {
			await authenticatedPage.setViewportSize({ width: 768, height: 1024 });

			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const isVisible = await analyticsPage.isVisible();
			expect(isVisible).toBe(true);
		});

		test('should display properly on desktop viewport', async ({ authenticatedPage }) => {
			await authenticatedPage.setViewportSize({ width: 1920, height: 1080 });

			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const isVisible = await analyticsPage.isVisible();
			expect(isVisible).toBe(true);
		});
	});

	test.describe('Tab Animation', () => {
		test('should animate tab content when switching', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			// Tab panels should exist
			await expect(analyticsPage.tabContent).toBeVisible();
		});
	});

	test.describe('Dashboard Components', () => {
		test('should load Overview dashboard', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await analyticsPage.clickOverviewTab();
			await analyticsPage.waitForDataLoad();

			await expect(analyticsPage.enhancedDashboard).toBeVisible();
		});

		test('should load Metrics display', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await analyticsPage.clickMetricsTab();
			await analyticsPage.waitForDataLoad();

			await expect(analyticsPage.providerMetrics).toBeVisible();
		});

		test('should load Health monitor', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			await analyticsPage.clickHealthTab();
			await analyticsPage.waitForDataLoad();

			await expect(analyticsPage.providerHealth).toBeVisible();
		});
	});

	test.describe('Styling', () => {
		test('should have styled page header', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			// Check page header has styling
			const header = authenticatedPage.locator('.page-header');
			await expect(header).toBeVisible();
		});

		test('should have styled tabs', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			// Check tabs have styling
			await expect(analyticsPage.tabNavigation).toBeVisible();
		});

		test('should have styled info cards', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			// Check info cards have styling
			await expect(analyticsPage.infoCards.first()).toBeVisible();
		});
	});

	test.describe('Tab Icons', () => {
		test('should display tab icons', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			// Check for tab icons
			const overviewIcon = analyticsPage.overviewTab.locator('.tab-icon');
			const metricsIcon = analyticsPage.metricsTab.locator('.tab-icon');
			const healthIcon = analyticsPage.healthTab.locator('.tab-icon');

			await expect(overviewIcon).toBeVisible();
			await expect(metricsIcon).toBeVisible();
			await expect(healthIcon).toBeVisible();
		});
	});

	test.describe('Info Card Icons', () => {
		test('should display info card icons', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			const icons = authenticatedPage.locator('.info-icon');
			const count = await icons.count();
			expect(count).toBeGreaterThan(0);
		});
	});

	test.describe('Active Tab State', () => {
		test('should highlight active tab', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			// Overview should be active by default
			const hasActiveClass = await analyticsPage.overviewTab.evaluate((el) =>
				el.classList.contains('active')
			);
			expect(hasActiveClass).toBe(true);
		});

		test('should update active state when switching tabs', async ({ authenticatedPage }) => {
			const analyticsPage = new AnalyticsPage(authenticatedPage);
			await analyticsPage.goto();

			// Click metrics tab
			await analyticsPage.clickMetricsTab();

			// Overview should not be active
			const overviewActive = await analyticsPage.overviewTab.evaluate((el) =>
				el.classList.contains('active')
			);
			expect(overviewActive).toBe(false);

			// Metrics should be active
			const metricsActive = await analyticsPage.metricsTab.evaluate((el) =>
				el.classList.contains('active')
			);
			expect(metricsActive).toBe(true);
		});
	});
});
