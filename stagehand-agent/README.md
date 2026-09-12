# stagehand-agent

Side-by-side comparison of **traditional Playwright automation** vs **AI-driven Stagehand** on the same SauceDemo scenarios — measuring execution time, token usage, and reliability.

[Stagehand](https://github.com/browserbase/stagehand) is Browserbase's open-source SDK for AI-driven browser automation. Instead of writing explicit selectors and POM actions, you describe intent in natural language and the LLM generates browser interactions via `act()`, `observe()`, and `extract()` APIs.

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI-driven automation | Stagehand SDK · Browserbase cloud browser |
| Traditional automation | Playwright (Python sync API) |
| Page Object Model | BasePage → LoginPage · InventoryPage · CartPage · CheckoutPage |
| Data extraction schemas | Pydantic v2 models → JSON schema for `extract()` |
| Reporting | JSON + Markdown comparison reports |
| Observability | DataDog v2 GAUGE metrics (graceful skip) |
| Test runner | Pytest with `pytest-asyncio` |
| Language | Python 3.11+ |

## Scenarios

| # | Scenario | Traditional (POM) | AI-Driven (Stagehand) |
|---|----------|-------------------|----------------------|
| 1 | Login | `LoginPage.login_as()` + URL assertion | `act("type username...")` → `extract(LoginResult)` |
| 2 | Browse Inventory | `InventoryPage.get_product_count()` | `extract(ProductList)` |
| 3 | Add to Cart | `InventoryPage.add_item_to_cart()` | `act("click Add to Cart...")` → `extract(CartState)` |
| 4 | Checkout | POM chain: 3 page objects | Sequential `act()` calls → `extract(CheckoutResult)` |

## Directory Structure

```
stagehand-agent/
├── run.py                     # CLI entry point (argparse, dotenv)
├── requirements.txt
├── .env.example
├── pytest.ini
├── datasets/
│   ├── users.json             # SauceDemo credentials
│   └── products.json          # Product catalog
├── pages/                     # Traditional Playwright POM
│   ├── base_page.py           # BasePage: click, type_text, get_text, wait_for_visibility
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── cart_page.py
│   └── checkout_page.py
├── agent/                     # AI-driven Stagehand module
│   ├── stagehand_runner.py    # StagehandRunner: login, browse, cart, checkout via act/extract
│   └── schemas.py             # Pydantic models for extract() JSON schemas
├── traditional/               # Deterministic Playwright module
│   └── playwright_runner.py   # PlaywrightRunner: same 4 scenarios via POM
├── comparison/                # Metrics and orchestration
│   ├── metrics.py             # ScenarioResult, ComparisonReport dataclasses
│   ├── runner.py              # Orchestrator: runs both sides, collects metrics
│   └── reporter.py            # JSON + Markdown report generator
├── utils/
│   └── datadog_reporter.py    # DataDog v2 GAUGE metrics (graceful skip)
├── output/
│   └── .gitkeep
└── tests/
    ├── conftest.py            # Fake env vars, mock fixtures
    ├── test_schemas.py
    ├── test_metrics.py
    ├── test_playwright_runner.py
    ├── test_stagehand_runner.py
    ├── test_reporter.py
    └── test_comparison_runner.py
```

## How to Run

### Unit tests (no API keys needed)

```bash
cd stagehand-agent
pip install -r requirements.txt
pip install pytest pytest-asyncio
pytest tests/ -v
```

### Traditional mode (local browser, no API keys)

```bash
cd stagehand-agent
pip install -r requirements.txt
python run.py --mode traditional
```

### AI-driven mode (requires Browserbase + model API keys)

```bash
cd stagehand-agent
cp .env.example .env  # fill in BROWSERBASE_API_KEY, BROWSERBASE_PROJECT_ID, MODEL_API_KEY
python run.py --mode ai
```

### Full comparison

```bash
python run.py --mode compare --format both --output output/comparison
```

### CLI options

```
--mode       traditional | ai | compare (default: compare)
--scenarios  login | inventory | cart | checkout | all (default: all)
--output     output file path without extension (default: output/comparison)
--format     json | markdown | both (default: both)
```

## DataDog Metrics

| Metric | Description |
|---|---|
| `stagehand.traditional.duration_ms` | Traditional Playwright total duration |
| `stagehand.ai_driven.duration_ms` | AI-driven Stagehand total duration |
| `stagehand.ai_driven.tokens_used` | Total LLM tokens consumed |
| `stagehand.speed_ratio` | AI duration / Traditional duration |
| `stagehand.scenarios_passed` | Number of passing scenarios |
| `stagehand.scenarios_total` | Total scenarios run |

All metrics tagged with `framework:stagehand-agent`, `service:qa-automation-portfolio`, `env:ci`. Skips gracefully when `DD_API_KEY` is absent.
