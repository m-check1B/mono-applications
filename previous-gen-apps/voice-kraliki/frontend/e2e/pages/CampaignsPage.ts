import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for Campaigns Page
 * Handles all interactions with campaign management
 */
export class CampaignsPage {
	readonly page: Page;

	// Locators
	readonly pageTitle: Locator;
	readonly pageDescription: Locator;
	readonly importButton: Locator;
	readonly campaignCards: Locator;
	readonly loadingIndicator: Locator;
	readonly errorMessage: Locator;
	readonly retryButton: Locator;
	readonly emptyState: Locator;

	constructor(page: Page) {
		this.page = page;

		// Initialize locators based on the actual component structure
		this.pageTitle = page.locator('h1:has-text("Campaign Library")');
		this.pageDescription = page.locator('p:has-text("Manage AI-driven calling campaigns")');
		this.importButton = page.locator('button:has-text("Import Campaign")');
		this.campaignCards = page.locator('article.card');
		this.loadingIndicator = page.locator('text=Loading campaigns');
		this.errorMessage = page.locator('.border-error');
		this.retryButton = page.locator('button:has-text("Retry")');
		this.emptyState = page.locator('text=No campaigns found');
	}

	/**
	 * Navigate to the campaigns page
	 */
	async goto(): Promise<void> {
		await this.page.goto('/campaigns');
		await this.waitForPageLoad();
	}

	/**
	 * Wait for campaigns page to fully load
	 */
	async waitForPageLoad(): Promise<void> {
		await expect(this.pageTitle).toBeVisible({ timeout: 10000 });
	}

	/**
	 * Check if campaigns page is visible
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
	 * Wait for campaigns to load
	 */
	async waitForCampaignsLoad(): Promise<void> {
		// Wait for either campaigns to appear, empty state, or error
		await Promise.race([
			this.campaignCards.first().waitFor({ timeout: 10000 }).catch(() => {}),
			this.emptyState.waitFor({ timeout: 10000 }).catch(() => {}),
			this.errorMessage.waitFor({ timeout: 10000 }).catch(() => {})
		]);
	}

	/**
	 * Check if loading indicator is visible
	 */
	async isLoading(): Promise<boolean> {
		return await this.loadingIndicator.isVisible();
	}

	/**
	 * Get the number of campaign cards
	 */
	async getCampaignCount(): Promise<number> {
		await this.waitForCampaignsLoad();
		return await this.campaignCards.count();
	}

	/**
	 * Check if error message is displayed
	 */
	async hasError(): Promise<boolean> {
		try {
			await expect(this.errorMessage).toBeVisible({ timeout: 3000 });
			return true;
		} catch {
			return false;
		}
	}

	/**
	 * Get error message text
	 */
	async getErrorMessage(): Promise<string> {
		try {
			await expect(this.errorMessage).toBeVisible({ timeout: 5000 });
			return (await this.errorMessage.textContent()) || '';
		} catch {
			return '';
		}
	}

	/**
	 * Click retry button on error
	 */
	async clickRetry(): Promise<void> {
		await this.retryButton.click();
	}

	/**
	 * Check if empty state is displayed
	 */
	async isEmpty(): Promise<boolean> {
		try {
			await expect(this.emptyState).toBeVisible({ timeout: 3000 });
			return true;
		} catch {
			return false;
		}
	}

	/**
	 * Click import campaign button
	 */
	async clickImportCampaign(): Promise<void> {
		await this.importButton.click();
	}

	/**
	 * Get campaign card by name
	 */
	getCampaignCard(name: string): Locator {
		return this.page.locator(`article.card:has-text("${name}")`);
	}

	/**
	 * Get campaign names from cards
	 */
	async getCampaignNames(): Promise<string[]> {
		await this.waitForCampaignsLoad();
		const cards = await this.campaignCards.all();
		const names: string[] = [];
		for (const card of cards) {
			const nameElement = card.locator('h2');
			const name = await nameElement.textContent();
			if (name) names.push(name.trim());
		}
		return names;
	}

	/**
	 * Get campaign details from a card
	 */
	async getCampaignDetails(index: number): Promise<{ name: string; language: string; steps: string }> {
		const card = this.campaignCards.nth(index);
		const name = (await card.locator('h2').textContent()) || '';
		const listItems = await card.locator('li').all();

		let language = '';
		let steps = '';

		for (const item of listItems) {
			const text = (await item.textContent()) || '';
			if (text.includes('Language:')) {
				language = text.replace('Language:', '').trim();
			}
			if (text.includes('Steps:')) {
				steps = text.replace('Steps:', '').trim();
			}
		}

		return { name: name.trim(), language, steps };
	}

	/**
	 * Wait for API response
	 */
	async waitForCampaignsApiResponse(): Promise<void> {
		await this.page.waitForResponse(
			(response) => response.url().includes('/api/v1/campaigns') && response.status() === 200
		);
	}

	/**
	 * Click on a campaign card
	 */
	async clickCampaign(name: string): Promise<void> {
		const card = this.getCampaignCard(name);
		await card.click();
	}

	/**
	 * Check if import button is visible
	 */
	async isImportButtonVisible(): Promise<boolean> {
		return await this.importButton.isVisible();
	}

	/**
	 * Verify page structure
	 */
	async verifyPageStructure(): Promise<boolean> {
		try {
			await expect(this.pageTitle).toBeVisible();
			await expect(this.pageDescription).toBeVisible();
			await expect(this.importButton).toBeVisible();
			return true;
		} catch {
			return false;
		}
	}
}
