# fastapi-service

A self-contained REST API built with **FastAPI + Pydantic v2**, paired with a full
contract and integration test suite in **pytest**. A **Redis** caching layer sits
between endpoints and the in-memory store as a transparent read-through cache with
graceful fallback when Redis is unavailable.

This framework closes the full-stack loop in the portfolio: instead of testing
*someone else's* API, this service is built here and tested here -- demonstrating
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

Seeded with the SauceDemo product catalogue and user roster -- the same domain
used by the selenium-java and ai-eval suites.

Interactive Swagger UI: `http://localhost:8001/docs`

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests (no external server or API keys needed)
pytest tests/ -v --cov=app --cov-report=term-missing

# Start the live server (without Redis -- graceful fallback)
uvicorn app.main:app --reload --port 8001

# Start with Redis (optional)
docker compose up -d
uvicorn app.main:app --reload --port 8001
```

Or via the root Makefile:

```bash
make fastapi-service-test   # run pytest
make fastapi-service        # start live server on :8001
```

---

## Redis Caching

A transparent read-through cache using Redis. GET endpoints check the cache first
and populate it on a miss. Mutation endpoints (POST/PUT/DELETE) invalidate affected
keys. When Redis is unavailable, the app works identically to before.

### Cache Key Scheme

| Key | Cached By | Invalidated By |
|-----|-----------|----------------|
| `fastapi:products:list` | `GET /products` | POST, PUT, DELETE |
| `fastapi:products:{id}` | `GET /products/{id}` | PUT, DELETE that id |
| `fastapi:users:list` | `GET /users` | -- (read-only) |
| `fastapi:users:{id}` | `GET /users/{id}` | -- (read-only) |

### Graceful Degradation

- **No Redis running:** app starts normally, all endpoints return store data directly
- **Redis goes down mid-flight:** cache ops become no-ops, `[WARN]` logged
- **`is_connected()`** returns `False` when the client is absent or unreachable

### Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | *(empty -- caching disabled)* | Redis connection string |
| `REDIS_CACHE_TTL` | `300` | Cache entry TTL in seconds |

### Local Development

```bash
docker compose up -d          # redis:7-alpine on :6379
export REDIS_URL=redis://localhost:6379/0
uvicorn app.main:app --reload --port 8001
```

---

## Test Suite

| File | Tests | Scope |
|------|-------|-------|
| `test_health.py` | 2 | Liveness endpoint |
| `test_products.py` | 11 | Full CRUD: list, get, create, update, delete |
| `test_users.py` | 5 | Read-only user endpoints + 405 guard |
| `test_api_contract.py` | 4 | OpenAPI schema validation |
| `test_cache.py` | 15 | Cache hit/miss, invalidation, TTL, graceful degradation, utilities |

**37 tests total.** All tests are **fully deterministic** -- no external network
calls, no ports, no API keys required. The `reset_store` autouse fixture restores
seed data and the `_reset_cache` fixture injects a fresh `fakeredis` instance before
every test so suites are order-independent.

---

## Load Testing (k6)

`k6/load-test.js` exercises the HTTP interface under load using four scenario executors.
No Redis needed — tests run against the in-memory store.

### Scenarios

| Scenario | Executor | What it tests |
|----------|----------|---------------|
| `health_baseline` | `constant-vus` (1 VU, 30s) | Baseline latency for `GET /health` |
| `read_heavy` | `ramping-vus` (0→10→10→0 over 55s) | GET traffic across products + users endpoints |
| `crud_workflow` | `per-vu-iterations` (5 VUs × 3 iter) | Full create → read → update → delete cycle on `/products` |
| `error_handling` | `constant-vus` (2 VUs, 20s) | 404 responses for invalid IDs (products/9999, users/9999) |

### Thresholds

| Metric | Threshold |
|--------|-----------|
| `http_req_duration` p(95) | < 200ms |
| `http_req_failed` rate | < 5% |
| `checks` rate | > 95% |
| `health_req_duration` p(95) / p(99) | < 100ms / < 150ms |
| `read_req_duration` p(95) / p(99) | < 250ms / < 350ms |
| `crud_req_duration` p(95) / p(99) | < 300ms / < 500ms |

### Quick Start

```bash
# Start the server (no Redis needed)
uvicorn app.main:app --port 8001 &

# Run load tests (requires k6: https://k6.io/docs/get-started/installation/)
k6 run k6/load-test.js

# Export JSON results
k6 run k6/load-test.js --out json=k6-results.json

# Override base URL
k6 run -e BASE_URL=http://staging:8001 k6/load-test.js
```

### CI

GitHub Actions workflow: `.github/workflows/k6-load-test.yml`

- Trigger: nightly `0 11 * * *` UTC (1 hour after pytest suite) + `workflow_dispatch`
- Starts uvicorn in background, waits for health check, runs k6
- Uploads JSON results as 30-day artifact

---

## DataDog Integration

Set `DD_API_KEY` in `.env` (copy from `.env.example`) to send suite-level
metrics (`test.suite.passed`, `test.suite.failed`, `test.suite.skipped`,
`test.suite.duration_ms`) and cache metrics (`cache.hits`, `cache.misses`)
tagged `framework:fastapi-service` to DataDog.
CI remains green when the key is absent.

---

## CI

GitHub Actions workflow: `.github/workflows/fastapi-service.yml`

- Trigger: nightly `0 10 * * *` UTC + `workflow_dispatch`
- Python 3.11, pip cache
- Redis 7 Alpine service container for integration cache tests
- Uploads JUnit XML + coverage report as artifacts (30-day retention)
- DataDog CI Visibility upload (`DD_API_KEY` secret, optional)
