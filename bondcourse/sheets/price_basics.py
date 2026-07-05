"""Sheet 4: Price Basics -- clean price, dirty price, accrued interest."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import cell_comment, define_name

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "PRICE BASICS", "Clean price, dirty price and accrued interest - the price you actually pay",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "There are TWO prices for a bond. The CLEAN price is the quoted market price you see on a screen. The DIRTY "
        "price is what you actually PAY, because it also includes accrued interest.",
        "ACCRUED INTEREST is the coupon the seller has earned since the last coupon date. When you buy, you pay it "
        "back to the seller (you will collect the full coupon next time).",
        "Dirty price = clean price + accrued interest.",
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

    r = common.section(sh, r, "The three numbers", c1=1, c2=LAST)
    row("Clean price (quoted)", "CleanPrice", "=MktClean", Fmt.PRICE, role="link")
    box("This is just your input from the Inputs sheet - the quoted price, excluding accrued interest.")
    row("Accrued interest", "Accrued",
        "=IF(IsZero=1,0,COUPDAYBS(Settle,Mat,Freq,Basis)/COUPDAYS(Settle,Mat,Freq,Basis)*Cpn/Freq*Face)", Fmt.PRICE)
    cell_comment(sh, r - 1, 2, "Accrued = (days since last coupon / days in the period) x periodic coupon.")
    box(["What it means: the slice of the next coupon the seller has already earned. Why it matters: it is added to "
         "the quoted price, so it is part of what you pay. It is ZERO for a bill / zero-coupon bond (no coupons).",
         "Example: on a 4% bond, halfway through a 6-month period, roughly half of the 2.0 semiannual coupon (~1.0) "
         "has accrued."])
    row("Dirty price (what you pay)", "Dirty", "=MktClean+Accrued", Fmt.PRICE, role="result")
    box(["What it means: the real cash cost = clean + accrued. Example: if the clean price is 98 and accrued is 1, the "
         "dirty price is 99 - the buyer actually pays 99."])
    r += 1

    r = common.section(sh, r, "Is it a premium or a discount?", c1=1, c2=LAST)
    sh.put(r, 1, "Premium / discount", role="label_b")
    sh.put(r, 2, '=IF(MktClean>100.25,"PREMIUM (price above 100)",IF(MktClean<99.75,"DISCOUNT (price below 100)","NEAR PAR (around 100)"))',
           role="status")
    common.traffic_light(sh, f"B{r}:B{r}", f"B{r}")
    sh.merge(r, 2, r, 4); r += 1
    box("Clean price above 100 = a PREMIUM (you pay more than face). Below 100 = a DISCOUNT (you pay less than face). "
        "Around 100 = NEAR PAR. A discount usually means the coupon is below current market yields.")

    sh.freeze("A6")
    sh.col_width(1, 26); sh.col_width(2, 13); sh.col_width(3, 8)
    for c in range(4, LAST + 1):
        sh.col_width(c, 14)
    return sh
