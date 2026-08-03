using Microsoft.Playwright;

namespace Framework.Core.Pages;

/// <summary>
/// Page Object for the SauceDemo inventory/dashboard page (inventory.html).
///
/// This is the first page a user sees after a successful login. It displays
/// all available products and contains the navigation elements (cart icon,
/// hamburger menu, logout link) shared across the authenticated section of the app.
///
/// Why a separate page object from InventoryPage: DashboardPage owns the
/// top-level navigation concerns (page title, cart icon, menu, logout),
/// while InventoryPage owns the product listing actions (add to cart, remove
/// from cart, item count). This separation keeps each class focused and small.
///
/// Inherits shared interaction helpers from BasePage.
/// </summary>
public class DashboardPage : BasePage
{
    // CSS selectors — defined as private constants so any selector change is
    // made in exactly one place rather than scattered across multiple test files.
    private const string CartLink        = ".shopping_cart_link";   // The cart icon/link in the header
    private const string BurgerMenu      = "#react-burger-menu-btn"; // The hamburger (≡) menu button
    private const string LogoutLink      = "#logout_sidebar_link";   // Logout option inside the open menu
    private const string PageTitle       = ".title";                  // The "Products" heading
    private const string CartBadge       = ".shopping_cart_badge";   // The red number overlay on the cart icon

    /// <summary>
    /// Constructor — passes the IPage instance up to BasePage.
    /// </summary>
    public DashboardPage(IPage page) : base(page) { }

    /// <summary>
    /// Returns the current page heading text.
    /// On the inventory page this should be "Products".
    /// Useful for asserting that a login redirect landed on the correct page.
    /// </summary>
    public async Task<string> GetPageTitle() =>
        await GetTextAsync(PageTitle);

    /// <summary>
    /// Clicks the hamburger menu button to open the navigation sidebar.
    /// The sidebar slides in and exposes links like Logout, About, and Reset App State.
    /// Must be called before interacting with any sidebar link (e.g., LogoutLink).
    /// </summary>
    public async Task OpenMenu() =>
        await ClickAsync(BurgerMenu, "burger menu");

    /// <summary>
    /// Performs a complete logout: opens the sidebar menu and clicks the Logout link.
    /// After this call the browser should be back on the login page.
    ///
    /// Combining two steps into one method hides the menu-first requirement from
    /// tests so they can simply call dashboardPage.Logout() without knowing the
    /// internal sequence.
    /// </summary>
    public async Task Logout()
    {
        // Step 1: The logout link is hidden inside a sidebar — open the menu first.
        await OpenMenu();
        // Step 2: Now that the sidebar is visible, click Logout.
        await ClickAsync(LogoutLink, "logout link");
    }

    /// <summary>
    /// Clicks the shopping cart icon in the header to navigate to the cart page.
    /// </summary>
    public async Task GoToCart() =>
        await ClickAsync(CartLink, "cart link");

    /// <summary>
    /// Returns true if the red numeric badge on the cart icon is currently visible.
    /// The badge only appears when at least one item has been added to the cart.
    /// Useful for asserting that adding a product updated the cart counter.
    /// </summary>
    public async Task<bool> IsCartBadgeVisible() =>
        await IsVisibleAsync(CartBadge);

    /// <summary>
    /// Returns the text shown inside the cart badge (e.g., "1", "2", "3").
    /// This count reflects how many distinct items are currently in the cart.
    /// </summary>
    public async Task<string> GetCartBadgeCount() =>
        await GetTextAsync(CartBadge);

    /// <summary>
    /// Returns true when the browser URL contains "inventory", confirming the user
    /// is on the dashboard/inventory page and not redirected elsewhere.
    /// Delegates to BasePage.WaitForUrlAsync which handles the fast-path optimisation
    /// for already-completed navigations.
    /// </summary>
    public async Task<bool> IsOnDashboard() =>
        await WaitForUrlAsync("inventory");
}
