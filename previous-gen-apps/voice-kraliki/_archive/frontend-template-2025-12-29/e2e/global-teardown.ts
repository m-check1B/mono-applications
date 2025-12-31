import { FullConfig } from '@playwright/test';
import { BACKEND_URL } from './fixtures/test-data.js';
import * as path from 'node:path';
import * as fs from 'node:fs';
import { fileURLToPath } from 'node:url';

// ESM-compatible __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Global teardown for E2E tests
 * Runs once after all tests complete
 */
async function globalTeardown(config: FullConfig) {
	console.log('\n🧹 Starting E2E test cleanup...');

	// Clean up test data (optional - only if backend supports it)
	if (process.env.CLEANUP_TEST_DATA === 'true') {
		console.log('🗑️  Cleaning up test database...');
		await cleanupTestData();
	}

	// Clean up authentication state
	console.log('🔐 Cleaning up authentication state...');
	cleanupAuthState();

	// Clean up old screenshots (optional)
	if (process.env.CLEANUP_SCREENSHOTS === 'true') {
		console.log('📸 Cleaning up old screenshots...');
		cleanupOldScreenshots();
	}

	// Generate summary report
	console.log('📊 Test run summary:');
	printTestSummary();

	console.log('✅ E2E test cleanup complete!\n');
}

/**
 * Clean up test data from database
 */
async function cleanupTestData(): Promise<void> {
	try {
		const response = await fetch(`${BACKEND_URL}/api/v1/test/cleanup`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			signal: AbortSignal.timeout(10000)
		});

		if (response.ok) {
			console.log('✓ Test data cleaned up successfully');
		} else {
			console.warn('⚠️  Failed to cleanup test data (endpoint may not exist)');
		}
	} catch (error) {
		console.warn('⚠️  Could not cleanup test data:', error);
	}
}

/**
 * Clean up authentication state files
 */
function cleanupAuthState(): void {
	try {
		const authDir = path.join(__dirname, '.auth');

		if (fs.existsSync(authDir)) {
			const files = fs.readdirSync(authDir);

			for (const file of files) {
				const filePath = path.join(authDir, file);
				fs.unlinkSync(filePath);
			}

			console.log('✓ Authentication state cleaned up');
		}
	} catch (error) {
		console.warn('⚠️  Could not cleanup auth state:', error);
	}
}

/**
 * Clean up old screenshots (keep only recent ones)
 */
function cleanupOldScreenshots(): void {
	try {
		const screenshotsDir = path.join(__dirname, 'screenshots');

		if (!fs.existsSync(screenshotsDir)) {
			return;
		}

		const files = fs.readdirSync(screenshotsDir);
		const now = Date.now();
		const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days

		let deletedCount = 0;

		for (const file of files) {
			const filePath = path.join(screenshotsDir, file);
			const stats = fs.statSync(filePath);
			const age = now - stats.mtime.getTime();

			if (age > maxAge) {
				fs.unlinkSync(filePath);
				deletedCount++;
			}
		}

		if (deletedCount > 0) {
			console.log(`✓ Cleaned up ${deletedCount} old screenshot(s)`);
		}
	} catch (error) {
		console.warn('⚠️  Could not cleanup old screenshots:', error);
	}
}

/**
 * Print test summary information
 */
function printTestSummary(): void {
	const resultsDir = path.join(__dirname, 'test-results');

	if (!fs.existsSync(resultsDir)) {
		console.log('  No test results found');
		return;
	}

	try {
		const files = fs.readdirSync(resultsDir);
		const testResultFiles = files.filter((f) => f.endsWith('.json'));

		if (testResultFiles.length > 0) {
			console.log(`  Test result files: ${testResultFiles.length}`);
		}

		// Check for failed tests
		const hasFailures = files.some((f) => f.includes('failed'));
		if (hasFailures) {
			console.log('  ⚠️  Some tests failed - check the report for details');
		}
	} catch (error) {
		console.warn('  Could not read test results:', error);
	}
}

export default globalTeardown;
