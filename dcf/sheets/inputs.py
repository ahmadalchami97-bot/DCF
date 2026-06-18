"""
Inputs sheet -- the single, clean data-entry layer.

Holds every raw figure the analyst provides (income statement, balance sheet,
cash flow, shares, optional drivers, market/WACC references) plus the *subtotals*
the model derives from them. Inputs are yellow cells; subtotals are black/green
formulas computed here so the whole rest of the workbook can link to one
consistent set of figures.

Layout is computed in a first pass (a row is reserved for every line item and
section header) so that subtotal formulas -- some of which reference items in
later sections, e.g. EBITDA pulling D&A from the cash-flow block -- can be wired
with correct cell references in a second pass.
"""

from __future__ import annotations

from ..config import Fmt
from ..schema import MARKET_INPUTS, TIME_SERIES_SECTIONS
from ..utils import f, ratio, safe_sum
from . import common

LABEL_COL = 1
FIRST_DATA_COL = 2


def build(sh, ctx: common.Context):
    data = ctx.data
    n = ctx.n_hist
    note_col = FIRST_DATA_COL + n
    last_col = note_col

    common.setup_grid(sh, n_data_cols=n, note_col=note_col)
    r = common.title_block(sh, "INPUTS", "Standardised financial-statement input layer",
                           last_col=last_col)
    r += 1

    # --- company / meta block ---------------------------------------------
    r = _meta_block(sh, ctx, r, last_col)
    r += 1

    # --- legend & convention notes ----------------------------------------
    r = common.legend_block(sh, r)
    r += 1
    sh.put(r, 1, "Conventions", role="label_b")
    sh.merge(r, 1, r, last_col)
    r += 1
    for note in _CONVENTIONS:
        sh.put(r, 1, "•  " + note, role="note")
        sh.merge(r, 1, r, last_col)
        sh.row_height(r, 24)
        r += 1
    r += 1

    # --- pass 1: reserve rows ---------------------------------------------
    rowmap: dict[str, int] = {}
    header_rows: list[tuple[int, str]] = []
    cursor = r
    for sec in TIME_SERIES_SECTIONS:
        header_rows.append((cursor, sec.title))
        cursor += 1  # section band
        period_hdr_row = cursor
        cursor += 1  # period header
        rowmap[f"__hdr__{sec.title}"] = period_hdr_row
        for it in sec.items:
            rowmap[it.key] = cursor
            cursor += 1
        cursor += 1  # spacer between sections

    # --- pass 2: write everything -----------------------------------------
    for sec in TIME_SERIES_SECTIONS:
        hdr_row = rowmap[f"__hdr__{sec.title}"] - 1
        common.section(sh, hdr_row, sec.title, c1=1, c2=last_col)
        common.period_headers(
            sh, hdr_row + 1, label_col=LABEL_COL, first_data_col=FIRST_DATA_COL,
            labels=ctx.periods, note_text="Source / note",
            note_col=note_col,
        )
        for it in sec.items:
            row = rowmap[it.key]
            indent = "    " * it.indent
            role = "label_b" if it.key.startswith("total") or it.key in _BOLD_LABELS else "label"
            sh.put(row, LABEL_COL, indent + it.label, role=role)
            if it.note:
                sh.put(row, note_col, it.note, role="note")
            for p in range(n):
                col = FIRST_DATA_COL + p
                key = f"in.{it.key}@{p}"
                if it.kind == "input":
                    val = data["series"].get(it.key, [None] * n)[p]
                    sh.put(row, col, val, role="input", fmt=it.fmt, key=key)
                else:  # subtotal -> formula
                    formula = _subtotal_formula(it.key, sh, rowmap, col)
                    srole = "link" if it.key in _LINK_SUBTOTALS else "calc"
                    bold = it.key.startswith("total")
                    sh.put(row, col, formula, role=srole, fmt=it.fmt, key=key,
                           bold=bold or None)

    r = cursor + 1

    # --- market & valuation reference inputs ------------------------------
    r = _market_block(sh, ctx, r, last_col)

    sh.freeze("B" + str(rowmap[f"__hdr__{TIME_SERIES_SECTIONS[0].title}"] + 1))
    return sh


_BOLD_LABELS = {"revenue", "ebit", "ebitda", "net_income", "cfo", "cfi", "cff"}
_LINK_SUBTOTALS = {"da"}  # D&A is linked from the cash-flow block

_CONVENTIONS = [
    "COGS and SG&A are entered AS REPORTED (they already include their share of "
    "depreciation). Total D&A is entered ONCE in the Cash Flow block; EBITDA is "
    "built as EBIT + D&A so depreciation is never double-counted.",
    "Capex, acquisitions, dividends paid and buybacks are entered as POSITIVE "
    "amounts (cash spent); the model applies the sign automatically.",
    "Signed cash-flow lines (change in working capital, net debt issued/repaid, "
    "other lines) are entered as net cash impact: positive = inflow.",
    "Leave any cell blank if the figure is unavailable — the model marks it "
    "missing and continues with the best partial output (it will not invent data).",
]


def _meta_block(sh, ctx, r, last_col):
    m = ctx.data["meta"]
    common.section(sh, r, "Company & Reporting Profile", c1=1, c2=last_col)
    r += 1
    fields = [
        ("Company name", "name", m.get("name")),
        ("Ticker / identifier", "ticker", m.get("ticker")),
        ("Business type", "business_type", m.get("business_type")),
        ("Reporting currency", "currency", m.get("currency")),
        ("Units", "units", m.get("units")),
        ("Fiscal year end", "fye", m.get("fiscal_year_end")),
    ]
    for label, key, val in fields:
        sh.put(r, 1, label, role="label")
        sh.put(r, 2, val, role="input_l", key=f"in.{key}")
        sh.merge(r, 2, r, min(4, last_col))
        r += 1
    # description (wrapped)
    sh.put(r, 1, "Business description", role="label")
    sh.merge(r, 2, r + 2, last_col)
    sh.put(r, 2, m.get("description"), role="input_l", key="in.description", align="ltw")
    for rr in range(r, r + 3):
        sh.row_height(rr, 16)
    r += 3
    sh.put(r, 1, "Industry note", role="label")
    sh.merge(r, 2, r + 1, last_col)
    sh.put(r, 2, m.get("industry_note"), role="input_l", key="in.industry_note", align="ltw")
    r += 2
    return r


def _market_block(sh, ctx, r, last_col):
    common.section(sh, r, "Market & Valuation Reference Inputs", c1=1, c2=last_col)
    r += 1
    sh.put(r, 1, "Used by the WACC build-up and the equity-value bridge. "
                 "Fallback defaults are applied (and labelled) where left blank.",
           role="note")
    sh.merge(r, 1, r, last_col)
    sh.row_height(r, 16)
    r += 1
    sh.put(r, 1, "Reference", role="colhdr")
    sh.put(r, 2, "Value", role="colhdr_r")
    sh.put(r, 3, "Type", role="colhdr")
    sh.put(r, 4, "Note", role="colhdr")
    sh.merge(r, 4, r, last_col)
    r += 1
    market = ctx.data["market"]
    for it in MARKET_INPUTS:
        sh.put(r, 1, it.label, role="label")
        val = market.get(it.key)
        sh.put(r, 2, val, role="input", fmt=it.fmt, key=f"mkt.{it.key}")
        sh.put(r, 3, "input" if it.source == "input" else "input/fallback",
               role="neutral", align="c")
        sh.put(r, 4, it.note, role="note")
        sh.merge(r, 4, r, last_col)
        r += 1
    # derived market cap
    price = ctx.refs.ref("mkt.mkt_share_price")
    shares = ctx.refs.ref("mkt.mkt_shares_out")
    sh.put(r, 1, "Market capitalisation (derived)", role="label_b")
    sh.put(r, 2, f"=IF(AND(ISNUMBER({price}),ISNUMBER({shares})),{price}*{shares},\"n/a\")",
           role="calc", fmt=Fmt.MONEY, key="mkt.market_cap", bold=True)
    sh.put(r, 4, "Current price × shares outstanding.", role="note")
    sh.merge(r, 4, r, last_col)
    r += 1
    return r


# --- subtotal formula registry ---------------------------------------------
def _subtotal_formula(key: str, sh, rowmap: dict[str, int], col: int) -> str:
    """Build the formula for a subtotal cell at *col*, referencing same-sheet rows."""
    def ref(k):  # absolute same-sheet reference to item k at this column
        return sh.local(rowmap[k], col)

    summands = {
        "total_current_assets": ["cash", "st_investments", "accounts_receivable",
                                 "inventory", "other_current_assets"],
        "total_noncurrent_assets": ["ppe_net", "goodwill_intangibles",
                                    "other_noncurrent_assets"],
        "total_current_liabilities": ["accounts_payable", "short_term_debt",
                                      "other_current_liabilities"],
        "total_noncurrent_liabilities": ["long_term_debt", "other_noncurrent_liabilities"],
    }
    if key in summands:
        return safe_sum([ref(k) for k in summands[key]])
    if key == "gross_profit":
        return f(f"{ref('revenue')}-{ref('cogs')}")
    if key == "ebit":
        return f(f"{ref('gross_profit')}-{ref('sga')}-{ref('rd')}-{ref('other_operating')}")
    if key == "da":
        return f(ref("cf_da"))  # linked from cash-flow block
    if key == "ebitda":
        return f(f"{ref('ebit')}+{ref('da')}")
    if key == "pretax_income":
        return f(f"{ref('ebit')}-{ref('interest_expense')}+{ref('interest_income')}"
                 f"+{ref('other_nonoperating')}")
    if key == "net_income":
        return f(f"{ref('pretax_income')}-{ref('tax_expense')}-{ref('minority_interest')}")
    if key == "total_assets":
        return f(f"{ref('total_current_assets')}+{ref('total_noncurrent_assets')}")
    if key == "total_liabilities":
        return f(f"{ref('total_current_liabilities')}+{ref('total_noncurrent_liabilities')}")
    if key == "total_liab_equity":
        return f(f"{ref('total_liabilities')}+{ref('total_equity')}+{ref('minority_equity')}")
    if key == "cfo":
        return safe_sum([ref("cf_net_income"), ref("cf_da"), ref("cf_wc_change"),
                         ref("cf_other_operating")])
    if key == "cfi":
        return f(f"-{ref('capex')}-{ref('acquisitions')}+{ref('other_investing')}")
    if key == "cff":
        return f(f"{ref('debt_change')}-{ref('dividends_paid')}-{ref('buybacks')}"
                 f"+{ref('other_financing')}")
    if key == "net_change_cash":
        return f(f"{ref('cfo')}+{ref('cfi')}+{ref('cff')}")
    if key == "eps_basic":
        return ratio(ref("net_income"), ref("shares_basic"))
    if key == "eps_diluted":
        return ratio(ref("net_income"), ref("shares_diluted"))
    if key == "dps":
        return ratio(ref("dividends_paid"), ref("shares_basic"))
    if key == "payout_ratio":
        return ratio(ref("dividends_paid"), ref("net_income"))
    if key == "driver_implied_rev":
        return f(f"{ref('driver_volume')}*{ref('driver_price')}")
    return "=0"
