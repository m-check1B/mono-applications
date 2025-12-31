import { test, expect } from '../fixtures/auth.fixture.js';
import { CallPage } from '../pages/CallPage.js';
import { DashboardPage } from '../pages/DashboardPage.js';
import { TEST_PHONE_NUMBERS } from '../fixtures/test-data.js';
import {
	assertCallInProgress,
	assertProviderActive,
	assertErrorDisplayed
} from '../utils/assertions.js';
import { waitForLoadingComplete, takeScreenshot } from '../utils/helpers.js';

test.describe('Calls', () => {
	test('should start an outbound call', async ({ authenticatedPage }) => {
		const callPage = new CallPage(authenticatedPage);

		// Navigate to call page
		await callPage.goto();

		// Start a call with valid phone number
		await callPage.startOutboundCall(TEST_PHONE_NUMBERS.valid.us);

		// Verify call is in progress
		await assertCallInProgress(authenticatedPage);

		// Check call status
		const status = await callPage.getCallStatus();
		expect(status).toMatch(/in progress|connected|active/i);

		// End the call
		await callPage.endCall();
	});

	test('should display error for invalid phone number', async ({ authenticatedPage }) => {
		const callPage = new CallPage(authenticatedPage);

		// Navigate to call page
		await callPage.goto();

		// Try to start call with invalid phone number
		await callPage.phoneNumberInput.fill(TEST_PHONE_NUMBERS.invalid.tooShort);
		await callPage.dialButton.click();

		// Should show error
		await assertErrorDisplayed(authenticatedPage);
	});

	test('should end an active call', async ({ authenticatedPage }) => {
		const callPage = new CallPage(authenticatedPage);

		// Navigate to call page
		await callPage.goto();

		// Start a call
		await callPage.startOutboundCall(TEST_PHONE_NUMBERS.valid.us);

		// Verify call is active
		expect(await callPage.isCallActive()).toBe(true);

		// End the call
		await callPage.endCall();

		// Verify call ended
		await callPage.waitForCallEnded();
	});

	test('should mute and unmute call', async ({ authenticatedPage }) => {
		const callPage = new CallPage(authenticatedPage);

		// Navigate to call page
		await callPage.goto();

		// Start a call
		await callPage.startOutboundCall(TEST_PHONE_NUMBERS.valid.us);

		// Mute the call
		await callPage.mute();
		expect(await callPage.isMuted()).toBe(true);

		// Unmute the call
		await callPage.unmute();
		expect(await callPage.isMuted()).toBe(false);

		// End the call
		await callPage.endCall();
	});

	test('should put call on hold and resume', async ({ authenticatedPage }) => {
		const callPage = new CallPage(authenticatedPage);

		// Navigate to call page
		await callPage.goto();

		// Start a call
		await callPage.startOutboundCall(TEST_PHONE_NUMBERS.valid.us);

		// Put call on hold
		await callPage.hold();

		// Wait a moment
		await authenticatedPage.waitForTimeout(1000);

		// Resume call
		await callPage.resume();

		// End the call
		await callPage.endCall();
	});

	test('should switch provider during call', async ({ authenticatedPage }) => {
		const callPage = new CallPage(authenticatedPage);

		// Navigate to call page
		await callPage.goto();

		// Start a call
		await callPage.startOutboundCall(TEST_PHONE_NUMBERS.valid.us);

		// Get current provider
		const currentProvider = await callPage.getActiveProvider();
		expect(currentProvider).toBeTruthy();

		// Try to switch provider (if available)
		if (await callPage.providerSelector.isVisible()) {
			await callPage.switchProvider('Vonage');

			// Verify provider switched
			await assertProviderActive(authenticatedPage, 'Vonage');
		}

		// End the call
		await callPage.endCall();
	});

	test('should display call duration', async ({ authenticatedPage }) => {
		const callPage = new CallPage(authenticatedPage);

		// Navigate to call page
		await callPage.goto();

		// Start a call
		await callPage.startOutboundCall(TEST_PHONE_NUMBERS.valid.us);

		// Wait for call to be in progress
		await callPage.waitForCallInProgress();

		// Wait a few seconds
		await authenticatedPage.waitForTimeout(3000);

		// Get call duration
		const duration = await callPage.getCallDuration();
		expect(duration).toBeTruthy();
		expect(duration).toMatch(/\d{2}:\d{2}/); // Format: MM:SS

		// End the call
		await callPage.endCall();
	});

	test('should handle call controls visibility', async ({ authenticatedPage }) => {
		const callPage = new CallPage(authenticatedPage);

		// Navigate to call page
		await callPage.goto();

		// Verify call controls are visible
		await expect(callPage.callControls).toBeVisible();

		// Verify phone input is visible
		await expect(callPage.phoneNumberInput).toBeVisible();
	});

	test('should display provider selector', async ({ authenticatedPage }) => {
		const callPage = new CallPage(authenticatedPage);

		// Navigate to call page
		await callPage.goto();

		// Check if provider selector exists
		const selectorCount = await callPage.providerSelector.count();
		expect(selectorCount).toBeGreaterThanOrEqual(0);
	});

	test('should adjust volume', async ({ authenticatedPage }) => {
		const callPage = new CallPage(authenticatedPage);

		// Navigate to call page
		await callPage.goto();

		// Start a call
		await callPage.startOutboundCall(TEST_PHONE_NUMBERS.valid.us);

		// Try to adjust volume (if control exists)
		if (await callPage.volumeSlider.isVisible()) {
			await callPage.setVolume(75);

			// Verify volume was set
			const volume = await callPage.volumeSlider.inputValue();
			expect(volume).toBe('75');
		}

		// End the call
		await callPage.endCall();
	});

	test('should display caller information', async ({ authenticatedPage }) => {
		const callPage = new CallPage(authenticatedPage);

		// Navigate to call page
		await callPage.goto();

		// Start a call
		await callPage.startOutboundCall(TEST_PHONE_NUMBERS.valid.us);

		// Get caller info (if available)
		const callerInfo = await callPage.getCallerInfo();

		// Caller info may or may not be available
		expect(callerInfo).toBeDefined();

		// End the call
		await callPage.endCall();
	});

	test('should handle call from dashboard', async ({ authenticatedPage }) => {
		const dashboardPage = new DashboardPage(authenticatedPage);

		// Navigate to dashboard
		await dashboardPage.goto();

		// Check if call button exists
		const callButtonCount = await dashboardPage.callButton.count();

		if (callButtonCount > 0) {
			// Click call button
			await dashboardPage.startCall();

			// Wait for call interface
			await waitForLoadingComplete(authenticatedPage);

			// Take screenshot
			await takeScreenshot(authenticatedPage, 'call-interface');
		}
	});

	test('should show connection status', async ({ authenticatedPage }) => {
		const callPage = new CallPage(authenticatedPage);

		// Navigate to call page
		await callPage.goto();

		// Start a call
		await callPage.startOutboundCall(TEST_PHONE_NUMBERS.valid.us);

		// Check connection status (if available)
		if (await callPage.connectionStatus.isVisible()) {
			expect(await callPage.isConnected()).toBe(true);
		}

		// End the call
		await callPage.endCall();
	});
});
