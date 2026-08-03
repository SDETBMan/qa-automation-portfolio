using Microsoft.Playwright;

namespace Framework.Core.Pages;

/// <summary>
/// Page Object for the SauceDemo product inventory list on inventory.html.
///
/// Handles interactions with individual product cards: adding items to the cart,
/// removing items, navigating to the cart, and reading cart state. This is the
/// primary page where end-to-end shopping flow tests begin.
///
/// The "slug" pattern: SauceDemo generates button IDs from the product name
/// (e.g., "sauce-labs-backpack"). Using the slug as a parameter lets tests
/// reference products by their readable name rather than a numeric ID, making
/// tests self-documenting.
///
/// Attribute selectors used here:
///   [id^='add-to-cart-'] — matches any element whose id STARTS WITH "add-to-cart-"
///   [id^='remove-']      — matches any element whose id STARTS WITH "remove-"
/// These "starts with" selectors catch all products generically without needing
/// a list of every individual product ID.
///
/// Inherits shared interaction helpers from BasePage.
/// </summary>
public class InventoryPage : BasePage
{
    // CSS selectors for inventory page elements.
    private const string CartBadge       = ".shopping_cart_badge";    // Numeric item count on cart icon
    private const string CartLink        = ".shopping_cart_link";     // Cart icon — clicks to go to cart page
    private const string AddToCartPrefix = "[id^='add-to-cart-']";   // Matches ALL "Add to cart" buttons
    private const string RemovePrefix    = "[id^='remove-']";        // Matches ALL "Remove" buttons
    private const string InventoryItems  = ".inventory_item";        // Each product card container

    /// <summary>
    /// Constructor — passes the IPage instance up to BasePage.
    /// </summary>
    public InventoryPage(IPage page) : base(page) { }

    /// <summary>
    /// Clicks the first "Add to cart" button on the page, regardless of which product it belongs to.
    /// Useful for smoke tests where the specific product does not matter —
    /// the test only needs to confirm the cart mechanism works.
    ///
    /// .First is a Playwright shorthand for .Nth(0), selecting the first matched element.
    /// </summary>
    public async Task AddFirstItemToCart() =>
        await Page.Locator(AddToCartPrefix).First.ClickAsync();

    /// <summary>
    /// Clicks the "Add to cart" button for the product identified by its slug.
    /// The slug is the hyphenated, lowercase product name used in the button's HTML id attribute.
    ///
    /// Example: AddItemToCart("sauce-labs-backpack") clicks the button with id="add-to-cart-sauce-labs-backpack".
    /// </summary>
    public async Task AddItemToCart(string itemSlug) =>
        await ClickAsync($"#add-to-cart-{itemSlug}", $"add-to-cart-{itemSlug}");

    /// <summary>
    /// Clicks the "Remove" button for an item already in the cart, identified by its slug.
    /// After clicking, the item is removed from the cart and the "Add to cart" button reappears.
    ///
    /// Example: RemoveItemFromCart("sauce-labs-backpack") clicks id="remove-sauce-labs-backpack".
    /// </summary>
    public async Task RemoveItemFromCart(string itemSlug) =>
        await ClickAsync($"#remove-{itemSlug}", $"remove-{itemSlug}");

    /// <summary>
    /// Clicks the shopping cart icon to navigate to the cart page (cart.html).
    /// </summary>
    public async Task GoToCart() =>
        await ClickAsync(CartLink, "cart link");

    /// <summary>
    /// Returns the text shown in the cart badge (e.g., "1", "2").
    /// The badge appears on the cart icon and reflects the current number of items added.
    /// </summary>
    public async Task<string> GetCartBadgeCount() =>
        await GetTextAsync(CartBadge);

    /// <summary>
    /// Returns true if the cart badge is currently visible on the cart icon.
    /// The badge is only visible when the cart contains at least one item.
    /// </summary>
    public async Task<bool> IsCartBadgeVisible() =>
        await IsVisibleAsync(CartBadge);

    /// <summary>
    /// Returns the total number of product cards currently displayed on the inventory page.
    /// The standard SauceDemo inventory has 6 items. Used to verify the page loaded
    /// completely or that filtering did not unexpectedly remove products.
    ///
    /// CountAsync is a Playwright method that returns the number of elements matching
    /// the locator — it never throws even if zero elements are found.
    /// </summary>
    public async Task<int> GetInventoryItemCount() =>
        await Page.Locator(InventoryItems).CountAsync();
}
