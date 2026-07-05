"""Sheet 2: Bond Terms -- the only input page. Defines named ranges."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import define_name
from ..config import FREQUENCIES, SEC_TYPES

LAST = 7


def build(sh, ctx):
    t = ctx.data["terms"]
    common.title_block(sh, "BOND TERMS", "Type the Treasury's details here. Every other sheet reads from this page.",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "WHAT TO DO:  fill the yellow cells. Use the drop-downs for security type and coupon frequency.",
        "TREASURY BILL:  set Security type = Treasury Bill and Coupon frequency = Zero-coupon; the coupon rate is 0%.",
        "TREASURY NOTE / BOND:  set Coupon frequency = Semiannual (US Treasuries pay coupons twice a year).",
        "Day-count basis is Actual/Actual (1) - the US Treasury convention.",
    ], last_col=LAST)
    r = common.legend(sh, r, LAST) + 1

    def field(label, name, value, role="input_l", fmt=None, note="", options=None):
        nonlocal r
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, value, role=role, fmt=fmt)
        sh.merge(r, 2, r, 3)
        if name:
            define_name(sh, name, r, 2)
        if options:
            common.dropdown(sh, r, 2, options)
        if note:
            sh.put(r, 4, note, role="note_l")
            sh.merge(r, 4, r, LAST)
        r += 1

    def sect(title):
        nonlocal r
        r = common.section(sh, r, title, c1=1, c2=LAST)

    sect("Security identification")
    field("Security name", "SecName", t.get("name"))
    field("CUSIP / ticker", "CUSIP", t.get("cusip"))
    field("Security type", "SecType", t.get("sec_type"), role="input_c", options=SEC_TYPES,
          note="Treasury Bill (zero-coupon), Treasury Note (2-10y), or Treasury Bond (20-30y).")
    field("Currency", "Ccy", t.get("currency"), role="input_c")

    sect("Economic terms")
    field("Face value (per bond)", "Face", t.get("face"), role="input", fmt=Fmt.PRICE,
          note="Prices are quoted per 100 face. Keep this 100.")
    field("Coupon rate (annual)", "CouponRate", t.get("coupon"), role="input", fmt=Fmt.PCT2,
          note="Fixed rate for notes/bonds. Use 0% for a Treasury Bill.")
    field("Coupon frequency", "FreqName", t.get("freq_name"), role="input_c", options=FREQUENCIES,
          note="Semiannual for notes/bonds; Zero-coupon for bills.")
    field("Day-count basis", "Basis", t.get("basis"), role="input_c", fmt=Fmt.INT,
          options=["0", "1", "2", "3", "4"], note="1 = Actual/Actual (Treasury convention).")
    field("Issue date", "IssueDate", t.get("issue"), role="input_c", fmt=Fmt.DATE)
    field("Settlement date", "Settle", t.get("settle"), role="input_c", fmt=Fmt.DATE,
          note="The date you buy/value the security.")
    field("Maturity date", "Maturity", t.get("maturity"), role="input_c", fmt=Fmt.DATE)
    field("Market clean price", "MktClean", t.get("mkt_clean"), role="input", fmt=Fmt.PRICE,
          note="Quoted price per 100 face (excludes accrued interest).")
    field("Benchmark Treasury yield", "BenchYield", t.get("bench_yield"), role="input", fmt=Fmt.PCT2,
          note="Yield of a Treasury of similar maturity (for the spread). Optional.")

    sect("Analyst")
    field("Analyst name", "Analyst", t.get("analyst"))
    field("Analysis date", "AnalysisDate", t.get("analysis_date"), role="input_c", fmt=Fmt.DATE)

    # ---- derived (auto) ----
    sect("Derived values (auto - do not edit)")
    sh.put(r, 1, "Zero-coupon?", role="label_b")
    sh.put(r, 2, '=IF(FreqName="Zero-coupon",1,0)', role="formula", fmt=Fmt.INT)
    define_name(sh, "IsZero", r, 2)
    sh.put(r, 4, "1 = bill / zero-coupon (only principal at maturity).", role="note_l")
    sh.merge(r, 4, r, LAST); r += 1
    sh.put(r, 1, "Payments per year", role="label_b")
    sh.put(r, 2, "=IF(IsZero=1,1,2)", role="formula", fmt=Fmt.INT)
    define_name(sh, "Freq", r, 2); r += 1
    sh.put(r, 1, "Effective coupon rate", role="label_b")
    sh.put(r, 2, "=IF(IsZero=1,0,CouponRate)", role="formula", fmt=Fmt.PCT2)
    define_name(sh, "EffCoupon", r, 2); r += 1
    sh.put(r, 1, "Day-count basis used", role="label_b")
    sh.put(r, 2, '=CHOOSE(Basis+1,"US 30/360","Actual/Actual","Actual/360","Actual/365","European 30/360")',
           role="formula_l"); sh.merge(r, 2, r, 3); r += 1
    sh.put(r, 1, "Years to maturity", role="label_b")
    sh.put(r, 2, "=YEARFRAC(Settle,Maturity,Basis)", role="formula", fmt=Fmt.YEARS)
    define_name(sh, "YearsToMat", r, 2); r += 1
    sh.put(r, 1, "Consistency check", role="label_b")
    sh.put(r, 2, '=IF(AND(SecType="Treasury Bill",FreqName<>"Zero-coupon"),"WARNING: a Treasury Bill must be Zero-coupon",'
                 'IF(AND(SecType<>"Treasury Bill",FreqName<>"Semiannual"),"WARNING: notes/bonds must be Semiannual","OK"))',
           role="status")
    define_name(sh, "FreqWarn", r, 2)
    sh.merge(r, 2, r, 3)
    common.traffic_light(sh, f"{common.col_letter(2)}{r}:{common.col_letter(2)}{r}", f"B{r}")
    r += 1

    sh.freeze("A6")
    sh.col_width(1, 24)
    for c in range(2, LAST + 1):
        sh.col_width(c, 15 if c <= 3 else 12)
    return sh
