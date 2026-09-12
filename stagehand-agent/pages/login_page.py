"""
login_page.py — Page Object for the SauceDemo login page.

Selectors match cypress/cypress/pages/LoginPage.ts.
"""

from __future__ import annotations

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Login page interactions for SauceDemo."""

    # Selectors
    USERNAME_INPUT = "#user-name"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_MESSAGE = "[data-test='error']"

    def navigate(self, base_url: str = "https://www.saucedemo.com") -> None:
        """Navigate to the login page."""
        self.page.goto(base_url)

    def login_as(self, username: str, password: str) -> None:
        """Fill credentials and submit the login form."""
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self) -> str:
        """Return the text of the login error banner."""
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        """Return True if the error message is visible."""
        return self.is_element_visible(self.ERROR_MESSAGE)
