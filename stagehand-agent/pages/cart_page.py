"""
cart_page.py — Page Object for the SauceDemo cart page.

Selectors match cypress/cypress/pages/CartPage.ts.
"""

from __future__ import annotations

from pages.base_page import BasePage


class CartPage(BasePage):
    """Cart page interactions for SauceDemo."""

    # Selectors
    CART_ITEM = ".cart_item"
    ITEM_NAME = ".inventory_item_name"
    CHECKOUT_BUTTON = "[data-test='checkout']"
    CONTINUE_SHOPPING = "[data-test='continue-shopping']"
    REMOVE_BUTTON = ".cart_button"

    def get_cart_items(self) -> list[str]:
        """Return the names of all items in the cart."""
        return self.page.locator(self.ITEM_NAME).all_inner_texts()

    def get_cart_item_count(self) -> int:
        """Return the number of items in the cart."""
        return self.page.locator(self.CART_ITEM).count()

    def proceed_to_checkout(self) -> None:
        """Click the checkout button."""
        self.click(self.CHECKOUT_BUTTON)

    def continue_shopping(self) -> None:
        """Click 'Continue Shopping' to return to inventory."""
        self.click(self.CONTINUE_SHOPPING)
