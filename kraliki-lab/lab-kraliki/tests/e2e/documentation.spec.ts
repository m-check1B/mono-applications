import { test, expect } from '@playwright/test';

/**
 * Documentation Navigation E2E Tests
 *
 * Tests for navigating through Lab by Kraliki documentation.
 * Currently tests the landing page documentation links.
 * Will expand when dedicated docs site is available.
 */

test.describe('Documentation Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/sample-landing-page.html');
  });

  test('should have documentation link in footer', async ({ page }) => {
    const footer = page.locator('footer');
    const docsLink = footer.locator('a:has-text("Documentation")');

    await expect(docsLink).toBeVisible();
  });

  test('should have navigation links to main sections', async ({ page }) => {
    // Check for features link
    const featuresLink = page.locator('nav a[href="#features"]');
    await expect(featuresLink).toBeVisible();

    // Check for pricing link
    const pricingLink = page.locator('nav a[href="#pricing"]');
    await expect(pricingLink).toBeVisible();

    // Check for about link
    const aboutLink = page.locator('nav a[href="#about"]');
    await expect(aboutLink).toBeVisible();
  });

  test('should scroll to features section when clicked', async ({ page }) => {
    const featuresLink = page.locator('nav a[href="#features"]');
    await featuresLink.click();

    // Check that URL has #features
    await expect(page).toHaveURL(/#features/);

    // Features section should be in viewport
    const featuresSection = page.locator('.features, #features');
    await expect(featuresSection).toBeInViewport();
  });

  test('should have API documentation link in footer', async ({ page }) => {
    const footer = page.locator('footer');
    const apiLink = footer.locator('a:has-text("API")');

    await expect(apiLink).toBeVisible();
  });

  test('should have all footer resource links', async ({ page }) => {
    const resourcesSection = page.locator('.footer-links').filter({ hasText: 'Resources' });

    // Check for expected resource links
    const docLink = resourcesSection.locator('a:has-text("Documentation")');
    const apiLink = resourcesSection.locator('a:has-text("API")');
    const communityLink = resourcesSection.locator('a:has-text("Community")');

    await expect(docLink).toBeVisible();
    await expect(apiLink).toBeVisible();
    await expect(communityLink).toBeVisible();
  });
});

test.describe('In-Page Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/sample-landing-page.html');
  });

  test('should have sticky header for easy navigation', async ({ page }) => {
    const header = page.locator('header');

    // Scroll down
    await page.evaluate(() => window.scrollBy(0, 500));

    // Header should still be visible (sticky)
    await expect(header).toBeVisible();
    await expect(header).toBeInViewport();
  });

  test('should navigate between page sections smoothly', async ({ page }) => {
    // Click features link
    await page.click('nav a[href="#features"]');
    await page.waitForTimeout(300); // Allow for scroll animation

    const featuresSection = page.locator('.features');
    await expect(featuresSection).toBeInViewport();
  });

  test('should have all main content sections', async ({ page }) => {
    // Verify all major sections exist
    const sections = [
      { selector: 'header', name: 'Header' },
      { selector: '.hero', name: 'Hero' },
      { selector: '.features', name: 'Features' },
      { selector: '.social-proof', name: 'Social Proof' },
      { selector: '.cta-section', name: 'CTA' },
      { selector: 'footer', name: 'Footer' },
    ];

    for (const section of sections) {
      const element = page.locator(section.selector);
      await expect(element, `${section.name} section should exist`).toBeVisible();
    }
  });
});

test.describe('Documentation - Future Implementation', () => {
  // These tests are for when the full documentation site is built

  test.skip('should load documentation index page', async ({ page }) => {
    await page.goto('/docs/');

    const title = page.locator('h1');
    await expect(title).toContainText(/Lab by Kraliki|Documentation/);
  });

  test.skip('should have sidebar navigation in docs', async ({ page }) => {
    await page.goto('/docs/');

    const sidebar = page.locator('nav.sidebar, aside.sidebar, .docs-nav');
    await expect(sidebar).toBeVisible();
  });

  test.skip('should navigate to getting started guide', async ({ page }) => {
    await page.goto('/docs/');

    const gettingStartedLink = page.locator('a:has-text("Getting Started")');
    await gettingStartedLink.click();

    await expect(page).toHaveURL(/getting-started/);
  });

  test.skip('should have search functionality in docs', async ({ page }) => {
    await page.goto('/docs/');

    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]');
    await expect(searchInput).toBeVisible();

    await searchInput.fill('orchestration');

    // Search results should appear
    const searchResults = page.locator('.search-results, [role="listbox"]');
    await expect(searchResults).toBeVisible();
  });
});
