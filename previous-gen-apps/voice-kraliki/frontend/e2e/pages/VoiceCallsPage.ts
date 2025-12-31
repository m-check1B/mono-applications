import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for Voice Calls (Outbound) Page
 * Handles all interactions with outbound call orchestration
 */
export class VoiceCallsPage {
	readonly page: Page;

	// Header locators
	readonly pageTitle: Locator;
	readonly pageDescription: Locator;

	// Error display
	readonly errorMessage: Locator;

	// Provider switcher
	readonly providerSwitcher: Locator;

	// Call configuration section
	readonly callConfigCard: Locator;
	readonly countrySelect: Locator;
	readonly fromPhoneNumber: Locator;
	readonly modelSelect: Locator;
	readonly voiceSelect: Locator;
	readonly languageSelect: Locator;
	readonly audioModeSelect: Locator;
	readonly deEssingToggle: Locator;

	// Campaign script section
	readonly campaignScriptCard: Locator;
	readonly campaignButtons: Locator;
	readonly aiInstructionsTextarea: Locator;
	readonly resetSummaryButton: Locator;

	// Target companies section
	readonly targetCompaniesCard: Locator;
	readonly addCompanyButton: Locator;
	readonly companyInputs: Locator;
	readonly phoneInputs: Locator;
	readonly launchCallButtons: Locator;
	readonly stopCallButtons: Locator;
	readonly removeCompanyButtons: Locator;

	// AI Insights panel
	readonly aiInsightsPanel: Locator;

	// Local audio tester
	readonly audioTesterCard: Locator;
	readonly startMicButton: Locator;
	readonly stopAudioButton: Locator;

	// Session monitor
	readonly sessionMonitorCard: Locator;
	readonly latestSummary: Locator;

	// Realtime session
	readonly realtimeSessionCard: Locator;
	readonly connectSessionButton: Locator;
	readonly disconnectButton: Locator;

	constructor(page: Page) {
		this.page = page;

		// Header
		this.pageTitle = page.locator('h1:has-text("Outbound Call Orchestration")');
		this.pageDescription = page.locator('p:has-text("Configure AI voice, language")');

		// Error display
		this.errorMessage = page.locator('.border-error');

		// Provider switcher
		this.providerSwitcher = page.locator('[class*="provider"], :has-text("Google Gemini Live")').first();

		// Call configuration
		this.callConfigCard = page.locator('article.card:has-text("Call Configuration")');
		this.countrySelect = page.locator('#country-select');
		this.fromPhoneNumber = page.locator('#from-number');
		this.modelSelect = page.locator('#model-select');
		this.voiceSelect = page.locator('#voice-select');
		this.languageSelect = page.locator('#language-select');
		this.audioModeSelect = page.locator('#audio-mode');
		this.deEssingToggle = page.locator('input[type="checkbox"]').first();

		// Campaign script
		this.campaignScriptCard = page.locator('article.card:has-text("Campaign Script")');
		this.campaignButtons = page.locator('button:has-text("Insurance"), button:has-text("Solar"), button:has-text("Re-engagement")');
		this.aiInstructionsTextarea = page.locator('textarea');
		this.resetSummaryButton = page.locator('button:has-text("Reset Summary")');

		// Target companies
		this.targetCompaniesCard = page.locator('article.card:has-text("Target Companies")');
		this.addCompanyButton = page.locator('button:has-text("Add company")');
		this.companyInputs = page.locator('input[id^="company-"]');
		this.phoneInputs = page.locator('input[id^="phone-"]');
		this.launchCallButtons = page.locator('button:has-text("Launch Call")');
		this.stopCallButtons = page.locator('button:has-text("Stop")');
		this.removeCompanyButtons = page.locator('button:has(.size-4):has-text("")').filter({ hasText: '' });

		// AI Insights
		this.aiInsightsPanel = page.locator('[class*="AIInsights"], :has-text("AI Insights")').first();

		// Audio tester
		this.audioTesterCard = page.locator('article.card:has-text("Local Audio Tester")');
		this.startMicButton = page.locator('button:has-text("Start microphone")');
		this.stopAudioButton = page.locator('button:has-text("Stop")').nth(1);

		// Session monitor
		this.sessionMonitorCard = page.locator('article.card:has-text("Session Monitor")');
		this.latestSummary = page.locator('text=Latest Summary');

		// Realtime session
		this.realtimeSessionCard = page.locator('article.card:has-text("Realtime Session")');
		this.connectSessionButton = page.locator('button:has-text("Connect session")');
		this.disconnectButton = page.locator('button:has-text("Disconnect")');
	}

	/**
	 * Navigate to the outbound calls page
	 */
	async goto(): Promise<void> {
		await this.page.goto('/calls/outbound');
		await this.waitForPageLoad();
	}

	/**
	 * Wait for page to fully load
	 */
	async waitForPageLoad(): Promise<void> {
		await expect(this.pageTitle).toBeVisible({ timeout: 10000 });
	}

	/**
	 * Check if page is visible
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
	 * Wait for configuration to load
	 */
	async waitForConfigurationLoad(): Promise<void> {
		// Wait for models and voices to load
		await Promise.race([
			this.modelSelect.locator('option').first().waitFor({ timeout: 10000 }),
			this.page.locator('text=Failed to load voice/model configuration').waitFor({ timeout: 10000 })
		]).catch(() => {});
	}

	/**
	 * Select a country
	 */
	async selectCountry(countryCode: string): Promise<void> {
		await this.countrySelect.selectOption(countryCode);
	}

	/**
	 * Get the from phone number
	 */
	async getFromPhoneNumber(): Promise<string> {
		return (await this.fromPhoneNumber.inputValue()) || '';
	}

	/**
	 * Select an AI model
	 */
	async selectModel(modelId: string): Promise<void> {
		await this.modelSelect.selectOption(modelId);
	}

	/**
	 * Select a voice
	 */
	async selectVoice(voiceId: string): Promise<void> {
		await this.voiceSelect.selectOption(voiceId);
	}

	/**
	 * Select a language
	 */
	async selectLanguage(languageCode: string): Promise<void> {
		await this.languageSelect.selectOption(languageCode);
	}

	/**
	 * Select audio mode
	 */
	async selectAudioMode(mode: 'twilio' | 'local'): Promise<void> {
		await this.audioModeSelect.selectOption(mode);
	}

	/**
	 * Toggle de-essing
	 */
	async toggleDeEssing(): Promise<void> {
		await this.deEssingToggle.click();
	}

	/**
	 * Check if de-essing is enabled
	 */
	async isDeEssingEnabled(): Promise<boolean> {
		return await this.deEssingToggle.isChecked();
	}

	/**
	 * Load a campaign script
	 */
	async loadCampaign(campaignName: 'Insurance Renewal' | 'Solar Outreach' | 'Customer Re-engagement'): Promise<void> {
		const button = this.page.locator(`button:has-text("${campaignName.split(' ')[0]}")`);
		await button.click();
		// Wait for script to load
		await this.page.waitForTimeout(1000);
	}

	/**
	 * Set AI instructions
	 */
	async setAIInstructions(instructions: string): Promise<void> {
		await this.aiInstructionsTextarea.fill(instructions);
	}

	/**
	 * Get AI instructions
	 */
	async getAIInstructions(): Promise<string> {
		return (await this.aiInstructionsTextarea.inputValue()) || '';
	}

	/**
	 * Add a new company
	 */
	async addCompany(): Promise<void> {
		await this.addCompanyButton.click();
	}

	/**
	 * Set company details
	 */
	async setCompanyDetails(index: number, name: string, phone: string): Promise<void> {
		const companyInput = this.page.locator(`#company-${index}`);
		const phoneInput = this.page.locator(`#phone-${index}`);
		await companyInput.fill(name);
		await phoneInput.fill(phone);
	}

	/**
	 * Get company count
	 */
	async getCompanyCount(): Promise<number> {
		return await this.companyInputs.count();
	}

	/**
	 * Launch call for a company
	 */
	async launchCall(index: number): Promise<void> {
		const button = this.launchCallButtons.nth(index);
		await button.click();
	}

	/**
	 * Stop call for a company
	 */
	async stopCall(index: number): Promise<void> {
		const button = this.stopCallButtons.nth(index);
		await button.click();
	}

	/**
	 * Remove a company
	 */
	async removeCompany(index: number): Promise<void> {
		const button = this.page.locator(`button:has(svg.size-4)`).nth(index * 3 + 2);
		await button.click();
	}

	/**
	 * Check if error is displayed
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
	 * Get error message
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
	 * Click reset summary button
	 */
	async resetSummary(): Promise<void> {
		await this.resetSummaryButton.click();
	}

	/**
	 * Start microphone
	 */
	async startMicrophone(): Promise<void> {
		await this.startMicButton.click();
	}

	/**
	 * Stop audio
	 */
	async stopAudio(): Promise<void> {
		await this.stopAudioButton.click();
	}

	/**
	 * Connect realtime session
	 */
	async connectSession(): Promise<void> {
		await this.connectSessionButton.click();
	}

	/**
	 * Disconnect realtime session
	 */
	async disconnectSession(): Promise<void> {
		await this.disconnectButton.click();
	}

	/**
	 * Check if session is connected
	 */
	async isSessionConnected(): Promise<boolean> {
		const statusText = await this.realtimeSessionCard.locator('.text-text-muted').first().textContent();
		return statusText?.includes('connected') || false;
	}

	/**
	 * Get session status
	 */
	async getSessionStatus(): Promise<string> {
		const statusText = await this.realtimeSessionCard.locator('.text-text-muted').first().textContent();
		const match = statusText?.match(/Status:\s*(\w+)/);
		return match ? match[1] : '';
	}

	/**
	 * Get call status description
	 */
	async getCallStatusDescription(): Promise<string> {
		const text = await this.sessionMonitorCard.locator('.text-text-muted').first().textContent();
		return text?.trim() || '';
	}

	/**
	 * Check if latest summary is displayed
	 */
	async hasSummary(): Promise<boolean> {
		return await this.latestSummary.isVisible();
	}

	/**
	 * Get available models
	 */
	async getAvailableModels(): Promise<string[]> {
		const options = await this.modelSelect.locator('option').all();
		const models: string[] = [];
		for (const option of options) {
			const text = await option.textContent();
			if (text) models.push(text.trim());
		}
		return models;
	}

	/**
	 * Get available voices
	 */
	async getAvailableVoices(): Promise<string[]> {
		const options = await this.voiceSelect.locator('option').all();
		const voices: string[] = [];
		for (const option of options) {
			const text = await option.textContent();
			if (text) voices.push(text.trim());
		}
		return voices;
	}

	/**
	 * Get available languages
	 */
	async getAvailableLanguages(): Promise<string[]> {
		const options = await this.languageSelect.locator('option').all();
		const languages: string[] = [];
		for (const option of options) {
			const text = await option.textContent();
			if (text) languages.push(text.trim());
		}
		return languages;
	}

	/**
	 * Get current provider
	 */
	async getCurrentProvider(): Promise<string> {
		const text = await this.realtimeSessionCard.locator('.text-text-muted').first().textContent();
		const match = text?.match(/Provider:\s*(\w+)/);
		return match ? match[1] : '';
	}

	/**
	 * Verify page structure
	 */
	async verifyPageStructure(): Promise<boolean> {
		try {
			await expect(this.pageTitle).toBeVisible();
			await expect(this.callConfigCard).toBeVisible();
			await expect(this.campaignScriptCard).toBeVisible();
			await expect(this.targetCompaniesCard).toBeVisible();
			return true;
		} catch {
			return false;
		}
	}

	/**
	 * Wait for API response
	 */
	async waitForCallApiResponse(): Promise<void> {
		await this.page.waitForResponse(
			(response) => response.url().includes('/api/') && response.status() === 200
		);
	}
}
