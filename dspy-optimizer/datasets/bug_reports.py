"""30-item synthetic bug-report dataset.

Each item is a dspy.Example with:
    report  — bug report text (input)
    severity — Critical / High / Medium / Low (label)

The dataset is hardcoded — no API call needed, zero cost, works offline.
Train split: first 20 items.  Dev/held-out split: last 10 items.
"""

from __future__ import annotations

import dspy

_RAW: list[tuple[str, str]] = [
    # ── Critical ───────────────────────────────────────────────────────────
    (
        "The payment service is completely down. All checkout attempts return "
        "500 Internal Server Error. Revenue impact estimated at $50k/hour.",
        "Critical",
    ),
    (
        "Production database is unresponsive. All user sessions have been "
        "terminated and data may be corrupted.",
        "Critical",
    ),
    (
        "Security breach detected: unauthenticated users can access admin panel "
        "by manipulating the URL. Customer PII is exposed.",
        "Critical",
    ),
    (
        "Authentication service crashes on every login attempt after the latest "
        "deploy. 100% of users cannot log in.",
        "Critical",
    ),
    (
        "Data migration script ran against production instead of staging. "
        "Approximately 2,000 user records deleted permanently.",
        "Critical",
    ),
    (
        "Memory leak causes the application server to OOM-kill every 15 minutes. "
        "Affects all production pods.",
        "Critical",
    ),
    (
        "SSL certificate expired. Browser shows 'Not Secure' warning. "
        "All HTTPS traffic is failing.",
        "Critical",
    ),
    # ── High ───────────────────────────────────────────────────────────────
    (
        "The 'Add to Cart' button does not work for any item in the Electronics "
        "category. Other categories are unaffected.",
        "High",
    ),
    (
        "Search results return incorrect products when the query contains "
        "special characters such as & or +.",
        "High",
    ),
    (
        "Email notifications are not being sent after order confirmation. "
        "Users are complaining they missed their shipping updates.",
        "High",
    ),
    (
        "Report export to CSV fails with a timeout error for datasets larger "
        "than 500 rows. No workaround is available.",
        "High",
    ),
    (
        "The password reset link expires in 1 minute instead of the documented "
        "24 hours, locking users out of their accounts.",
        "High",
    ),
    (
        "Third-party payment gateway integration returning card-declined errors "
        "for valid Visa cards issued outside the US.",
        "High",
    ),
    (
        "Product images fail to load on the checkout summary page in Safari 17. "
        "Affects approximately 20% of users.",
        "High",
    ),
    # ── Medium ─────────────────────────────────────────────────────────────
    (
        "The date picker widget does not allow selecting dates in February "
        "during leap years. Affects booking forms only.",
        "Medium",
    ),
    (
        "User profile page shows the incorrect time zone for users in GMT+5:30. "
        "All other time zones display correctly.",
        "Medium",
    ),
    (
        "Pagination on the order history page skips page 3 and jumps directly "
        "to page 4 when there are more than 50 orders.",
        "Medium",
    ),
    (
        "The discount code field accepts expired promo codes and applies a 0% "
        "discount without showing an error message.",
        "Medium",
    ),
    (
        "Sorting products by 'Price: Low to High' occasionally returns results "
        "in a random order on the second page.",
        "Medium",
    ),
    (
        "The mobile navigation menu overlaps the hero banner on screens with "
        "375px width (iPhone SE). Layout issue only.",
        "Medium",
    ),
    (
        "CSV import truncates product descriptions longer than 255 characters "
        "without warning the user.",
        "Medium",
    ),
    (
        "The 'Remember Me' checkbox on the login form has no effect; session "
        "always expires after 30 minutes regardless.",
        "Medium",
    ),
    # ── Low ────────────────────────────────────────────────────────────────
    (
        "The footer copyright year still shows 2023 instead of the current year.",
        "Low",
    ),
    (
        "Tooltip on the 'Help' icon is misspelled: 'Clcik here for help' "
        "instead of 'Click here for help'.",
        "Low",
    ),
    (
        "The loading spinner animation is slightly off-center on the dashboard "
        "page in Firefox 120.",
        "Low",
    ),
    (
        "Hover state color for secondary buttons is #F0F0F0 instead of the "
        "design spec value of #E8E8E8.",
        "Low",
    ),
    (
        "The breadcrumb trail on category pages does not update when the user "
        "navigates back using the browser's back button.",
        "Low",
    ),
    (
        "Success toast notification disappears after 2 seconds; UX team "
        "recommends 3 seconds for readability.",
        "Low",
    ),
    (
        "The 'About Us' page title in the browser tab reads 'About - Acme' "
        "instead of 'About Us - Acme'.",
        "Low",
    ),
    (
        "Dark mode toggle state is not persisted across page refreshes. "
        "Users must re-enable dark mode on each visit.",
        "Low",
    ),
]

# Build dspy.Example objects — inputs_= marks which fields are inputs
DATASET: list[dspy.Example] = [
    dspy.Example(report=report, severity=severity).with_inputs("report")
    for report, severity in _RAW
]

TRAINSET: list[dspy.Example] = DATASET[:20]
DEVSET: list[dspy.Example] = DATASET[20:]
