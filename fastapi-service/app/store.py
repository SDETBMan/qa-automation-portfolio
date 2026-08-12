"""
store.py — In-memory singleton store for products, users, and annuity policies.

The Store class is instantiated once at module load as `store`.
Call store.reset() to restore the seed data between tests.

Seed data uses the SauceDemo product catalogue (same domain as the
selenium-java and ai-eval suites) so reviewers see a consistent data story.
Annuity seed data uses MYGA (Multi-Year Guaranteed Annuity) policies
representative of the Gainbridge / Group 1001 product line.
"""

from datetime import date

from app.annuity_models import Annuity
from app.models import Product, User


class Store:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Restore products, users, and annuities to their seeded state."""
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

        # -- MYGA annuity seed policies --
        self.annuities: dict[str, Annuity] = {
            "MYGA-001": Annuity(
                policy_id="MYGA-001",
                principal_cents=10_000_000,   # $100,000.00
                rate_bps=450,                 # 4.50%
                term_years=5,
                effective_date=date(2023, 1, 15),
                maturity_date=date(2028, 1, 15),
                surrender_schedule_bps=[500, 400, 300, 200, 100],
            ),
            "MYGA-002": Annuity(
                policy_id="MYGA-002",
                principal_cents=25_000_000,   # $250,000.00
                rate_bps=525,                 # 5.25%
                term_years=7,
                effective_date=date(2022, 6, 1),
                maturity_date=date(2029, 6, 1),
                surrender_schedule_bps=[700, 600, 500, 400, 300, 200, 100],
            ),
            "MYGA-003": Annuity(
                policy_id="MYGA-003",
                principal_cents=5_000_000,    # $50,000.00
                rate_bps=375,                 # 3.75%
                term_years=3,
                effective_date=date(2024, 3, 1),
                maturity_date=date(2027, 3, 1),
                surrender_schedule_bps=[500, 300, 100],
            ),
        }
        self._next_annuity_seq: int = 4  # next sequence after seed

    def next_annuity_id(self) -> str:
        """Generate the next MYGA policy ID."""
        policy_id = f"MYGA-{self._next_annuity_seq:03d}"
        self._next_annuity_seq += 1
        return policy_id


store = Store()
