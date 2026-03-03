# fastapi-service

A self-contained REST API built with **FastAPI + Pydantic v2**, paired with a full
contract and integration test suite in **pytest**.

This framework closes the full-stack loop in the portfolio: instead of testing
*someone else's* API, this service is built here and tested here — demonstrating
API-first quality ownership relevant to SDET, QA Lead, and AI QA roles.

---

## API Overview

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| GET | `/products` | List all products |
| GET | `/products/{id}` | Get product by ID |
| POST | `/products` | Create product |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Delete product (204) |
| GET | `/users` | List all users (read-only) |
| GET | `/users/{id}` | Get user by ID |

Seeded with the SauceDemo product catalogue and user roster — the same domain
used by the selenium-java and ai-eval suites.

Interactive Swagger UI: `http://localhost:8001/docs`

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests (no external server or API keys needed)
pytest tests/ -v --cov=app --cov-report=term-missing

# Start the live server
uvicorn app.main:app --reload --port 8001
```

Or via the root Makefile:

```bash
make fastapi-service-test   # run pytest
make fastapi-service        # start live server on :8001
```

---

## Test Suite

| File | Tests | Scope |
|------|-------|-------|
| `test_health.py` | 2 | Liveness endpoint |
| `test_products.py` | 11 | Full CRUD: list, get, create, update, delete |
| `test_users.py` | 5 | Read-only user endpoints + 405 guard |
| `test_api_contract.py` | 4 | OpenAPI schema validation |

All tests are **fully deterministic** — no external network calls, no ports,
no API keys required. The `reset_store` autouse fixture restores seed data
before every test so suites are order-independent.

---

## DataDog Integration

Set `DD_API_KEY` in `.env` (copy from `.env.example`) to send suite-level
metrics (`test.suite.passed`, `test.suite.failed`, `test.suite.skipped`,
`test.suite.duration_ms`) tagged `framework:fastapi-service` to DataDog.
CI remains green when the key is absent.

---

## CI

GitHub Actions workflow: `.github/workflows/fastapi-service.yml`

- Trigger: nightly `0 10 * * *` UTC + `workflow_dispatch`
- Python 3.11, pip cache
- Uploads JUnit XML + coverage report as artifacts (30-day retention)
- DataDog CI Visibility upload (`DD_API_KEY` secret, optional)
