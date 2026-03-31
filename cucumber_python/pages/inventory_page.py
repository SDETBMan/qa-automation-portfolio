"""
inventory_page.py — Page Object for the SauceDemo product inventory screen.

Uses parameterized locator helpers so a single method handles any product
by name rather than requiring one method per product (avoids "God Object" bloat).

Replaces: InventoryPage.java
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage

# Product name → add-to-cart button data-test attribute mapping
# Using a dictionary here is the Page Factory / registry pattern described in
# strategy #3 (Aggressive Parameterization). One step handles every product.
_PRODUCT_BUTTON_IDS: dict[str, str] = {
    "Sauce Labs Backpack":     "add-to-cart-sauce-labs-backpack",
    "Sauce Labs Bike Light":   "add-to-cart-sauce-labs-bike-light",
    "Sauce Labs Bolt T-Shirt": "add-to-cart-sauce-labs-bolt-t-shirt",
    "Sauce Labs Fleece Jacket": "add-to-cart-sauce-labs-fleece-jacket",
    "Sauce Labs Onesie":       "add-to-cart-sauce-labs-onesie",
    "Test.allTheThings() T-Shirt (Red)": "add-to-cart-test.allthethings()-t-shirt-(red)",
}

_REMOVE_BUTTON_IDS: dict[str, str] = {
    "Sauce Labs Backpack":     "remove-sauce-labs-backpack",
    "Sauce Labs Bike Light":   "remove-sauce-labs-bike-light",
    "Sauce Labs Bolt T-Shirt": "remove-sauce-labs-bolt-t-shirt",
    "Sauce Labs Fleece Jacket": "remove-sauce-labs-fleece-jacket",
    "Sauce Labs Onesie":       "remove-sauce-labs-onesie",
    "Test.allTheThings() T-Shirt (Red)": "remove-test.allthethings()-t-shirt-(red)",
}


class InventoryPage(BasePage):
    # ── Locators ──────────────────────────────────────────────────────────────
    _CART_BADGE    = (By.CLASS_NAME, "shopping_cart_badge")
    _CART_ICON     = (By.CLASS_NAME, "shopping_cart_link")
    _CHECKOUT_BTN  = (By.ID, "checkout")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Product actions ───────────────────────────────────────────────────────

    def add_product(self, product_name: str) -> None:
        """Add a product to the cart by name."""
        btn_id = _PRODUCT_BUTTON_IDS.get(product_name)
        if not btn_id:
            raise ValueError(f"Unknown product: '{product_name}'")
        self.click((By.ID, btn_id))

    def remove_product(self, product_name: str) -> None:
        """Remove a product from the cart while on the inventory page."""
        btn_id = _REMOVE_BUTTON_IDS.get(product_name)
        if not btn_id:
            raise ValueError(f"Unknown product for removal: '{product_name}'")
        self.click((By.ID, btn_id))

    # ── Cart badge ────────────────────────────────────────────────────────────

    def get_cart_badge_count(self) -> int:
        """Return the integer shown on the cart badge; 0 if badge is absent."""
        try:
            text = self.wait.until(
                EC.visibility_of_element_located(self._CART_BADGE)
            ).text
            return int(text)
        except Exception:
            return 0

    def is_cart_empty(self) -> bool:
        try:
            self.driver.find_element(*self._CART_BADGE)
            return False
        except Exception:
            return True

    # ── Navigation ────────────────────────────────────────────────────────────

    def go_to_cart(self) -> None:
        self.click(self._CART_ICON)

    def click_checkout(self) -> None:
        self.click(self._CHECKOUT_BTN)
