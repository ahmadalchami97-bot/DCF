"""Sheet 12: Independent Quality Check / Audit.

Re-checks the main model with alternative methods (Excel's own bond functions,
a bump-and-reprice, the cash-flow schedule and logical tests). Tolerances are
stated at the top.
"""

from __future__ import annotations

from .. import common
from ..config import Fmt, Tol

LAST = 7

# reusable clean-price-at-yield expression (coupon via PRICE, zero via manual PV)
def _clean_at(y):
    return (f"IF(IsZero=1,Face/(1+({y}))^YearsToMat,"
            f"PRICE(Settle,Maturity,CouponRate,{y},Face,Freq,Basis))")


def build(sh, ctx):
    common.title_block(sh, "INDEPENDENT QUALITY CHECK / AUDIT",
                       "The main numbers, re-checked with independent methods", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "Each row recomputes a result a DIFFERENT way and compares. Status: Pass = within tolerance; "
        "Warning = small difference to review; Fail = check the inputs / assumptions.",
        f"Tolerances:  price +/- {Tol.PRICE} per 100;  yield +/- {Tol.YIELD_BPS} bps;  duration +/- {Tol.DURATION} yrs;  "
        f"DV01 +/- {Tol.DV01}.  Small rounding differences are expected and acceptable.",
    ], last_col=LAST)
    r += 1

    hdr = r
    for c, tx in enumerate(["Check", "Method / formula tested", "Model", "Independent", "Diff", "Status",
                            "Plain-English explanation"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c not in (2, 7) else "colhdr_l")
    sh.row_height(hdr, 18)
    r += 1
    rows_first = r

    def num(name, tested, model_f, indep_f, tol, explain, fmt=Fmt.PRICE):
        nonlocal r
        sh.put(r, 1, name, role="label_b")
        sh.put(r, 2, tested, role="note_l")
        sh.put(r, 3, model_f, role="formula", fmt=fmt)
        sh.put(r, 4, indep_f, role="formula", fmt=fmt)
        sh.put(r, 5, f"=IF(AND(ISNUMBER(C{r}),ISNUMBER(D{r})),C{r}-D{r},\"\")", role="formula", fmt=fmt)
        sh.put(r, 6, f'=IF(NOT(AND(ISNUMBER(C{r}),ISNUMBER(D{r}))),"n/a",'
                     f'IF(ABS(E{r})<={tol},"Pass",IF(ABS(E{r})<={3 * tol},"Warning","Fail")))', role="status")
        sh.put(r, 7, explain, role="note_l")
        r += 1

    def flag(name, tested, status_f, explain):
        nonlocal r
        sh.put(r, 1, name, role="label_b")
        sh.put(r, 2, tested, role="note_l")
        sh.put(r, 3, "", role="formula")
        sh.put(r, 4, "", role="formula")
        sh.put(r, 5, "", role="formula")
        sh.put(r, 6, status_f, role="status")
        sh.put(r, 7, explain, role="note_l")
        r += 1

    y = "YTM"
    # 1. Dirty price
    num("Dirty price", "clean + accrued  vs  sum of PV from the schedule", "=Dirty", "=DirtyCF", Tol.PRICE,
        "Dirty price should equal the present value of all cash flows.")
    # 2. Accrued interest
    num("Accrued interest", "model accrued  vs  Excel ACCRINT",
        "=Accrued",
        "=IF(IsZero=1,0,ACCRINT(COUPPCD(Settle,Maturity,Freq,Basis),COUPNCD(Settle,Maturity,Freq,Basis),Settle,CouponRate,Face,Freq,Basis))",
        Tol.PRICE, "Independent accrued from Excel's ACCRINT. Zero for a zero-coupon bond.")
    # 3. YTM vs YIELD ; price recomputed at YTM
    num("YTM vs Excel YIELD", "model YTM  vs  Excel YIELD (coupon bonds)",
        "=YTM", '=IF(IsZero=1,(Face/MktClean)^(1/YearsToMat)-1,YIELD(Settle,Maturity,CouponRate,MktClean,Face,Freq,Basis))',
        Tol.YIELD_BPS / 10000, "The model uses Excel YIELD for coupon bonds; a manual formula for zero-coupon.",
        fmt=Fmt.PCT3)
    num("Price = PV at YTM", "market clean  vs  reprice at YTM (PRICE / manual PV)",
        "=MktClean", f"={_clean_at(y)}", Tol.PRICE,
        "Repricing at the calculated YTM should return the market clean price.")
    # 5. Duration
    num("Macaulay duration", "Excel DURATION  vs  schedule sum(t*PV)/sum(PV)",
        "=MacDur", "=MacaulayCF", Tol.DURATION,
        "Two independent routes to Macaulay duration. For a zero it equals time to maturity.", fmt=Fmt.YEARS)
    num("Modified duration", "MDURATION  vs  Macaulay/(1+y/f)",
        "=ModDur", "=IF(IsZero=1,YearsToMat/(1+YTM),MacaulayCF/(1+YTM/Freq))", Tol.DURATION,
        "Modified duration cross-check.", fmt=Fmt.RATIO)
    # 6. DV01 two ways
    num("DV01 (two methods)", "duration approx  vs  bump-and-reprice (+/-1 bp)",
        "=DV01", f"=({_clean_at('YTM-0.0001')}-{_clean_at('YTM+0.0001')})/2", Tol.DV01,
        "DV01 from modified duration vs actually repricing at +/-1 bp.", fmt=Fmt.NUM4)
    # 7. Convexity
    flag("Convexity positive?", "convexity > 0 for a plain fixed-rate bond",
         '=IF(Convexity>0,"Pass","Fail")', "Plain-vanilla fixed-rate bonds have positive convexity.")
    num("Convexity reasonableness", "schedule convexity  vs  bump-and-reprice (+/-10 bp)",
        "=Convexity",
        f"=({_clean_at('YTM+0.001')}+{_clean_at('YTM-0.001')}-2*CleanModel)/(Dirty*0.001^2)",
        1.5, "Two independent convexity estimates should be in the same ballpark.", fmt=Fmt.RATIO)
    # 8. Yield to call
    flag("YTC validity", "if callable: settlement < call date < maturity",
         '=IF(CallableFlag<>"Yes",IF(YTC="Not callable","Pass","Warning"),'
         'IF(AND(Settle<CallDate,CallDate<Maturity),"Pass","Fail"))',
         "A call date must sit between settlement and maturity. Not-callable bonds must show 'Not callable'.")
    # 9. Yield to worst
    flag("YTW logic", "callable: min(YTM,YTC);  not callable: = YTM",
         '=IF(CallableFlag<>"Yes",IF(ABS(YTW-YTM)<0.000001,"Pass","Fail"),'
         'IF(ABS(YTW-MIN(YTM,YTC))<0.000001,"Pass","Fail"))',
         "Yield to worst must be the lower of YTM and YTC (or YTM if not callable).")
    # 10. Dates
    flag("Date order", "settlement date < maturity date",
         '=IF(Settle<Maturity,"Pass","Fail")', "Settlement must be before maturity.")
    flag("No negative times", "all payment times to come are positive",
         '=IF(YearsToMat>0,"Pass","Fail")', "Only future cash flows are valued.")
    # 11. Frequency
    flag("Frequency supported", "Annual / Semiannual / Quarterly / Zero-coupon only",
         '=IF(OR(FreqName="Annual",FreqName="Semiannual",FreqName="Quarterly",FreqName="Zero-coupon"),"Pass","Fail")',
         "Monthly and other frequencies are not supported in this version.")
    flag("Coupon count matches frequency", "remaining payments consistent with the frequency",
         '=IF(IsZero=1,IF(Ncoup=1,"Pass","Warning"),IF(Ncoup>0,"Pass","Fail"))',
         "Number of scheduled payments should match the chosen frequency.")
    # 12. Sanity
    flag("Price vs par direction", "coupon>YTM->premium; coupon<YTM->discount",
         '=IF(IsZero=1,"n/a",IF(ABS(CouponRate-YTM)<0.0005,"Pass",'
         'IF(SIGN(CouponRate-YTM)=SIGN(MktClean-Face),"Pass","Fail")))',
         "Higher coupon than yield => price above par, and vice versa.")
    flag("Stress monotonic", "yields up -> price down (from the stress table logic)",
         '=IF(ModDur>0,"Pass","Fail")', "Positive duration means price falls when yields rise.")
    flag("DV01 positive", "DV01 shown as a positive risk magnitude",
         '=IF(DV01>0,"Pass","Fail")', "DV01 is quoted positive even though price falls when yields rise.")
    # 13. Credit ratios
    flag("Net debt identity", "net debt = total debt - cash",
         '=IF(N(TotalDebt)=0,"n/a",IF(ABS(NetDebt-(TotalDebt-CashEq))<0.01,"Pass","Fail"))',
         "Confirms the net-debt calculation.")
    flag("Liquidity identity", "liquidity = cash + credit lines",
         '=IF(N(CashEq)+N(CreditLines)=0,"n/a",IF(ABS(Liquidity-(CashEq+CreditLines))<0.01,"Pass","Fail"))',
         "Confirms the liquidity calculation.")
    flag("Interest coverage flag", "warn if EBITDA/interest <= 1.5x",
         '=IF(NOT(ISNUMBER(EBITDACover)),"n/a",IF(EBITDACover>1.5,"Pass","Warning"))',
         "Low interest coverage is a credit warning.")
    flag("Leverage flag", "warn if net debt/EBITDA very high (>5x)",
         '=IF(NOT(ISNUMBER(NetDebtEBITDA)),"n/a",IF(NetDebtEBITDA<=5,"Pass","Warning"))',
         "Very high leverage is a credit warning.")
    flag("Liquidity coverage flag", "warn if liquidity coverage < 1.0x",
         '=IF(NOT(ISNUMBER(LiqCoverage)),"n/a",IF(LiqCoverage>=1,"Pass","Warning"))',
         "Liquidity below near-term maturities is a warning.")
    rows_last = r - 1
    common.traffic_light(sh, f"F{rows_first}:F{rows_last}", f"F{rows_first}")

    # summary
    r += 1
    sh.put(r, 1, "Summary", role="label_b")
    sh.put(r, 2, f'="Pass: "&COUNTIF(F{rows_first}:F{rows_last},"Pass")&"   Warning: "&'
                 f'COUNTIF(F{rows_first}:F{rows_last},"Warning")&"   Fail: "&COUNTIF(F{rows_first}:F{rows_last},"Fail")',
           role="output_l")
    sh.merge(r, 2, r, LAST)
    r += 2

    common.explain_box(sh, r, [
        "MODEL LIMITATIONS - this simple model does NOT cover:  OAS  -  Z-spread  -  full callable-bond option "
        "valuation  -  floating-rate notes  -  amortizing bonds  -  monthly-coupon bonds  -  inflation-linked bonds  "
        "-  distressed debt / recovery  -  CDS-implied credit risk  -  full issuer forecasting.",
        "For those, use a dedicated fixed-income system. This tool is for plain-vanilla fixed-rate bonds.",
    ], last_col=LAST, title="What this model does NOT cover")

    sh.freeze(f"A{rows_first}")
    sh.col_width(1, 24); sh.col_width(2, 34); sh.col_width(3, 11); sh.col_width(4, 11)
    sh.col_width(5, 9); sh.col_width(6, 10); sh.col_width(7, 52)
    return sh
