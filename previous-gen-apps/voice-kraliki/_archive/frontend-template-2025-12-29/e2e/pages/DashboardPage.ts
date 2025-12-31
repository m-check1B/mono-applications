import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for Dashboard Page
 * Handles all interactions with the main dashboard
 */
export class DashboardPage {
	readonly page: Page;

	// Navigation locators
	readonly navigationMenu: Locator;
	readonly dashboardLink: Locator;
	readonly callsLink: Locator;
	readonly analyticsLink: Locator;
	readonly settingsLink: Locator;
	readonly complianceLink: Locator;

	// User profile locators
	readonly userProfile: Locator;
	readonly userAvatar: Locator;
	readonly userEmail: Locator;
	readonly userName: Locator;
	readonly logoutButton: Locator;

	// Call-related locators
	readonly callButton: Locator;
	readonly startCallButton: Locator;
	readonly callList: Locator;
	readonly callHistoryTable: Locator;
	readonly recentCallsSection: Locator;

	// Dashboard content locators
	readonly welcomeMessage: Locator;
	readonly statsCards: Locator;
	readonly loadingSpinner: Locator;

	constructor(page: Page) {
		this.page = page;

		// Navigation
		this.navigationMenu = page.locator('nav, [role="navigation"]');
		this.dashboardLink = page.locator('a[href*="dashboard"]');
		this.callsLink = page.locator('a[href*="calls"]');
		this.analyticsLink = page.locator('a[href*="analytics"]');
		this.settingsLink = page.locator('a[href*="settings"]');
		this.complianceLink = page.locator('a[href*="compliance"]');

		// User profile
		this.userProfile = page.locator('[data-testid="user-profile"], .user-profile');
		this.userAvatar = page.locator('[data-testid="user-avatar"], .user-avatar');
		this.userEmail = page.locator('[data-testid="user-email"]');
		this.userName = page.locator('[data-testid="user-name"]');
		this.logoutButton = page.locator('button:has-text("Logout"), button:has-text("Sign out")');

		// Call buttons
		this.callButton = page.locator(
			'button:has-text("Call"), button:has-text("Start Call"), [data-testid="call-button"]'
		);
		this.startCallButton = page.locator(
			'button:has-text("Start Call"), [data-testid="start-call"]'
		);
		this.callList = page.locator('[data-testid="call-list"], .call-list');
		this.callHistoryTable = page.locator('table[data-testid="call-history"], .call-history');
		this.recentCallsSection = page.locator('[data-testid="recent-calls"]');

		// Dashboard content
		this.welcomeMessage = page.locator('h1, [data-testid="welcome-message"]');
		this.statsCards = page.locator('[data-testid="stats-card"], .stats-card');
		this.loadingSpinner = page.locator('[data-testid="loading"], .loading, .spinner');
	}

	/**
	 * Navigate to dashboard
	 */
	async goto(): Promise<void> {
		await this.page.goto('/dashboard');
		await this.waitForPageLoad();
	}

	/**
	 * Wait for dashboard to fully load
	 */
	async waitForPageLoad(): Promise<void> {
		// Wait for navigation menu to be visible
		await expect(this.navigationMenu).toBeVisible({ timeout: 10000 });

		// Wait for any loading spinners to disappear
		await this.waitForLoadingComplete();
	}

	/**
	 * Wait for all loading spinners to disappear
	 */
	async waitForLoadingComplete(): Promise<void> {
		try {
			// Wait for loading spinner to appear and disappear
			await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 15000 });
		} catch {
			// If no spinner found, that's okay - page might load instantly
		}
	}

	/**
	 * Check if dashboard is visible
	 */
	async isVisible(): Promise<boolean> {
		try {
			await expect(this.navigationMenu).toBeVisible({ timeout: 5000 });
			const currentUrl = this.page.url();
			return currentUrl.includes('/dashboard');
		} catch {
			return false;
		}
	}

	/**
	 * Check if user is authenticated on dashboard
	 */
	async isAuthenticated(): Promise<boolean> {
		const hasToken = await this.page.evaluate(() => {
			return localStorage.getItem('accessToken') !== null;
		});

		const isOnDashboard = await this.isVisible();
		return hasToken && isOnDashboard;
	}

	/**
	 * Get user information displayed on dashboard
	 */
	async getUserInfo(): Promise<{ name: string; email: string }> {
		let name = '';
		let email = '';

		try {
			if (await this.userName.isVisible()) {
				name = (await this.userName.textContent()) || '';
			}
		} catch {
			// Name might not be visible
		}

		try {
			if (await this.userEmail.isVisible()) {
				email = (await this.userEmail.textContent()) || '';
			}
		} catch {
			// Email might not be visible
		}

		return { name: name.trim(), email: email.trim() };
	}

	/**
	 * Click the call button to initiate a call
	 */
	async startCall(): Promise<void> {
		const button = await this.callButton.first();
		await button.click();
	}

	/**
	 * Navigate to calls page
	 */
	async viewCalls(): Promise<void> {
		await this.callsLink.click();
		await this.page.waitForURL('**/calls', { timeout: 5000 });
	}

	/**
	 * Navigate to analytics page
	 */
	async viewAnalytics(): Promise<void> {
		await this.analyticsLink.click();
		await this.page.waitForURL('**/analytics', { timeout: 5000 });
	}

	/**
	 * Navigate to settings page
	 */
	async goToSettings(): Promise<void> {
		await this.settingsLink.click();
		await this.page.waitForURL('**/settings', { timeout: 5000 });
	}

	/**
	 * Navigate to compliance page
	 */
	async goToCompliance(): Promise<void> {
		if (await this.complianceLink.isVisible()) {
			await this.complianceLink.click();
			await this.page.waitForURL('**/compliance', { timeout: 5000 });
		}
	}

	/**
	 * Logout from dashboard
	 */
	async logout(): Promise<void> {
		// Open user menu if it exists
		if (await this.userProfile.isVisible()) {
			await this.userProfile.click();
		}

		// Click logout button
		await this.logoutButton.click();

		// Wait for redirect to login
		await this.page.waitForURL('**/auth/login', { timeout: 5000 });
	}

	/**
	 * Get recent calls count
	 */
	async getRecentCallsCount(): Promise<number> {
		try {
			if (await this.recentCallsSection.isVisible()) {
				const calls = await this.callList.locator('> *').count();
				return calls;
			}
		} catch {
			// Section might not exist
		}
		return 0;
	}

	/**
	 * Check if call history is visible
	 */
	async hasCallHistory(): Promise<boolean> {
		try {
			await expect(this.callHistoryTable).toBeVisible({ timeout: 3000 });
			const rowCount = await this.callHistoryTable.locator('tbody tr').count();
			return rowCount > 0;
		} catch {
			return false;
		}
	}

	/**
	 * Get statistics from dashboard cards
	 */
	async getStatistics(): Promise<Record<string, string>> {
		const stats: Record<string, string> = {};

		try {
			const cards = await this.statsCards.all();

			for (const card of cards) {
				const label = await card.locator('[data-testid="stat-label"]').textContent();
				const value = await card.locator('[data-testid="stat-value"]').textContent();

				if (label && value) {
					stats[label.trim()] = value.trim();
				}
			}
		} catch {
			// Stats might not be available
		}

		return stats;
	}

	/**
	 * Wait for specific API response
	 */
	async waitForApiResponse(endpoint: string): Promise<void> {
		await this.page.waitForResponse(
			(response) => response.url().includes(endpoint) && response.status() === 200,
			{ timeout: 10000 }
		);
	}

	/**
	 * Check if welcome message is displayed with user name
	 */
	async hasWelcomeMessage(): Promise<boolean> {
		try {
			await expect(this.welcomeMessage).toBeVisible({ timeout: 3000 });
			return true;
		} catch {
			return false;
		}
	}

	/**
	 * Refresh dashboard data
	 */
	async refresh(): Promise<void> {
		await this.page.reload();
		await this.waitForPageLoad();
	}

	/**
	 * Search in call history (if search functionality exists)
	 */
	async searchCallHistory(query: string): Promise<void> {
		const searchInput = this.page.locator('input[type="search"], input[placeholder*="Search"]');

		if (await searchInput.isVisible()) {
			await searchInput.fill(query);
			await searchInput.press('Enter');
			await this.waitForLoadingComplete();
		}
	}

	/**
	 * Get recent call by index
	 */
	async getRecentCall(index: number): Promise<Record<string, string> | null> {
		try {
			const call = this.callList.locator('> *').nth(index);

			if (!(await call.isVisible())) {
				return null;
			}

			const phoneNumber =
				(await call.locator('[data-testid="call-phone"]').textContent()) || '';
			const duration = (await call.locator('[data-testid="call-duration"]').textContent()) || '';
			const status = (await call.locator('[data-testid="call-status"]').textContent()) || '';

			return {
				phoneNumber: phoneNumber.trim(),
				duration: duration.trim(),
				status: status.trim()
			};
		} catch {
			return null;
		}
	}
}
