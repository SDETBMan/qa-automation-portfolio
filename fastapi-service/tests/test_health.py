"""
test_health.py — Tests for GET /health.

2 tests:
  - Returns HTTP 200
  - Response body is {"status": "ok"}
"""


def test_health_status_code(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_body(client):
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
