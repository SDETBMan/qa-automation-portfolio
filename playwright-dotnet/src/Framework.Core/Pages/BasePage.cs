using Microsoft.Playwright;

namespace Framework.Core.Pages;

/// <summary>
/// Abstract base class for all Page Object classes in the framework.
///
/// Why this exists: The Page Object Model (POM) is an industry-standard design pattern
/// that separates "how to interact with a page" (this layer) from "what to verify"
/// (the test layer). Benefits:
///   - A selector change (e.g., a developer renames a CSS class) only needs fixing here,
///     not in every test that touches that element.
///   - Test methods read like plain English: "loginPage.LoginAs(...)" instead of
///     "page.Locator('#user-name').FillAsync(...)".
///
/// Why abstract: BasePage should never be instantiated directly. Each concrete page
/// (LoginPage, DashboardPage, etc.) extends this class and adds its own page-specific
/// methods. The "abstract" keyword enforces that rule at compile time.
///
/// Auto-waiting: Playwright's ILocator API automatically waits for elements to be
/// visible, enabled, and stable before interacting. This eliminates the fragile
/// Thread.Sleep() and explicit WebDriverWait calls common in older Selenium frameworks.
///
/// IPage: Playwright's representation of a single browser tab. One IPage = one tab.
/// It is injected (passed in) rather than created here so tests can share the same
/// browser context managed by the test framework (PageTest base class).
/// </summary>
public abstract class BasePage
{
    // Protected means this field is accessible to this class and all subclasses
    // (LoginPage, DashboardPage, etc.) but not to outside code. The readonly keyword
    // prevents it from being reassigned after the constructor runs.
    protected readonly IPage Page;

    /// <summary>
    /// Constructor — receives the Playwright IPage instance from the test.
    /// All page objects share the same live browser tab, so navigation on
    /// one page object is immediately visible to another.
    /// </summary>
    protected BasePage(IPage page)
    {
        Page = page;
    }

    /// <summary>
    /// Clicks the element identified by the given CSS selector.
    /// Playwright automatically waits for the element to be visible and enabled
    /// before clicking — no manual wait code required.
    ///
    /// The optional <paramref name="name"/> parameter is reserved for logging
    /// and reporting purposes (e.g., "clicked login button") without affecting behaviour.
    /// </summary>
    protected async Task ClickAsync(string selector, string name = "")
    {
        // Page.Locator(selector) creates a lazy reference to a DOM element.
        // It doesn't find the element until an action (like ClickAsync) is called.
        await Page.Locator(selector).ClickAsync();
    }

    /// <summary>
    /// Clears the input field identified by the selector and types the given value.
    /// FillAsync is preferred over TypeAsync for form fields because it sets the
    /// entire value atomically rather than simulating key-by-key input, which is
    /// faster and avoids issues with autocomplete or input masking.
    /// </summary>
    protected async Task FillAsync(string selector, string value, string name = "")
    {
        await Page.Locator(selector).FillAsync(value);
    }

    /// <summary>
    /// Returns the visible inner text of the element matching the selector.
    /// Used for reading labels, error messages, badge counts, etc.
    /// InnerTextAsync returns the rendered text (after CSS is applied), not raw HTML.
    /// </summary>
    protected async Task<string> GetTextAsync(string selector)
    {
        return await Page.Locator(selector).InnerTextAsync();
    }

    /// <summary>
    /// Returns true if the element matching the selector is currently visible on the page.
    /// "Visible" in Playwright means the element exists in the DOM, has non-zero dimensions,
    /// and is not hidden by CSS (display:none, visibility:hidden, opacity:0).
    /// This does NOT wait — it checks the current state immediately.
    /// </summary>
    protected async Task<bool> IsVisibleAsync(string selector)
    {
        return await Page.Locator(selector).IsVisibleAsync();
    }

    /// <summary>
    /// Waits until the browser URL contains the given fragment string, then returns true.
    /// Returns false if the URL does not change within Playwright's default timeout.
    ///
    /// Why the fast-path check: After a click that triggers navigation, Playwright's
    /// Page.WaitForURLAsync waits for a *future* URL change event. If the navigation
    /// already completed before this method is called (which is common with auto-wait),
    /// WaitForURLAsync would hang indefinitely waiting for an event that already fired.
    /// The pre-check avoids that deadlock.
    ///
    /// The Regex.Escape call treats the fragment as a literal string, not a regex pattern,
    /// so special characters in URLs (e.g., "?", ".") are matched literally.
    /// </summary>
    protected async Task<bool> WaitForUrlAsync(string fragment)
    {
        // Fast path: if the navigation already completed (common after ClickAsync),
        // WaitForURLAsync would hang waiting for a future event that never fires.
        if (Page.Url.Contains(fragment, StringComparison.OrdinalIgnoreCase))
            return true;

        try
        {
            await Page.WaitForURLAsync(new System.Text.RegularExpressions.Regex(
                System.Text.RegularExpressions.Regex.Escape(fragment),
                System.Text.RegularExpressions.RegexOptions.IgnoreCase));
            return true;
        }
        catch (TimeoutException)
        {
            // Navigation did not happen within the timeout — return false instead of
            // throwing, letting the test produce a meaningful assertion message.
            return false;
        }
    }

    /// <summary>
    /// Waits until the element matching the selector is present and visible in the DOM.
    /// Used before reading data from slow-loading elements (e.g., results loaded via AJAX).
    /// Playwright's WaitForAsync uses the default timeout configured in playwright.config
    /// (or 30 seconds if not overridden).
    /// </summary>
    protected async Task WaitForElementAsync(string selector)
    {
        await Page.Locator(selector).WaitForAsync();
    }
}
