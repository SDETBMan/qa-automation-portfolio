"""
tools.py — Tool definitions and implementations for the Swag Labs support agent.

Each tool exists in two forms:
  1. TOOL_DEFINITIONS  — OpenAI function-calling format, passed to the API so
                         the model knows what tools are available and how to call them.
  2. AVAILABLE_TOOLS_DEEPEVAL — DeepEval ToolCall list, passed to ToolCorrectnessMetric
                                so it knows what tools the agent had access to when
                                judging whether the right ones were called.

Tool implementations are deterministic Python functions backed by the Swag Labs
knowledge base. The agent (LLM) decides WHICH tools to call and with WHAT
arguments — the tools themselves just return known, correct data.
"""

from deepeval.test_case import ToolCall

# ── OpenAI function-calling definitions ───────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_product",
            "description": (
                "Look up details for a Swag Labs product by name, including "
                "price, SKU, and description. Use this whenever a customer asks "
                "about a specific product's details or price."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The product name to look up, e.g. 'Sauce Labs Backpack'",
                    }
                },
                "required": ["product_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_return_eligibility",
            "description": (
                "Check whether a Swag Labs product is eligible for return based "
                "on days since purchase and whether the customer has a receipt. "
                "Use this whenever a customer asks about returning a product."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the product the customer wants to return",
                    },
                    "days_since_purchase": {
                        "type": "integer",
                        "description": "Number of days since the product was purchased",
                    },
                    "has_receipt": {
                        "type": "boolean",
                        "description": "Whether the customer has a receipt or order confirmation email",
                    },
                },
                "required": ["product_name", "days_since_purchase", "has_receipt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_shipping_cost",
            "description": (
                "Get the cost and estimated delivery window for a Swag Labs "
                "shipping option. Use this when a customer asks about shipping "
                "costs or delivery times."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "shipping_type": {
                        "type": "string",
                        "enum": ["standard", "expedited", "overnight"],
                        "description": "The shipping tier to look up",
                    }
                },
                "required": ["shipping_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_account_status",
            "description": (
                "Get the login status and any restrictions for a Swag Labs user "
                "account. Use this when a customer asks why they cannot log in "
                "or what access a specific account type has."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The Swag Labs username to look up, e.g. 'locked_out_user'",
                    }
                },
                "required": ["username"],
            },
        },
    },
]

# ── DeepEval ToolCall list (for ToolCorrectnessMetric.available_tools) ────────

AVAILABLE_TOOLS_DEEPEVAL = [
    ToolCall(
        name="lookup_product",
        description="Look up details for a Swag Labs product by name, including price, SKU, and description.",
    ),
    ToolCall(
        name="check_return_eligibility",
        description="Check whether a Swag Labs product is eligible for return based on purchase date and receipt status.",
    ),
    ToolCall(
        name="calculate_shipping_cost",
        description="Get the cost and delivery window for a Swag Labs shipping tier.",
    ),
    ToolCall(
        name="get_account_status",
        description="Get the login status and restrictions for a Swag Labs user account.",
    ),
]

# ── Tool implementations ───────────────────────────────────────────────────────

_PRODUCTS = {
    "sauce labs backpack":      {"name": "Sauce Labs Backpack",      "price_usd": 29.99, "sku": "SauceLabsBackpack",         "description": "A carry-all with tire tread design featuring a 15-inch laptop sleeve."},
    "sauce labs bike light":    {"name": "Sauce Labs Bike Light",    "price_usd":  9.99, "sku": "SauceLabsBikeLight",         "description": "A red safety light for night cycling. Water-resistant with 5 lighting modes."},
    "sauce labs bolt t-shirt":  {"name": "Sauce Labs Bolt T-Shirt",  "price_usd": 15.99, "sku": "SauceLabsBoltTShirt",        "description": "The testing superhero bolt T-shirt."},
    "sauce labs fleece jacket": {"name": "Sauce Labs Fleece Jacket", "price_usd": 49.99, "sku": "SauceLabsFleeceJacket",      "description": "A midweight quarter-zip fleece jacket for morning runs and daily commuting."},
    "sauce labs onesie":        {"name": "Sauce Labs Onesie",        "price_usd":  7.99, "sku": "SauceLabsOnesie",            "description": "A rib snap infant onesie for the junior automation engineer in development."},
    "test.allthethings() t-shirt": {"name": "Test.allTheThings() T-Shirt (Red)", "price_usd": 15.99, "sku": "TestAllTheThingsTShirt", "description": "Classic Sauce Labs red t-shirt for automating at the keyboard."},
}

_SHIPPING = {
    "standard":  {"cost_usd": 0.00,  "delivery_window": "5–7 business days",  "description": "Free standard shipping on all orders."},
    "expedited": {"cost_usd": 9.99,  "delivery_window": "2–3 business days",  "description": "Expedited shipping at $9.99."},
    "overnight": {"cost_usd": 19.99, "delivery_window": "1 business day",     "description": "Overnight shipping at $19.99."},
}

_ACCOUNTS = {
    "standard_user":           {"can_login": True,  "account_type": "standard_user",           "restrictions": None,                                                  "notes": "Full access — browse, add to cart, and complete checkout."},
    "locked_out_user":         {"can_login": False, "account_type": "locked_out_user",         "restrictions": "Account is locked and cannot log in.",                "notes": "This account is intentionally blocked from accessing the application."},
    "problem_user":            {"can_login": True,  "account_type": "problem_user",            "restrictions": "Experiences broken product images.",                  "notes": "Used for UI defect testing."},
    "performance_glitch_user": {"can_login": True,  "account_type": "performance_glitch_user", "restrictions": "Experiences intentional performance delays on login.", "notes": "Used for performance testing."},
    "error_user":              {"can_login": True,  "account_type": "error_user",              "restrictions": "Encounters errors during the checkout flow.",          "notes": "Used for error-handling testing."},
    "visual_user":             {"can_login": True,  "account_type": "visual_user",             "restrictions": "Sees visual layout differences throughout the app.",   "notes": "Used for visual regression testing."},
}


def lookup_product(product_name: str) -> dict:
    """Return product details for the closest matching Swag Labs product."""
    key = product_name.lower().strip()
    # Try exact match first, then substring match
    if key in _PRODUCTS:
        return _PRODUCTS[key]
    for k, v in _PRODUCTS.items():
        if k in key or key in k:
            return v
    return {"error": f"Product '{product_name}' not found in the Swag Labs catalog."}


def check_return_eligibility(
    product_name: str,
    days_since_purchase: int,
    has_receipt: bool,
) -> dict:
    """Return whether a product is eligible for return under Swag Labs policy."""
    policy_window = 30
    within_window = days_since_purchase <= policy_window

    if not within_window:
        return {
            "product_name": product_name,
            "eligible": False,
            "reason": f"Purchase was {days_since_purchase} days ago, which exceeds the {policy_window}-day return window.",
            "policy_window_days": policy_window,
        }
    if not has_receipt:
        return {
            "product_name": product_name,
            "eligible": False,
            "reason": "A receipt or order confirmation email is required for all returns.",
            "policy_window_days": policy_window,
        }
    return {
        "product_name": product_name,
        "eligible": True,
        "reason": f"Purchase is within the {policy_window}-day return window and a receipt is available.",
        "policy_window_days": policy_window,
        "refund_processing_days": "5–7 business days after the return is received.",
    }


def calculate_shipping_cost(shipping_type: str) -> dict:
    """Return cost and delivery window for the requested shipping tier."""
    key = shipping_type.lower().strip()
    if key in _SHIPPING:
        return _SHIPPING[key]
    return {"error": f"Shipping type '{shipping_type}' is not available. Choose standard, expedited, or overnight."}


def get_account_status(username: str) -> dict:
    """Return login status and restrictions for a Swag Labs account."""
    key = username.lower().strip()
    if key in _ACCOUNTS:
        return _ACCOUNTS[key]
    return {"error": f"Account '{username}' not found. Valid accounts: {', '.join(_ACCOUNTS)}."}


def execute_tool(name: str, args: dict) -> dict:
    """Dispatch a tool call by name to the appropriate implementation."""
    dispatch = {
        "lookup_product":          lambda: lookup_product(**args),
        "check_return_eligibility": lambda: check_return_eligibility(**args),
        "calculate_shipping_cost": lambda: calculate_shipping_cost(**args),
        "get_account_status":      lambda: get_account_status(**args),
    }
    if name not in dispatch:
        return {"error": f"Unknown tool: '{name}'"}
    return dispatch[name]()
