using Microsoft.Playwright;

namespace Framework.Core.Pages;

/// <summary>
/// Page Object for the SauceDemo login page (https://www.saucedemo.com).
///
/// Why this exists: Centralises every selector and action related to the login
/// screen in one place. If the site's HTML changes (e.g., the username field gets
/// a new ID), only this file needs updating — not every test that performs a login.
///
/// Inherits from BasePage, which provides the shared ClickAsync, FillAsync, and
/// other helper methods. This class adds the login-specific selectors and
/// business-logic methods (like LoginAs) on top of that foundation.
/// </summary>
public class LoginPage : BasePage
{
    // CSS selectors for the login form elements.
    // Stored as private constants so they are defined in one place and cannot
    // be accidentally changed by a subclass. The "#" prefix means "ID selector"
    // (the most reliable selector type because IDs are unique per page).
    private const string UsernameInput   = "#user-name";
    private const string PasswordInput   = "#password";
    private const string LoginButton     = "#login-button";

    // This selector uses an attribute selector: find an <h3> element whose
    // data-test attribute equals "error". Attribute selectors are useful when
    // an element has no unique ID but has a stable test-specific attribute.
    private const string ErrorMessage    = "h3[data-test='error']";

    /// <summary>
    /// Constructor — passes the Playwright IPage up to BasePage so all
    /// inherited helper methods operate on the same browser tab.
    /// </summary>
    public LoginPage(IPage page) : base(page) { }

    /// <summary>
    /// Types the given username into the username input field.
    /// Uses BasePage.FillAsync which clears any existing text before typing.
    /// </summary>
    public async Task EnterUsername(string username) =>
        await FillAsync(UsernameInput, username, "username");

    /// <summary>
    /// Types the given password into the password input field.
    /// Playwright does not mask the value in traces by default; for real projects
    /// consider using the SecretValue option or clearing sensitive data after the test.
    /// </summary>
    public async Task EnterPassword(string password) =>
        await FillAsync(PasswordInput, password, "password");

    /// <summary>
    /// Clicks the Login button to submit the form.
    /// Playwright waits for the button to be visible and enabled before clicking.
    /// </summary>
    public async Task ClickLogin() =>
        await ClickAsync(LoginButton, "login button");

    /// <summary>
    /// Convenience method that performs a complete login in one call:
    /// enters the username, enters the password, and clicks the login button.
    ///
    /// Why this exists: Most tests need to log in as a precondition. Providing a
    /// single LoginAs() method means tests read like a user story ("login as X")
    /// rather than three separate steps, and it keeps test code concise.
    /// </summary>
    public async Task LoginAs(string username, string password)
    {
        await EnterUsername(username);
        await EnterPassword(password);
        await ClickLogin();
    }

    /// <summary>
    /// Reads and returns the text of the error banner that appears after a failed login.
    /// Example return values: "Epic sadface: Username is required",
    /// "Epic sadface: Sorry, this user has been locked out."
    /// </summary>
    public async Task<string> GetErrorMessage() =>
        await GetTextAsync(ErrorMessage);

    /// <summary>
    /// Returns true if the red error banner is currently visible on the page.
    /// Used to assert that a login failure produced a user-facing error (rather than
    /// silently failing or navigating away).
    /// </summary>
    public async Task<bool> IsErrorDisplayed() =>
        await IsVisibleAsync(ErrorMessage);

    /// <summary>
    /// Returns true if the Login button is visible.
    /// Used after a logout to confirm the user was returned to the login page
    /// (as opposed to some intermediate or error page).
    /// </summary>
    public async Task<bool> IsLoginButtonVisible() =>
        await IsVisibleAsync(LoginButton);
}
