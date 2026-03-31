"""
auth_steps.py — Step definitions for all authentication scenarios.

Domain: Login, Logout, MFA, Session (auth_steps owns anything identity-related).

Design decisions applied:
  #1 Declarative Gherkin — "I login with valid credentials" hides the how.
     The actual username/password lives in config or the Login Task, not Gherkin.
  #2 Domain-Object Organization — all auth steps live here, not scattered across files.
  #4 Screenplay Pattern — complex flows delegated to tasks/login_task.py.

Replaces: LoginSteps.java + DashboardSteps.java (logout)
"""

from behave import given, when, then
from behave.runner import Context

from utils import driver_manager, config_reader
from utils.tasks import LoginTask
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage


# ── Shared context helpers ────────────────────────────────────────────────────

def _login_page(context: Context) -> LoginPage:
    return LoginPage(driver_manager.get_driver())


def _dashboard_page(context: Context) -> DashboardPage:
    return DashboardPage(driver_manager.get_driver())


# ── Given steps ───────────────────────────────────────────────────────────────

@given("I am on the SauceDemo login page")
def step_navigate_to_login(context: Context) -> None:
    url = config_reader.get("web", "url", "https://www.saucedemo.com/")
    driver_manager.get_driver().get(url)
    assert "saucedemo" in driver_manager.get_driver().current_url, (
        f"Not on login page — current URL: {driver_manager.get_driver().current_url}"
    )


@given('I am logged in as "{username}"')
def step_logged_in_as(context: Context, username: str) -> None:
    """Declarative precondition — delegates entire login flow to the Login Task."""
    url = config_reader.get("web", "url", "https://www.saucedemo.com/")
    driver_manager.get_driver().get(url)
    password = config_reader.get("web", "app_password", "secret_sauce")
    LoginTask(driver_manager.get_driver()).perform(username, password)


# ── When steps ────────────────────────────────────────────────────────────────

@when("I login with valid credentials")
def step_login_valid(context: Context) -> None:
    """Declarative: reads credentials from config — Gherkin stays data-free."""
    username = config_reader.get("web", "app_username", "standard_user")
    password = config_reader.get("web", "app_password", "secret_sauce")
    LoginTask(driver_manager.get_driver()).perform(username, password)


@when("I login with invalid credentials")
def step_login_invalid(context: Context) -> None:
    locked = config_reader.get("web", "locked_out_username", "locked_out_user")
    _login_page(context).login(locked, "wrong_password")


@when('I login as "{username}"')
def step_login_as_user(context: Context, username: str) -> None:
    """Scenario Outline variant — username from Examples table.

    Uses LoginPage.login() directly so the @then step can verify the outcome
    (success OR failure) without LoginTask's success assertion interfering.
    """
    password = config_reader.get("web", "app_password", "secret_sauce")
    LoginPage(driver_manager.get_driver()).login(username, password)


@when("I logout")
def step_logout(context: Context) -> None:
    _dashboard_page(context).open_menu_and_logout()


@when('I navigate directly to "{path}"')
def step_navigate_direct(context: Context, path: str) -> None:
    base = config_reader.get("web", "url", "https://www.saucedemo.com/")
    driver_manager.get_driver().get(f"{base.rstrip('/')}/{path}")


# ── Then steps ────────────────────────────────────────────────────────────────

@then("I should be on the Products page")
def step_assert_products_page(context: Context) -> None:
    page = _dashboard_page(context)
    assert page.is_products_page_displayed(), "Products page not displayed"
    assert page.get_page_title() == "Products", (
        f"Expected 'Products', got '{page.get_page_title()}'"
    )


@then("I should see an authentication error")
def step_assert_auth_error(context: Context) -> None:
    assert _login_page(context).is_error_displayed(), (
        "Expected an error message but none was displayed"
    )


@then('I should see the "{outcome}" state')
def step_assert_login_outcome(context: Context, outcome: str) -> None:
    """Strategy #3 — one step handles both success and failure outcomes."""
    if outcome.lower() == "success":
        step_assert_products_page(context)
    else:
        step_assert_auth_error(context)


@then("I should be returned to the login page")
def step_assert_login_page(context: Context) -> None:
    assert _login_page(context).is_login_button_displayed(), (
        "Expected to be on login page but login button not found"
    )


@then('the page header should display "{title}"')
def step_assert_header(context: Context, title: str) -> None:
    actual = _dashboard_page(context).get_page_title()
    assert actual == title, f"Expected header '{title}', got '{actual}'"


@then("the cart icon should be visible")
def step_assert_cart_icon(context: Context) -> None:
    assert _dashboard_page(context).is_cart_icon_visible(), (
        "Cart icon not visible on dashboard"
    )
