"""Sheet 2: Bond Terms -- the only place most inputs are typed. Defines named ranges."""

from __future__ import annotations

from .. import common
from ..common import define_name
from ..config import FREQUENCIES, Fmt

LAST = 7


def build(sh, ctx):
    t = ctx.data["terms"]
    common.title_block(sh, "BOND TERMS", "Type the bond's details here. Every other sheet reads from this page.",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "WHAT TO DO:  fill the yellow cells with your bond's terms. Use the drop-downs for coupon frequency, "
        "day-count basis and callable. Everything else in the workbook updates automatically.",
        "ZERO-COUPON:  set Coupon frequency = Zero-coupon; the coupon rate is then ignored.",
        "NOT CALLABLE:  set Callable = No; the call date and call price are then ignored.",
    ], last_col=LAST)
    r = common.legend(sh, r, LAST) + 1

    def field(label, name, value, role="input_l", fmt=None, note="", options=None):
        nonlocal r
        sh.put(r, 1, label, role="label_b")
        c = sh.put(r, 2, value, role=role, fmt=fmt)
        sh.merge(r, 2, r, 3)
        if name:
            define_name(sh, name, r, 2)
        if options:
            common.dropdown(sh, r, 2, options)
        if note:
            sh.put(r, 4, note, role="note_l")
            sh.merge(r, 4, r, LAST)
        r += 1
        return c

    def sect(title):
        nonlocal r
        r = common.section(sh, r, title, c1=1, c2=LAST)

    sect("Bond identification")
    field("Issuer name", "Issuer", t.get("issuer"))
    field("Bond name / ticker", "BondName", t.get("bond_name"))
    field("ISIN", "ISIN", t.get("isin"))
    field("Currency", "Ccy", t.get("currency"), role="input_c")
    field("Sector", "Sector", t.get("sector"))
    field("Credit rating", "Rating", t.get("rating"), role="input_c",
          note="e.g. AAA, AA, A, BBB, BB, B (BBB- and above = investment grade).")
    field("Seniority", "Seniority", t.get("seniority"), role="input_c",
          options=["Senior", "Subordinated", "Junior"])
    field("Secured / unsecured", "Secured", t.get("secured"), role="input_c",
          options=["Secured", "Unsecured"])

    sect("Economic terms")
    field("Face value (per bond)", "Face", t.get("face"), role="input", fmt=Fmt.PRICE,
          note="Prices are quoted per 100 face (market convention). Keep this 100.")
    field("Coupon rate (annual)", "CouponRate", t.get("coupon"), role="input", fmt=Fmt.PCT2,
          note="Fixed annual rate. Ignored if Zero-coupon.")
    field("Coupon frequency", "FreqName", t.get("freq_name"), role="input_c",
          options=FREQUENCIES, note="Annual=1, Semiannual=2, Quarterly=4, or Zero-coupon.")
    field("Day-count basis", "Basis", t.get("basis"), role="input_c", fmt=Fmt.INT,
          options=["0", "1", "2", "3", "4"],
          note="0=US 30/360, 1=Actual/Actual, 2=Actual/360, 3=Actual/365, 4=European 30/360.")
    field("Issue date", "IssueDate", t.get("issue"), role="input_c", fmt=Fmt.DATE)
    field("Settlement date", "Settle", t.get("settle"), role="input_c", fmt=Fmt.DATE,
          note="The date you buy/value the bond (today, or trade settlement).")
    field("Maturity date", "Maturity", t.get("maturity"), role="input_c", fmt=Fmt.DATE)
    field("Market clean price", "MktClean", t.get("mkt_clean"), role="input", fmt=Fmt.PRICE,
          note="Quoted price per 100 face (excludes accrued interest).")
    field("Benchmark govt yield", "BenchYield", t.get("bench_yield"), role="input", fmt=Fmt.PCT2,
          note="Yield of a government bond of similar maturity (for the spread).")

    sect("Call features")
    field("Callable?", "CallableFlag", t.get("callable"), role="input_c", options=["Yes", "No"])
    field("Call date", "CallDate", t.get("call_date"), role="input_c", fmt=Fmt.DATE,
          note="Ignored if Callable = No.")
    field("Call price", "CallPrice", t.get("call_price"), role="input", fmt=Fmt.PRICE,
          note="Price the issuer pays if it calls the bond early. Ignored if Callable = No.")

    sect("Analyst")
    field("Analyst name", "Analyst", t.get("analyst"))
    field("Analysis date", "AnalysisDate", t.get("analysis_date"), role="input_c", fmt=Fmt.DATE)

    # ---- derived values (auto) ----
    sect("Derived values  (auto - do not edit)")
    sh.put(r, 1, "Payments per year", role="label_b")
    sh.put(r, 2, '=IF(FreqName="Annual",1,IF(FreqName="Semiannual",2,IF(FreqName="Quarterly",4,1)))',
           role="formula", fmt=Fmt.INT)
    define_name(sh, "Freq", r, 2)
    sh.put(r, 4, "Coupons per year used by all calculations (Zero-coupon uses 1 for date steps).", role="note_l")
    sh.merge(r, 4, r, LAST); r += 1

    sh.put(r, 1, "Zero-coupon?", role="label_b")
    sh.put(r, 2, '=IF(FreqName="Zero-coupon",1,0)', role="formula", fmt=Fmt.INT)
    define_name(sh, "IsZero", r, 2)
    sh.put(r, 4, "1 = zero-coupon (no coupons; only principal at maturity).", role="note_l")
    sh.merge(r, 4, r, LAST); r += 1

    sh.put(r, 1, "Effective coupon rate", role="label_b")
    sh.put(r, 2, "=IF(IsZero=1,0,CouponRate)", role="formula", fmt=Fmt.PCT2)
    define_name(sh, "EffCoupon", r, 2); r += 1

    sh.put(r, 1, "Day-count basis used", role="label_b")
    sh.put(r, 2, '=CHOOSE(Basis+1,"US 30/360","Actual/Actual","Actual/360","Actual/365","European 30/360")',
           role="formula_l"); sh.merge(r, 2, r, 3); r += 1

    sh.put(r, 1, "Years to maturity", role="label_b")
    sh.put(r, 2, "=YEARFRAC(Settle,Maturity,Basis)", role="formula", fmt=Fmt.YEARS)
    define_name(sh, "YearsToMat", r, 2); r += 1

    sh.put(r, 1, "Years to call", role="label_b")
    sh.put(r, 2, '=IF(CallableFlag="Yes",YEARFRAC(Settle,CallDate,Basis),"n/a")', role="formula", fmt=Fmt.YEARS)
    define_name(sh, "YearsToCall", r, 2); r += 1

    sh.freeze("A6")
    sh.col_width(1, 24)
    for c in range(2, LAST + 1):
        sh.col_width(c, 15 if c <= 3 else 12)
    return sh
