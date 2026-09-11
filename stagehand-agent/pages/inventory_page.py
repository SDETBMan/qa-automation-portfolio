"""
inventory_page.py — Page Object for the SauceDemo inventory page.

Selectors match cypress/cypress/pages/InventoryPage.ts.
"""

from __future__ import annotations

from pages.base_page import BasePage


class InventoryPage(BasePage):
    """Inventory page interactions for SauceDemo."""

    # Selectors
    INVENTORY_ITEM = ".inventory_item"
    ITEM_NAME = ".inventory_item_name"
    CART_BADGE = ".shopping_cart_badge"
    CART_LINK = ".shopping_cart_link"
    ADD_TO_CART_PREFIX = "[data-test='add-to-cart-"
    REMOVE_PREFIX = "[data-test='remove-"

    def get_product_count(self) -> int:
        """Return the number of products displayed on the page."""
        return self.page.locator(self.INVENTORY_ITEM).count()

    def get_product_names(self) -> list[str]:
        """Return a list of all product names on the page."""
        return self.page.locator(self.ITEM_NAME).all_inner_texts()

    def add_item_to_cart(self, product_id: str) -> None:
        """Click 'Add to cart' for a specific product by its data-test ID suffix."""
        selector = f"{self.ADD_TO_CART_PREFIX}{product_id}']"
        self.click(selector)

    def remove_item_from_cart(self, product_id: str) -> None:
        """Click 'Remove' for a specific product."""
        selector = f"{self.REMOVE_PREFIX}{product_id}']"
        self.click(selector)

    def get_cart_badge_count(self) -> int:
        """Return the number shown on the cart badge, or 0 if not visible."""
        if self.is_element_visible(self.CART_BADGE):
            text = self.get_text(self.CART_BADGE)
            return int(text)
        return 0

    def go_to_cart(self) -> None:
        """Click the shopping cart icon to navigate to the cart page."""
        self.click(self.CART_LINK)
