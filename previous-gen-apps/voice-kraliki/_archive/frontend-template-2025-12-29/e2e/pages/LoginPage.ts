import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for Login Page
 * Handles all interactions with the login form
 */
export class LoginPage {
	readonly page: Page;

	// Locators
	readonly emailInput: Locator;
	readonly passwordInput: Locator;
	readonly loginButton: Locator;
	readonly errorMessage: Locator;
	readonly registerLink: Locator;
	readonly forgotPasswordLink: Locator;
	readonly rememberMeCheckbox: Locator;

	constructor(page: Page) {
		this.page = page;

		// Initialize locators
		this.emailInput = page.locator('input[name="email"], input[type="email"]');
		this.passwordInput = page.locator('input[name="password"], input[type="password"]');
		this.loginButton = page.locator('button[type="submit"]');
		this.errorMessage = page.locator('[role="alert"], .error-message, .alert-error');
		this.registerLink = page.locator('a[href*="register"]');
		this.forgotPasswordLink = page.locator('a[href*="forgot-password"]');
		this.rememberMeCheckbox = page.locator('input[type="checkbox"][name*="remember"]');
	}

	/**
	 * Navigate to the login page
	 */
	async goto(): Promise<void> {
		await this.page.goto('/auth/login');
		await this.waitForPageLoad();
	}

	/**
	 * Wait for login page to fully load
	 */
	async waitForPageLoad(): Promise<void> {
		await expect(this.emailInput).toBeVisible({ timeout: 10000 });
		await expect(this.passwordInput).toBeVisible({ timeout: 10000 });
		await expect(this.loginButton).toBeVisible({ timeout: 10000 });
	}

	/**
	 * Check if login form is visible
	 */
	async isFormVisible(): Promise<boolean> {
		try {
			await expect(this.emailInput).toBeVisible({ timeout: 5000 });
			await expect(this.passwordInput).toBeVisible({ timeout: 5000 });
			await expect(this.loginButton).toBeVisible({ timeout: 5000 });
			return true;
		} catch {
			return false;
		}
	}

	/**
	 * Fill in email field
	 */
	async fillEmail(email: string): Promise<void> {
		await this.emailInput.clear();
		await this.emailInput.fill(email);
	}

	/**
	 * Fill in password field
	 */
	async fillPassword(password: string): Promise<void> {
		await this.passwordInput.clear();
		await this.passwordInput.fill(password);
	}

	/**
	 * Click login button
	 */
	async clickLogin(): Promise<void> {
		await this.loginButton.click();
	}

	/**
	 * Toggle remember me checkbox
	 */
	async toggleRememberMe(): Promise<void> {
		if (await this.rememberMeCheckbox.isVisible()) {
			await this.rememberMeCheckbox.click();
		}
	}

	/**
	 * Perform complete login flow
	 * @param email - User email
	 * @param password - User password
	 * @param rememberMe - Whether to check remember me (optional)
	 */
	async login(email: string, password: string, rememberMe?: boolean): Promise<void> {
		await this.fillEmail(email);
		await this.fillPassword(password);

		if (rememberMe !== undefined && (await this.rememberMeCheckbox.isVisible())) {
			const isChecked = await this.rememberMeCheckbox.isChecked();
			if (isChecked !== rememberMe) {
				await this.toggleRememberMe();
			}
		}

		await this.clickLogin();
	}

	/**
	 * Perform login and wait for navigation to dashboard
	 * @param email - User email
	 * @param password - User password
	 */
	async loginAndWaitForDashboard(email: string, password: string): Promise<void> {
		await this.login(email, password);
		await this.page.waitForURL('**/dashboard', { timeout: 10000 });
	}

	/**
	 * Check if user is logged in (redirected away from login page)
	 */
	async isLoggedIn(): Promise<boolean> {
		try {
			// Wait a bit for potential redirect
			await this.page.waitForTimeout(1000);

			// Check if we're not on login page anymore
			const currentUrl = this.page.url();
			const isOnLoginPage = currentUrl.includes('/auth/login');

			// Also check if localStorage has auth tokens
			const hasAuthToken = await this.page.evaluate(() => {
				return localStorage.getItem('accessToken') !== null;
			});

			return !isOnLoginPage && hasAuthToken;
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
			return await this.errorMessage.textContent() || '';
		} catch {
			return '';
		}
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
	 * Validate that error message contains specific text
	 */
	async expectErrorMessage(expectedMessage: string): Promise<void> {
		await expect(this.errorMessage).toBeVisible();
		await expect(this.errorMessage).toContainText(expectedMessage);
	}

	/**
	 * Click register link
	 */
	async goToRegister(): Promise<void> {
		await this.registerLink.click();
		await this.page.waitForURL('**/auth/register', { timeout: 5000 });
	}

	/**
	 * Click forgot password link
	 */
	async goToForgotPassword(): Promise<void> {
		if (await this.forgotPasswordLink.isVisible()) {
			await this.forgotPasswordLink.click();
			await this.page.waitForURL('**/auth/forgot-password', { timeout: 5000 });
		}
	}

	/**
	 * Attempt login with invalid credentials
	 */
	async loginWithInvalidCredentials(): Promise<void> {
		await this.login('invalid@example.com', 'wrongpassword');
		// Wait for error message
		await expect(this.errorMessage).toBeVisible({ timeout: 5000 });
	}

	/**
	 * Clear all form fields
	 */
	async clearForm(): Promise<void> {
		await this.emailInput.clear();
		await this.passwordInput.clear();
	}

	/**
	 * Check if login button is enabled
	 */
	async isLoginButtonEnabled(): Promise<boolean> {
		return await this.loginButton.isEnabled();
	}

	/**
	 * Check if login button is loading/disabled during submission
	 */
	async isLoginButtonLoading(): Promise<boolean> {
		const isDisabled = !(await this.loginButton.isEnabled());
		const hasLoadingClass = await this.loginButton.evaluate((el) => {
			return (
				el.classList.contains('loading') ||
				el.classList.contains('disabled') ||
				el.hasAttribute('disabled')
			);
		});
		return isDisabled || hasLoadingClass;
	}
}
