"""Sheet 4: Price / Yield Analysis."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import cell_comment, define_name

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "PRICE & YIELD", "Accrued interest, clean vs dirty price, yield and spread", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "CLEAN PRICE is the quoted price. DIRTY PRICE is what you actually pay = clean price + accrued interest "
        "(the coupon that has built up since the last payment).",
        "YIELD TO MATURITY is the single rate that discounts the bond's cash flows back to its price - the return "
        "if you hold to maturity. For a Treasury Bill it is computed from price, face and time to maturity.",
        "SPREAD = yield - benchmark Treasury yield (optional; often ~0 for an on-the-run Treasury).",
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

    r = common.section(sh, r, "Results", c1=1, c2=LAST)
    row("Accrued interest (per 100)", "Accrued",
        "=IF(IsZero=1,0,COUPDAYBS(Settle,Maturity,Freq,Basis)/COUPDAYS(Settle,Maturity,Freq,Basis)*CouponRate/Freq*Face)",
        Fmt.PRICE, "Coupon built up since the last payment. Zero for a Treasury Bill.")
    cell_comment(sh, r - 1, 2, "Accrued = (days since last coupon / days in the period) x periodic coupon.")
    row("Market clean price", "CleanPrice", "=MktClean", Fmt.PRICE, "As entered on Bond Terms.", role="link")
    row("Dirty price (invoice price)", "Dirty", "=MktClean+Accrued", Fmt.PRICE, "What you actually pay = clean + accrued.")
    cell_comment(sh, r - 1, 2, "Dirty price = clean price + accrued interest.")
    row("Yield to maturity (YTM)", "YTM",
        "=IF(IsZero=1,(Face/MktClean)^(1/YearsToMat)-1,YIELD(Settle,Maturity,CouponRate,MktClean,Face,Freq,Basis))",
        Fmt.PCT3, "Return if held to maturity. Bill: (Face/Price)^(1/Years)-1 (effective annual).")
    cell_comment(sh, r - 1, 2, "Notes/bonds use Excel YIELD(); a Treasury Bill uses the manual zero-coupon formula.")
    row("Current yield", "CurrentYield", "=IF(IsZero=1,\"N/A\",(CouponRate*Face)/MktClean)", Fmt.PCT2,
        "Annual coupon / clean price. N/A for a Treasury Bill (no coupon).")
    row("Premium / discount to par", "PremDisc", "=MktClean-Face", Fmt.PRICE,
        "Positive = premium (above 100); negative = discount (below 100).")
    row("Spread over benchmark", "Spread", "=YTM-BenchYield", Fmt.PCT3, "Yield minus the benchmark Treasury yield.")
    row("Spread (basis points)", "SpreadBps", "=Spread*10000", Fmt.BPS, role="formula")
    row("Model clean price (reprice at YTM)", "CleanModel",
        "=IF(IsZero=1,Face/(1+YTM)^YearsToMat,PRICE(Settle,Maturity,CouponRate,YTM,Face,Freq,Basis))",
        Fmt.PRICE, "Should equal the market clean price (checked in Audit).", role="formula")
    r += 1

    r = common.section(sh, r, "Interpretation", c1=1, c2=LAST)
    sh.put(r, 1, "Price vs par", role="label_b")
    sh.put(r, 2, '=IF(MktClean>Face+0.25,"Premium - trades above par (coupon > yield)",'
                 'IF(MktClean<Face-0.25,"Discount - trades below par (coupon < yield)","Near par"))', role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1
    sh.put(r, 1, "Yield & price", role="label_b")
    sh.put(r, 2, '="Remember: higher yield -> lower price, and lower yield -> higher price."', role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1
    sh.put(r, 1, "Yield vs coupon", role="label_b")
    sh.put(r, 2, '=IF(IsZero=1,"Treasury Bill: all return comes from the discount to face value",'
                 'IF(YTM>CouponRate,"Yield above coupon - priced at a discount",'
                 'IF(YTM<CouponRate,"Yield below coupon - priced at a premium","Yield ~ coupon - priced near par")))',
           role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1

    sh.freeze("A6")
    sh.col_width(1, 28); sh.col_width(2, 13); sh.col_width(3, 8)
    for c in range(4, LAST + 1):
        sh.col_width(c, 14)
    return sh
