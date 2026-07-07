# Pact Consumer — Contract Tests

Consumer-driven contract tests (pact-js v13) validating the `fastapi-service` API contract.

## Contracts

| Interaction | Method | Path | Expected |
|---|---|---|---|
| Health check | GET | `/health` | 200 — `{ status: "ok" }` |
| List products | GET | `/products` | 200 — array of Product |
| Get product | GET | `/products/{id}` | 200 — Product |
| Product not found | GET | `/products/9999` | 404 — `{ detail: "..." }` |
| Create product | POST | `/products` | 201 — Product with `id` |
| List users | GET | `/users` | 200 — array of User |
| Get user | GET | `/users/{id}` | 200 — User |
| User not found | GET | `/users/9999` | 404 — `{ detail: "..." }` |

## Quick Start

```bash
npm install
npm test
# Pact files written to pacts/
```

## Provider Verification

```bash
cd ../fastapi-service
pip install -r requirements.txt
pytest tests/test_pact_provider.py -v
```

## CI

The `pact.yml` workflow runs consumer tests, then verifies the provider against the generated pact files.
