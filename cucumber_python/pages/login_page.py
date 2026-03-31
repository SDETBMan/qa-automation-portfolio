"""
login_page.py — Page Object for the SauceDemo login screen.

Exposes both granular methods (for Gherkin step mapping) and a composite
login() helper (for setup-noise scenarios where login is a precondition).

Replaces: LoginPage.java
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from pages.base_page import BasePage


class LoginPage(BasePage):
    # ── Locators ──────────────────────────────────────────────────────────────
    _USERNAME_FIELD = (By.ID, "user-name")
    _PASSWORD_FIELD = (By.ID, "password")
    _LOGIN_BUTTON   = (By.ID, "login-button")
    _ERROR_MESSAGE  = (By.CSS_SELECTOR, "[data-test='error']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    # ── Granular actions (used by Cucumber steps) ─────────────────────────────

    def enter_username(self, username: str) -> None:
        self.send_keys(self._USERNAME_FIELD, username)

    def enter_password(self, password: str) -> None:
        self.send_keys(self._PASSWORD_FIELD, password)

    def click_login(self) -> None:
        self.click(self._LOGIN_BUTTON)

    # ── Composite helper (used by Screenplay Login task and hooks) ────────────

    def login(self, username: str, password: str) -> None:
        """Enter credentials and submit in one call."""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    # ── Assertions ────────────────────────────────────────────────────────────

    def is_error_displayed(self) -> bool:
        return self.is_element_present(self._ERROR_MESSAGE)

    def get_error_text(self) -> str:
        try:
            return self.get_text(self._ERROR_MESSAGE)
        except Exception:
            return ""

    def is_login_button_displayed(self) -> bool:
        return self.is_element_present(self._LOGIN_BUTTON)
