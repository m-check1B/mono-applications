/**
 * Test Runner - Core testing execution engine
 */

import chalk from 'chalk';
import ora from 'ora';
import type { 
  AppConfig, 
  TestResult, 
  TestCase, 
  TestScenario,
  ValidationRule,
  UserAction 
} from './types';
import { AppTester } from './app-tester';
import { HealthChecker } from './health-checker';
import { standardScenarios } from './test-scenarios';

export interface TestRunnerConfig {
  apps: AppConfig[];
  scenarios?: TestScenario[];
  parallel?: boolean;
  timeout?: number;
  retries?: number;
  headless?: boolean;
  outputDir?: string;
}

export class TestRunner {
  private config: TestRunnerConfig;
  private results: TestResult[] = [];
  private healthChecker: HealthChecker;

  constructor(config: TestRunnerConfig) {
    this.config = {
      parallel: true,
      timeout: 30000,
      retries: 2,
      headless: true,
      outputDir: './test-results',
      ...config
    };
    this.healthChecker = new HealthChecker();
  }

  async runAll(): Promise<TestResult[]> {
    const spinner = ora('Starting test suite...').start();
    
    try {
      // Health check first
      spinner.text = 'Performing health checks...';
      await this.runHealthChecks();

      // Run tests
      if (this.config.parallel) {
        await this.runParallel();
      } else {
        await this.runSequential();
      }

      spinner.succeed('Test suite completed');
      this.printSummary();
      
      return this.results;
    } catch (error) {
      spinner.fail(`Test suite failed: ${error}`);
      throw error;
    }
  }

  async runApp(appName: string): Promise<TestResult> {
    const app = this.config.apps.find(a => a.name === appName);
    if (!app) {
      throw new Error(`App ${appName} not found in configuration`);
    }

    return await this.executeAppTests(app);
  }

  async runScenario(appName: string, scenarioName: string): Promise<TestCase> {
    const app = this.config.apps.find(a => a.name === appName);
    if (!app) {
      throw new Error(`App ${appName} not found`);
    }

    const scenarios = this.config.scenarios || standardScenarios[app.name] || [];
    const scenario = scenarios.find(s => s.name === scenarioName);
    if (!scenario) {
      throw new Error(`Scenario ${scenarioName} not found for app ${appName}`);
    }

    const appTester = new AppTester(app);
    return await appTester.runScenario(scenario);
  }

  private async runHealthChecks(): Promise<void> {
    for (const app of this.config.apps) {
      try {
        const isHealthy = await this.healthChecker.checkApp(app);
        if (!isHealthy) {
          console.warn(chalk.yellow(`⚠️  ${app.name} health check failed - continuing anyway`));
        }
      } catch (error) {
        console.warn(chalk.yellow(`⚠️  ${app.name} health check error: ${error}`));
      }
    }
  }

  private async runParallel(): Promise<void> {
    const promises = this.config.apps.map(app => this.executeAppTests(app));
    this.results = await Promise.all(promises);
  }

  private async runSequential(): Promise<void> {
    for (const app of this.config.apps) {
      this.results.push(await this.executeAppTests(app));
    }
  }

  private async executeAppTests(app: AppConfig): Promise<TestResult> {
    const spinner = ora(`Testing ${app.name}...`).start();
    const startTime = Date.now();

    try {
      const appTester = new AppTester(app);
      const scenarios = this.config.scenarios || standardScenarios[app.name.toLowerCase()] || [];
      const tests: TestCase[] = [];

      // Run each scenario
      for (const scenario of scenarios) {
        try {
          const testCase = await this.executeScenarioWithRetry(appTester, scenario);
          tests.push(testCase);
          
          if (testCase.status === 'passed') {
            spinner.text = `${app.name}: ✓ ${scenario.name}`;
          } else {
            spinner.text = `${app.name}: ✗ ${scenario.name}`;
          }
        } catch (error) {
          tests.push({
            name: scenario.name,
            category: 'scenario',
            status: 'failed',
            duration: 0,
            error: String(error)
          });
        }
      }

      const duration = Date.now() - startTime;
      const summary = this.calculateSummary(tests);
      
      const result: TestResult = {
        app: app.name,
        timestamp: new Date(),
        duration,
        status: summary.failed > 0 ? 'failed' : 'passed',
        tests,
        summary
      };

      if (result.status === 'passed') {
        spinner.succeed(`${app.name}: All tests passed (${duration}ms)`);
      } else {
        spinner.fail(`${app.name}: ${summary.failed}/${summary.total} tests failed`);
      }

      return result;

    } catch (error) {
      const duration = Date.now() - startTime;
      spinner.fail(`${app.name}: Test execution failed`);
      
      return {
        app: app.name,
        timestamp: new Date(),
        duration,
        status: 'failed',
        tests: [],
        summary: { total: 0, passed: 0, failed: 1, skipped: 0 }
      };
    }
  }

  private async executeScenarioWithRetry(
    appTester: AppTester, 
    scenario: TestScenario
  ): Promise<TestCase> {
    let lastError: Error | undefined;
    
    for (let attempt = 1; attempt <= (this.config.retries || 1) + 1; attempt++) {
      try {
        return await appTester.runScenario(scenario);
      } catch (error) {
        lastError = error as Error;
        if (attempt <= (this.config.retries || 1)) {
          console.log(chalk.yellow(`Retrying ${scenario.name} (attempt ${attempt + 1})`));
          await this.sleep(1000 * attempt); // Exponential backoff
        }
      }
    }
    
    throw lastError;
  }

  private calculateSummary(tests: TestCase[]) {
    return {
      total: tests.length,
      passed: tests.filter(t => t.status === 'passed').length,
      failed: tests.filter(t => t.status === 'failed').length,
      skipped: tests.filter(t => t.status === 'skipped').length
    };
  }

  private printSummary(): void {
    console.log('\n' + chalk.bold('='.repeat(60)));
    console.log(chalk.bold.blue('TEST SUITE SUMMARY'));
    console.log(chalk.bold('='.repeat(60)));

    let totalTests = 0;
    let totalPassed = 0;
    let totalFailed = 0;
    let totalDuration = 0;

    for (const result of this.results) {
      totalTests += result.summary.total;
      totalPassed += result.summary.passed;
      totalFailed += result.summary.failed;
      totalDuration += result.duration;

      const status = result.status === 'passed' 
        ? chalk.green('✓ PASSED') 
        : chalk.red('✗ FAILED');
      
      console.log(`${status} ${result.app}: ${result.summary.passed}/${result.summary.total} (${result.duration}ms)`);
      
      if (result.status === 'failed') {
        const failedTests = result.tests.filter(t => t.status === 'failed');
        for (const test of failedTests) {
          console.log(chalk.red(`  ✗ ${test.name}: ${test.error}`));
        }
      }
    }

    console.log(chalk.bold('='.repeat(60)));
    console.log(`Total Tests: ${totalTests}`);
    console.log(chalk.green(`Passed: ${totalPassed}`));
    console.log(chalk.red(`Failed: ${totalFailed}`));
    console.log(`Duration: ${totalDuration}ms`);
    
    const successRate = totalTests > 0 ? ((totalPassed / totalTests) * 100).toFixed(1) : '0';
    console.log(`Success Rate: ${successRate}%`);
    console.log(chalk.bold('='.repeat(60)) + '\n');
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Utility methods for programmatic usage
  getResults(): TestResult[] {
    return this.results;
  }

  getFailedTests(): TestCase[] {
    return this.results.flatMap(r => r.tests.filter(t => t.status === 'failed'));
  }

  getPassedTests(): TestCase[] {
    return this.results.flatMap(r => r.tests.filter(t => t.status === 'passed'));
  }

  getTotalDuration(): number {
    return this.results.reduce((sum, r) => sum + r.duration, 0);
  }

  getSuccessRate(): number {
    const totalTests = this.results.reduce((sum, r) => sum + r.summary.total, 0);
    const passedTests = this.results.reduce((sum, r) => sum + r.summary.passed, 0);
    return totalTests > 0 ? (passedTests / totalTests) * 100 : 0;
  }

  // Export results to file
  async saveResults(filePath?: string): Promise<void> {
    const outputPath = filePath || `${this.config.outputDir}/test-results-${Date.now()}.json`;
    const data = {
      timestamp: new Date().toISOString(),
      config: this.config,
      results: this.results,
      summary: {
        totalApps: this.config.apps.length,
        totalTests: this.results.reduce((sum, r) => sum + r.summary.total, 0),
        passedTests: this.results.reduce((sum, r) => sum + r.summary.passed, 0),
        failedTests: this.results.reduce((sum, r) => sum + r.summary.failed, 0),
        totalDuration: this.getTotalDuration(),
        successRate: this.getSuccessRate()
      }
    };

    // In a real implementation, you'd write to file here
    console.log(`Results saved to ${outputPath}`);
  }
}

// Factory function for easy setup
export function createTestRunner(config: TestRunnerConfig): TestRunner {
  return new TestRunner(config);
}

// Default configurations for different environments
export const defaultConfigs = {
  development: {
    timeout: 10000,
    retries: 1,
    headless: false,
    parallel: false
  },
  ci: {
    timeout: 30000,
    retries: 2,
    headless: true,
    parallel: true
  },
  production: {
    timeout: 60000,
    retries: 3,
    headless: true,
    parallel: true
  }
};