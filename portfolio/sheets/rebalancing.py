"""
Rebalancing.

Turns the recommended allocation into concrete actions: for each asset, the
current value and weight, the recommended weight and value, the buy/sell amount,
a Buy / Sell / Hold action, and a plain-English reason. Small gaps are left as
Hold so you are not trading on noise.
"""

from __future__ import annotations

from .. import common
from ..config import ASSETS, Defaults, Fmts

LAST = 8


def build(sh, ctx):
    refs = ctx.refs
    keys = ctx.keys
    k0, kN = keys[0], keys[-1]
    band = Defaults.REBALANCE_BAND
    OUT = lambda k, key: refs.ref(f"out.{k}@{key}")   # noqa: E731

    common.title_block(sh, "REBALANCING", "What to buy, sell or hold to reach the recommended allocation",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "WHAT THIS SHEET TELLS YOU:  the exact trades to move from your current portfolio to the recommended one "
        "(chosen on the Allocation sheet, Step 5).",
        "HOW TO READ IT:  Buy/Sell amount = Target value - Current value (positive = buy, negative = sell). "
        f"If the weight gap is small (within {band:.0%}), the action is Hold so you don't trade on noise.",
        "The Reason column explains each action in plain language (risk, scenario and target weight).",
    ], last_col=LAST)
    r += 1

    avg_vol = f"IFERROR(AVERAGE({refs.range('rr.vol@' + k0, 'rr.vol@' + kN)}),0)"

    hdr = r
    cols = ["Asset", f"Current value\n({ctx.base_ccy})", "Current\nweight", "Recommended\nweight",
            f"Target value\n({ctx.base_ccy})", f"Buy / Sell\n({ctx.base_ccy})", "Action", "Reason"]
    for c, t in enumerate(cols, 1):
        sh.put(hdr, c, t, role="colhdr" if c > 1 else "colhdr_l")
    common.cell_comment(sh, hdr, 6, "Buy/Sell = Target value - Current value.\n"
                                    "Target value = Recommended weight x Total invested.")
    common.cell_comment(sh, hdr, 7, f"Buy if recommended weight is above current, Sell if below, "
                                    f"Hold if the gap is within {band:.0%}.")
    sh.row_height(hdr, 26)
    r += 1
    first = r
    for key, name, _ in ASSETS:
        cur_w = OUT("weight", key)
        rec_w = refs.ref(f"al.rec_w@{key}")
        cur_v = OUT("start_val", key)
        scen = OUT("curradj", key)
        vol = refs.ref(f"rr.vol@{key}")
        sh.put(r, 1, name, role="label")
        sh.put(r, 2, f"={cur_v}", role="link", fmt=Fmts.MONEY)
        sh.put(r, 3, f"={cur_w}", role="link", fmt=Fmts.PCT)
        sh.put(r, 4, f"={rec_w}", role="link", fmt=Fmts.PCT)
        sh.put(r, 5, f"={rec_w}*TotalInvested", role="formula", fmt=Fmts.MONEY, key=f"rb.target_val@{key}")
        sh.put(r, 6, f"={sh.local(r, 5)}-{sh.local(r, 2)}", role="output", fmt=Fmts.MONEY, key=f"rb.trade@{key}")
        action = f'=IF(ABS({rec_w}-{cur_w})<={band},"Hold",IF({rec_w}>{cur_w},"Buy","Sell"))'
        sh.put(r, 7, action, role="status", key=f"rb.action@{key}")
        # plain-English reason
        act = sh.local(r, 7)
        driver_buy = f'IF({vol}<={avg_vol},"it is a calmer asset that lowers portfolio volatility","it improves long-term return per unit of risk")'
        driver_sell = f'IF({scen}<0,"it was weak in this scenario and its weight is above target","its weight is above target and scenario-adjusted risk is high")'
        reason = (f'=IF({act}="Hold","{name} is already near target - no trade needed.",'
                  f'IF({act}="Buy","Increase {name} because "&{driver_buy}&".",'
                  f'"Reduce {name} because "&{driver_sell}&"."))')
        sh.put(r, 8, reason, role="formula_l")
        sh.merge(r, 8, r, LAST)
        r += 1
    last = r - 1
    sh.put(r, 1, "Total", role="total_l")
    sh.put(r, 2, f"=SUM({refs.range('out.start_val@' + k0, 'out.start_val@' + kN)})", role="total", fmt=Fmts.MONEY)
    sh.put(r, 3, f"=SUM({refs.range('out.weight@' + k0, 'out.weight@' + kN)})", role="total", fmt=Fmts.PCT)
    sh.put(r, 4, f"=SUM({refs.range('al.rec_w@' + k0, 'al.rec_w@' + kN)})", role="total", fmt=Fmts.PCT)
    sh.put(r, 5, f"=SUM({refs.range('rb.target_val@' + k0, 'rb.target_val@' + kN)})", role="total", fmt=Fmts.MONEY)
    sh.put(r, 6, f"=SUM({refs.range('rb.trade@' + k0, 'rb.trade@' + kN)})", role="total", fmt=Fmts.MONEY)
    common.traffic_light(sh, f"{common.col_letter(7)}{first}:{common.col_letter(7)}{last}", f"{common.col_letter(7)}{first}")
    sh.put(r + 1, 1, "The Buy/Sell column should sum to about 0 (a rebalance moves money between assets, it does not "
                     "add or remove cash).", role="note")
    sh.merge(r + 1, 1, r + 1, LAST)

    sh.freeze("A6")
    widths = [26, 14, 9, 11, 14, 13, 9, 60]
    for c, w in enumerate(widths, 1):
        sh.col_width(c, w)
    return sh
