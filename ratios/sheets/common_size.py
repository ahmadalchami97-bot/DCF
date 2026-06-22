"""Common Size & Trend Analysis (Sheet 4)."""

from __future__ import annotations

from dcf.config import Fmt
from ..formulas import div
from ..render import Grid

PCT = Fmt.PCT


def build(sh, ctx):
    g = Grid(sh, ctx, "cs")
    R = g.R
    g.title("COMMON SIZE & TREND ANALYSIS",
            "Income statement vs revenue, balance sheet vs assets, indexed trend")
    g.yearhead("Line item")

    g.section("Income Statement — Common Size (% of revenue)")
    is_rows = [
        ("revenue", "Revenue"), ("cogs", "Cost of goods sold"), ("gross_profit", "Gross profit"),
        ("opex", "Operating expenses"), ("ebitda", "EBITDA"), ("depreciation", "Depreciation"),
        ("ebit", "EBIT"), ("interest_expense", "Interest expense"), ("pretax", "Pre-tax income"),
        ("tax_expense", "Income tax"), ("net_income", "Net income"),
    ]
    for key, label in is_rows:
        g.ratio(key, label, lambda i, k=key: div(R(k, i), R("revenue", i)), PCT, None,
                arrow=False, total=(key in ("gross_profit", "ebitda", "ebit", "net_income")))
    g.blank()

    g.section("Balance Sheet — Common Size (% of total assets)")
    bs_rows = [
        ("cash", "Cash & equivalents"), ("receivables", "Receivables"), ("inventory", "Inventory"),
        ("other_current_assets", "Other current assets"), ("current_assets", "Total current assets"),
        ("ppe", "PP&E (net)"), ("goodwill_intangibles", "Goodwill & intangibles"),
        ("other_noncurrent_assets", "Other non-current assets"),
        ("current_liabilities", "Total current liabilities"), ("long_term_debt", "Long-term debt"),
        ("total_liabilities", "Total liabilities"), ("equity", "Shareholders' equity"),
    ]
    for key, label in bs_rows:
        g.ratio("bs_" + key, label, lambda i, k=key: div(R(k, i), R("total_assets", i)), PCT, None,
                arrow=False, total=(key in ("current_assets", "total_liabilities", "equity")))
    g.blank()

    g.section("Horizontal / Trend Analysis (indexed to first year = 100)")
    base = ctx.periods[0]
    g.ratio("idx_revenue", f"Revenue index ({base}=100)", lambda i: f'=IFERROR({R("revenue", i)}/{R("revenue", 0)}*100,"")',
            Fmt.INT, None, arrow=False, total=True)
    g.ratio("idx_ni", f"Net income index ({base}=100)", lambda i: f'=IFERROR({R("net_income", i)}/{R("net_income", 0)}*100,"")',
            Fmt.INT, None, arrow=False)
    g.ratio("idx_equity", f"Equity index ({base}=100)", lambda i: f'=IFERROR({R("equity", i)}/{R("equity", 0)}*100,"")',
            Fmt.INT, None, arrow=False)
    g.blank()
    g.note("Common-size analysis normalises the statements so structural shifts and "
           "trends are visible regardless of absolute size. Heat-maps highlight the gradient.")
    g.finalize()
    return sh
