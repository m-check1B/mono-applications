import { FullConfig } from '@playwright/test';
import path from 'path';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global teardown for Focus by Kraliki E2E tests');

  // Clean up test data
  const testResultsDir = path.join(process.cwd(), 'test-results');
  const testDataPath = path.join(testResultsDir, 'test-user.json');

  const fs = require('fs');
  if (fs.existsSync(testDataPath)) {
    const testData = JSON.parse(fs.readFileSync(testDataPath, 'utf8'));

    // Generate test summary
    const summary = {
      testRun: 'completed',
      timestamp: new Date().toISOString(),
      testUser: testData.email,
      testResultsDir: testResultsDir,
      cleanup: 'successful'
    };

    const summaryPath = path.join(testResultsDir, 'test-summary.json');
    fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));

    // Clean up test user data file
    fs.unlinkSync(testDataPath);
  }

  console.log('✅ Global teardown completed');
  console.log(`📊 Test results available in: ${testResultsDir}`);
}

export default globalTeardown;