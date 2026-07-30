"""
main.py -- FastAPI application with product and user endpoints.

Routes:
  GET  /health           -- liveness check
  GET  /products         -- list all products
  GET  /products/{id}    -- get product by id
  POST /products         -- create product (returns 201)
  PUT  /products/{id}    -- update product
  DELETE /products/{id}  -- delete product (returns 204)
  GET  /users            -- list all users
  GET  /users/{id}       -- get user by id

All state lives in the module-level store singleton (app/store.py).
Redis caching (app/cache.py) sits between endpoints and the store as a
transparent read-through layer.  When Redis is unavailable, every
endpoint works identically to before.
Users are read-only; POST /users returns 405 Method Not Allowed.
"""

import json

from fastapi import FastAPI, HTTPException, Response

from app.cache import cache
from app.models import Product, ProductCreate, User
from app.store import store

app = FastAPI(
    title="QA Portfolio — FastAPI Service",
    description="SauceDemo-seeded REST API used for contract and integration testing.",
    version="1.0.0",
)


# -- Health ---------------------------------------------------------------

@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# -- Products -------------------------------------------------------------

@app.get("/products", response_model=list[Product], tags=["products"])
def list_products() -> list[Product]:
    cached = cache.get("products:list")
    if cached is not None:
        return [Product(**p) for p in json.loads(cached)]

    products = list(store.products.values())
    cache.set("products:list", [p.model_dump() for p in products])
    return products


@app.get("/products/{product_id}", response_model=Product, tags=["products"])
def get_product(product_id: int) -> Product:
    cached = cache.get(f"products:{product_id}")
    if cached is not None:
        return Product(**json.loads(cached))

    product = store.products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    cache.set(f"products:{product_id}", product.model_dump())
    return product


@app.post("/products", response_model=Product, status_code=201, tags=["products"])
def create_product(body: ProductCreate) -> Product:
    new_id = store._next_id
    store._next_id += 1
    product = Product(id=new_id, **body.model_dump())
    store.products[new_id] = product
    cache.delete("products:list")
    return product


@app.put("/products/{product_id}", response_model=Product, tags=["products"])
def update_product(product_id: int, body: ProductCreate) -> Product:
    if product_id not in store.products:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    updated = Product(id=product_id, **body.model_dump())
    store.products[product_id] = updated
    cache.delete("products:list")
    cache.delete(f"products:{product_id}")
    return updated


@app.delete("/products/{product_id}", status_code=204, tags=["products"])
def delete_product(product_id: int) -> Response:
    if product_id not in store.products:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    del store.products[product_id]
    cache.delete("products:list")
    cache.delete(f"products:{product_id}")
    return Response(status_code=204)


# -- Users (read-only) ----------------------------------------------------

@app.get("/users", response_model=list[User], tags=["users"])
def list_users() -> list[User]:
    cached = cache.get("users:list")
    if cached is not None:
        return [User(**u) for u in json.loads(cached)]

    users = list(store.users.values())
    cache.set("users:list", [u.model_dump() for u in users])
    return users


@app.get("/users/{user_id}", response_model=User, tags=["users"])
def get_user(user_id: int) -> User:
    cached = cache.get(f"users:{user_id}")
    if cached is not None:
        return User(**json.loads(cached))

    user = store.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    cache.set(f"users:{user_id}", user.model_dump())
    return user
