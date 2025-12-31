import { Page, expect } from '@playwright/test';

/**
 * Custom assertions for E2E tests
 */

/**
 * Assert that a call is currently in progress
 * @param page - Playwright page instance
 */
export async function assertCallInProgress(page: Page): Promise<void> {
	const statusIndicator = page.locator('[data-testid="call-status"], .call-status');

	// Check that status indicator exists and is visible
	await expect(statusIndicator).toBeVisible({ timeout: 10000 });

	// Check that status text indicates call is in progress
	const statusText = await statusIndicator.textContent();
	const activeStatuses = ['in progress', 'connected', 'active', 'ongoing'];

	const isActive = activeStatuses.some((status) =>
		statusText?.toLowerCase().includes(status)
	);

	expect(isActive).toBeTruthy();

	// Check that end call button is visible
	const endCallButton = page.locator(
		'button[data-testid="end-call"], button:has-text("End Call"), button:has-text("Hang Up")'
	);
	await expect(endCallButton).toBeVisible();

	// Check that call duration is counting up
	const callDuration = page.locator('[data-testid="call-duration"], .call-duration');
	if (await callDuration.isVisible()) {
		const duration = await callDuration.textContent();
		expect(duration).toMatch(/\d{2}:\d{2}/); // Format: MM:SS
	}
}

/**
 * Assert that a specific provider is active
 * @param page - Playwright page instance
 * @param providerName - Expected provider name (e.g., "Twilio", "Vonage")
 */
export async function assertProviderActive(page: Page, providerName: string): Promise<void> {
	const activeProviderBadge = page.locator('[data-testid="active-provider"]');

	// Check that provider badge exists and is visible
	await expect(activeProviderBadge).toBeVisible({ timeout: 10000 });

	// Check that provider name matches
	await expect(activeProviderBadge).toContainText(providerName, { ignoreCase: true });

	// Optionally check that provider indicator has active state
	const hasActiveClass = await activeProviderBadge.evaluate((el) => {
		return (
			el.classList.contains('active') ||
			el.classList.contains('connected') ||
			el.getAttribute('data-active') === 'true'
		);
	});

	expect(hasActiveClass).toBeTruthy();
}

/**
 * Assert that user is authenticated
 * @param page - Playwright page instance
 */
export async function assertAuthenticated(page: Page): Promise<void> {
	// Check that access token exists in localStorage
	const hasAccessToken = await page.evaluate(() => {
		return localStorage.getItem('accessToken') !== null;
	});

	expect(hasAccessToken).toBeTruthy();

	// Check that user is not on login page
	const currentUrl = page.url();
	expect(currentUrl).not.toContain('/auth/login');
	expect(currentUrl).not.toContain('/auth/register');

	// Check that navigation/dashboard elements are visible
	const navigation = page.locator('nav, [role="navigation"]');
	await expect(navigation).toBeVisible({ timeout: 5000 });
}

/**
 * Assert that user is not authenticated
 * @param page - Playwright page instance
 */
export async function assertNotAuthenticated(page: Page): Promise<void> {
	// Check that access token does not exist in localStorage
	const hasAccessToken = await page.evaluate(() => {
		return localStorage.getItem('accessToken') !== null;
	});

	expect(hasAccessToken).toBeFalsy();

	// Check that user is redirected to login page when trying to access protected route
	const currentUrl = page.url();
	expect(currentUrl).toMatch(/\/(auth\/login|login)/);
}

/**
 * Assert that an error message is displayed
 * @param page - Playwright page instance
 * @param expectedMessage - Expected error message (can be partial match)
 */
export async function assertErrorDisplayed(page: Page, expectedMessage?: string): Promise<void> {
	const errorMessage = page.locator('[role="alert"], .error-message, .alert-error');

	// Check that error message exists and is visible
	await expect(errorMessage).toBeVisible({ timeout: 5000 });

	// If specific message is provided, check for it
	if (expectedMessage) {
		await expect(errorMessage).toContainText(expectedMessage, { ignoreCase: true });
	}

	// Check that error message is not empty
	const messageText = await errorMessage.textContent();
	expect(messageText?.trim().length).toBeGreaterThan(0);
}

/**
 * Assert that no error message is displayed
 * @param page - Playwright page instance
 */
export async function assertNoError(page: Page): Promise<void> {
	const errorMessage = page.locator('[role="alert"], .error-message, .alert-error');

	try {
		await expect(errorMessage).toBeHidden({ timeout: 2000 });
	} catch {
		// If element doesn't exist, that's also fine
		const count = await errorMessage.count();
		expect(count).toBe(0);
	}
}

/**
 * Assert that URL contains a specific path
 * @param page - Playwright page instance
 * @param expectedPath - Expected path in URL
 */
export async function assertUrlContains(page: Page, expectedPath: string): Promise<void> {
	const currentUrl = page.url();
	expect(currentUrl).toContain(expectedPath);
}

/**
 * Assert that URL matches a pattern
 * @param page - Playwright page instance
 * @param pattern - URL pattern (can be regex)
 */
export async function assertUrlMatches(page: Page, pattern: string | RegExp): Promise<void> {
	const currentUrl = page.url();
	expect(currentUrl).toMatch(pattern);
}

/**
 * Assert that an element has specific text
 * @param page - Playwright page instance
 * @param selector - Element selector
 * @param expectedText - Expected text content
 */
export async function assertElementHasText(
	page: Page,
	selector: string,
	expectedText: string
): Promise<void> {
	const element = page.locator(selector);
	await expect(element).toBeVisible({ timeout: 5000 });
	await expect(element).toHaveText(expectedText);
}

/**
 * Assert that an element contains specific text
 * @param page - Playwright page instance
 * @param selector - Element selector
 * @param expectedText - Expected text content (partial match)
 */
export async function assertElementContainsText(
	page: Page,
	selector: string,
	expectedText: string
): Promise<void> {
	const element = page.locator(selector);
	await expect(element).toBeVisible({ timeout: 5000 });
	await expect(element).toContainText(expectedText);
}

/**
 * Assert that form validation error is shown
 * @param page - Playwright page instance
 * @param fieldName - Form field name
 * @param expectedError - Expected validation error message
 */
export async function assertFormValidationError(
	page: Page,
	fieldName: string,
	expectedError?: string
): Promise<void> {
	// Look for validation error near the field
	const validationError = page.locator(
		`[data-testid="${fieldName}-error"], .error-${fieldName}, input[name="${fieldName}"] ~ .error`
	);

	await expect(validationError).toBeVisible({ timeout: 3000 });

	if (expectedError) {
		await expect(validationError).toContainText(expectedError);
	}
}

/**
 * Assert that a loading indicator is visible
 * @param page - Playwright page instance
 */
export async function assertLoading(page: Page): Promise<void> {
	const loadingIndicator = page.locator(
		'[data-testid="loading"], .loading, .spinner, [role="progressbar"]'
	);

	await expect(loadingIndicator).toBeVisible({ timeout: 3000 });
}

/**
 * Assert that loading is complete (no loading indicators)
 * @param page - Playwright page instance
 */
export async function assertLoadingComplete(page: Page): Promise<void> {
	const loadingIndicator = page.locator(
		'[data-testid="loading"], .loading, .spinner, [role="progressbar"]'
	);

	await expect(loadingIndicator).toBeHidden({ timeout: 15000 });
}

/**
 * Assert that a success message is displayed
 * @param page - Playwright page instance
 * @param expectedMessage - Expected success message (optional)
 */
export async function assertSuccessMessage(
	page: Page,
	expectedMessage?: string
): Promise<void> {
	const successMessage = page.locator(
		'[role="status"], .success-message, .alert-success, [data-testid="success-message"]'
	);

	await expect(successMessage).toBeVisible({ timeout: 5000 });

	if (expectedMessage) {
		await expect(successMessage).toContainText(expectedMessage);
	}
}

/**
 * Assert that a modal/dialog is visible
 * @param page - Playwright page instance
 * @param modalTitle - Expected modal title (optional)
 */
export async function assertModalVisible(page: Page, modalTitle?: string): Promise<void> {
	const modal = page.locator('[role="dialog"], .modal, [data-testid="modal"]');

	await expect(modal).toBeVisible({ timeout: 5000 });

	if (modalTitle) {
		const title = modal.locator('h1, h2, h3, [data-testid="modal-title"]');
		await expect(title).toContainText(modalTitle);
	}
}

/**
 * Assert that a toast notification is visible
 * @param page - Playwright page instance
 * @param message - Expected toast message (optional)
 */
export async function assertToastVisible(page: Page, message?: string): Promise<void> {
	const toast = page.locator('[role="alert"], .toast, [data-testid="toast"]');

	await expect(toast).toBeVisible({ timeout: 5000 });

	if (message) {
		await expect(toast).toContainText(message);
	}
}

/**
 * Assert that table has specific number of rows
 * @param page - Playwright page instance
 * @param tableSelector - Table selector
 * @param expectedRowCount - Expected number of rows
 */
export async function assertTableRowCount(
	page: Page,
	tableSelector: string,
	expectedRowCount: number
): Promise<void> {
	const table = page.locator(tableSelector);
	await expect(table).toBeVisible({ timeout: 5000 });

	const rows = table.locator('tbody tr');
	await expect(rows).toHaveCount(expectedRowCount);
}

/**
 * Assert that list has specific number of items
 * @param page - Playwright page instance
 * @param listSelector - List selector
 * @param expectedItemCount - Expected number of items
 */
export async function assertListItemCount(
	page: Page,
	listSelector: string,
	expectedItemCount: number
): Promise<void> {
	const list = page.locator(listSelector);
	await expect(list).toBeVisible({ timeout: 5000 });

	const items = list.locator('> *');
	await expect(items).toHaveCount(expectedItemCount);
}

/**
 * Assert that button is disabled
 * @param page - Playwright page instance
 * @param buttonSelector - Button selector
 */
export async function assertButtonDisabled(page: Page, buttonSelector: string): Promise<void> {
	const button = page.locator(buttonSelector);
	await expect(button).toBeVisible({ timeout: 5000 });
	await expect(button).toBeDisabled();
}

/**
 * Assert that button is enabled
 * @param page - Playwright page instance
 * @param buttonSelector - Button selector
 */
export async function assertButtonEnabled(page: Page, buttonSelector: string): Promise<void> {
	const button = page.locator(buttonSelector);
	await expect(button).toBeVisible({ timeout: 5000 });
	await expect(button).toBeEnabled();
}

/**
 * Assert that checkbox is checked
 * @param page - Playwright page instance
 * @param checkboxSelector - Checkbox selector
 */
export async function assertCheckboxChecked(page: Page, checkboxSelector: string): Promise<void> {
	const checkbox = page.locator(checkboxSelector);
	await expect(checkbox).toBeVisible({ timeout: 5000 });
	await expect(checkbox).toBeChecked();
}

/**
 * Assert that checkbox is not checked
 * @param page - Playwright page instance
 * @param checkboxSelector - Checkbox selector
 */
export async function assertCheckboxUnchecked(
	page: Page,
	checkboxSelector: string
): Promise<void> {
	const checkbox = page.locator(checkboxSelector);
	await expect(checkbox).toBeVisible({ timeout: 5000 });
	await expect(checkbox).not.toBeChecked();
}

/**
 * Assert that input field has specific value
 * @param page - Playwright page instance
 * @param inputSelector - Input selector
 * @param expectedValue - Expected input value
 */
export async function assertInputValue(
	page: Page,
	inputSelector: string,
	expectedValue: string
): Promise<void> {
	const input = page.locator(inputSelector);
	await expect(input).toBeVisible({ timeout: 5000 });
	await expect(input).toHaveValue(expectedValue);
}

/**
 * Assert that element has specific attribute
 * @param page - Playwright page instance
 * @param selector - Element selector
 * @param attribute - Attribute name
 * @param expectedValue - Expected attribute value
 */
export async function assertElementAttribute(
	page: Page,
	selector: string,
	attribute: string,
	expectedValue: string
): Promise<void> {
	const element = page.locator(selector);
	await expect(element).toBeVisible({ timeout: 5000 });
	await expect(element).toHaveAttribute(attribute, expectedValue);
}

/**
 * Assert that element has specific CSS class
 * @param page - Playwright page instance
 * @param selector - Element selector
 * @param className - Expected CSS class
 */
export async function assertElementHasClass(
	page: Page,
	selector: string,
	className: string
): Promise<void> {
	const element = page.locator(selector);
	await expect(element).toBeVisible({ timeout: 5000 });
	await expect(element).toHaveClass(new RegExp(className));
}

/**
 * Assert that API call was made
 * @param page - Playwright page instance
 * @param endpoint - API endpoint
 * @param method - HTTP method (default: 'GET')
 */
export async function assertApiCalled(
	page: Page,
	endpoint: string,
	method: string = 'GET'
): Promise<void> {
	// This requires setting up request interception in the test
	// For now, we'll check if the request was made
	await page.waitForResponse(
		(response) => response.url().includes(endpoint) && response.request().method() === method,
		{ timeout: 10000 }
	);
}

/**
 * Assert that localStorage has specific key
 * @param page - Playwright page instance
 * @param key - localStorage key
 */
export async function assertLocalStorageHasKey(page: Page, key: string): Promise<void> {
	const value = await page.evaluate((storageKey) => {
		return localStorage.getItem(storageKey);
	}, key);

	expect(value).not.toBeNull();
}

/**
 * Assert that localStorage has specific value
 * @param page - Playwright page instance
 * @param key - localStorage key
 * @param expectedValue - Expected value
 */
export async function assertLocalStorageValue(
	page: Page,
	key: string,
	expectedValue: string
): Promise<void> {
	const value = await page.evaluate((storageKey) => {
		return localStorage.getItem(storageKey);
	}, key);

	expect(value).toBe(expectedValue);
}

/**
 * Assert that an element is visible
 * @param locator - Playwright locator
 * @param timeout - Timeout in ms
 * @param message - Optional message
 */
export async function expectVisible(
	locator: import('@playwright/test').Locator,
	timeout: number = 5000,
	message?: string
): Promise<void> {
	await expect(locator, message).toBeVisible({ timeout });
}

/**
 * Assert that page title contains expected text
 * @param page - Playwright page instance
 * @param expectedText - Expected title text
 */
export async function expectTitleContains(page: Page, expectedText: string): Promise<void> {
	await expect(page).toHaveTitle(new RegExp(expectedText, 'i'));
}

/**
 * Alias for assertUrlContains for backwards compatibility
 * @param page - Playwright page instance
 * @param expectedPath - Expected URL path
 */
export async function expectUrlContains(page: Page, expectedPath: string): Promise<void> {
	await assertUrlContains(page, expectedPath);
}
