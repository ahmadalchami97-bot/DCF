"""Efficiency Ratios (Sheet 8)."""

from __future__ import annotations

from dcf.config import Fmt
from ..formulas import div, q, sentence, text
from ..render import Grid

MULT, DAYS = Fmt.MULT2, Fmt.DAYS


def build(sh, ctx):
    g = Grid(sh, ctx, "eff")
    R, S = g.R, g.S
    li = ctx.last_hist_idx
    g.title("EFFICIENCY RATIOS", "Asset utilisation, turnover and the cash conversion cycle")
    g.yearhead("Efficiency ratio")

    g.section("Turnover")
    at = g.ratio("asset_turnover", "Asset turnover", lambda i: div(R("revenue", i), R("avg_assets", i)),
                 MULT, ("trend", ("Weak", "Stable", "Strong")), start=1)
    g.ratio("fixed_turnover", "Fixed-asset turnover", lambda i: div(R("revenue", i), R("avg_fixed_assets", i)),
            MULT, ("trend", ("Weak", "Stable", "Strong")), start=1)
    g.ratio("inventory_turnover", "Inventory turnover", lambda i: div(R("cogs", i), R("avg_inventory", i)),
            MULT, ("trend", ("Weak", "Stable", "Strong")), start=1)
    g.ratio("receivable_turnover", "Receivable turnover", lambda i: div(R("revenue", i), R("avg_receivables", i)),
            MULT, ("trend", ("Weak", "Stable", "Strong")), start=1)
    g.ratio("payable_turnover", "Payable turnover", lambda i: div(R("cogs", i), R("avg_payables", i)),
            MULT, None, start=1)
    g.ratio("wc_turnover", "Working-capital turnover", lambda i: div(R("revenue", i), R("working_capital", i)),
            MULT, None)
    g.blank()

    g.section("Cash Conversion Cycle  (days)")
    g.ratio("dso", "Days sales outstanding (DSO)",
            lambda i: f'=IFERROR({R("avg_receivables", i)}/{R("revenue", i)}*365,"")', DAYS, None, start=1, heat=True, reverse=True)
    g.ratio("dio", "Days inventory outstanding (DIO)",
            lambda i: f'=IFERROR({R("avg_inventory", i)}/{R("cogs", i)}*365,"")', DAYS, None, start=1, heat=True, reverse=True)
    g.ratio("dpo", "Days payable outstanding (DPO)",
            lambda i: f'=IFERROR({R("avg_payables", i)}/{R("cogs", i)}*365,"")', DAYS, None, start=1)
    ccc = g.ratio("ccc", "Cash conversion cycle (DSO+DIO−DPO)",
                  lambda i: f'=IFERROR({S("dso", i)}+{S("dio", i)}-{S("dpo", i)},"")', DAYS,
                  ("bandc", 30, 90, ("Strong", "Adequate", "Weak")), start=1, reverse=True, total=True)
    g.blank()

    g.section("Automated Observations")
    g.commentary(sentence(
        q("» The cash conversion cycle is "), text(S("ccc", li), "0"), q(" days — "),
        ctx.refs.ref("eff.ccc.read"),
        q(" (a negative cycle means customers fund operations)." )))
    g.commentary(sentence(
        q("» Asset turnover of "), text(S("asset_turnover", li), "0.00"),
        q("x shows revenue generated per unit of assets.")))

    g.chart(at, "Turnover ratios", at, at, height=7)
    g.chart(ccc, "Cash conversion cycle", ccc, ccc, kind="bar", height=7)
    g.finalize()
    return sh
