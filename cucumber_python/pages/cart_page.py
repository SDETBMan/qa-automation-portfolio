"""
cart_page.py — Page Object for the SauceDemo shopping cart screen.

Replaces: CartPage.java
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class CartPage(BasePage):
    # ── Locators ──────────────────────────────────────────────────────────────
    _CART_ITEMS    = (By.CLASS_NAME, "cart_item")
    _ITEM_NAMES    = (By.CLASS_NAME, "inventory_item_name")
    _CART_BADGE    = (By.CLASS_NAME, "shopping_cart_badge")
    _CHECKOUT_BTN  = (By.ID, "checkout")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def get_cart_badge_text(self) -> str:
        try:
            return self.driver.find_element(*self._CART_BADGE).text
        except Exception:
            return ""

    def get_item_names(self) -> list[str]:
        """Return a list of all product names currently in the cart."""
        try:
            elements = self.wait.until(
                EC.presence_of_all_elements_located(self._ITEM_NAMES)
            )
            return [el.text for el in elements]
        except Exception:
            return []

    def is_item_in_cart(self, product_name: str) -> bool:
        return product_name in self.get_item_names()

    def click_checkout(self) -> None:
        self.javascript_click(self._CHECKOUT_BTN)

    def is_on_checkout_page(self) -> bool:
        return self.wait_for_url_contains("checkout")
