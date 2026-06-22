"""
Historical Financial Statements (the ACTUAL layer).

Every financial figure on this sheet is a hard-coded blue INPUT -- pasted in from
the filings, never reconstructed by a formula. That includes the subtotals
(gross profit, EBITDA, EBIT, net income, total assets, total liabilities): if it
appears in a report, it is typed here exactly as reported. This is the crisp
"historical = input" half of the model.

The only formulas on the sheet are audit CHECKS (do the pasted statements tie?)
and the auto-detected TIMELINE: the model counts the reported years and derives
``LastActual``; the Forecast sheet begins the year after it. Add a new column of
actuals and the whole forecast shifts forward automatically -- no other edits.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..common import FIRST_COL, FY_FMT
from ..sample_data import (BALANCE_ASSETS, BALANCE_LE, CASHFLOW_LINES, INCOME_LINES)

M = Fmt.MONEY
LBL = 1

LABELS = {
    "revenue": "Revenue", "cogs": "Cost of goods sold", "gross_profit": "Gross profit",
    "opex": "Operating expenses (ex-D&A)", "ebitda": "EBITDA",
    "depreciation": "Depreciation & amortisation", "ebit": "EBIT",
    "net_interest": "Net interest expense", "pretax": "Pre-tax income",
    "tax": "Tax expense", "net_income": "Net income",
    "cash": "Cash & equivalents", "nwc": "Net working capital",
    "net_ppe": "Net PP&E", "other_assets": "Other assets", "total_assets": "Total assets",
    "total_debt": "Total debt", "other_liabilities": "Other liabilities",
    "total_liabilities": "Total liabilities", "equity": "Shareholders' equity",
    "operating_cash_flow": "Operating cash flow", "capex": "Capital expenditure",
    "fcf": "Free cash flow",
}
SUBTOTALS = {"gross_profit", "ebitda", "ebit", "net_income", "total_assets",
             "total_liabilities", "fcf"}


def build(sh, ctx):
    refs = ctx.refs
    slots = ctx.hist_slots
    na = ctx.actual_years
    last_col = FIRST_COL + slots - 1
    series = ctx.data["hist"]

    common.title_block(sh, "HISTORICAL FINANCIAL STATEMENTS  (ACTUAL)",
                       "Reported results -- every figure is a hard-coded input pasted from the filings",
                       last_col=last_col)
    common.nav_bar(sh, 5)
    sh.put(7, 1, common.units_note(ctx), role="note")
    sh.merge(7, 1, 7, last_col)

    # ---- timeline panel (auto-detected); formulas filled after the grid -----
    common.section(sh, 8, "Timeline  -  auto-detected (the forecast begins the year after the last actual)",
                   c1=1, c2=last_col)
    sh.put(9, 1, "First fiscal year", role="label_b")
    sh.put(9, 3, ctx.first_year, role="input", fmt=Fmt.INT, key="t.first_year")
    common.define_name(sh, "FirstYear", 9, 3)
    sh.put(9, 5, "Type the first reported year here (e.g. 2015). Everything else keys off it.",
           role="note_l"); sh.merge(9, 5, 9, last_col)
    sh.put(10, 1, "Reported years detected", role="label")
    sh.put(11, 1, "Last actual year", role="label_b")
    common.define_name(sh, "LastActual", 11, 3)
    sh.put(12, 1, "Forecast begins (next year)", role="label_b")
    sh.put(12, 5, "The Forecast sheet starts here automatically.", role="note_l")
    sh.merge(12, 5, 12, last_col)

    # ---- year header + status tag ------------------------------------------
    yr_row = 14
    sh.put(yr_row, LBL, "Fiscal year", role="colhdr")
    for j in range(slots):
        col = FIRST_COL + j
        f = "=FirstYear" if j == 0 else f"={sh.local(yr_row, col - 1)}+1"
        sh.put(yr_row, col, f, role="actual_hdr", fmt=FY_FMT, key=f"t.year@{j}")
    tag_row = yr_row + 1
    sh.put(tag_row, LBL, "Status", role="sublabel")
    for j in range(slots):
        col = FIRST_COL + j
        sh.put(tag_row, col, f'=IF({sh.local(yr_row, col)}<=LastActual,"Actual","- spare -")',
               role="actual_tag")

    r = tag_row + 1
    rev_row = None

    def line(key, *, label=None, kind="input", bold=None):
        nonlocal r, rev_row
        label = label or LABELS[key]
        is_bold = (key in SUBTOTALS) if bold is None else bold
        sh.put(r, LBL, label, role=("label_b" if is_bold else "label"))
        if key == "revenue":
            rev_row = r
        for j in range(slots):
            col = FIRST_COL + j
            if kind == "input":
                val = series.get(key, [None] * na)[j] if j < na else None
                sh.put(r, col, val, role="input", fmt=M, key=f"h.{key}@{j}")
            else:
                sh.put(r, col, kind(j), role="formula", fmt=M, key=f"h.{key}@{j}")
        r += 1

    def sect(t):
        nonlocal r
        r = common.section(sh, r, t, c1=1, c2=last_col)

    H = lambda k, j: refs.ref(f"h.{k}@{j}")  # noqa: E731

    sect("Income Statement")
    for k in INCOME_LINES:
        line(k)

    sect("Balance Sheet  -  Assets")
    for k in BALANCE_ASSETS:
        line(k)
    sect("Balance Sheet  -  Liabilities & Equity")
    for k in BALANCE_LE:
        line(k)
    line("total_liab_equity", label="Total liabilities & equity", bold=True,
         kind=lambda j: f"={H('total_liabilities', j)}+{H('equity', j)}")

    sect("Cash Flow Statement")
    for k in CASHFLOW_LINES:
        line(k)

    sect("Audit Checks  (every value should be 0 -- they confirm the pasted statements tie)")
    line("balance_check", label="Balance check  (assets - (liabilities + equity))", bold=True,
         kind=lambda j: f"={H('total_assets', j)}-{H('total_liab_equity', j)}")
    line("asset_check", label="Asset build check  (components - total assets)", bold=False,
         kind=lambda j: "=" + "+".join(H(k, j) for k in
         ("cash", "nwc", "net_ppe", "other_assets")) + f"-{H('total_assets', j)}")
    line("liab_check", label="Liability build check  (components - total liabilities)", bold=False,
         kind=lambda j: f"={H('total_debt', j)}+{H('other_liabilities', j)}-{H('total_liabilities', j)}")
    last_row = r - 1

    # ---- fill the timeline formulas now the revenue range is known ---------
    rev_rng = refs.range("h.revenue@0", f"h.revenue@{slots - 1}")
    sh.put(10, 3, f"=COUNT({rev_rng})", role="formula", fmt=Fmt.INT, key="t.count")
    sh.put(11, 3, f"=FirstYear+{refs.ref('t.count')}-1", role="output", fmt=FY_FMT, key="t.last_actual")
    sh.put(12, 3, "=LastActual+1", role="output", fmt=FY_FMT, key="t.fcst_start")

    # ---- distinct shading: blue = live actual column, grey = empty spare ----
    block = f"{sh.coord(tag_row, FIRST_COL)}:{sh.coord(last_row, last_col)}"
    common.shade_by_status(sh, block, f"{common.col_letter(FIRST_COL)}${yr_row}")

    sh.freeze(f"B{tag_row + 1}")
    sh.col_width(LBL, 34)
    for j in range(slots):
        sh.col_width(FIRST_COL + j, 10)
    return sh
