#!/usr/bin/env node

/**
 * Comprehensive Test Runner for Focus by Kraliki and Business Operations
 *
 * This script provides a centralized way to run different test suites
 * with various configurations and reporting options.
 *
 * @module TestRunner
 * @version 2.0.0
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class TestRunner {
  constructor() {
    this.results = {
      startTime: new Date().toISOString(),
      suites: {},
      summary: {
        total: 0,
        passed: 0,
        failed: 0,
        skipped: 0
      },
      environment: {
        node: process.version,
        platform: process.platform,
        ci: !!process.env.CI
      }
    };
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const prefix = {
      info: 'ℹ️',
      success: '✅',
      error: '❌',
      warning: '⚠️',
      debug: '🔍'
    }[type] || 'ℹ️';

    console.log(`[${timestamp}] ${prefix} ${message}`);
  }

  executeCommand(command, options = {}) {
    const { cwd = process.cwd(), env = {}, silent = false } = options;
    const fullEnv = { ...process.env, ...env };

    this.log(`Executing: ${command}`, 'debug');

    try {
      const output = execSync(command, {
        cwd,
        env: fullEnv,
        stdio: silent ? 'pipe' : 'inherit',
        timeout: options.timeout || 300000
      });

      return { success: true, output: output?.toString() };
    } catch (error) {
      this.log(`Command failed: ${command}`, 'error');
      this.log(`Error: ${error.message}`, 'error');
      return { success: false, error: error.message };
    }
  }

  async runSuite(suiteName, config) {
    const startTime = Date.now();
    this.log(`Starting test suite: ${suiteName}`, 'info');

    const suiteConfig = {
      name: suiteName,
      configPath: config.configPath,
      command: config.command,
      env: config.env || {},
      timeout: config.timeout || 300000
    };

    try {
      const result = this.executeCommand(suiteConfig.command, {
        env: suiteConfig.env,
        timeout: suiteConfig.timeout
      });

      const duration = Date.now() - startTime;

      this.results.suites[suiteName] = {
        status: result.success ? 'passed' : 'failed',
        duration,
        config: suiteConfig,
        error: result.error,
        output: result.output
      };

      if (result.success) {
        this.log(`✅ Test suite completed: ${suiteName} (${duration}ms)`, 'success');
      } else {
        this.log(`❌ Test suite failed: ${suiteName} (${duration}ms)`, 'error');
      }

      return result.success;

    } catch (error) {
      const duration = Date.now() - startTime;
      this.results.suites[suiteName] = {
        status: 'failed',
        duration,
        config: suiteConfig,
        error: error.message
      };

      this.log(`💥 Test suite crashed: ${suiteName} (${duration}ms)`, 'error');
      return false;
    }
  }

  async runFocusKralikiTests() {
    this.log('Running Focus by Kraliki E2E tests...', 'info');

    const success = await this.runSuite('focus-kraliki-e2e', {
      command: 'npx playwright test --config=tests/playwright.config.ts',
      env: {
        FOCUS_KRALIKI_BASE_URL: 'http://localhost:5173',
        FOCUS_LITE_BASE_URL: 'http://localhost:5173'
      }
    });

    if (success) {
      this.log('Focus by Kraliki tests completed successfully', 'success');
    }

    return success;
  }

  async runBusinessOpsTests() {
    this.log('Running Business Operations integration tests...', 'info');

    const success = await this.runSuite('business-ops', {
      command: 'npx playwright test --config=e2e/config/business-operations.config.ts',
      env: {
        BUSINESS_OPS_BASE_URL: 'http://localhost:3000',
        FOCUS_KRALIKI_BASE_URL: 'http://localhost:5173',
        FOCUS_LITE_BASE_URL: 'http://localhost:5173'
      }
    });

    if (success) {
      this.log('Business Operations tests completed successfully', 'success');
    }

    return success;
  }

  async runAccessibilityTests() {
    this.log('Running accessibility and mobile tests...', 'info');

    const success = await this.runSuite('accessibility-mobile', {
      command: 'npx playwright test e2e/accessibility-mobile.spec.ts --config=playwright.config.enhanced.ts',
      env: {
        ACCESSIBILITY_TEST: 'true'
      }
    });

    if (success) {
      this.log('Accessibility tests completed successfully', 'success');
    }

    return success;
  }

  async runPerformanceTests() {
    this.log('Running performance tests...', 'info');

    const success = await this.runSuite('performance', {
      command: 'npx playwright test --grep "performance" --config=playwright.config.enhanced.ts',
      env: {
        PERFORMANCE_TEST: 'true'
      }
    });

    if (success) {
      this.log('Performance tests completed successfully', 'success');
    }

    return success;
  }

  async runAllTests() {
    this.log('Running comprehensive test suite...', 'info');

    const suites = [
      () => this.runFocusKralikiTests(),
      () => this.runBusinessOpsTests(),
      () => this.runAccessibilityTests(),
      () => this.runPerformanceTests()
    ];

    const results = [];
    for (const suite of suites) {
      try {
        const result = await suite();
        results.push(result);
      } catch (error) {
        this.log(`Suite failed with error: ${error.message}`, 'error');
        results.push(false);
      }
    }

    const allPassed = results.every(result => result);
    const passedCount = results.filter(result => result).length;

    this.log(`Test suite results: ${passedCount}/${results.length} passed`, allPassed ? 'success' : 'error');

    return allPassed;
  }

  generateReport() {
    const reportPath = path.join(process.cwd(), 'test-results', 'comprehensive-test-report.json');

    // Update summary
    const suites = Object.values(this.results.suites);
    this.results.summary.total = suites.length;
    this.results.summary.passed = suites.filter(s => s.status === 'passed').length;
    this.results.summary.failed = suites.filter(s => s.status === 'failed').length;
    this.results.summary.skipped = suites.filter(s => s.status === 'skipped').length;

    this.results.endTime = new Date().toISOString();

    // Create report directory if it doesn't exist
    const reportDir = path.dirname(reportPath);
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }

    // Write report
    fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2));

    this.log(`📊 Test report generated: ${reportPath}`, 'info');
    this.log(`📈 Summary: ${this.results.summary.passed}/${this.results.summary.total} suites passed`, 'success');

    return reportPath;
  }

  async cleanup() {
    this.log('Cleaning up test environment...', 'info');

    // Clean up test results older than 7 days
    const testResultsDir = path.join(process.cwd(), 'test-results');
    if (fs.existsSync(testResultsDir)) {
      const files = fs.readdirSync(testResultsDir);
      const oneWeekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);

      for (const file of files) {
        const filePath = path.join(testResultsDir, file);
        const stats = fs.statSync(filePath);

        if (stats.isFile() && stats.mtime.getTime() < oneWeekAgo) {
          fs.unlinkSync(filePath);
          this.log(`Cleaned up old file: ${file}`, 'debug');
        }
      }
    }

    this.log('Cleanup completed', 'success');
  }

  async run(args) {
    const command = args[0] || 'all';

    this.log(`🚀 Starting test runner with command: ${command}`, 'info');

    try {
      let success = false;

      switch (command) {
        case 'focus-kraliki':
          success = await this.runFocusKralikiTests();
          break;
        case 'business-ops':
          success = await this.runBusinessOpsTests();
          break;
        case 'accessibility':
          success = await this.runAccessibilityTests();
          break;
        case 'performance':
          success = await this.runPerformanceTests();
          break;
        case 'all':
          success = await this.runAllTests();
          break;
        default:
          this.log(`Unknown command: ${command}`, 'error');
          this.log('Available commands: focus-kraliki, business-ops, accessibility, performance, all', 'info');
          process.exit(1);
      }

      // Generate report
      const reportPath = this.generateReport();

      // Cleanup
      await this.cleanup();

      if (success) {
        this.log('🎉 All tests completed successfully!', 'success');
        process.exit(0);
      } else {
        this.log('❌ Some tests failed. Check the report for details.', 'error');
        process.exit(1);
      }

    } catch (error) {
      this.log(`💥 Test runner failed: ${error.message}`, 'error');
      process.exit(1);
    }
  }
}

// CLI interface
if (require.main === module) {
  const runner = new TestRunner();
  runner.run(process.argv.slice(2));
}

module.exports = TestRunner;
