"""
Historical Financial Statements (Sheet 2).

Ten years of statements: granular reported lines are blue inputs; subtotals are
black formulas; a few reusable helper rows (total/net debt, invested capital,
two-point averages) feed the Analysis and Assumptions sheets. A balance check
row confirms the entered balance sheet ties.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..formulas import add, avg2, diff, summ

LBL = 1
M = Fmt.MONEY


def build(sh, ctx):
    refs = ctx.refs
    n = ctx.hist
    last = ctx.hcol(n - 1)
    R = lambda k, i: refs.ref(f"h.{k}@{i}")     # noqa: E731

    common.title_block(sh, "HISTORICAL FINANCIAL STATEMENTS",
                       "Ten years of reported results — the manual data-entry layer", last_col=last)
    common.nav_bar(sh, 5)
    r = 7
    sh.put(r, 1, common.units_note(ctx), role="note")
    sh.merge(r, 1, r, last)
    r += 1
    r = common.hist_headers(sh, ctx, r, label="Line item", split=False)
    sh.freeze(f"B{r}")
    common.setup_cols(sh, ctx, split=False)

    def row(key, label, kind, builder=None, fmt=M, total=False):
        nonlocal r
        sh.put(r, LBL, label, role=("label_b" if total else "label"))
        for i in range(n):
            col = ctx.hcol(i)
            if kind == "input":
                sh.put(r, col, ctx.data["series"].get(key, [None] * n)[i], role="input", fmt=fmt,
                       key=f"h.{key}@{i}")
            else:
                sh.put(r, col, builder(i), role=("total" if total else "formula"), fmt=fmt,
                       key=f"h.{key}@{i}")
        r += 1

    def sect(t):
        nonlocal r
        r = common.section(sh, r, t, c1=1, c2=last)

    sect("Income Statement")
    row("revenue", "Revenue", "input", total=True)
    row("cogs", "Cost of goods sold", "input")
    row("gross_profit", "Gross profit", "calc", lambda i: diff(R("revenue", i), R("cogs", i)))
    row("opex", "Operating expenses (ex-D&A)", "input")
    row("ebitda", "EBITDA", "calc", lambda i: diff(R("gross_profit", i), R("opex", i)), total=True)
    row("depreciation", "Depreciation & amortisation", "input")
    row("ebit", "EBIT", "calc", lambda i: diff(R("ebitda", i), R("depreciation", i)), total=True)
    row("interest_expense", "Interest expense", "input")
    row("pretax", "Pre-tax income", "calc", lambda i: diff(R("ebit", i), R("interest_expense", i)))
    row("tax_expense", "Tax expense", "input")
    row("net_income", "Net income", "calc", lambda i: diff(R("pretax", i), R("tax_expense", i)), total=True)

    sect("Balance Sheet — Assets")
    for k, lab in (("cash", "Cash & equivalents"), ("receivables", "Receivables"),
                   ("inventory", "Inventory"), ("other_current_assets", "Other current assets"),
                   ("ppe", "PP&E (net)"), ("intangibles", "Intangibles"), ("other_assets", "Other assets")):
        row(k, lab, "input")
    row("total_assets", "Total assets", "calc", total=True,
        builder=lambda i: summ([R(k, i) for k in ("cash", "receivables", "inventory",
                                                  "other_current_assets", "ppe", "intangibles", "other_assets")]))

    sect("Balance Sheet — Liabilities & Equity")
    for k, lab in (("payables", "Payables"), ("short_term_debt", "Short-term debt"),
                   ("long_term_debt", "Long-term debt"), ("other_liabilities", "Other liabilities")):
        row(k, lab, "input")
    row("total_liabilities", "Total liabilities", "calc", total=True,
        builder=lambda i: summ([R(k, i) for k in ("payables", "short_term_debt", "long_term_debt", "other_liabilities")]))
    row("equity", "Shareholders' equity", "input", total=True)
    row("total_liab_equity", "Total liabilities & equity", "calc", total=True,
        builder=lambda i: add(R("total_liabilities", i), R("equity", i)))
    row("balance_check", "Balance check (A − (L+E))", "calc",
        builder=lambda i: diff(R("total_assets", i), R("total_liab_equity", i)))

    sect("Cash Flow Statement")
    row("operating_cash_flow", "Operating cash flow", "input", total=True)
    row("capex", "Capital expenditure", "input")
    row("fcf", "Free cash flow", "calc", lambda i: diff(R("operating_cash_flow", i), R("capex", i)), total=True)

    sect("Helper Calculations  (reused by Analysis, Assumptions & Forecast)")
    row("total_debt", "Total debt", "calc", lambda i: add(R("short_term_debt", i), R("long_term_debt", i)))
    row("net_debt", "Net debt", "calc", lambda i: diff(R("total_debt", i), R("cash", i)))
    row("invested_capital", "Invested capital (equity + debt − cash)", "calc",
        builder=lambda i: f"={R('equity', i)}+{R('total_debt', i)}-{R('cash', i)}")
    row("nwc", "Net working capital", "calc",
        builder=lambda i: f"={R('receivables', i)}+{R('inventory', i)}+{R('other_current_assets', i)}-{R('payables', i)}-{R('other_liabilities', i)}")
    for key, src, lab in (("avg_equity", "equity", "Average equity"),
                          ("avg_assets", "total_assets", "Average total assets"),
                          ("avg_ic", "invested_capital", "Average invested capital"),
                          ("avg_receivables", "receivables", "Average receivables"),
                          ("avg_inventory", "inventory", "Average inventory"),
                          ("avg_payables", "payables", "Average payables")):
        sh.put(r, LBL, "  " + lab, role="sublabel")
        for i in range(n):
            col = ctx.hcol(i)
            sh.put(r, col, (None if i == 0 else avg2(R(src, i - 1), R(src, i))),
                   role="formula", fmt=M, key=f"h.{key}@{i}")
        r += 1
    return sh
