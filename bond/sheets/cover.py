"""Sheet 1: Cover / Instructions."""

from __future__ import annotations

from .. import common
from ..config import BASES, DISCLAIMER, FUTURE_UPGRADES

LAST = 10


def build(sh, ctx):
    common.title_block(sh, "FIXED-RATE BOND ANALYZER",
                       "A simple, clean model to value and analyze one plain-vanilla fixed-rate bond", last_col=LAST)
    common.nav_bar(sh, 5)
    r = 7

    def para(text, role="note"):
        nonlocal r
        sh.put(r, 1, text, role=role, align="lw")
        sh.merge(r, 1, r, LAST)
        sh.row_height(r, max(14, 13 + 12 * (len(text) // 130)))
        r += 1

    def head(text):
        nonlocal r
        r = common.section(sh, r, text, c1=1, c2=LAST)

    head("What this model does")
    para("It values a single fixed-rate bond and explains the result: clean & dirty price, accrued interest, yield "
         "to maturity, duration, convexity, DV01, yield to call and yield to worst. It also has an optional issuer "
         "credit view, a maturity-wall chart, a risk checklist, a recommendation page, and an independent audit sheet "
         "that re-checks the main numbers using Excel's own bond functions.")
    para("It is built to be understood: inputs are in yellow, results in green, every formula is visible, and the "
         "Formula Explanations sheet describes each calculation in plain English.")

    head("Key assumptions")
    for t in [
        "Plain-vanilla fixed-rate bond. Face value = 100 (prices are quoted per 100 face).",
        "Coupon is fixed. Supported frequencies: Annual (1), Semiannual (2), Quarterly (4), and Zero-coupon.",
        "Day-count basis is selectable: " + "; ".join(f"{k}={v}" for k, v in BASES.items()) + ".",
        "Yields use the standard street convention (Excel YIELD/PRICE/DURATION). Zero-coupon yields are computed "
        "directly from price, face and time to maturity.",
        "Optional one-date / one-price call analysis. Yield to worst = lower of YTM and YTC.",
    ]:
        para("- " + t, role="note_l")

    head("Supported vs NOT supported")
    para("SUPPORTED:  annual, semiannual, quarterly and zero-coupon plain-vanilla fixed-rate bonds; optional simple "
         "call analysis; simple spread vs a government benchmark; optional simple issuer credit ratios.", role="note_l")
    para("NOT supported (listed as limitations, not modelled): monthly-coupon bonds, floating-rate notes, amortizing / "
         "sinking-fund bonds, inflation-linked bonds, OAS / Z-spread, full callable-bond option valuation, CDS-implied "
         "credit, and full issuer forecasting / distressed recovery. See 'Future upgrades' below.", role="note_l")

    head("How to use this model")
    for i, t in enumerate([
        "Go to 'Bond Terms' and fill the yellow cells (dates, coupon, frequency, basis, market price, call terms).",
        "Read 'Valuation' for price/yield/spread and 'Duration & Convexity' for interest-rate risk.",
        "Check 'Call & YTW' for callable bonds, then the optional 'Issuer Financial Strength' and 'Maturity Wall'.",
        "Fill the 'Risks' checklist, then use 'Recommendation' to summarise and make your Buy/Hold/Sell/Avoid call.",
        "Open 'Audit' to confirm the numbers pass the independent checks. Use 'Formula Explanations' whenever unsure.",
    ], 1):
        para(f"{i}.  {t}", role="note_l")

    head("Future upgrades (not in this version)")
    para("  -  " + "  -  ".join(FUTURE_UPGRADES), role="note_l")

    r += 1
    common.explain_box(sh, r, [DISCLAIMER], last_col=LAST, title="Important")

    sh.col_width(1, 16)
    for c in range(2, LAST + 1):
        sh.col_width(c, 12)
    return sh
