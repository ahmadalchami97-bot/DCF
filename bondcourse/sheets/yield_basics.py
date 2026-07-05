"""Sheet 5: Yield Basics -- what return am I getting?"""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import cell_comment, define_name

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "YIELD BASICS", "What return am I getting? Yield, current yield and spread", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "YIELD TO MATURITY (YTM) is the annual return implied by the price if you hold the bond to maturity and get "
        "all the payments. It is THE main yield number.",
        "The most important rule in bonds: YIELD and PRICE move in OPPOSITE directions. If the price falls, the yield "
        "rises - a new buyer pays less for the same future cash flows, so they earn more.",
        "CURRENT YIELD is simpler - just the coupon divided by the price. SPREAD = your bond's yield minus a "
        "benchmark government yield of similar maturity.",
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

    r = common.section(sh, r, "Yields", c1=1, c2=LAST)
    row("Yield to maturity (YTM)", "YTM",
        "=IF(IsZero=1,(Face/MktClean)^(1/YrsToMat)-1,YIELD(Settle,Mat,Cpn,MktClean,Face,Freq,Basis))", Fmt.PCT3,
        role="result")
    cell_comment(sh, r - 1, 2, "Coupon bonds: Excel YIELD(). Bill/zero: (Face/Price)^(1/Years)-1.")
    box(["What it means: the return you lock in if you hold to maturity. Why it matters: it is the fairest way to "
         "compare bonds. Example: if the price falls, the YTM rises because a new buyer pays less for the same cash "
         "flows. Interpretation: higher price -> lower YTM; lower price -> higher YTM."])
    row("Current yield", "CurrentYield", '=IF(IsZero=1,"N/A",Cpn*Face/MktClean)', Fmt.PCT2)
    box("What it means: annual coupon / clean price - the income you get relative to today's price. Why it is limited: "
        "it ignores the gain or loss you make by holding to maturity. It is N/A for a zero-coupon bond (no coupon).")
    row("Premium / discount to par", "PremDisc", "=MktClean-Face", Fmt.PRICE)
    box("If the coupon rate is ABOVE the YTM, the bond usually trades ABOVE par (a premium). If the coupon is BELOW "
        "the YTM, it trades BELOW par (a discount). If they are close, it trades near par.")
    r += 1

    r = common.section(sh, r, "Spread over benchmark", c1=1, c2=LAST)
    row("Benchmark yield", None, "=BenchYield", Fmt.PCT2, role="link")
    row("Spread over benchmark", "Spread", "=YTM-BenchYield", Fmt.PCT3)
    row("Spread (basis points)", "SpreadBps", "=Spread*10000", Fmt.BPS, role="formula")
    box("Spread = your bond's yield minus the benchmark government yield of similar maturity. A positive spread means "
        "you earn a little more than the benchmark. For governments it is usually small.")

    sh.freeze("A6")
    sh.col_width(1, 26); sh.col_width(2, 13); sh.col_width(3, 8)
    for c in range(4, LAST + 1):
        sh.col_width(c, 14)
    return sh
