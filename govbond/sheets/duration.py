"""Sheet 5: Duration / DV01 / Convexity -- interest-rate sensitivity, explained."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import cell_comment, define_name

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "DURATION / DV01 / CONVEXITY", "How sensitive the bond is to interest-rate moves",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = 7

    def row(label, name, formula, fmt, role="output"):
        nonlocal r
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, formula, role=role, fmt=fmt)
        sh.merge(r, 2, r, 3)
        if name:
            define_name(sh, name, r, 2)
        r += 1

    def box(lines):
        nonlocal r
        r = common.interp(sh, r, lines, last_col=LAST)

    r = common.section(sh, r, "Sensitivity measures", c1=1, c2=LAST)

    row("Macaulay duration", "MacDur",
        "=IF(IsZero=1,YearsToMat,DURATION(Settle,Maturity,CouponRate,YTM,Freq,Basis))", Fmt.YEARS)
    cell_comment(sh, r - 1, 2, "Excel DURATION() for coupon bonds; = time to maturity for a zero.")
    box(["Macaulay duration is the weighted average time to receive the bond's cash flows. For a zero-coupon bond it "
         "is close to the time to maturity, because all the cash arrives at the end. For a coupon bond it is usually "
         "shorter than maturity, because some cash is received earlier through coupons.",
         "Interpretation: a HIGHER Macaulay duration means the investor waits longer, on average, to get their money."])

    row("Modified duration", "ModDur",
        "=IF(IsZero=1,YearsToMat/(1+YTM),MDURATION(Settle,Maturity,CouponRate,YTM,Freq,Basis))", Fmt.RATIO)
    box(["Modified duration estimates the percentage price change for a 1% move in yield. If modified duration is 5, "
         "then a 1% rise in yield would reduce the price by around 5%, before convexity.",
         "Interpretation: HIGHER modified duration = HIGHER interest-rate risk; LOWER = lower rate risk."])

    row("DV01 (per 100 face)", "DV01", "=ModDur*Dirty*0.0001", Fmt.NUM4)
    cell_comment(sh, r - 1, 2, "DV01 = Modified duration x Dirty price x 0.0001.")
    box(["DV01 shows the approximate money price change for a 1 basis-point move in yield (1 bp = 0.01%). If DV01 is "
         "45, a 1 bp rise in yield reduces the value by about 45, and a 1 bp fall increases it by about 45. (Here it "
         "is per 100 of face; scale by your position size for a money amount.)",
         "Interpretation: DV01 turns rate risk into money terms. HIGHER DV01 = bigger profit/loss for small yield moves."])

    row("Convexity", "ConvexityView", "=Convexity", Fmt.RATIO, role="link")
    box(["Convexity measures how the bond's price sensitivity itself changes when yields move. Duration gives a "
         "straight-line estimate, but bond prices move in a curved way; convexity improves the estimate, especially "
         "for larger yield moves.",
         "Interpretation: for normal fixed-rate government bonds convexity is POSITIVE, which is good for you - the "
         "bond gains slightly MORE when yields fall and loses slightly LESS when yields rise than duration alone says."])

    sh.freeze("A6")
    sh.col_width(1, 26); sh.col_width(2, 13); sh.col_width(3, 8)
    for c in range(4, LAST + 1):
        sh.col_width(c, 14)
    return sh
