"""
Inputs sheet (Sheet 3) -- the single data-entry layer.

Holds 10 historical + 5 forecast years of raw financial statement inputs (yellow),
the subtotals the model derives from them (blue formulas), and a reusable
"Helper Calculations" block (averages, totals, NOPAT, invested capital, EV, etc.)
that every ratio sheet links to -- so each ratio is one short, auditable formula
referencing already-computed cells. Everything is registered as ``in.<key>@<i>``.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..formulas import add, avg2, diff, div, product, summ

LBL, FY0 = 1, 2
M, P, X = Fmt.MONEY, Fmt.PER_SHARE, Fmt.PCT


def build(sh, ctx: common.Context):
    refs = ctx.refs
    n = ctx.n_years
    last = ctx.last_year_col
    R = lambda k, i: refs.ref(f"in.{k}@{i}")     # noqa: E731

    common.title_block(sh, "RAW FINANCIAL INPUTS",
                       "10 historical + 5 forecast years — the single data-entry layer",
                       last_col=last)
    common.nav_bar(sh, 5, exclude={"Home"})
    r = 7
    sh.put(r, 1, common.units_note(ctx), role="note")
    sh.merge(r, 1, r, last)
    r += 1
    r = common.year_headers(sh, ctx, r)
    sh.freeze(f"B{r}")

    def row(key, label, kind, fmt=M, builder=None, total=False):
        nonlocal r
        role = "label_b" if total else "label"
        sh.put(r, LBL, label, role=role)
        for i in range(n):
            col = ctx.year_col(i)
            if kind == "input":
                val = ctx.data["series"].get(key, [None] * n)[i]
                sh.put(r, col, val, role="input", fmt=fmt, key=f"in.{key}@{i}")
            else:
                sh.put(r, col, builder(i), role=("output" if total else "formula"),
                       fmt=fmt, key=f"in.{key}@{i}")
        r += 1

    def sect(text):
        nonlocal r
        r = common.section(sh, r, text, c1=1, c2=last)

    # ---- income statement ----
    sect("Income Statement")
    row("revenue", "Revenue", "input", total=True)
    row("cogs", "Cost of goods sold", "input")
    row("gross_profit", "Gross profit", "formula", builder=lambda i: diff(R("revenue", i), R("cogs", i)))
    row("opex", "Operating expenses (ex-D&A)", "input")
    row("ebitda", "EBITDA", "formula", builder=lambda i: diff(R("gross_profit", i), R("opex", i)), total=True)
    row("depreciation", "Depreciation & amortisation", "input")
    row("ebit", "EBIT (operating income)", "formula", builder=lambda i: diff(R("ebitda", i), R("depreciation", i)), total=True)
    row("interest_expense", "Interest expense", "input")
    row("other_income", "Other income / (expense)", "input")
    row("pretax", "Pre-tax income", "formula",
        builder=lambda i: f"={R('ebit', i)}-{R('interest_expense', i)}+{R('other_income', i)}")
    row("tax_expense", "Income tax expense", "input")
    row("net_income", "Net income", "formula", builder=lambda i: diff(R("pretax", i), R("tax_expense", i)), total=True)

    # ---- balance sheet ----
    sect("Balance Sheet — Assets")
    row("cash", "Cash & equivalents", "input")
    row("receivables", "Accounts receivable", "input")
    row("inventory", "Inventory", "input")
    row("other_current_assets", "Other current assets", "input")
    row("current_assets", "Total current assets", "formula", total=True,
        builder=lambda i: summ([R("cash", i), R("receivables", i), R("inventory", i), R("other_current_assets", i)]))
    row("ppe", "Property, plant & equipment (net)", "input")
    row("goodwill_intangibles", "Goodwill & intangibles", "input")
    row("other_noncurrent_assets", "Other non-current assets", "input")
    row("noncurrent_assets", "Total non-current assets", "formula", total=True,
        builder=lambda i: summ([R("ppe", i), R("goodwill_intangibles", i), R("other_noncurrent_assets", i)]))
    row("total_assets", "TOTAL ASSETS", "formula", total=True,
        builder=lambda i: add(R("current_assets", i), R("noncurrent_assets", i)))

    sect("Balance Sheet — Liabilities & Equity")
    row("accounts_payable", "Accounts payable", "input")
    row("short_term_debt", "Short-term debt", "input")
    row("other_current_liabilities", "Other current liabilities", "input")
    row("current_liabilities", "Total current liabilities", "formula", total=True,
        builder=lambda i: summ([R("accounts_payable", i), R("short_term_debt", i), R("other_current_liabilities", i)]))
    row("long_term_debt", "Long-term debt", "input")
    row("other_noncurrent_liabilities", "Other non-current liabilities", "input")
    row("noncurrent_liabilities", "Total non-current liabilities", "formula", total=True,
        builder=lambda i: add(R("long_term_debt", i), R("other_noncurrent_liabilities", i)))
    row("total_liabilities", "TOTAL LIABILITIES", "formula", total=True,
        builder=lambda i: add(R("current_liabilities", i), R("noncurrent_liabilities", i)))
    row("equity", "Shareholders' equity", "input", total=True)
    row("retained_earnings", "  of which: retained earnings", "input")
    row("total_liab_equity", "TOTAL LIABILITIES & EQUITY", "formula", total=True,
        builder=lambda i: add(R("total_liabilities", i), R("equity", i)))

    # ---- cash flow ----
    sect("Cash Flow Statement")
    row("operating_cash_flow", "Operating cash flow", "input", total=True)
    row("capex", "Capital expenditure", "input")
    row("fcf", "Free cash flow", "formula", builder=lambda i: diff(R("operating_cash_flow", i), R("capex", i)), total=True)
    row("dividends_paid", "Dividends paid", "input")
    row("buybacks", "Share buybacks (net)", "input")

    # ---- market & per share ----
    sect("Market Data & Per-Share")
    row("share_price", "Share price (period close)", "input", fmt=P)
    row("shares_outstanding", "Shares outstanding (m)", "input", fmt=Fmt.INT)
    row("market_cap", "Market capitalisation", "formula", total=True,
        builder=lambda i: product(R("share_price", i), R("shares_outstanding", i)))
    row("eps", "Earnings per share (EPS)", "formula", fmt=P, builder=lambda i: div(R("net_income", i), R("shares_outstanding", i)))
    row("dps", "Dividend per share (DPS)", "formula", fmt=P, builder=lambda i: div(R("dividends_paid", i), R("shares_outstanding", i)))

    # ---- cost-of-capital assumptions (registered before helpers use the tax rate) ----
    sect("Cost of Capital (for ROIC vs WACC)")
    sc = ctx.data.get("scalars", {})
    for key, label, fmt in (("rf", "Risk-free rate", X), ("erp", "Equity risk premium", X),
                            ("beta", "Beta", Fmt.FLOAT2), ("pretax_kd", "Pre-tax cost of debt", X),
                            ("tax_rate", "Tax rate", X)):
        sh.put(r, LBL, label, role="label")
        sh.put(r, FY0, sc.get(key), role="input", fmt=fmt, key=f"coc.{key}")
        sh.put(r, FY0 + 1, "← input", role="note_l")
        r += 1
    sh.put(r, LBL, "Cost of equity  Ke = Rf + β×ERP", role="label")
    sh.put(r, FY0, f"={refs.ref('coc.rf')}+{refs.ref('coc.beta')}*{refs.ref('coc.erp')}",
           role="formula", fmt=X, key="coc.ke")
    r += 1
    sh.put(r, LBL, "After-tax cost of debt", role="label")
    sh.put(r, FY0, f"={refs.ref('coc.pretax_kd')}*(1-{refs.ref('coc.tax_rate')})",
           role="formula", fmt=X, key="coc.kd_at")
    r += 1

    # ---- helper calculations (reused by every ratio sheet) ----
    sect("Helper Calculations  (intermediate steps reused across the workbook)")
    row("total_debt", "Total debt = ST + LT debt", "formula", builder=lambda i: add(R("short_term_debt", i), R("long_term_debt", i)))
    row("net_debt", "Net debt = total debt − cash", "formula", builder=lambda i: diff(R("total_debt", i), R("cash", i)))
    row("working_capital", "Working capital = CA − CL", "formula", builder=lambda i: diff(R("current_assets", i), R("current_liabilities", i)))
    row("capital_employed", "Capital employed = TA − CL", "formula", builder=lambda i: diff(R("total_assets", i), R("current_liabilities", i)))
    row("invested_capital", "Invested capital = equity + debt − cash", "formula",
        builder=lambda i: f"={R('equity', i)}+{R('total_debt', i)}-{R('cash', i)}")
    row("nopat", "NOPAT = EBIT × (1 − tax rate)", "formula",
        builder=lambda i: f"={R('ebit', i)}*(1-{refs.ref('coc.tax_rate')})")
    row("tangible_book", "Tangible book = equity − goodwill", "formula", builder=lambda i: diff(R("equity", i), R("goodwill_intangibles", i)))
    row("enterprise_value", "Enterprise value = mkt cap + debt − cash", "formula", total=True,
        builder=lambda i: f"={R('market_cap', i)}+{R('total_debt', i)}-{R('cash', i)}")
    # two-point averages (blank in the first column — no prior year)
    for key, label, src in (
        ("avg_equity", "Average equity", "equity"),
        ("avg_assets", "Average total assets", "total_assets"),
        ("avg_receivables", "Average receivables", "receivables"),
        ("avg_inventory", "Average inventory", "inventory"),
        ("avg_payables", "Average payables", "accounts_payable"),
        ("avg_fixed_assets", "Average net PP&E", "ppe"),
        ("avg_invested_capital", "Average invested capital", "invested_capital"),
    ):
        sh.put(r, LBL, label, role="label")
        for i in range(n):
            col = ctx.year_col(i)
            if i == 0:
                sh.put(r, col, None, role="formula", fmt=M, key=f"in.{key}@{i}")
            else:
                sh.put(r, col, avg2(R(src, i - 1), R(src, i)), role="formula", fmt=M, key=f"in.{key}@{i}")
        r += 1

    # ---- WACC (needs total_debt from the helper block above) ----
    r += 1
    le = ctx.last_hist_idx
    sh.put(r, LBL, "WACC (latest-year market-value weights)", role="label_b")
    e = R("market_cap", le)
    d = R("total_debt", le)
    sh.put(r, FY0, f"=IFERROR(({e}*{refs.ref('coc.ke')}+{d}*{refs.ref('coc.kd_at')})/({e}+{d}),{refs.ref('coc.ke')})",
           role="output", fmt=X, key="coc.wacc")
    sh.put(r, FY0 + 1, "WACC = We·Ke + Wd·Kd(1−t)", role="note_l")
    sh.merge(r, FY0 + 1, r, last)
    r += 1

    # widths
    sh.col_width(LBL, 38)
    for i in range(n):
        sh.col_width(ctx.year_col(i), 11)
    return sh
