/**
 * Stack 2025 Testing Core
 * Automated testing framework for all Stack 2025 apps
 */

export * from './app-tester';
export * from './test-runner';
export * from './user-agent';
export * from './test-scenarios';
export * from './health-checker';
export * from './frontend-tester';
export * from './integration-tests';
export * from './types';

// Convenience exports for common use cases
export { TestRunner, createTestRunner, defaultConfigs } from './test-runner';
export { AppTester } from './app-tester';
export { 
  runDevelopmentTests, 
  runCiTests, 
  runSmokeTests, 
  checkAllAppsRunning,
  STACK_2025_APPS,
  TEST_CONFIGS 
} from './integration-tests';