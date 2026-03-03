"""
test_products.py — Integration tests for the /products CRUD endpoints.

10 tests covering:
  - List returns all 6 seeded products
  - List response items contain expected fields
  - Get by valid id → 200 + correct data
  - Get by invalid id → 404
  - Create → 201, body round-trips, next GET returns it
  - Update → 200, fields changed, other fields unchanged
  - Delete → 204, subsequent GET → 404
  - Delete non-existent id → 404
"""


def test_list_products_count(client):
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) == 6


def test_list_products_fields(client):
    products = client.get("/products").json()
    first = products[0]
    assert set(first.keys()) == {"id", "name", "price", "inventory"}


def test_get_product_valid_id(client):
    response = client.get("/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Sauce Labs Backpack"
    assert data["price"] == 29.99
    assert data["inventory"] == 10


def test_get_product_invalid_id(client):
    response = client.get("/products/9999")
    assert response.status_code == 404


def test_create_product_returns_201(client):
    payload = {"name": "New Widget", "price": 19.99, "inventory": 5}
    response = client.post("/products", json=payload)
    assert response.status_code == 201


def test_create_product_body_round_trips(client):
    payload = {"name": "New Widget", "price": 19.99, "inventory": 5}
    created = client.post("/products", json=payload).json()
    assert created["name"] == payload["name"]
    assert created["price"] == payload["price"]
    assert created["inventory"] == payload["inventory"]
    assert "id" in created


def test_create_product_retrievable(client):
    payload = {"name": "New Widget", "price": 19.99, "inventory": 5}
    created = client.post("/products", json=payload).json()
    fetch = client.get(f"/products/{created['id']}")
    assert fetch.status_code == 200
    assert fetch.json()["name"] == "New Widget"


def test_update_product(client):
    payload = {"name": "Updated Backpack", "price": 34.99, "inventory": 8}
    response = client.put("/products/1", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Backpack"
    assert data["price"] == 34.99
    assert data["inventory"] == 8
    assert data["id"] == 1


def test_delete_product_returns_204(client):
    response = client.delete("/products/1")
    assert response.status_code == 204


def test_delete_product_then_get_returns_404(client):
    client.delete("/products/1")
    response = client.get("/products/1")
    assert response.status_code == 404


def test_delete_nonexistent_product(client):
    response = client.delete("/products/9999")
    assert response.status_code == 404
