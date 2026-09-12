"""
checkout_page.py — Page Object for the SauceDemo checkout flow.

Covers checkout step one (info form), step two (overview), and
the completion page. Selectors match cypress/cypress/pages/CheckoutPage.ts.
"""

from __future__ import annotations

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """Checkout flow interactions for SauceDemo."""

    # Step One — Information
    FIRST_NAME = "[data-test='firstName']"
    LAST_NAME = "[data-test='lastName']"
    POSTAL_CODE = "[data-test='postalCode']"
    CONTINUE_BUTTON = "[data-test='continue']"
    ERROR_MESSAGE = "[data-test='error']"

    # Step Two — Overview
    FINISH_BUTTON = "[data-test='finish']"
    SUMMARY_TOTAL = ".summary_total_label"

    # Complete
    COMPLETE_HEADER = ".complete-header"

    def fill_info(self, first_name: str, last_name: str, postal_code: str) -> None:
        """Fill in the checkout information form."""
        self.type_text(self.FIRST_NAME, first_name)
        self.type_text(self.LAST_NAME, last_name)
        self.type_text(self.POSTAL_CODE, postal_code)

    def continue_to_overview(self) -> None:
        """Click 'Continue' to proceed to the order overview."""
        self.click(self.CONTINUE_BUTTON)

    def finish_checkout(self) -> None:
        """Click 'Finish' to complete the order."""
        self.click(self.FINISH_BUTTON)

    def get_confirmation_header(self) -> str:
        """Return the text of the order completion header."""
        return self.get_text(self.COMPLETE_HEADER)

    def get_summary_total(self) -> str:
        """Return the total price string from the overview page."""
        return self.get_text(self.SUMMARY_TOTAL)

    def is_error_displayed(self) -> bool:
        """Return True if a checkout error message is visible."""
        return self.is_element_visible(self.ERROR_MESSAGE)
