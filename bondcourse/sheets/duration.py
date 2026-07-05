"""Sheet 7: Duration -- how sensitive is my bond to yield moves?"""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import cell_comment, define_name

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "DURATION", "How sensitive is my bond to interest-rate moves?", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "Duration is the single most important risk measure for a government bond. There are two versions, and this "
        "sheet teaches both.",
    ], last_col=LAST)
    r += 1

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

    r = common.section(sh, r, "Macaulay duration", c1=1, c2=LAST)
    row("Macaulay duration", "MacDur",
        "=IF(IsZero=1,YrsToMat,DURATION(Settle,Mat,Cpn,YTM,Freq,Basis))", Fmt.YEARS, role="result")
    cell_comment(sh, r - 1, 2, "Excel DURATION() for coupon bonds; = time to maturity for a zero.")
    box(["Macaulay duration is the weighted average time to receive the bond's cash flows. It is NOT exactly the "
         "maturity. For coupon bonds it is usually shorter than maturity, because some cash is received earlier "
         "through coupons. For a zero-coupon bond it is close to the time to maturity (all cash comes at the end).",
         "Interpretation: a HIGHER Macaulay duration means you wait longer, on average, to get your money back."])

    r = common.section(sh, r, "Modified duration", c1=1, c2=LAST)
    row("Modified duration", "ModDur",
        "=IF(IsZero=1,YrsToMat/(1+YTM),MDURATION(Settle,Mat,Cpn,YTM,Freq,Basis))", Fmt.RATIO, role="result")
    box(["Modified duration estimates how much the price changes when the yield changes. If modified duration is 7, "
         "then a 1% RISE in yield would reduce the price by around 7% (before convexity).",
         "Interpretation: HIGHER duration = MORE interest-rate risk; LOWER duration = less risk. Long bonds usually "
         "have higher duration; zero-coupon bonds have duration close to their maturity.",
         "Example: a modified duration of 7 means the bond may lose about 7% if yields rise by 1% - and gain about 7% "
         "if yields fall by 1%."])

    r = common.section(sh, r, "What it says about this bond", c1=1, c2=LAST)
    sh.put(r, 1, "Rate-risk read", role="label_b")
    sh.put(r, 2, '=IF(ModDur<3,"LOW rate risk (short duration)",IF(ModDur<8,"MEDIUM rate risk (intermediate duration)",'
                 '"HIGH rate risk (long duration)"))', role="status")
    common.traffic_light(sh, f"B{r}:B{r}", f"B{r}")
    sh.merge(r, 2, r, 4); r += 1

    sh.freeze("A6")
    sh.col_width(1, 26); sh.col_width(2, 13); sh.col_width(3, 8)
    for c in range(4, LAST + 1):
        sh.col_width(c, 14)
    return sh
