/**
 * Main App Tester - Orchestrates testing for Stack 2025 apps
 */

import chalk from 'chalk';
import ora from 'ora';
import { HealthChecker } from './health-checker';
import { UserAgent } from './user-agent';
import { FrontendTester } from './frontend-tester';
import { UIComponentTester } from './ui-component-tester';
import { UIDiagnosticTester } from './ui-diagnostic-tester';
import { AppConfig, TestResult, TestCase, TestScenario } from './types';
import { commonScenarios, invoiceAppScenarios, productivityHubScenarios, ccLightScenarios } from './test-scenarios';

export class AppTester {
  private healthChecker: HealthChecker;
  private frontendTester: FrontendTester;
  private results: TestResult[] = [];
  private config: AppConfig;

  constructor(config: AppConfig) {
    this.config = config;
    this.healthChecker = new HealthChecker();
    this.frontendTester = new FrontendTester();
  }

  async runScenario(scenario: TestScenario): Promise<TestCase> {
    const startTime = Date.now();
    const agent = new UserAgent(this.config);
    
    try {
      await agent.initialize({ headless: true });
      
      // Login if required and credentials available
      if (this.config.testCredentials) {
        await agent.login(
          this.config.testCredentials.email,
          this.config.testCredentials.password
        );
      }
      
      const success = await agent.executeScenario(scenario);
      
      return {
        name: scenario.name,
        category: 'functional',
        status: success ? 'passed' : 'failed',
        duration: Date.now() - startTime,
        screenshots: [] // Would be populated by agent
      };
    } catch (error: any) {
      return {
        name: scenario.name,
        category: 'functional',
        status: 'failed',
        duration: Date.now() - startTime,
        error: error.message,
        screenshots: []
      };
    } finally {
      await agent.cleanup();
    }
  }

  async testUIComponents(): Promise<TestResult> {
    console.log(chalk.cyan.bold(`\n🎨 UI Component Testing ${this.config.name}\n${'='.repeat(50)}`));
    
    const startTime = Date.now();
    const testCases: TestCase[] = [];
    
    const agent = new UserAgent(this.config);
    let agentInitialized = false;
    
    try {
      const initSpinner = ora('Initializing browser for UI testing...').start();
      await agent.initialize({ headless: true }); // Use headless mode for CI/server environments
      agentInitialized = true;
      initSpinner.succeed('Browser initialized');

      // Navigate to the app
      const navSpinner = ora('Navigating to application...').start();
      await agent.getPage().goto(this.config.frontendUrl);
      await agent.getPage().waitForTimeout(3000); // Wait for app to load
      navSpinner.succeed('Application loaded');

      // Take initial screenshot
      await agent.getPage().screenshot({ path: `ui-test-initial-${Date.now()}.png`, fullPage: true });

      // Run comprehensive UI component tests
      const uiTester = new UIComponentTester(agent.getPage(), this.config);
      const uiResults = await uiTester.testAllUIComponents();
      
      // Convert UI test results to TestCase format
      for (const componentResult of uiResults) {
        for (const test of componentResult.tests) {
          testCases.push({
            name: `${componentResult.component}: ${test.name}`,
            category: 'ui-component',
            status: test.result === 'passed' ? 'passed' : 'failed',
            duration: 0,
            error: test.error,
            screenshots: test.screenshot ? [test.screenshot] : []
          });
        }
      }

      // Generate detailed report
      await uiTester.generateReport(uiResults);

    } catch (error: any) {
      console.log(chalk.red(`\n❌ UI Component test execution failed: ${error.message}`));
      testCases.push({
        name: 'UI Component Test Execution',
        category: 'system',
        status: 'failed',
        duration: Date.now() - startTime,
        error: error.message,
      });
    } finally {
      if (agentInitialized) {
        await agent.cleanup();
      }
    }

    return this.createResult(this.config, testCases, startTime);
  }

  async diagnoseUI(): Promise<TestResult> {
    console.log(chalk.cyan.bold(`\n🔍 UI Diagnosis for ${this.config.name}\n${'='.repeat(50)}`));
    
    const startTime = Date.now();
    const testCases: TestCase[] = [];
    
    const agent = new UserAgent(this.config);
    let agentInitialized = false;
    
    try {
      const initSpinner = ora('Initializing browser for UI diagnosis...').start();
      await agent.initialize({ headless: true });
      agentInitialized = true;
      initSpinner.succeed('Browser initialized');

      // Run comprehensive UI diagnosis
      const diagnosticTester = new UIDiagnosticTester(agent.getPage(), this.config);
      const diagnosticResult = await diagnosticTester.diagnoseUI();
      
      // Generate detailed report
      await diagnosticTester.generateDiagnosticReport(diagnosticResult);

      // Convert diagnostic results to TestCase format
      testCases.push({
        name: `UI Diagnosis`,
        category: 'ui-diagnostic',
        status: diagnosticResult.status === 'broken' ? 'failed' : 'passed',
        duration: Date.now() - startTime,
        error: diagnosticResult.issues.join('; ') || undefined,
        screenshots: diagnosticResult.screenshots
      });

      // Add individual issue test cases
      diagnosticResult.issues.forEach((issue, index) => {
        testCases.push({
          name: `Issue ${index + 1}: ${issue.slice(0, 50)}...`,
          category: 'ui-issue',
          status: 'failed',
          duration: 0,
          error: issue
        });
      });

      // Add JS error test cases
      diagnosticResult.jsErrors.forEach((error, index) => {
        testCases.push({
          name: `JS Error ${index + 1}`,
          category: 'javascript',
          status: 'failed',
          duration: 0,
          error: error
        });
      });

    } catch (error: any) {
      console.log(chalk.red(`\n❌ UI diagnosis failed: ${error.message}`));
      testCases.push({
        name: 'UI Diagnosis Execution',
        category: 'system',
        status: 'failed',
        duration: Date.now() - startTime,
        error: error.message,
      });
    } finally {
      if (agentInitialized) {
        await agent.cleanup();
      }
    }

    return this.createResult(this.config, testCases, startTime);
  }

  async testApp(options?: { 
    headless?: boolean; 
    skipHealth?: boolean;
    scenarios?: 'all' | 'basic' | 'app-specific';
    includeFrontend?: boolean;
    includeUIComponents?: boolean;
  }): Promise<TestResult> {
    const config = this.config;
    console.log(chalk.cyan.bold(`\n🧪 Testing ${config.name}\n${'='.repeat(50)}`));
    
    const startTime = Date.now();
    const testCases: TestCase[] = [];
    
    // Health check
    if (!options?.skipHealth) {
      const healthSpinner = ora('Running health check...').start();
      const isHealthy = await this.healthChecker.checkApp(config);
      
      if (!isHealthy) {
        healthSpinner.fail('Health check failed');
        testCases.push({
          name: 'Health Check',
          category: 'infrastructure',
          status: 'failed',
          duration: Date.now() - startTime,
          error: 'App is not healthy',
        });
        
        return this.createResult(config, testCases, startTime);
      }
      healthSpinner.succeed('Health check passed');
    }

    // User agent tests
    const agent = new UserAgent(config);
    let agentInitialized = false;
    
    try {
      const initSpinner = ora('Initializing browser...').start();
      await agent.initialize({ headless: options?.headless ?? true });
      agentInitialized = true;
      initSpinner.succeed('Browser initialized');

      // Test authentication if credentials provided
      if (config.testCredentials) {
        const authSpinner = ora('Testing authentication...').start();
        const loginSuccess = await agent.login(
          config.testCredentials.email,
          config.testCredentials.password
        );
        
        testCases.push({
          name: 'Login',
          category: 'authentication',
          status: loginSuccess ? 'passed' : 'failed',
          duration: 0,
          error: loginSuccess ? undefined : 'Login failed',
        });
        
        if (loginSuccess) {
          authSpinner.succeed('Authentication successful');
        } else {
          authSpinner.fail('Authentication failed');
        }
      }

      // Run test scenarios
      const scenariosToRun = this.getScenarios(config, options?.scenarios || 'basic');
      
      for (const scenario of scenariosToRun) {
        const scenarioSpinner = ora(`Running: ${scenario.name}`).start();
        const scenarioStart = Date.now();
        
        try {
          const success = await agent.executeScenario(scenario);
          
          testCases.push({
            name: scenario.name,
            category: 'functional',
            status: success ? 'passed' : 'failed',
            duration: Date.now() - scenarioStart,
          });
          
          if (success) {
            scenarioSpinner.succeed(`${scenario.name} passed`);
          } else {
            scenarioSpinner.fail(`${scenario.name} failed`);
          }
        } catch (error: any) {
          scenarioSpinner.fail(`${scenario.name} failed`);
          testCases.push({
            name: scenario.name,
            category: 'functional',
            status: 'failed',
            duration: Date.now() - scenarioStart,
            error: error.message,
          });
        }
      }

      // Run frontend tests if requested
      if (options?.includeFrontend) {
        const frontendResults = await this.frontendTester.runFrontendTests(agent.getPage(), config);
        testCases.push(...frontendResults);
      }

    } catch (error: any) {
      console.log(chalk.red(`\n❌ Test execution failed: ${error.message}`));
      testCases.push({
        name: 'Test Execution',
        category: 'system',
        status: 'failed',
        duration: Date.now() - startTime,
        error: error.message,
      });
    } finally {
      if (agentInitialized) {
        await agent.cleanup();
      }
    }

    return this.createResult(config, testCases, startTime);
  }

  private getScenarios(config: AppConfig, type: 'all' | 'basic' | 'app-specific') {
    let scenarios = [...commonScenarios];
    
    if (type === 'all' || type === 'app-specific') {
      if (config.name.toLowerCase().includes('invoice')) {
        scenarios.push(...invoiceAppScenarios);
      } else if (config.name.toLowerCase().includes('productivity')) {
        scenarios.push(...productivityHubScenarios);
      } else if (config.name.toLowerCase().includes('cc')) {
        scenarios.push(...ccLightScenarios);
      }
    }
    
    return type === 'app-specific' 
      ? scenarios.filter(s => !commonScenarios.includes(s))
      : scenarios;
  }

  private createResult(config: AppConfig, testCases: TestCase[], startTime: number): TestResult {
    const result: TestResult = {
      app: config.name,
      timestamp: new Date(),
      duration: Date.now() - startTime,
      status: testCases.every(tc => tc.status === 'passed') ? 'passed' : 'failed',
      tests: testCases,
      summary: {
        total: testCases.length,
        passed: testCases.filter(tc => tc.status === 'passed').length,
        failed: testCases.filter(tc => tc.status === 'failed').length,
        skipped: testCases.filter(tc => tc.status === 'skipped').length,
      },
    };

    this.results.push(result);
    this.printSummary(result);
    
    return result;
  }

  private printSummary(result: TestResult) {
    console.log(chalk.cyan(`\n📊 Test Summary for ${result.app}`));
    console.log(chalk.cyan('='.repeat(50)));
    
    console.log(`Total Tests: ${result.summary.total}`);
    console.log(chalk.green(`✅ Passed: ${result.summary.passed}`));
    
    if (result.summary.failed > 0) {
      console.log(chalk.red(`❌ Failed: ${result.summary.failed}`));
    }
    
    if (result.summary.skipped > 0) {
      console.log(chalk.yellow(`⏭️  Skipped: ${result.summary.skipped}`));
    }
    
    console.log(`Duration: ${(result.duration / 1000).toFixed(2)}s`);
    
    if (result.status === 'passed') {
      console.log(chalk.green.bold(`\n🎉 All tests passed!`));
    } else {
      console.log(chalk.red.bold(`\n😞 Some tests failed`));
      
      // Show failed tests
      const failedTests = result.tests.filter(t => t.status === 'failed');
      if (failedTests.length > 0) {
        console.log(chalk.red('\nFailed tests:'));
        failedTests.forEach(test => {
          console.log(chalk.red(`  ❌ ${test.name}: ${test.error || 'Unknown error'}`));
        });
      }
    }
  }

  static async testMultipleApps(configs: AppConfig[], options?: { 
    headless?: boolean; 
    parallel?: boolean;
    includeFrontend?: boolean;
  }): Promise<TestResult[]> {
    console.log(chalk.cyan.bold('\n🚀 Starting Multi-App Testing Suite\n'));
    
    const results: TestResult[] = [];
    
    if (options?.parallel) {
      // Run tests in parallel
      const promises = configs.map(async (config) => {
        const tester = new AppTester(config);
        return await tester.testApp({
          headless: options.headless,
          includeFrontend: options.includeFrontend
        });
      });
      results.push(...await Promise.all(promises));
    } else {
      // Run tests sequentially
      for (const config of configs) {
        const tester = new AppTester(config);
        const result = await tester.testApp({
          headless: options?.headless,
          includeFrontend: options?.includeFrontend
        });
        results.push(result);
      }
    }
    
    // Final summary
    AppTester.printFinalSummary(results);
    
    return results;
  }

  private static printFinalSummary(results: TestResult[]) {
    console.log(chalk.cyan.bold('\n\n🏁 FINAL TEST SUMMARY'));
    console.log(chalk.cyan('='.repeat(60)));
    
    const totalApps = results.length;
    const passedApps = results.filter(r => r.status === 'passed').length;
    const failedApps = results.filter(r => r.status === 'failed').length;
    
    console.log(`\nApps Tested: ${totalApps}`);
    console.log(chalk.green(`✅ Passed: ${passedApps}`));
    
    if (failedApps > 0) {
      console.log(chalk.red(`❌ Failed: ${failedApps}`));
    }
    
    // Per-app summary
    console.log('\nPer-App Results:');
    console.log('-'.repeat(40));
    
    results.forEach(result => {
      const icon = result.status === 'passed' ? '✅' : '❌';
      const color = result.status === 'passed' ? chalk.green : chalk.red;
      console.log(
        color(`${icon} ${result.app.padEnd(20)} ${result.summary.passed}/${result.summary.total} tests passed`)
      );
    });
    
    // Overall status
    const allPassed = failedApps === 0;
    if (allPassed) {
      console.log(chalk.green.bold('\n🎉 ALL APPS PASSED! 🎉'));
    } else {
      console.log(chalk.red.bold(`\n⚠️  ${failedApps} APP(S) HAVE FAILING TESTS`));
    }
  }
}