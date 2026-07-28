#!/usr/bin/env npx tsx
/**
 * AI Test Generator — Produces Cypress .cy.ts files from plain-English user stories.
 *
 * Reads the project's page objects, custom commands, fixtures, and existing tests
 * to give the LLM full context about framework patterns, then generates a test file
 * that follows the same conventions.
 *
 * Usage:
 *   npx tsx ai-generator/generate-test.ts "User adds two items to cart and completes checkout"
 *   npx tsx ai-generator/generate-test.ts --story "User sorts products by price" --name price-sort
 *   npx tsx ai-generator/generate-test.ts --dry-run "User logs in with invalid credentials"
 *
 * Environment:
 *   ANTHROPIC_API_KEY  — required
 *   MODEL              — optional (default: claude-sonnet-4-20250514)
 */

import Anthropic from '@anthropic-ai/sdk';
import * as fs from 'fs';
import * as path from 'path';

// ── Constants ───────────────────────────────────────────────────────────────────

const PROJECT_ROOT = path.resolve(__dirname, '..');

const CONTEXT_FILES = {
  pageObjects: [
    'cypress/pages/BasePage.ts',
    'cypress/pages/LoginPage.ts',
    'cypress/pages/InventoryPage.ts',
    'cypress/pages/CartPage.ts',
    'cypress/pages/CheckoutPage.ts',
  ],
  commands: ['cypress/support/commands.ts'],
  fixtures: ['cypress/fixtures/users.json', 'cypress/fixtures/products.json'],
  exampleTests: [
    'cypress/e2e/login.cy.ts',
    'cypress/e2e/inventory.cy.ts',
    'cypress/e2e/checkout.cy.ts',
  ],
} as const;

const SYSTEM_PROMPT = `You are a senior SDET generating Cypress TypeScript test files for a SauceDemo (https://www.saucedemo.com) E2E test suite.

You have access to the project's page objects, custom commands, fixtures, and example tests below. Your generated tests MUST follow these exact conventions:

## Conventions
1. Import page objects from '../pages/<PageName>' and instantiate them as const at module level.
2. Use \`testIsolation: false\` in the describe() config to avoid SauceDemo CDN rate-limiting.
3. Use \`before()\` for one-time setup: login via \`cy.login()\` custom command with fixture data.
4. Use \`beforeEach()\` for state reset — typically \`cy.clearCart()\` when cart state matters.
5. Tag every \`it()\` block with \`@smoke\` or \`@regression\` in the description string.
6. Use \`cy.fixture()\` to load test data — never hardcode credentials or product names.
7. Use page object methods — never use raw \`cy.get()\` selectors directly in test files.
8. Use custom commands (\`cy.login\`, \`cy.addToCart\`, \`cy.clearCart\`) where appropriate.
9. Export nothing — the file is a side-effect-only test module.
10. Add a JSDoc comment above the describe() explaining the testIsolation strategy.

## Available page objects and their methods:
- LoginPage: open(), loginAs(user, pass), getErrorMessage(), assertErrorContains(text), assertOnLoginPage()
- InventoryPage: open(), getProductCount(), addItemToCart(name), removeItemFromCart(name), getCartBadgeCount(), cartBadgeShouldNotExist(), goToCart(), sortBy(option: 'az'|'za'|'lohi'|'hilo'), getProductNames(), getProductPrices()
- CartPage: open(), getCartItems(), getCartItemNames(), proceedToCheckout(), continueShopping(), assertItemInCart(name), assertCartEmpty()
- CheckoutPage: openStepOne(), fillInfo(first, last, zip), continueToStepTwo(), finish(), cancel(), getConfirmationMessage(), assertOrderComplete(), assertErrorContains(text)

## Available custom commands:
- cy.login(username, password) — visits /, logs in, asserts on /inventory.html
- cy.addToCart(productName) — finds item by name, clicks add-to-cart button
- cy.clearCart() — removes all cart items, clicks Continue Shopping to return to inventory

## Available fixtures:
- users.json: standard, locked, problem, performance, invalid (each has username + password)
- products.json: products[] array with {name, price, id}; stubbedProducts[] for network stubs

## Output format
Return ONLY the TypeScript code for the .cy.ts file. No markdown fences, no explanation, no preamble. Just the raw TypeScript source code that can be saved directly to a file and executed by Cypress.`;

// ── Helpers ─────────────────────────────────────────────────────────────────────

function readProjectFile(relativePath: string): string {
  const fullPath = path.join(PROJECT_ROOT, relativePath);
  return fs.readFileSync(fullPath, 'utf-8');
}

function buildContext(): string {
  const sections: string[] = [];

  sections.push('# Page Objects\n');
  for (const file of CONTEXT_FILES.pageObjects) {
    sections.push(
      `## ${path.basename(file)}\n\`\`\`typescript\n${readProjectFile(file)}\n\`\`\`\n`,
    );
  }

  sections.push('# Custom Commands\n');
  for (const file of CONTEXT_FILES.commands) {
    sections.push(
      `## ${path.basename(file)}\n\`\`\`typescript\n${readProjectFile(file)}\n\`\`\`\n`,
    );
  }

  sections.push('# Fixtures\n');
  for (const file of CONTEXT_FILES.fixtures) {
    sections.push(
      `## ${path.basename(file)}\n\`\`\`json\n${readProjectFile(file)}\n\`\`\`\n`,
    );
  }

  sections.push('# Example Tests (follow these patterns exactly)\n');
  for (const file of CONTEXT_FILES.exampleTests) {
    sections.push(
      `## ${path.basename(file)}\n\`\`\`typescript\n${readProjectFile(file)}\n\`\`\`\n`,
    );
  }

  return sections.join('\n');
}

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 50);
}

function parseArgs(): { story: string; name?: string; dryRun: boolean } {
  const args = process.argv.slice(2);
  let story = '';
  let name: string | undefined;
  let dryRun = false;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--story' && args[i + 1]) {
      story = args[++i];
    } else if (arg === '--name' && args[i + 1]) {
      name = args[++i];
    } else if (arg === '--dry-run') {
      dryRun = true;
    } else if (arg === '--help' || arg === '-h') {
      printUsage();
      process.exit(0);
    } else if (!arg.startsWith('--')) {
      story = arg;
    }
  }

  if (!story) {
    printUsage();
    process.exit(1);
  }

  return { story, name, dryRun };
}

function printUsage(): void {
  console.log(`
AI Test Generator — Cypress .cy.ts from plain-English user stories

Usage:
  npx tsx ai-generator/generate-test.ts "User story here"
  npx tsx ai-generator/generate-test.ts --story "..." --name my-test
  npx tsx ai-generator/generate-test.ts --dry-run "..."

Options:
  --story <text>   The user story to generate a test for
  --name <slug>    Output file name (default: slugified story)
  --dry-run        Print generated code to stdout without writing a file
  --help, -h       Show this help

Environment:
  ANTHROPIC_API_KEY   Required — your Anthropic API key
  MODEL               Optional — model to use (default: claude-sonnet-4-20250514)

Output:
  Generated tests are written to cypress/e2e/generated/<name>.cy.ts
  Run with: npx cypress run --spec "cypress/e2e/generated/<name>.cy.ts"
`);
}

// ── Main ────────────────────────────────────────────────────────────────────────

async function main(): Promise<void> {
  const { story, name, dryRun } = parseArgs();

  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('Error: ANTHROPIC_API_KEY environment variable is required.');
    console.error('Set it with: export ANTHROPIC_API_KEY=sk-ant-...');
    process.exit(1);
  }

  const client = new Anthropic();
  const model = process.env.MODEL || 'claude-sonnet-4-20250514';

  // 1. Read framework context
  console.log('Reading project context...');
  console.log(
    `  ${CONTEXT_FILES.pageObjects.length} page objects, ` +
      `${CONTEXT_FILES.commands.length} command files, ` +
      `${CONTEXT_FILES.fixtures.length} fixtures, ` +
      `${CONTEXT_FILES.exampleTests.length} example tests`,
  );
  const context = buildContext();

  // 2. Call Claude
  console.log(`\nGenerating test for: "${story}"`);
  console.log(`Model: ${model}\n`);

  const response = await client.messages.create({
    model,
    max_tokens: 4096,
    system: SYSTEM_PROMPT,
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'text',
            text: `Here is the full framework context:\n\n${context}`,
          },
          {
            type: 'text',
            text: `Generate a Cypress TypeScript test file for the following user story:\n\n"${story}"`,
          },
        ],
      },
    ],
  });

  // 3. Extract generated code
  const generated = response.content
    .filter((block): block is Anthropic.TextBlock => block.type === 'text')
    .map((block) => block.text)
    .join('');

  // Strip markdown fences if the model included them despite instructions
  const code = generated
    .replace(/^```(?:typescript|ts)?\n?/, '')
    .replace(/\n?```$/, '')
    .trim();

  // 4. Output
  if (dryRun) {
    console.log('--- Generated Test ---\n');
    console.log(code);
    console.log('\n--- End ---');
    console.log(`\nTokens used: ${response.usage.input_tokens} in, ${response.usage.output_tokens} out`);
    return;
  }

  const outDir = path.join(PROJECT_ROOT, 'cypress', 'e2e', 'generated');
  fs.mkdirSync(outDir, { recursive: true });

  const fileName = `${name || slugify(story)}.cy.ts`;
  const outPath = path.join(outDir, fileName);

  fs.writeFileSync(outPath, code + '\n', 'utf-8');

  const relativePath = path.relative(PROJECT_ROOT, outPath).replace(/\\/g, '/');
  console.log(`Generated: ${relativePath}`);
  console.log(`Tokens:    ${response.usage.input_tokens} in, ${response.usage.output_tokens} out`);
  console.log(`\nRun it:`);
  console.log(`  npx cypress run --spec "${relativePath}"`);
}

main().catch((err) => {
  console.error('Generation failed:', err instanceof Error ? err.message : err);
  process.exit(1);
});
