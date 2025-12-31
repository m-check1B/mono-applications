import { chromium, FullConfig } from '@playwright/test';
import path from 'path';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup for Focus by Kraliki E2E tests');

  // Create test directories
  const testResultsDir = path.join(process.cwd(), 'test-results');
  const screenshotsDir = path.join(testResultsDir, 'screenshots');
  const videosDir = path.join(testResultsDir, 'videos');

  const fs = require('fs');
  if (!fs.existsSync(testResultsDir)) {
    fs.mkdirSync(testResultsDir, { recursive: true });
  }
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }
  if (!fs.existsSync(videosDir)) {
    fs.mkdirSync(videosDir, { recursive: true });
  }

  // Generate test user credentials
  const timestamp = Date.now();
  const testUser = {
    email: `test-${timestamp}@focus-kraliki.test`,
    name: `Test User ${timestamp}`,
    password: 'test123456'
  };

  // Save test user data for global access
  const testDataPath = path.join(testResultsDir, 'test-user.json');
  fs.writeFileSync(testDataPath, JSON.stringify(testUser, null, 2));

  console.log('✅ Global setup completed');
  console.log(`📁 Test results directory: ${testResultsDir}`);
  console.log(`👤 Test user: ${testUser.email}`);

  return {
    testUser,
    testResultsDir,
    screenshotsDir,
    videosDir
  };
}

export default globalSetup;