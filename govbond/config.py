"""
Configuration for the Government Bond Analyzer.

A simple, government-bonds-only model: fixed-coupon notes/bonds (semiannual or
annual) and zero-coupon bills. No corporate credit, no TIPS/callable/floaters.
Reuses the shared palette/formats/tolerances from the bond engine.
"""

from __future__ import annotations

APP_NAME = "Government Bond Analyzer"
APP_VERSION = "1.0"

SHEET_ORDER = [
    "Inputs", "Price & Yield", "Cash Flows", "Valuation Summary", "Duration & DV01",
    "Rate Shock", "Yield Curve", "Investment Attractiveness", "Recommendation",
    "Explanations", "Quality Check", "Limitations",
]

SEC_TYPES = ["Treasury Bill", "Treasury Note", "Treasury Bond", "Government Bond"]
FREQUENCIES = ["Semiannual", "Annual", "Zero-coupon"]
OUTLOOKS = ["Yields Rise", "Yields Fall", "Yields Stable"]

BASES = {0: "US 30/360", 1: "Actual/Actual", 2: "Actual/360", 3: "Actual/365", 4: "European 30/360"}
DEFAULT_BASIS = 1  # Actual/Actual (the government-bond convention)

MAX_CF_ROWS = 62   # up to 30y semiannual (or 60y annual)

GOOD_WORDS = ["PASS", "OK", "Low", "Normal", "Buy", "Short", "Yes", "Within", "Attractive", "Cheap", "Upside"]
WARN_WORDS = ["WARNING", "WARN", "Medium", "Flat", "Hold", "Intermediate", "Review", "Fair", "Neutral"]
BAD_WORDS = ["FAIL", "High", "Inverted", "Avoid", "Long", "Negative", "Expensive", "Not Attractive", "Downside"]

DISCLAIMER = ("This is a simplified educational model for a single government bond. "
              "It is a decision-support tool, not investment advice.")

FUTURE_UPGRADES = [
    "TIPS / inflation-linked analysis", "Key rate duration",
    "Treasury curve interpolation / bootstrapping", "Portfolio duration",
    "Bond-ladder comparison", "Comparison across multiple government bonds",
]

EXCLUDED = [
    "Corporate bonds", "Credit analysis", "Floating-rate notes",
    "Inflation-linked bonds / TIPS", "Callable bonds", "Option-adjusted spread (OAS)",
    "Z-spread", "Repo financing", "Futures hedging", "Key rate duration",
    "Full portfolio analysis",
]
