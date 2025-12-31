/**
 * UI Diagnostic Tester - Diagnoses why UI isn't loading properly
 */

import { Page } from 'playwright';
import chalk from 'chalk';
import { AppConfig } from './types';

export interface DiagnosticResult {
  url: string;
  status: 'working' | 'broken' | 'partially-working';
  issues: string[];
  screenshots: string[];
  consoleLogs: string[];
  networkErrors: string[];
  htmlContent: string;
  jsErrors: string[];
}

export class UIDiagnosticTester {
  private page: Page;
  private config: AppConfig;
  private consoleLogs: string[] = [];
  private jsErrors: string[] = [];
  private networkErrors: string[] = [];

  constructor(page: Page, config: AppConfig) {
    this.page = page;
    this.config = config;
    this.setupLogging();
  }

  private setupLogging(): void {
    // Capture console logs
    this.page.on('console', (msg) => {
      const text = `[${msg.type()}] ${msg.text()}`;
      this.consoleLogs.push(text);
      
      if (msg.type() === 'error') {
        this.jsErrors.push(text);
      }
      
      console.log(chalk.gray(`Console: ${text}`));
    });

    // Capture page errors
    this.page.on('pageerror', (error) => {
      const errorText = `Page Error: ${error.message}`;
      this.jsErrors.push(errorText);
      console.log(chalk.red(`❌ ${errorText}`));
    });

    // Capture network failures
    this.page.on('response', (response) => {
      if (!response.ok()) {
        const errorText = `Network Error: ${response.status()} ${response.url()}`;
        this.networkErrors.push(errorText);
        console.log(chalk.yellow(`⚠️  ${errorText}`));
      }
    });
  }

  async diagnoseUI(): Promise<DiagnosticResult> {
    console.log(chalk.blue('🔍 Starting UI Diagnosis...'));
    
    const screenshots: string[] = [];
    const issues: string[] = [];

    try {
      // Navigate to the app
      console.log(chalk.cyan(`🌐 Navigating to ${this.config.frontendUrl}`));
      await this.page.goto(this.config.frontendUrl, { 
        waitUntil: 'networkidle',
        timeout: 30000 
      });
      
      // Wait for potential React/JS to load
      await this.page.waitForTimeout(3000);
      
      // Take initial screenshot
      const initialScreenshot = `diagnostic-initial-${Date.now()}.png`;
      await this.page.screenshot({ path: initialScreenshot, fullPage: true });
      screenshots.push(initialScreenshot);
      console.log(chalk.green(`📸 Initial screenshot: ${initialScreenshot}`));

      // Check HTML content
      const htmlContent = await this.page.content();
      console.log(chalk.blue(`📄 HTML length: ${htmlContent.length} characters`));

      // Check if React root exists
      const rootElement = await this.page.locator('#root').count();
      if (rootElement === 0) {
        issues.push('No #root element found - React may not be set up correctly');
      } else {
        console.log(chalk.green('✅ React root element found'));
      }

      // Check if React has rendered
      const bodyContent = await this.page.locator('body').textContent();
      if (!bodyContent || bodyContent.trim().length < 10) {
        issues.push('Body appears empty - JavaScript may not be executing');
      } else {
        console.log(chalk.green(`✅ Body content found: ${bodyContent.slice(0, 100)}...`));
      }

      // Check for common React/Vite indicators
      const reactIndicators = [
        'data-reactroot',
        '#root > div',
        '[data-vite-dev-id]',
        'script[type="module"]'
      ];

      for (const indicator of reactIndicators) {
        const count = await this.page.locator(indicator).count();
        if (count > 0) {
          console.log(chalk.green(`✅ Found ${indicator}: ${count} elements`));
        } else {
          console.log(chalk.yellow(`⚠️  Missing ${indicator}`));
        }
      }

      // Check for loading states
      const loadingIndicators = [
        'text="Loading"',
        '.loading',
        '.spinner',
        '[data-loading="true"]'
      ];

      for (const indicator of loadingIndicators) {
        const count = await this.page.locator(indicator).count();
        if (count > 0) {
          console.log(chalk.blue(`🔄 Loading indicator found: ${indicator}`));
        }
      }

      // Test basic DOM elements
      const basicElements = [
        'button',
        'input',
        'a',
        'nav',
        'header',
        'main',
        'div'
      ];

      for (const element of basicElements) {
        const count = await this.page.locator(element).count();
        console.log(chalk.gray(`📊 ${element}: ${count} found`));
        
        if (element === 'div' && count === 0) {
          issues.push('No div elements found - HTML may not be loading');
        }
      }

      // Try to interact with the page
      try {
        await this.page.click('body');
        await this.page.keyboard.press('Tab');
        console.log(chalk.green('✅ Page interaction successful'));
      } catch (interactionError) {
        issues.push(`Page interaction failed: ${interactionError}`);
      }

      // Take screenshot after interactions
      const afterScreenshot = `diagnostic-after-interaction-${Date.now()}.png`;
      await this.page.screenshot({ path: afterScreenshot, fullPage: true });
      screenshots.push(afterScreenshot);

      // Check for specific Productivity Hub elements
      const hubElements = [
        'text="Productivity Hub"',
        'text="Dashboard"',
        'text="Tasks"',
        'text="Calendar"',
        'text="Login"',
        '.task-',
        '.calendar-',
        '.dashboard-'
      ];

      let hubElementsFound = 0;
      for (const element of hubElements) {
        const count = await this.page.locator(element).count();
        if (count > 0) {
          hubElementsFound++;
          console.log(chalk.green(`✅ Hub element found: ${element} (${count})`));
        }
      }

      if (hubElementsFound === 0) {
        issues.push('No Productivity Hub specific elements found - app may not be loading correctly');
      }

      // Final diagnostic screenshot
      const finalScreenshot = `diagnostic-final-${Date.now()}.png`;
      await this.page.screenshot({ path: finalScreenshot, fullPage: true });
      screenshots.push(finalScreenshot);

      // Determine status
      let status: 'working' | 'broken' | 'partially-working';
      
      if (issues.length === 0 && hubElementsFound > 2) {
        status = 'working';
      } else if (rootElement > 0 && bodyContent && bodyContent.trim().length > 10) {
        status = 'partially-working';
      } else {
        status = 'broken';
      }

      return {
        url: this.config.frontendUrl,
        status,
        issues,
        screenshots,
        consoleLogs: this.consoleLogs,
        networkErrors: this.networkErrors,
        htmlContent: htmlContent.slice(0, 2000), // First 2000 chars
        jsErrors: this.jsErrors
      };

    } catch (error) {
      issues.push(`Navigation failed: ${error}`);
      
      return {
        url: this.config.frontendUrl,
        status: 'broken',
        issues,
        screenshots,
        consoleLogs: this.consoleLogs,
        networkErrors: this.networkErrors,
        htmlContent: '',
        jsErrors: this.jsErrors
      };
    }
  }

  async generateDiagnosticReport(result: DiagnosticResult): Promise<void> {
    console.log(chalk.blue.bold('\n🔍 UI DIAGNOSTIC REPORT'));
    console.log(chalk.blue('='.repeat(60)));
    
    console.log(`URL: ${result.url}`);
    
    // Status
    const statusColor = result.status === 'working' ? chalk.green : 
                       result.status === 'partially-working' ? chalk.yellow : chalk.red;
    console.log(`Status: ${statusColor(result.status.toUpperCase())}`);
    
    // Issues
    if (result.issues.length > 0) {
      console.log(chalk.red('\n❌ ISSUES FOUND:'));
      result.issues.forEach((issue, i) => {
        console.log(chalk.red(`  ${i + 1}. ${issue}`));
      });
    } else {
      console.log(chalk.green('\n✅ No issues detected'));
    }
    
    // JavaScript Errors
    if (result.jsErrors.length > 0) {
      console.log(chalk.red('\n💥 JAVASCRIPT ERRORS:'));
      result.jsErrors.forEach((error, i) => {
        console.log(chalk.red(`  ${i + 1}. ${error}`));
      });
    }
    
    // Network Errors
    if (result.networkErrors.length > 0) {
      console.log(chalk.yellow('\n🌐 NETWORK ERRORS:'));
      result.networkErrors.forEach((error, i) => {
        console.log(chalk.yellow(`  ${i + 1}. ${error}`));
      });
    }
    
    // Screenshots
    console.log(chalk.blue(`\n📸 SCREENSHOTS CAPTURED: ${result.screenshots.length}`));
    result.screenshots.forEach((screenshot, i) => {
      console.log(chalk.blue(`  ${i + 1}. ${screenshot}`));
    });
    
    // Console Logs Summary
    console.log(chalk.gray(`\n📋 Console Logs: ${result.consoleLogs.length} entries`));
    if (result.consoleLogs.length > 0) {
      // Show last 5 logs
      const recentLogs = result.consoleLogs.slice(-5);
      recentLogs.forEach(log => {
        console.log(chalk.gray(`  ${log}`));
      });
    }
    
    // HTML Content Preview
    if (result.htmlContent) {
      console.log(chalk.gray(`\n📄 HTML Preview (first 500 chars):`));
      console.log(chalk.gray(result.htmlContent.slice(0, 500) + '...'));
    }
    
    console.log(chalk.blue('='.repeat(60)));
    
    // Recommendations
    console.log(chalk.blue('\n💡 RECOMMENDATIONS:'));
    
    if (result.status === 'broken') {
      console.log(chalk.yellow('  • Check if the development server is running'));
      console.log(chalk.yellow('  • Verify the frontend URL is correct'));
      console.log(chalk.yellow('  • Check for JavaScript compilation errors'));
      console.log(chalk.yellow('  • Ensure all dependencies are installed'));
    } else if (result.status === 'partially-working') {
      console.log(chalk.yellow('  • App is loading but may have routing issues'));
      console.log(chalk.yellow('  • Check React Router configuration'));
      console.log(chalk.yellow('  • Verify component imports and exports'));
    } else {
      console.log(chalk.green('  • App appears to be working correctly!'));
      console.log(chalk.green('  • You can proceed with UI component testing'));
    }
    
    console.log(chalk.blue('\n='.repeat(60)));
  }
}

// Export is already done in the class declaration above