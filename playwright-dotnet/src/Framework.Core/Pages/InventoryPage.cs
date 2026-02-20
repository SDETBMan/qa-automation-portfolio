using Microsoft.Playwright;

namespace Framework.Core.Pages;

public class InventoryPage : BasePage
{
    private const string CartBadge       = ".shopping_cart_badge";
    private const string CartLink        = ".shopping_cart_link";
    private const string AddToCartPrefix = "[id^='add-to-cart-']";
    private const string RemovePrefix    = "[id^='remove-']";
    private const string InventoryItems  = ".inventory_item";

    public InventoryPage(IPage page) : base(page) { }

    /// <summary>Clicks the first "Add to cart" button on the page.</summary>
    public async Task AddFirstItemToCart() =>
        await Page.Locator(AddToCartPrefix).First.ClickAsync();

    /// <summary>Clicks the "Add to cart" button for a specific item by product name slug.</summary>
    public async Task AddItemToCart(string itemSlug) =>
        await ClickAsync($"#add-to-cart-{itemSlug}", $"add-to-cart-{itemSlug}");

    /// <summary>Clicks the "Remove" button for a specific item by product name slug.</summary>
    public async Task RemoveItemFromCart(string itemSlug) =>
        await ClickAsync($"#remove-{itemSlug}", $"remove-{itemSlug}");

    public async Task GoToCart() =>
        await ClickAsync(CartLink, "cart link");

    public async Task<string> GetCartBadgeCount() =>
        await GetTextAsync(CartBadge);

    public async Task<bool> IsCartBadgeVisible() =>
        await IsVisibleAsync(CartBadge);

    public async Task<int> GetInventoryItemCount() =>
        await Page.Locator(InventoryItems).CountAsync();
}
