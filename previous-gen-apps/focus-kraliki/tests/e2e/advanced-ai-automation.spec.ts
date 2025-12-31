import { test, expect } from '@playwright/test';
import TestUtils from './utils/test-utils';

test.describe('Advanced AI and Automation Features', () => {
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

  test.describe('AI-Powered Task Automation', () => {
    test('should handle natural language task parsing', async ({ page }) => {
      await testUtils.safeClick('text=AI Chat');
      await testUtils.waitForNetworkIdle();

      const naturalLanguageTasks = [
        'Schedule a team meeting for next Monday at 2 PM about the Q4 roadmap',
        'Create a task to review the pull requests in the repository',
        'Set up a reminder to call the client about project status tomorrow',
        'Organize a brainstorming session for new feature ideas next week'
      ];

      for (let i = 0; i < naturalLanguageTasks.length; i++) {
        const task = naturalLanguageTasks[i];
        console.log(`Testing natural language task: ${task}`);

        // Send natural language request
        await testUtils.safeFill('textarea[placeholder*="Ask"], textarea[placeholder*="message"]', task);
        await testUtils.takeScreenshot(`nl-task-input-${i}`, `Natural language task input ${i + 1}`);

        await testUtils.safeClick('button:has-text("Send"), button:has-text("Submit")');
        await testUtils.waitForNetworkIdle();

        // Wait for AI response
        await testUtils.waitForSelector('.bg-gray-100, .dark\\:bg-gray-800, .ai-response', { timeout: 15000 });
        await testUtils.takeScreenshot(`nl-task-response-${i}`, `AI response to task ${i + 1}`);

        // Check if task creation notification appears
        const taskCreated = await testUtils.elementExists('[data-testid*="task-created"], .toast, .notification');
        if (taskCreated) {
          console.log(`✅ Task created from natural language: ${task}`);
        }
      }
    });

    test('should test AI mode switching', async ({ page }) => {
      await testUtils.safeClick('text=AI Chat');
      await testUtils.waitForNetworkIdle();

      const aiModes = [
        { name: 'Standard', placeholder: 'standard' },
        { name: 'High Reasoning', placeholder: 'high-reasoning' },
        { name: 'Collaborative', placeholder: 'collaborative' }
      ];

      for (const mode of aiModes) {
        console.log(`Testing AI mode: ${mode.name}`);

        // Click mode button
        await testUtils.safeClick(`button:has-text("${mode.name}")`);
        await testUtils.waitForNetworkIdle();

        // Verify placeholder changes
        const input = page.locator('textarea[placeholder*="Ask"], textarea[placeholder*="message"]').first();
        const placeholder = await input.getAttribute('placeholder') || '';

        expect(placeholder.toLowerCase()).toContain(mode.placeholder.toLowerCase());
        await testUtils.takeScreenshot(`ai-mode-${mode.name.toLowerCase()}`, `AI ${mode.name} mode`);
      }
    });

    test('should test voice input functionality', async ({ page }) => {
      await testUtils.safeClick('text=AI Chat');
      await testUtils.waitForNetworkIdle();

      // Find voice button
      const voiceButton = page.locator('button:has(svg[class*="Mic"]), button[aria-label*="voice"], button[title*="voice"]').first();

      if (await voiceButton.isVisible()) {
        console.log('Testing voice input button...');

        // Click voice button
        await testUtils.safeClick('button:has(svg[class*="Mic"])');

        // Check if recording state is indicated
        await testUtils.waitForTimeout(2000);
        await testUtils.takeScreenshot('voice-recording', 'Voice input recording state');

        // Click again to stop recording
        await testUtils.safeClick('button:has(svg[class*="Mic"])');
        await testUtils.waitForNetworkIdle();
      }
    });
  });

  test.describe('Shadow Work and Cognitive Features', () => {
    test('should navigate to Shadow Work', async ({ page }) => {
      await testUtils.safeClick('text=Shadow Work');
      await testUtils.waitForNetworkIdle();

      await expect(page.locator('h1:has-text("Shadow Work")')).toBeVisible();
      await expect(page.locator('text=Day')).toBeVisible();
      await expect(page.locator('text=of 30')).toBeVisible();

      await testUtils.takeScreenshot('shadow-work-main', 'Shadow Work main page');
    });

    test('should test shadow work daily exercises', async ({ page }) => {
      await testUtils.safeClick('text=Shadow Work');
      await testUtils.waitForNetworkIdle();

      // Look for daily exercise
      const exerciseCard = page.locator('.exercise-card, .daily-exercise, .shadow-card').first();
      if (await exerciseCard.isVisible()) {
        await testUtils.takeScreenshot('shadow-work-exercise', 'Shadow work daily exercise');

        // Try to start exercise
        const startButton = page.locator('button:has-text("Start"), button:has-text("Begin")').first();
        if (await startButton.isVisible()) {
          await testUtils.safeClick('button:has-text("Start"), button:has-text("Begin")');
          await testUtils.waitForNetworkIdle();
          await testUtils.takeScreenshot('shadow-work-exercise-started', 'Shadow work exercise started');
        }
      }
    });

    test('should access Cognitive Status dashboard', async ({ page }) => {
      await testUtils.safeClick('text=Cognitive');
      await testUtils.waitForNetworkIdle();

      await expect(page.locator('h1:has-text("Cognitive Status")')).toBeVisible();

      // Check for cognitive metrics
      const metrics = ['Energy', 'Focus', 'Creativity', 'Stress'];
      for (const metric of metrics) {
        await expect(page.locator(`text=${metric}`)).toBeVisible();
      }

      await testUtils.takeScreenshot('cognitive-status', 'Cognitive Status dashboard');
    });

    test('should test cognitive status updates', async ({ page }) => {
      await testUtils.safeClick('text=Cognitive');
      await testUtils.waitForNetworkIdle();

      // Look for update controls
      const updateControls = page.locator('input[type="range"], select, .metric-control').first();
      if (await updateControls.isVisible()) {
        await testUtils.takeScreenshot('cognitive-controls', 'Cognitive status update controls');

        // Try to update a metric
        const energySlider = page.locator('input[aria-label*="Energy"], input[name*="energy"]').first();
        if (await energySlider.isVisible()) {
          await energySlider.fill('7');
          await testUtils.waitForNetworkIdle();
          await testUtils.takeScreenshot('cognitive-updated', 'Cognitive status after update');
        }
      }
    });
  });

  test.describe('Type System and Customization', () => {
    test('should access Type Manager', async ({ page }) => {
      await testUtils.safeClick('text=Types');
      await testUtils.waitForNetworkIdle();

      await expect(page.locator('h2:has-text("Type Manager")')).toBeVisible();
      await expect(page.locator('text=Customize your mental model')).toBeVisible();

      await testUtils.takeScreenshot('type-manager', 'Type Manager interface');
    });

    test('should test type creation and management', async ({ page }) => {
      await testUtils.safeClick('text=Types');
      await testUtils.waitForNetworkIdle();

      // Look for existing types
      const existingTypes = page.locator('.type-item, .type-card').first();
      if (await existingTypes.isVisible()) {
        await testUtils.takeScreenshot('existing-types', 'Existing type items');
      }

      // Look for create type button
      const createTypeButton = page.locator('button:has-text("Create Type"), button:has-text("Add Type")').first();
      if (await createTypeButton.isVisible()) {
        await testUtils.safeClick('button:has-text("Create Type"), button:has-text("Add Type")');
        await testUtils.waitForNetworkIdle();

        // Fill type creation form
        const uniqueData = testUtils.generateUniqueData('type');
        await testUtils.safeFill('input[name*="name"], input[placeholder*="name"]', uniqueData.title);
        await testUtils.safeFill('textarea[placeholder*="description"], input[placeholder*="description"]', uniqueData.description);

        await testUtils.takeScreenshot('type-creation', 'Type creation form');

        // Submit type creation
        await testUtils.safeClick('button:has-text("Create"), button:has-text("Save")');
        await testUtils.waitForNetworkIdle();

        // Verify type was created
        await expect(page.locator(`text=${uniqueData.title}`)).toBeVisible();
      }
    });
  });

  test.describe('Automation and Workflow Features', () => {
    test('should test task automation workflows', async ({ page }) => {
      // Navigate to automation section
      await testUtils.safeClick('text=Automation, text=Workflows');
      await testUtils.waitForNetworkIdle();

      await expect(page.locator('h1:has-text("Automation"), h2:has-text("Workflows")')).toBeVisible();
      await testUtils.takeScreenshot('automation-dashboard', 'Automation dashboard');
    });

    test('should test workflow creation', async ({ page }) => {
      await testUtils.safeClick('text=Automation, text=Workflows');
      await testUtils.waitForNetworkIdle();

      // Look for create workflow button
      const createWorkflowButton = page.locator('button:has-text("Create Workflow"), button:has-text("New Workflow")').first();
      if (await createWorkflowButton.isVisible()) {
        await testUtils.safeClick('button:has-text("Create Workflow"), button:has-text("New Workflow")');
        await testUtils.waitForNetworkIdle();

        await testUtils.takeScreenshot('workflow-creation', 'Workflow creation interface');

        // Test workflow triggers
        const triggers = page.locator('.trigger-select, .workflow-trigger').first();
        if (await triggers.isVisible()) {
          await testUtils.takeScreenshot('workflow-triggers', 'Workflow trigger selection');
        }

        // Test workflow actions
        const actions = page.locator('.action-select, .workflow-action').first();
        if (await actions.isVisible()) {
          await testUtils.takeScreenshot('workflow-actions', 'Workflow action selection');
        }
      }
    });

    test('should test scheduled automation', async ({ page }) => {
      await testUtils.safeClick('text=Automation, text=Workflows');
      await testUtils.waitForNetworkIdle();

      // Look for scheduled tasks
      const scheduledTasks = page.locator('.scheduled-tasks, .automation-schedule').first();
      if (await scheduledTasks.isVisible()) {
        await testUtils.takeScreenshot('scheduled-tasks', 'Scheduled automation tasks');

        // Test schedule creation
        const createScheduleButton = page.locator('button:has-text("Create Schedule"), button:has-text("Add Schedule")').first();
        if (await createScheduleButton.isVisible()) {
          await testUtils.safeClick('button:has-text("Create Schedule"), button:has-text("Add Schedule")');
          await testUtils.waitForNetworkIdle();
          await testUtils.takeScreenshot('schedule-creation', 'Schedule creation interface');
        }
      }
    });
  });

  test.describe('Performance and Load Testing', () => {
    test('should measure page load performance', async ({ page }) => {
      const loadTime = await testUtils.measurePerformance('Page load', async () => {
        await page.goto('/');
        await testUtils.waitForNetworkIdle();
      });

      console.log(`Page load time: ${loadTime}ms`);

      // Performance assertion (adjust threshold as needed)
      expect(loadTime).toBeLessThan(10000);
    });

    test('should measure task creation performance', async ({ page }) => {
      await testUtils.safeClick('text=Tasks');
      await testUtils.waitForNetworkIdle();

      const creationTime = await testUtils.measurePerformance('Task creation', async () => {
        const uniqueData = testUtils.generateUniqueData('performance');
        await testUtils.safeFill('input[placeholder*="task"]', uniqueData.title);
        await testUtils.press('input[placeholder*="task"]', 'Enter');
        await testUtils.waitForNetworkIdle();
      });

      console.log(`Task creation time: ${creationTime}ms`);

      // Performance assertion
      expect(creationTime).toBeLessThan(5000);
    });

    test('should handle multiple rapid interactions', async ({ page }) => {
      await testUtils.safeClick('text=Tasks');
      await testUtils.waitForNetworkIdle();

      const interactionCount = 5;
      const interactionTimes = [];

      for (let i = 0; i < interactionCount; i++) {
        const startTime = performance.now();

        const uniqueData = testUtils.generateUniqueData(`rapid-${i}`);
        await testUtils.safeFill('input[placeholder*="task"]', uniqueData.title);
        await testUtils.press('input[placeholder*="task"]', 'Enter');

        const endTime = performance.now();
        interactionTimes.push(endTime - startTime);
      }

      const averageTime = interactionTimes.reduce((a, b) => a + b, 0) / interactionTimes.length;
      console.log(`Average rapid interaction time: ${averageTime}ms`);

      // Performance assertion for rapid interactions
      expect(averageTime).toBeLessThan(3000);
    });
  });
});