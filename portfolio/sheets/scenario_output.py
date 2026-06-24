"""
Scenario Output.

Turns the inputs into the scenario result for each asset: local return, FX effect,
currency-adjusted return, market values, weight, and contribution to the total
portfolio return. Every cell is a short, visible formula.
"""

from __future__ import annotations

from .. import common
from ..config import ASSETS, Fmts

LAST = 11


def build(sh, ctx):
    refs = ctx.refs
    I = lambda k, key: refs.ref(f"in.{k}@{key}")   # noqa: E731
    O = lambda k, key: refs.ref(f"out.{k}@{key}")  # noqa: E731

    common.title_block(sh, "SCENARIO OUTPUT", "What the scenario did to each asset and to the whole portfolio",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "WHAT THIS SHEET TELLS YOU:  how each asset performed in the scenario, in your base currency, and how much "
        "each one added to (or subtracted from) the total portfolio return.",
        "COLUMNS:  Local return = price move in the asset's own currency.  FX effect = currency move vs your base "
        "currency.  Currency-adjusted return = the two combined (what you actually earned).  "
        "Contribution = Current weight x Currency-adjusted return.  Portfolio return = sum of all contributions.",
        "FORMULAS:   Local = End / Start - 1   |   FX = End FX / Start FX - 1   |   "
        "Adjusted = (1 + Local) x (1 + FX) - 1   |   Contribution = Weight x Adjusted.",
        "Note: 'US Government Bonds' local return comes from the Bond Calculator (price move + coupon), not price alone.",
    ], last_col=LAST)
    r += 1

    hdr = r
    cols = ["Asset", "Start\nprice", "End\nprice", "Local\nreturn", "FX\neffect",
            "Currency-adj.\nreturn", "Current\nweight", "Contribution\nto return",
            f"Start value\n({ctx.base_ccy})", f"End value\n({ctx.base_ccy})", "Performance attribution"]
    for c, t in enumerate(cols, start=1):
        sh.put(hdr, c, t, role="colhdr" if c > 1 else "colhdr_l")
    common.cell_comment(sh, hdr, 6, "Currency-adjusted return = (1 + Local return) x (1 + FX effect) - 1.\n"
                                    "This is what you actually earned in your base currency.")
    common.cell_comment(sh, hdr, 8, "Contribution = Current weight x Currency-adjusted return.\n"
                                    "Add up every asset's contribution to get the portfolio return.")
    sh.row_height(hdr, 26)
    r += 1
    for key, name, _ccy in ASSETS:
        sh.put(r, 1, name, role="label")
        sh.put(r, 2, f"={I('start_price', key)}", role="link", fmt=Fmts.PRICE)
        sh.put(r, 3, f"={I('end_price', key)}", role="link", fmt=Fmts.PRICE)
        if key == "ust":
            local = f"={refs.ref('bond.total_return')}"
        else:
            local = f"=IFERROR({I('end_price', key)}/{I('start_price', key)}-1,0)"
        sh.put(r, 4, local, role="formula", fmt=Fmts.PCT, key=f"out.local@{key}")
        sh.put(r, 5, f"=IFERROR({I('end_fx', key)}/{I('start_fx', key)}-1,0)",
               role="formula", fmt=Fmts.PCT, key=f"out.fx@{key}")
        sh.put(r, 6, f"=(1+{O('local', key)})*(1+{O('fx', key)})-1",
               role="output", fmt=Fmts.PCT, key=f"out.curradj@{key}")
        sh.put(r, 7, f"={I('cur_w', key)}", role="link", fmt=Fmts.PCT, key=f"out.weight@{key}")
        sh.put(r, 8, f"={O('weight', key)}*{O('curradj', key)}",
               role="output", fmt=Fmts.PCT, key=f"out.contrib@{key}")
        sh.put(r, 9, f"={I('invested', key)}", role="link", fmt=Fmts.MONEY, key=f"out.start_val@{key}")
        sh.put(r, 10, f"={O('start_val', key)}*(1+{O('curradj', key)})",
               role="formula", fmt=Fmts.MONEY, key=f"out.end_val@{key}")
        sh.put(r, 11, f'=IF({O("curradj", key)}>=0,"Helped: +","Hurt: ")&TEXT({O("contrib", key)},"0.0%")&" of portfolio return"',
               role="formula_l")
        r += 1

    # totals + portfolio return
    contrib_rng = refs.range(f"out.contrib@{ctx.keys[0]}", f"out.contrib@{ctx.keys[-1]}")
    sv_rng = refs.range(f"out.start_val@{ctx.keys[0]}", f"out.start_val@{ctx.keys[-1]}")
    ev_rng = refs.range(f"out.end_val@{ctx.keys[0]}", f"out.end_val@{ctx.keys[-1]}")
    sh.put(r, 1, "Portfolio total", role="total_l")
    sh.put(r, 7, f"=SUM({refs.range('out.weight@'+ctx.keys[0], 'out.weight@'+ctx.keys[-1])})", role="total", fmt=Fmts.PCT)
    sh.put(r, 8, f"=SUM({contrib_rng})", role="total", fmt=Fmts.PCT, key="out.port_return")
    sh.put(r, 9, f"=SUM({sv_rng})", role="total", fmt=Fmts.MONEY, key="out.start_total")
    sh.put(r, 10, f"=SUM({ev_rng})", role="total", fmt=Fmts.MONEY, key="out.end_total")
    r += 2

    # headline boxes
    sh.put(r, 1, "Scenario portfolio return", role="label_b")
    sh.put(r, 3, f"={refs.ref('out.port_return')}", role="kpi", fmt=Fmts.PCT)
    sh.merge(r, 3, r, 4)
    sh.put(r, 6, "Cross-check (End value / Start value - 1)", role="label")
    sh.put(r, 9, f"=IFERROR({refs.ref('out.end_total')}/{refs.ref('out.start_total')}-1,\"\")",
           role="output", fmt=Fmts.PCT)
    sh.put(r + 1, 1, "The two match because each weight is the asset's share of the starting value.", role="note")
    sh.merge(r + 1, 1, r + 1, LAST)

    sh.freeze("A6")
    widths = [30, 9, 9, 9, 9, 12, 9, 12, 13, 13, 34]
    for c, w in enumerate(widths, start=1):
        sh.col_width(c, w)
    return sh
