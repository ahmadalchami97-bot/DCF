"""
Configuration for the US Treasury Bond Analyzer.

A simple, Treasury-only model: fixed-coupon notes/bonds (semiannual) and
zero-coupon bills. No corporate credit, no callable/floating/TIPS. Reuses the
shared number formats, tolerances and palette from the bond engine.
"""

from __future__ import annotations

APP_NAME = "US Treasury Bond Analyzer"
APP_VERSION = "1.0"

SHEET_ORDER = [
    "Cover", "Bond Terms", "Cash Flows", "Price & Yield", "Duration & Convexity",
    "Rate Shock", "Yield Curve", "Risk Summary", "Recommendation",
    "Formula Explanations", "Audit", "Limitations",
]

SEC_TYPES = ["Treasury Bill", "Treasury Note", "Treasury Bond"]
FREQUENCIES = ["Semiannual", "Zero-coupon"]

# Day-count basis (Excel bond-function `basis`). Treasuries use Actual/Actual.
BASES = {0: "US 30/360", 1: "Actual/Actual", 2: "Actual/360", 3: "Actual/365", 4: "European 30/360"}
DEFAULT_BASIS = 1  # Actual/Actual (the Treasury convention)

MAX_CF_ROWS = 62   # up to 30y semiannual

GOOD_WORDS = ["PASS", "OK", "Low", "Normal", "Buy", "Short", "Yes", "Within"]
WARN_WORDS = ["WARNING", "WARN", "Medium", "Flat", "Hold", "Intermediate", "Review", "Watch"]
BAD_WORDS = ["FAIL", "High", "Inverted", "Avoid", "Long", "Negative", "No"]

DISCLAIMER = ("This is a simplified educational model for a single US Treasury security. "
              "It is a decision-support tool, not investment advice.")

FUTURE_UPGRADES = [
    "TIPS (inflation-linked) analysis", "Key rate duration",
    "Treasury curve interpolation / bootstrapping", "Portfolio duration",
    "Bond-ladder analysis", "Comparison across multiple Treasuries",
]

EXCLUDED = [
    "Corporate bonds", "Credit spreads", "Callable bonds", "Floating-rate notes",
    "TIPS", "STRIPS complexity", "Repo financing", "Futures hedging",
    "Key rate duration", "Full yield-curve bootstrapping", "Scenario probabilities",
    "Portfolio-level bond analysis",
]
