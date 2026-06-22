"""
Configuration for the Institutional Forecasting Engine (rebuilt, first-principles).

Design goals, in strict priority order: TRANSPARENCY, CLARITY, AUDITABILITY,
USABILITY -- ahead of sophistication, automation and flexibility. One direct
driver per forecast line; historical figures are pure pasted-in inputs; forecasts
begin the year AFTER the last reported year (auto-detected). No forecasting
"engine", no method selector, no scenario machinery.

This file is the single, auditable source of truth for every tunable constant.
"""

from __future__ import annotations

APP_NAME = "Institutional Forecasting Engine"
APP_VERSION = "2.0"

# Timeline -------------------------------------------------------------------
FIRST_YEAR = 2015          # default first historical year (an input in the model)
HIST_SLOTS = 15            # historical year columns provided (room to add actuals)
ACTUAL_YEARS = 11          # actual years pre-filled in the sample (FY2015-FY2025)
HORIZON = 10               # forecast years shown (begin after the last actual)

SHEET_ORDER = [
    "Dashboard", "Methodology", "Historical", "Assumptions",
    "Forecast", "Bridge", "Diagnostics",
]


# ---------------------------------------------------------------------------
# The forecast drivers -- exactly one per forecast line. This single list is
# shared by the Assumptions grid, the Forecast model and the sample data, so the
# assumption -> output relationship is impossible to mis-wire.
#   (key, label, kind, drives)   kind in {"pct", "money"}
# ---------------------------------------------------------------------------
DRIVERS = [
    ("rev_growth",    "Revenue growth",                      "pct",
     "Revenue = prior revenue x (1 + growth)"),
    ("ebitda_margin", "EBITDA margin",                       "pct",
     "EBITDA = revenue x EBITDA margin"),
    ("da_pct",        "D&A (% of revenue)",                  "pct",
     "D&A = revenue x D&A%"),
    ("capex_pct",     "Capex (% of revenue)",                "pct",
     "Capex = revenue x capex%"),
    ("nwc_pct",       "Net working capital (% of revenue)",  "pct",
     "Net working capital = revenue x NWC%"),
    ("net_int_rate",  "Net interest rate (on opening net debt)", "pct",
     "Net interest = rate x opening net debt (no circularity)"),
    ("tax_rate",      "Tax rate",                            "pct",
     "Tax = tax rate x pre-tax income"),
    ("payout",        "Dividend payout",                     "pct",
     "Dividends = payout x max(0, net income)"),
    ("net_new_debt",  "Net new debt raised",                 "money",
     "Debt = prior debt + net new debt"),
]


class Palette:
    TITLE = "1F3354"          # deep navy
    HEADER = "2E4A6B"
    SUBHEADER = "5B7286"
    ACTUAL_HDR = "39506B"     # actual-year column header (steel blue)
    FCST_HDR = "1F7A4D"       # forecast-year column header (distinct green)
    BAND = "EFF3F7"
    ACTUAL_FILL = "EAF0F7"    # subtle blue shade for actual columns
    FCST_FILL = "EAF5EE"      # subtle green shade for forecast columns
    SPARE_FILL = "F2F2F2"     # neutral grey for empty/spare actual columns
    PANEL = "F7F9FB"
    GRID = "D5DCE4"
    RULE = "AEBCCD"

    # mandated font-colour code
    INPUT = "0000FF"          # blue   -> inputs
    INPUT_FILL = "FFFDEB"     # very light highlight so inputs are easy to find
    FORMULA = "1A1A1A"        # black  -> formulas
    OUTPUT = "1F7A4D"         # green  -> key outputs
    OUTPUT_FILL = "E2EFDA"
    ERROR = "C00000"          # red    -> errors / warnings
    ERROR_FILL = "FCE4E4"
    HEADER_FONT = "FFFFFF"
    TEXT = "1A2330"
    MUTED = "6B7886"
    WHITE = "FFFFFF"

    GOOD = "1F7A4D"
    GOOD_FILL = "D6EAD9"
    WARN = "9C6500"
    WARN_FILL = "FFF1C2"
    BAD = "C00000"
    BAD_FILL = "FCE4E4"


GOOD_WORDS = ["PASS", "OK", "Balanced", "Healthy", "Reasonable", "Clean", "Actual"]
WARN_WORDS = ["WARN", "REVIEW", "Watch", "Elevated", "Caution", "Check"]
BAD_WORDS = ["FAIL", "Negative", "Breach", "Imbalanced", "Error", "Unreasonable"]


class Thresholds:
    REV_GROWTH_HI = 0.30        # > 30% YoY -> warn
    REV_GROWTH_LO = -0.20       # < -20% YoY -> warn
    MARGIN_DRIFT_BPS = 0.04     # EBITDA-margin avg annual drift > 400 bps -> warn
    CAPEX_PCT_HI = 0.25         # capex > 25% of revenue -> warn
    NWC_PCT_HI = 0.40           # NWC > 40% of revenue -> warn
    TAX_LO, TAX_HI = 0.0, 0.50  # tax rate outside 0-50% -> warn
    BALANCE_TOL = 1.0           # |A-(L+E)| above this -> fail
