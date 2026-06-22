"""
Integrated Forecast Model (Sheet 5) — the core.

A complete 10-year three-statement forecast that reconciles WITHOUT a plug:
cash is the natural residual of a comprehensive cash-flow statement (which
captures the change in every non-cash balance-sheet item), equity rolls forward
by NI − dividends, and debt rolls forward by new debt − repayment. Interest is
charged on BEGINNING balances, so there are no circular references.

Because every line is wired into the cash flow, Assets = Liabilities + Equity
holds identically every year (the balance check is exactly 0). Cells are
registered in a first pass so the (legitimate) forward references — e.g. cash
referencing the cash-flow lines shown below it — resolve cleanly.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common

M = Fmt.MONEY


def build(sh, ctx):
    refs = ctx.refs
    N = ctx.fcst
    li = ctx.last_hist
    F = lambda k, t: refs.ref(f"f.{k}@{t}")     # noqa: E731
    A = lambda k, t: refs.ref(f"a.{k}@{t}")     # noqa: E731
    H = lambda k: refs.ref(f"h.{k}@{li}")       # noqa: E731

    def fc(t):
        return common.FIRST_COL + t  # t=0 anchor (col 2), t=1..N forecast

    last = fc(N)

    entries = [
        ("sec", "Income Statement Forecast"),
        ("line", "revenue", "Revenue", "output", ("hist", "revenue"),
         lambda t: f"={F('revenue', t-1)}*(1+{A('rev_growth', t)})"),
        ("line", "gross_profit", "Gross profit", "formula", ("hist", "gross_profit"),
         lambda t: f"={F('revenue', t)}*{A('gross_margin', t)}"),
        ("line", "cogs", "Cost of goods sold", "formula", ("hist", "cogs"),
         lambda t: f"={F('revenue', t)}-{F('gross_profit', t)}"),
        ("line", "ebitda", "EBITDA", "output", ("hist", "ebitda"),
         lambda t: f"={F('revenue', t)}*{A('ebitda_margin', t)}"),
        ("line", "opex", "Operating expenses", "formula", ("hist", "opex"),
         lambda t: f"={F('gross_profit', t)}-{F('ebitda', t)}"),
        ("line", "depreciation", "Depreciation & amortisation", "formula", ("hist", "depreciation"),
         lambda t: f"={F('revenue', t)}*{A('da_pct', t)}"),
        ("line", "ebit", "EBIT", "output", ("hist", "ebit"),
         lambda t: f"={F('ebitda', t)}-{F('depreciation', t)}"),
        ("line", "interest_expense", "Interest expense", "formula", ("hist", "interest_expense"),
         lambda t: f"={A('int_rate', t)}*{F('total_debt', t-1)}"),
        ("line", "interest_income", "Interest income (on cash)", "formula", ("zero",),
         lambda t: f"={A('cash_yield', t)}*{F('cash', t-1)}"),
        ("line", "pretax", "Pre-tax income", "formula", ("hist", "pretax"),
         lambda t: f"={F('ebit', t)}-{F('interest_expense', t)}+{F('interest_income', t)}"),
        ("line", "tax", "Tax expense", "formula", ("hist", "tax_expense"),
         lambda t: f"={A('tax_rate', t)}*{F('pretax', t)}"),
        ("line", "net_income", "Net income", "output", ("hist", "net_income"),
         lambda t: f"={F('pretax', t)}-{F('tax', t)}"),

        ("sec", "Balance Sheet Forecast — Assets"),
        ("line", "cash", "Cash & equivalents", "formula", ("hist", "cash"),
         lambda t: f"={F('cash', t-1)}+{F('cfo', t)}+{F('cfi', t)}+{F('cff', t)}"),
        ("line", "receivables", "Receivables", "formula", ("hist", "receivables"),
         lambda t: f"={A('dso', t)}/365*{F('revenue', t)}"),
        ("line", "inventory", "Inventory", "formula", ("hist", "inventory"),
         lambda t: f"={A('dio', t)}/365*{F('cogs', t)}"),
        ("line", "other_current_assets", "Other current assets", "formula", ("hist", "other_current_assets"),
         lambda t: f"=IFERROR({F('revenue', t)}*{H('other_current_assets')}/{H('revenue')},0)"),
        ("line", "ppe", "PP&E (net)", "formula", ("hist", "ppe"),
         lambda t: f"={F('ppe', t-1)}+{F('capex', t)}-{F('depreciation', t)}"),
        ("line", "intangibles", "Intangibles", "formula", ("hist", "intangibles"),
         lambda t: f"={F('intangibles', t-1)}"),
        ("line", "other_assets", "Other assets", "formula", ("hist", "other_assets"),
         lambda t: f"={A('oa_pct', t)}*{F('revenue', t)}"),
        ("line", "total_assets", "Total assets", "output", ("hist", "total_assets"),
         lambda t: "=" + "+".join(F(k, t) for k in ("cash", "receivables", "inventory",
                   "other_current_assets", "ppe", "intangibles", "other_assets"))),

        ("sec", "Balance Sheet Forecast — Liabilities & Equity"),
        ("line", "payables", "Payables", "formula", ("hist", "payables"),
         lambda t: f"={A('dpo', t)}/365*{F('cogs', t)}"),
        ("line", "short_term_debt", "Short-term debt", "formula", ("hist", "short_term_debt"),
         lambda t: f"={F('short_term_debt', t-1)}"),
        ("line", "long_term_debt", "Long-term debt", "formula", ("hist", "long_term_debt"),
         lambda t: f"={F('long_term_debt', t-1)}+{F('new_debt', t)}-{F('repayment', t)}"),
        ("line", "other_liabilities", "Other liabilities", "formula", ("hist", "other_liabilities"),
         lambda t: f"={A('ol_pct', t)}*{F('revenue', t)}"),
        ("line", "total_liabilities", "Total liabilities", "total", ("hist", "total_liabilities"),
         lambda t: "=" + "+".join(F(k, t) for k in ("payables", "short_term_debt",
                   "long_term_debt", "other_liabilities"))),
        ("line", "equity", "Shareholders' equity", "output", ("hist", "equity"),
         lambda t: f"={F('equity', t-1)}+{F('net_income', t)}-{F('dividends', t)}"),
        ("line", "total_liab_equity", "Total liabilities & equity", "total", ("hist", "total_liab_equity"),
         lambda t: f"={F('total_liabilities', t)}+{F('equity', t)}"),
        ("line", "balance_check", "Balance check  (must be 0)", "formula", ("zero",),
         lambda t: f"={F('total_assets', t)}-{F('total_liab_equity', t)}"),

        ("sec", "Cash Flow Forecast"),
        ("line", "dwc", "(−) Increase in working capital", "formula", ("zero",),
         lambda t: (f"=({F('receivables', t)}-{F('receivables', t-1)})+({F('inventory', t)}-{F('inventory', t-1)})"
                    f"+({F('other_current_assets', t)}-{F('other_current_assets', t-1)})"
                    f"-({F('payables', t)}-{F('payables', t-1)})-({F('other_liabilities', t)}-{F('other_liabilities', t-1)})")),
        ("line", "cfo", "Operating cash flow (CFO)", "output", ("hist", "operating_cash_flow"),
         lambda t: f"={F('net_income', t)}+{F('depreciation', t)}-{F('dwc', t)}"),
        ("line", "capex", "Capital expenditure", "formula", ("hist", "capex"),
         lambda t: f"={A('capex_pct', t)}*{F('revenue', t)}"),
        ("line", "cfi", "Investing cash flow (CFI)", "formula", ("zero",),
         lambda t: (f"=-{F('capex', t)}-({F('other_assets', t)}-{F('other_assets', t-1)})"
                    f"-({F('intangibles', t)}-{F('intangibles', t-1)})")),
        ("line", "cff", "Financing cash flow (CFF)", "formula", ("zero",),
         lambda t: (f"={F('new_debt', t)}-{F('repayment', t)}-{F('dividends', t)}"
                    f"+({F('short_term_debt', t)}-{F('short_term_debt', t-1)})")),
        ("line", "fcf", "Free cash flow (CFO − capex)", "output", ("hist", "fcf"),
         lambda t: f"={F('cfo', t)}-{F('capex', t)}"),

        ("sec", "Equity Roll-Forward"),
        ("line", "eq_begin", "Beginning equity", "formula", ("zero",), lambda t: f"={F('equity', t-1)}"),
        ("line", "eq_ni", "(+) Net income", "formula", ("zero",), lambda t: f"={F('net_income', t)}"),
        ("line", "dividends", "(−) Dividends", "formula", ("zero",),
         lambda t: f"={A('dividend_payout', t)}*MAX(0,{F('net_income', t)})"),
        ("line", "eq_end", "(=) Ending equity", "total", ("hist", "equity"), lambda t: f"={F('equity', t)}"),

        ("sec", "Debt Roll-Forward"),
        ("line", "dt_begin", "Beginning long-term debt", "formula", ("zero",), lambda t: f"={F('long_term_debt', t-1)}"),
        ("line", "new_debt", "(+) New debt raised", "formula", ("zero",), lambda t: f"={A('new_debt', t)}"),
        ("line", "repayment", "(−) Debt repayment", "formula", ("zero",),
         lambda t: f"={A('debt_repay_pct', t)}*{F('long_term_debt', t-1)}"),
        ("line", "dt_end", "(=) Ending long-term debt", "total", ("hist", "long_term_debt"), lambda t: f"={F('long_term_debt', t)}"),
        ("line", "total_debt", "Total debt (memo)", "formula", ("hist", "total_debt"),
         lambda t: f"={F('short_term_debt', t)}+{F('long_term_debt', t)}"),
    ]

    common.title_block(sh, "INTEGRATED FORECAST MODEL",
                       "A fully-reconciled 10-year three-statement forecast — no plugs, no circularity",
                       last_col=last)
    common.nav_bar(sh, 5)
    r = 7
    sh.put(r, 1, "Active method # / scenario #:", role="label")
    sh.put(r, 2, "=Method", role="formula", fmt=Fmt.INT)
    sh.put(r, 3, "=Scenario", role="formula", fmt=Fmt.INT)
    sh.put(r, 4, common.units_note(ctx), role="note")
    sh.merge(r, 4, r, last)
    r += 1
    sh.put(r, 1, "Line item", role="colhdr")
    sh.put(r, common.FIRST_COL, f"{ctx.hist_periods[li]} (base)", role="colhdr_r")
    for t in range(1, N + 1):
        sh.put(r, fc(t), ctx.fcst_periods[t - 1], role="colhdr_r")
    header_row = r
    r += 1

    # pass 1: assign rows & register cells (enables forward references)
    rows = []
    rr = r
    for e in entries:
        rows.append(rr)
        if e[0] == "line":
            for t in range(N + 1):
                refs.put(f"f.{e[1]}@{t}", sh.name, sh.coord(rr, fc(t)))
        rr += 1

    # pass 2: write labels, anchors, formulas
    for e, row in zip(entries, rows):
        if e[0] == "sec":
            common.section(sh, row, e[1], c1=1, c2=last)
            continue
        _, key, label, role, anchor, builder = e
        sh.put(row, 1, label, role=("label_b" if role in ("output", "total") else "label"))
        if anchor[0] == "hist":
            sh.put(row, fc(0), f"={H(anchor[1])}", role="formula", fmt=M)
        elif anchor[0] == "zero":
            sh.put(row, fc(0), 0, role="formula", fmt=M)
        for t in range(1, N + 1):
            sh.put(row, fc(t), builder(t), role=role, fmt=M)

    sh.freeze(f"C{header_row + 1}")
    sh.col_width(1, 32)
    sh.col_width(common.FIRST_COL, 12)
    for t in range(1, N + 1):
        sh.col_width(fc(t), 11)
    return sh
