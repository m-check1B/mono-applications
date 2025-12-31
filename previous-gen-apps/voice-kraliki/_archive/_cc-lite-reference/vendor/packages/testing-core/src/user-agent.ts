/**
 * Automated User Agent - Simulates real user interactions
 */

import { chromium, Browser, Page, BrowserContext } from 'playwright';
import chalk from 'chalk';
import { AppConfig, UserAction, TestScenario } from './types';

export class UserAgent {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private page: Page | null = null;
  private config: AppConfig;

  constructor(config: AppConfig) {
    this.config = config;
  }

  async initialize(options?: { headless?: boolean }): Promise<void> {
    console.log(chalk.blue(`🤖 Starting user agent for ${this.config.name}...`));
    
    this.browser = await chromium.launch({
      headless: options?.headless ?? true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
    
    this.context = await this.browser.newContext({
      viewport: { width: 1280, height: 720 },
      userAgent: 'Stack2025-TestAgent/1.0',
    });
    
    this.page = await this.context.newPage();
    
    // Log console messages
    this.page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(chalk.red(`[Browser Error] ${msg.text()}`));
      }
    });
  }

  getPage(): Page {
    if (!this.page) {
      throw new Error('Page not initialized. Call initialize() first.');
    }
    return this.page;
  }

  async cleanup(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
      this.context = null;
      this.page = null;
    }
  }

  async navigate(url: string): Promise<void> {
    if (!this.page) throw new Error('User agent not initialized');
    console.log(chalk.gray(`→ Navigating to ${url}`));
    await this.page.goto(url, { waitUntil: 'networkidle' });
  }

  async login(email: string, password: string): Promise<boolean> {
    if (!this.page) throw new Error('User agent not initialized');
    
    try {
      console.log(chalk.blue('🔐 Attempting login...'));
      
      // Navigate to app
      await this.navigate(this.config.frontendUrl);
      
      // Look for login form
      const emailInput = await this.page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first();
      const passwordInput = await this.page.locator('input[type="password"], input[name="password"]').first();
      
      if (!await emailInput.isVisible() || !await passwordInput.isVisible()) {
        console.log(chalk.yellow('⚠️  Login form not found, might already be logged in'));
        return true;
      }
      
      // Fill credentials
      await emailInput.fill(email);
      await passwordInput.fill(password);
      
      // Find and click submit button
      const submitButton = await this.page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Přihlásit")').first();
      await submitButton.click();
      
      // Wait for navigation or error
      await this.page.waitForTimeout(2000);
      
      // Check if login successful (no error messages, login form gone)
      const hasError = await this.page.locator('.error, .alert-error, [role="alert"]').count() > 0;
      const stillOnLogin = await emailInput.isVisible().catch(() => false);
      
      if (hasError) {
        const errorText = await this.page.locator('.error, .alert-error, [role="alert"]').first().textContent();
        console.log(chalk.red(`✗ Login failed: ${errorText}`));
        return false;
      }
      
      if (!stillOnLogin) {
        console.log(chalk.green('✓ Login successful'));
        return true;
      }
      
      console.log(chalk.yellow('⚠️  Login status unclear'));
      return false;
      
    } catch (error: any) {
      console.log(chalk.red(`✗ Login error: ${error.message}`));
      return false;
    }
  }

  async register(email: string, password: string, firstName: string, lastName: string): Promise<boolean> {
    if (!this.page) throw new Error('User agent not initialized');
    
    try {
      console.log(chalk.blue('📝 Attempting registration...'));
      
      // Navigate to app
      await this.navigate(this.config.frontendUrl);
      
      // Look for register link
      const registerLink = await this.page.locator('a:has-text("Register"), a:has-text("Registrace"), a:has-text("Sign up")').first();
      if (await registerLink.isVisible()) {
        await registerLink.click();
        await this.page.waitForTimeout(1000);
      }
      
      // Fill registration form
      await this.page.locator('input[name="email"], input[type="email"]').first().fill(email);
      await this.page.locator('input[name="password"], input[type="password"]').first().fill(password);
      
      // Try to find name fields
      const firstNameInput = await this.page.locator('input[name="firstName"], input[name="first_name"], input[placeholder*="first" i]').first();
      const lastNameInput = await this.page.locator('input[name="lastName"], input[name="last_name"], input[placeholder*="last" i]').first();
      
      if (await firstNameInput.isVisible()) {
        await firstNameInput.fill(firstName);
      }
      if (await lastNameInput.isVisible()) {
        await lastNameInput.fill(lastName);
      }
      
      // Submit
      const submitButton = await this.page.locator('button[type="submit"], button:has-text("Register"), button:has-text("Registrovat")').first();
      await submitButton.click();
      
      await this.page.waitForTimeout(2000);
      
      // Check result
      const hasError = await this.page.locator('.error, .alert-error, [role="alert"]').count() > 0;
      
      if (hasError) {
        const errorText = await this.page.locator('.error, .alert-error, [role="alert"]').first().textContent();
        console.log(chalk.red(`✗ Registration failed: ${errorText}`));
        return false;
      }
      
      console.log(chalk.green('✓ Registration successful'));
      return true;
      
    } catch (error: any) {
      console.log(chalk.red(`✗ Registration error: ${error.message}`));
      return false;
    }
  }

  async executeAction(action: UserAction): Promise<void> {
    if (!this.page) throw new Error('User agent not initialized');
    
    console.log(chalk.gray(`  → ${action.description}`));
    
    switch (action.type) {
      case 'click':
        await this.page.locator(action.target!).first().click();
        break;
        
      case 'fill':
        await this.page.locator(action.target!).first().fill(action.value);
        break;
        
      case 'navigate':
        await this.navigate(action.value);
        break;
        
      case 'wait':
        await this.page.waitForTimeout(action.value || 1000);
        break;
        
      case 'screenshot':
        await this.page.screenshot({ 
          path: action.value || `screenshot-${Date.now()}.png`,
          fullPage: true 
        });
        break;
    }
  }

  async executeScenario(scenario: TestScenario): Promise<boolean> {
    console.log(chalk.cyan(`\n🎬 Running scenario: ${scenario.name}`));
    console.log(chalk.gray(`   ${scenario.description}`));
    
    try {
      // Execute actions
      for (const action of scenario.actions) {
        await this.executeAction(action);
      }
      
      // Run validations
      for (const validation of scenario.validations) {
        console.log(chalk.gray(`  ✓ Checking: ${validation.description}`));
        
        switch (validation.type) {
          case 'exists':
            const exists = await this.page!.locator(validation.target).count() > 0;
            if (!exists) {
              throw new Error(`Element not found: ${validation.target}`);
            }
            break;
            
          case 'contains':
            const text = await this.page!.locator(validation.target).textContent();
            if (!text?.includes(validation.expected)) {
              throw new Error(`Text not found. Expected: ${validation.expected}, Got: ${text}`);
            }
            break;
        }
      }
      
      console.log(chalk.green(`✅ Scenario passed: ${scenario.name}`));
      return true;
      
    } catch (error: any) {
      console.log(chalk.red(`❌ Scenario failed: ${scenario.name}`));
      console.log(chalk.red(`   Error: ${error.message}`));
      
      // Take screenshot on failure
      try {
        const screenshotPath = `failure-${scenario.name.replace(/\s/g, '-')}-${Date.now()}.png`;
        await this.page!.screenshot({ path: screenshotPath, fullPage: true });
        console.log(chalk.gray(`   Screenshot saved: ${screenshotPath}`));
      } catch {}
      
      return false;
    }
  }

  async getCurrentUrl(): Promise<string> {
    if (!this.page) throw new Error('User agent not initialized');
    return this.page.url();
  }

  async takeScreenshot(filename?: string): Promise<string> {
    if (!this.page) throw new Error('User agent not initialized');
    const path = filename || `screenshot-${Date.now()}.png`;
    await this.page.screenshot({ path, fullPage: true });
    return path;
  }

}