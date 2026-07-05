"""Sheet 1: Cover / Instructions."""

from __future__ import annotations

from .. import common
from ..config import DISCLAIMER

LAST = 10


def build(sh, ctx):
    common.title_block(sh, "US TREASURY BOND ANALYZER",
                       "A simple, clean model to value and analyze one US Treasury security", last_col=LAST)
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
    para("It values and analyzes a single US Treasury security: clean & dirty price, accrued interest, yield to "
         "maturity, current yield, duration, convexity, DV01, a rate-shock table, yield-curve context, a risk "
         "checklist, a recommendation page, and an independent audit sheet.")
    para("It is built to be understood: inputs are yellow, results are green, every formula is visible, and the "
         "Formula Explanations sheet describes each calculation in plain English.")

    head("The main risk for a US Treasury is INTEREST-RATE risk")
    para("US Treasuries are backed by the US government and are treated as the risk-free benchmark, so credit/default "
         "risk is not the focus. What moves their price is INTEREST RATES: when yields rise, Treasury prices fall, and "
         "when yields fall, prices rise. INFLATION also matters because coupons are fixed in nominal terms.")

    head("What it supports")
    for t in ["Fixed-coupon Treasury Notes and Bonds (semiannual coupons).",
              "Zero-coupon Treasury Bills (and stripped zeros): no coupon, only principal at maturity.",
              "Face value = 100 (prices quoted per 100 face). Day-count basis = Actual/Actual (Treasury convention)."]:
        para("- " + t, role="note_l")

    head("What it does NOT cover")
    para("Corporate bonds, credit spreads, callable bonds, floating-rate notes, TIPS, STRIPS complexity, and complex "
         "derivatives are out of scope - see the Limitations sheet. This keeps the model simple and correct for "
         "plain US Treasuries.", role="note_l")

    head("How to use this model")
    for i, t in enumerate([
        "Go to 'Bond Terms' and fill the yellow cells (security type, coupon, dates, market price).",
        "Read 'Price & Yield' and 'Duration & Convexity' for value and interest-rate risk.",
        "Use 'Rate Shock' to see price impact if yields move, and 'Yield Curve' for curve context.",
        "Review the 'Risk Summary', then use 'Recommendation' to summarise and make your Buy/Hold/Avoid call.",
        "Open 'Audit' to confirm the numbers pass the independent checks; use 'Formula Explanations' when unsure.",
    ], 1):
        para(f"{i}.  {t}", role="note_l")

    r += 1
    common.explain_box(sh, r, [DISCLAIMER], last_col=LAST, title="Important")

    sh.col_width(1, 16)
    for c in range(2, LAST + 1):
        sh.col_width(c, 12)
    return sh
