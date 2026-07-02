"""Sheet 4: Price / Valuation -- accrued, clean, dirty, YTM, current yield, spread."""

from __future__ import annotations

from .. import common
from ..common import cell_comment, define_name
from ..config import Fmt

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "PRICE / VALUATION", "Accrued interest, clean vs dirty price, yield and spread",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "CLEAN PRICE is the quoted price (what you see on a screen). DIRTY PRICE is what you actually pay = "
        "clean price + accrued interest (the coupon that has built up since the last payment).",
        "YTM (yield to maturity) is the single discount rate that makes the bond's future cash flows equal its "
        "price - the return you earn if you hold to maturity and reinvest coupons at the same rate.",
        "SPREAD = YTM - benchmark government yield: the extra yield you earn for taking this issuer's risk.",
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
        Fmt.PRICE, "Coupon built up since the last payment. Zero for a zero-coupon bond.")
    cell_comment(sh, r - 1, 2, "Accrued = (days since last coupon / days in the coupon period) x periodic coupon.\n"
                               "Uses the day-count basis you selected (COUPDAYBS / COUPDAYS).")
    row("Market clean price", "CleanPrice", "=MktClean", Fmt.PRICE, "As entered on Bond Terms.", role="link")
    row("Dirty price (invoice price)", "Dirty", "=MktClean+Accrued", Fmt.PRICE,
        "What you actually pay = clean + accrued.")
    cell_comment(sh, r - 1, 2, "Dirty price = clean price + accrued interest. This is the cash amount that changes hands.")
    row("Yield to maturity (YTM)", "YTM",
        "=IF(IsZero=1,(Face/MktClean)^(1/YearsToMat)-1,YIELD(Settle,Maturity,CouponRate,MktClean,Face,Freq,Basis))",
        Fmt.PCT3, "Return if held to maturity. Zero-coupon: (Face/Price)^(1/Years)-1.")
    cell_comment(sh, r - 1, 2, "Coupon bonds: Excel YIELD() solves for the yield from the clean price.\n"
                               "Zero-coupon: computed directly from price, face and years to maturity.")
    row("Current yield", "CurrentYield", "=IF(IsZero=1,\"N/A\",(CouponRate*Face)/MktClean)", Fmt.PCT2,
        "Annual coupon / clean price. Ignores capital gain/loss and timing. N/A for zero-coupon.")
    row("Premium / discount to par", "PremDisc", "=MktClean-Face", Fmt.PRICE,
        "Positive = premium (above par); negative = discount (below par).")
    row("Spread over benchmark", "Spread", "=YTM-BenchYield", Fmt.PCT3,
        "Extra yield vs a similar-maturity government bond.")
    row("Spread (basis points)", "SpreadBps", "=Spread*10000", Fmt.BPS, role="formula")

    # model reprice (kept for the Audit sheet)
    row("Model clean price (reprice at YTM)", "CleanModel",
        "=IF(IsZero=1,Face/(1+YTM)^YearsToMat,PRICE(Settle,Maturity,CouponRate,YTM,Face,Freq,Basis))",
        Fmt.PRICE, "Should equal the market clean price (checked on the Audit sheet).", role="formula")
    r += 1

    # ---- interpretation box ----
    r = common.section(sh, r, "Interpretation", c1=1, c2=LAST)
    sh.put(r, 1, "Price vs par", role="label_b")
    sh.put(r, 2, '=IF(MktClean>Face+0.5,"Premium - trades above par (coupon > yield)",'
                 'IF(MktClean<Face-0.5,"Discount - trades below par (coupon < yield)","Near par"))',
           role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1
    sh.put(r, 1, "Spread read", role="label_b")
    sh.put(r, 2, '=IF(Spread>=0.02,"Wide spread - potentially cheap, but only if the credit risk is acceptable",'
                 'IF(Spread<=0.005,"Tight spread - limited extra compensation for credit risk","Moderate spread"))',
           role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1
    sh.put(r, 1, "Yield vs coupon", role="label_b")
    sh.put(r, 2, '=IF(IsZero=1,"Zero-coupon: all return comes from the discount to face",'
                 'IF(YTM>CouponRate,"Yield above coupon - consistent with a discount price",'
                 'IF(YTM<CouponRate,"Yield below coupon - consistent with a premium price","Yield ~ coupon - priced near par")))',
           role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1

    sh.freeze("A6")
    sh.col_width(1, 28)
    sh.col_width(2, 13)
    sh.col_width(3, 8)
    for c in range(4, LAST + 1):
        sh.col_width(c, 14)
    return sh
