#!/usr/bin/env npx ts-node

/**
 * Post-deploy health check script.
 *
 * Validates a deployment URL by running a battery of checks:
 *   1. HTTP 200 on the root path
 *   2. HTTP 200 on key routes (configurable)
 *   3. Page title is present (not blank)
 *   4. No critical console errors on the homepage
 *
 * Usage:
 *   npx ts-node scripts/health-check.ts https://www.saucedemo.com
 *   npx ts-node scripts/health-check.ts https://my-app.vercel.app
 *
 * Exit codes:
 *   0 — all checks passed
 *   1 — one or more checks failed
 *
 * Outputs JSON to stdout for audit trail consumption in CI.
 */

import { chromium, Browser } from 'playwright';

interface CheckResult {
  name: string;
  passed: boolean;
  detail: string;
}

interface HealthReport {
  url: string;
  timestamp: string;
  passed: boolean;
  checks: CheckResult[];
  duration_ms: number;
}

// ── Configuration ────────────────────────────────────────────────────────────

/** Routes to check for HTTP 200 (relative to the deployment URL).
 *  Override with HEALTH_CHECK_ROUTES env var (comma-separated), e.g.:
 *    HEALTH_CHECK_ROUTES=/,/collections/all npx ts-node scripts/health-check.ts <URL>
 */
const ROUTES_TO_CHECK = process.env['HEALTH_CHECK_ROUTES']
  ? process.env['HEALTH_CHECK_ROUTES'].split(',').map((r) => r.trim())
  : ['/'];

/** Console message levels treated as critical errors. */
const CRITICAL_CONSOLE_LEVELS = ['error'];

// ── Main ─────────────────────────────────────────────────────────────────────

async function main(): Promise<void> {
  const deploymentUrl = process.argv[2];

  if (!deploymentUrl) {
    console.error('Usage: npx ts-node scripts/health-check.ts <DEPLOYMENT_URL>');
    process.exit(1);
  }

  const start = Date.now();
  const checks: CheckResult[] = [];
  let browser: Browser | undefined;

  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();

    // ── Check 1: HTTP status on key routes ─────────────────────────────────
    for (const route of ROUTES_TO_CHECK) {
      const url = new URL(route, deploymentUrl).toString();
      try {
        const response = await page.goto(url, {
          waitUntil: 'domcontentloaded',
          timeout: 30_000,
        });
        const status = response?.status() ?? 0;
        checks.push({
          name: `HTTP status ${route}`,
          passed: status >= 200 && status < 400,
          detail: `${status} ${response?.statusText() ?? 'no response'}`,
        });
      } catch (err) {
        checks.push({
          name: `HTTP status ${route}`,
          passed: false,
          detail: `Navigation error: ${(err as Error).message}`,
        });
      }
    }

    // ── Check 2: Page title is present ─────────────────────────────────────
    try {
      await page.goto(deploymentUrl, { waitUntil: 'domcontentloaded', timeout: 30_000 });
      const title = await page.title();
      checks.push({
        name: 'Page title present',
        passed: title.trim().length > 0,
        detail: title || '(empty)',
      });
    } catch (err) {
      checks.push({
        name: 'Page title present',
        passed: false,
        detail: `Error: ${(err as Error).message}`,
      });
    }

    // ── Check 3: No critical console errors ────────────────────────────────
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (CRITICAL_CONSOLE_LEVELS.includes(msg.type())) {
        consoleErrors.push(`[${msg.type()}] ${msg.text()}`);
      }
    });

    try {
      await page.goto(deploymentUrl, { waitUntil: 'networkidle', timeout: 30_000 });
      // Give the page a moment to settle
      await page.waitForTimeout(2_000);
      checks.push({
        name: 'No critical console errors',
        passed: consoleErrors.length === 0,
        detail: consoleErrors.length === 0
          ? 'Clean console'
          : `${consoleErrors.length} error(s): ${consoleErrors.slice(0, 3).join('; ')}`,
      });
    } catch (err) {
      checks.push({
        name: 'No critical console errors',
        passed: false,
        detail: `Error during console check: ${(err as Error).message}`,
      });
    }
  } finally {
    if (browser) {
      await browser.close();
    }
  }

  // ── Report ───────────────────────────────────────────────────────────────
  const allPassed = checks.every((c) => c.passed);
  const report: HealthReport = {
    url: deploymentUrl,
    timestamp: new Date().toISOString(),
    passed: allPassed,
    checks,
    duration_ms: Date.now() - start,
  };

  console.log(JSON.stringify(report, null, 2));
  process.exit(allPassed ? 0 : 1);
}

main().catch((err) => {
  console.error('Health check script failed:', err);
  process.exit(1);
});
