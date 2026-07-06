"""
Configuration for the Macro Market Intelligence System (core engine).

Phase 1-2 of the full 18-sheet design in docs/MACRO_INTELLIGENCE_SYSTEM.md:
the foundation + first scoring engines. Six sheets that already work end to end
so the analyst can validate the surprise/Fed mechanics on real data releases
before the market modules, synthesis engines and dashboard are added.

All formulas use only original-spec Excel functions (INDEX/MATCH, nested IF,
SUMPRODUCT, AVERAGEIF) so the workbook runs in any modern Excel, not just 365.
"""

from __future__ import annotations

APP_NAME = "Macro Market Intelligence System"
APP_VERSION = "0.9 (core)"

# Sheets built in this phase (reading order == tab order).
SHEET_ORDER = [
    "Cover", "Settings", "Impact Library", "Data Tracker", "Surprise Engine", "Fed Tracker",
]

# Sheets that exist in the full design but are not built yet (shown on the Cover
# roadmap so the analyst knows what is coming).
FUTURE_SHEETS = [
    "Executive Dashboard", "USD Dashboard", "Bond Module", "Geopolitical Risk",
    "Oil & Commodity", "Cross-Asset Matrix", "Scenario Engine", "Regime Classifier",
    "Portfolio Link", "Market Note Generator", "Watchlist", "Executive Snapshot", "Glossary",
]

# --- number formats (a few beyond bond.config.Fmt) ------------------------
F_NUM1 = "0.0"
F_NUM2 = "0.00"
F_NUM0 = "#,##0"
F_SCORE = "0.00"
F_SIGNED = "+0.00;-0.00;0.00"
F_DATE = "dd-mmm-yyyy"
F_INT = "0"

# --- dropdown / vocabulary lists (single source of truth) -----------------
LIST_COUNTRY = ["US", "Eurozone", "UK", "Japan", "China", "Global", "Kuwait", "GCC", "EM"]
LIST_FREQUENCY = ["Monthly", "Weekly", "Quarterly", "Daily", "Ad hoc"]
LIST_IMPORTANCE = ["1", "2", "3", "4", "5"]
LIST_CONFIDENCE = ["Low", "Medium", "High"]
LIST_FEDBIAS = ["Hawkish", "Mildly hawkish", "Neutral", "Mildly dovish", "Dovish"]
LIST_DIRECTION = ["Up", "Flat", "Down"]
LIST_SCORE5 = ["-2", "-1", "0", "1", "2"]
LIST_DOTPLOT = ["More hikes", "Fewer cuts", "On hold", "More cuts", "Cutting"]
LIST_CBBIAS = ["Hawkish", "Mildly hawkish", "Neutral", "Mildly dovish", "Dovish"]
LIST_DECISION = ["Hike", "Hold", "Cut"]
LIST_CATEGORY = ["Inflation", "Labor", "Growth", "Trade", "Fiscal", "Energy"]

# --- Fed hawkish/dovish score: 7 sub-scores and their weights -------------
# (label, weight)  -- weights sum to 1.0; stored on Settings as Fed_Weights.
FED_SUBSCORES = [
    ("Inflation surprises", 0.25),
    ("Labor-market strength", 0.20),
    ("Growth strength", 0.15),
    ("Fed-speech tone", 0.15),
    ("Market-implied rate change", 0.10),
    ("Yield-curve move (2Y)", 0.10),
    ("Real-yield move (10Y)", 0.05),
]

# Fed bias bands on the composite score (lower bound, label).
FED_BANDS = [(1.0, "Hawkish"), (0.33, "Mildly hawkish"), (-0.33, "Neutral"),
             (-1.0, "Mildly dovish")]  # below -1.0 -> "Dovish"

# --- shared table layout (Data Tracker and Surprise Engine share rows) -----
HDR_ROW = 8          # header row on the two data sheets
FIRST_ROW = 9        # first data row
NROWS = 40           # data rows (sample releases + blanks for the analyst)


class TRK:
    """Data Tracker (S02) column map."""
    DATE, COUNTRY, INDIC, ACTUAL, FCST, PREV, UNIT, FREQ, SURP, HOT, IMP, SRC, NOTES = range(2, 15)
    LAST = NOTES


class SUR:
    """Surprise Engine (S03) column map."""
    (DATE, INDIC, CAT, ACTUAL, FCST, PREV, ABS, Z, HOT, INFLIMP, GROWIMP,
     INFL, GROW, USD, UYLD, UPX, GOLD, OIL, SPX, EM, GCC, TONE, CONF) = range(2, 25)
    LAST = CONF
    # hidden helper columns
    MIDX = 26        # MATCH index into the library


class LIB:
    """Impact Library (S04) column map."""
    (INDIC, MEAS, WHY, HIGH, LOW, CAT, FED, USD, UYLD, UPX, EQ, GOLD, OIL, GCC,
     PINF, PGRO, IMP, SCALE, EXC) = range(2, 21)
    LAST = EXC
    HDR = 8
    FIRST = 9


DISCLAIMER = ("Intelligence and decision-support tool for monitoring macro and geopolitical risk. "
              "Its scores are transparent, weighted heuristics - a structured way to organise "
              "judgement, not a guaranteed predictor of market moves.")
