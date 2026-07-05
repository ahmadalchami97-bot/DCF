"""Sheet 2: Inputs / Bond Terms -- the only input page. Defines named ranges."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import define_name
from ..config import FREQUENCIES, OUTLOOKS, SEC_TYPES

LAST = 7


def build(sh, ctx):
    t = ctx.data["terms"]
    common.title_block(sh, "INPUTS / BOND TERMS", "Enter your bond here - this is the only page you type on",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "THESE INPUTS DRIVE THE WHOLE WORKBOOK.  Change only the yellow cells; every other sheet updates by itself.",
        "For a Treasury Bill or a zero-coupon bond: set Coupon frequency = Zero-coupon and Coupon rate = 0%. The bond "
        "then has a single payment - the principal at maturity.",
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
    field("Bond name", "BondName", t.get("name"), note="Whatever you want to call this bond.")
    field("Country / issuer", "Issuer", t.get("issuer"), note="Who borrowed the money (e.g. the US Treasury).")
    field("Currency", "Ccy", t.get("currency"), role="input_c")
    field("Security type", "SecType", t.get("sec_type"), role="input_c", options=SEC_TYPES,
          note="Bill = zero-coupon; Note/Bond = pays coupons; Government Bond = generic sovereign.")

    sect("Economic terms")
    field("Face value", "Face", t.get("face"), role="input", fmt=Fmt.PRICE,
          note="The amount repaid at maturity. Prices are quoted per 100 face - keep this 100.")
    field("Position size (optional)", "PosSize", t.get("position"), role="input", fmt=Fmt.MONEY0,
          note="How much face value you hold. Optional - used only to show money amounts.")
    field("Coupon rate (annual)", "Cpn", t.get("coupon"), role="input", fmt=Fmt.PCT2,
          note="The annual interest rate the bond pays. Use 0% for a bill / zero-coupon bond.")
    field("Coupon frequency", "FreqName", t.get("freq_name"), role="input_c", options=FREQUENCIES,
          note="How often coupons are paid: Semiannual (twice a year), Annual, or Zero-coupon.")
    field("Day-count basis", "Basis", t.get("basis"), role="input_c", fmt=Fmt.INT,
          options=["0", "1", "2", "3", "4"], note="How days are counted. 1 = Actual/Actual (usual for governments).")
    field("Issue date", "IssueDate", t.get("issue"), role="input_c", fmt=Fmt.DATE,
          note="When the bond was first sold.")
    field("Settlement date", "Settle", t.get("settle"), role="input_c", fmt=Fmt.DATE,
          note="The date you buy / value the bond (usually today).")
    field("Maturity date", "Mat", t.get("maturity"), role="input_c", fmt=Fmt.DATE,
          note="The date the government repays the principal.")

    sect("Market data")
    field("Market clean price", "MktClean", t.get("mkt_clean"), role="input", fmt=Fmt.PRICE,
          note="The quoted market price per 100 face. Drives the yield.")
    field("Market yield to maturity", "MktYTM", t.get("mkt_ytm"), role="input", fmt=Fmt.PCT2,
          note="Optional. A yield you want to cross-check against the calculated one.")
    field("Benchmark yield (similar maturity)", "BenchYield", t.get("bench_yield"), role="input", fmt=Fmt.PCT2,
          note="The comparable government market yield, for the spread.")

    sect("Analyst")
    field("Rate outlook", "RateOutlook", t.get("outlook"), role="input_c", options=OUTLOOKS,
          note="Your view on where yields go next - used by the attractiveness score.")
    field("Analyst name", "Analyst", t.get("analyst"))
    field("Analysis date", "AnalysisDate", t.get("analysis_date"), role="input_c", fmt=Fmt.DATE)

    sect("Derived values (auto - do not edit)")
    sh.put(r, 1, "Zero-coupon?", role="label_b")
    sh.put(r, 2, '=IF(OR(FreqName="Zero-coupon",SecType="Treasury Bill"),1,0)', role="formula", fmt=Fmt.INT)
    define_name(sh, "IsZero", r, 2)
    sh.put(r, 4, "1 = no coupons; only principal at maturity.", role="note_l"); sh.merge(r, 4, r, LAST); r += 1
    sh.put(r, 1, "Payments per year", role="label_b")
    sh.put(r, 2, '=IF(IsZero=1,1,IF(FreqName="Annual",1,2))', role="formula", fmt=Fmt.INT)
    define_name(sh, "Freq", r, 2); r += 1
    sh.put(r, 1, "Effective coupon rate", role="label_b")
    sh.put(r, 2, "=IF(IsZero=1,0,Cpn)", role="formula", fmt=Fmt.PCT2)
    define_name(sh, "EffCoupon", r, 2); r += 1
    sh.put(r, 1, "Years to maturity", role="label_b")
    sh.put(r, 2, "=YEARFRAC(Settle,Mat,Basis)", role="formula", fmt=Fmt.YEARS)
    define_name(sh, "YrsToMat", r, 2); r += 1
    sh.put(r, 1, "Consistency check", role="label_b")
    sh.put(r, 2, '=IF(AND(OR(SecType="Treasury Bill",FreqName="Zero-coupon"),Cpn>0),'
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
