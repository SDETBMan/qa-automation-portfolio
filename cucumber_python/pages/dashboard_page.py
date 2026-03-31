"""
dashboard_page.py — Page Object for the SauceDemo inventory/dashboard screen.

Replaces: DashboardPage.java
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from pages.base_page import BasePage


class DashboardPage(BasePage):
    # ── Locators ──────────────────────────────────────────────────────────────
    _PRODUCTS_TITLE  = (By.CLASS_NAME, "title")
    _CART_ICON       = (By.CLASS_NAME, "shopping_cart_link")
    _BURGER_MENU     = (By.ID, "react-burger-menu-btn")
    _LOGOUT_LINK     = (By.ID, "logout_sidebar_link")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def get_page_title(self) -> str:
        return self.get_text(self._PRODUCTS_TITLE)

    def is_products_page_displayed(self) -> bool:
        return self.is_element_present(self._PRODUCTS_TITLE)

    def is_cart_icon_visible(self) -> bool:
        return self.is_element_present(self._CART_ICON)

    def open_menu_and_logout(self) -> None:
        self.click(self._BURGER_MENU)
        # SauceDemo's burger menu uses a CSS slide-in animation.  The logout
        # link is technically in the DOM and "enabled" before the animation
        # completes, so element_to_be_clickable fires while the element is still
        # off-screen.  javascript_click bypasses coordinate-based dispatch and
        # fires the click event directly on the element.
        self.javascript_click(self._LOGOUT_LINK)
