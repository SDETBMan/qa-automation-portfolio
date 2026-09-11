"""
schemas.py — Pydantic models for Stagehand extract() JSON schemas.

Each model defines the expected structure of data extracted by the
AI-driven runner. The `to_json_schema()` helper converts a Pydantic
model to a plain dict suitable for Stagehand's extract() instruction.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginResult(BaseModel):
    """Result of a login attempt extracted from the page."""

    logged_in: bool = Field(description="Whether the login was successful")
    current_url: str = Field(description="The URL after the login attempt")
    error_message: str | None = Field(
        default=None,
        description="Error message displayed on failed login",
    )


class ProductItem(BaseModel):
    """A single product from the inventory page."""

    name: str = Field(description="Product name")
    price: str = Field(description="Product price including dollar sign")


class ProductList(BaseModel):
    """List of products extracted from the inventory page."""

    products: list[ProductItem] = Field(description="All visible products")
    count: int = Field(description="Total number of products")


class CartState(BaseModel):
    """Current state of the shopping cart."""

    items: list[str] = Field(description="Names of items in the cart")
    item_count: int = Field(description="Number of items in the cart")
    badge_count: int = Field(description="Number shown on the cart badge")


class CheckoutResult(BaseModel):
    """Result of the checkout flow."""

    completed: bool = Field(description="Whether checkout completed successfully")
    confirmation_text: str | None = Field(
        default=None,
        description="Order confirmation header text",
    )
    total: str | None = Field(
        default=None,
        description="Order total price string",
    )


def to_json_schema(model: type[BaseModel]) -> dict:
    """Convert a Pydantic model to a JSON schema dict for Stagehand extract()."""
    return model.model_json_schema()
