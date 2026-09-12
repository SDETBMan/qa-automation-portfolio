"""Tests for agent/schemas.py — Pydantic model validation and JSON schema generation."""

import pytest

from agent.schemas import (
    CartState,
    CheckoutResult,
    LoginResult,
    ProductItem,
    ProductList,
    to_json_schema,
)


class TestLoginResult:
    def test_successful_login(self):
        result = LoginResult(
            logged_in=True,
            current_url="https://www.saucedemo.com/inventory.html",
        )
        assert result.logged_in is True
        assert result.error_message is None

    def test_failed_login(self):
        result = LoginResult(
            logged_in=False,
            current_url="https://www.saucedemo.com/",
            error_message="Username and password do not match",
        )
        assert result.logged_in is False
        assert "do not match" in result.error_message


class TestProductList:
    def test_product_list_with_items(self):
        products = ProductList(
            products=[
                ProductItem(name="Sauce Labs Backpack", price="$29.99"),
                ProductItem(name="Sauce Labs Bike Light", price="$9.99"),
            ],
            count=2,
        )
        assert len(products.products) == 2
        assert products.count == 2

    def test_empty_product_list(self):
        products = ProductList(products=[], count=0)
        assert products.count == 0


class TestCartState:
    def test_cart_with_items(self):
        cart = CartState(
            items=["Sauce Labs Backpack"],
            item_count=1,
            badge_count=1,
        )
        assert cart.item_count == 1
        assert cart.badge_count == 1

    def test_empty_cart(self):
        cart = CartState(items=[], item_count=0, badge_count=0)
        assert cart.items == []


class TestCheckoutResult:
    def test_successful_checkout(self):
        result = CheckoutResult(
            completed=True,
            confirmation_text="Thank you for your order!",
            total="Total: $29.99",
        )
        assert result.completed is True
        assert "Thank you" in result.confirmation_text

    def test_failed_checkout(self):
        result = CheckoutResult(completed=False)
        assert result.confirmation_text is None
        assert result.total is None


class TestToJsonSchema:
    def test_login_result_schema(self):
        schema = to_json_schema(LoginResult)
        assert "properties" in schema
        assert "logged_in" in schema["properties"]
        assert "current_url" in schema["properties"]

    def test_product_list_schema(self):
        schema = to_json_schema(ProductList)
        assert "properties" in schema
        assert "products" in schema["properties"]
        assert "count" in schema["properties"]

    def test_cart_state_schema(self):
        schema = to_json_schema(CartState)
        assert "properties" in schema
        assert "items" in schema["properties"]

    def test_checkout_result_schema(self):
        schema = to_json_schema(CheckoutResult)
        assert "properties" in schema
        assert "completed" in schema["properties"]

    @pytest.mark.smoke
    def test_all_schemas_have_required_type(self):
        for model in [LoginResult, ProductList, CartState, CheckoutResult]:
            schema = to_json_schema(model)
            assert schema.get("type") == "object"
