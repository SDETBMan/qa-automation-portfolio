"""
driver_manager.py — Thread-safe WebDriver factory.

Manages driver lifecycle per thread so parallel scenario execution is safe.
Supports: local, grid, browserstack execution targets.
Includes graceful Healenium proxy integration via the Remote WebDriver bridge.

Replaces: DriverManager.java
"""

import threading
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.remote.webdriver import WebDriver

from utils import config_reader

# ── Thread-local storage ──────────────────────────────────────────────────────
# Each thread (parallel scenario) gets its own private driver instance.
# Python's threading.local() is the equivalent of Java's ThreadLocal<WebDriver>.
_local = threading.local()


def get_driver() -> WebDriver:
    """Return the WebDriver for the current thread, creating it on first call."""
    if not hasattr(_local, "driver") or _local.driver is None:
        _initialize_driver()
    return _local.driver


def quit_driver() -> None:
    """Close the browser and release the thread-local driver slot."""
    if hasattr(_local, "driver") and _local.driver is not None:
        try:
            _local.driver.quit()
        except Exception:
            pass
        _local.driver = None


# ── Initialization dispatcher ─────────────────────────────────────────────────

def _initialize_driver() -> None:
    target = config_reader.get("execution", "target", "local").lower()

    print("=" * 45)
    print("[INFO] DriverManager — initializing")
    print(f"[INFO] Target: {target}")
    print("=" * 45)

    dispatch = {
        "grid":         _init_grid,
        "browserstack": _init_browserstack,
    }
    init_fn = dispatch.get(target, _init_local)
    init_fn()


# ── Local driver ──────────────────────────────────────────────────────────────

def _init_local() -> None:
    browser = config_reader.get("execution", "browser", "chrome").lower()
    headless = config_reader.is_headless()

    builders = {
        "firefox": lambda: webdriver.Firefox(options=_firefox_options(headless)),
        "edge":    lambda: webdriver.Edge(options=_edge_options(headless)),
    }
    raw_driver = builders.get(browser, lambda: webdriver.Chrome(options=_chrome_options(headless)))()

    print(f"[INFO] Started local {browser} (headless={headless})")
    _local.driver = _wrap_healenium(raw_driver)


# ── Selenium Grid ─────────────────────────────────────────────────────────────

def _init_grid() -> None:
    grid_url = config_reader.get("grid", "url", "http://localhost:4444/wd/hub")
    browser = config_reader.get("execution", "browser", "chrome").lower()
    headless = config_reader.is_headless()

    options_map = {
        "firefox": _firefox_options(headless),
        "edge":    _edge_options(headless),
    }
    opts = options_map.get(browser, _chrome_options(headless))

    raw_driver = webdriver.Remote(command_executor=grid_url, options=opts)
    print(f"[INFO] Started Grid driver → {grid_url} ({browser})")
    _local.driver = _wrap_healenium(raw_driver)


# ── BrowserStack ──────────────────────────────────────────────────────────────

def _init_browserstack() -> None:
    user = config_reader.get("browserstack", "user") or os.getenv("BS_USER", "")
    key  = config_reader.get("browserstack", "key")  or os.getenv("BS_KEY", "")

    if not user or not key:
        raise RuntimeError(
            "BrowserStack credentials not found. "
            "Set BS_USER / BS_KEY secrets or BROWSERSTACK_USER / BROWSERSTACK_KEY env vars."
        )

    opts = ChromeOptions()
    opts.set_capability("bstack:options", {
        "os":          "Windows",
        "osVersion":   "11",
        "sessionName": "CucumberPythonFramework Build",
    })

    url = f"https://{user}:{key}@hub-cloud.browserstack.com/wd/hub"
    _local.driver = webdriver.Remote(command_executor=url, options=opts)
    print("[INFO] Started BrowserStack remote driver")


# ── Healenium wrapper ─────────────────────────────────────────────────────────
# Python does not have a native Healenium SDK wrapper like Java's SelfHealingDriver.
# Instead, Healenium exposes a Selenium Grid-compatible HTTP proxy on port 8085.
# When enabled, we route the driver through that proxy instead of the real Grid or
# local browser — Healenium intercepts element lookups and applies self-healing.

def _wrap_healenium(raw_driver: WebDriver) -> WebDriver:
    """Route driver through Healenium proxy if enabled; otherwise pass through."""
    enabled = config_reader.get_bool("healenium", "enabled", fallback=False)

    if not enabled:
        return raw_driver

    proxy_url = config_reader.get("healenium", "proxy_url", "http://localhost:8085")

    try:
        # Quit the raw driver — Healenium will start its own session through the proxy
        raw_driver.quit()

        browser = config_reader.get("execution", "browser", "chrome").lower()
        headless = config_reader.is_headless()

        options_map = {
            "firefox": _firefox_options(headless),
            "edge":    _edge_options(headless),
        }
        opts = options_map.get(browser, _chrome_options(headless))

        healed = webdriver.Remote(command_executor=proxy_url, options=opts)
        print(f"[INFO] Healenium self-healing active → {proxy_url}")
        return healed
    except Exception as exc:
        print(f"[WARN] Healenium proxy not reachable — using standard driver. {exc}")
        # Re-initialize a fresh raw driver since we quit the original above
        return _fallback_local_driver()


def _fallback_local_driver() -> WebDriver:
    browser = config_reader.get("execution", "browser", "chrome").lower()
    headless = config_reader.is_headless()
    builders = {
        "firefox": lambda: webdriver.Firefox(options=_firefox_options(headless)),
        "edge":    lambda: webdriver.Edge(options=_edge_options(headless)),
    }
    return builders.get(browser, lambda: webdriver.Chrome(options=_chrome_options(headless)))()


# ── Browser options builders ──────────────────────────────────────────────────

def _chrome_options(headless: bool) -> ChromeOptions:
    opts = ChromeOptions()
    opts.add_argument("--remote-allow-origins=*")
    if headless:
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--window-size=1920,1080")
    return opts


def _firefox_options(headless: bool) -> FirefoxOptions:
    opts = FirefoxOptions()
    if headless:
        opts.add_argument("-headless")
        opts.add_argument("--width=1920")
        opts.add_argument("--height=1080")
    return opts


def _edge_options(headless: bool) -> EdgeOptions:
    opts = EdgeOptions()
    if headless:
        opts.add_argument("--headless")
    return opts
