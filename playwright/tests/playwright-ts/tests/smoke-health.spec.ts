import { test, expect } from '@playwright/test';

/**
 * Smoke Health Tests — Post-deploy validation suite.
 *
 * Lightweight Playwright tests designed to run against a live deployment URL
 * after a deploy. Used by the deploy-validate-rollback pipeline to determine
 * whether a deployment is healthy enough to promote.
 *
 * The deployment URL is passed via BASE_URL environment variable
 * (picked up by Playwright's baseURL config).
 *
 * Tags: @smoke @health
 */

test.describe('Post-Deploy Smoke Health @smoke @health', () => {
  test('@smoke @health homepage returns 200 and has title', async ({ page }) => {
    const response = await page.goto('/', { waitUntil: 'domcontentloaded' });

    expect(response?.status()).toBeLessThan(400);

    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
  });

  test('@smoke @health no critical JavaScript errors on load', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));

    await page.goto('/', { waitUntil: 'networkidle' });

    expect(errors).toEqual([]);
  });

  test('@smoke @health key page elements render', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' });

    // At minimum the page should have a body with visible content
    const bodyVisible = await page.locator('body').isVisible();
    expect(bodyVisible).toBe(true);

    // Check that the page has some interactive elements
    const interactiveCount = await page.locator('a, button, input, select').count();
    expect(interactiveCount).toBeGreaterThan(0);
  });

  test('@smoke @health page loads within performance budget', async ({ page }) => {
    const start = Date.now();
    await page.goto('/', { waitUntil: 'load' });
    const loadTime = Date.now() - start;

    // 10 second budget — generous for CI environments
    expect(loadTime).toBeLessThan(10_000);
  });

  test('@smoke @health no broken images on homepage', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle' });

    const images = page.locator('img[src]');
    const count = await images.count();

    for (let i = 0; i < count; i++) {
      const naturalWidth = await images.nth(i).evaluate(
        (img: HTMLImageElement) => img.naturalWidth,
      );
      const src = await images.nth(i).getAttribute('src');
      expect(naturalWidth, `Broken image: ${src}`).toBeGreaterThan(0);
    }
  });
});
