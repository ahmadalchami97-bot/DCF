"""Sheet 11: Independent Quality Check / Audit."""

from __future__ import annotations

from bond.config import Fmt, Tol
from .. import common


def _clean_at(y):
    return (f"IF(IsZero=1,Face/(1+({y}))^YearsToMat,PRICE(Settle,Maturity,CouponRate,{y},Face,Freq,Basis))")


LAST = 6


def build(sh, ctx):
    common.title_block(sh, "INDEPENDENT QUALITY CHECK / AUDIT",
                       "The main numbers, re-checked with independent methods", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "Each row recomputes a result a DIFFERENT way and compares. Status: Pass = within tolerance; "
        "Warning = small difference to review; Fail = check the inputs.",
        f"Tolerances:  price +/- {Tol.PRICE} per 100;  yield +/- {Tol.YIELD_BPS} bps;  duration +/- {Tol.DURATION} yrs;  "
        f"DV01 +/- {Tol.DV01}.  Small rounding differences are expected.",
    ], last_col=LAST)
    r += 1

    hdr = r
    for c, tx in enumerate(["Check", "Model", "Independent", "Diff", "Status", "Explanation"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c != 6 else "colhdr_l")
    sh.row_height(hdr, 18)
    r += 1
    first = r

    def num(name, model_f, indep_f, tol, explain, fmt=Fmt.PRICE):
        nonlocal r
        sh.put(r, 1, name, role="label_b")
        sh.put(r, 2, model_f, role="formula", fmt=fmt)
        sh.put(r, 3, indep_f, role="formula", fmt=fmt)
        sh.put(r, 4, f"=IF(AND(ISNUMBER(B{r}),ISNUMBER(C{r})),B{r}-C{r},\"\")", role="formula", fmt=fmt)
        sh.put(r, 5, f'=IF(NOT(AND(ISNUMBER(B{r}),ISNUMBER(C{r}))),"n/a",'
                     f'IF(ABS(D{r})<={tol},"Pass",IF(ABS(D{r})<={3 * tol},"Warning","Fail")))', role="status")
        sh.put(r, 6, explain, role="note_l")
        r += 1

    def flag(name, status_f, explain):
        nonlocal r
        sh.put(r, 1, name, role="label_b")
        sh.put(r, 2, "", role="formula"); sh.put(r, 3, "", role="formula"); sh.put(r, 4, "", role="formula")
        sh.put(r, 5, status_f, role="status")
        sh.put(r, 6, explain, role="note_l")
        r += 1

    num("Dirty price", "=Dirty", "=DirtyCF", Tol.PRICE,
        "Dirty price should equal the sum of the cash-flow present values.")
    num("Accrued interest", "=Accrued",
        "=IF(IsZero=1,0,ACCRINT(COUPPCD(Settle,Maturity,Freq,Basis),COUPNCD(Settle,Maturity,Freq,Basis),Settle,CouponRate,Face,Freq,Basis))",
        Tol.PRICE, "Independent accrued from Excel ACCRINT. Zero for a Treasury Bill.")
    num("YTM vs Excel YIELD", "=YTM",
        "=IF(IsZero=1,(Face/MktClean)^(1/YearsToMat)-1,YIELD(Settle,Maturity,CouponRate,MktClean,Face,Freq,Basis))",
        Tol.YIELD_BPS / 10000, "Notes/bonds: Excel YIELD. Bill: manual zero-coupon formula.", fmt=Fmt.PCT3)
    num("Price = PV at YTM", "=MktClean", f"={_clean_at('YTM')}", Tol.PRICE,
        "Repricing at the calculated yield returns the market clean price.")
    num("Macaulay duration", "=MacDur", "=MacaulayCF", Tol.DURATION,
        "Excel DURATION vs the schedule. For a bill it equals time to maturity.", fmt=Fmt.YEARS)
    num("Modified duration", "=ModDur", "=IF(IsZero=1,YearsToMat/(1+YTM),MacaulayCF/(1+YTM/Freq))", Tol.DURATION,
        "Modified duration cross-check.", fmt=Fmt.RATIO)
    num("DV01 (two methods)", "=DV01", f"=({_clean_at('YTM-0.0001')}-{_clean_at('YTM+0.0001')})/2", Tol.DV01,
        "Duration approximation vs bump-and-reprice at +/-1 bp.", fmt=Fmt.NUM4)
    flag("Convexity positive?", '=IF(Convexity>0,"Pass","Fail")',
         "A normal fixed-rate Treasury has positive convexity.")
    num("Convexity reasonableness", "=Convexity",
        f"=({_clean_at('YTM+0.001')}+{_clean_at('YTM-0.001')}-2*CleanModel)/(Dirty*0.001^2)", 1.5,
        "Schedule convexity vs a bump-and-reprice estimate.", fmt=Fmt.RATIO)
    flag("Date order", '=IF(Settle<Maturity,"Pass","Fail")', "Settlement must be before maturity.")
    flag("No negative times", '=IF(YearsToMat>0,"Pass","Fail")', "Only future cash flows are valued.")
    flag("Frequency correct", '=IF(SecType="Treasury Bill",IF(IsZero=1,"Pass","Fail"),IF(Freq=2,"Pass","Fail"))',
         "Notes/bonds must be semiannual; bills must be zero-coupon.")
    flag("Consistency check", '=IF(FreqWarn="OK","Pass","Fail")',
         "Security type and coupon frequency must be consistent (see Bond Terms).")
    flag("Coupon count", '=IF(IsZero=1,IF(Ncoup=1,"Pass","Warning"),IF(Ncoup>0,"Pass","Fail"))',
         "Number of scheduled payments matches the frequency.")
    flag("Price vs par direction",
         '=IF(IsZero=1,"n/a",IF(ABS(CouponRate-YTM)<0.0005,"Pass",IF(SIGN(CouponRate-YTM)=SIGN(MktClean-Face),"Pass","Fail")))',
         "Coupon above yield => price above par, and vice versa.")
    flag("Duration positive", '=IF(ModDur>0,"Pass","Fail")', "Price falls when yields rise (positive duration).")
    flag("DV01 positive", '=IF(DV01>0,"Pass","Fail")', "DV01 is quoted positive as a risk magnitude.")
    last = r - 1
    common.traffic_light(sh, f"E{first}:E{last}", f"E{first}")

    r += 1
    sh.put(r, 1, "Summary", role="label_b")
    sh.put(r, 2, f'="Pass: "&COUNTIF(E{first}:E{last},"Pass")&"   Warning: "&COUNTIF(E{first}:E{last},"Warning")'
                 f'&"   Fail: "&COUNTIF(E{first}:E{last},"Fail")', role="output_l")
    sh.merge(r, 2, r, LAST)

    sh.freeze(f"A{first}")
    sh.col_width(1, 24); sh.col_width(2, 12); sh.col_width(3, 12); sh.col_width(4, 9)
    sh.col_width(5, 10); sh.col_width(6, 58)
    return sh
