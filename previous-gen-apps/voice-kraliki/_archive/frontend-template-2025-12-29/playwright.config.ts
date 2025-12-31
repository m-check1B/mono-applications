import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration
 * See https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
	// Test directory
	testDir: './e2e',

	// Test file pattern
	testMatch: '**/*.spec.ts',

	// Maximum time one test can run for
	timeout: 30 * 1000,

	// Expect timeout for assertions
	expect: {
		timeout: 10000
	},

	// Run tests in files in parallel
	fullyParallel: true,

	// Fail the build on CI if you accidentally left test.only in the source code
	forbidOnly: !!process.env.CI,

	// Retry on CI only
	retries: process.env.CI ? 2 : 0,

	// Number of parallel workers
	workers: process.env.CI ? 1 : undefined,

	// Reporter configuration
	reporter: [
		['html', { outputFolder: 'e2e/test-results/html-report', open: 'never' }],
		['json', { outputFile: 'e2e/test-results/results.json' }],
		['junit', { outputFile: 'e2e/test-results/junit.xml' }],
		['list']
	],

	// Shared settings for all projects
	use: {
		// Base URL for navigation
		baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',

		// Collect trace when retrying the failed test
		trace: 'on-first-retry',

		// Screenshot on failure
		screenshot: 'only-on-failure',

		// Video on failure
		video: 'retain-on-failure',

		// Maximum time for actions (click, fill, etc.)
		actionTimeout: 10000,

		// Maximum time for navigation
		navigationTimeout: 10000,

		// Capture console logs
		launchOptions: {
			slowMo: process.env.SLOW_MO ? parseInt(process.env.SLOW_MO, 10) : 0
		}
	},

	// Global setup and teardown
	globalSetup: './e2e/global-setup.ts',
	globalTeardown: './e2e/global-teardown.ts',

	// Configure projects for major browsers
	projects: [
		{
			name: 'chromium',
			use: { ...devices['Desktop Chrome'] }
		},

		{
			name: 'firefox',
			use: { ...devices['Desktop Firefox'] }
		},

		{
			name: 'webkit',
			use: { ...devices['Desktop Safari'] }
		},

		// Mobile viewports
		{
			name: 'mobile-chrome',
			use: { ...devices['Pixel 5'] }
		},

		{
			name: 'mobile-safari',
			use: { ...devices['iPhone 13'] }
		},

		// Tablet viewports
		{
			name: 'tablet',
			use: { ...devices['iPad Pro'] }
		}
	],

	// Run local dev server before starting tests (optional)
	webServer: process.env.SKIP_SERVER
		? undefined
		: {
				command: 'npm run dev',
				url: 'http://localhost:3000',
				reuseExistingServer: !process.env.CI,
				timeout: 120 * 1000,
				stdout: 'ignore',
				stderr: 'pipe'
		  }
});
