"""
Central configuration for the company analysis engine.

Everything that controls the *look* (colors, fonts, number formats) and the
*judgement* (interpretation thresholds, conservative default assumptions) lives
here so the model has a single, auditable source of truth. No analysis logic
lives in this file -- only constants and tunable parameters.

Design intent: an analyst (or auditor) should be able to read this one file and
understand every threshold and default the model can apply.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Workbook identity
# ---------------------------------------------------------------------------
APP_NAME = "Investment-Grade Company Analysis Engine"
APP_VERSION = "1.0"
APP_TAGLINE = "Driver-based, fully-auditable financial analysis & DCF valuation"

# Order in which sheets appear in the workbook.
SHEET_ORDER = [
    "Cover",
    "Inputs",
    "Historical",
    "Assumptions",
    "WACC",
    "Forecast",
    "DCF",
    "Sensitivity",
    "Scenario",
    "Checks",
    "Dashboard",
    "Conclusion",
]

# ---------------------------------------------------------------------------
# Colour palette  (institutional / premium look)
# Hex without the leading '#'. openpyxl expects "FFRRGGBB" or "RRGGBB".
# ---------------------------------------------------------------------------
class Palette:
    # Brand / structural
    NAVY = "1F3A5F"        # primary header band
    NAVY_DARK = "152A45"   # cover / title
    SLATE = "2E5984"       # secondary header band
    STEEL = "4A789C"       # tertiary / sub-section
    LIGHT_BAND = "E8EEF4"  # zebra / sub-section background
    PANEL = "F4F7FA"       # light panel background

    # Cell-type coding (the legend explains these to the user)
    INPUT_FILL = "FFF7D6"      # pale yellow  -> user types here
    INPUT_FONT = "0563C1"      # blue font    -> classic "input" convention
    CALC_FONT = "000000"       # black        -> formula computed on this sheet
    LINK_FONT = "1F7A3D"       # green        -> pulled from another sheet
    OUTPUT_FILL = "DDEBF7"     # pale blue    -> key output
    RESULT_FILL = "E2EFDA"     # pale green    -> headline result
    HEADER_FONT = "FFFFFF"     # white on dark bands

    # Status / semantic
    GOOD = "1F7A3D"            # green text
    GOOD_FILL = "D6EAD9"
    WARN = "9C6500"            # amber text
    WARN_FILL = "FFF1CC"
    BAD = "B02418"             # red text
    BAD_FILL = "F8D7D5"
    NEUTRAL = "5A6B7B"         # grey text
    NEUTRAL_FILL = "ECEFF2"

    # Lines & text
    GRID = "D5DCE4"            # thin borders
    RULE = "B7C2CE"            # section rules
    TEXT = "20303F"            # default body text
    MUTED = "6B7986"           # secondary / notes text
    WHITE = "FFFFFF"


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_NAME = "Calibri"
FONT_SIZE = 10
FONT_SIZE_SMALL = 9
FONT_SIZE_NOTE = 8.5

# ---------------------------------------------------------------------------
# Number formats (Excel format codes)
# Negatives in parentheses & red where it aids readability of financials.
# ---------------------------------------------------------------------------
class Fmt:
    MONEY = '#,##0;(#,##0)'
    MONEY_DEC = '#,##0.0;(#,##0.0)'
    MONEY_RED = '#,##0;[Red](#,##0)'
    PER_SHARE = '#,##0.00;(#,##0.00)'
    PCT = '0.0%;(0.0%)'
    PCT0 = '0%;(0%)'
    PCT2 = '0.00%;(0.00%)'
    MULT = '0.0"x"'
    MULT2 = '0.00"x"'
    RATIO = '0.00'
    DAYS = '0.0" days"'
    INT = '#,##0'
    FLOAT1 = '0.0'
    FLOAT2 = '0.00'
    TEXT = '@'
    YEAR = '0'


# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
LABEL_COL_WIDTH = 42      # first column holding metric names
NOTE_COL_WIDTH = 52       # rationale / interpretation column
DATA_COL_WIDTH = 13       # per-period data columns
ROW_H_TITLE = 30
ROW_H_HEADER = 20
ROW_H_NORMAL = 15


# ---------------------------------------------------------------------------
# Interpretation thresholds
# These drive the plain-English labels. They are intentionally explicit and
# centralised so the labelling rules are auditable and tunable.
# ---------------------------------------------------------------------------
class Thresholds:
    # "Materially above / below history" band used for improving/stable/deteriorating.
    # Compares latest value vs trailing average; +/- this fraction of the average.
    TREND_BAND = 0.05            # 5% relative move vs history = a real change

    # Growth interpretation (accelerating / stable / decelerating) in pct points.
    GROWTH_ACCEL_PP = 0.02       # +2pp vs prior-period growth

    # Gross / operating margin move (pp) for expanding / compressing.
    MARGIN_MOVE_PP = 0.01        # 1pp

    # Leverage: Net debt / EBITDA bands (x).
    LEV_LOW = 1.0
    LEV_MODERATE = 2.5
    LEV_HIGH = 4.0               # above this = stretched / elevated risk

    # Interest coverage (EBIT / interest) bands (x).
    COVER_WEAK = 2.0
    COVER_ADEQUATE = 4.0         # above = strong

    # Liquidity: current ratio bands (x).
    CURRENT_WEAK = 1.0
    CURRENT_STRONG = 2.0

    # Quick ratio bands (x).
    QUICK_WEAK = 0.8
    QUICK_STRONG = 1.2

    # Returns vs an assumed hurdle: ROE / ROIC quality bands (%).
    RETURN_WEAK = 0.08
    RETURN_STRONG = 0.15

    # FCF margin bands (%).
    FCF_WEAK = 0.03
    FCF_STRONG = 0.10

    # Valuation upside/downside band vs current price for under/over-valued (%).
    VAL_BAND = 0.15              # +/-15% = fairly valued zone

    # WACC sanity bounds (%) -- outside these the Checks sheet flags it.
    WACC_MIN = 0.04
    WACC_MAX = 0.18

    # Terminal growth sanity bounds (%).
    TG_MIN = -0.01
    TG_MAX = 0.04                # should not exceed long-run nominal GDP-ish

    # Terminal growth must be below WACC by at least this margin (else TV blows up).
    TG_WACC_GAP_MIN = 0.01

    # Terminal value as % of EV above which we warn it is "TV-heavy".
    TV_SHARE_WARN = 0.80


# ---------------------------------------------------------------------------
# Conservative default assumptions (clearly labelled as FALLBACK in the model).
# Used only when the analyst supplies no market / driver data. Each one is
# economically defensible and intentionally cautious.
# ---------------------------------------------------------------------------
class Defaults:
    # WACC build-up fallbacks
    RISK_FREE = 0.04             # ~long-run developed-market nominal risk free
    EQUITY_RISK_PREMIUM = 0.05   # standard mature-market ERP
    BETA = 1.0                   # market beta when none supplied
    PRETAX_COST_OF_DEBT = 0.06   # plain investment-grade-ish coupon
    TAX_RATE = 0.25              # generic statutory blend

    # Terminal assumptions
    TERMINAL_GROWTH = 0.025      # ~ long-run nominal GDP, conservative
    EXIT_EBITDA_MULTIPLE = 8.0   # generic cross-check multiple

    # Forecast horizon (explicit years) before terminal value.
    FORECAST_YEARS = 5

    # Mean-reversion: weight on long-run growth at end of horizon.
    # Revenue growth fades from the historical trend toward a terminal rate.
    LONGRUN_GROWTH = 0.03        # economy-like long-run nominal growth anchor

    # Fallback intensities used ONLY when there is no history to derive them
    # from (keeps the forecast numeric instead of erroring). Clearly labelled.
    EBIT_MARGIN_FALLBACK = 0.12  # generic operating margin
    DA_PCT_FALLBACK = 0.05       # D&A as % of revenue
    CAPEX_PCT_FALLBACK = 0.05    # capex as % of revenue
    NWC_PCT_FALLBACK = 0.10      # net working capital as % of revenue

    # Scenario deltas applied to the base growth & margin paths.
    # (relative tilts -- see Assumptions sheet for how they are used)
    BULL_GROWTH_TILT = 0.03      # +3pp to revenue growth path
    BEAR_GROWTH_TILT = -0.03     # -3pp
    DOWNSIDE_GROWTH_TILT = -0.06 # -6pp stress
    BULL_MARGIN_TILT = 0.02      # +2pp to terminal EBIT margin
    BEAR_MARGIN_TILT = -0.02
    DOWNSIDE_MARGIN_TILT = -0.05


# Scenario registry. Order matters: index used by the scenario selector.
SCENARIOS = ["Base", "Bull", "Bear", "Downside"]
DEFAULT_SCENARIO_INDEX = 1  # 1-based -> "Base"

# ---------------------------------------------------------------------------
# Business types. The forecast/historical layers adapt to these. "Generic" is
# the safe industry-agnostic fallback that always works.
# ---------------------------------------------------------------------------
BUSINESS_TYPES = [
    "Generic / Diversified",
    "Consumer / Retail",
    "Industrial / Manufacturing",
    "SaaS / Software",
    "Asset-light Services",
    "Capital-intensive",
    "Bank",
    "Insurer",
]

# Working-capital relevance by business type (whether inventory/turnover ratios
# are meaningful). Banks/insurers do not use classic working capital.
WC_RELEVANT_DEFAULT = True

# Sentinel used throughout for "data not available / not meaningful".
NA_TEXT = "n/a"
NM_TEXT = "n/m"   # not meaningful (e.g. growth off a negative base)
MISSING_TEXT = "— missing —"
