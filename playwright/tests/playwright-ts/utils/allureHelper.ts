import {
  label,
  step as allureStep,
  attachment as allureAttachment,
  LabelName,
  ContentType,
} from 'allure-js-commons';

/**
 * Allure metadata helpers — TypeScript equivalent of C# [AllureSuite], [AllureFeature],
 * [AllureStory], and Allure.Step() decorators.
 *
 * In C#, Allure metadata is applied via NUnit attributes on test classes and methods:
 *   [AllureNUnit]
 *   [AllureSuite("Login")]
 *   [AllureFeature("Authentication")]
 *   [AllureStory("Valid login navigates to inventory")]
 *
 * In Playwright + TypeScript, there are no decorators on test functions. Instead,
 * call these helpers at the top of each test body (or in a beforeEach hook) to attach
 * the same metadata to the Allure report.
 *
 * Why this matters for the BlastPoint role:
 *   Allure's suite/feature/story hierarchy maps directly to how QA teams organise
 *   regression coverage: Suite → functional area, Feature → capability,
 *   Story → specific user scenario. This makes test gaps visible at a glance.
 */

/** Attach suite label (top-level grouping). C# equivalent: [AllureSuite("...")] */
export function suite(name: string): void {
  label(LabelName.SUITE, name);
}

/** Attach parent suite label (above suite in the tree). */
export function parentSuite(name: string): void {
  label(LabelName.PARENT_SUITE, name);
}

/** Attach sub-suite label (below suite in the tree). */
export function subSuite(name: string): void {
  label(LabelName.SUB_SUITE, name);
}

/** Attach feature label. C# equivalent: [AllureFeature("...")] */
export function feature(name: string): void {
  label(LabelName.FEATURE, name);
}

/** Attach story label. C# equivalent: [AllureStory("...")] */
export function story(name: string): void {
  label(LabelName.STORY, name);
}

/** Attach severity label (blocker, critical, normal, minor, trivial). */
export function severity(level: 'blocker' | 'critical' | 'normal' | 'minor' | 'trivial'): void {
  label(LabelName.SEVERITY, level);
}

/** Attach an owner label (useful for triage — who owns this test area). */
export function owner(name: string): void {
  label(LabelName.OWNER, name);
}

/** Attach a tag label (maps to @smoke, @regression tags in Playwright grep). */
export function tag(name: string): void {
  label(LabelName.TAG, name);
}

/**
 * Wrap an async operation as a named Allure step. Steps appear as collapsible
 * entries in the Allure report, giving visibility into what each test does
 * without reading the source.
 *
 * C# equivalent: AllureApi.Step("step name", () => { ... });
 *
 * Example:
 *   await step('Query database for user record', async () => {
 *     rows = await db.executeQuery('SELECT * FROM users WHERE id = ?', [userId]);
 *   });
 *   await step('Verify username on profile page', async () => {
 *     await expect(page.locator('#name')).toHaveText(rows[0].name);
 *   });
 */
export async function step<T>(name: string, body: () => Promise<T>): Promise<T> {
  return allureStep(name, body);
}

/**
 * Attach a text or JSON artifact to the current test in the Allure report.
 * Useful for attaching DB query results, API responses, or debug context.
 *
 * Example:
 *   attach('DB query result', JSON.stringify(rows, null, 2), 'application/json');
 */
export function attach(name: string, content: string, type?: string): void {
  const contentType = type ?? ContentType.TEXT;
  allureAttachment(name, Buffer.from(content), contentType);
}
