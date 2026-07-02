"""Sheet 5: Duration / Convexity + a yield-shock stress table."""

from __future__ import annotations

from .. import common
from ..common import cell_comment, define_name
from ..config import Fmt

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "DURATION & CONVEXITY", "Interest-rate sensitivity and a simple stress table",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "MACAULAY DURATION = the weighted-average time (in years) to receive the bond's cash flows.",
        "MODIFIED DURATION = the approximate % change in price for a 1% (100 bps) change in yield. Bigger = more "
        "sensitive to rates.  DV01 = the price change for a 1 basis-point move (a dollar/price risk measure).",
        "CONVEXITY improves the estimate for larger yield moves (the price/yield line is actually a curve). "
        "Price change is approximately:  - Modified duration x (yield change)  +  0.5 x convexity x (yield change)^2.",
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
            sh.put(r, 4, note, role="note_l")
            sh.merge(r, 4, r, LAST)
        r += 1

    r = common.section(sh, r, "Sensitivity measures", c1=1, c2=LAST)
    row("Macaulay duration", "MacDur",
        "=IF(IsZero=1,YearsToMat,DURATION(Settle,Maturity,CouponRate,YTM,Freq,Basis))", Fmt.YEARS,
        "For a zero-coupon bond this equals the time to maturity.")
    cell_comment(sh, r - 1, 2, "Excel DURATION() for coupon bonds; equals time-to-maturity for a zero-coupon bond.")
    row("Modified duration", "ModDur",
        "=IF(IsZero=1,YearsToMat/(1+YTM),MDURATION(Settle,Maturity,CouponRate,YTM,Freq,Basis))", Fmt.RATIO,
        "Approx % price fall if yield rises by 1% (100 bps).")
    row("Convexity", "ConvexityView", "=Convexity", Fmt.RATIO,
        "Computed on the Cash Flows sheet (Excel has no convexity function).", role="link")
    row("DV01 (per 100 face)", "DV01", "=ModDur*Dirty*0.0001", Fmt.NUM4,
        "Price change for a 1 basis-point yield move. Positive = the size of the risk.")
    cell_comment(sh, r - 1, 2, "DV01 = Modified duration x Dirty price x 0.0001.\n"
                               "It is quoted as a positive number (the magnitude of the 1 bp risk).")
    r += 1

    # ---- stress table ----
    r = common.section(sh, r, "Yield-shock stress table  (estimated impact on the dirty price)", c1=1, c2=LAST)
    hdr = r
    for c, tx in enumerate(["Yield change", "Change (decimal)", "Est. % price change",
                            "Est. new dirty price", "Est. change (per 100)"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c > 1 else "colhdr_l")
    sh.merge(hdr, 5, hdr, LAST)
    r += 1
    for bps in (100, 50, 25, -25, -50, -100):
        sign = "+" if bps > 0 else ""
        sh.put(r, 1, f"{sign}{bps} bps", role="label_b")
        sh.put(r, 2, bps / 10000.0, role="formula", fmt=Fmt.PCT2)
        dy = sh.local(r, 2)
        sh.put(r, 3, f"=-ModDur*{dy}+0.5*Convexity*{dy}^2", role="formula", fmt=Fmt.PCT2)
        sh.put(r, 4, f"=Dirty*(1+{sh.local(r,3)})", role="output", fmt=Fmt.PRICE)
        sh.put(r, 5, f"=Dirty*{sh.local(r,3)}", role="formula", fmt=Fmt.PRICE)
        sh.merge(r, 5, r, LAST)
        r += 1
    sh.put(r, 1, "Note: yields UP -> price DOWN (and vice versa). Convexity makes the price gain on a big rally "
                 "a bit larger than the loss on an equal sell-off.", role="note")
    sh.merge(r, 1, r, LAST)

    sh.freeze("A6")
    sh.col_width(1, 22)
    sh.col_width(2, 14)
    sh.col_width(3, 16)
    sh.col_width(4, 18)
    for c in range(5, LAST + 1):
        sh.col_width(c, 12)
    return sh
