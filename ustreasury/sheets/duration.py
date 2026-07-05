"""Sheet 5: Duration / Convexity / DV01."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import cell_comment, define_name

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "DURATION & CONVEXITY", "Interest-rate sensitivity of the bond", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "MACAULAY DURATION = the weighted-average time (years) to receive the cash flows. For a Treasury Bill it "
        "equals the time to maturity.",
        "MODIFIED DURATION = the approximate % price change for a 1% (100 bps) yield move. Bigger = more rate risk.",
        "DV01 = the price change for a 1 basis-point move (a price-risk measure).  CONVEXITY improves the estimate "
        "for larger moves: price change is approximately  -Modified x (yield change) + 0.5 x convexity x (yield change)^2.",
    ], last_col=LAST)
    r += 1

    def row(label, name, formula, fmt, note="", role="output"):
        nonlocal r
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, formula, role=role, fmt=fmt)
        sh.merge(r, 2, r, 3)
        if name:
            define_name(sh, name, r, 2)
        if note:
            sh.put(r, 4, note, role="note_l"); sh.merge(r, 4, r, LAST)
        r += 1

    r = common.section(sh, r, "Sensitivity measures", c1=1, c2=LAST)
    row("Macaulay duration", "MacDur",
        "=IF(IsZero=1,YearsToMat,DURATION(Settle,Maturity,CouponRate,YTM,Freq,Basis))", Fmt.YEARS,
        "For a Treasury Bill this equals the time to maturity.")
    cell_comment(sh, r - 1, 2, "Excel DURATION() for coupon Treasuries; = time-to-maturity for a bill.")
    row("Modified duration", "ModDur",
        "=IF(IsZero=1,YearsToMat/(1+YTM),MDURATION(Settle,Maturity,CouponRate,YTM,Freq,Basis))", Fmt.RATIO,
        "Approx % price fall if the yield rises 1% (100 bps).")
    row("Convexity", "ConvexityView", "=Convexity", Fmt.RATIO,
        "Computed on the Cash Flows sheet (Excel has no convexity function).", role="link")
    row("DV01 (per 100 face)", "DV01", "=ModDur*Dirty*0.0001", Fmt.NUM4,
        "Price change for a 1 basis-point yield move. Positive = the size of the risk.")
    cell_comment(sh, r - 1, 2, "DV01 = Modified duration x Dirty price x 0.0001.")
    r += 1
    sh.put(r, 1, "Rule of thumb: a modified duration of D means about a D% price change for a 1% yield move. "
                 "Longer-maturity Treasuries have larger duration and more price risk.", role="note")
    sh.merge(r, 1, r, LAST)

    sh.freeze("A6")
    sh.col_width(1, 26); sh.col_width(2, 13); sh.col_width(3, 8)
    for c in range(4, LAST + 1):
        sh.col_width(c, 14)
    return sh
