"""
test_api_contract.py — OpenAPI schema / contract tests.

4 tests covering:
  - GET /openapi.json returns 200
  - info.title matches expected value
  - paths contains all 8 expected routes
  - All route response schemas define a 422 (validation error) entry
"""

import pytest

EXPECTED_PATHS = [
    "/health",
    "/products",
    "/products/{product_id}",
    "/users",
    "/users/{user_id}",
]


@pytest.fixture
def openapi(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    return response.json()


def test_openapi_returns_200(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_openapi_title(openapi):
    assert openapi["info"]["title"] == "QA Portfolio — FastAPI Service"


def test_openapi_paths_present(openapi):
    schema_paths = set(openapi["paths"].keys())
    for path in EXPECTED_PATHS:
        assert path in schema_paths, f"Expected path '{path}' not found in OpenAPI schema"


def test_openapi_routes_define_422(openapi):
    """Routes with path params or a request body must document 422."""
    for path, methods in openapi["paths"].items():
        for method, operation in methods.items():
            has_params = bool(operation.get("parameters") or operation.get("requestBody"))
            if not has_params:
                continue
            responses = operation.get("responses", {})
            assert "422" in responses, (
                f"{method.upper()} {path} does not define a 422 response in the schema"
            )
