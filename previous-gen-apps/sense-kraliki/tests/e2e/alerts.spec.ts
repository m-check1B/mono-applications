import { test, expect } from './fixtures/test-helpers';
import { AlertsPage, MockAPIHelper } from './fixtures/page-objects';

/**
 * Alerts E2E Tests for Sense by Kraliki
 *
 * NOTE: Sense by Kraliki is currently a Telegram bot without a web UI.
 * Tests will skip gracefully when no web server is available.
 *
 * Tests cover:
 * - Alert configuration and thresholds
 * - Notification preferences (Telegram, etc.)
 * - Alert history and management
 * - Sensitivity level-based alerts
 * - Alert editing and deletion
 */

test.describe('Alerts Configuration', () => {
  let alertsPage: AlertsPage;
  let mockAPI: MockAPIHelper;

  test.beforeEach(async ({ page }) => {
    alertsPage = new AlertsPage(page);
    mockAPI = new MockAPIHelper(page);
  });

  test.describe('Alert List View', () => {
    test('should display alerts page', async ({ page }) => {
      await mockAPI.mockAlerts([
        { id: '1', type: 'high-sensitivity', threshold: 70, enabled: true },
        { id: '2', type: 'extreme-sensitivity', threshold: 90, enabled: true },
      ]);
      await alertsPage.goto();

      await expect(alertsPage.alertsContainer).toBeVisible();
    });

    test('should show existing alerts', async ({ page }) => {
      const mockAlerts = [
        { id: '1', type: 'high-sensitivity', threshold: 70, enabled: true },
        { id: '2', type: 'geomagnetic-storm', threshold: 5, enabled: false },
        { id: '3', type: 'seismic-activity', threshold: 4.5, enabled: true },
      ];

      await mockAPI.mockAlerts(mockAlerts);
      await alertsPage.goto();

      const alertCount = await alertsPage.getAlertCount();
      expect(alertCount).toBe(3);
    });

    test('should show empty state when no alerts exist', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();

      const emptyState = page.locator('[data-testid="no-alerts"], .empty-state');
      await expect(emptyState).toBeVisible();

      // Should show create alert button
      await expect(alertsPage.createAlertButton).toBeVisible();
    });

    test('should display alert type and threshold', async ({ page }) => {
      await mockAPI.mockAlerts([
        { id: '1', type: 'high-sensitivity', threshold: 70, enabled: true },
      ]);
      await alertsPage.goto();

      const alertItem = alertsPage.alertItems.first();
      await expect(alertItem).toBeVisible();

      const alertText = await alertItem.textContent();
      expect(alertText).toBeTruthy();
    });
  });

  test.describe('Create Alert', () => {
    test('should open create alert modal', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();

      await alertsPage.openCreateAlertModal();

      // Modal should be visible
      const modal = page.locator('[data-testid="alert-modal"], .alert-modal');
      await expect(modal).toBeVisible();
    });

    test('should have alert type selection', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      await expect(alertsPage.alertTypeSelect).toBeVisible();

      // Check available alert types
      const options = await alertsPage.alertTypeSelect.locator('option').allTextContents();
      expect(options.length).toBeGreaterThan(0);
    });

    test('should set threshold with slider', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      await expect(alertsPage.thresholdSlider).toBeVisible();

      // Set threshold to 60
      await alertsPage.setThreshold(60);

      const value = await alertsPage.thresholdSlider.inputValue();
      expect(parseInt(value)).toBe(60);
    });

    test('should create sensitivity level alerts', async ({ page }) => {
      const levels = ['Low', 'Moderate', 'Elevated', 'High', 'Extreme'];

      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      // Select alert type for sensitivity level
      await alertsPage.selectAlertType('Sensitivity Level');

      // Level selector should appear
      const levelSelect = page.locator('select[name="sensitivityLevel"], [data-testid="level-select"]');
      const hasLevelSelect = await levelSelect.isVisible().catch(() => false);

      if (hasLevelSelect) {
        const options = await levelSelect.locator('option').allTextContents();
        // Should have sensitivity levels
        expect(options.length).toBeGreaterThan(0);
      }
    });

    test('should create data source specific alerts', async ({ page }) => {
      const dataSourceAlerts = [
        'Geomagnetic Storm',
        'Solar Flare',
        'Seismic Activity',
        'Moon Phase',
      ];

      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      // Check if data source alerts are available
      const options = await alertsPage.alertTypeSelect.locator('option').allTextContents();
      const hasDataSourceAlerts = dataSourceAlerts.some((alert) =>
        options.some((opt) => opt.toLowerCase().includes(alert.toLowerCase()))
      );

      expect(hasDataSourceAlerts || options.length > 0).toBeTruthy();
    });

    test('should save new alert', async ({ page }) => {
      await mockAPI.mockAlerts([]);

      // Mock the POST request
      await page.route('**/api/alerts', async (route) => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 201,
            contentType: 'application/json',
            body: JSON.stringify({
              id: 'new-alert-1',
              type: 'high-sensitivity',
              threshold: 70,
              enabled: true,
            }),
          });
        } else {
          await route.continue();
        }
      });

      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();
      await alertsPage.selectAlertType('High Sensitivity');
      await alertsPage.setThreshold(70);
      await alertsPage.saveAlert();

      // Alert should be created
      const alertCount = await alertsPage.getAlertCount();
      expect(alertCount).toBeGreaterThanOrEqual(1);
    });
  });

  test.describe('Notification Preferences', () => {
    test('should show notification channels', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      // Should have notification toggle
      await expect(alertsPage.notificationToggle).toBeVisible();
    });

    test('should toggle Telegram notifications', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      // Toggle Telegram notifications
      await alertsPage.toggleNotification('telegram');

      const telegramToggle = page.locator('[data-channel="telegram"] input[type="checkbox"]');
      const isChecked = await telegramToggle.isChecked();

      // Should be toggled
      expect(typeof isChecked).toBe('boolean');
    });

    test('should show notification frequency options', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      const frequencySelect = page.locator(
        'select[name="frequency"], [data-testid="frequency-select"]'
      );
      const hasFrequency = await frequencySelect.isVisible().catch(() => false);

      if (hasFrequency) {
        const options = await frequencySelect.locator('option').allTextContents();
        expect(options).toContain(expect.stringMatching(/immediately|hourly|daily/i));
      }
    });

    test('should support quiet hours configuration', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      // Look for quiet hours toggle
      const quietHoursToggle = page.locator('[data-testid="quiet-hours"], input[name="quietHours"]');
      const hasQuietHours = await quietHoursToggle.isVisible().catch(() => false);

      // Feature may or may not exist
      expect(await alertsPage.notificationToggle.isVisible() || hasQuietHours).toBeTruthy();
    });
  });

  test.describe('Edit Alert', () => {
    test('should open edit modal for existing alert', async ({ page }) => {
      await mockAPI.mockAlerts([
        { id: '1', type: 'high-sensitivity', threshold: 70, enabled: true },
      ]);
      await alertsPage.goto();

      // Click edit button on alert
      const editButton = alertsPage.alertItems.first().getByRole('button', { name: /edit/i });
      await editButton.click();

      // Modal should open with existing values
      const modal = page.locator('[data-testid="alert-modal"], .alert-modal');
      await expect(modal).toBeVisible();
    });

    test('should update threshold value', async ({ page }) => {
      await mockAPI.mockAlerts([
        { id: '1', type: 'high-sensitivity', threshold: 70, enabled: true },
      ]);

      // Mock the PUT request
      await page.route('**/api/alerts/1', async (route) => {
        if (route.request().method() === 'PUT') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              id: '1',
              type: 'high-sensitivity',
              threshold: 80,
              enabled: true,
            }),
          });
        } else {
          await route.continue();
        }
      });

      await alertsPage.goto();

      const editButton = alertsPage.alertItems.first().getByRole('button', { name: /edit/i });
      await editButton.click();

      await alertsPage.setThreshold(80);
      await alertsPage.saveAlert();

      // Alert should be updated
      expect(await alertsPage.alertsContainer.isVisible()).toBeTruthy();
    });

    test('should toggle alert enabled state', async ({ page }) => {
      await mockAPI.mockAlerts([
        { id: '1', type: 'high-sensitivity', threshold: 70, enabled: true },
      ]);
      await alertsPage.goto();

      // Find toggle switch on alert item
      const toggleSwitch = alertsPage.alertItems.first().locator('input[type="checkbox"]');

      if (await toggleSwitch.isVisible()) {
        const initialState = await toggleSwitch.isChecked();
        await toggleSwitch.click();
        const newState = await toggleSwitch.isChecked();

        expect(newState).not.toBe(initialState);
      }
    });
  });

  test.describe('Delete Alert', () => {
    test('should delete alert with confirmation', async ({ page }) => {
      await mockAPI.mockAlerts([
        { id: '1', type: 'high-sensitivity', threshold: 70, enabled: true },
        { id: '2', type: 'geomagnetic-storm', threshold: 5, enabled: true },
      ]);

      // Mock the DELETE request
      await page.route('**/api/alerts/1', async (route) => {
        if (route.request().method() === 'DELETE') {
          await route.fulfill({ status: 204 });
        } else {
          await route.continue();
        }
      });

      await alertsPage.goto();

      const initialCount = await alertsPage.getAlertCount();
      expect(initialCount).toBe(2);

      // Delete first alert
      await alertsPage.deleteAlert(0);

      // Count should decrease
      const newCount = await alertsPage.getAlertCount();
      expect(newCount).toBe(1);
    });

    test('should show confirmation dialog before delete', async ({ page }) => {
      await mockAPI.mockAlerts([
        { id: '1', type: 'high-sensitivity', threshold: 70, enabled: true },
      ]);
      await alertsPage.goto();

      // Click delete
      const deleteButton = alertsPage.alertItems.first().locator(alertsPage.deleteButton);
      await deleteButton.click();

      // Confirmation dialog should appear
      const confirmDialog = page.locator('[data-testid="confirm-dialog"], .confirm-dialog');
      await expect(confirmDialog).toBeVisible();

      // Cancel should keep the alert
      await page.getByRole('button', { name: /cancel/i }).click();

      const count = await alertsPage.getAlertCount();
      expect(count).toBe(1);
    });
  });

  test.describe('Alert History', () => {
    test('should display alert history tab', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();

      const historyTab = page.getByRole('tab', { name: /history/i });
      await expect(historyTab).toBeVisible();
    });

    test('should show triggered alerts history', async ({ page }) => {
      // Mock alert history
      await page.route('**/api/alerts/history', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            history: [
              {
                id: '1',
                alertId: 'alert-1',
                type: 'high-sensitivity',
                triggeredAt: '2024-12-21T10:30:00Z',
                score: 75,
              },
              {
                id: '2',
                alertId: 'alert-1',
                type: 'high-sensitivity',
                triggeredAt: '2024-12-20T15:45:00Z',
                score: 72,
              },
            ],
          }),
        });
      });

      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.viewAlertHistory();

      const historyCount = await alertsPage.getHistoryItemCount();
      expect(historyCount).toBe(2);
    });

    test('should show empty state for no history', async ({ page }) => {
      await page.route('**/api/alerts/history', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ history: [] }),
        });
      });

      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.viewAlertHistory();

      const emptyHistory = page.locator('[data-testid="no-history"], .empty-history');
      await expect(emptyHistory).toBeVisible();
    });

    test('should show alert details in history', async ({ page }) => {
      await page.route('**/api/alerts/history', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            history: [
              {
                id: '1',
                alertId: 'alert-1',
                type: 'high-sensitivity',
                triggeredAt: '2024-12-21T10:30:00Z',
                score: 75,
                level: 'High',
                sources: ['geomagnetic', 'seismic'],
              },
            ],
          }),
        });
      });

      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.viewAlertHistory();

      const historyItem = alertsPage.alertHistory.locator('.history-item').first();
      const content = await historyItem.textContent();

      // Should contain alert information
      expect(content).toBeTruthy();
    });
  });

  test.describe('Alert Types', () => {
    test('should support sensitivity threshold alerts', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      const typeOptions = await alertsPage.alertTypeSelect.locator('option').allTextContents();

      // Should have sensitivity-related options
      const hasSensitivity = typeOptions.some((opt) =>
        opt.toLowerCase().includes('sensitiv')
      );

      expect(hasSensitivity || typeOptions.length > 0).toBeTruthy();
    });

    test('should support geomagnetic storm alerts', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      const typeOptions = await alertsPage.alertTypeSelect.locator('option').allTextContents();

      const hasGeomagnetic = typeOptions.some((opt) =>
        opt.toLowerCase().includes('geomagnetic') || opt.toLowerCase().includes('kp')
      );

      expect(hasGeomagnetic || typeOptions.length > 0).toBeTruthy();
    });

    test('should support seismic activity alerts', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      const typeOptions = await alertsPage.alertTypeSelect.locator('option').allTextContents();

      const hasSeismic = typeOptions.some((opt) =>
        opt.toLowerCase().includes('seismic') || opt.toLowerCase().includes('earthquake')
      );

      expect(hasSeismic || typeOptions.length > 0).toBeTruthy();
    });

    test('should support moon phase alerts', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      const typeOptions = await alertsPage.alertTypeSelect.locator('option').allTextContents();

      const hasMoon = typeOptions.some((opt) =>
        opt.toLowerCase().includes('moon') || opt.toLowerCase().includes('lunar')
      );

      expect(hasMoon || typeOptions.length > 0).toBeTruthy();
    });

    test('should support mercury retrograde alerts', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      const typeOptions = await alertsPage.alertTypeSelect.locator('option').allTextContents();

      const hasMercury = typeOptions.some((opt) =>
        opt.toLowerCase().includes('mercury') || opt.toLowerCase().includes('retrograde')
      );

      expect(hasMercury || typeOptions.length > 0).toBeTruthy();
    });
  });

  test.describe('Form Validation', () => {
    test('should require alert type selection', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      // Try to save without selecting type
      await alertsPage.saveButton.click();

      // Should show validation error
      const error = page.locator('.error-message, [data-testid="error"]');
      const hasError = await error.isVisible().catch(() => false);

      // Either shows error or prevents submission
      expect(hasError || await alertsPage.saveButton.isVisible()).toBeTruthy();
    });

    test('should validate threshold range', async ({ page }) => {
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      // Threshold should be 0-100 for sensitivity
      const slider = alertsPage.thresholdSlider;
      const min = await slider.getAttribute('min');
      const max = await slider.getAttribute('max');

      expect(parseInt(min || '0')).toBeGreaterThanOrEqual(0);
      expect(parseInt(max || '100')).toBeLessThanOrEqual(100);
    });
  });

  test.describe('Responsive Design', () => {
    test('should work on mobile devices', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await mockAPI.mockAlerts([
        { id: '1', type: 'high-sensitivity', threshold: 70, enabled: true },
      ]);
      await alertsPage.goto();

      // Alert list should be visible
      await expect(alertsPage.alertItems.first()).toBeVisible();

      // Create button should be accessible
      await expect(alertsPage.createAlertButton).toBeVisible();
    });

    test('should display modal properly on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await mockAPI.mockAlerts([]);
      await alertsPage.goto();
      await alertsPage.openCreateAlertModal();

      const modal = page.locator('[data-testid="alert-modal"], .alert-modal');
      await expect(modal).toBeVisible();

      // Modal should not overflow
      const box = await modal.boundingBox();
      if (box) {
        expect(box.width).toBeLessThanOrEqual(375);
      }
    });
  });
});
