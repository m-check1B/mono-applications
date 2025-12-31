import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for Call Page
 * Handles all interactions during an active call
 */
export class CallPage {
	readonly page: Page;

	// Call control locators
	readonly callControls: Locator;
	readonly startCallButton: Locator;
	readonly endCallButton: Locator;
	readonly muteButton: Locator;
	readonly unmuteButton: Locator;
	readonly holdButton: Locator;
	readonly resumeButton: Locator;

	// Phone number input
	readonly phoneNumberInput: Locator;
	readonly dialButton: Locator;
	readonly numberPad: Locator;

	// Provider controls
	readonly providerSelector: Locator;
	readonly providerDropdown: Locator;
	readonly activeProviderBadge: Locator;
	readonly switchProviderButton: Locator;

	// Call status indicators
	readonly statusIndicator: Locator;
	readonly callDuration: Locator;
	readonly callQualityIndicator: Locator;
	readonly connectionStatus: Locator;

	// Audio controls
	readonly audioControls: Locator;
	readonly volumeSlider: Locator;
	readonly speakerToggle: Locator;
	readonly microphoneToggle: Locator;

	// Call info
	readonly callerInfo: Locator;
	readonly callerId: Locator;
	readonly callStartTime: Locator;

	// Error messages
	readonly errorMessage: Locator;
	readonly callFailedMessage: Locator;

	constructor(page: Page) {
		this.page = page;

		// Call controls
		this.callControls = page.locator('[data-testid="call-controls"], .call-controls');
		this.startCallButton = page.locator(
			'button[data-testid="start-call"], button:has-text("Start Call")'
		);
		this.endCallButton = page.locator(
			'button[data-testid="end-call"], button:has-text("End Call"), button:has-text("Hang Up")'
		);
		this.muteButton = page.locator('button[data-testid="mute"], button:has-text("Mute")');
		this.unmuteButton = page.locator('button[data-testid="unmute"], button:has-text("Unmute")');
		this.holdButton = page.locator('button[data-testid="hold"], button:has-text("Hold")');
		this.resumeButton = page.locator('button[data-testid="resume"], button:has-text("Resume")');

		// Phone input
		this.phoneNumberInput = page.locator(
			'input[type="tel"], input[name="phone"], input[placeholder*="phone"]'
		);
		this.dialButton = page.locator('button:has-text("Dial"), button:has-text("Call")');
		this.numberPad = page.locator('[data-testid="number-pad"], .number-pad');

		// Provider
		this.providerSelector = page.locator('[data-testid="provider-selector"], .provider-selector');
		this.providerDropdown = page.locator(
			'select[name="provider"], [data-testid="provider-dropdown"]'
		);
		this.activeProviderBadge = page.locator('[data-testid="active-provider"]');
		this.switchProviderButton = page.locator(
			'button[data-testid="switch-provider"], button:has-text("Switch Provider")'
		);

		// Status indicators
		this.statusIndicator = page.locator('[data-testid="call-status"], .call-status');
		this.callDuration = page.locator('[data-testid="call-duration"], .call-duration');
		this.callQualityIndicator = page.locator('[data-testid="call-quality"]');
		this.connectionStatus = page.locator('[data-testid="connection-status"]');

		// Audio
		this.audioControls = page.locator('[data-testid="audio-controls"], .audio-controls');
		this.volumeSlider = page.locator('input[type="range"][name*="volume"]');
		this.speakerToggle = page.locator('button[data-testid="speaker-toggle"]');
		this.microphoneToggle = page.locator('button[data-testid="microphone-toggle"]');

		// Call info
		this.callerInfo = page.locator('[data-testid="caller-info"], .caller-info');
		this.callerId = page.locator('[data-testid="caller-id"]');
		this.callStartTime = page.locator('[data-testid="call-start-time"]');

		// Errors
		this.errorMessage = page.locator('[role="alert"], .error-message, .alert-error');
		this.callFailedMessage = page.locator('[data-testid="call-failed"]');
	}

	/**
	 * Navigate to call page
	 */
	async goto(): Promise<void> {
		await this.page.goto('/calls/new');
		await this.waitForPageLoad();
	}

	/**
	 * Wait for call page to load
	 */
	async waitForPageLoad(): Promise<void> {
		await expect(this.callControls).toBeVisible({ timeout: 10000 });
	}

	/**
	 * Start an outbound call to a phone number
	 * @param phoneNumber - The phone number to call
	 */
	async startOutboundCall(phoneNumber: string): Promise<void> {
		// Fill phone number
		await this.phoneNumberInput.fill(phoneNumber);

		// Wait for response
		const responsePromise = this.page.waitForResponse(
			(response) => response.url().includes('/api/v1/calls') && response.status() === 200,
			{ timeout: 15000 }
		);

		// Click dial/call button
		if (await this.dialButton.isVisible()) {
			await this.dialButton.click();
		} else {
			await this.startCallButton.click();
		}

		// Wait for call to connect
		await responsePromise;
		await this.waitForCallInProgress();
	}

	/**
	 * Wait for call to be in progress
	 */
	async waitForCallInProgress(): Promise<void> {
		// Wait for status to show "in-progress", "connected", or "active"
		await expect(this.statusIndicator).toContainText(/in progress|connected|active/i, {
			timeout: 10000
		});
	}

	/**
	 * End the current call
	 */
	async endCall(): Promise<void> {
		await this.endCallButton.click();

		// Wait for call to end
		await this.waitForCallEnded();
	}

	/**
	 * Wait for call to end
	 */
	async waitForCallEnded(): Promise<void> {
		await expect(this.statusIndicator).toContainText(/ended|completed|terminated/i, {
			timeout: 5000
		});
	}

	/**
	 * Check if call is currently active
	 */
	async isCallActive(): Promise<boolean> {
		try {
			const status = await this.getCallStatus();
			return (
				status.toLowerCase().includes('active') ||
				status.toLowerCase().includes('in progress') ||
				status.toLowerCase().includes('connected')
			);
		} catch {
			return false;
		}
	}

	/**
	 * Get current call status
	 */
	async getCallStatus(): Promise<string> {
		await expect(this.statusIndicator).toBeVisible({ timeout: 5000 });
		return (await this.statusIndicator.textContent()) || '';
	}

	/**
	 * Get call duration
	 */
	async getCallDuration(): Promise<string> {
		try {
			await expect(this.callDuration).toBeVisible({ timeout: 3000 });
			return (await this.callDuration.textContent()) || '';
		} catch {
			return '00:00';
		}
	}

	/**
	 * Mute the call
	 */
	async mute(): Promise<void> {
		if (await this.muteButton.isVisible()) {
			await this.muteButton.click();
			await expect(this.unmuteButton).toBeVisible({ timeout: 3000 });
		}
	}

	/**
	 * Unmute the call
	 */
	async unmute(): Promise<void> {
		if (await this.unmuteButton.isVisible()) {
			await this.unmuteButton.click();
			await expect(this.muteButton).toBeVisible({ timeout: 3000 });
		}
	}

	/**
	 * Check if call is muted
	 */
	async isMuted(): Promise<boolean> {
		return await this.unmuteButton.isVisible();
	}

	/**
	 * Put call on hold
	 */
	async hold(): Promise<void> {
		if (await this.holdButton.isVisible()) {
			await this.holdButton.click();
			await expect(this.resumeButton).toBeVisible({ timeout: 3000 });
		}
	}

	/**
	 * Resume call from hold
	 */
	async resume(): Promise<void> {
		if (await this.resumeButton.isVisible()) {
			await this.resumeButton.click();
			await expect(this.holdButton).toBeVisible({ timeout: 3000 });
		}
	}

	/**
	 * Switch to a different provider
	 * @param providerName - Name of the provider to switch to (e.g., "Twilio", "Vonage")
	 */
	async switchProvider(providerName: string): Promise<void> {
		// Open provider selector
		if (await this.providerSelector.isVisible()) {
			await this.providerSelector.click();
		}

		// Select provider from dropdown
		const providerOption = this.page.locator(
			`option:has-text("${providerName}"), [data-provider="${providerName}"]`
		);
		await providerOption.click();

		// Wait for provider to be active
		await this.waitForProviderActive(providerName);
	}

	/**
	 * Wait for specific provider to be active
	 */
	async waitForProviderActive(providerName: string): Promise<void> {
		await expect(this.activeProviderBadge).toContainText(providerName, { timeout: 10000 });
	}

	/**
	 * Get current active provider
	 */
	async getActiveProvider(): Promise<string> {
		try {
			await expect(this.activeProviderBadge).toBeVisible({ timeout: 5000 });
			return (await this.activeProviderBadge.textContent()) || '';
		} catch {
			return '';
		}
	}

	/**
	 * Adjust volume
	 * @param level - Volume level (0-100)
	 */
	async setVolume(level: number): Promise<void> {
		if (await this.volumeSlider.isVisible()) {
			await this.volumeSlider.fill(level.toString());
		}
	}

	/**
	 * Get call quality indicator status
	 */
	async getCallQuality(): Promise<string> {
		try {
			if (await this.callQualityIndicator.isVisible()) {
				return (await this.callQualityIndicator.textContent()) || '';
			}
		} catch {
			// Quality indicator might not be present
		}
		return '';
	}

	/**
	 * Check if there's an error message
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
			await expect(this.errorMessage).toBeVisible({ timeout: 3000 });
			return (await this.errorMessage.textContent()) || '';
		} catch {
			return '';
		}
	}

	/**
	 * Check if call failed
	 */
	async hasCallFailed(): Promise<boolean> {
		try {
			await expect(this.callFailedMessage).toBeVisible({ timeout: 3000 });
			return true;
		} catch {
			return false;
		}
	}

	/**
	 * Get caller information
	 */
	async getCallerInfo(): Promise<{ id: string; startTime: string }> {
		let id = '';
		let startTime = '';

		try {
			if (await this.callerId.isVisible()) {
				id = (await this.callerId.textContent()) || '';
			}
		} catch {
			// ID might not be visible
		}

		try {
			if (await this.callStartTime.isVisible()) {
				startTime = (await this.callStartTime.textContent()) || '';
			}
		} catch {
			// Start time might not be visible
		}

		return { id: id.trim(), startTime: startTime.trim() };
	}

	/**
	 * Use number pad to dial additional digits (DTMF)
	 */
	async dialDigits(digits: string): Promise<void> {
		if (await this.numberPad.isVisible()) {
			for (const digit of digits) {
				const button = this.numberPad.locator(`button:has-text("${digit}")`);
				await button.click();
			}
		}
	}

	/**
	 * Wait for specific call event
	 */
	async waitForCallEvent(eventType: string): Promise<void> {
		await this.page.waitForResponse(
			(response) =>
				response.url().includes('/api/v1/calls') &&
				response.url().includes(eventType) &&
				response.status() === 200,
			{ timeout: 15000 }
		);
	}

	/**
	 * Check connection status
	 */
	async isConnected(): Promise<boolean> {
		try {
			const status = (await this.connectionStatus.textContent()) || '';
			return status.toLowerCase().includes('connected');
		} catch {
			return false;
		}
	}
}
