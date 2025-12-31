import { test, expect } from '../fixtures/auth.fixture.js';
import { VoiceCallsPage } from '../pages/VoiceCallsPage.js';

test.describe('Voice Calls Page (Outbound)', () => {
	test.describe('Page Structure', () => {
		test('should display outbound calls page with correct structure', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const structureValid = await voiceCallsPage.verifyPageStructure();
			expect(structureValid).toBe(true);
		});

		test('should display page title and description', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.pageTitle).toBeVisible();
			await expect(voiceCallsPage.pageDescription).toBeVisible();
		});

		test('should display call configuration card', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.callConfigCard).toBeVisible();
		});

		test('should display campaign script card', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.campaignScriptCard).toBeVisible();
		});

		test('should display target companies card', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.targetCompaniesCard).toBeVisible();
		});
	});

	test.describe('Call Configuration', () => {
		test('should display country selector', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.countrySelect).toBeVisible();
		});

		test('should display from phone number field', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.fromPhoneNumber).toBeVisible();
		});

		test('should display model selector', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();
			await voiceCallsPage.waitForConfigurationLoad();

			await expect(voiceCallsPage.modelSelect).toBeVisible();
		});

		test('should display voice selector', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();
			await voiceCallsPage.waitForConfigurationLoad();

			await expect(voiceCallsPage.voiceSelect).toBeVisible();
		});

		test('should display language selector', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.languageSelect).toBeVisible();
		});

		test('should display audio mode selector', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.audioModeSelect).toBeVisible();
		});

		test('should be able to select country', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await voiceCallsPage.selectCountry('US');
			const phoneNumber = await voiceCallsPage.getFromPhoneNumber();
			expect(phoneNumber).toBeTruthy();
		});

		test('should update phone number when country changes', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await voiceCallsPage.selectCountry('CZ');
			const czPhone = await voiceCallsPage.getFromPhoneNumber();

			await voiceCallsPage.selectCountry('US');
			const usPhone = await voiceCallsPage.getFromPhoneNumber();

			// Phone numbers should exist
			expect(czPhone).toBeTruthy();
			expect(usPhone).toBeTruthy();
		});

		test('should have available languages', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const languages = await voiceCallsPage.getAvailableLanguages();
			expect(languages.length).toBeGreaterThan(0);
			expect(languages).toContain('English');
		});
	});

	test.describe('Campaign Script Section', () => {
		test('should display AI instructions textarea', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.aiInstructionsTextarea).toBeVisible();
		});

		test('should be able to set AI instructions', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const testInstructions = 'Test AI instructions for the call';
			await voiceCallsPage.setAIInstructions(testInstructions);

			const instructions = await voiceCallsPage.getAIInstructions();
			expect(instructions).toBe(testInstructions);
		});

		test('should display reset summary button', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.resetSummaryButton).toBeVisible();
		});

		test('should display campaign preset buttons', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			// Check for campaign buttons
			const insuranceButton = authenticatedPage.locator('button:has-text("Insurance")');
			const solarButton = authenticatedPage.locator('button:has-text("Solar")');
			const reengagementButton = authenticatedPage.locator('button:has-text("Re-engagement")');

			await expect(insuranceButton).toBeVisible();
			await expect(solarButton).toBeVisible();
			await expect(reengagementButton).toBeVisible();
		});
	});

	test.describe('Target Companies Section', () => {
		test('should display add company button', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.addCompanyButton).toBeVisible();
		});

		test('should have at least one company input', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const count = await voiceCallsPage.getCompanyCount();
			expect(count).toBeGreaterThanOrEqual(1);
		});

		test('should be able to add a company', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const initialCount = await voiceCallsPage.getCompanyCount();
			await voiceCallsPage.addCompany();

			const newCount = await voiceCallsPage.getCompanyCount();
			expect(newCount).toBe(initialCount + 1);
		});

		test('should be able to set company details', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await voiceCallsPage.setCompanyDetails(0, 'Test Company', '+15551234567');

			const companyInput = authenticatedPage.locator('#company-0');
			const phoneInput = authenticatedPage.locator('#phone-0');

			await expect(companyInput).toHaveValue('Test Company');
			await expect(phoneInput).toHaveValue('+15551234567');
		});

		test('should display launch call button', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.launchCallButtons.first()).toBeVisible();
		});

		test('should display stop button', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			// Stop button should exist (might be disabled initially)
			const stopButtons = await voiceCallsPage.stopCallButtons.count();
			expect(stopButtons).toBeGreaterThan(0);
		});
	});

	test.describe('Audio Tester Section', () => {
		test('should display local audio tester card', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.audioTesterCard).toBeVisible();
		});

		test('should display start microphone button', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.startMicButton).toBeVisible();
		});
	});

	test.describe('Session Monitor Section', () => {
		test('should display session monitor card', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.sessionMonitorCard).toBeVisible();
		});

		test('should display call status description', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const status = await voiceCallsPage.getCallStatusDescription();
			expect(status).toBeTruthy();
		});
	});

	test.describe('Realtime Session Section', () => {
		test('should display realtime session card', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.realtimeSessionCard).toBeVisible();
		});

		test('should display connect session button', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.connectSessionButton).toBeVisible();
		});

		test('should display disconnect button', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.disconnectButton).toBeVisible();
		});

		test('should show session status', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const status = await voiceCallsPage.getSessionStatus();
			// Status should be present (idle, disconnected, etc.)
			expect(status).toBeTruthy();
		});

		test('should show current provider', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const provider = await voiceCallsPage.getCurrentProvider();
			expect(provider).toBeTruthy();
		});
	});

	test.describe('Error Handling', () => {
		test('should show error when launching call without configuration', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			// Clear AI instructions
			await voiceCallsPage.setAIInstructions('');

			// Try to launch call
			await voiceCallsPage.launchCall(0);

			// Should show an error
			await authenticatedPage.waitForTimeout(1000);
			const hasError = await voiceCallsPage.hasError();
			expect(hasError).toBe(true);
		});

		test('should show error when phone number is empty', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			// Set AI instructions but leave phone empty
			await voiceCallsPage.setAIInstructions('Test instructions');
			await voiceCallsPage.setCompanyDetails(0, 'Test Company', '');

			// Try to launch call
			await voiceCallsPage.launchCall(0);

			await authenticatedPage.waitForTimeout(1000);
			const hasError = await voiceCallsPage.hasError();
			expect(hasError).toBe(true);
		});
	});

	test.describe('Navigation', () => {
		test('should be accessible from protected routes', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(authenticatedPage).toHaveURL(/.*calls\/outbound.*/);
		});

		test('should maintain authentication state', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(authenticatedPage).not.toHaveURL(/.*login.*/);
		});
	});

	test.describe('Responsive Design', () => {
		test('should display properly on mobile viewport', async ({ authenticatedPage }) => {
			await authenticatedPage.setViewportSize({ width: 375, height: 667 });

			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const isVisible = await voiceCallsPage.isVisible();
			expect(isVisible).toBe(true);
		});

		test('should display properly on tablet viewport', async ({ authenticatedPage }) => {
			await authenticatedPage.setViewportSize({ width: 768, height: 1024 });

			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const isVisible = await voiceCallsPage.isVisible();
			expect(isVisible).toBe(true);
		});

		test('should display properly on desktop viewport', async ({ authenticatedPage }) => {
			await authenticatedPage.setViewportSize({ width: 1920, height: 1080 });

			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const isVisible = await voiceCallsPage.isVisible();
			expect(isVisible).toBe(true);
		});
	});

	test.describe('De-essing Toggle', () => {
		test('should display de-essing toggle', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await expect(voiceCallsPage.deEssingToggle).toBeVisible();
		});

		test('should be able to toggle de-essing', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			const initialState = await voiceCallsPage.isDeEssingEnabled();
			await voiceCallsPage.toggleDeEssing();
			const newState = await voiceCallsPage.isDeEssingEnabled();

			expect(newState).not.toBe(initialState);
		});
	});

	test.describe('Local Storage Persistence', () => {
		test('should persist company data in localStorage', async ({ authenticatedPage }) => {
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			// Set company details
			await voiceCallsPage.setCompanyDetails(0, 'Persistent Company', '+15559876543');

			// Wait for localStorage to be updated
			await authenticatedPage.waitForTimeout(500);

			// Check localStorage
			const stored = await authenticatedPage.evaluate(() => {
				return localStorage.getItem('operator-console.target-companies');
			});

			expect(stored).toBeTruthy();
			if (stored) {
				const parsed = JSON.parse(stored);
				expect(parsed[0].name).toBe('Persistent Company');
			}
		});

		test('should load company data from localStorage on page load', async ({ authenticatedPage }) => {
			// First set some data
			const voiceCallsPage = new VoiceCallsPage(authenticatedPage);
			await voiceCallsPage.goto();

			await voiceCallsPage.setCompanyDetails(0, 'Test Company', '+15551111111');

			// Wait for save
			await authenticatedPage.waitForTimeout(500);

			// Reload page
			await authenticatedPage.reload();
			await voiceCallsPage.waitForPageLoad();

			// Wait for hydration
			await authenticatedPage.waitForTimeout(500);

			// Check if data was loaded
			const companyInput = authenticatedPage.locator('#company-0');
			await expect(companyInput).toHaveValue('Test Company');
		});
	});
});
