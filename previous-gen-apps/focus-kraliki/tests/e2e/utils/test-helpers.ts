// Test utilities for authentication testing

export function generateTestUser() {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 10000);

  return {
    name: `Test User ${random}`,
    email: `test.user.${timestamp}.${random}@example.com`,
    password: `SecurePassword${random}!`
  };
}

export function validateApiResponse(response: any, expectedKeys: string[] = []) {
  if (!response || typeof response !== 'object') {
    throw new Error('Invalid response format');
  }

  // Check for standard success response structure
  if (response.result && response.result.data) {
    const data = response.result.data;

    // Check required keys
    for (const key of expectedKeys) {
      if (!data[key]) {
        throw new Error(`Missing required key: ${key}`);
      }
    }

    return data;
  }

  throw new Error('Response missing result.data structure');
}

export async function checkDatabaseRecord(email: string) {
  // This would typically query the database directly
  // For now, we'll return a mock implementation
  console.log(`🔍 Checking database for user: ${email}`);

  // In a real implementation, you would:
  // 1. Connect to the database
  // 2. Query for the user record
  // 3. Verify the record exists and has correct data
  // 4. Return the record or null

  return {
    id: 'mock-id',
    email: email,
    name: 'Mock User',
    createdAt: new Date().toISOString()
  };
}

export async function simulateNetworkFailure(page: any) {
  await page.route('**/*', route => {
    if (route.request().url().includes('/trpc/')) {
      route.abort('failed');
    } else {
      route.continue();
    }
  });
}

export async function simulateSlowNetwork(page: any, delay: number = 3000) {
  await page.route('**/*', async route => {
    if (route.request().url().includes('/trpc/')) {
      await new Promise(resolve => setTimeout(resolve, delay));
      await route.continue();
    } else {
      await route.continue();
    }
  });
}

export function generateInvalidEmails(): string[] {
  return [
    'invalid-email',
    'user@',
    '@domain.com',
    'user.domain.com',
    'user@domain',
    'user..user@domain.com',
    'user@domain..com',
    'user@domain.c',
    'user@domain.toolongtld'
  ];
}

export function generateWeakPasswords(): string[] {
  return [
    '123',
    'password',
    'qwerty',
    '111111',
    'abc123',
    'letmein',
    'welcome',
    'admin',
    'test',
    ''
  ];
}

export function generateTestUsers(count: number = 1) {
  const users = [];
  for (let i = 0; i < count; i++) {
    users.push(generateTestUser());
  }
  return users;
}

export async function waitForElementWithRetry(page: any, selector: string, timeout: number = 5000, retries: number = 3) {
  let lastError;

  for (let i = 0; i < retries; i++) {
    try {
      await page.waitForSelector(selector, { timeout: timeout / retries });
      return await page.$(selector);
    } catch (error) {
      lastError = error;
      await page.waitForTimeout(1000); // Wait before retry
    }
  }

  throw lastError;
}

export async function takeScreenshotOnError(page: any, testName: string) {
  try {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    await page.screenshot({
      path: `test-results/errors/${testName}-error-${timestamp}.png`,
      fullPage: true
    });
  } catch (error) {
    console.error('Failed to take error screenshot:', error);
  }
}

export function createPerformanceMetrics() {
  return {
    startTime: Date.now(),
    metrics: {} as Record<string, number>,

    mark(name: string) {
      this.metrics[name] = Date.now() - this.startTime;
    },

    getMetrics() {
      return {
        ...this.metrics,
        totalTime: Date.now() - this.startTime
      };
    },

    log() {
      console.log('📊 Performance Metrics:', this.getMetrics());
    }
  };
}

export async function simulateDeviceConditions(page: any, deviceType: 'mobile' | 'tablet' | 'desktop') {
  const viewports = {
    mobile: { width: 375, height: 667 },
    tablet: { width: 768, height: 1024 },
    desktop: { width: 1920, height: 1080 }
  };

  await page.setViewportSize(viewports[deviceType]);

  if (deviceType === 'mobile') {
    await page.emulateMedia({ colorScheme: 'light' });
  }
}

export async function checkAccessibility(page: any) {
  // Basic accessibility checks
  const issues: string[] = [];

  // Check for alt text on images
  const imagesWithoutAlt = await page.$$eval('img:not([alt])', imgs => imgs.length);
  if (imagesWithoutAlt > 0) {
    issues.push(`${imagesWithoutAlt} images missing alt text`);
  }

  // Check for form labels
  const inputsWithoutLabels = await page.$$eval('input:not([aria-label]):not([id])', inputs =>
    inputs.filter(input => !input.labels || input.labels.length === 0).length
  );
  if (inputsWithoutLabels > 0) {
    issues.push(`${inputsWithoutLabels} inputs missing labels`);
  }

  // Check for color contrast (simplified)
  const lowContrastElements = await page.$$eval('[style*="color"]', elements => {
    return elements.length; // In real implementation, you'd calculate contrast ratios
  });

  return {
    issues,
    score: issues.length === 0 ? 100 : Math.max(0, 100 - (issues.length * 10))
  };
}

export async function clearBrowserData(page: any) {
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
    document.cookie.split(';').forEach(cookie => {
      document.cookie = cookie.replace(/^ +/, '').replace(/=.*/, '=;expires=' + new Date().toUTCString() + ';path=/');
    });
  });
}

export function logTestStep(stepName: string, details: any = {}) {
  const timestamp = new Date().toISOString();
  console.log(`\n📋 [${timestamp}] ${stepName}`);
  if (Object.keys(details).length > 0) {
    console.log('   Details:', JSON.stringify(details, null, 2));
  }
}

export async function measureResponseTime(page: any, action: () => Promise<any>) {
  const startTime = Date.now();
  const result = await action();
  const endTime = Date.now();

  return {
    result,
    responseTime: endTime - startTime
  };
}

export function generateTestReport(testResults: any[]) {
  const passed = testResults.filter(r => r.status === 'passed').length;
  const failed = testResults.filter(r => r.status === 'failed').length;
  const skipped = testResults.filter(r => r.status === 'skipped').length;

  return {
    total: testResults.length,
    passed,
    failed,
    skipped,
    passRate: (passed / testResults.length) * 100,
    timestamp: new Date().toISOString(),
    results: testResults
  };
}