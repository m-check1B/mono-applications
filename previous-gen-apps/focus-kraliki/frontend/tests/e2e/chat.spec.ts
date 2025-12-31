import { test, expect } from '@playwright/test';

test.describe('AI Chat Interface', () => {
	test.beforeEach(async ({ page }) => {
		// Login first (assuming login is required)
		await page.goto('http://127.0.0.1:5175/login');

		// Fill in login form
		await page.fill('input[name="email"]', 'test@example.com');
		await page.fill('input[name="password"]', 'testpassword');
		await page.click('button[type="submit"]');

		// Wait for redirect to dashboard
		await page.waitForURL('**/dashboard');

		// Navigate to chat
		await page.goto('http://127.0.0.1:5175/dashboard/chat');
	});

	test('should load chat interface', async ({ page }) => {
		await expect(page.locator('h1:has-text("AI Chat")')).toBeVisible();
		await expect(page.locator('input[placeholder*="Type your message"]')).toBeVisible();
	});

	test('should send a message and receive response', async ({ page }) => {
		const input = page.locator('input[placeholder*="Type your message"]');
		const sendButton = page.locator('button:has-text("Send")');

		// Type a message
		await input.fill('Hello, AI assistant!');
		await sendButton.click();

		// Wait for user message to appear
		await expect(page.locator('text=Hello, AI assistant!')).toBeVisible();

		// Wait for assistant response (with longer timeout)
		await expect(page.locator('.markdown-content').first()).toBeVisible({ timeout: 10000 });
	});

	test('should display welcome message on first load', async ({ page }) => {
		await expect(page.locator('text=Hi! I\'m your AI assistant')).toBeVisible();
	});

	test('should clear chat history', async ({ page }) => {
		// Click clear chat button
		await page.click('button:has-text("Clear Chat")');

		// Confirm dialog
		page.on('dialog', (dialog) => dialog.accept());

		// Check that chat is cleared
		await expect(page.locator('text=Chat cleared')).toBeVisible();
	});

	test('should render markdown in AI responses', async ({ page }) => {
		const input = page.locator('input[placeholder*="Type your message"]');
		const sendButton = page.locator('button:has-text("Send")');

		// Ask for a code example
		await input.fill('Show me a simple Python function');
		await sendButton.click();

		// Wait for response with code block
		await page.waitForSelector('.hljs', { timeout: 15000 });

		// Check that syntax highlighting is applied
		const codeBlock = page.locator('.hljs').first();
		await expect(codeBlock).toBeVisible();
	});
});
