"""
security_steps.py — Step definitions for security test scenarios.

Domain: SQL injection, XSS, brute-force resilience, HTTP security headers.

Replaces: SecuritySteps.java
"""

import requests
from behave import when, then
from behave.runner import Context

from utils import driver_manager, config_reader
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

# SQL injection payload — verifies the app rejects it gracefully
_SQL_INJECTION = "' OR '1'='1' --"

# XSS payload — verifies the browser does not execute it
_XSS_PAYLOAD = "<script>document.title='xss'</script>"

# Headers that indicate a security-conscious application
_REQUIRED_HEADERS = [
    "x-frame-options",
    "x-content-type-options",
]


def _login_page(context: Context) -> LoginPage:
    return LoginPage(driver_manager.get_driver())


def _dashboard_page(context: Context) -> DashboardPage:
    return DashboardPage(driver_manager.get_driver())


# ── When steps ────────────────────────────────────────────────────────────────

@when("I attempt to login with SQL injection payload")
def step_sql_injection(context: Context) -> None:
    _login_page(context).login(_SQL_INJECTION, "anything")


@when("I attempt to login with XSS payload")
def step_xss(context: Context) -> None:
    _login_page(context).login(_XSS_PAYLOAD, "anything")


@when("I submit {count:d} failed login attempts")
def step_failed_attempts(context: Context, count: int) -> None:
    page = _login_page(context)
    for _ in range(count):
        page.login("wrong_user", "wrong_pass")


# ── Then steps ────────────────────────────────────────────────────────────────

@then("the error message should not expose system internals")
def step_assert_no_system_internals(context: Context) -> None:
    error_text = _login_page(context).get_error_text().lower()
    forbidden = ["sql", "exception", "stack trace", "org.", "com.", "java"]
    for keyword in forbidden:
        assert keyword not in error_text, (
            f"Error message exposes system internals — contains '{keyword}': {error_text}"
        )


@then('the page title should not contain "{text}"')
def step_assert_title_not_contain(context: Context, text: str) -> None:
    title = driver_manager.get_driver().title
    assert text.lower() not in title.lower(), (
        f"Page title contains '{text}' — possible XSS execution: {title}"
    )


@then("the security response headers should be present")
def step_assert_security_headers(context: Context) -> None:
    """Fetch the page via requests (not the browser) to inspect HTTP headers."""
    url = config_reader.get("web", "url", "https://www.saucedemo.com/")
    response = requests.get(url, timeout=10)
    response_headers_lower = {k.lower(): v for k, v in response.headers.items()}

    missing = [h for h in _REQUIRED_HEADERS if h not in response_headers_lower]
    assert not missing, (
        f"Missing security headers: {missing}. "
        f"Present headers: {list(response_headers_lower.keys())}"
    )
