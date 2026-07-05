"""Sheet 1: Inputs / Bond Terms -- the only input page. Defines named ranges."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import define_name
from ..config import FREQUENCIES, OUTLOOKS, SEC_TYPES

LAST = 7


def build(sh, ctx):
    t = ctx.data["terms"]
    common.title_block(sh, "INPUTS / BOND TERMS", "Enter the government bond's details here", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "THESE INPUTS DRIVE THE ENTIRE MODEL.  Only change the yellow cells - every calculation on the other sheets "
        "updates automatically. You never edit the green/black output cells.",
        "For a Treasury Bill or a zero-coupon bond, set Coupon frequency = Zero-coupon and Coupon rate = 0%; the model "
        "then values it as a single principal payment at maturity.",
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

    sect("Identification")
    field("Bond name", "BondName", t.get("name"))
    field("Country / issuer", "Issuer", t.get("issuer"))
    field("Currency", "Ccy", t.get("currency"), role="input_c")
    field("Security type", "SecType", t.get("sec_type"), role="input_c", options=SEC_TYPES,
          note="Bill = zero-coupon; Note/Bond = fixed coupon; Government Bond = generic sovereign.")

    sect("Economic terms")
    field("Face value", "Face", t.get("face"), role="input", fmt=Fmt.PRICE,
          note="Prices are quoted per 100 face. Keep this 100.")
    field("Position size / market value", "PosSize", t.get("position"), role="input", fmt=Fmt.MONEY0,
          note="Optional - your holding's face amount (used only for information).")
    field("Coupon rate (annual)", "CouponRate", t.get("coupon"), role="input", fmt=Fmt.PCT2,
          note="Fixed annual rate. Use 0% for a bill / zero-coupon bond.")
    field("Coupon frequency", "FreqName", t.get("freq_name"), role="input_c", options=FREQUENCIES,
          note="Semiannual, Annual, or Zero-coupon.")
    field("Day-count basis", "Basis", t.get("basis"), role="input_c", fmt=Fmt.INT,
          options=["0", "1", "2", "3", "4"], note="1 = Actual/Actual (usual government convention).")
    field("Issue date", "IssueDate", t.get("issue"), role="input_c", fmt=Fmt.DATE)
    field("Settlement date", "Settle", t.get("settle"), role="input_c", fmt=Fmt.DATE,
          note="The date you value / buy the bond.")
    field("Maturity date", "Maturity", t.get("maturity"), role="input_c", fmt=Fmt.DATE)

    sect("Market data")
    field("Market clean price", "MktClean", t.get("mkt_clean"), role="input", fmt=Fmt.PRICE,
          note="Quoted price per 100 face (drives the implied yield).")
    field("Market yield to maturity", "MktYTM", t.get("mkt_ytm"), role="input", fmt=Fmt.PCT2,
          note="Optional. A yield you want to cross-check against the implied yield.")
    field("Benchmark yield (similar maturity)", "BenchYield", t.get("bench_yield"), role="input", fmt=Fmt.PCT2,
          note="Yield of a similar-maturity government bond (for the spread and the 'fair price' test).")

    sect("Analyst")
    field("Rate outlook", "RateOutlook", t.get("outlook"), role="input_c", options=OUTLOOKS,
          note="Your view on where yields go next - used by the attractiveness score.")
    field("Analyst name", "Analyst", t.get("analyst"))
    field("Analysis date", "AnalysisDate", t.get("analysis_date"), role="input_c", fmt=Fmt.DATE)

    sect("Derived values (auto - do not edit)")
    sh.put(r, 1, "Zero-coupon?", role="label_b")
    sh.put(r, 2, '=IF(OR(FreqName="Zero-coupon",SecType="Treasury Bill"),1,0)', role="formula", fmt=Fmt.INT)
    define_name(sh, "IsZero", r, 2)
    sh.put(r, 4, "1 = no coupons (bill / zero-coupon); only principal at maturity.", role="note_l")
    sh.merge(r, 4, r, LAST); r += 1
    sh.put(r, 1, "Payments per year", role="label_b")
    sh.put(r, 2, '=IF(IsZero=1,1,IF(FreqName="Annual",1,2))', role="formula", fmt=Fmt.INT)
    define_name(sh, "Freq", r, 2); r += 1
    sh.put(r, 1, "Effective coupon rate", role="label_b")
    sh.put(r, 2, "=IF(IsZero=1,0,CouponRate)", role="formula", fmt=Fmt.PCT2)
    define_name(sh, "EffCoupon", r, 2); r += 1
    sh.put(r, 1, "Years to maturity", role="label_b")
    sh.put(r, 2, "=YEARFRAC(Settle,Maturity,Basis)", role="formula", fmt=Fmt.YEARS)
    define_name(sh, "YearsToMat", r, 2); r += 1
    sh.put(r, 1, "Consistency check", role="label_b")
    sh.put(r, 2, '=IF(AND(OR(SecType="Treasury Bill",FreqName="Zero-coupon"),CouponRate>0),'
                 '"WARNING: set coupon rate to 0% for a bill / zero-coupon bond","OK")', role="status")
    define_name(sh, "InputWarn", r, 2)
    sh.merge(r, 2, r, 4)
    common.traffic_light(sh, f"B{r}:B{r}", f"B{r}")
    r += 1

    sh.freeze("A6")
    sh.col_width(1, 26)
    for c in range(2, LAST + 1):
        sh.col_width(c, 15 if c <= 3 else 12)
    return sh
