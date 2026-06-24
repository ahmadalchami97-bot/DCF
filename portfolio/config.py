"""
Configuration for the Portfolio Allocation Optimizer + Scenario Analysis.

Single, auditable source of truth for the asset universe, the explanatory market
indicators, the colour language, number formats and every tunable default.

Design intent (per the brief): a clean, professional, EXPLAINABLE Excel tool --
not a black-box quant model. Allocation rules are simple and visible; the only
slightly-technical number (portfolio volatility) is computed transparently from a
visible covariance table and explained on the Formula Guide.
"""

from __future__ import annotations

APP_NAME = "Portfolio Allocation Optimizer"
APP_VERSION = "1.0"
APP_TAGLINE = "Scenario analysis, risk/return and recommended rebalancing"

BASE_CURRENCY = "KWD"   # the investor's reporting currency (an input in the model)

# Investable assets: (key, display name, native currency).
ASSETS = [
    ("smi",    "SMI (Swiss Market Index)",            "CHF"),
    ("sp500",  "S&P 500",                              "USD"),
    ("sxi_re", "SXI Real Estate Funds Broad Index",    "CHF"),
    ("gold",   "Gold",                                 "USD"),
    ("ust",    "US Government Bonds",                   "USD"),
]
ASSET_KEYS = [a[0] for a in ASSETS]

# Market indicators -- shown as drivers/explanatory context ONLY. They are never
# treated as portfolio holdings unless the user flips "Investable?" to "Yes".
INDICATORS = [
    ("dxy",     "DXY (US Dollar Index)",   "Strength of the US dollar vs major currencies."),
    ("chf_usd", "CHF/USD",                 "Swiss franc per US dollar (drives USD-asset value in CHF terms)."),
    ("usd_kwd", "USD/KWD",                 "US dollar value in Kuwaiti dinar (FX for USD assets)."),
    ("chf_kwd", "CHF/KWD",                 "Swiss franc value in Kuwaiti dinar (FX for CHF assets)."),
]

SHEET_ORDER = [
    "Overview", "Scenario Inputs", "Scenario Output", "Risk & Return",
    "Allocation", "Rebalancing", "Dashboard", "Formula Guide",
]

# The six allocations compared on the Allocation sheet (key, label, short note).
ALLOCATIONS = [
    ("current",  "Current",         "Your portfolio today, from invested amounts."),
    ("equal",    "Equal-weight",    "Every asset gets the same weight (1 / N)."),
    ("target",   "Custom target",   "The target weights you type in."),
    ("sharpe",   "Max-Sharpe*",     "Tilts to assets with the best long-term return per unit of risk."),
    ("minvol",   "Min-volatility*", "Tilts to the calmer (lower-volatility) assets."),
    ("scenario", "Scenario-stressed", "Max-Sharpe base, modestly tilted by the scenario, within your limits."),
]


class Palette:
    TITLE = "12324F"          # deep navy
    HEADER = "1F4E79"
    SUBHEADER = "2E6CA4"
    SECTION = "4A7FB0"
    BAND = "EAF1F8"
    PANEL = "F4F8FC"
    EXPLAIN_FILL = "FFF8E1"   # soft amber panel for "what this sheet is" boxes
    EXPLAIN_BORDER = "E6C200"
    GRID = "D5DCE4"
    RULE = "B7C2CE"

    # mandated colour code
    INPUT = "0000FF"          # blue font  -> user inputs
    INPUT_FILL = "FFF7D6"     # pale yellow highlight so inputs are obvious
    FORMULA = "1A1A1A"        # black      -> on-sheet formulas
    LINK = "1F7A3D"           # green      -> pulled from another sheet
    OUTPUT = "1F7A3D"         # green      -> key outputs
    OUTPUT_FILL = "E2EFDA"
    RESULT_FILL = "D6EAD9"
    ERROR = "C00000"
    HEADER_FONT = "FFFFFF"
    TEXT = "1A2330"
    MUTED = "6B7886"
    WHITE = "FFFFFF"

    GOOD = "1F7A3D"
    GOOD_FILL = "D6EAD9"
    WARN = "9C6500"
    WARN_FILL = "FFF1C2"
    BAD = "C00000"
    BAD_FILL = "FCE4E4"

    # asset slice colours for pie/bar charts
    SERIES = ["1F4E79", "2E6CA4", "5B9BD5", "C9A227", "70AD47", "A5A5A5"]


class Fmts:
    PRICE = '#,##0.00'
    FX = '#,##0.0000'
    MONEY = '#,##0;(#,##0)'
    PCT = '0.0%;(0.0%)'
    PCT2 = '0.00%;(0.00%)'
    RATIO = '0.00'
    DAYS = '0" days"'
    INT = '#,##0'


# Status vocabulary for the traffic-light conditional formatting.
GOOD_WORDS = ["Buy", "Increase", "Good", "OK", "Balanced", "Within"]
WARN_WORDS = ["Hold", "Review", "Watch", "Near"]
BAD_WORDS = ["Sell", "Reduce", "Breach", "Outside", "High risk"]


class Defaults:
    RISK_FREE = 0.025          # annual risk-free rate (base currency)
    SCENARIO_TILT = 0.50       # how strongly to tilt toward scenario winners (0 = ignore)
    TILT_CAP = 0.40            # cap the relative tilt so we never chase short-term moves
    REBALANCE_BAND = 0.01      # |target - current| <= 1% weight -> Hold (no trade)
    DEFAULT_MIN_W = 0.05       # default minimum weight per asset
    DEFAULT_MAX_W = 0.40       # default maximum weight per asset


DISCLAIMER = ("The recommended allocation is model-based and should be used as a "
              "decision-support tool, not as a guaranteed perfect portfolio.")
