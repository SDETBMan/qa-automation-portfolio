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
        self.click(self._LOGOUT_LINK)
