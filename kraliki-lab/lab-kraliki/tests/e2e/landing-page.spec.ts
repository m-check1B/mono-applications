import { test, expect } from '@playwright/test';

/**
 * Landing Page E2E Tests
 *
 * Tests the Lab by Kraliki landing page for:
 * - Page load and basic rendering
 * - Hero section content
 * - Navigation elements
 * - CTA buttons
 * - Responsive design
 */

test.describe('Landing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/sample-landing-page.html');
  });

  test('should load the landing page successfully', async ({ page }) => {
    // Verify page title
    await expect(page).toHaveTitle(/Acme|Lab by Kraliki/);

    // Verify the page has loaded with main content
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });

  test('should display hero section with headline', async ({ page }) => {
    // Check for hero section
    const hero = page.locator('.hero');
    await expect(hero).toBeVisible();

    // Verify headline is present
    const headline = hero.locator('h1');
    await expect(headline).toBeVisible();
    await expect(headline).not.toBeEmpty();
  });

  test('should display navigation with logo and links', async ({ page }) => {
    // Check for navigation
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();

    // Verify logo
    const logo = page.locator('.logo');
    await expect(logo).toBeVisible();

    // Verify navigation links exist
    const navLinks = page.locator('.nav-links a');
    await expect(navLinks).toHaveCount(3); // Features, Pricing, About
  });

  test('should display CTA buttons in hero section', async ({ page }) => {
    const heroCTAs = page.locator('.hero-ctas .btn');
    await expect(heroCTAs).toHaveCount(2);

    // Verify primary CTA
    const primaryCTA = page.locator('.hero-ctas .btn-primary');
    await expect(primaryCTA).toBeVisible();
    await expect(primaryCTA).toHaveText(/Start Free Trial|See It In Action|Book a Demo/i);
  });

  test('should display features section with feature cards', async ({ page }) => {
    const featuresSection = page.locator('.features');
    await expect(featuresSection).toBeVisible();

    // Verify features headline
    const featuresHeadline = featuresSection.locator('h2');
    await expect(featuresHeadline).toBeVisible();

    // Verify feature cards
    const featureCards = page.locator('.feature-card');
    await expect(featureCards).toHaveCount(3);
  });

  test('should display social proof section with stats', async ({ page }) => {
    const socialProof = page.locator('.social-proof');
    await expect(socialProof).toBeVisible();

    // Verify stats are present
    const stats = page.locator('.stat-item');
    await expect(stats).toHaveCount(3);

    // Verify testimonial
    const testimonial = page.locator('.testimonial');
    await expect(testimonial).toBeVisible();
  });

  test('should display footer with navigation links', async ({ page }) => {
    const footer = page.locator('footer');
    await expect(footer).toBeVisible();

    // Verify footer has link sections
    const footerLinks = page.locator('.footer-links');
    await expect(footerLinks).toHaveCount(4);
  });

  test('should have proper heading hierarchy for accessibility', async ({ page }) => {
    // Check that h1 exists and is the main headline
    const h1 = page.locator('h1');
    await expect(h1).toHaveCount(1);

    // Check for h2 section headings
    const h2s = page.locator('h2');
    const h2Count = await h2s.count();
    expect(h2Count).toBeGreaterThanOrEqual(2);
  });

  test('should have meta description for SEO', async ({ page }) => {
    const metaDescription = page.locator('meta[name="description"]');
    await expect(metaDescription).toHaveAttribute('content', /.+/);
  });
});

test.describe('Landing Page - Responsive Design', () => {
  test('should be responsive on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/sample-landing-page.html');

    // Page should still be functional
    const hero = page.locator('.hero');
    await expect(hero).toBeVisible();

    const headline = page.locator('.hero h1');
    await expect(headline).toBeVisible();
  });

  test('should be responsive on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/sample-landing-page.html');

    const hero = page.locator('.hero');
    await expect(hero).toBeVisible();

    const features = page.locator('.features');
    await expect(features).toBeVisible();
  });
});
