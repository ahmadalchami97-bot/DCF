"""
Scenario Analysis (Sheet 8).

Runs the full driver logic for Bear / Base / Bull simultaneously via a compact
per-scenario engine (P&L + cash + equity/debt roll, mirroring the Integrated
Forecast), then presents a professional comparison of the headline metrics. The
Base column reconciles with the main Forecast sheet.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..config import SCENARIOS

M, PCT, MULT = Fmt.MONEY, Fmt.PCT, Fmt.MULT2
G1 = {"rev_growth", "gross_margin", "ebitda_margin", "tax_rate", "dso", "dio", "dpo",
      "capex_pct", "da_pct", "oa_pct", "ol_pct", "int_rate"}
SCEN_KEYS = ["bear", "base", "bull"]


def _cagr(SC, s, key, N):
    return f'=IFERROR(({SC(s, key, N)}/{SC(s, key, 0)})^(1/{N})-1,"")'


def build(sh, ctx):
    refs = ctx.refs
    N = ctx.fcst
    li = ctx.last_hist
    H = lambda k: refs.ref(f"h.{k}@{li}")              # noqa: E731
    SC = lambda s, k, t: refs.ref(f"sc.{s}.{k}@{t}")   # noqa: E731

    def fc(t):
        return common.FIRST_COL + t

    last = fc(N)

    def drv(d, s, t):
        sel = refs.ref(f"a.{d}.{s}")
        if d in G1:
            avg5 = refs.ref(f"a.{d}.avg5")
            return f"IF(ISNUMBER({avg5}),CHOOSE(Method,{avg5},{sel},{avg5}+({sel}-{avg5})*{t/N:.4f}),{sel})"
        return sel

    L = [
        ("revenue", "revenue", lambda s, t: f"={SC(s,'revenue',t-1)}*(1+{drv('rev_growth',s,t)})"),
        ("cogs", "cogs", lambda s, t: f"={SC(s,'revenue',t)}*(1-{drv('gross_margin',s,t)})"),
        ("ebitda", "ebitda", lambda s, t: f"={SC(s,'revenue',t)}*{drv('ebitda_margin',s,t)}"),
        ("dep", "depreciation", lambda s, t: f"={SC(s,'revenue',t)}*{drv('da_pct',s,t)}"),
        ("ebit", "ebit", lambda s, t: f"={SC(s,'ebitda',t)}-{SC(s,'dep',t)}"),
        ("ltd", "long_term_debt", lambda s, t: f"={SC(s,'ltd',t-1)}+{drv('new_debt',s,t)}-{drv('debt_repay_pct',s,t)}*{SC(s,'ltd',t-1)}"),
        ("total_debt", "total_debt", lambda s, t: f"={H('short_term_debt')}+{SC(s,'ltd',t)}"),
        ("int_exp", "interest_expense", lambda s, t: f"={drv('int_rate',s,t)}*{SC(s,'total_debt',t-1)}"),
        ("int_inc", "zero", lambda s, t: f"={drv('cash_yield',s,t)}*{SC(s,'cash',t-1)}"),
        ("pretax", "pretax", lambda s, t: f"={SC(s,'ebit',t)}-{SC(s,'int_exp',t)}+{SC(s,'int_inc',t)}"),
        ("tax", "tax_expense", lambda s, t: f"={drv('tax_rate',s,t)}*{SC(s,'pretax',t)}"),
        ("ni", "net_income", lambda s, t: f"={SC(s,'pretax',t)}-{SC(s,'tax',t)}"),
        ("recv", "receivables", lambda s, t: f"={drv('dso',s,t)}/365*{SC(s,'revenue',t)}"),
        ("inv", "inventory", lambda s, t: f"={drv('dio',s,t)}/365*{SC(s,'cogs',t)}"),
        ("oca", "other_current_assets", lambda s, t: f"=IFERROR({SC(s,'revenue',t)}*{H('other_current_assets')}/{H('revenue')},0)"),
        ("pay", "payables", lambda s, t: f"={drv('dpo',s,t)}/365*{SC(s,'cogs',t)}"),
        ("otherL", "other_liabilities", lambda s, t: f"={drv('ol_pct',s,t)}*{SC(s,'revenue',t)}"),
        ("oa", "other_assets", lambda s, t: f"={drv('oa_pct',s,t)}*{SC(s,'revenue',t)}"),
        ("dwc", "zero", lambda s, t: (f"=({SC(s,'recv',t)}-{SC(s,'recv',t-1)})+({SC(s,'inv',t)}-{SC(s,'inv',t-1)})"
                                      f"+({SC(s,'oca',t)}-{SC(s,'oca',t-1)})-({SC(s,'pay',t)}-{SC(s,'pay',t-1)})"
                                      f"-({SC(s,'otherL',t)}-{SC(s,'otherL',t-1)})")),
        ("capex", "capex", lambda s, t: f"={drv('capex_pct',s,t)}*{SC(s,'revenue',t)}"),
        ("cfo", "operating_cash_flow", lambda s, t: f"={SC(s,'ni',t)}+{SC(s,'dep',t)}-{SC(s,'dwc',t)}"),
        ("fcf", "fcf", lambda s, t: f"={SC(s,'cfo',t)}-{SC(s,'capex',t)}"),
        ("dividends", "zero", lambda s, t: f"={drv('dividend_payout',s,t)}*MAX(0,{SC(s,'ni',t)})"),
        ("cash", "cash", lambda s, t: (f"={SC(s,'cash',t-1)}+{SC(s,'cfo',t)}-{SC(s,'capex',t)}"
                                       f"-({SC(s,'oa',t)}-{SC(s,'oa',t-1)})+{drv('new_debt',s,t)}"
                                       f"-{drv('debt_repay_pct',s,t)}*{SC(s,'ltd',t-1)}-{SC(s,'dividends',t)}")),
        ("equity", "equity", lambda s, t: f"={SC(s,'equity',t-1)}+{SC(s,'ni',t)}-{SC(s,'dividends',t)}"),
        ("nopat", "zero", lambda s, t: f"={SC(s,'ebit',t)}*(1-{drv('tax_rate',s,t)})"),
        ("ic", "invested_capital", lambda s, t: f"={SC(s,'equity',t)}+{SC(s,'total_debt',t)}-{SC(s,'cash',t)}"),
    ]

    common.title_block(sh, "SCENARIO ANALYSIS",
                       "Bear / Base / Bull run through the full driver logic and compared",
                       last_col=last)
    common.nav_bar(sh, 5)
    r = 7

    metrics = [
        ("Revenue CAGR", lambda s: _cagr(SC, s, "revenue", N), PCT),
        ("EBITDA CAGR", lambda s: _cagr(SC, s, "ebitda", N), PCT),
        ("EBIT CAGR", lambda s: _cagr(SC, s, "ebit", N), PCT),
        ("Net income CAGR", lambda s: _cagr(SC, s, "ni", N), PCT),
        ("FCF CAGR", lambda s: _cagr(SC, s, "fcf", N), PCT),
        ("EBITDA margin (terminal)", lambda s: f'=IFERROR({SC(s,"ebitda",N)}/{SC(s,"revenue",N)},"")', PCT),
        ("Net margin (terminal)", lambda s: f'=IFERROR({SC(s,"ni",N)}/{SC(s,"revenue",N)},"")', PCT),
        ("ROE (terminal)", lambda s: f'=IFERROR({SC(s,"ni",N)}/(({SC(s,"equity",N)}+{SC(s,"equity",N-1)})/2),"")', PCT),
        ("ROIC (terminal)", lambda s: f'=IFERROR({SC(s,"nopat",N)}/(({SC(s,"ic",N)}+{SC(s,"ic",N-1)})/2),"")', PCT),
        ("Debt / EBITDA (terminal)", lambda s: f'=IFERROR({SC(s,"total_debt",N)}/{SC(s,"ebitda",N)},"")', MULT),
    ]
    summary_start = r
    blocks_start = summary_start + len(metrics) + 4

    # pass 1: lay out & register engine-block cells (enables forward refs)
    rr = blocks_start
    block_hdr = {}
    for s in SCEN_KEYS:
        block_hdr[s] = rr
        rr += 2  # title row + period-label row
        for key, _, _ in L:
            for t in range(N + 1):
                refs.put(f"sc.{s}.{key}@{t}", sh.name, sh.coord(rr, fc(t)))
            rr += 1
        rr += 1

    # pass 2a: summary comparison table
    common.section(sh, summary_start, "Scenario Comparison (10-year)", c1=1, c2=4)
    sh.put(summary_start + 1, 1, "Metric", role="colhdr")
    for j, s in enumerate(SCENARIOS):
        sh.put(summary_start + 1, 2 + j, s, role="colhdr_r")
    for i, (label, fn, fmt) in enumerate(metrics):
        row = summary_start + 2 + i
        sh.put(row, 1, label, role="label")
        for j, sk in enumerate(SCEN_KEYS):
            sh.put(row, 2 + j, fn(sk), role="output", fmt=fmt)
    sh.put(summary_start + 2 + len(metrics), 1,
           "Base reconciles with the Forecast sheet; Bear/Bull apply that scenario's drivers.", role="note")
    sh.merge(summary_start + 2 + len(metrics), 1, summary_start + 2 + len(metrics), 4)

    # pass 2b: engine blocks
    names = dict(zip(SCEN_KEYS, SCENARIOS))
    for s in SCEN_KEYS:
        hr = block_hdr[s]
        common.section(sh, hr, f"Scenario Engine — {names[s]}", c1=1, c2=last)
        sh.put(hr + 1, 1, "Line item", role="colhdr")
        sh.put(hr + 1, common.FIRST_COL, f"{ctx.hist_periods[li]} (base)", role="colhdr_r")
        for t in range(1, N + 1):
            sh.put(hr + 1, fc(t), ctx.fcst_periods[t - 1], role="colhdr_r")
        row = hr + 2
        for key, anchor, builder in L:
            sh.put(row, 1, key, role="sublabel")
            sh.put(row, fc(0), (0 if anchor == "zero" else f"={H(anchor)}"), role="formula", fmt=M)
            for t in range(1, N + 1):
                sh.put(row, fc(t), builder(s, t), role="formula", fmt=M)
            row += 1

    sh.col_width(1, 28)
    for c in range(2, last + 1):
        sh.col_width(c, 11)
    sh.freeze("B8")
    return sh
