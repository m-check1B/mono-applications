import { Page, expect } from '@playwright/test';

/**
 * Helper utilities for E2E tests
 */

/**
 * Wait for all loading spinners to disappear
 * @param page - Playwright page instance
 * @param timeout - Maximum wait time in milliseconds (default: 15000)
 */
export async function waitForLoadingComplete(page: Page, timeout = 15000): Promise<void> {
	const loadingSelectors = [
		'[data-testid="loading"]',
		'.loading',
		'.spinner',
		'[role="progressbar"]',
		'.loading-spinner',
		'.loader'
	];

	try {
		for (const selector of loadingSelectors) {
			const element = page.locator(selector);
			const count = await element.count();

			if (count > 0) {
				await element.first().waitFor({ state: 'hidden', timeout });
			}
		}
	} catch (error) {
		// If loading spinner not found or timeout, continue
		console.warn('Loading spinner wait timeout or not found:', error);
	}
}

/**
 * Wait for specific API response
 * @param page - Playwright page instance
 * @param endpoint - API endpoint to wait for
 * @param timeout - Maximum wait time in milliseconds (default: 10000)
 */
export async function waitForApiResponse(
	page: Page,
	endpoint: string,
	timeout = 10000
): Promise<void> {
	await page.waitForResponse(
		(response) => response.url().includes(endpoint) && response.status() === 200,
		{ timeout }
	);
}

/**
 * Wait for multiple API responses
 * @param page - Playwright page instance
 * @param endpoints - Array of API endpoints to wait for
 * @param timeout - Maximum wait time in milliseconds (default: 10000)
 */
export async function waitForMultipleApiResponses(
	page: Page,
	endpoints: string[],
	timeout = 10000
): Promise<void> {
	const promises = endpoints.map((endpoint) => waitForApiResponse(page, endpoint, timeout));
	await Promise.all(promises);
}

/**
 * Generate random test data
 */
export const generateTestData = {
	/**
	 * Generate a random test email
	 */
	email: (): string => {
		const timestamp = Date.now();
		const random = Math.floor(Math.random() * 10000);
		return `test.user.${timestamp}.${random}@example.com`;
	},

	/**
	 * Generate a random test phone number
	 * @param countryCode - Country code (default: "+1")
	 */
	phoneNumber: (countryCode = '+1'): string => {
		const areaCode = Math.floor(Math.random() * 900) + 100;
		const prefix = Math.floor(Math.random() * 900) + 100;
		const lineNumber = Math.floor(Math.random() * 9000) + 1000;
		return `${countryCode}${areaCode}${prefix}${lineNumber}`;
	},

	/**
	 * Generate a random test name
	 */
	name: (): string => {
		const firstNames = ['John', 'Jane', 'Alex', 'Sam', 'Chris', 'Taylor', 'Jordan', 'Morgan'];
		const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller'];

		const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
		const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];

		return `${firstName} ${lastName}`;
	},

	/**
	 * Generate a random test company name
	 */
	companyName: (): string => {
		const prefixes = ['Tech', 'Global', 'Smart', 'Digital', 'Cloud', 'Innovative'];
		const suffixes = ['Solutions', 'Systems', 'Corp', 'Inc', 'Technologies', 'Services'];

		const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
		const suffix = suffixes[Math.floor(Math.random() * suffixes.length)];

		return `${prefix} ${suffix}`;
	},

	/**
	 * Generate a random password
	 * @param length - Password length (default: 12)
	 */
	password: (length = 12): string => {
		const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
		let password = '';
		for (let i = 0; i < length; i++) {
			password += chars.charAt(Math.floor(Math.random() * chars.length));
		}
		return password;
	},

	/**
	 * Generate a random string
	 * @param length - String length (default: 10)
	 */
	randomString: (length = 10): string => {
		const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
		let result = '';
		for (let i = 0; i < length; i++) {
			result += chars.charAt(Math.floor(Math.random() * chars.length));
		}
		return result;
	}
};

/**
 * Take a screenshot with a descriptive name
 * @param page - Playwright page instance
 * @param name - Screenshot name/description
 */
export async function takeScreenshot(page: Page, name: string): Promise<void> {
	const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
	const filename = `${name}_${timestamp}.png`;

	await page.screenshot({
		path: `e2e/screenshots/${filename}`,
		fullPage: true
	});

	console.log(`Screenshot saved: ${filename}`);
}

/**
 * Clear database (calls backend API to clear test data)
 * @param page - Playwright page instance
 */
export async function clearDatabase(page: Page): Promise<void> {
	try {
		await page.evaluate(async () => {
			const token = localStorage.getItem('accessToken');
			await fetch('/api/v1/test/clear-database', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				}
			});
		});

		console.log('Database cleared successfully');
	} catch (error) {
		console.warn('Failed to clear database:', error);
	}
}

/**
 * Seed database with test data
 * @param page - Playwright page instance
 * @param data - Test data to seed
 */
export async function seedDatabase(page: Page, data?: Record<string, unknown>): Promise<void> {
	try {
		await page.evaluate(
			async (seedData) => {
				const token = localStorage.getItem('accessToken');
				await fetch('/api/v1/test/seed-database', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						Authorization: `Bearer ${token}`
					},
					body: JSON.stringify(seedData || {})
				});
			},
			data || {}
		);

		console.log('Database seeded successfully');
	} catch (error) {
		console.warn('Failed to seed database:', error);
	}
}

/**
 * Wait for navigation to complete
 * @param page - Playwright page instance
 * @param url - URL pattern to wait for
 * @param timeout - Maximum wait time in milliseconds (default: 5000)
 */
export async function waitForNavigation(
	page: Page,
	url: string,
	timeout = 5000
): Promise<void> {
	await page.waitForURL(url, { timeout });
}

/**
 * Wait for element to be stable (not animating)
 * @param page - Playwright page instance
 * @param selector - Element selector
 * @param timeout - Maximum wait time in milliseconds (default: 5000)
 */
export async function waitForElementStable(
	page: Page,
	selector: string,
	timeout = 5000
): Promise<void> {
	const element = page.locator(selector);
	await element.waitFor({ state: 'visible', timeout });

	// Wait for any animations to complete
	await page.waitForTimeout(300);
}

/**
 * Retry an action until it succeeds or timeout
 * @param action - Async function to retry
 * @param maxAttempts - Maximum number of attempts (default: 3)
 * @param delay - Delay between attempts in milliseconds (default: 1000)
 */
export async function retryAction<T>(
	action: () => Promise<T>,
	maxAttempts = 3,
	delay = 1000
): Promise<T> {
	let lastError: Error | null = null;

	for (let attempt = 1; attempt <= maxAttempts; attempt++) {
		try {
			return await action();
		} catch (error) {
			lastError = error as Error;
			console.warn(`Attempt ${attempt} failed:`, error);

			if (attempt < maxAttempts) {
				await new Promise((resolve) => setTimeout(resolve, delay));
			}
		}
	}

	throw lastError || new Error('Retry action failed');
}

/**
 * Fill form fields from an object
 * @param page - Playwright page instance
 * @param formData - Object with field names and values
 */
export async function fillForm(
	page: Page,
	formData: Record<string, string>
): Promise<void> {
	for (const [fieldName, value] of Object.entries(formData)) {
		const input = page.locator(`input[name="${fieldName}"], textarea[name="${fieldName}"]`);
		await input.fill(value);
	}
}

/**
 * Get all console messages from page
 * @param page - Playwright page instance
 */
export function captureConsoleMessages(page: Page): {
	messages: string[];
	errors: string[];
} {
	const messages: string[] = [];
	const errors: string[] = [];

	page.on('console', (msg) => {
		const text = msg.text();
		messages.push(text);

		if (msg.type() === 'error') {
			errors.push(text);
		}
	});

	return { messages, errors };
}

/**
 * Check if element is in viewport
 * @param page - Playwright page instance
 * @param selector - Element selector
 */
export async function isInViewport(page: Page, selector: string): Promise<boolean> {
	const element = page.locator(selector);
	return await element.evaluate((el) => {
		const rect = el.getBoundingClientRect();
		return (
			rect.top >= 0 &&
			rect.left >= 0 &&
			rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
			rect.right <= (window.innerWidth || document.documentElement.clientWidth)
		);
	});
}

/**
 * Scroll element into view
 * @param page - Playwright page instance
 * @param selector - Element selector
 */
export async function scrollIntoView(page: Page, selector: string): Promise<void> {
	const element = page.locator(selector);
	await element.scrollIntoViewIfNeeded();
}

/**
 * Wait for WebSocket connection
 * @param page - Playwright page instance
 * @param timeout - Maximum wait time in milliseconds (default: 10000)
 */
export async function waitForWebSocketConnection(
	page: Page,
	timeout = 10000
): Promise<void> {
	await page.waitForFunction(
		() => {
			return (window as any).wsConnected === true;
		},
		{ timeout }
	);
}

/**
 * Mock API response
 * @param page - Playwright page instance
 * @param endpoint - API endpoint to mock
 * @param response - Mock response data
 */
export async function mockApiResponse(
	page: Page,
	endpoint: string,
	response: unknown
): Promise<void> {
	await page.route(`**${endpoint}`, async (route) => {
		await route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: JSON.stringify(response)
		});
	});
}

/**
 * Get localStorage value
 * @param page - Playwright page instance
 * @param key - localStorage key
 */
export async function getLocalStorageItem(page: Page, key: string): Promise<string | null> {
	return await page.evaluate((storageKey) => {
		return localStorage.getItem(storageKey);
	}, key);
}

/**
 * Set localStorage value
 * @param page - Playwright page instance
 * @param key - localStorage key
 * @param value - Value to set
 */
export async function setLocalStorageItem(
	page: Page,
	key: string,
	value: string
): Promise<void> {
	await page.evaluate(
		({ storageKey, storageValue }) => {
			localStorage.setItem(storageKey, storageValue);
		},
		{ storageKey: key, storageValue: value }
	);
}

/**
 * Clear localStorage
 * @param page - Playwright page instance
 */
export async function clearLocalStorage(page: Page): Promise<void> {
	await page.evaluate(() => {
		localStorage.clear();
	});
}
