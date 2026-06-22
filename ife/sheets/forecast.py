"""
Integrated Forecast Model (the FORECAST layer -- the core).

A compact, fully-reconciled three-statement forecast. It begins the year AFTER
the last actual (the base column is pulled from the last reported year with
INDEX, so it shifts automatically when you add actuals) and runs for the horizon.

Two principles keep it auditable:
  1. ONE driver per line. Every forecast cell is a single short formula -- prior
     value x (1 + growth), revenue x margin, a roll-forward, etc. You never trace
     a number through layers; the driver it uses is named right in the formula.
  2. It reconciles WITHOUT a plug and WITHOUT circularity. Cash is the residual
     of a complete cash-flow statement; equity and debt roll forward; net interest
     is charged on the OPENING net-debt balance. Because every balance-sheet move
     flows through the cash flow, Assets = Liabilities + Equity to the cent every
     year (the balance check is exactly 0).
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..common import FIRST_COL, FY_FMT

M = Fmt.MONEY


def build(sh, ctx):
    refs = ctx.refs
    N = ctx.horizon
    slots = ctx.hist_slots
    F = lambda k, t: refs.ref(f"f.{k}@{t}")                       # noqa: E731
    A = lambda k, t: refs.ref(f"a.{k}@{t}")                       # noqa: E731
    HR = lambda k: refs.range(f"h.{k}@0", f"h.{k}@{slots - 1}")   # noqa: E731
    CNT = refs.ref("t.count")

    def fc(t):
        return FIRST_COL + t  # t=0 = base (last actual), t=1..N = forecast

    last = fc(N)

    # (kind, key, label, role, anchor, builder)
    # anchor: ("hist", histkey) | ("zero",) | ("calc", lambda: formula)
    entries = [
        ("sec", "Income Statement"),
        ("line", "revenue", "Revenue", "output", ("hist", "revenue"),
         lambda t: f"={F('revenue', t-1)}*(1+{A('rev_growth', t)})"),
        ("line", "ebitda", "EBITDA", "output", ("hist", "ebitda"),
         lambda t: f"={F('revenue', t)}*{A('ebitda_margin', t)}"),
        ("line", "depreciation", "Depreciation & amortisation", "formula", ("hist", "depreciation"),
         lambda t: f"={F('revenue', t)}*{A('da_pct', t)}"),
        ("line", "ebit", "EBIT", "output", ("hist", "ebit"),
         lambda t: f"={F('ebitda', t)}-{F('depreciation', t)}"),
        ("line", "net_interest", "Net interest expense", "formula", ("hist", "net_interest"),
         lambda t: f"={A('net_int_rate', t)}*{F('net_debt', t-1)}"),
        ("line", "pretax", "Pre-tax income", "formula", ("hist", "pretax"),
         lambda t: f"={F('ebit', t)}-{F('net_interest', t)}"),
        ("line", "tax", "Tax expense", "formula", ("hist", "tax"),
         lambda t: f"={A('tax_rate', t)}*{F('pretax', t)}"),
        ("line", "net_income", "Net income", "output", ("hist", "net_income"),
         lambda t: f"={F('pretax', t)}-{F('tax', t)}"),

        ("sec", "Balance Sheet  -  Assets"),
        ("line", "cash", "Cash & equivalents", "formula", ("hist", "cash"),
         lambda t: f"={F('cash', t-1)}+{F('cfo', t)}+{F('cfi', t)}+{F('cff', t)}"),
        ("line", "nwc", "Net working capital", "formula", ("hist", "nwc"),
         lambda t: f"={A('nwc_pct', t)}*{F('revenue', t)}"),
        ("line", "net_ppe", "Net PP&E", "formula", ("hist", "net_ppe"),
         lambda t: f"={F('net_ppe', t-1)}+{F('capex', t)}-{F('depreciation', t)}"),
        ("line", "other_assets", "Other assets (held flat)", "formula", ("hist", "other_assets"),
         lambda t: f"={F('other_assets', t-1)}"),
        ("line", "total_assets", "Total assets", "output", ("hist", "total_assets"),
         lambda t: "=" + "+".join(F(k, t) for k in ("cash", "nwc", "net_ppe", "other_assets"))),

        ("sec", "Balance Sheet  -  Liabilities & Equity"),
        ("line", "total_debt", "Total debt", "formula", ("hist", "total_debt"),
         lambda t: f"={F('total_debt', t-1)}+{A('net_new_debt', t)}"),
        ("line", "other_liabilities", "Other liabilities (held flat)", "formula", ("hist", "other_liabilities"),
         lambda t: f"={F('other_liabilities', t-1)}"),
        ("line", "total_liabilities", "Total liabilities", "total", ("hist", "total_liabilities"),
         lambda t: f"={F('total_debt', t)}+{F('other_liabilities', t)}"),
        ("line", "equity", "Shareholders' equity", "output", ("hist", "equity"),
         lambda t: f"={F('equity', t-1)}+{F('net_income', t)}-{F('dividends', t)}"),
        ("line", "total_liab_equity", "Total liabilities & equity", "total", ("hist", "total_liab_equity"),
         lambda t: f"={F('total_liabilities', t)}+{F('equity', t)}"),
        ("line", "balance_check", "Balance check  (must be 0)", "formula", ("zero",),
         lambda t: f"={F('total_assets', t)}-{F('total_liab_equity', t)}"),

        ("sec", "Cash Flow"),
        ("line", "d_nwc", "(-) Increase in net working capital", "formula", ("zero",),
         lambda t: f"={F('nwc', t)}-{F('nwc', t-1)}"),
        ("line", "cfo", "Operating cash flow", "output", ("hist", "operating_cash_flow"),
         lambda t: f"={F('net_income', t)}+{F('depreciation', t)}-{F('d_nwc', t)}"),
        ("line", "capex", "Capital expenditure", "formula", ("hist", "capex"),
         lambda t: f"={A('capex_pct', t)}*{F('revenue', t)}"),
        ("line", "cfi", "Investing cash flow", "formula", ("zero",),
         lambda t: f"=-{F('capex', t)}-({F('other_assets', t)}-{F('other_assets', t-1)})"),
        ("line", "dividends", "Dividends paid", "formula", ("zero",),
         lambda t: f"={A('payout', t)}*MAX(0,{F('net_income', t)})"),
        ("line", "cff", "Financing cash flow", "formula", ("zero",),
         lambda t: f"={A('net_new_debt', t)}-{F('dividends', t)}"),
        ("line", "fcf", "Free cash flow", "output", ("hist", "fcf"),
         lambda t: f"={F('cfo', t)}-{F('capex', t)}"),

        ("sec", "Memo"),
        ("line", "net_debt", "Net debt  (debt - cash)", "formula",
         ("calc", lambda: f"={F('total_debt', 0)}-{F('cash', 0)}"),
         lambda t: f"={F('total_debt', t)}-{F('cash', t)}"),
    ]

    common.title_block(sh, "INTEGRATED FORECAST MODEL  (FORECAST)",
                       "One driver per line; reconciles to the cent with no plug and no circularity",
                       last_col=last)
    common.nav_bar(sh, 5)
    sh.put(7, 1, f'="Forecast window:  FY"&(LastActual+1)&"  through  FY"&(LastActual+{N})',
           role="output_l")
    sh.merge(7, 1, 7, 6)
    sh.put(7, 7, common.units_note(ctx), role="note")
    sh.merge(7, 7, 7, last)

    hdr = 9
    sh.put(hdr, 1, "Line item", role="colhdr")
    sh.put(hdr, fc(0), "=LastActual", role="actual_hdr", fmt=FY_FMT)
    for t in range(1, N + 1):
        sh.put(hdr, fc(t), f"={sh.local(hdr, fc(t) - 1)}+1", role="fcst_hdr", fmt=FY_FMT)
    tag = hdr + 1
    sh.put(tag, 1, "", role="sublabel")
    sh.put(tag, fc(0), "Actual", role="actual_tag")
    for t in range(1, N + 1):
        sh.put(tag, fc(t), "Forecast", role="fcst_tag")
    r0 = tag + 1

    # pass 1: assign rows & register cells (enables legitimate forward refs)
    rows, rr = [], r0
    for e in entries:
        rows.append(rr)
        if e[0] == "line":
            for t in range(N + 1):
                refs.put(f"f.{e[1]}@{t}", sh.name, sh.coord(rr, fc(t)))
        rr += 1

    # pass 2: write labels, base anchors, forecast formulas
    for e, row in zip(entries, rows):
        if e[0] == "sec":
            common.section(sh, row, e[1], c1=1, c2=last)
            continue
        _, key, label, role, anchor, builder = e
        sh.put(row, 1, label, role=("label_b" if role in ("output", "total") else "label"))
        if anchor[0] == "hist":
            sh.put(row, fc(0), f"=IFERROR(INDEX({HR(anchor[1])},{CNT}),0)", role="formula", fmt=M)
        elif anchor[0] == "zero":
            sh.put(row, fc(0), 0, role="formula", fmt=M)
        else:  # calc
            sh.put(row, fc(0), anchor[1](), role="formula", fmt=M)
        for t in range(1, N + 1):
            sh.put(row, fc(t), builder(t), role=role, fmt=M)

    sh.freeze(f"C{r0}")
    sh.col_width(1, 34)
    sh.col_width(fc(0), 12)
    for t in range(1, N + 1):
        sh.col_width(fc(t), 11)
    return sh
