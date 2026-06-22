"""Liquidity Ratios (Sheet 6)."""

from __future__ import annotations

from dcf.config import Fmt
from ..formulas import div, q, sentence, text
from ..render import Grid

PCT, MULT = Fmt.PCT, Fmt.MULT2


def build(sh, ctx):
    g = Grid(sh, ctx, "liq")
    R, S = g.R, g.S
    li = ctx.last_hist_idx
    g.title("LIQUIDITY RATIOS", "Short-term solvency and working-capital strength")
    g.yearhead("Liquidity ratio")

    g.section("Coverage of Current Liabilities")
    cr = g.ratio("current_ratio", "Current ratio", lambda i: div(R("current_assets", i), R("current_liabilities", i)),
                 MULT, ("bands", "current_ratio"))
    g.ratio("quick_ratio", "Quick ratio (ex-inventory)",
            lambda i: div(f'({R("current_assets", i)}-{R("inventory", i)})', R("current_liabilities", i)),
            MULT, ("bands", "quick_ratio"))
    cashr = g.ratio("cash_ratio", "Cash ratio", lambda i: div(R("cash", i), R("current_liabilities", i)),
                    MULT, ("bands", "cash_ratio"))
    g.blank()

    g.section("Working Capital")
    g.ratio("working_capital", "Working capital", lambda i: f"={R('working_capital', i)}",
            Fmt.MONEY, ("trend", ("Falling", "Stable", "Rising")))
    g.ratio("wc_to_rev", "Working capital / revenue", lambda i: div(R("working_capital", i), R("revenue", i)),
            PCT, ("trend", ("Falling", "Stable", "Rising")))
    g.blank()

    g.section("Cash-Flow Liquidity")
    g.ratio("ocf_ratio", "Operating cash flow ratio", lambda i: div(R("operating_cash_flow", i), R("current_liabilities", i)),
            MULT, ("trend", ("Weak", "Stable", "Strong")))
    g.ratio("cash_conv", "Cash conversion (OCF / net income)", lambda i: div(R("operating_cash_flow", i), R("net_income", i)),
            PCT, ("trend", ("Weak", "Stable", "Strong")))
    g.blank()

    g.section("Automated Observations")
    g.commentary(sentence(
        q("» Current ratio of "), text(S("current_ratio", li), "0.00"), q("x is assessed "),
        ctx.refs.ref("liq.current_ratio.read"), q("; the cash ratio is "),
        text(S("cash_ratio", li), "0.00"), q("x.")))
    g.commentary(sentence(
        q("» Operations convert "), text(S("cash_conv", li), "0%"),
        q(" of net income into operating cash — a check on earnings quality.")))

    g.chart(cr, "Liquidity ratios", cr, cashr, height=8)
    g.finalize()
    return sh
