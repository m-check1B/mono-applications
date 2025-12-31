import { test, expect } from './fixtures/test-helpers';
import { LandingPage } from './fixtures/page-objects';

/**
 * Landing Page E2E Tests for Sense by Kraliki
 *
 * NOTE: Sense by Kraliki is currently a Telegram bot without a web UI.
 * Tests will skip gracefully when no web server is available.
 *
 * Tests cover:
 * - Homepage loading and content
 * - Navigation functionality
 * - Call-to-action buttons
 * - Responsive design
 * - Feature showcase
 * - Pricing section
 */

test.describe('Landing Page', () => {
  let landingPage: LandingPage;

  test.beforeEach(async ({ page }) => {
    landingPage = new LandingPage(page);
    await landingPage.goto();
  });

  test.describe('Homepage Content', () => {
    test('should display hero section with title and CTA', async ({ page }) => {
      // Verify hero title is visible
      await expect(landingPage.heroTitle).toBeVisible();
      const titleText = await landingPage.heroTitle.textContent();
      expect(titleText).toBeTruthy();

      // Verify CTA button is visible and clickable
      await expect(landingPage.ctaButton).toBeVisible();
      await expect(landingPage.ctaButton).toBeEnabled();
    });

    test('should have proper page title and meta description', async ({ page }) => {
      const title = await page.title();
      expect(title).toContain('Sense by Kraliki');

      // Check meta description
      const metaDescription = await page.locator('meta[name="description"]').getAttribute('content');
      expect(metaDescription).toBeTruthy();
    });

    test('should display all data source features', async () => {
      // Sense by Kraliki has 9 data sources
      const expectedDataSources = [
        'NOAA Geomagnetic',
        'NOAA Solar',
        'USGS Seismic',
        'Schumann Resonance',
        'Weather',
        'Astrology',
        'Moon Phase',
        'Mercury Retrograde',
        'Biorhythm',
      ];

      const featureCount = await landingPage.getFeatureCount();
      expect(featureCount).toBeGreaterThan(0);

      // Verify at least some data sources are mentioned
      const pageContent = await landingPage.page.content();
      let foundSources = 0;
      for (const source of expectedDataSources) {
        if (pageContent.toLowerCase().includes(source.toLowerCase())) {
          foundSources++;
        }
      }
      expect(foundSources).toBeGreaterThan(0);
    });

    test('should have sensitivity level indicators', async ({ page }) => {
      // Check for sensitivity levels: Low, Moderate, Elevated, High, Extreme
      const pageContent = await page.content();
      const levels = ['low', 'moderate', 'elevated', 'high', 'extreme'];

      let foundLevels = 0;
      for (const level of levels) {
        if (pageContent.toLowerCase().includes(level)) {
          foundLevels++;
        }
      }
      // At least some levels should be mentioned
      expect(foundLevels).toBeGreaterThan(0);
    });
  });

  test.describe('Navigation', () => {
    test('should have working navigation links', async ({ page }) => {
      const navLinks = await landingPage.navLinks.all();
      expect(navLinks.length).toBeGreaterThan(0);

      // Check each nav link is visible
      for (const link of navLinks) {
        await expect(link).toBeVisible();
      }
    });

    test('should navigate to features section', async ({ page }) => {
      await landingPage.scrollToSection('features');

      // Verify scroll position changed
      const scrollY = await page.evaluate(() => window.scrollY);
      expect(scrollY).toBeGreaterThan(0);
    });

    test('should navigate to pricing section', async ({ page }) => {
      await landingPage.scrollToSection('pricing');

      // Verify pricing section is in view
      await expect(landingPage.pricingSection).toBeInViewport();
    });

    test('should show mobile menu on small screens', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Look for hamburger menu
      const menuButton = page.locator('[data-testid="mobile-menu"], .hamburger, button[aria-label*="menu"]');

      // Mobile menu should exist on small screens
      const menuExists = await menuButton.isVisible().catch(() => false);

      if (menuExists) {
        await menuButton.click();
        // Menu should expand
        const mobileNav = page.locator('[data-testid="mobile-nav"], .mobile-nav');
        await expect(mobileNav).toBeVisible();
      }
    });
  });

  test.describe('Call-to-Action', () => {
    test('should navigate to signup when clicking Get Started', async ({ page }) => {
      await landingPage.clickGetStarted();

      // Should navigate to signup or onboarding
      await page.waitForURL(/\/(signup|register|onboarding|dashboard)/);
    });

    test('should have working Telegram bot link', async ({ page }) => {
      const telegramLink = page.getByRole('link', { name: /telegram/i });

      if (await telegramLink.isVisible()) {
        const href = await telegramLink.getAttribute('href');
        expect(href).toContain('t.me');
      }
    });

    test('should display subscription plans in pricing section', async ({ page }) => {
      await landingPage.scrollToSection('pricing');

      // Look for Sensitive and Empath plans mentioned in the app
      const pricingContent = await landingPage.pricingSection.textContent();

      // Should mention at least one pricing plan
      const hasPricing = pricingContent?.toLowerCase().includes('sensitive') ||
                         pricingContent?.toLowerCase().includes('empath') ||
                         pricingContent?.toLowerCase().includes('premium');

      expect(hasPricing || (await landingPage.pricingSection.isVisible())).toBeTruthy();
    });
  });

  test.describe('Responsive Design', () => {
    const viewports = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1440, height: 900 },
    ];

    for (const viewport of viewports) {
      test(`should render correctly on ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await landingPage.goto();

        // Hero should be visible on all viewports
        await expect(landingPage.heroTitle).toBeVisible();
        await expect(landingPage.ctaButton).toBeVisible();

        // No horizontal scroll
        const hasHorizontalScroll = await page.evaluate(() => {
          return document.documentElement.scrollWidth > document.documentElement.clientWidth;
        });
        expect(hasHorizontalScroll).toBeFalsy();
      });
    }
  });

  test.describe('Footer', () => {
    test('should display footer with legal links', async ({ page }) => {
      await expect(landingPage.footer).toBeVisible();

      // Check for privacy policy and terms
      const footerText = await landingPage.footer.textContent();
      const hasLegalContent = footerText?.toLowerCase().includes('privacy') ||
                              footerText?.toLowerCase().includes('terms') ||
                              footerText?.toLowerCase().includes('verduona');

      expect(hasLegalContent).toBeTruthy();
    });

    test('should display copyright notice', async ({ page }) => {
      const footerText = await landingPage.footer.textContent();
      expect(footerText).toMatch(/\d{4}|copyright|verduona/i);
    });
  });

  test.describe('Performance', () => {
    test('should load within acceptable time', async ({ page }) => {
      const startTime = Date.now();
      await landingPage.goto();
      await page.waitForLoadState('domcontentloaded');
      const loadTime = Date.now() - startTime;

      // Page should load in under 3 seconds
      expect(loadTime).toBeLessThan(3000);
    });

    test('should have no console errors', async ({ page }) => {
      const errors: string[] = [];
      page.on('console', (msg) => {
        if (msg.type() === 'error') {
          errors.push(msg.text());
        }
      });

      await landingPage.goto();
      await page.waitForLoadState('networkidle');

      // Filter out expected third-party errors
      const criticalErrors = errors.filter(
        (e) => !e.includes('favicon') && !e.includes('third-party')
      );

      expect(criticalErrors.length).toBe(0);
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper heading hierarchy', async ({ page }) => {
      const h1Count = await page.locator('h1').count();
      expect(h1Count).toBe(1);

      // H2 should come after H1
      const headings = await page.locator('h1, h2, h3').allTextContents();
      expect(headings.length).toBeGreaterThan(0);
    });

    test('should have alt text on images', async ({ page }) => {
      const images = await page.locator('img').all();

      for (const img of images) {
        const alt = await img.getAttribute('alt');
        const src = await img.getAttribute('src');

        // Decorative images can have empty alt, but should have alt attribute
        if (src && !src.includes('svg')) {
          expect(alt).toBeDefined();
        }
      }
    });

    test('should be keyboard navigable', async ({ page }) => {
      await page.keyboard.press('Tab');
      const activeElement = page.locator(':focus');
      await expect(activeElement).toBeVisible();

      // Should be able to tab through interactive elements
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
    });
  });
});
