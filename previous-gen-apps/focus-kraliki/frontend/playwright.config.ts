import type { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
	testDir: './tests/e2e',
	timeout: 30000,
	fullyParallel: true,
	forbidOnly: !!process.env.CI,
	retries: process.env.CI ? 2 : 0,
	workers: process.env.CI ? 1 : undefined,
	reporter: 'html',

	use: {
		baseURL: 'http://127.0.0.1:5175',
		trace: 'on-first-retry',
		screenshot: 'only-on-failure',
		video: 'retain-on-failure'
	},

	projects: [
		{
			name: 'chromium',
			use: {
				...require('@playwright/test').devices['Desktop Chrome']
			}
		}
	],

	webServer: {
		command: 'pnpm run preview',
		port: 5175,
		timeout: 120000,
		reuseExistingServer: !process.env.CI
	}
};

export default config;
