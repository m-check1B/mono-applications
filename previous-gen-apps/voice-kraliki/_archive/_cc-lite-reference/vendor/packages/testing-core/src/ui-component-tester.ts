/**
 * UI Component Tester - Tests Stack 2025 UI components specifically
 */

import { Page } from 'playwright';
import chalk from 'chalk';
import { AppConfig, TestCase } from './types';

export interface UIComponentTestResult {
  component: string;
  tests: ComponentTest[];
  screenshots: string[];
  success: boolean;
}

export interface ComponentTest {
  name: string;
  action: string;
  result: 'passed' | 'failed';
  error?: string;
  screenshot?: string;
}

export class UIComponentTester {
  private page: Page;
  private config: AppConfig;
  private screenshotCount = 0;

  constructor(page: Page, config: AppConfig) {
    this.page = page;
    this.config = config;
  }

  async testAllUIComponents(): Promise<UIComponentTestResult[]> {
    console.log(chalk.blue('🎨 Starting UI Component Tests...'));
    
    const results: UIComponentTestResult[] = [];
    
    // Test each component type
    const components = [
      'buttons',
      'inputs', 
      'forms',
      'navigation',
      'cards',
      'modals',
      'dropdowns',
      'tabs',
      'badges',
      'progress',
      'toasts'
    ];

    for (const component of components) {
      try {
        const result = await this.testComponent(component);
        results.push(result);
        
        if (result.success) {
          console.log(chalk.green(`✅ ${component} tests passed`));
        } else {
          console.log(chalk.red(`❌ ${component} tests failed`));
        }
      } catch (error) {
        console.log(chalk.red(`💥 ${component} testing crashed: ${error}`));
        results.push({
          component,
          tests: [],
          screenshots: [],
          success: false
        });
      }
    }

    return results;
  }

  private async testComponent(componentType: string): Promise<UIComponentTestResult> {
    const tests: ComponentTest[] = [];
    const screenshots: string[] = [];
    
    console.log(chalk.cyan(`🔍 Testing ${componentType} components...`));

    switch (componentType) {
      case 'buttons':
        return await this.testButtons();
      case 'inputs':
        return await this.testInputs();
      case 'forms':
        return await this.testForms();
      case 'navigation':
        return await this.testNavigation();
      case 'cards':
        return await this.testCards();
      case 'modals':
        return await this.testModals();
      case 'dropdowns':
        return await this.testDropdowns();
      case 'tabs':
        return await this.testTabs();
      case 'badges':
        return await this.testBadges();
      case 'progress':
        return await this.testProgress();
      case 'toasts':
        return await this.testToasts();
      default:
        return { component: componentType, tests: [], screenshots: [], success: false };
    }
  }

  private async testButtons(): Promise<UIComponentTestResult> {
    const tests: ComponentTest[] = [];
    const screenshots: string[] = [];

    // Take initial screenshot
    const initialScreenshot = await this.takeScreenshot('buttons-initial');
    screenshots.push(initialScreenshot);

    // Test different button types
    const buttonSelectors = [
      'button:has-text("Save")',
      'button:has-text("Cancel")',
      'button:has-text("Delete")',
      'button:has-text("Submit")',
      'button:has-text("Create")',
      'button:has-text("Edit")',
      'button:has-text("Add")',
      'button[type="submit"]',
      'button[type="button"]',
      '.btn',
      '[role="button"]'
    ];

    for (const selector of buttonSelectors) {
      try {
        const buttons = await this.page.locator(selector);
        const count = await buttons.count();
        
        if (count > 0) {
          console.log(chalk.gray(`  Found ${count} buttons matching "${selector}"`));
          
          // Test first button of this type
          const button = buttons.first();
          
          // Check if button is visible
          const isVisible = await button.isVisible();
          tests.push({
            name: `Button visibility (${selector})`,
            action: 'Check visibility',
            result: isVisible ? 'passed' : 'failed',
            error: isVisible ? undefined : 'Button not visible'
          });

          if (isVisible) {
            // Test hover state
            await button.hover();
            const hoverScreenshot = await this.takeScreenshot(`button-hover-${this.screenshotCount}`);
            screenshots.push(hoverScreenshot);

            // Test click (if it looks safe)
            const buttonText = await button.textContent() || '';
            if (!buttonText.toLowerCase().includes('delete') && 
                !buttonText.toLowerCase().includes('remove') &&
                !buttonText.toLowerCase().includes('logout')) {
              
              try {
                await button.click({ timeout: 2000 });
                const clickScreenshot = await this.takeScreenshot(`button-clicked-${this.screenshotCount}`);
                screenshots.push(clickScreenshot);
                
                tests.push({
                  name: `Button click (${buttonText})`,
                  action: 'Click button',
                  result: 'passed'
                });
              } catch (clickError) {
                tests.push({
                  name: `Button click (${buttonText})`,
                  action: 'Click button', 
                  result: 'failed',
                  error: String(clickError)
                });
              }
            }
          }
        }
      } catch (error) {
        tests.push({
          name: `Button test (${selector})`,
          action: 'Find and test button',
          result: 'failed',
          error: String(error)
        });
      }
    }

    return {
      component: 'buttons',
      tests,
      screenshots,
      success: tests.some(t => t.result === 'passed')
    };
  }

  private async testInputs(): Promise<UIComponentTestResult> {
    const tests: ComponentTest[] = [];
    const screenshots: string[] = [];

    const inputSelectors = [
      'input[type="text"]',
      'input[type="email"]',
      'input[type="password"]',
      'input[type="search"]',
      'textarea',
      'input[placeholder]',
      '.input'
    ];

    for (const selector of inputSelectors) {
      try {
        const inputs = await this.page.locator(selector);
        const count = await inputs.count();
        
        if (count > 0) {
          const input = inputs.first();
          const isVisible = await input.isVisible();
          
          tests.push({
            name: `Input visibility (${selector})`,
            action: 'Check visibility',
            result: isVisible ? 'passed' : 'failed'
          });

          if (isVisible) {
            // Test typing
            const testText = 'Test input value 123';
            await input.fill(testText);
            
            const inputScreenshot = await this.takeScreenshot(`input-filled-${this.screenshotCount}`);
            screenshots.push(inputScreenshot);
            
            const value = await input.inputValue();
            tests.push({
              name: `Input typing (${selector})`,
              action: 'Fill input with text',
              result: value === testText ? 'passed' : 'failed',
              error: value !== testText ? `Expected "${testText}", got "${value}"` : undefined
            });
          }
        }
      } catch (error) {
        tests.push({
          name: `Input test (${selector})`,
          action: 'Find and test input',
          result: 'failed',
          error: String(error)
        });
      }
    }

    return {
      component: 'inputs',
      tests,
      screenshots,
      success: tests.some(t => t.result === 'passed')
    };
  }

  private async testNavigation(): Promise<UIComponentTestResult> {
    const tests: ComponentTest[] = [];
    const screenshots: string[] = [];

    // Take navigation screenshot
    const navScreenshot = await this.takeScreenshot('navigation');
    screenshots.push(navScreenshot);

    const navSelectors = [
      'nav',
      '.navbar',
      '.navigation',
      '.sidebar',
      'header nav',
      '[role="navigation"]',
      'a[href*="/dashboard"]',
      'a[href*="/tasks"]',
      'a[href*="/calendar"]',
      'a[href*="/settings"]'
    ];

    for (const selector of navSelectors) {
      try {
        const elements = await this.page.locator(selector);
        const count = await elements.count();
        
        if (count > 0) {
          tests.push({
            name: `Navigation element found (${selector})`,
            action: 'Check existence',
            result: 'passed'
          });
          
          // Test first navigation element
          const element = elements.first();
          const isVisible = await element.isVisible();
          
          tests.push({
            name: `Navigation visibility (${selector})`,
            action: 'Check visibility',
            result: isVisible ? 'passed' : 'failed'
          });

          // If it's a link, try clicking it
          if (selector.includes('href') && isVisible) {
            try {
              await element.click({ timeout: 2000 });
              await this.page.waitForTimeout(1000);
              
              const afterClickScreenshot = await this.takeScreenshot(`nav-after-click-${this.screenshotCount}`);
              screenshots.push(afterClickScreenshot);
              
              tests.push({
                name: `Navigation link click (${selector})`,
                action: 'Click navigation link',
                result: 'passed'
              });
            } catch (clickError) {
              tests.push({
                name: `Navigation link click (${selector})`,
                action: 'Click navigation link',
                result: 'failed',
                error: String(clickError)
              });
            }
          }
        }
      } catch (error) {
        tests.push({
          name: `Navigation test (${selector})`,
          action: 'Find and test navigation',
          result: 'failed',
          error: String(error)
        });
      }
    }

    return {
      component: 'navigation',
      tests,
      screenshots,
      success: tests.some(t => t.result === 'passed')
    };
  }

  private async testCards(): Promise<UIComponentTestResult> {
    const tests: ComponentTest[] = [];
    const screenshots: string[] = [];

    const cardSelectors = [
      '.card',
      '.panel',
      '.widget',
      '[class*="card"]',
      '.task-card',
      '.project-card'
    ];

    for (const selector of cardSelectors) {
      try {
        const cards = await this.page.locator(selector);
        const count = await cards.count();
        
        if (count > 0) {
          tests.push({
            name: `Cards found (${selector})`,
            action: 'Count cards',
            result: 'passed'
          });

          const cardScreenshot = await this.takeScreenshot(`cards-${this.screenshotCount}`);
          screenshots.push(cardScreenshot);

          // Test first card interactions
          const card = cards.first();
          await card.hover();
          
          const hoverScreenshot = await this.takeScreenshot(`card-hover-${this.screenshotCount}`);
          screenshots.push(hoverScreenshot);
          
          tests.push({
            name: `Card hover (${selector})`,
            action: 'Hover over card',
            result: 'passed'
          });
        }
      } catch (error) {
        tests.push({
          name: `Card test (${selector})`,
          action: 'Find and test cards',
          result: 'failed',
          error: String(error)
        });
      }
    }

    return {
      component: 'cards',
      tests,
      screenshots,
      success: tests.some(t => t.result === 'passed')
    };
  }

  private async testModals(): Promise<UIComponentTestResult> {
    const tests: ComponentTest[] = [];
    const screenshots: string[] = [];

    // Look for modal triggers
    const modalTriggers = [
      'button:has-text("Add")',
      'button:has-text("Create")',
      'button:has-text("New")',
      '[data-modal-trigger]',
      '.modal-trigger'
    ];

    for (const trigger of modalTriggers) {
      try {
        const buttons = await this.page.locator(trigger);
        const count = await buttons.count();
        
        if (count > 0) {
          const button = buttons.first();
          const isVisible = await button.isVisible();
          
          if (isVisible) {
            await button.click();
            await this.page.waitForTimeout(1000);
            
            // Look for modal
            const modalSelectors = ['.modal', '.dialog', '[role="dialog"]', '.overlay'];
            
            for (const modalSelector of modalSelectors) {
              const modals = await this.page.locator(modalSelector);
              const modalCount = await modals.count();
              
              if (modalCount > 0) {
                const modal = modals.first();
                const isModalVisible = await modal.isVisible();
                
                if (isModalVisible) {
                  const modalScreenshot = await this.takeScreenshot(`modal-open-${this.screenshotCount}`);
                  screenshots.push(modalScreenshot);
                  
                  tests.push({
                    name: `Modal opens (${trigger})`,
                    action: 'Click trigger and check modal',
                    result: 'passed'
                  });
                  
                  // Try to close modal
                  const closeButtons = modal.locator('button:has-text("Cancel"), button:has-text("Close"), .close, [aria-label="Close"]');
                  const closeCount = await closeButtons.count();
                  
                  if (closeCount > 0) {
                    await closeButtons.first().click();
                    await this.page.waitForTimeout(500);
                    
                    const isStillVisible = await modal.isVisible();
                    tests.push({
                      name: `Modal closes (${trigger})`,
                      action: 'Click close button',
                      result: !isStillVisible ? 'passed' : 'failed'
                    });
                  }
                  
                  break; // Found and tested a modal
                }
              }
            }
          }
        }
      } catch (error) {
        tests.push({
          name: `Modal test (${trigger})`,
          action: 'Test modal functionality',
          result: 'failed',
          error: String(error)
        });
      }
    }

    return {
      component: 'modals',
      tests,
      screenshots,
      success: tests.some(t => t.result === 'passed')
    };
  }

  private async testDropdowns(): Promise<UIComponentTestResult> {
    const tests: ComponentTest[] = [];
    const screenshots: string[] = [];

    const dropdownSelectors = [
      'select',
      '.dropdown',
      '.select',
      '[role="combobox"]',
      '[role="listbox"]'
    ];

    for (const selector of dropdownSelectors) {
      try {
        const dropdowns = await this.page.locator(selector);
        const count = await dropdowns.count();
        
        if (count > 0) {
          const dropdown = dropdowns.first();
          const isVisible = await dropdown.isVisible();
          
          if (isVisible) {
            await dropdown.click();
            await this.page.waitForTimeout(500);
            
            const dropdownScreenshot = await this.takeScreenshot(`dropdown-open-${this.screenshotCount}`);
            screenshots.push(dropdownScreenshot);
            
            tests.push({
              name: `Dropdown opens (${selector})`,
              action: 'Click dropdown',
              result: 'passed'
            });
          }
        }
      } catch (error) {
        tests.push({
          name: `Dropdown test (${selector})`,
          action: 'Test dropdown functionality',
          result: 'failed',
          error: String(error)
        });
      }
    }

    return {
      component: 'dropdowns',
      tests,
      screenshots,
      success: tests.some(t => t.result === 'passed')
    };
  }

  private async testTabs(): Promise<UIComponentTestResult> {
    const tests: ComponentTest[] = [];
    const screenshots: string[] = [];

    const tabSelectors = [
      '[role="tab"]',
      '.tab',
      '.nav-tabs a',
      '.tabs button'
    ];

    for (const selector of tabSelectors) {
      try {
        const tabs = await this.page.locator(selector);
        const count = await tabs.count();
        
        if (count > 1) { // Need at least 2 tabs to test switching
          const firstTab = tabs.first();
          const secondTab = tabs.nth(1);
          
          // Click first tab
          await firstTab.click();
          await this.page.waitForTimeout(300);
          
          const firstTabScreenshot = await this.takeScreenshot(`tab1-active-${this.screenshotCount}`);
          screenshots.push(firstTabScreenshot);
          
          // Click second tab
          await secondTab.click();
          await this.page.waitForTimeout(300);
          
          const secondTabScreenshot = await this.takeScreenshot(`tab2-active-${this.screenshotCount}`);
          screenshots.push(secondTabScreenshot);
          
          tests.push({
            name: `Tab switching (${selector})`,
            action: 'Switch between tabs',
            result: 'passed'
          });
        }
      } catch (error) {
        tests.push({
          name: `Tab test (${selector})`,
          action: 'Test tab functionality',
          result: 'failed',
          error: String(error)
        });
      }
    }

    return {
      component: 'tabs',
      tests,
      screenshots,
      success: tests.some(t => t.result === 'passed')
    };
  }

  private async testBadges(): Promise<UIComponentTestResult> {
    const tests: ComponentTest[] = [];
    const screenshots: string[] = [];

    const badgeSelectors = [
      '.badge',
      '.chip',
      '.tag',
      '.status',
      '.label'
    ];

    for (const selector of badgeSelectors) {
      try {
        const badges = await this.page.locator(selector);
        const count = await badges.count();
        
        if (count > 0) {
          const badgeScreenshot = await this.takeScreenshot(`badges-${this.screenshotCount}`);
          screenshots.push(badgeScreenshot);
          
          tests.push({
            name: `Badges found (${selector})`,
            action: `Found ${count} badges`,
            result: 'passed'
          });
        }
      } catch (error) {
        tests.push({
          name: `Badge test (${selector})`,
          action: 'Find badges',
          result: 'failed',
          error: String(error)
        });
      }
    }

    return {
      component: 'badges',
      tests,
      screenshots,
      success: tests.some(t => t.result === 'passed')
    };
  }

  private async testProgress(): Promise<UIComponentTestResult> {
    const tests: ComponentTest[] = [];
    const screenshots: string[] = [];

    const progressSelectors = [
      'progress',
      '.progress',
      '.progress-bar',
      '[role="progressbar"]'
    ];

    for (const selector of progressSelectors) {
      try {
        const progressElements = await this.page.locator(selector);
        const count = await progressElements.count();
        
        if (count > 0) {
          const progressScreenshot = await this.takeScreenshot(`progress-${this.screenshotCount}`);
          screenshots.push(progressScreenshot);
          
          tests.push({
            name: `Progress bars found (${selector})`,
            action: `Found ${count} progress bars`,
            result: 'passed'
          });
        }
      } catch (error) {
        tests.push({
          name: `Progress test (${selector})`,
          action: 'Find progress bars',
          result: 'failed',
          error: String(error)
        });
      }
    }

    return {
      component: 'progress',
      tests,
      screenshots,
      success: tests.some(t => t.result === 'passed')
    };
  }

  private async testToasts(): Promise<UIComponentTestResult> {
    const tests: ComponentTest[] = [];
    const screenshots: string[] = [];

    // Look for toast trigger buttons
    const toastTriggers = [
      'button:has-text("Save")',
      'button:has-text("Submit")',
      'button[type="submit"]'
    ];

    for (const trigger of toastTriggers) {
      try {
        const buttons = await this.page.locator(trigger);
        const count = await buttons.count();
        
        if (count > 0) {
          const button = buttons.first();
          const isVisible = await button.isVisible();
          
          if (isVisible) {
            await button.click();
            await this.page.waitForTimeout(2000); // Wait for potential toast
            
            // Look for toasts
            const toastSelectors = ['.toast', '.notification', '.alert', '.snackbar'];
            
            for (const toastSelector of toastSelectors) {
              const toasts = await this.page.locator(toastSelector);
              const toastCount = await toasts.count();
              
              if (toastCount > 0) {
                const toastScreenshot = await this.takeScreenshot(`toast-${this.screenshotCount}`);
                screenshots.push(toastScreenshot);
                
                tests.push({
                  name: `Toast appears (${trigger})`,
                  action: 'Trigger action that shows toast',
                  result: 'passed'
                });
                break;
              }
            }
          }
        }
      } catch (error) {
        tests.push({
          name: `Toast test (${trigger})`,
          action: 'Test toast functionality',
          result: 'failed',
          error: String(error)
        });
      }
    }

    return {
      component: 'toasts',
      tests,
      screenshots,
      success: tests.some(t => t.result === 'passed')
    };
  }

  private async testForms(): Promise<UIComponentTestResult> {
    const tests: ComponentTest[] = [];
    const screenshots: string[] = [];

    const formSelectors = ['form', '.form', '[role="form"]'];

    for (const selector of formSelectors) {
      try {
        const forms = await this.page.locator(selector);
        const count = await forms.count();
        
        if (count > 0) {
          const form = forms.first();
          const isVisible = await form.isVisible();
          
          if (isVisible) {
            const formScreenshot = await this.takeScreenshot(`form-${this.screenshotCount}`);
            screenshots.push(formScreenshot);
            
            // Fill form fields
            const inputs = form.locator('input[type="text"], input[type="email"], textarea');
            const inputCount = await inputs.count();
            
            for (let i = 0; i < Math.min(inputCount, 3); i++) {
              const input = inputs.nth(i);
              await input.fill(`Test value ${i + 1}`);
            }
            
            const filledFormScreenshot = await this.takeScreenshot(`form-filled-${this.screenshotCount}`);
            screenshots.push(filledFormScreenshot);
            
            tests.push({
              name: `Form interaction (${selector})`,
              action: `Fill ${inputCount} form fields`,
              result: 'passed'
            });
          }
        }
      } catch (error) {
        tests.push({
          name: `Form test (${selector})`,
          action: 'Test form functionality',
          result: 'failed',
          error: String(error)
        });
      }
    }

    return {
      component: 'forms',
      tests,
      screenshots,
      success: tests.some(t => t.result === 'passed')
    };
  }

  private async takeScreenshot(name: string): Promise<string> {
    this.screenshotCount++;
    const filename = `${name}-${Date.now()}.png`;
    await this.page.screenshot({ path: filename, fullPage: true });
    console.log(chalk.gray(`📸 Screenshot: ${filename}`));
    return filename;
  }

  async generateReport(results: UIComponentTestResult[]): Promise<void> {
    console.log(chalk.blue.bold('\n🎨 UI COMPONENT TEST REPORT'));
    console.log(chalk.blue('='.repeat(50)));

    let totalTests = 0;
    let passedTests = 0;
    let totalScreenshots = 0;

    for (const result of results) {
      const componentPassed = result.tests.filter(t => t.result === 'passed').length;
      const componentFailed = result.tests.filter(t => t.result === 'failed').length;
      
      totalTests += result.tests.length;
      passedTests += componentPassed;
      totalScreenshots += result.screenshots.length;

      const status = result.success ? chalk.green('✅') : chalk.red('❌');
      console.log(`${status} ${result.component}: ${componentPassed}/${result.tests.length} tests passed, ${result.screenshots.length} screenshots`);
      
      if (componentFailed > 0) {
        const failedTests = result.tests.filter(t => t.result === 'failed');
        for (const test of failedTests.slice(0, 3)) { // Show max 3 failures
          console.log(chalk.red(`   ❌ ${test.name}: ${test.error || 'Unknown error'}`));
        }
      }
    }

    console.log(chalk.blue('-'.repeat(50)));
    console.log(`Total Tests: ${totalTests}`);
    console.log(chalk.green(`Passed: ${passedTests}`));
    console.log(chalk.red(`Failed: ${totalTests - passedTests}`));
    console.log(`Screenshots: ${totalScreenshots}`);
    console.log(`Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);
    console.log(chalk.blue('='.repeat(50)));
  }
}

// Export is already done in the class declaration above