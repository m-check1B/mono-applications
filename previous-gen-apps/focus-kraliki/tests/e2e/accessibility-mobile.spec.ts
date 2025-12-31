import { test, expect } from '@playwright/test';
import TestUtils from './utils/test-utils';

test.describe('Accessibility and Mobile Testing', () => {
  let testUtils: TestUtils;

  test.beforeEach(async ({ page }) => {
    testUtils = new TestUtils(page);

    // Login with demo credentials
    await page.goto('/');
    await testUtils.safeFill('input[type="email"]', 'test@focus-kraliki.app');
    await testUtils.safeFill('input[type="password"]', 'test123');
    await testUtils.safeClick('button[type="submit"]');
    await expect(page.locator('text=Dashboard')).toBeVisible({ timeout: 10000 });
  });

  test.describe('Accessibility Testing', () => {
    test('should check basic accessibility compliance', async ({ page }) => {
      await testUtils.takeScreenshot('accessibility-dashboard', 'Dashboard for accessibility check');

      // Check for missing alt text on images
      const images = await page.$$eval('img', imgs =>
        imgs.filter(img => !img.alt || img.alt.trim() === '').length
      );
      console.log(`Images without alt text: ${images}`);
      expect(images).toBeLessThan(3);

      // Check for proper heading hierarchy
      const headings = await page.$$eval('h1, h2, h3, h4, h5, h6', headings =>
        headings.map(h => h.tagName)
      );
      console.log(`Heading hierarchy: ${headings.join(', ')}`);

      // Check for form labels
      const formInputs = await page.$$eval('input:not([type="hidden"]), textarea, select', inputs =>
        inputs.filter(input => !input.labels || input.labels.length === 0).length
      );
      console.log(`Form inputs without labels: ${formInputs}`);
      expect(formInputs).toBeLessThan(2);

      // Check for ARIA labels on interactive elements
      const buttonsWithoutLabels = await page.$$eval('button', buttons =>
        buttons.filter(button =>
          !button.textContent?.trim() &&
          !button.getAttribute('aria-label') &&
          !button.getAttribute('title')
        ).length
      );
      console.log(`Buttons without accessible labels: ${buttonsWithoutLabels}`);
      expect(buttonsWithoutLabels).toBeLessThan(2);
    });

    test('should test keyboard navigation', async ({ page }) => {
      await testUtils.takeScreenshot('keyboard-nav-start', 'Starting keyboard navigation test');

      // Test Tab navigation through main elements
      const focusableElements = [
        'nav >> button',
        'nav >> a',
        'input',
        'button',
        'select',
        'textarea'
      ];

      for (let i = 0; i < focusableElements.length; i++) {
        await page.keyboard.press('Tab');
        await page.waitForTimeout(200);

        const focusedElement = await page.evaluate(() => {
          const active = document.activeElement;
          return {
            tagName: active?.tagName,
            type: active?.getAttribute('type'),
            placeholder: active?.getAttribute('placeholder'),
            textContent: active?.textContent?.trim()
          };
        });

        console.log(`Tab ${i + 1}: ${JSON.stringify(focusedElement)}`);
      }

      await testUtils.takeScreenshot('keyboard-nav-end', 'End of keyboard navigation test');
    });

    test('should test screen reader compatibility', async ({ page }) => {
      // Check for proper ARIA roles
      const ariaRoles = [
        { role: 'navigation', selector: 'nav' },
        { role: 'main', selector: 'main' },
        { role: 'complementary', selector: 'aside' },
        { role: 'banner', selector: 'header' },
        { role: 'contentinfo', selector: 'footer' }
      ];

      for (const { role, selector } of ariaRoles) {
        const elements = await page.$$(selector);
        console.log(`Found ${elements.length} elements for role "${role}" using selector "${selector}"`);

        // Check if any element has the role
        const hasRole = await page.$$eval(selector, elements =>
          elements.some(el => el.getAttribute('role'))
        );

        if (!hasRole && elements.length > 0) {
          console.log(`⚠️  Elements found for "${selector}" but no explicit ARIA role "${role}"`);
        }
      }

      await testUtils.takeScreenshot('screen-reader-test', 'Screen reader compatibility check');
    });

    test('should test color contrast and visual accessibility', async ({ page }) => {
      // Check for sufficient color contrast (simplified test)
      const textElements = await page.$$eval('p, span, div', elements =>
        elements.map(el => {
          const styles = window.getComputedStyle(el);
          return {
            fontSize: styles.fontSize,
            fontWeight: styles.fontWeight,
            color: styles.color,
            backgroundColor: styles.backgroundColor
          };
        })
      );

      console.log(`Found ${textElements.length} text elements for contrast analysis`);

      // Look for potential contrast issues (very small text with light colors)
      const potentialIssues = textElements.filter(el => {
        const fontSize = parseFloat(el.fontSize);
        const isSmallText = fontSize < 14;
        const hasLightColor = el.color.includes('rgb(255') || el.color.includes('#fff');
        return isSmallText && hasLightColor;
      });

      console.log(`Potential contrast issues: ${potentialIssues.length}`);
      expect(potentialIssues.length).toBeLessThan(5);

      await testUtils.takeScreenshot('color-contrast-test', 'Color contrast analysis');
    });

    test('should test focus management', async ({ page }) => {
      // Test modal focus management
      await testUtils.safeClick('text=Tasks');
      await testUtils.waitForNetworkIdle();

      // Try to open a modal/dialog
      const createTaskButton = page.locator('button:has-text("Add Task"), button:has-text("Create")').first();
      if (await createTaskButton.isVisible()) {
        await testUtils.safeClick('button:has-text("Add Task"), button:has-text("Create")');
        await testUtils.waitForNetworkIdle();

        await testUtils.takeScreenshot('modal-focus-test', 'Modal focus management test');

        // Check if focus is trapped in modal
        const modal = page.locator('.modal, .dialog, [role="dialog"]').first();
        if (await modal.isVisible()) {
          const focusedElement = await page.evaluate(() => {
            const active = document.activeElement;
            return active?.closest('.modal, .dialog, [role="dialog"]') !== null;
          });

          console.log(`Focus trapped in modal: ${focusedElement}`);
          expect(focusedElement).toBeTruthy();

          // Close modal
          await page.keyboard.press('Escape');
          await testUtils.waitForNetworkIdle();
        }
      }
    });
  });

  test.describe('Mobile Responsiveness Testing', () => {
    test.use({ viewport: { width: 375, height: 667 } }); // iPhone 6/7/8

    test('should display correctly on mobile devices', async ({ page }) => {
      await testUtils.takeScreenshot('mobile-dashboard', 'Mobile dashboard view');

      // Check for mobile navigation
      const mobileNav = page.locator('.mobile-nav, nav.mobile, [role="navigation"].mobile').first();
      if (await mobileNav.isVisible()) {
        await testUtils.takeScreenshot('mobile-nav', 'Mobile navigation');
      }

      // Check for hamburger menu
      const hamburgerMenu = page.locator('button:has-text("☰"), button[aria-label*="menu"], .hamburger').first();
      if (await hamburgerMenu.isVisible()) {
        await testUtils.safeClick('button:has-text("☰"), button[aria-label*="menu"], .hamburger');
        await testUtils.waitForNetworkIdle();
        await testUtils.takeScreenshot('mobile-menu-open', 'Mobile menu open');
      }

      // Test touch interactions
      const touchableElements = page.locator('button, a, input, select, textarea');
      const touchableCount = await touchableElements.count();
      console.log(`Touchable elements on mobile: ${touchableCount}`);

      // Ensure touch targets are large enough (minimum 44x44 pixels)
      const smallTouchTargets = await page.$$eval('button, a', elements =>
        elements.filter(el => {
          const rect = el.getBoundingClientRect();
          return rect.width < 44 || rect.height < 44;
        }).length
      );

      console.log(`Small touch targets (<44px): ${smallTouchTargets}`);
      expect(smallTouchTargets).toBeLessThan(3);
    });

    test('should test mobile task management', async ({ page }) => {
      await testUtils.safeClick('text=Tasks');
      await testUtils.waitForNetworkIdle();

      await testUtils.takeScreenshot('mobile-tasks', 'Mobile tasks view');

      // Test task creation on mobile
      const quickAddInput = page.locator('input[placeholder*="task"], textarea[placeholder*="task"]').first();
      if (await quickAddInput.isVisible()) {
        const uniqueData = testUtils.generateUniqueData('mobile');
        await testUtils.safeFill('input[placeholder*="task"], textarea[placeholder*="task"]', uniqueData.title);
        await testUtils.press('input[placeholder*="task"], textarea[placeholder*="task"]', 'Enter');
        await testUtils.waitForNetworkIdle();

        await testUtils.takeScreenshot('mobile-task-created', 'Task created on mobile');

        // Verify task appears
        await expect(page.locator(`text=${uniqueData.title}`)).toBeVisible();
      }

      // Test task view switching on mobile
      const viewButtons = page.locator('button:has-text("View"), button:has-text("List"), button:has-text("Kanban")');
      const viewCount = await viewButtons.count();

      for (let i = 0; i < viewCount; i++) {
        const button = viewButtons.nth(i);
        const buttonText = await button.textContent();
        if (buttonText) {
          await testUtils.safeClick(`button:has-text("${buttonText}")`);
          await testUtils.waitForNetworkIdle();
          await testUtils.takeScreenshot(`mobile-view-${buttonText.toLowerCase()}`, `Mobile ${buttonText} view`);
        }
      }
    });

    test('should test mobile AI Chat interface', async ({ page }) => {
      await testUtils.safeClick('text=AI Chat');
      await testUtils.waitForNetworkIdle();

      await testUtils.takeScreenshot('mobile-ai-chat', 'Mobile AI Chat interface');

      // Test chat input on mobile
      const chatInput = page.locator('textarea[placeholder*="Ask"], textarea[placeholder*="message"]').first();
      if (await chatInput.isVisible()) {
        const testMessage = 'Test message from mobile';
        await testUtils.safeFill('textarea[placeholder*="Ask"], textarea[placeholder*="message"]', testMessage);
        await testUtils.takeScreenshot('mobile-chat-input', 'Mobile chat input filled');

        await testUtils.safeClick('button:has-text("Send"), button:has-text("Submit")');
        await testUtils.waitForNetworkIdle();

        await testUtils.takeScreenshot('mobile-chat-sent', 'Message sent from mobile');
      }

      // Test mobile voice button
      const voiceButton = page.locator('button:has(svg[class*="Mic"]), button[aria-label*="voice"]').first();
      if (await voiceButton.isVisible()) {
        await testUtils.takeScreenshot('mobile-voice-button', 'Mobile voice button');
      }
    });
  });

  test.describe('Tablet Responsiveness Testing', () => {
    test.use({ viewport: { width: 768, height: 1024 } }); // iPad

    test('should display correctly on tablet devices', async ({ page }) => {
      await testUtils.takeScreenshot('tablet-dashboard', 'Tablet dashboard view');

      // Test navigation menu visibility
      const navMenu = page.locator('nav').first();
      expect(await navMenu.isVisible()).toBeTruthy();

      // Test sidebar behavior
      const sidebar = page.locator('.sidebar, aside').first();
      if (await sidebar.isVisible()) {
        await testUtils.takeScreenshot('tablet-sidebar', 'Tablet sidebar view');
      }

      // Test content layout
      const mainContent = page.locator('main, .main-content').first();
      expect(await mainContent.isVisible()).toBeTruthy();

      // Test form interactions
      await testUtils.safeClick('text=Tasks');
      await testUtils.waitForNetworkIdle();

      const taskForm = page.locator('form, .task-form').first();
      if (await taskForm.isVisible()) {
        await testUtils.takeScreenshot('tablet-task-form', 'Tablet task form');
      }
    });
  });

  test.describe('Cross-Browser Compatibility', () => {
    test('should work in different viewport sizes', async ({ page }) => {
      const viewports = [
        { width: 1920, height: 1080, name: 'Desktop' },
        { width: 1366, height: 768, name: 'Laptop' },
        { width: 768, height: 1024, name: 'Tablet' },
        { width: 375, height: 667, name: 'Mobile' }
      ];

      for (const viewport of viewports) {
        console.log(`Testing viewport: ${viewport.name} (${viewport.width}x${viewport.height})`);

        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await page.goto('/');
        await testUtils.waitForNetworkIdle();

        await testUtils.takeScreenshot(`viewport-${viewport.name.toLowerCase()}`, `${viewport.name} viewport`);

        // Test basic functionality
        const dashboardVisible = await testUtils.isVisible('text=Dashboard, text=Focus by Kraliki');
        console.log(`${viewport.name}: Dashboard visible: ${dashboardVisible}`);

        // Test navigation
        const navVisible = await testUtils.isVisible('nav');
        console.log(`${viewport.name}: Navigation visible: ${navVisible}`);

        // Test responsive behavior
        const hamburgerVisible = await testUtils.isVisible('button:has-text("☰"), .hamburger');
        console.log(`${viewport.name}: Hamburger menu visible: ${hamburgerVisible}`);

        expect(dashboardVisible).toBeTruthy();
      }
    });

    test('should handle orientation changes', async ({ page }) => {
      // Test landscape orientation
      await page.setViewportSize({ width: 667, height: 375 }); // iPhone 6/7/8 landscape
      await page.goto('/');
      await testUtils.waitForNetworkIdle();

      await testUtils.takeScreenshot('mobile-landscape', 'Mobile landscape orientation');

      // Test portrait orientation
      await page.setViewportSize({ width: 375, height: 667 }); // iPhone 6/7/8 portrait
      await page.goto('/');
      await testUtils.waitForNetworkIdle();

      await testUtils.takeScreenshot('mobile-portrait', 'Mobile portrait orientation');

      // Test if layout adapts properly
      const contentArea = page.locator('main, .main-content').first();
      const isVisible = await contentArea.isVisible();
      expect(isVisible).toBeTruthy();
    });
  });

  test.describe('Performance Testing on Mobile', () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test('should measure mobile performance', async ({ page }) => {
      const loadTime = await testUtils.measurePerformance('Mobile page load', async () => {
        await page.goto('/');
        await testUtils.waitForNetworkIdle();
      });

      console.log(`Mobile load time: ${loadTime}ms`);
      expect(loadTime).toBeLessThan(15000); // Longer timeout for mobile
    });

    test('should test mobile interactions performance', async ({ page }) => {
      await testUtils.safeClick('text=Tasks');
      await testUtils.waitForNetworkIdle();

      const interactionTimes = [];

      // Test multiple interactions
      for (let i = 0; i < 3; i++) {
        const startTime = performance.now();

        const uniqueData = testUtils.generateUniqueData(`mobile-perf-${i}`);
        await testUtils.safeFill('input[placeholder*="task"]', uniqueData.title);
        await testUtils.press('input[placeholder*="task"]', 'Enter');

        const endTime = performance.now();
        interactionTimes.push(endTime - startTime);
      }

      const averageTime = interactionTimes.reduce((a, b) => a + b, 0) / interactionTimes.length;
      console.log(`Average mobile interaction time: ${averageTime}ms`);
      expect(averageTime).toBeLessThan(4000);
    });
  });
});