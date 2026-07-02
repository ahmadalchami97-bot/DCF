"""
Configuration for the Fixed-Rate Bond Analyzer.

Single source of truth for the colour language, number formats, the supported
coupon frequencies and day-count bases, tolerances used by the audit sheet, and
the sample bond. Deliberately simple: a plain-vanilla fixed-rate bond model.
"""

from __future__ import annotations

APP_NAME = "Fixed-Rate Bond Analyzer"
APP_VERSION = "1.0"

SHEET_ORDER = [
    "Cover", "Bond Terms", "Cash Flows", "Valuation", "Duration & Convexity",
    "Call & YTW", "Issuer Financial Strength", "Maturity Wall", "Risks",
    "Recommendation", "Formula Explanations", "Audit",
]

# Coupon frequency: label -> payments per year (Excel bond-function `frequency`).
# Zero-coupon is handled specially (no coupons); we step dates annually for it.
FREQUENCIES = ["Annual", "Semiannual", "Quarterly", "Zero-coupon"]
FREQ_NUM = {"Annual": 1, "Semiannual": 2, "Quarterly": 4, "Zero-coupon": 1}

# Day-count basis selector (matches Excel bond-function `basis`).
BASES = {
    0: "US (NASD) 30/360",
    1: "Actual/Actual",
    2: "Actual/360",
    3: "Actual/365",
    4: "European 30/360",
}

MAX_CF_ROWS = 80  # cash-flow schedule rows (covers e.g. 40y semi / 20y quarterly)


class Palette:
    TITLE = "1F3A5F"
    HEADER = "2E5984"
    SECTION = "4A789C"
    BAND = "E8EEF4"
    PANEL = "F4F7FA"
    EXPLAIN_FILL = "FFF8E1"
    EXPLAIN_BORDER = "E6C200"
    GRID = "D5DCE4"
    RULE = "B7C2CE"

    INPUT = "0000FF"          # blue  -> inputs
    INPUT_FILL = "FFF7D6"     # pale yellow highlight
    FORMULA = "1A1A1A"        # black -> formulas
    LINK = "1F7A3D"           # green -> cross-sheet links / key outputs
    OUTPUT = "1F7A3D"
    OUTPUT_FILL = "E2EFDA"
    RESULT_FILL = "D6EAD9"
    ERROR = "C00000"
    HEADER_FONT = "FFFFFF"
    TEXT = "20303F"
    MUTED = "6B7986"
    WHITE = "FFFFFF"

    GOOD = "1F7A3D"
    GOOD_FILL = "D6EAD9"
    WARN = "9C6500"
    WARN_FILL = "FFF1C2"
    BAD = "C00000"
    BAD_FILL = "FCE4E4"
    SERIES = ["2E5984", "C0641F"]


class Fmt:
    PRICE = '#,##0.00'
    MONEY = '#,##0.00'
    MONEY0 = '#,##0'
    PCT2 = '0.00%'
    PCT3 = '0.000%'
    RATIO = '0.00'
    MULT = '0.00"x"'
    YEARS = '0.00" yrs"'
    DATE = 'dd-mmm-yyyy'
    NUM4 = '#,##0.0000'
    BPS = '0.0" bps"'
    INT = '#,##0'


# Audit tolerances (stated on the Audit sheet).
class Tol:
    PRICE = 0.05        # price units per 100 face
    YIELD_BPS = 2.0     # basis points
    DURATION = 0.05     # years
    DV01 = 0.005        # price units
    GENERIC = 0.01


GOOD_WORDS = ["PASS", "OK", "Low", "Lower", "Buy", "Strong", "Adequate", "Within", "Yes"]
WARN_WORDS = ["WARNING", "WARN", "Medium", "Caution", "Watch", "Review", "Hold", "Near"]
BAD_WORDS = ["FAIL", "High", "Weak", "Sell", "Avoid", "Breach", "Negative", "No near"]

DISCLAIMER = ("This is a simplified educational model for a plain-vanilla fixed-rate bond. "
              "It is a decision-support tool, not investment advice.")

FUTURE_UPGRADES = [
    "Monthly-coupon bonds (12 payments/year)",
    "Floating-rate notes (FRNs)", "Amortizing / sinking-fund bonds",
    "Inflation-linked bonds", "Option-adjusted spread (OAS) & Z-spread",
    "Full callable-bond option valuation (binomial/Monte Carlo)",
    "CDS-implied credit risk", "Full issuer forecasting & distressed recovery analysis",
]
