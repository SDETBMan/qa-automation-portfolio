"""
config_reader.py — Central configuration resolver.

Priority (highest → lowest):
  1. Environment variables  (e.g. export TARGET=grid)
  2. config.ini values

Replaces: ConfigReader.java
"""

import configparser
import os
from pathlib import Path

# Resolve the path to config.ini relative to this file's package root
_CONFIG_PATH = Path(__file__).parent.parent / "config.ini"

_parser = configparser.ConfigParser()
_parser.read(_CONFIG_PATH)

# Flat alias map: env-var name → (section, key) in config.ini
_ENV_ALIASES: dict[str, tuple[str, str]] = {
    "TARGET":             ("execution", "target"),
    "BROWSER":            ("execution", "browser"),
    "HEADLESS":           ("execution", "headless"),
    "URL":                ("web", "url"),
    "APP_USERNAME":       ("web", "app_username"),
    "APP_PASSWORD":       ("web", "app_password"),
    "GRID_URL":           ("grid", "url"),
    "BS_USER":            ("browserstack", "user"),
    "BS_KEY":             ("browserstack", "key"),
    "HEALENIUM_PROXY":    ("healenium", "proxy_url"),
    "HEALENIUM_ENABLED":  ("healenium", "enabled"),
    "API_BASE_URL":       ("api", "base_url"),
}


def get(section: str, key: str, fallback: str = "") -> str:
    """Return a config value, checking env vars first.

    Args:
        section:  INI section name (e.g. "execution").
        key:      INI key name (e.g. "browser").
        fallback: Default value if neither env var nor INI entry exists.

    Returns:
        The resolved string value.
    """
    # 1. Check explicit env-var aliases (e.g. TARGET → execution.target)
    for env_name, (s, k) in _ENV_ALIASES.items():
        if s == section and k == key:
            env_val = os.getenv(env_name)
            if env_val is not None:
                return env_val

    # 2. Auto-convert section+key to uppercase env var (section_key → SECTION_KEY)
    auto_env = f"{section}_{key}".upper()
    env_val = os.getenv(auto_env)
    if env_val is not None:
        return env_val

    # 3. Fall back to config.ini value
    return _parser.get(section, key, fallback=fallback)


def get_bool(section: str, key: str, fallback: bool = False) -> bool:
    """Convenience wrapper that parses the value as a boolean.

    Truthy strings: "true", "1", "yes" (case-insensitive).
    """
    raw = get(section, key, fallback=str(fallback))
    return raw.strip().lower() in ("true", "1", "yes")


def is_ci() -> bool:
    """Return True when running inside a CI environment.

    GitHub Actions, GitLab CI, Jenkins, and most other CI platforms
    automatically set the CI environment variable.
    """
    return os.getenv("CI") is not None


def is_headless() -> bool:
    """Determine headless mode from config, env var, or CI detection."""
    return (
        get_bool("execution", "headless", fallback=False)
        or is_ci()
    )
