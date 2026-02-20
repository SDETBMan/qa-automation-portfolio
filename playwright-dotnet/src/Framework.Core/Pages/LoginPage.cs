using Microsoft.Playwright;

namespace Framework.Core.Pages;

public class LoginPage : BasePage
{
    private const string UsernameInput   = "#user-name";
    private const string PasswordInput   = "#password";
    private const string LoginButton     = "#login-button";
    private const string ErrorMessage    = "h3[data-test='error']";

    public LoginPage(IPage page) : base(page) { }

    public async Task EnterUsername(string username) =>
        await FillAsync(UsernameInput, username, "username");

    public async Task EnterPassword(string password) =>
        await FillAsync(PasswordInput, password, "password");

    public async Task ClickLogin() =>
        await ClickAsync(LoginButton, "login button");

    public async Task LoginAs(string username, string password)
    {
        await EnterUsername(username);
        await EnterPassword(password);
        await ClickLogin();
    }

    public async Task<string> GetErrorMessage() =>
        await GetTextAsync(ErrorMessage);

    public async Task<bool> IsErrorDisplayed() =>
        await IsVisibleAsync(ErrorMessage);

    public async Task<bool> IsLoginButtonVisible() =>
        await IsVisibleAsync(LoginButton);
}
