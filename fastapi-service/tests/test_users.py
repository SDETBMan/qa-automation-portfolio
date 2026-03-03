"""
test_users.py — Tests for the read-only /users endpoints.

5 tests covering:
  - List returns all 5 seeded users
  - List response items contain expected fields
  - Get by valid id → 200 + correct data
  - Get by invalid id → 404
  - POST /users → 405 Method Not Allowed (users are read-only)
"""


def test_list_users_count(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_list_users_fields(client):
    users = client.get("/users").json()
    first = users[0]
    assert set(first.keys()) == {"id", "username", "role"}


def test_get_user_valid_id(client):
    response = client.get("/users/5")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 5
    assert data["username"] == "admin"
    assert data["role"] == "admin"


def test_get_user_invalid_id(client):
    response = client.get("/users/9999")
    assert response.status_code == 404


def test_post_users_method_not_allowed(client):
    response = client.post("/users", json={"username": "new_user", "role": "standard_user"})
    assert response.status_code == 405
