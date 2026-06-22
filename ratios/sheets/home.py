"""
Home sheet (Sheet 1) -- professional cover page + navigation.

Built first so the company-identity input cells (name, ticker, industry, fiscal
year, analysis date) are registered before any other sheet links to them for its
header. Provides the colour legend and one-click navigation to every sheet.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..config import APP_NAME, APP_VERSION


def build(sh, ctx: common.Context):
    m = ctx.data["meta"]
    LAST = 9
    sh.hide_gridlines()
    sh.merge(1, 1, 1, LAST)
    sh.put(1, 1, APP_NAME, role="title")
    sh.row_height(1, 34)
    sh.merge(2, 1, 2, LAST)
    sh.put(2, 1, "A fully formula-driven, auditable ratio-analysis platform "
                 f"·  v{APP_VERSION}", role="subtitle")
    sh.row_height(2, 18)

    r = 4
    r = common.section(sh, r, "Company Profile", c1=1, c2=LAST)
    fields = [
        ("Company name", "meta_name", m.get("name"), Fmt.TEXT),
        ("Ticker", "meta_ticker", m.get("ticker"), Fmt.TEXT),
        ("Industry", "meta_industry", m.get("industry"), Fmt.TEXT),
        ("Reporting currency", "meta_currency", m.get("currency"), Fmt.TEXT),
        ("Units", "meta_units", m.get("units"), Fmt.TEXT),
        ("Fiscal year end", "meta_fye", m.get("fiscal_year_end"), Fmt.TEXT),
    ]
    for label, key, val, fmt in fields:
        sh.put(r, 1, label, role="label")
        sh.put(r, 2, val, role="input_l", fmt=fmt, key=f"in.{key}")
        sh.merge(r, 2, r, 4)
        r += 1
    sh.put(r, 1, "Analysis date", role="label")
    sh.put(r, 2, "=TODAY()", role="formula_l", fmt="dd mmm yyyy", key="in.meta_date")
    sh.merge(r, 2, r, 4)
    r += 2

    r = common.section(sh, r, "Navigation", c1=1, c2=LAST)
    r = common.nav_bar(sh, r, exclude={"Home"})
    r += 1
    r = common.legend(sh, r)
    r += 1
    r = common.section(sh, r, "About This Workbook", c1=1, c2=LAST)
    for line in _ABOUT:
        sh.put(r, 1, "•  " + line, role="note_l")
        sh.merge(r, 1, r, LAST)
        sh.row_height(r, 26)
        r += 1
    sh.col_width(1, 24)
    for c in range(2, LAST + 1):
        sh.col_width(c, 15)
    return sh


_ABOUT = [
    "15 sheets covering every major ratio family plus quality scores, peer "
    "benchmarking, an interpretation guide and automated quality-control checks.",
    "Every output is a live formula that traces back to the Inputs sheet — no "
    "hardcoded results. Yellow cells are the only ones you edit.",
    "Calculations are deliberately broken into helper rows and short formulas so "
    "each ratio is understandable without opening Excel's formula auditor.",
    "Classifications, trend arrows and commentary update automatically as you "
    "change the inputs.",
]
