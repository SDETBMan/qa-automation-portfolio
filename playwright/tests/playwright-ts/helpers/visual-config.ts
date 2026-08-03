import { PageScreenshotOptions } from '@playwright/test';
import path from 'path';

/**
 * Shared visual regression configuration.
 *
 * Centralises threshold values, mask selectors, and style overrides so that
 * every `toHaveScreenshot()` call uses consistent settings.  Individual tests
 * can override any property by spreading the result of `visualOptions()`.
 */

/** Absolute path to the CSS file that freezes animations during capture. */
export const FREEZE_ANIMATIONS_CSS = path.join(__dirname, 'freeze-animations.css');

/** Default comparison thresholds. */
export const DEFAULT_THRESHOLD = 0.2;          // Per-pixel colour sensitivity (0–1)
export const DEFAULT_MAX_DIFF_PIXEL_RATIO = 0.01; // 1 % overall pixel tolerance

/**
 * Selectors whose content changes between runs (timestamps, badges, session
 * IDs, etc.).  These are masked (blacked-out) in screenshots to reduce flaky
 * diffs that don't represent real regressions.
 */
export const DYNAMIC_SELECTORS = [
  '.shopping_cart_badge',   // SauceDemo cart count — varies per test
  '[data-test="error"]',    // Error banners — presence varies
];

/**
 * Build the options object accepted by `expect(page).toHaveScreenshot()`.
 *
 * Usage:
 *   await expect(page).toHaveScreenshot('login.png', visualOptions());
 *   await expect(page).toHaveScreenshot('cart.png', visualOptions({
 *     maxDiffPixelRatio: 0.02,            // relax tolerance for this shot
 *     mask: [page.locator('.promo-banner')], // mask an extra dynamic element
 *   }));
 */
export function visualOptions(
  overrides: {
    threshold?: number;
    maxDiffPixelRatio?: number;
    mask?: import('@playwright/test').Locator[];
    fullPage?: boolean;
    animations?: 'disabled' | 'allow';
  } = {},
) {
  return {
    threshold: overrides.threshold ?? DEFAULT_THRESHOLD,
    maxDiffPixelRatio: overrides.maxDiffPixelRatio ?? DEFAULT_MAX_DIFF_PIXEL_RATIO,
    animations: overrides.animations ?? ('disabled' as const),
    stylePath: FREEZE_ANIMATIONS_CSS,
    fullPage: overrides.fullPage ?? true,
    ...(overrides.mask && { mask: overrides.mask }),
  };
}

/**
 * Build mask locators for the common dynamic selectors on a given page.
 *
 * Usage:
 *   await expect(page).toHaveScreenshot('page.png', {
 *     ...visualOptions(),
 *     mask: dynamicMasks(page),
 *   });
 */
export function dynamicMasks(page: import('@playwright/test').Page) {
  return DYNAMIC_SELECTORS.map((sel) => page.locator(sel));
}
