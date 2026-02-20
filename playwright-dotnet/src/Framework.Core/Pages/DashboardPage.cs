using Microsoft.Playwright;

namespace Framework.Core.Pages;

public class DashboardPage : BasePage
{
    private const string CartLink        = ".shopping_cart_link";
    private const string BurgerMenu      = "#react-burger-menu-btn";
    private const string LogoutLink      = "#logout_sidebar_link";
    private const string PageTitle       = ".title";
    private const string CartBadge       = ".shopping_cart_badge";

    public DashboardPage(IPage page) : base(page) { }

    public async Task<string> GetPageTitle() =>
        await GetTextAsync(PageTitle);

    public async Task OpenMenu() =>
        await ClickAsync(BurgerMenu, "burger menu");

    public async Task Logout()
    {
        await OpenMenu();
        await ClickAsync(LogoutLink, "logout link");
    }

    public async Task GoToCart() =>
        await ClickAsync(CartLink, "cart link");

    public async Task<bool> IsCartBadgeVisible() =>
        await IsVisibleAsync(CartBadge);

    public async Task<string> GetCartBadgeCount() =>
        await GetTextAsync(CartBadge);

    public async Task<bool> IsOnDashboard() =>
        await WaitForUrlAsync("inventory");
}
