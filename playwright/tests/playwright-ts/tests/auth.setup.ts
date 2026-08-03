import { test as setup } from '@playwright/test';
import { LoginPage } from '../pages/loginPage';

/**
 * Global auth setup — runs once before all browser projects.
 *
 * Logs in as the standard test user and saves the authenticated browser state
 * (cookies, localStorage) to a file. Browser projects that depend on this
 * setup project reuse the saved state, eliminating per-test login overhead.
 *
 * Why storageState over per-test login:
 *   - At scale, login-per-test adds seconds × hundreds of tests = minutes of CI
 *   - For MFA-protected apps, it's the difference between one OTP and hundreds
 *   - The authenticatedPage fixture now loads state from file instead of
 *     performing UI login, but the fixture guard (waitForURL) still validates
 *
 * C# equivalent: AuthenticatedTest.cs uses [SetUp] per-test login.
 * The storageState pattern has no direct C# analog — it's a TypeScript-only
 * optimization. The C# equivalent would be a [OneTimeSetUp] that serializes
 * cookies, but NUnit doesn't provide the same browser-state serialization.
 */

const authFile = 'test-results/.auth/user.json';

setup('authenticate as standard user', async ({ page }) => {
  await page.goto('/');

  await new LoginPage(page).loginAs(
    process.env['APP_USERNAME'] ?? 'standard_user',
    process.env['APP_PASSWORD'] ?? 'secret_sauce',
  );

  // Wait for login to complete before saving state.
  await page.waitForURL(/inventory/, { timeout: 10_000 });

  // Save authenticated state — cookies and localStorage.
  await page.context().storageState({ path: authFile });
});
