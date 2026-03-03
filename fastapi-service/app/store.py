"""
store.py — In-memory singleton store for products and users.

The Store class is instantiated once at module load as `store`.
Call store.reset() to restore the seed data between tests.

Seed data uses the SauceDemo product catalogue (same domain as the
selenium-java and ai-eval suites) so reviewers see a consistent data story.
"""

from app.models import Product, User


class Store:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Restore products and users to their seeded state."""
        self.products: dict[int, Product] = {
            1: Product(id=1, name="Sauce Labs Backpack",         price=29.99, inventory=10),
            2: Product(id=2, name="Sauce Labs Bike Light",       price=9.99,  inventory=25),
            3: Product(id=3, name="Sauce Labs Bolt T-Shirt",     price=15.99, inventory=50),
            4: Product(id=4, name="Sauce Labs Fleece Jacket",    price=49.99, inventory=5),
            5: Product(id=5, name="Sauce Labs Onesie",           price=7.99,  inventory=30),
            6: Product(id=6, name="Test.allTheThings() T-Shirt", price=15.99, inventory=20),
        }
        self.users: dict[int, User] = {
            1: User(id=1, username="standard_user",       role="standard_user"),
            2: User(id=2, username="performance_glitch_user", role="standard_user"),
            3: User(id=3, username="error_user",          role="standard_user"),
            4: User(id=4, username="visual_user",         role="standard_user"),
            5: User(id=5, username="admin",               role="admin"),
        }
        self._next_id: int = 7  # next product id after seed


store = Store()
