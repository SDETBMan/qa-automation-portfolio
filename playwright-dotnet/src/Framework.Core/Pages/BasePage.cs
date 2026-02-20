using Microsoft.Playwright;

namespace Framework.Core.Pages;

/// <summary>
/// Base class for all Page Objects. Wraps ILocator interactions with
/// Playwright's built-in auto-wait — no explicit WebDriverWait needed.
/// </summary>
public abstract class BasePage
{
    protected readonly IPage Page;

    protected BasePage(IPage page)
    {
        Page = page;
    }

    protected async Task ClickAsync(string selector, string name = "")
    {
        await Page.Locator(selector).ClickAsync();
    }

    protected async Task FillAsync(string selector, string value, string name = "")
    {
        await Page.Locator(selector).FillAsync(value);
    }

    protected async Task<string> GetTextAsync(string selector)
    {
        return await Page.Locator(selector).InnerTextAsync();
    }

    protected async Task<bool> IsVisibleAsync(string selector)
    {
        return await Page.Locator(selector).IsVisibleAsync();
    }

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
            return false;
        }
    }

    protected async Task WaitForElementAsync(string selector)
    {
        await Page.Locator(selector).WaitForAsync();
    }
}
