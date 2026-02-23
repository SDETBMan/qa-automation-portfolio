using Microsoft.Playwright;

namespace Framework.Core.Pages;

/// <summary>
/// Page Object for the SauceDemo shopping cart page (cart.html).
///
/// This page is reached by clicking the cart icon from the inventory/dashboard.
/// It lists all items currently in the cart and provides buttons to continue
/// shopping or proceed to checkout.
///
/// Why XPath here: The item name is nested inside a cart_item container with
/// no unique ID, so an XPath expression is used to navigate the HTML tree
/// precisely. XPath is used sparingly — CSS selectors are preferred — but it is
/// the right tool when element hierarchy context is required for disambiguation.
///
/// Inherits shared interaction helpers from BasePage.
/// </summary>
public class CartPage : BasePage
{
    // CSS selectors for the cart page.
    private const string CartItems        = ".cart_item";           // Each line item row in the cart
    private const string CheckoutButton   = "#checkout";            // "Checkout" button — starts purchase flow
    private const string ContinueShopping = "#continue-shopping";  // Returns user to inventory page

    // XPath selector: navigates from any cart_item container down to its nested
    // inventory_item_name div. Used when CSS alone cannot uniquely target the element.
    // The "//" means "find anywhere in the document", and the nested path
    // ensures we get the name div that belongs to a cart_item (not some other context).
    private const string ItemNameXPath    = "//div[@class='cart_item']//div[@class='inventory_item_name']";

    /// <summary>
    /// Constructor — passes the IPage instance up to BasePage.
    /// </summary>
    public CartPage(IPage page) : base(page) { }

    /// <summary>
    /// Returns the number of line items currently shown in the cart.
    /// Each cart_item element represents one unique product, regardless of quantity.
    /// A return value of 0 means the cart is empty.
    /// </summary>
    public async Task<int> GetCartItemCount() =>
        await Page.Locator(CartItems).CountAsync();

    /// <summary>
    /// Clicks the "Checkout" button to begin the checkout/purchase flow.
    /// After this action the browser navigates to the first checkout step (checkout-step-one.html).
    /// </summary>
    public async Task ClickCheckout() =>
        await ClickAsync(CheckoutButton, "checkout button");

    /// <summary>
    /// Clicks "Continue Shopping" to return to the inventory page without checking out.
    /// The trailing underscore in the method name avoids a conflict with the C# keyword
    /// "continue" which is reserved for loop control flow.
    /// </summary>
    public async Task ContinueShopping_() =>
        await ClickAsync(ContinueShopping, "continue shopping");

    /// <summary>
    /// Returns the name text of the first item listed in the cart.
    /// Useful for asserting that a specific product was added (e.g., "Sauce Labs Backpack").
    /// Uses an XPath selector to drill into the nested name element within the cart row.
    /// </summary>
    public async Task<string> GetFirstItemName() =>
        await GetTextAsync(ItemNameXPath);

    /// <summary>
    /// Returns true when the browser URL contains "cart", confirming the user is on
    /// the cart page. Delegates to BasePage.WaitForUrlAsync which handles the
    /// already-navigated fast-path case.
    /// </summary>
    public async Task<bool> IsOnCartPage() =>
        await WaitForUrlAsync("cart");
}
