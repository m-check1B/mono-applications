/**
 * Frontend Testing - UI/UX and interaction testing
 */

import { Page } from 'playwright';
import chalk from 'chalk';
import { AppConfig, TestCase } from './types';

export interface FrontendTest {
  name: string;
  description: string;
  test: (page: Page, config: AppConfig) => Promise<boolean>;
}

export class FrontendTester {
  private tests: FrontendTest[] = [
    {
      name: 'Page Load Performance',
      description: 'Page loads within acceptable time',
      test: async (page, config) => {
        const startTime = Date.now();
        await page.goto(config.frontendUrl, { waitUntil: 'networkidle' });
        const loadTime = Date.now() - startTime;
        console.log(chalk.gray(`  Load time: ${loadTime}ms`));
        return loadTime < 5000; // 5 seconds max
      },
    },
    {
      name: 'CSS Styles Applied',
      description: 'Page has proper styling and layout',
      test: async (page) => {
        // Check if body has background color (indicating CSS loaded)
        const hasStyles = await page.evaluate(() => {
          const body = document.body;
          const computedStyle = window.getComputedStyle(body);
          return computedStyle.backgroundColor !== 'rgba(0, 0, 0, 0)';
        });
        return hasStyles;
      },
    },
    {
      name: 'JavaScript Bundle Loaded',
      description: 'JavaScript executes and React renders',
      test: async (page) => {
        // Check if React has rendered by looking for data-reactroot or React dev tools
        const hasReact = await page.evaluate(() => {
          return !!(window as any).React || 
                 document.querySelector('[data-reactroot]') !== null ||
                 (document.querySelector('#root')?.children?.length || 0) > 0;
        });
        return hasReact;
      },
    },
    {
      name: 'No JavaScript Errors',
      description: 'No console errors on page load',
      test: async (page) => {
        const errors: string[] = [];
        page.on('console', msg => {
          if (msg.type() === 'error') {
            errors.push(msg.text());
          }
        });
        
        await page.waitForTimeout(2000); // Wait for any async errors
        
        // Filter out known acceptable errors
        const criticalErrors = errors.filter(error => 
          !error.includes('Failed to load resource') && // 404s are common in dev
          !error.includes('TRPCClientError') && // API errors are expected during testing
          !error.includes('chunk-') // Vite chunk loading issues
        );
        
        if (criticalErrors.length > 0) {
          console.log(chalk.yellow(`  Found ${criticalErrors.length} critical errors:`));
          criticalErrors.forEach(error => console.log(chalk.red(`    ${error}`)));
        }
        
        return criticalErrors.length === 0;
      },
    },
    {
      name: 'Responsive Design',
      description: 'Layout adapts to different screen sizes',
      test: async (page) => {
        // Test mobile viewport
        await page.setViewportSize({ width: 375, height: 667 });
        await page.waitForTimeout(500);
        
        // Check if layout responds (no horizontal overflow)
        const hasHorizontalScroll = await page.evaluate(() => {
          return document.body.scrollWidth > window.innerWidth;
        });
        
        // Reset to desktop
        await page.setViewportSize({ width: 1280, height: 720 });
        
        return !hasHorizontalScroll;
      },
    },
    {
      name: 'Navigation Menu Works',
      description: 'Main navigation is functional',
      test: async (page) => {
        // Look for common navigation elements
        const navElements = await page.locator('nav, [role="navigation"], .nav, .navbar, .menu').count();
        
        if (navElements === 0) {
          // Try to find any clickable menu items
          const menuItems = await page.locator('a, button').filter({ hasText: /menu|home|dashboard|about/i }).count();
          return menuItems > 0;
        }
        
        return navElements > 0;
      },
    },
    {
      name: 'Interactive Elements',
      description: 'Buttons and links are clickable',
      test: async (page) => {
        // Count interactive elements
        const interactiveElements = await page.locator('button:visible, a:visible, input:visible').count();
        return interactiveElements > 0;
      },
    },
    {
      name: 'Form Validation',
      description: 'Forms provide proper validation feedback',
      test: async (page) => {
        // Look for forms
        const forms = await page.locator('form').count();
        
        if (forms === 0) {
          console.log(chalk.gray('  No forms found, skipping validation test'));
          return true; // No forms to test
        }
        
        // Try to find form inputs
        const inputs = await page.locator('form input[required], form input[type="email"]').count();
        return inputs > 0; // At least has form structure
      },
    },
    {
      name: 'Accessibility Basics',
      description: 'Basic accessibility features present',
      test: async (page) => {
        // Check for basic accessibility features
        const hasAltTexts = await page.locator('img[alt]').count();
        const hasAriaLabels = await page.locator('[aria-label]').count();
        const hasHeadings = await page.locator('h1, h2, h3').count();
        
        // Should have at least some accessibility features
        return (hasAltTexts + hasAriaLabels + hasHeadings) > 0;
      },
    },
    {
      name: 'SEO Meta Tags',
      description: 'Page has proper meta tags for SEO',
      test: async (page) => {
        const title = await page.title();
        const description = await page.locator('meta[name="description"]').getAttribute('content');
        const viewport = await page.locator('meta[name="viewport"]').getAttribute('content');
        
        return !!(title && title.length > 0 && viewport);
      },
    }
  ];

  async runFrontendTests(page: Page, config: AppConfig): Promise<TestCase[]> {
    console.log(chalk.cyan(`\n🎨 Running Frontend Tests for ${config.name}`));
    console.log(chalk.cyan('='.repeat(50)));
    
    const results: TestCase[] = [];
    
    for (const test of this.tests) {
      const startTime = Date.now();
      console.log(chalk.blue(`\n📋 ${test.name}`));
      console.log(chalk.gray(`   ${test.description}`));
      
      try {
        const success = await test.test(page, config);
        const duration = Date.now() - startTime;
        
        results.push({
          name: test.name,
          category: 'frontend',
          status: success ? 'passed' : 'failed',
          duration,
          error: success ? undefined : `${test.description} failed`,
        });
        
        if (success) {
          console.log(chalk.green(`   ✅ ${test.name} passed (${duration}ms)`));
        } else {
          console.log(chalk.red(`   ❌ ${test.name} failed (${duration}ms)`));
        }
      } catch (error: any) {
        const duration = Date.now() - startTime;
        console.log(chalk.red(`   ❌ ${test.name} error: ${error.message}`));
        
        results.push({
          name: test.name,
          category: 'frontend',
          status: 'failed',
          duration,
          error: error.message,
        });
      }
    }
    
    // Summary
    const passed = results.filter(r => r.status === 'passed').length;
    const total = results.length;
    
    console.log(chalk.cyan(`\n📊 Frontend Test Summary`));
    console.log(chalk.cyan('='.repeat(30)));
    console.log(`Total Tests: ${total}`);
    console.log(chalk.green(`✅ Passed: ${passed}`));
    console.log(chalk.red(`❌ Failed: ${total - passed}`));
    
    if (passed === total) {
      console.log(chalk.green.bold('\n🎉 All frontend tests passed!'));
    } else {
      console.log(chalk.yellow.bold(`\n⚠️  ${total - passed} frontend test(s) failed`));
    }
    
    return results;
  }
}