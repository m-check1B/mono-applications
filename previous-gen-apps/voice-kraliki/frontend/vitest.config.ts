import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
	plugins: [],

	test: {
		// Test environment
		environment: 'jsdom',

		// Global test setup
		globals: true,

		// Coverage configuration
		coverage: {
			provider: 'v8',
			reporter: ['text', 'html', 'json', 'lcov'],

			// Directories and files to include
			include: ['src/**/*.{js,ts,svelte}'],

			// Directories and files to exclude
			exclude: [
				'node_modules/',
				'dist/',
				'build/',
				'.svelte-kit/',
				'src/**/*.test.{js,ts}',
				'src/**/*.spec.{js,ts}',
				'src/test/',
				'src/**/__tests__/',
				'src/app.d.ts',
				'src/app.html',
				'src/**/*.config.{js,ts}',
			],

			// Coverage thresholds
			thresholds: {
				lines: 70,
				functions: 70,
				branches: 70,
				statements: 70,
			},

			// Other coverage options
			all: true,
			clean: true,
		},

		// Test file patterns
		include: ['src/**/*.{test,spec}.{js,ts}'],

		// Setup files
		setupFiles: [],

		// Test timeout
		testTimeout: 10000,

		// Hook timeout
		hookTimeout: 10000,

		// Watch options
		watch: false,

		// Reporter options
		reporters: ['verbose'],
	},

	resolve: {
		alias: {
			$lib: resolve('./src/lib'),
			$app: resolve('./.svelte-kit/runtime/app'),
		},
	},
});
