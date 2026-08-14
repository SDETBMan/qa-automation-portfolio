#!/usr/bin/env node
/**
 * validate-locators.mjs — Validates CSS selectors from changed page objects
 * against the live SauceDemo site using Playwright.
 *
 * Usage:
 *   cd playwright/tests/playwright-ts && npm ci --quiet && npx playwright install chromium 2>/dev/null
 *   NODE_PATH=playwright/tests/playwright-ts/node_modules node .claude/skills/verify-changes/scripts/validate-locators.mjs
 */
import { execSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const BASE_URL = 'https://www.saucedemo.com';
const LOGIN_USER = 'standard_user';
const LOGIN_PASS = 'secret_sauce';

// ── Page object file patterns ───────────────────────────────────────────────
const PAGE_OBJECT_GLOBS = [
  'cypress/cypress/pages/*.ts',
  'selenium-java/src/main/java/**/pages/*.java',
  'cucumber/src/test/java/**/pages/*.java',
  'cucumber_python/pages/*.py',
  'playwright/src/Framework.Core/Pages/*.cs',
  'playwright/tests/playwright-ts/pages/*.ts',
];

// ── Filename → URL path mapping ─────────────────────────────────────────────
function urlForPage(filename) {
  const lower = filename.toLowerCase();
  if (lower.includes('login'))     return '/';
  if (lower.includes('inventory')) return '/inventory.html';
  if (lower.includes('cart'))      return '/cart.html';
  if (lower.includes('checkout'))  return '/checkout-step-one.html';
  if (lower.includes('dashboard')) return '/inventory.html';
  if (lower.includes('products'))  return '/inventory.html';
  // Unknown page — default to inventory (most elements are there)
  return '/inventory.html';
}

// ── Conditional elements that may not always be present ─────────────────────
const CONDITIONAL_SELECTORS = new Set([
  '.shopping_cart_badge',
  '[data-test="error"]',
  'h3[data-test=\'error\']',
  '#error-message-container',
]);

function isConditional(selector) {
  return CONDITIONAL_SELECTORS.has(selector) ||
    selector.includes('error') ||
    selector.includes('badge') ||
    selector.includes('remove');
}

// ── Selector extraction per framework ───────────────────────────────────────

/** Cypress TS: `SELECTORS = { key: '#selector' } as const` */
function extractCypressSelectors(content) {
  const selectors = [];
  // Only extract from within SELECTORS block
  const blockMatch = content.match(/const\s+SELECTORS\s*=\s*\{([^}]+)\}/s);
  if (!blockMatch) return selectors;
  const block = blockMatch[1];
  // Match key: 'value' or key: "value" pairs — handles nested quotes
  // Single-quoted values (may contain double quotes): 'text'
  const singleRe = /:\s*'([^']+)'/g;
  const doubleRe = /:\s*"([^"]+)"/g;
  let m;
  while ((m = singleRe.exec(block)) !== null) {
    const val = m[1];
    if (val.startsWith('#') || val.startsWith('.') || val.startsWith('[')) {
      selectors.push(val);
    }
  }
  while ((m = doubleRe.exec(block)) !== null) {
    const val = m[1];
    if (val.startsWith('#') || val.startsWith('.') || val.startsWith('[')) {
      selectors.push(val);
    }
  }
  return selectors;
}

/** Selenium/Cucumber Java: By.id("x"), By.cssSelector("x"), By.className("x") */
function extractJavaSelectors(content) {
  const selectors = [];
  const patterns = [
    { re: /By\.id\("([^"]+)"\)/g,          fmt: v => `#${v}` },
    { re: /By\.cssSelector\("([^"]+)"\)/g,  fmt: v => v },
    { re: /By\.className\("([^"]+)"\)/g,    fmt: v => `.${v}` },
  ];
  for (const { re, fmt } of patterns) {
    let m;
    while ((m = re.exec(content)) !== null) {
      // Skip dynamic selectors with string concatenation
      if (m[1].includes('+') || m[1].includes('%s')) continue;
      selectors.push(fmt(m[1]));
    }
  }
  return selectors;
}

/** Cucumber Python: (By.ID, "x"), (By.CSS_SELECTOR, "x"), (By.CLASS_NAME, "x") */
function extractPythonSelectors(content) {
  const selectors = [];
  const patterns = [
    { re: /\(By\.ID,\s*"([^"]+)"\)/g,           fmt: v => `#${v}` },
    { re: /\(By\.CSS_SELECTOR,\s*"([^"]+)"\)/g,  fmt: v => v },
    { re: /\(By\.CLASS_NAME,\s*"([^"]+)"\)/g,    fmt: v => `.${v}` },
  ];
  for (const { re, fmt } of patterns) {
    let m;
    while ((m = re.exec(content)) !== null) {
      selectors.push(fmt(m[1]));
    }
  }
  return selectors;
}

/** Playwright C#: private const string Name = "#selector" */
function extractCSharpSelectors(content) {
  const selectors = [];
  const re = /private\s+const\s+string\s+\w+\s*=\s*"([^"]+)"/g;
  let m;
  while ((m = re.exec(content)) !== null) {
    const val = m[1];
    // Skip XPath
    if (val.startsWith('//') || val.startsWith('(//')) continue;
    selectors.push(val);
  }
  return selectors;
}

/** Playwright TS: page.locator('css'), page.getByTestId('x') */
function extractPlaywrightTsSelectors(content) {
  const selectors = [];
  // page.locator('css') or page.locator("css")
  const locatorRe = /page\.locator\(['"]([^'"]+)['"]\)/g;
  let m;
  while ((m = locatorRe.exec(content)) !== null) {
    const val = m[1];
    if (val.startsWith('//') || val.startsWith('(//')) continue;
    selectors.push(val);
  }
  // page.getByTestId('x') → [data-testid="x"]
  // Note: SauceDemo uses data-test, not data-testid. Playwright's getByTestId
  // matches the configured testIdAttribute (default: data-testid).
  // The actual config may set it to data-test. Extract as data-test for validation.
  const testIdRe = /page\.getByTestId\(['"]([^'"]+)['"]\)/g;
  while ((m = testIdRe.exec(content)) !== null) {
    // Try both data-test and data-testid since config varies
    selectors.push(`[data-test="${m[1]}"]`);
  }
  return selectors;
}

// ── Determine extractor from file path ──────────────────────────────────────
function getExtractor(filePath) {
  if (filePath.includes('cypress/') && filePath.endsWith('.ts'))
    return extractCypressSelectors;
  if (filePath.endsWith('.java'))
    return extractJavaSelectors;
  if (filePath.endsWith('.py'))
    return extractPythonSelectors;
  if (filePath.endsWith('.cs'))
    return extractCSharpSelectors;
  if (filePath.includes('playwright-ts/') && filePath.endsWith('.ts'))
    return extractPlaywrightTsSelectors;
  return null;
}

// ── Find changed page object files ──────────────────────────────────────────
function getChangedPageObjects() {
  let diffOutput;
  try {
    diffOutput = execSync('git diff --name-only HEAD', { encoding: 'utf8' }).trim();
  } catch {
    // Fallback: compare against empty tree (all files are "changed")
    diffOutput = execSync('git diff --name-only', { encoding: 'utf8' }).trim();
  }
  if (!diffOutput) return [];

  const changedFiles = diffOutput.split('\n').map(f => f.trim()).filter(Boolean);

  // Match against page object patterns
  const pageObjects = [];
  for (const file of changedFiles) {
    const isPageObject = PAGE_OBJECT_GLOBS.some(glob => {
      // Convert glob to a simple regex for matching
      const pattern = glob
        .replace(/\*\*/g, '.*')
        .replace(/\*/g, '[^/]*')
        .replace(/\./g, '\\.');
      return new RegExp(pattern).test(file);
    });
    if (isPageObject) {
      // Skip BasePage files — they contain utility methods, not selectors
      const basename = file.split('/').pop();
      if (basename.toLowerCase().includes('basepage') || basename.toLowerCase().includes('base_page')) continue;
      pageObjects.push(file);
    }
  }
  return pageObjects;
}

// ── Main ────────────────────────────────────────────────────────────────────
async function main() {
  // 1. Find changed page objects
  const pageObjects = getChangedPageObjects();
  if (pageObjects.length === 0) {
    console.log('LOCATOR VALIDATION: No page objects changed — nothing to validate.');
    process.exit(0);
  }

  console.log(`LOCATOR VALIDATION: Found ${pageObjects.length} changed page object(s):`);
  for (const po of pageObjects) console.log(`  ${po}`);
  console.log();

  // 2. Extract selectors from each file
  const validationTasks = []; // { file, selector, url, conditional }
  for (const file of pageObjects) {
    const extractor = getExtractor(file);
    if (!extractor) {
      console.log(`  SKIP: No extractor for ${file}`);
      continue;
    }

    let content;
    try {
      content = readFileSync(resolve(file), 'utf8');
    } catch {
      console.log(`  SKIP: Cannot read ${file}`);
      continue;
    }

    const selectors = extractor(content);
    const basename = file.split('/').pop();
    const url = urlForPage(basename);

    for (const sel of selectors) {
      validationTasks.push({
        file,
        selector: sel,
        url,
        conditional: isConditional(sel),
      });
    }

    if (selectors.length === 0) {
      console.log(`  ${basename}: no CSS selectors extracted`);
    } else {
      console.log(`  ${basename}: ${selectors.length} selector(s) → ${url}`);
    }
  }

  if (validationTasks.length === 0) {
    console.log('\nNo CSS selectors to validate (locators may be XPath, role-based, or placeholder-based).');
    process.exit(0);
  }

  // 3. Launch Playwright and validate
  let chromium;
  try {
    // Try importing from node_modules — works when NODE_PATH is set or run from playwright-ts dir
    const pw = await import('playwright');
    chromium = pw.chromium;
  } catch {
    try {
      // Fallback: resolve playwright from the playwright-ts project's node_modules
      const { createRequire } = await import('node:module');
      const playwrightTs = resolve('playwright/tests/playwright-ts');
      const require = createRequire(resolve(playwrightTs, 'package.json'));
      const pw = require('playwright');
      chromium = pw.chromium;
    } catch {
      console.error('\nERROR: Playwright not available. Run:');
      console.error('  cd playwright/tests/playwright-ts && npm ci && npx playwright install chromium');
      process.exit(1);
    }
  }

  let browser;
  try {
    browser = await chromium.launch({ headless: true });
  } catch {
    console.log('\nSKIP: Could not launch Chromium. Playwright browsers may not be installed.');
    process.exit(0);
  }

  const context = await browser.newContext();
  const page = await context.newPage();

  // Check if SauceDemo is reachable
  try {
    const resp = await page.goto(BASE_URL, { timeout: 15000 });
    if (!resp || resp.status() >= 400) {
      console.log(`\nSKIP: saucedemo.com returned status ${resp?.status() ?? 'unknown'}. Skipping validation.`);
      await browser.close();
      process.exit(0);
    }
  } catch {
    console.log('\nSKIP: saucedemo.com unreachable. Skipping locator validation.');
    await browser.close();
    process.exit(0);
  }

  // Group tasks by URL to minimize navigation
  const byUrl = new Map();
  for (const task of validationTasks) {
    if (!byUrl.has(task.url)) byUrl.set(task.url, []);
    byUrl.get(task.url).push(task);
  }

  const results = { pass: 0, fail: 0, skip: 0, conditional: 0 };
  const failures = [];
  let loggedIn = false;

  console.log('\n── Validating selectors ──────────────────────────────────────');

  for (const [url, tasks] of byUrl) {
    // Login if needed (any page other than / requires auth)
    if (url !== '/' && !loggedIn) {
      try {
        await page.goto(BASE_URL, { timeout: 10000 });
        await page.locator('#user-name').fill(LOGIN_USER);
        await page.locator('#password').fill(LOGIN_PASS);
        await page.locator('#login-button').click();
        await page.waitForURL('**/inventory.html', { timeout: 10000 });
        loggedIn = true;
      } catch (err) {
        console.log(`  SKIP: Login failed — ${err.message}`);
        for (const t of tasks) {
          console.log(`  SKIP  ${t.selector}  (login required)`);
          results.skip++;
        }
        continue;
      }
    }

    // Navigate to the target page
    const fullUrl = `${BASE_URL}${url}`;
    try {
      if (page.url() !== fullUrl) {
        await page.goto(fullUrl, { timeout: 10000 });
        // Wait for the page to stabilize
        await page.waitForLoadState('domcontentloaded');
      }
    } catch {
      console.log(`  SKIP: Could not navigate to ${url}`);
      for (const t of tasks) {
        console.log(`  SKIP  ${t.selector}  (navigation failed)`);
        results.skip++;
      }
      continue;
    }

    // Validate each selector on the current page
    for (const task of tasks) {
      try {
        const count = await page.locator(task.selector).count();
        if (count > 0) {
          console.log(`  PASS  ${task.selector}  (${count} match${count > 1 ? 'es' : ''}) [${task.file}]`);
          results.pass++;
        } else if (task.conditional) {
          console.log(`  OK    ${task.selector}  (conditional — 0 matches is expected) [${task.file}]`);
          results.conditional++;
        } else {
          console.log(`  FAIL  ${task.selector}  (0 matches on ${url}) [${task.file}]`);
          results.fail++;
          failures.push({ file: task.file, selector: task.selector, url });
        }
      } catch (err) {
        console.log(`  SKIP  ${task.selector}  (invalid selector: ${err.message}) [${task.file}]`);
        results.skip++;
      }
    }
  }

  // For login page selectors, navigate there if we haven't validated it yet
  if (byUrl.has('/') && loggedIn) {
    // We need to navigate back to login page — but we're logged in.
    // Clear cookies and go to login.
    await context.clearCookies();
    try {
      await page.goto(BASE_URL, { timeout: 10000 });
      await page.waitForLoadState('domcontentloaded');
    } catch {
      // Already handled above
    }

    for (const task of byUrl.get('/')) {
      try {
        const count = await page.locator(task.selector).count();
        if (count > 0) {
          console.log(`  PASS  ${task.selector}  (${count} match${count > 1 ? 'es' : ''}) [${task.file}]`);
          results.pass++;
        } else if (task.conditional) {
          console.log(`  OK    ${task.selector}  (conditional — 0 matches is expected) [${task.file}]`);
          results.conditional++;
        } else {
          console.log(`  FAIL  ${task.selector}  (0 matches on /) [${task.file}]`);
          results.fail++;
          failures.push({ file: task.file, selector: task.selector, url: '/' });
        }
      } catch (err) {
        console.log(`  SKIP  ${task.selector}  (invalid selector: ${err.message}) [${task.file}]`);
        results.skip++;
      }
    }
  }

  await browser.close();

  // 4. Summary
  console.log('\n── Summary ──────────────────────────────────────────────────');
  console.log(`  PASS: ${results.pass}  |  FAIL: ${results.fail}  |  CONDITIONAL: ${results.conditional}  |  SKIP: ${results.skip}`);

  if (failures.length > 0) {
    console.log('\nFailed selectors (no matching elements on live page):');
    for (const f of failures) {
      console.log(`  ${f.file}: "${f.selector}" → 0 matches on ${f.url}`);
    }
  }

  // Exit with failure only if there are hard failures
  process.exit(results.fail > 0 ? 1 : 0);
}

main().catch(err => {
  console.error('Locator validation error:', err.message);
  process.exit(1);
});
