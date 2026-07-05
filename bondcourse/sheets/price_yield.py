"""Sheet 6: Price and Yield Calculator (both directions + a price-yield table)."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import clean_at, define_name

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "PRICE & YIELD CALCULATOR", "Price from a yield, yield from a price, both ways",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = 8

    def result(label, name, formula, fmt, role="output"):
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

    # SECTION A
    r = common.section(sh, r, "Section A - Yield from Price  (you entered the price on Inputs)", c1=1, c2=LAST)
    result("Accrued interest", None, "=Accrued", Fmt.PRICE, role="link")
    result("Dirty price", None, "=Dirty", Fmt.PRICE, role="link")
    result("Implied yield to maturity", None, "=YTM", Fmt.PCT3, role="link")
    result("Current yield", None, "=CurrentYield", Fmt.PCT2, role="link")
    result("Premium / discount to par", None, "=PremDisc", Fmt.PRICE, role="link")
    box("These come from your market price (see the Price Basics and Yield Basics sheets). The price you type gives a "
        "yield.")
    r += 1

    # SECTION B
    r = common.section(sh, r, "Section B - Price from Yield  (type a yield, get the price it implies)", c1=1, c2=LAST)
    sh.put(r, 1, "Yield to test", role="label_b")
    sh.put(r, 2, "=BenchYield", role="input", fmt=Fmt.PCT3)
    define_name(sh, "TestYield", r, 2)
    sh.put(r, 4, "Editable. Default = benchmark yield. Try your own 'fair value' yield.", role="note_l")
    sh.merge(r, 2, r, 3); sh.merge(r, 4, r, LAST); r += 1
    result("Theoretical clean price", "TheoClean", f"={clean_at('TestYield')}", Fmt.PRICE, role="result")
    result("Accrued interest", None, "=Accrued", Fmt.PRICE, role="link")
    result("Theoretical dirty price", "TheoDirty", "=TheoClean+Accrued", Fmt.PRICE, role="formula")
    result("Market clean - theoretical", "PriceDiff", "=MktClean-TheoClean", Fmt.PRICE, role="formula")
    result("Cheap / fair / expensive", "CheapFair",
           '=IF(TheoClean-MktClean>0.25,"Cheap (worth more than its price)",'
           'IF(TheoClean-MktClean<-0.25,"Expensive (worth less than its price)","Fair (close to its price)"))',
           None, role="status")
    common.traffic_light(sh, f"B{r-1}:B{r-1}", f"B{r-1}")
    box("This shows what the price SHOULD be at the yield you type. If the theoretical price is ABOVE the market "
        "price, the bond looks a little CHEAP; if BELOW, it looks EXPENSIVE. A simple check - not a guarantee.")
    r += 1

    # SECTION C
    r = common.section(sh, r, "Section C - Price-Yield Table  (theoretical clean price at different yields)",
                       c1=1, c2=LAST)
    hdr = r
    for c, tx in enumerate(["Yield scenario", "Yield", "Theoretical clean price"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c > 1 else "colhdr_l")
    sh.merge(hdr, 3, hdr, LAST)
    r += 1
    for bps in (-100, -50, -25, 0, 25, 50, 100):
        lab = "Current YTM" if bps == 0 else f"YTM {'+' if bps > 0 else '-'}{abs(bps)} bps"
        sh.put(r, 1, lab, role="label_b" if bps == 0 else "label")
        y = f"(YTM+{bps / 10000.0})"
        sh.put(r, 2, f"={y}", role="formula", fmt=Fmt.PCT3)
        sh.put(r, 3, f"={clean_at(y)}", role="output" if bps == 0 else "formula", fmt=Fmt.PRICE)
        sh.merge(r, 3, r, LAST)
        r += 1
    box("This table teaches the most important bond rule: when yields RISE, prices FALL; when yields FALL, prices "
        "RISE. Look down the table - as the yield goes up, the price goes down.")

    sh.freeze("A6")
    sh.col_width(1, 26); sh.col_width(2, 13); sh.col_width(3, 12)
    for c in range(4, LAST + 1):
        sh.col_width(c, 12)
    return sh
