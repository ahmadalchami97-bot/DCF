"""
Configuration for the Government Bond Course & Calculator.

A beginner teaching workbook that is also a working government-bond calculator.
Government bonds only (fixed-coupon notes/bonds + zero-coupon bills). Reuses the
shared bond palette / number formats / tolerances.
"""

from __future__ import annotations

APP_NAME = "Government Bond Course & Calculator"
APP_VERSION = "1.0"

SHEET_ORDER = [
    "Start Here", "Inputs", "Cash Flows", "Price Basics", "Yield Basics",
    "Price & Yield", "Duration", "DV01", "Convexity", "Rate Shock", "Yield Curve",
    "Valuation Summary", "Is It Attractive", "Recommendation", "Glossary",
    "Formula Explanations", "Quality Check", "Limitations",
]

SEC_TYPES = ["Treasury Bill", "Treasury Note", "Treasury Bond", "Government Bond"]
FREQUENCIES = ["Semiannual", "Annual", "Zero-coupon"]
OUTLOOKS = ["Yields Rise", "Yields Fall", "Yields Stable"]

BASES = {0: "US 30/360", 1: "Actual/Actual", 2: "Actual/360", 3: "Actual/365", 4: "European 30/360"}
DEFAULT_BASIS = 1
MAX_CF_ROWS = 62

GOOD_WORDS = ["PASS", "OK", "Low", "Normal", "Buy", "Short", "Yes", "Within", "Attractive", "Cheap", "Upside"]
WARN_WORDS = ["WARNING", "WARN", "Medium", "Flat", "Hold", "Intermediate", "Review", "Fair", "Neutral"]
BAD_WORDS = ["FAIL", "High", "Inverted", "Avoid", "Long", "Negative", "Expensive", "Not Attractive", "Downside"]

DISCLAIMER = ("This is a simplified educational model for a single government bond. "
              "It is a learning and decision-support tool, not investment advice.")

FUTURE_UPGRADES = [
    "TIPS / inflation-linked analysis", "Key rate duration",
    "Treasury curve interpolation / bootstrapping", "Bond-ladder comparison",
    "Portfolio duration", "Comparison across multiple government bonds",
]

EXCLUDED = [
    "Corporate bonds", "Corporate credit analysis", "Floating-rate notes",
    "Inflation-linked bonds / TIPS", "Callable bonds", "Option-adjusted spread (OAS)",
    "Z-spread", "Key rate duration", "Repo financing", "Futures hedging",
    "Portfolio-level analysis", "Advanced curve bootstrapping",
]
