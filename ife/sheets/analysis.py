"""
Historical Analysis Engine (Sheet 3).

Computes growth, profitability, returns, efficiency, liquidity, leverage and the
per-year driver ratios (tax rate, capex %, D&A %, working-capital days, etc.)
from the Historical sheet. The Assumption Center averages these (3/5/10-year)
to anchor the forecast. Plus common-size and an indexed revenue trend.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..formulas import div, growth

PCT, MULT, DAYS = Fmt.PCT, Fmt.MULT2, Fmt.DAYS


def build(sh, ctx):
    refs = ctx.refs
    n = ctx.hist
    last = ctx.hcol(n - 1)
    H = lambda k, i: refs.ref(f"h.{k}@{i}")     # noqa: E731
    A = lambda k, i: refs.ref(f"ha.{k}@{i}")    # noqa: E731

    common.title_block(sh, "HISTORICAL ANALYSIS ENGINE",
                       "Ratios, margins, efficiency & the driver ratios the forecast is anchored on",
                       last_col=last)
    common.nav_bar(sh, 5)
    r = 7
    sh.put(r, 1, common.units_note(ctx), role="note")
    sh.merge(r, 1, r, last)
    r += 1
    r = common.hist_headers(sh, ctx, r, label="Metric", split=False)
    sh.freeze(f"B{r}")
    common.setup_cols(sh, ctx, split=False)

    def sect(t):
        nonlocal r
        r = common.section(sh, r, t, c1=1, c2=last)

    def row(key, label, fn, fmt=PCT, start=0):
        nonlocal r
        sh.put(r, 1, label, role="label")
        for i in range(n):
            sh.put(r, ctx.hcol(i), (None if i < start else fn(i)), role="formula", fmt=fmt,
                   key=f"ha.{key}@{i}")
        r += 1

    # driver ratios first (tax_rate needed by ROIC below)
    sect("Driver Ratios  (averaged on the Assumption Center)")
    row("tax_rate", "Effective tax rate", lambda i: div(H("tax_expense", i), H("pretax", i)))
    row("capex_pct", "Capex % of revenue", lambda i: div(H("capex", i), H("revenue", i)))
    row("da_pct", "D&A % of revenue", lambda i: div(H("depreciation", i), H("revenue", i)))
    row("cash_pct", "Cash % of revenue", lambda i: div(H("cash", i), H("revenue", i)))
    row("oa_pct", "Other assets % of revenue", lambda i: div(H("other_assets", i), H("revenue", i)))
    row("ol_pct", "Other liabilities % of revenue", lambda i: div(H("other_liabilities", i), H("revenue", i)))
    row("int_rate", "Interest rate (int exp / total debt)", lambda i: div(H("interest_expense", i), H("total_debt", i)))
    row("dso", "Receivable days (DSO)", lambda i: div(f"{H('avg_receivables', i)}*365", H("revenue", i)), DAYS, start=1)
    row("dio", "Inventory days (DIO)", lambda i: div(f"{H('avg_inventory', i)}*365", H("cogs", i)), DAYS, start=1)
    row("dpo", "Payable days (DPO)", lambda i: div(f"{H('avg_payables', i)}*365", H("cogs", i)), DAYS, start=1)
    r += 1

    sect("Growth")
    row("rev_growth", "Revenue growth", lambda i: growth(H("revenue", i), H("revenue", i - 1)), PCT, start=1)
    row("ebitda_growth", "EBITDA growth", lambda i: growth(H("ebitda", i), H("ebitda", i - 1)), PCT, start=1)
    row("ebit_growth", "EBIT growth", lambda i: growth(H("ebit", i), H("ebit", i - 1)), PCT, start=1)
    row("ni_growth", "Net income growth", lambda i: growth(H("net_income", i), H("net_income", i - 1)), PCT, start=1)
    row("fcf_growth", "Free cash flow growth", lambda i: growth(H("fcf", i), H("fcf", i - 1)), PCT, start=1)
    r += 1

    sect("Profitability")
    row("gross_margin", "Gross margin", lambda i: div(H("gross_profit", i), H("revenue", i)))
    row("ebitda_margin", "EBITDA margin", lambda i: div(H("ebitda", i), H("revenue", i)))
    row("ebit_margin", "EBIT margin", lambda i: div(H("ebit", i), H("revenue", i)))
    row("net_margin", "Net margin", lambda i: div(H("net_income", i), H("revenue", i)))
    row("fcf_margin", "FCF margin", lambda i: div(H("fcf", i), H("revenue", i)))
    r += 1

    sect("Returns")
    row("roe", "ROE", lambda i: div(H("net_income", i), H("avg_equity", i)), PCT, start=1)
    row("roa", "ROA", lambda i: div(H("net_income", i), H("avg_assets", i)), PCT, start=1)
    row("roic", "ROIC", lambda i: div(f"{H('ebit', i)}*(1-{A('tax_rate', i)})", H("avg_ic", i)), PCT, start=1)
    r += 1

    sect("Efficiency, Liquidity & Leverage")
    row("asset_turnover", "Asset turnover", lambda i: div(H("revenue", i), H("avg_assets", i)), MULT, start=1)
    row("current_ratio", "Current ratio",
        lambda i: div(f"({H('cash', i)}+{H('receivables', i)}+{H('inventory', i)}+{H('other_current_assets', i)})",
                      f"({H('payables', i)}+{H('short_term_debt', i)}+{H('other_liabilities', i)})"), MULT)
    row("quick_ratio", "Quick ratio",
        lambda i: div(f"({H('cash', i)}+{H('receivables', i)}+{H('other_current_assets', i)})",
                      f"({H('payables', i)}+{H('short_term_debt', i)}+{H('other_liabilities', i)})"), MULT)
    row("debt_equity", "Debt / equity", lambda i: div(H("total_debt", i), H("equity", i)), MULT)
    row("debt_ebitda", "Debt / EBITDA", lambda i: div(H("total_debt", i), H("ebitda", i)), MULT)
    row("net_debt_ebitda", "Net debt / EBITDA", lambda i: div(H("net_debt", i), H("ebitda", i)), MULT)
    row("interest_cover", "Interest coverage", lambda i: div(H("ebit", i), H("interest_expense", i)), MULT)
    r += 1

    sect("Common Size (% of revenue)")
    for key, num in (("cs_cogs", "cogs"), ("cs_gross", "gross_profit"), ("cs_opex", "opex"),
                     ("cs_ebitda", "ebitda"), ("cs_ebit", "ebit"), ("cs_net", "net_income")):
        row(key, num.replace("_", " ").title(), lambda i, nm=num: div(H(nm, i), H("revenue", i)))
    r += 1

    sect("Trend Index (first year = 100)")
    row("idx_revenue", "Revenue index", lambda i: f'=IFERROR({H("revenue", i)}/{H("revenue", 0)}*100,"")', Fmt.INT)
    row("idx_ebitda", "EBITDA index", lambda i: f'=IFERROR({H("ebitda", i)}/{H("ebitda", 0)}*100,"")', Fmt.INT)
    row("idx_ni", "Net income index", lambda i: f'=IFERROR({H("net_income", i)}/{H("net_income", 0)}*100,"")', Fmt.INT)
    return sh
