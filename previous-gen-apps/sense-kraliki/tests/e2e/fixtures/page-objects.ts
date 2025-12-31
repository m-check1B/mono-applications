import { Page, Locator } from '@playwright/test';

/**
 * Page Object for Landing Page
 * Encapsulates all landing page interactions and locators
 */
export class LandingPage {
  readonly page: Page;
  readonly heroTitle: Locator;
  readonly heroSubtitle: Locator;
  readonly ctaButton: Locator;
  readonly featureCards: Locator;
  readonly navLinks: Locator;
  readonly footer: Locator;
  readonly pricingSection: Locator;
  readonly testimonials: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heroTitle = page.getByRole('heading', { level: 1 });
    this.heroSubtitle = page.locator('.hero-subtitle, [data-testid="hero-subtitle"]');
    this.ctaButton = page.getByRole('button', { name: /get started|try now|start free/i });
    this.featureCards = page.locator('.feature-card, [data-testid="feature-card"]');
    this.navLinks = page.locator('nav a, header a');
    this.footer = page.locator('footer');
    this.pricingSection = page.locator('#pricing, [data-testid="pricing-section"]');
    this.testimonials = page.locator('.testimonial, [data-testid="testimonial"]');
  }

  async goto() {
    await this.page.goto('/');
  }

  async clickGetStarted() {
    await this.ctaButton.click();
  }

  async navigateTo(section: string) {
    await this.page.getByRole('link', { name: new RegExp(section, 'i') }).click();
  }

  async scrollToSection(section: string) {
    const sectionElement = this.page.locator(`#${section}, [data-section="${section}"]`);
    await sectionElement.scrollIntoViewIfNeeded();
  }

  async getFeatureCount(): Promise<number> {
    return await this.featureCards.count();
  }
}

/**
 * Page Object for Sensor Dashboard
 * Handles sensitivity score display, data sources, and charts
 */
export class SensorDashboard {
  readonly page: Page;
  readonly sensitivityScore: Locator;
  readonly scoreLevel: Locator;
  readonly dataSources: Locator;
  readonly refreshButton: Locator;
  readonly chartContainer: Locator;
  readonly dataSourceCards: Locator;
  readonly loadingSpinner: Locator;
  readonly lastUpdated: Locator;
  readonly trendIndicator: Locator;

  constructor(page: Page) {
    this.page = page;
    this.sensitivityScore = page.locator('[data-testid="sensitivity-score"], .sensitivity-score');
    this.scoreLevel = page.locator('[data-testid="score-level"], .score-level');
    this.dataSources = page.locator('[data-testid="data-sources"], .data-sources');
    this.refreshButton = page.getByRole('button', { name: /refresh|update/i });
    this.chartContainer = page.locator('[data-testid="chart-container"], .chart-container');
    this.dataSourceCards = page.locator('[data-testid="data-source-card"], .data-source-card');
    this.loadingSpinner = page.locator('[data-testid="loading"], .loading-spinner');
    this.lastUpdated = page.locator('[data-testid="last-updated"], .last-updated');
    this.trendIndicator = page.locator('[data-testid="trend"], .trend-indicator');
  }

  async goto() {
    await this.page.goto('/dashboard');
  }

  async waitForDataLoad() {
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 30000 }).catch(() => {});
    await this.sensitivityScore.waitFor({ state: 'visible', timeout: 30000 });
  }

  async refreshData() {
    await this.refreshButton.click();
    await this.waitForDataLoad();
  }

  async getScore(): Promise<string> {
    return await this.sensitivityScore.textContent() || '';
  }

  async getScoreLevel(): Promise<string> {
    return await this.scoreLevel.textContent() || '';
  }

  async getDataSourceCount(): Promise<number> {
    return await this.dataSourceCards.count();
  }

  async getDataSourceStatus(name: string): Promise<string> {
    const card = this.page.locator(`[data-source="${name}"], [data-testid="source-${name}"]`);
    return await card.getAttribute('data-status') || 'unknown';
  }

  async expandDataSource(name: string) {
    const card = this.page.locator(`[data-source="${name}"], [data-testid="source-${name}"]`);
    await card.click();
  }
}

/**
 * Page Object for Alerts Configuration
 * Manages alert thresholds, notification preferences, and alert history
 */
export class AlertsPage {
  readonly page: Page;
  readonly alertsContainer: Locator;
  readonly createAlertButton: Locator;
  readonly alertList: Locator;
  readonly alertItems: Locator;
  readonly thresholdSlider: Locator;
  readonly notificationToggle: Locator;
  readonly alertTypeSelect: Locator;
  readonly saveButton: Locator;
  readonly deleteButton: Locator;
  readonly alertHistory: Locator;

  constructor(page: Page) {
    this.page = page;
    this.alertsContainer = page.locator('[data-testid="alerts-container"], .alerts-container');
    this.createAlertButton = page.getByRole('button', { name: /create alert|add alert|new alert/i });
    this.alertList = page.locator('[data-testid="alert-list"], .alert-list');
    this.alertItems = page.locator('[data-testid="alert-item"], .alert-item');
    this.thresholdSlider = page.locator('input[type="range"], [data-testid="threshold-slider"]');
    this.notificationToggle = page.locator('[data-testid="notification-toggle"], .notification-toggle');
    this.alertTypeSelect = page.locator('select[name="alertType"], [data-testid="alert-type-select"]');
    this.saveButton = page.getByRole('button', { name: /save|confirm/i });
    this.deleteButton = page.getByRole('button', { name: /delete|remove/i });
    this.alertHistory = page.locator('[data-testid="alert-history"], .alert-history');
  }

  async goto() {
    await this.page.goto('/alerts');
  }

  async openCreateAlertModal() {
    await this.createAlertButton.click();
    await this.page.locator('[data-testid="alert-modal"], .alert-modal').waitFor({ state: 'visible' });
  }

  async setThreshold(value: number) {
    await this.thresholdSlider.fill(String(value));
  }

  async selectAlertType(type: string) {
    await this.alertTypeSelect.selectOption({ label: type });
  }

  async toggleNotification(channel: string) {
    const toggle = this.page.locator(`[data-channel="${channel}"] input[type="checkbox"]`);
    await toggle.click();
  }

  async saveAlert() {
    await this.saveButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async getAlertCount(): Promise<number> {
    return await this.alertItems.count();
  }

  async deleteAlert(index: number) {
    const item = this.alertItems.nth(index);
    await item.locator(this.deleteButton).click();
    await this.page.getByRole('button', { name: /confirm/i }).click();
  }

  async viewAlertHistory() {
    await this.page.getByRole('tab', { name: /history/i }).click();
    await this.alertHistory.waitFor({ state: 'visible' });
  }

  async getHistoryItemCount(): Promise<number> {
    return await this.alertHistory.locator('.history-item, [data-testid="history-item"]').count();
  }
}

/**
 * API Mock Helper for testing with mock data
 */
export class MockAPIHelper {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async mockSensitivityScore(score: number, level: string) {
    await this.page.route('**/api/sensitivity', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          score,
          level,
          timestamp: new Date().toISOString(),
          sources: {
            noaa_geomagnetic: { status: 'ok', value: 3.5, contribution: 15 },
            noaa_solar: { status: 'ok', value: 'C1.2', contribution: 10 },
            usgs_seismic: { status: 'ok', value: 4.2, contribution: 12 },
            schumann: { status: 'ok', value: 7.83, contribution: 8 },
            weather: { status: 'ok', value: { pressure: 1013, humidity: 65 }, contribution: 10 },
            astrology: { status: 'ok', value: { sun: 'Capricorn', moon: 'Pisces' }, contribution: 15 },
            moon_phase: { status: 'ok', value: 'Waxing Gibbous', contribution: 10 },
            mercury_retrograde: { status: 'ok', value: false, contribution: 0 },
            biorhythm: { status: 'ok', value: { physical: 75, emotional: 50, intellectual: 25 }, contribution: 20 },
          },
        }),
      });
    });
  }

  async mockAlerts(alerts: any[]) {
    await this.page.route('**/api/alerts', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ alerts }),
        });
      } else {
        await route.continue();
      }
    });
  }

  async mockDataSourceError(source: string) {
    await this.page.route(`**/api/sources/${source}`, async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: `Failed to fetch ${source} data` }),
      });
    });
  }
}
