"""Sheet 7: Issuer Financial Strength -- simple, optional credit ratios."""

from __future__ import annotations

from .. import common
from ..common import define_name
from ..config import Fmt

LAST = 6


def build(sh, ctx):
    d = ctx.data["issuer"]
    common.title_block(sh, "ISSUER FINANCIAL STRENGTH", "A few simple credit ratios (optional) - not a full model",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "OPTIONAL:  fill these to gauge the issuer's ability to pay. Leave blank if you only want bond math. "
        "Enter figures in the same currency units (e.g. millions).",
        "The ratios below tell you: how much debt vs earnings (leverage), whether earnings cover interest, and "
        "whether there is enough liquidity for near-term maturities.",
        "Guards:  if EBITDA or interest expense is zero/negative, ratios show N/A instead of breaking.",
    ], last_col=LAST)
    r += 1

    def inp(label, name, value, note=""):
        nonlocal r
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, value, role="input", fmt=Fmt.MONEY0)
        define_name(sh, name, r, 2)
        if note:
            sh.put(r, 4, note, role="note_l"); sh.merge(r, 4, r, LAST)
        r += 1

    r = common.section(sh, r, "Inputs  (issuer financials, e.g. $ millions)", c1=1, c2=LAST)
    inp("Revenue", "Revenue", d.get("revenue"))
    inp("EBITDA", "EBITDA", d.get("ebitda"))
    inp("EBIT", "EBIT", d.get("ebit"))
    inp("Cash & equivalents", "CashEq", d.get("cash"))
    inp("Total debt", "TotalDebt", d.get("total_debt"))
    inp("Short-term debt", "STDebt", d.get("st_debt"))
    inp("Long-term debt", "LTDebt", d.get("lt_debt"))
    inp("Interest expense", "IntExp", d.get("interest_expense"))
    inp("Operating cash flow", "OpCF", d.get("operating_cf"))
    inp("Capex", "Capex", d.get("capex"))
    inp("Available credit lines", "CreditLines", d.get("credit_lines"))
    inp("Debt due next 12 months", "DebtDue12m", d.get("debt_due_12m"))
    r += 1

    def calc(label, name, formula, fmt, note, role="output"):
        nonlocal r
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, formula, role=role, fmt=fmt)
        if name:
            define_name(sh, name, r, 2)
        sh.put(r, 4, note, role="note_l"); sh.merge(r, 4, r, LAST)
        r += 1

    r = common.section(sh, r, "Ratios (auto)", c1=1, c2=LAST)
    calc("Net debt", "NetDebt", "=TotalDebt-CashEq", Fmt.MONEY0, "Total debt minus cash.")
    calc("Net debt / EBITDA", "NetDebtEBITDA", '=IF(EBITDA<=0,"N/A",NetDebt/EBITDA)', Fmt.MULT,
         "Leverage. Lower is safer; very high is a red flag.")
    calc("EBITDA / interest", "EBITDACover", '=IF(IntExp<=0,"N/A",EBITDA/IntExp)', Fmt.MULT,
         "Interest coverage - ability to pay interest. Higher is safer.")
    calc("EBIT / interest", "EBITCover", '=IF(IntExp<=0,"N/A",EBIT/IntExp)', Fmt.MULT,
         "A more conservative interest-coverage measure.")
    calc("Free cash flow (FCF)", "FCF", "=OpCF-Capex", Fmt.MONEY0,
         "Cash left after capital spending - real cash to service debt.")
    calc("Liquidity", "Liquidity", "=CashEq+CreditLines", Fmt.MONEY0,
         "Cash plus committed credit lines.")
    calc("Liquidity coverage", "LiqCoverage",
         '=IF(DebtDue12m<=0,"No near-term debt maturities",Liquidity/DebtDue12m)', Fmt.MULT,
         "Liquidity vs debt due in the next 12 months. Below 1.0x is a concern.")
    r += 1

    r = common.section(sh, r, "Quick read", c1=1, c2=LAST)
    sh.put(r, 1, "Leverage", role="label_b")
    sh.put(r, 2, '=IF(EBITDA<=0,"N/A - EBITDA not positive",IF(NetDebtEBITDA>4,"High leverage",'
                 'IF(NetDebtEBITDA>2.5,"Moderate leverage","Low leverage")))', role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1
    sh.put(r, 1, "Interest coverage", role="label_b")
    sh.put(r, 2, '=IF(IntExp<=0,"N/A - no interest expense",IF(EBITDACover<1.5,"Weak coverage",'
                 'IF(EBITDACover<3,"Adequate coverage","Strong coverage")))', role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1
    sh.put(r, 1, "Liquidity", role="label_b")
    sh.put(r, 2, '=IF(DebtDue12m<=0,"No near-term maturities",IF(LiqCoverage<1,"Weak - liquidity below near-term debt",'
                 '"Adequate near-term liquidity"))', role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1

    sh.freeze("A6")
    sh.col_width(1, 24)
    sh.col_width(2, 14)
    sh.col_width(3, 4)
    for c in range(4, LAST + 1):
        sh.col_width(c, 15)
    return sh
