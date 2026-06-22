"""
Configuration for the Institutional Forecasting Engine.

Holds the visual language (the mandated colour code: blue inputs, black formulas,
green key outputs, gray headers, red errors), the model dimensions, the scenario
and forecast-method registries, and the diagnostic thresholds. Constants only --
every tunable number is auditable here.
"""

from __future__ import annotations

APP_NAME = "Institutional Forecasting Engine"
APP_VERSION = "1.0"

HIST_YEARS = 10
FCST_YEARS = 10

SHEET_ORDER = [
    "Dashboard", "Historical", "Analysis", "Assumptions", "Forecast",
    "Bridge", "Diagnostics", "Scenario", "Sensitivity", "Notes",
]

SCENARIOS = ["Bear", "Base", "Bull"]
DEFAULT_SCENARIO = 2  # 1-based -> Base
METHODS = ["Historical Trend", "Manual Forecast", "Hybrid Forecast"]
DEFAULT_METHOD = 3    # 1-based -> Hybrid


class Palette:
    # gray header system
    TITLE = "404040"
    HEADER = "595959"
    SUBHEADER = "808080"
    BAND = "F2F2F2"
    PANEL = "FAFAFA"
    GRID = "D9D9D9"
    RULE = "BFBFBF"

    # mandated font-colour code
    INPUT = "0000FF"       # blue   -> inputs
    INPUT_FILL = "EAF1FB"  # subtle fill so input cells are easy to find
    FORMULA = "000000"     # black  -> formulas
    OUTPUT = "006100"      # green  -> key outputs
    OUTPUT_FILL = "E2EFDA"
    ERROR = "C00000"       # red    -> errors / warnings
    ERROR_FILL = "FCE4E4"
    HEADER_FONT = "FFFFFF"
    TEXT = "1A1A1A"
    MUTED = "7F7F7F"
    WHITE = "FFFFFF"

    # status
    GOOD = "006100"
    GOOD_FILL = "D6EAD9"
    WARN = "9C6500"
    WARN_FILL = "FFF1C2"
    BAD = "C00000"
    BAD_FILL = "FCE4E4"


# Sentiment vocabulary for status colouring.
GOOD_WORDS = ["PASS", "OK", "Balanced", "Healthy", "Strong", "Low", "Reasonable", "Clean"]
WARN_WORDS = ["WARN", "REVIEW", "Watch", "Elevated", "Caution", "Check"]
BAD_WORDS = ["FAIL", "Negative", "Breach", "Imbalanced", "Error", "Unreasonable", "High risk"]


class Thresholds:
    REV_GROWTH_HI = 0.30        # > 30% YoY -> warn
    REV_GROWTH_LO = -0.20       # < -20% YoY -> warn
    MARGIN_EXPAND_BPS = 0.04    # EBITDA margin moving > 400 bps in a year -> warn
    CAPEX_PCT_HI = 0.25         # capex > 25% of revenue -> warn
    TAX_LO, TAX_HI = 0.0, 0.50  # tax rate outside 0-50% -> warn
    WC_DAYS_HI = 250            # cash conversion cycle > 250 days -> warn
    BALANCE_TOL = 1.0           # |A-(L+E)| above this -> fail


# Forecast-method blend: in Hybrid, weight on the manual target ramps from ~0 to 1
# across the horizon (so it converges to the analyst's view by the final year).
def hybrid_weight(t: int, n: int) -> float:
    return 0.0 if n <= 1 else t / n
