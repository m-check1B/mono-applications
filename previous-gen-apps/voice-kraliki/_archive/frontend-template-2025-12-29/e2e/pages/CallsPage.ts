import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for Calls Page (Outbound)
 * Handles all interactions with the outbound calls interface
 */
export class CallsPage {
	readonly page: Page;

	// Locators - Page Header
	readonly pageTitle: Locator;
	readonly pageDescription: Locator;

	// Locators - Call Configuration
	readonly countrySelect: Locator;
	readonly fromPhoneNumber: Locator;
	readonly modelSelect: Locator;
	readonly voiceSelect: Locator;
	readonly languageSelect: Locator;
	readonly audioModeSelect: Locator;
	readonly deEssingToggle: Locator;

	// Locators - Campaign Instructions
	readonly aiInstructionsTextarea: Locator;
	readonly loadCampaignButtons: Locator;

	// Locators - Target Companies
	readonly companyNameInput: Locator;
	readonly companyPhoneInput: Locator;
	readonly launchCallButton: Locator;
	readonly stopCallButton: Locator;
	readonly addCompanyButton: Locator;
	readonly removeCompanyButton: Locator;

	// Locators - Call Status and Monitoring
	readonly callStatusText: Locator;
	readonly providerIndicator: Locator;
	readonly callDurationCounter: Locator;
	readonly latencyMetrics: Locator;
	readonly connectionQualityIndicator: Locator;
	readonly transcriptContainer: Locator;

	// Locators - Audio Controls
	readonly audioControls: Locator;
	readonly muteButton: Locator;
	readonly volumeControl: Locator;
	readonly startMicrophoneButton: Locator;
	readonly stopMicrophoneButton: Locator;

	// Locators - Provider Switching
	readonly providerSwitcher: Locator;
	readonly providerMenu: Locator;
	readonly switchProviderButton: Locator;

	// Locators - Call Summary
	readonly callSummarySection: Locator;
	readonly callRecording: Locator;
	readonly callHistory: Locator;

	// Locators - Realtime Session
	readonly realtimeSessionStatus: Locator;
	readonly connectSessionButton: Locator;
	readonly disconnectSessionButton: Locator;

	// Locators - Error Messages
	readonly errorMessage: Locator;

	constructor(page: Page) {
		this.page = page;

		// Initialize page header locators
		this.pageTitle = page.locator('h1:has-text("Outbound Call Orchestration")');
		this.pageDescription = page.locator('text=Configure AI voice, language');

		// Initialize configuration locators
		this.countrySelect = page.locator('#country-select, select[name="country"]');
		this.fromPhoneNumber = page.locator('#from-number, input[name="fromPhoneNumber"]');
		this.modelSelect = page.locator('#model-select, select[name="model"]');
		this.voiceSelect = page.locator('#voice-select, select[name="voice"]');
		this.languageSelect = page.locator('#language-select, select[name="language"]');
		this.audioModeSelect = page.locator('#audio-mode, select[name="audioMode"]');
		this.deEssingToggle = page.locator('input[type="checkbox"]').filter({ hasText: /de-essing/i }).or(
			page.locator('label:has-text("De-essing") input[type="checkbox"]')
		);

		// Initialize campaign locators
		this.aiInstructionsTextarea = page.locator('textarea.textarea-field, textarea[placeholder*="AI instructions"]');
		this.loadCampaignButtons = page.locator('button:has-text("Insurance Renewal"), button:has-text("Solar Outreach")');

		// Initialize target company locators
		this.companyNameInput = page.locator('input[id^="company-"]').first();
		this.companyPhoneInput = page.locator('input[id^="phone-"]').first();
		this.launchCallButton = page.locator('button:has-text("Launch Call")').first();
		this.stopCallButton = page.locator('button:has-text("Stop")').first();
		this.addCompanyButton = page.locator('button:has-text("Add company")');
		this.removeCompanyButton = page.locator('button:has(svg)').filter({ hasText: /trash/i }).first();

		// Initialize call status locators
		this.callStatusText = page.locator('[data-testid="call-status"], text=/Status:/');
		this.providerIndicator = page.locator('[data-testid="provider-indicator"], text=/Provider:/');
		this.callDurationCounter = page.locator('[data-testid="call-duration"], text=/Duration:/');
		this.latencyMetrics = page.locator('[data-testid="latency-metrics"]');
		this.connectionQualityIndicator = page.locator('[data-testid="connection-quality"]');
		this.transcriptContainer = page.locator('[data-testid="transcript"], .transcript-container');

		// Initialize audio controls locators
		this.audioControls = page.locator('[data-testid="audio-controls"]');
		this.muteButton = page.locator('button[aria-label="Mute"], button:has-text("Mute")');
		this.volumeControl = page.locator('input[type="range"][aria-label*="volume"]');
		this.startMicrophoneButton = page.locator('button:has-text("Start microphone")');
		this.stopMicrophoneButton = page.locator('button:has-text("Stop")').nth(1);

		// Initialize provider switching locators
		this.providerSwitcher = page.locator('[data-testid="provider-switcher"]');
		this.providerMenu = page.locator('[data-testid="provider-menu"], .provider-menu');
		this.switchProviderButton = page.locator('button:has-text("Switch Provider"), button[data-testid="switch-provider"]');

		// Initialize call summary locators
		this.callSummarySection = page.locator('text=Latest Summary').locator('..');
		this.callRecording = page.locator('text=/Recording URL:/');
		this.callHistory = page.locator('[data-testid="call-history"], .call-history');

		// Initialize realtime session locators
		this.realtimeSessionStatus = page.locator('text=/Status: connected|Status: idle|Status: connecting/');
		this.connectSessionButton = page.locator('button:has-text("Connect session")');
		this.disconnectSessionButton = page.locator('button:has-text("Disconnect")');

		// Initialize error message locator
		this.errorMessage = page.locator('.text-error, [role="alert"]').first();
	}

	/**
	 * Navigate to the calls page
	 */
	async goto(): Promise<void> {
		await this.page.goto('/calls/outbound');
		await this.waitForPageLoad();
	}

	/**
	 * Wait for calls page to fully load
	 */
	async waitForPageLoad(): Promise<void> {
		await expect(this.pageTitle).toBeVisible({ timeout: 10000 });
		await expect(this.modelSelect).toBeVisible({ timeout: 10000 });
	}

	/**
	 * Configure call settings
	 */
	async configureCall(config: {
		phoneNumber: string;
		provider?: string;
		voice?: string;
		model?: string;
		language?: string;
	}): Promise<void> {
		// Fill in phone number
		await this.companyPhoneInput.clear();
		await this.companyPhoneInput.fill(config.phoneNumber);

		// Select model if provided
		if (config.model) {
			await this.modelSelect.selectOption({ label: config.model });
		}

		// Select voice if provided
		if (config.voice) {
			await this.voiceSelect.selectOption({ label: config.voice });
		}

		// Select language if provided
		if (config.language) {
			await this.languageSelect.selectOption({ value: config.language });
		}
	}

	/**
	 * Start an outbound call
	 */
	async startCall(): Promise<void> {
		await this.launchCallButton.click();
		// Wait for call to initiate
		await this.page.waitForTimeout(2000);
	}

	/**
	 * End an active call
	 */
	async endCall(): Promise<void> {
		await this.stopCallButton.click();
		await this.page.waitForTimeout(1000);
	}

	/**
	 * Wait for call to connect
	 */
	async waitForCallToConnect(timeout = 30000): Promise<void> {
		await expect(this.callStatusText).toContainText('In Progress', { timeout });
	}

	/**
	 * Verify call status
	 */
	async verifyCallStatus(expectedStatus: string): Promise<void> {
		await expect(this.callStatusText).toContainText(expectedStatus, { timeout: 10000 });
	}

	/**
	 * Verify audio controls are visible
	 */
	async verifyAudioControlsVisible(): Promise<void> {
		await expect(this.startMicrophoneButton).toBeVisible({ timeout: 5000 });
	}

	/**
	 * Get current provider
	 */
	async getCurrentProvider(): Promise<string> {
		const providerText = await this.realtimeSessionStatus.textContent();
		if (!providerText) return '';

		// Extract provider from "Provider: gemini " Status: connected" format
		const match = providerText.match(/Provider:\s*(\w+)/i);
		return match ? match[1] : '';
	}

	/**
	 * Switch to a different provider
	 */
	async switchProvider(providerName: string): Promise<void> {
		// Look for provider switcher component
		const providerButtons = this.page.locator(`button:has-text("${providerName}")`);
		const count = await providerButtons.count();

		if (count > 0) {
			// Click the provider button directly
			await providerButtons.first().click();
			await this.page.waitForTimeout(2000);
		} else {
			// Fallback: look for a dropdown or menu
			const switchButton = this.page.locator('button:has-text("Switch"), button:has-text("Provider")');
			if (await switchButton.isVisible()) {
				await switchButton.click();
				await this.page.locator(`text=${providerName}`).click();
				await this.page.waitForTimeout(2000);
			}
		}
	}

	/**
	 * Verify provider indicator shows expected provider
	 */
	async verifyProvider(expectedProvider: string): Promise<void> {
		const currentProvider = await this.getCurrentProvider();
		expect(currentProvider.toLowerCase()).toContain(expectedProvider.toLowerCase());
	}

	/**
	 * Verify call remains active after provider switch
	 */
	async verifyCallStillActive(): Promise<void> {
		// Check that call status is still "In Progress" or "connected"
		const statusText = await this.realtimeSessionStatus.textContent();
		expect(statusText).toMatch(/connected|in progress/i);
	}

	/**
	 * Verify conversation history is preserved
	 */
	async verifyConversationHistoryPreserved(): Promise<boolean> {
		try {
			const transcript = await this.transcriptContainer.textContent();
			return transcript !== null && transcript.length > 0;
		} catch {
			return false;
		}
	}

	/**
	 * Verify call metrics are displayed
	 */
	async verifyCallMetricsDisplayed(): Promise<void> {
		// Verify at least the session monitor section is visible
		const sessionMonitor = this.page.locator('text=Session Monitor').locator('..');
		await expect(sessionMonitor).toBeVisible();
	}

	/**
	 * Verify transcript updates in real-time
	 */
	async verifyTranscriptUpdating(): Promise<boolean> {
		try {
			const initialContent = await this.transcriptContainer.textContent();
			await this.page.waitForTimeout(2000);
			const updatedContent = await this.transcriptContainer.textContent();
			return initialContent !== updatedContent;
		} catch {
			return false;
		}
	}

	/**
	 * Wait for call to complete
	 */
	async waitForCallToComplete(timeout = 60000): Promise<void> {
		await expect(this.callStatusText).toContainText('Completed', { timeout });
	}

	/**
	 * Verify call summary is displayed
	 */
	async verifyCallSummaryDisplayed(): Promise<void> {
		await expect(this.callSummarySection).toBeVisible({ timeout: 10000 });
	}

	/**
	 * Verify call recording is available
	 */
	async verifyCallRecordingAvailable(): Promise<boolean> {
		try {
			const recordingText = await this.callRecording.textContent();
			return recordingText !== null && !recordingText.includes('Not available');
		} catch {
			return false;
		}
	}

	/**
	 * Verify call appears in history
	 */
	async verifyCallInHistory(): Promise<boolean> {
		try {
			await expect(this.callSummarySection).toBeVisible({ timeout: 5000 });
			const summaryText = await this.callSummarySection.textContent();
			return summaryText !== null && summaryText.length > 0;
		} catch {
			return false;
		}
	}

	/**
	 * Set AI instructions
	 */
	async setAIInstructions(instructions: string): Promise<void> {
		await this.aiInstructionsTextarea.clear();
		await this.aiInstructionsTextarea.fill(instructions);
	}

	/**
	 * Load a campaign script
	 */
	async loadCampaign(campaignName: string): Promise<void> {
		const campaignButton = this.page.locator(`button:has-text("${campaignName}")`);
		await campaignButton.click();
		await this.page.waitForTimeout(1000);
	}

	/**
	 * Connect realtime session
	 */
	async connectRealtimeSession(): Promise<void> {
		await this.connectSessionButton.click();
		await this.page.waitForTimeout(2000);
	}

	/**
	 * Disconnect realtime session
	 */
	async disconnectRealtimeSession(): Promise<void> {
		await this.disconnectSessionButton.click();
		await this.page.waitForTimeout(1000);
	}

	/**
	 * Start microphone
	 */
	async startMicrophone(): Promise<void> {
		// Grant microphone permission if needed
		await this.page.context().grantPermissions(['microphone']);
		await this.startMicrophoneButton.click();
		await this.page.waitForTimeout(1000);
	}

	/**
	 * Stop microphone
	 */
	async stopMicrophone(): Promise<void> {
		await this.stopMicrophoneButton.click();
		await this.page.waitForTimeout(500);
	}

	/**
	 * Get error message
	 */
	async getErrorMessage(): Promise<string> {
		try {
			await expect(this.errorMessage).toBeVisible({ timeout: 3000 });
			return await this.errorMessage.textContent() || '';
		} catch {
			return '';
		}
	}

	/**
	 * Verify no error is displayed
	 */
	async verifyNoError(): Promise<void> {
		const isVisible = await this.errorMessage.isVisible().catch(() => false);
		expect(isVisible).toBeFalsy();
	}
}
