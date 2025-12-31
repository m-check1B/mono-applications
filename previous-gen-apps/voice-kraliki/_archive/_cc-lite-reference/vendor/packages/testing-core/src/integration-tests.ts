/**
 * Integration Tests - Pre-configured test suites for Stack 2025 apps
 */

import { TestRunner, TestRunnerConfig } from './test-runner';
import { AppConfig } from './types';

// Stack 2025 App Configurations
export const STACK_2025_APPS: AppConfig[] = [
  {
    name: 'Productivity Hub',
    frontendUrl: 'http://localhost:3000',
    backendUrl: 'http://localhost:3001',
    healthEndpoint: '/api/health',
    authEndpoint: '/api/auth/login',
    features: ['tasks', 'calendar', 'notes', 'dashboard'],
    testCredentials: {
      email: 'test@example.com',
      password: 'testpass123'
    }
  },
  {
    name: 'CC Light',
    frontendUrl: 'http://localhost:3020',
    backendUrl: 'http://localhost:3021', 
    healthEndpoint: '/api/health',
    authEndpoint: '/api/auth/signin',
    features: ['calls', 'contacts', 'analytics'],
    testCredentials: {
      email: 'admin@cclight.test',
      password: 'admin123'
    }
  },
  {
    name: 'Invoice App',
    frontendUrl: 'http://localhost:3030',
    backendUrl: 'http://localhost:3031',
    healthEndpoint: '/api/health', 
    authEndpoint: '/api/auth/login',
    features: ['invoices', 'clients', 'payments'],
    testCredentials: {
      email: 'invoice@test.com',
      password: 'invoice123'
    }
  }
];

// Test Runner Configurations
export const TEST_CONFIGS = {
  development: {
    apps: STACK_2025_APPS,
    parallel: false,
    timeout: 10000,
    retries: 1,
    headless: false,
    outputDir: './test-results'
  } as TestRunnerConfig,

  ci: {
    apps: STACK_2025_APPS,
    parallel: true,
    timeout: 30000,
    retries: 2,
    headless: true,
    outputDir: './ci-test-results'
  } as TestRunnerConfig,

  production: {
    apps: STACK_2025_APPS,
    parallel: true,
    timeout: 60000,
    retries: 3,
    headless: true,
    outputDir: './prod-test-results'
  } as TestRunnerConfig
};

// Quick test functions
export async function runDevelopmentTests(): Promise<void> {
  const runner = new TestRunner(TEST_CONFIGS.development);
  const results = await runner.runAll();
  
  const failed = results.filter(r => r.status === 'failed');
  if (failed.length > 0) {
    console.error(`❌ ${failed.length} apps failed tests in development mode`);
    process.exit(1);
  }
  
  console.log('✅ All development tests passed!');
}

export async function runCiTests(): Promise<void> {
  const runner = new TestRunner(TEST_CONFIGS.ci);
  const results = await runner.runAll();
  
  await runner.saveResults('./ci-test-results.json');
  
  const failed = results.filter(r => r.status === 'failed');
  if (failed.length > 0) {
    console.error(`❌ CI Tests Failed: ${failed.length}/${results.length} apps`);
    process.exit(1);
  }
  
  console.log('✅ All CI tests passed!');
}

export async function runProductionHealthCheck(): Promise<void> {
  const runner = new TestRunner({
    ...TEST_CONFIGS.production,
    scenarios: [] // Only health checks, no scenarios
  });
  
  const results = await runner.runAll();
  const failed = results.filter(r => r.status === 'failed');
  
  if (failed.length > 0) {
    throw new Error(`Production health check failed for: ${failed.map(f => f.app).join(', ')}`);
  }
}

// Individual app test functions
export async function testProductivityHub(): Promise<void> {
  const runner = new TestRunner({
    apps: [STACK_2025_APPS[0]],
    parallel: false,
    headless: false
  });
  
  await runner.runAll();
}

export async function testCcLight(): Promise<void> {
  const runner = new TestRunner({
    apps: [STACK_2025_APPS[1]], 
    parallel: false,
    headless: false
  });
  
  await runner.runAll();
}

export async function testInvoiceApp(): Promise<void> {
  const runner = new TestRunner({
    apps: [STACK_2025_APPS[2]],
    parallel: false, 
    headless: false
  });
  
  await runner.runAll();
}

// Test coverage analysis
export async function generateTestReport(): Promise<void> {
  const runner = new TestRunner(TEST_CONFIGS.ci);
  const results = await runner.runAll();
  
  // Generate detailed report
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      totalApps: results.length,
      appsTestedSuccessfully: results.filter(r => r.status === 'passed').length,
      totalTestCases: results.reduce((sum, r) => sum + r.summary.total, 0),
      passedTests: results.reduce((sum, r) => sum + r.summary.passed, 0),
      failedTests: results.reduce((sum, r) => sum + r.summary.failed, 0),
      totalDuration: results.reduce((sum, r) => sum + r.duration, 0),
      averageDuration: results.reduce((sum, r) => sum + r.duration, 0) / results.length,
      successRate: (results.reduce((sum, r) => sum + r.summary.passed, 0) / results.reduce((sum, r) => sum + r.summary.total, 0)) * 100
    },
    appResults: results.map(r => ({
      app: r.app,
      status: r.status,
      duration: r.duration,
      testSummary: r.summary,
      failedTests: r.tests.filter(t => t.status === 'failed').map(t => ({
        name: t.name,
        error: t.error,
        category: t.category
      }))
    }))
  };
  
  await runner.saveResults('./comprehensive-test-report.json');
  console.log('📊 Test report generated successfully');
}

// Performance testing
export async function runPerformanceTests(): Promise<void> {
  console.log('🚀 Running performance tests...');
  
  // Run tests multiple times to get average
  const iterations = 3;
  const allResults = [];
  
  for (let i = 0; i < iterations; i++) {
    console.log(`Performance test iteration ${i + 1}/${iterations}`);
    const runner = new TestRunner(TEST_CONFIGS.ci);
    const results = await runner.runAll();
    allResults.push(results);
  }
  
  // Calculate performance metrics
  const avgDuration = allResults.flat().reduce((sum, r) => sum + r.duration, 0) / allResults.flat().length;
  const avgSuccessRate = allResults.map(results => {
    const total = results.reduce((sum, r) => sum + r.summary.total, 0);
    const passed = results.reduce((sum, r) => sum + r.summary.passed, 0);
    return (passed / total) * 100;
  }).reduce((sum, rate) => sum + rate, 0) / iterations;
  
  console.log(`📈 Performance Results (${iterations} iterations):`);
  console.log(`Average Duration: ${avgDuration.toFixed(2)}ms`);
  console.log(`Average Success Rate: ${avgSuccessRate.toFixed(1)}%`);
  
  // Alert if performance is degraded
  const PERFORMANCE_THRESHOLD = 30000; // 30s
  const SUCCESS_RATE_THRESHOLD = 95; // 95%
  
  if (avgDuration > PERFORMANCE_THRESHOLD) {
    console.warn(`⚠️  Performance warning: Average test duration (${avgDuration}ms) exceeds threshold (${PERFORMANCE_THRESHOLD}ms)`);
  }
  
  if (avgSuccessRate < SUCCESS_RATE_THRESHOLD) {
    console.warn(`⚠️  Reliability warning: Success rate (${avgSuccessRate}%) below threshold (${SUCCESS_RATE_THRESHOLD}%)`);
  }
}

// Smoke tests - Quick essential checks
export async function runSmokeTests(): Promise<void> {
  console.log('💨 Running smoke tests...');
  
  const smokeConfig: TestRunnerConfig = {
    apps: STACK_2025_APPS,
    parallel: true,
    timeout: 5000, // Quick timeout
    retries: 0, // No retries for smoke tests
    headless: true,
    scenarios: [] // Only health checks
  };
  
  const runner = new TestRunner(smokeConfig);
  const results = await runner.runAll();
  
  const failed = results.filter(r => r.status === 'failed');
  if (failed.length > 0) {
    throw new Error(`Smoke tests failed for: ${failed.map(f => f.app).join(', ')}`);
  }
  
  console.log('✅ All smoke tests passed!');
}

// Utility function to check all apps are running
export async function checkAllAppsRunning(): Promise<boolean> {
  try {
    await runSmokeTests();
    return true;
  } catch {
    return false;
  }
}

export default {
  TEST_CONFIGS,
  STACK_2025_APPS,
  runDevelopmentTests,
  runCiTests,
  runProductionHealthCheck,
  generateTestReport,
  runPerformanceTests,
  runSmokeTests,
  checkAllAppsRunning
};