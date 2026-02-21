"""
document.py — The Swag Labs (SauceDemo) knowledge base.

This simulates a real-world FAQ document that a RAG pipeline would ingest.
Each string in FAQ_CHUNKS is a topically coherent section — chunked so that
semantic search retrieves the most relevant piece for any given question.
"""

FAQ_CHUNKS = [
    """PRODUCT CATALOG
Swag Labs offers the following products:

1. Sauce Labs Backpack — $29.99
   A carry-all with tire tread design for all your snacking needs. Features a
   15-inch laptop sleeve. SKU: SauceLabsBackpack

2. Sauce Labs Bike Light — $9.99
   A red safety light for night cycling. Water-resistant with 5 lighting modes
   and 1 AAA battery included. SKU: SauceLabsBikeLight

3. Sauce Labs Bolt T-Shirt — $15.99
   Get your testing superhero on with the Sauce Labs bolt T-shirt.
   SKU: SauceLabsBoltTShirt

4. Sauce Labs Fleece Jacket — $49.99
   A midweight quarter-zip fleece jacket suitable for morning runs and daily
   commuting. SKU: SauceLabsFleeceJacket

5. Sauce Labs Onesie — $7.99
   A rib snap infant onesie for the junior automation engineer in development.
   SKU: SauceLabsOnesie

6. Test.allTheThings() T-Shirt (Red) — $15.99
   A classic Sauce Labs red t-shirt, perfect for cozying up to your keyboard
   and automating a few tests. SKU: TestAllTheThingsTShirt""",

    """CHECKOUT AND ORDERING PROCESS
To place an order at Swag Labs:

1. Browse the inventory page and click "Add to Cart" for desired items.
2. Click the shopping cart icon in the top-right corner to review your cart.
3. Click "Checkout" to begin the checkout process.
4. Enter your First Name, Last Name, and Zip/Postal Code.
5. Review your order summary, including the item subtotal and tax.
6. Click "Finish" to complete your purchase.

The tax rate applied to all orders is 8%. Standard shipping is free.""",

    """ACCOUNT TYPES AND ACCESS
Swag Labs supports several user account types for testing purposes:

- standard_user: Full access — browse, add to cart, and complete checkout.
- locked_out_user: Account is locked and cannot log in.
- problem_user: Experiences UI issues, including broken product images.
- performance_glitch_user: Experiences intentional performance delays on login.
- error_user: Encounters errors during the checkout flow.
- visual_user: Sees visual layout differences throughout the app.

All test accounts use the password: secret_sauce""",

    """RETURN AND REFUND POLICY
Swag Labs offers a 30-day return policy on all items:

- Items must be returned in original, unused condition with original packaging.
- A receipt or order confirmation email is required for all returns.
- Refunds are processed within 5-7 business days after the return is received.
- Sale items are final sale and cannot be returned or exchanged.
- The customer is responsible for return shipping costs.""",

    """SHIPPING INFORMATION
Swag Labs shipping details:

- Standard shipping is free on all orders.
- Orders are processed within 1-2 business days after purchase.
- Standard shipping delivery time: 5-7 business days.
- Expedited shipping (2-3 business days) is available for $9.99.
- Overnight shipping is available for $19.99.
- We ship to all 50 US states and select international destinations.""",
]
