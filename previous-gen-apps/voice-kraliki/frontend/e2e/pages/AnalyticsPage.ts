import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for Analytics Page
 * Handles all interactions with analytics dashboard
 */
export class AnalyticsPage {
	readonly page: Page;

	// Header locators
	readonly pageTitle: Locator;
	readonly pageDescription: Locator;

	// Tab navigation locators
	readonly tabNavigation: Locator;
	readonly overviewTab: Locator;
	readonly metricsTab: Locator;
	readonly healthTab: Locator;

	// Tab content locators
	readonly tabContent: Locator;
	readonly activeTabPanel: Locator;

	// Info cards
	readonly infoCards: Locator;

	// Dashboard components
	readonly enhancedDashboard: Locator;
	readonly providerMetrics: Locator;
	readonly providerHealth: Locator;

	// Loading states
	readonly loadingIndicator: Locator;

	constructor(page: Page) {
		this.page = page;

		// Header
		this.pageTitle = page.locator('h1:has-text("Analytics & Insights")');
		this.pageDescription = page.locator('p:has-text("Real-time monitoring")');

		// Tab navigation
		this.tabNavigation = page.locator('.tab-navigation');
		this.overviewTab = page.locator('button:has-text("Overview")');
		this.metricsTab = page.locator('button:has-text("Metrics & Charts")');
		this.healthTab = page.locator('button:has-text("Provider Health")');

		// Tab content
		this.tabContent = page.locator('.tab-content');
		this.activeTabPanel = page.locator('.tab-panel');

		// Info cards
		this.infoCards = page.locator('.info-card');

		// Dashboard components (based on actual component names)
		this.enhancedDashboard = page.locator('[data-tab="overview"]');
		this.providerMetrics = page.locator('[data-tab="metrics"]');
		this.providerHealth = page.locator('[data-tab="health"]');

		// Loading states
		this.loadingIndicator = page.locator('text=Loading');
	}

	/**
	 * Navigate to the analytics page
	 */
	async goto(): Promise<void> {
		await this.page.goto('/analytics');
		await this.waitForPageLoad();
	}

	/**
	 * Wait for analytics page to fully load
	 */
	async waitForPageLoad(): Promise<void> {
		await expect(this.pageTitle).toBeVisible({ timeout: 10000 });
		await expect(this.tabNavigation).toBeVisible({ timeout: 10000 });
	}

	/**
	 * Check if analytics page is visible
	 */
	async isVisible(): Promise<boolean> {
		try {
			await expect(this.pageTitle).toBeVisible({ timeout: 5000 });
			return true;
		} catch {
			return false;
		}
	}

	/**
	 * Get active tab name
	 */
	async getActiveTab(): Promise<string> {
		const activeButton = this.tabNavigation.locator('button.active');
		const label = await activeButton.locator('.tab-label').textContent();
		return label?.trim() || '';
	}

	/**
	 * Click on Overview tab
	 */
	async clickOverviewTab(): Promise<void> {
		await this.overviewTab.click();
		await expect(this.enhancedDashboard).toBeVisible({ timeout: 5000 });
	}

	/**
	 * Click on Metrics tab
	 */
	async clickMetricsTab(): Promise<void> {
		await this.metricsTab.click();
		await expect(this.providerMetrics).toBeVisible({ timeout: 5000 });
	}

	/**
	 * Click on Health tab
	 */
	async clickHealthTab(): Promise<void> {
		await this.healthTab.click();
		await expect(this.providerHealth).toBeVisible({ timeout: 5000 });
	}

	/**
	 * Check if Overview tab is active
	 */
	async isOverviewTabActive(): Promise<boolean> {
		return await this.overviewTab.evaluate((el) => el.classList.contains('active'));
	}

	/**
	 * Check if Metrics tab is active
	 */
	async isMetricsTabActive(): Promise<boolean> {
		return await this.metricsTab.evaluate((el) => el.classList.contains('active'));
	}

	/**
	 * Check if Health tab is active
	 */
	async isHealthTabActive(): Promise<boolean> {
		return await this.healthTab.evaluate((el) => el.classList.contains('active'));
	}

	/**
	 * Get number of info cards
	 */
	async getInfoCardCount(): Promise<number> {
		return await this.infoCards.count();
	}

	/**
	 * Get info card titles
	 */
	async getInfoCardTitles(): Promise<string[]> {
		const cards = await this.infoCards.all();
		const titles: string[] = [];
		for (const card of cards) {
			const title = await card.locator('.info-title').textContent();
			if (title) titles.push(title.trim());
		}
		return titles;
	}

	/**
	 * Check if loading indicator is visible
	 */
	async isLoading(): Promise<boolean> {
		return await this.loadingIndicator.isVisible();
	}

	/**
	 * Wait for dashboard data to load
	 */
	async waitForDataLoad(): Promise<void> {
		// Wait for loading to finish
		await this.page.waitForFunction(
			() => !document.querySelector('.loading, [class*="loading"]'),
			{ timeout: 15000 }
		).catch(() => {});
	}

	/**
	 * Verify all tabs are visible
	 */
	async verifyTabsVisible(): Promise<boolean> {
		try {
			await expect(this.overviewTab).toBeVisible();
			await expect(this.metricsTab).toBeVisible();
			await expect(this.healthTab).toBeVisible();
			return true;
		} catch {
			return false;
		}
	}

	/**
	 * Switch to tab and verify content
	 */
	async switchToTab(tabName: 'overview' | 'metrics' | 'health'): Promise<void> {
		switch (tabName) {
			case 'overview':
				await this.clickOverviewTab();
				break;
			case 'metrics':
				await this.clickMetricsTab();
				break;
			case 'health':
				await this.clickHealthTab();
				break;
		}
	}

	/**
	 * Check if tab content is animating
	 */
	async isTabContentAnimating(): Promise<boolean> {
		const tabPanel = this.page.locator('.tab-panel');
		return await tabPanel.evaluate((el) => {
			const style = window.getComputedStyle(el);
			return style.animationName !== 'none';
		});
	}

	/**
	 * Get page header text
	 */
	async getPageHeader(): Promise<{ title: string; description: string }> {
		const title = (await this.pageTitle.textContent()) || '';
		const description = (await this.pageDescription.textContent()) || '';
		return { title: title.trim(), description: description.trim() };
	}

	/**
	 * Verify page structure
	 */
	async verifyPageStructure(): Promise<boolean> {
		try {
			await expect(this.pageTitle).toBeVisible();
			await expect(this.pageDescription).toBeVisible();
			await expect(this.tabNavigation).toBeVisible();
			await expect(this.tabContent).toBeVisible();
			return true;
		} catch {
			return false;
		}
	}

	/**
	 * Click on Agent Operations link in info card
	 */
	async clickAgentOperationsLink(): Promise<void> {
		const link = this.page.locator('a[href="/calls/agent"]');
		await link.click();
		await this.page.waitForURL('**/calls/agent');
	}

	/**
	 * Wait for auto-refresh
	 */
	async waitForAutoRefresh(timeoutMs: number = 35000): Promise<void> {
		// Wait for a bit longer than the 30s refresh interval
		await this.page.waitForTimeout(timeoutMs);
	}
}
