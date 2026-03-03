"""
models.py — Pydantic v2 data models for the FastAPI service.

Three models:
  Product       — full product record (id, name, price, inventory)
  ProductCreate — request body for POST /products (no id field)
  User          — full user record (id, username, role)
"""

from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    price: float
    inventory: int


class ProductCreate(BaseModel):
    name: str
    price: float
    inventory: int = 0


class User(BaseModel):
    id: int
    username: str
    role: str  # "standard_user" | "admin"
