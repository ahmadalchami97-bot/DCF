"""Sheet 4: Valuation Summary -- the key numbers with interpretation boxes."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import define_name

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "VALUATION SUMMARY", "The key valuation numbers, with plain-English interpretation",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = 7

    def row(label, name, formula, fmt, role="output", note=""):
        nonlocal r
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, formula, role=role, fmt=fmt)
        sh.merge(r, 2, r, 3)
        if name:
            define_name(sh, name, r, 2)
        if note:
            sh.put(r, 4, note, role="note_l")
            sh.merge(r, 4, r, LAST)
        r += 1

    def box(lines):
        nonlocal r
        r = common.interp(sh, r, lines, last_col=LAST)

    r = common.section(sh, r, "Price & yield", c1=1, c2=LAST)
    row("Clean price", None, "=MktClean", Fmt.PRICE, role="link")
    row("Dirty price", None, "=Dirty", Fmt.PRICE, role="link")
    row("Accrued interest", None, "=Accrued", Fmt.PRICE, role="link")
    row("Yield to maturity", None, "=YTM", Fmt.PCT3, role="link")
    row("Current yield", None, "=CurrentYield", Fmt.PCT2, role="link")
    row("Coupon rate", None, "=CouponRate", Fmt.PCT2, role="link")
    r += 1

    r = common.section(sh, r, "Spread & structure", c1=1, c2=LAST)
    row("Benchmark yield", None, "=BenchYield", Fmt.PCT2, role="link")
    row("Spread over benchmark", "Spread", "=YTM-BenchYield", Fmt.PCT3)
    row("Spread (basis points)", "SpreadBps", "=Spread*10000", Fmt.BPS, role="formula")
    box("Spread = bond yield minus the benchmark government yield of similar maturity. For government bonds, small "
        "differences can come from maturity, liquidity, the specific issue, market pricing, or (for non-US sovereigns) "
        "country-specific risk. A positive spread means you earn a little more than the benchmark.")
    row("Premium / discount to par", None, "=PremDisc", Fmt.PRICE, role="link")
    box("If the coupon rate is ABOVE the yield, the price should generally be ABOVE par (a premium). If the coupon is "
        "BELOW the yield, the price should be BELOW par (a discount). If they are close, the price should be near par.")
    row("Years to maturity", None, "=YearsToMat", Fmt.YEARS, role="link")
    box("Years to maturity is roughly how long until you get your principal back. LONGER maturity usually means "
        "HIGHER sensitivity to interest-rate moves (bigger price swings when yields change).")
    row("Remaining coupon payments", None, "=IF(IsZero=1,0,Ncoup)", Fmt.INT, role="link")
    box("This is how many coupon payments are left before maturity. A zero-coupon bond has none - you only receive "
        "the principal at the end.")

    sh.freeze("A6")
    sh.col_width(1, 26); sh.col_width(2, 13); sh.col_width(3, 8)
    for c in range(4, LAST + 1):
        sh.col_width(c, 14)
    return sh
