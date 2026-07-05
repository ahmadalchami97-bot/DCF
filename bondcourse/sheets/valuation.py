"""Sheet 12: Valuation Summary -- the whole bond at a glance."""

from __future__ import annotations

from bond.config import Fmt
from .. import common

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "VALUATION SUMMARY", "The whole bond at a glance, with plain-English reads", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "This page collects the key numbers from all the other sheets so you can understand the bond at a glance. "
        "Change your inputs and this updates automatically.",
    ], last_col=LAST)
    r += 1

    def row(label, formula, fmt, role="link"):
        nonlocal r
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, formula, role=role, fmt=fmt)
        sh.merge(r, 2, r, 3)
        r += 1

    def box(lines):
        nonlocal r
        r = common.interp(sh, r, lines, last_col=LAST)

    r = common.section(sh, r, "Identity", c1=1, c2=LAST)
    for lab, f in (("Bond name", "=BondName"), ("Issuer", "=Issuer"), ("Currency", "=Ccy"),
                   ("Security type", "=SecType"), ("Maturity date", "=Mat")):
        row(lab, f, Fmt.DATE if lab == "Maturity date" else None)
    row("Years to maturity", "=YrsToMat", Fmt.YEARS)
    row("Coupon rate", "=Cpn", Fmt.PCT2)
    r += 1

    r = common.section(sh, r, "Price & yield", c1=1, c2=LAST)
    row("Clean price", "=MktClean", Fmt.PRICE)
    row("Dirty price", "=Dirty", Fmt.PRICE)
    row("Accrued interest", "=Accrued", Fmt.PRICE)
    row("Yield to maturity", "=YTM", Fmt.PCT3)
    row("Current yield", "=CurrentYield", Fmt.PCT2)
    row("Benchmark yield", "=BenchYield", Fmt.PCT2)
    row("Spread over benchmark (bps)", "=SpreadBps", Fmt.BPS)
    row("Premium / discount to par", "=PremDisc", Fmt.PRICE)
    box("Price above 100 = premium; below 100 = discount. YTM is your return to maturity; the spread is the little "
        "extra over the benchmark government yield.")
    r += 1

    r = common.section(sh, r, "Risk", c1=1, c2=LAST)
    row("Macaulay duration", "=MacDur", Fmt.YEARS)
    row("Modified duration", "=ModDur", Fmt.RATIO)
    row("DV01 (per 100)", "=DV01", Fmt.NUM4)
    row("Convexity", "=Convexity", Fmt.RATIO)
    box("Modified duration is roughly the % price change for a 1% yield move (bigger = riskier). DV01 is that risk in "
        "money terms per 1 bp. Convexity is a small positive cushion.")

    sh.freeze("A6")
    sh.col_width(1, 28); sh.col_width(2, 16); sh.col_width(3, 6)
    for c in range(4, LAST + 1):
        sh.col_width(c, 12)
    return sh
