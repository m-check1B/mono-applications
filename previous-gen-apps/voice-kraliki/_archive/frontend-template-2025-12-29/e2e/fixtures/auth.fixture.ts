import { test as base, Page, BrowserContext } from '@playwright/test';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';
import { TEST_USER } from './test-data.js';

// ESM-compatible __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Authentication state stored for reuse across tests
 */
export interface AuthState {
	accessToken: string;
	refreshToken: string;
	expiresAt: number;
	user: {
		id: string;
		email: string;
		name: string;
		role: string;
	};
}

/**
 * Extended test context with authentication fixtures
 */
export interface AuthFixtures {
	/**
	 * Page with authenticated user context
	 */
	authenticatedPage: Page;

	/**
	 * Browser context with authenticated state
	 */
	authenticatedContext: BrowserContext;

	/**
	 * Current authentication state
	 */
	authState: AuthState;

	/**
	 * Helper to log in programmatically
	 */
	loginAs: (email: string, password: string) => Promise<AuthState>;

	/**
	 * Helper to clear authentication and logout
	 */
	logout: () => Promise<void>;
}

const AUTH_STATE_PATH = path.join(__dirname, '../.auth/user.json');

/**
 * Performs login and returns authentication state
 */
async function performLogin(
	page: Page,
	email: string,
	password: string
): Promise<AuthState> {
	// Navigate to login page
	await page.goto('/auth/login');

	// Fill in credentials
	await page.fill('input[name="email"], input[type="email"]', email);
	await page.fill('input[name="password"], input[type="password"]', password);

	// Wait for response before clicking submit
	const responsePromise = page.waitForResponse(
		(response) =>
			response.url().includes('/api/v1/auth/login') && response.status() === 200
	);

	// Click login button
	await page.click('button[type="submit"]');

	// Wait for login response
	const response = await responsePromise;
	const authData = (await response.json()) as AuthState;

	// Wait for redirect to dashboard
	await page.waitForURL('**/dashboard', { timeout: 10000 });

	// Store auth data in localStorage for subsequent page loads
	await page.evaluate((auth) => {
		localStorage.setItem('accessToken', auth.accessToken);
		localStorage.setItem('refreshToken', auth.refreshToken);
		localStorage.setItem('expiresAt', auth.expiresAt.toString());
		localStorage.setItem('user', JSON.stringify(auth.user));
	}, authData);

	return authData;
}

/**
 * Saves authentication state to file for reuse
 */
function saveAuthState(authState: AuthState): void {
	const dir = path.dirname(AUTH_STATE_PATH);
	if (!fs.existsSync(dir)) {
		fs.mkdirSync(dir, { recursive: true });
	}
	fs.writeFileSync(AUTH_STATE_PATH, JSON.stringify(authState, null, 2));
}

/**
 * Loads authentication state from file
 */
function loadAuthState(): AuthState | null {
	try {
		if (fs.existsSync(AUTH_STATE_PATH)) {
			const data = fs.readFileSync(AUTH_STATE_PATH, 'utf-8');
			const authState = JSON.parse(data) as AuthState;

			// Check if token is still valid (not expired)
			if (authState.expiresAt && authState.expiresAt > Date.now()) {
				return authState;
			}
		}
	} catch (error) {
		console.warn('Failed to load auth state:', error);
	}
	return null;
}

/**
 * Applies authentication state to browser context
 */
async function applyAuthState(context: BrowserContext, authState: AuthState): Promise<void> {
	// Add localStorage state to context
	await context.addInitScript((auth) => {
		localStorage.setItem('accessToken', auth.accessToken);
		localStorage.setItem('refreshToken', auth.refreshToken);
		localStorage.setItem('expiresAt', auth.expiresAt.toString());
		localStorage.setItem('user', JSON.stringify(auth.user));
	}, authState);
}

/**
 * Extended test fixture with authentication support
 */
export const test = base.extend<AuthFixtures>({
	/**
	 * Authenticated browser context fixture
	 * Reuses stored auth state if available, otherwise performs fresh login
	 */
	authenticatedContext: async ({ browser }, use) => {
		// Try to load existing auth state
		let authState = loadAuthState();

		// Create new context
		const context = await browser.newContext();

		if (authState) {
			// Apply existing auth state
			await applyAuthState(context, authState);
		} else {
			// Perform fresh login
			const page = await context.newPage();
			authState = await performLogin(page, TEST_USER.email, TEST_USER.password);
			saveAuthState(authState);
			await page.close();
		}

		await use(context);
		await context.close();
	},

	/**
	 * Authenticated page fixture
	 * Provides a page with authentication already set up
	 */
	authenticatedPage: async ({ authenticatedContext }, use) => {
		const page = await authenticatedContext.newPage();
		await use(page);
		await page.close();
	},

	/**
	 * Current authentication state fixture
	 */
	authState: async ({ authenticatedPage }, use) => {
		const authState = await authenticatedPage.evaluate(() => {
			const accessToken = localStorage.getItem('accessToken') || '';
			const refreshToken = localStorage.getItem('refreshToken') || '';
			const expiresAt = parseInt(localStorage.getItem('expiresAt') || '0', 10);
			const user = JSON.parse(localStorage.getItem('user') || '{}');

			return {
				accessToken,
				refreshToken,
				expiresAt,
				user
			};
		});

		await use(authState as AuthState);
	},

	/**
	 * Helper fixture to log in as different user
	 */
	loginAs: async ({ page }, use) => {
		const login = async (email: string, password: string): Promise<AuthState> => {
			const authState = await performLogin(page, email, password);
			saveAuthState(authState);
			return authState;
		};

		await use(login);
	},

	/**
	 * Helper fixture to logout
	 */
	logout: async ({ authenticatedPage }, use) => {
		const logoutFn = async (): Promise<void> => {
			// Call logout API
			await authenticatedPage.evaluate(async () => {
				await fetch('/api/v1/auth/logout', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						Authorization: `Bearer ${localStorage.getItem('accessToken')}`
					}
				});

				// Clear localStorage
				localStorage.removeItem('accessToken');
				localStorage.removeItem('refreshToken');
				localStorage.removeItem('expiresAt');
				localStorage.removeItem('user');
			});

			// Delete saved auth state
			if (fs.existsSync(AUTH_STATE_PATH)) {
				fs.unlinkSync(AUTH_STATE_PATH);
			}

			// Navigate to login page
			await authenticatedPage.goto('/auth/login');
		};

		await use(logoutFn);
	}
});

/**
 * Export expect from Playwright for convenience
 */
export { expect } from '@playwright/test';
