"""Sheet 17: Quality Check -- 15 independent checks that the workbook is correct."""

from __future__ import annotations

from bond.config import Fmt, Tol
from .. import common
from ..common import clean_at

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "QUALITY CHECK", "15 independent checks that the calculations are correct", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "Each row recomputes a result a DIFFERENT way, or checks a rule that must always hold, and reports a status. "
        "Pass = within tolerance / rule holds; Warning = small difference worth a look; Fail = check your inputs.",
        f"Tolerances:  price +/- {Tol.PRICE} per 100;  duration +/- {Tol.DURATION} years. A little rounding is normal.",
    ], last_col=LAST)
    r += 1

    hdr = r
    for c, tx in enumerate(["Check", "Main result", "Independent", "Diff", "Status", "Explanation"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c != 6 else "colhdr_l")
    sh.row_height(hdr, 18)
    r += 1
    first = r

    def num(name, main_f, indep_f, tol, explain, fmt=Fmt.PRICE):
        nonlocal r
        sh.put(r, 1, name, role="label_b")
        sh.put(r, 2, main_f, role="formula", fmt=fmt)
        sh.put(r, 3, indep_f, role="formula", fmt=fmt)
        sh.put(r, 4, f'=IF(AND(ISNUMBER(B{r}),ISNUMBER(C{r})),B{r}-C{r},"")', role="formula", fmt=fmt)
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

    num("Dirty price identity", "=Dirty", "=MktClean+Accrued", Tol.PRICE,
        "Dirty price should equal clean price + accrued interest.")
    num("Yield check (PV = dirty)", "=DirtyCF", "=Dirty", Tol.PRICE,
        "Discounting the cash flows at the YTM should reproduce the dirty price.")
    num("Price check", "=MktClean", f"={clean_at('YTM')}", Tol.PRICE,
        "Theoretical price at the YTM should match the market clean price.")
    num("Macaulay duration two ways", "=MacDur", "=MacaulayCF", Tol.DURATION,
        "Excel DURATION() and the cash-flow schedule should give the same Macaulay duration.", fmt=Fmt.YEARS)
    flag("Duration positive", '=IF(MacDur>0,"Pass","Fail")', "Duration must be positive for a normal bond.")
    flag("Modified <= Macaulay", '=IF(ModDur<=MacDur+0.0001,"Pass","Fail")',
         "Modified duration = Macaulay / (1 + y/f), so it is always a little smaller.")
    flag("DV01 positive", '=IF(DV01>0,"Pass","Fail")', "DV01 is a positive risk magnitude.")
    flag("Convexity positive", '=IF(Convexity>0,"Pass","Fail")',
         "Convexity should be positive for a normal fixed-rate government bond.")
    flag("Price-yield direction", f'=IF({clean_at("YTM+0.005")}<{clean_at("YTM-0.005")},"Pass","Fail")',
         "If the yield rises the price should fall, and vice versa.")
    flag("Accrued in range", '=IF(IsZero=1,"n/a",IF(AND(Accrued>=0,Accrued<=Cpn/Freq*Face+0.001),"Pass","Fail"))',
         "Accrued interest cannot be negative or bigger than one whole coupon.")
    flag("Zero-coupon check", '=IF(IsZero=1,IF(EffCoupon=0,"Pass","Warning"),"n/a (not zero-coupon)")',
         "A zero-coupon bond should have no coupon cash flows - only principal at maturity.")
    flag("Date order (settle < maturity)", '=IF(Settle<Mat,"Pass","Fail")',
         "Settlement must be before maturity.")
    flag("Issue on or before settlement", '=IF(N(IssueDate)=0,"n/a",IF(IssueDate<=Settle,"Pass","Warning"))',
         "You normally value the bond on or after its issue date.")
    flag("Frequency supported",
         '=IF(OR(FreqName="Semiannual",FreqName="Annual",FreqName="Zero-coupon"),"Pass","Fail")',
         "Coupon frequency must be Semiannual, Annual or Zero-coupon.")
    flag("Sanity: price vs par",
         '=IF(IsZero=1,"n/a",IF(ABS(Cpn-YTM)<0.0005,"Pass",IF(SIGN(Cpn-YTM)=SIGN(MktClean-Face),"Pass","Fail")))',
         "Coupon above YTM -> price above par; coupon below YTM -> price below par.")
    last = r - 1
    common.traffic_light(sh, f"E{first}:E{last}", f"E{first}")

    r += 1
    sh.put(r, 1, "Summary", role="label_b")
    sh.put(r, 2, f'="Pass: "&COUNTIF(E{first}:E{last},"Pass")&"   Warning: "&COUNTIF(E{first}:E{last},"Warning")'
                 f'&"   Fail: "&COUNTIF(E{first}:E{last},"Fail")', role="output_l")
    sh.merge(r, 2, r, LAST)

    sh.freeze(f"A{first}")
    sh.col_width(1, 24); sh.col_width(2, 12); sh.col_width(3, 12); sh.col_width(4, 9)
    sh.col_width(5, 10); sh.col_width(6, 54)
    return sh
