"""
Dashboard.

The one-page visual summary: current vs recommended allocation (pies + bar),
scenario return and contribution by asset (bars), a risk/return map (scatter),
and a plain-English summary box of what happened in the scenario.

Small data tables (linked to the other sheets) feed the charts, so every chart
updates automatically when the inputs change.
"""

from __future__ import annotations

from openpyxl.chart import Reference

from .. import common
from ..config import ALLOCATIONS, ASSETS, Fmts

SHORT = {"smi": "SMI", "sp500": "S&P 500", "sxi_re": "SXI RE", "gold": "Gold", "ust": "US Bonds"}
LAST = 12


def build(sh, ctx):
    refs = ctx.refs
    ws = sh.ws

    common.title_block(sh, "DASHBOARD", "Scenario impact, allocation and risk/return at a glance", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "WHAT THIS SHEET SHOWS:  your current vs recommended allocation, how each asset performed in the scenario, "
        "how much each contributed to the portfolio return, and where each portfolio sits on the risk/return map.",
        "It is a summary -- all the detail (and every formula) lives on the Scenario Output, Risk & Return and "
        "Allocation sheets. Charts update automatically when you change the inputs.",
    ], last_col=LAST)
    r += 1

    # ---- scenario summary box ----
    r = common.section(sh, r, "Scenario summary", c1=1, c2=LAST)
    sh.put(r, 1, "Scenario", role="label_b")
    sh.put(r, 3, f"={refs.ref('in.scen_name')}", role="formula_l")
    sh.merge(r, 3, r, 6)
    sh.put(r, 7, "Portfolio scenario return", role="label_b")
    sh.put(r, 9, f"={refs.ref('out.port_return')}", role="kpi", fmt=Fmts.PCT)
    sh.merge(r, 9, r, 10)
    r += 1
    sh.put(r, 1, "Period", role="label")
    sh.put(r, 3, f"={refs.ref('in.start_date')}&\"  to  \"&{refs.ref('in.end_date')}", role="formula_l")
    sh.merge(r, 3, r, 6)
    summary_anchor = r
    r += 2

    # ---- data tables that feed the charts ----
    tbl = r
    # block 1: allocation (current vs recommended)
    sh.put(tbl, 1, "Asset", role="colhdr_l")
    sh.put(tbl, 2, "Current", role="colhdr")
    sh.put(tbl, 3, "Recommended", role="colhdr")
    # block 2: scenario by asset
    sh.put(tbl, 5, "Asset", role="colhdr_l")
    sh.put(tbl, 6, "Scenario return", role="colhdr")
    sh.put(tbl, 7, "Contribution", role="colhdr")
    # block 3: risk/return points
    sh.put(tbl, 9, "Point", role="colhdr_l")
    sh.put(tbl, 10, "Risk", role="colhdr")
    sh.put(tbl, 11, "Return", role="colhdr")
    d_first = tbl + 1
    for i, (key, name, _) in enumerate(ASSETS):
        rr = d_first + i
        sh.put(rr, 1, SHORT[key], role="label")
        sh.put(rr, 2, f"={refs.ref(f'al.w@current_{key}')}", role="formula", fmt=Fmts.PCT)
        sh.put(rr, 3, f"={refs.ref(f'al.rec_w@{key}')}", role="formula", fmt=Fmts.PCT)
        sh.put(rr, 5, SHORT[key], role="label")
        sh.put(rr, 6, f"={refs.ref(f'out.curradj@{key}')}", role="formula", fmt=Fmts.PCT)
        sh.put(rr, 7, f"={refs.ref(f'out.contrib@{key}')}", role="formula", fmt=Fmts.PCT)
    d_last = d_first + len(ASSETS) - 1
    names_rng = f"{common.col_letter(5)}{d_first}:{common.col_letter(5)}{d_last}"
    contrib_rng = f"{common.col_letter(7)}{d_first}:{common.col_letter(7)}{d_last}"

    # risk/return points: 6 portfolios then 5 assets
    rr = d_first
    for akey, alabel, _ in ALLOCATIONS:
        sh.put(rr, 9, alabel, role="label")
        sh.put(rr, 10, f"={refs.ref(f'al.vol@{akey}')}", role="formula", fmt=Fmts.PCT)
        sh.put(rr, 11, f"={refs.ref(f'al.ret@{akey}')}", role="formula", fmt=Fmts.PCT)
        rr += 1
    for key, name, _ in ASSETS:
        sh.put(rr, 9, SHORT[key], role="sublabel")
        sh.put(rr, 10, f"={refs.ref(f'rr.vol@{key}')}", role="formula", fmt=Fmts.PCT)
        sh.put(rr, 11, f"={refs.ref(f'rr.exp@{key}')}", role="formula", fmt=Fmts.PCT)
        rr += 1
    rr_last = rr - 1

    # best / worst contributor + summary sentence (now that ranges exist)
    best = f"INDEX({names_rng},MATCH(MAX({contrib_rng}),{contrib_rng},0))"
    worst = f"INDEX({names_rng},MATCH(MIN({contrib_rng}),{contrib_rng},0))"
    sh.put(summary_anchor, 7, "What happened", role="label_b")
    sentence = (f'="In the "&{refs.ref("in.scen_name")}&" scenario, the portfolio returned "'
                f'&TEXT({refs.ref("out.port_return")},"0.0%")&".  "&{best}&" helped most; "&{worst}&" detracted most."')
    sh.put(summary_anchor, 9, sentence, role="formula_l")
    sh.merge(summary_anchor, 9, summary_anchor, LAST)

    # ---- charts ----
    cr = rr_last + 2
    names_ref = Reference(ws, min_col=1, min_row=d_first, max_row=d_last)
    cur_ref = Reference(ws, min_col=2, min_row=d_first, max_row=d_last)
    rec_ref = Reference(ws, min_col=3, min_row=d_first, max_row=d_last)
    common.pie_chart(sh, f"A{cr}", "Current allocation", labels_ref=names_ref, data_ref=cur_ref)
    common.pie_chart(sh, f"E{cr}", "Recommended allocation", labels_ref=names_ref, data_ref=rec_ref)

    cr2 = cr + 15
    cvr_ref = Reference(ws, min_col=2, max_col=3, min_row=tbl, max_row=d_last)
    common.bar_chart(sh, f"A{cr2}", "Current vs recommended weight",
                     cats_ref=names_ref, data_refs=[cvr_ref])
    scen_ref = Reference(ws, min_col=6, max_col=6, min_row=tbl, max_row=d_last)
    common.bar_chart(sh, f"E{cr2}", "Scenario return by asset",
                     cats_ref=Reference(ws, min_col=5, min_row=d_first, max_row=d_last), data_refs=[scen_ref])

    cr3 = cr2 + 15
    contrib_ref = Reference(ws, min_col=7, max_col=7, min_row=tbl, max_row=d_last)
    common.bar_chart(sh, f"A{cr3}", "Contribution to portfolio return",
                     cats_ref=Reference(ws, min_col=5, min_row=d_first, max_row=d_last), data_refs=[contrib_ref])
    x_ref = Reference(ws, min_col=10, min_row=d_first, max_row=rr_last)
    y_ref = Reference(ws, min_col=11, min_row=d_first, max_row=rr_last)
    common.scatter_chart(sh, f"E{cr3}", "Risk / return map (portfolios and assets)", x_ref=x_ref, y_ref=y_ref)

    sh.freeze("A6")
    sh.col_width(1, 12)
    for c in range(2, LAST + 1):
        sh.col_width(c, 12)
    return sh
