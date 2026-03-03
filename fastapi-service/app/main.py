"""
main.py — FastAPI application with product and user endpoints.

Routes:
  GET  /health           — liveness check
  GET  /products         — list all products
  GET  /products/{id}    — get product by id
  POST /products         — create product (returns 201)
  PUT  /products/{id}    — update product
  DELETE /products/{id}  — delete product (returns 204)
  GET  /users            — list all users
  GET  /users/{id}       — get user by id

All state lives in the module-level store singleton (app/store.py).
Users are read-only; POST /users returns 405 Method Not Allowed.
"""

from fastapi import FastAPI, HTTPException, Response

from app.models import Product, ProductCreate, User
from app.store import store

app = FastAPI(
    title="QA Portfolio — FastAPI Service",
    description="SauceDemo-seeded REST API used for contract and integration testing.",
    version="1.0.0",
)


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# ── Products ───────────────────────────────────────────────────────────────────

@app.get("/products", response_model=list[Product], tags=["products"])
def list_products() -> list[Product]:
    return list(store.products.values())


@app.get("/products/{product_id}", response_model=Product, tags=["products"])
def get_product(product_id: int) -> Product:
    product = store.products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product


@app.post("/products", response_model=Product, status_code=201, tags=["products"])
def create_product(body: ProductCreate) -> Product:
    new_id = store._next_id
    store._next_id += 1
    product = Product(id=new_id, **body.model_dump())
    store.products[new_id] = product
    return product


@app.put("/products/{product_id}", response_model=Product, tags=["products"])
def update_product(product_id: int, body: ProductCreate) -> Product:
    if product_id not in store.products:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    updated = Product(id=product_id, **body.model_dump())
    store.products[product_id] = updated
    return updated


@app.delete("/products/{product_id}", status_code=204, tags=["products"])
def delete_product(product_id: int) -> Response:
    if product_id not in store.products:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    del store.products[product_id]
    return Response(status_code=204)


# ── Users (read-only) ──────────────────────────────────────────────────────────

@app.get("/users", response_model=list[User], tags=["users"])
def list_users() -> list[User]:
    return list(store.users.values())


@app.get("/users/{user_id}", response_model=User, tags=["users"])
def get_user(user_id: int) -> User:
    user = store.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user
