import { chromium, FullConfig } from '@playwright/test';
import { BACKEND_URL, FRONTEND_URL, TEST_USER } from './fixtures/test-data.js';
import * as path from 'node:path';
import * as fs from 'node:fs';
import { fileURLToPath } from 'node:url';

// ESM-compatible __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Global setup for E2E tests
 * Runs once before all tests
 */
async function globalSetup(config: FullConfig) {
	console.log('🚀 Starting E2E test setup...');

	// Create necessary directories
	const authDir = path.join(__dirname, '.auth');
	const screenshotsDir = path.join(__dirname, 'screenshots');
	const reportsDir = path.join(__dirname, 'test-results');

	for (const dir of [authDir, screenshotsDir, reportsDir]) {
		if (!fs.existsSync(dir)) {
			fs.mkdirSync(dir, { recursive: true });
			console.log(`✓ Created directory: ${dir}`);
		}
	}

	// Check if backend is running
	console.log('🔍 Checking backend availability...');
	const isBackendUp = await checkBackendHealth();

	if (!isBackendUp) {
		console.warn('⚠️  Backend is not responding. Some tests may fail.');
		console.warn(`    Expected backend URL: ${BACKEND_URL}`);
		console.warn('    Make sure the backend server is running.');
	} else {
		console.log('✓ Backend is available');
	}

	// Check if frontend is running
	console.log('🔍 Checking frontend availability...');
	const isFrontendUp = await checkFrontendHealth();

	if (!isFrontendUp) {
		console.warn('⚠️  Frontend is not responding. Tests will likely fail.');
		console.warn(`    Expected frontend URL: ${FRONTEND_URL}`);
		console.warn('    Make sure the frontend dev server is running.');
	} else {
		console.log('✓ Frontend is available');
	}

	// Create initial authentication state
	console.log('🔐 Setting up authentication state...');
	await setupAuthState();

	// Seed test data (optional - only if backend supports it)
	if (process.env.SEED_TEST_DATA === 'true') {
		console.log('🌱 Seeding test database...');
		await seedTestData();
	}

	console.log('✅ E2E test setup complete!\n');
}

/**
 * Check if backend is healthy and responding
 */
async function checkBackendHealth(): Promise<boolean> {
	try {
		const response = await fetch(`${BACKEND_URL}/health`, {
			method: 'GET',
			signal: AbortSignal.timeout(5000)
		});

		return response.ok;
	} catch (error) {
		// Try alternative health check endpoint
		try {
			const response = await fetch(`${BACKEND_URL}/api/health`, {
				method: 'GET',
				signal: AbortSignal.timeout(5000)
			});
			return response.ok;
		} catch {
			return false;
		}
	}
}

/**
 * Check if frontend is healthy and responding
 */
async function checkFrontendHealth(): Promise<boolean> {
	try {
		const response = await fetch(FRONTEND_URL, {
			method: 'GET',
			signal: AbortSignal.timeout(5000)
		});

		return response.ok;
	} catch (error) {
		return false;
	}
}

/**
 * Setup authentication state for test user
 */
async function setupAuthState(): Promise<void> {
	const browser = await chromium.launch();
	const context = await browser.newContext();
	const page = await context.newPage();

	try {
		// Navigate to login page
		await page.goto(`${FRONTEND_URL}/auth/login`, { timeout: 10000 });

		// Fill in credentials
		await page.fill('input[name="email"], input[type="email"]', TEST_USER.email);
		await page.fill('input[name="password"], input[type="password"]', TEST_USER.password);

		// Submit login form
		const responsePromise = page.waitForResponse(
			(response) =>
				response.url().includes('/api/v1/auth/login') &&
				(response.status() === 200 || response.status() === 201),
			{ timeout: 10000 }
		);

		await page.click('button[type="submit"]');

		// Wait for login response
		try {
			const response = await responsePromise;
			const authData = await response.json();

			// Save auth state
			const authStatePath = path.join(__dirname, '.auth', 'user.json');
			fs.writeFileSync(
				authStatePath,
				JSON.stringify(
					{
						accessToken: authData.access_token,
						refreshToken: authData.refresh_token,
						expiresAt: authData.expires_at || Date.now() + 3600000,
						user: authData.user || {
							id: 'test-user',
							email: TEST_USER.email,
							name: TEST_USER.name,
							role: TEST_USER.role
						}
					},
					null,
					2
				)
			);

			console.log('✓ Authentication state saved');
		} catch (error) {
			console.warn('⚠️  Failed to login test user. Tests will perform fresh logins.');
			console.warn('    Error:', error);
		}
	} catch (error) {
		console.warn('⚠️  Could not setup auth state:', error);
	} finally {
		await page.close();
		await context.close();
		await browser.close();
	}
}

/**
 * Seed test database with initial data
 */
async function seedTestData(): Promise<void> {
	try {
		const response = await fetch(`${BACKEND_URL}/api/v1/test/seed`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				users: true,
				companies: true,
				providers: true,
				calls: false // Don't seed calls to keep tests isolated
			}),
			signal: AbortSignal.timeout(10000)
		});

		if (response.ok) {
			console.log('✓ Test data seeded successfully');
		} else {
			console.warn('⚠️  Failed to seed test data (endpoint may not exist)');
		}
	} catch (error) {
		console.warn('⚠️  Could not seed test data:', error);
	}
}

export default globalSetup;
