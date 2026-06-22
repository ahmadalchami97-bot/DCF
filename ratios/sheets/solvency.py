"""Solvency Ratios (Sheet 7)."""

from __future__ import annotations

from dcf.config import Fmt
from ..formulas import div, q, sentence, text
from ..render import Grid

PCT, MULT = Fmt.PCT, Fmt.MULT2


def build(sh, ctx):
    g = Grid(sh, ctx, "solv")
    R, S = g.R, g.S
    li = ctx.last_hist_idx
    g.title("SOLVENCY RATIOS", "Leverage, coverage and long-term financial risk")
    g.yearhead("Solvency ratio")

    g.section("Leverage")
    de = g.ratio("debt_to_equity", "Debt / equity", lambda i: div(R("total_debt", i), R("equity", i)),
                 MULT, ("bands", "debt_to_equity"), reverse=True)
    g.ratio("debt_to_assets", "Debt / assets", lambda i: div(R("total_debt", i), R("total_assets", i)),
            PCT, ("bands", "debt_to_assets"), reverse=True)
    g.ratio("debt_to_capital", "Debt / total capital",
            lambda i: div(R("total_debt", i), f'({R("total_debt", i)}+{R("equity", i)})'),
            PCT, ("bands", "debt_to_capital"), reverse=True)
    g.ratio("fin_leverage", "Financial leverage (assets / equity)", lambda i: div(R("total_assets", i), R("equity", i)),
            MULT, ("trend", ("Falling", "Stable", "Rising")), reverse=True)
    g.ratio("equity_ratio", "Equity ratio (equity / assets)", lambda i: div(R("equity", i), R("total_assets", i)),
            PCT, ("trend", ("Weak", "Stable", "Strong")))
    g.blank()

    g.section("Net Debt")
    g.ratio("net_debt", "Net debt (debt − cash)", lambda i: f"={R('net_debt', i)}", Fmt.MONEY, None, heat=False)
    g.ratio("net_debt_ebitda", "Net debt / EBITDA", lambda i: div(R("net_debt", i), R("ebitda", i)),
            MULT, ("bands", "net_debt_ebitda"), reverse=True)
    g.blank()

    g.section("Coverage")
    ic = g.ratio("interest_coverage", "Interest coverage (EBIT / interest)", lambda i: div(R("ebit", i), R("interest_expense", i)),
                 MULT, ("bands", "interest_coverage"))
    g.ratio("ebitda_coverage", "EBITDA / interest", lambda i: div(R("ebitda", i), R("interest_expense", i)),
            MULT, ("trend", ("Weak", "Stable", "Strong")))
    g.ratio("dscr", "Debt-service coverage (EBITDA / (int + ST debt))",
            lambda i: div(R("ebitda", i), f'({R("interest_expense", i)}+{R("short_term_debt", i)})'),
            MULT, ("trend", ("Weak", "Stable", "Strong")))
    g.ratio("fixed_charge", "Fixed-charge coverage (EBIT+D&A) / interest",
            lambda i: div(f'({R("ebit", i)}+{R("depreciation", i)})', R("interest_expense", i)),
            MULT, ("trend", ("Weak", "Stable", "Strong")))
    g.note("Fixed-charge & debt-service coverage are proxies (no lease/principal schedule input).")
    g.blank()

    g.section("Automated Observations")
    g.commentary(sentence(
        q("» Net debt / EBITDA is "), text(S("net_debt_ebitda", li), "0.0"), q("x — "),
        ctx.refs.ref("solv.net_debt_ebitda.read"), q("; debt/equity is "),
        text(S("debt_to_equity", li), "0.00"), q("x.")))
    g.commentary(sentence(
        q("» Interest coverage of "), text(S("interest_coverage", li), "0.0"),
        q("x indicates "), ctx.refs.ref("solv.interest_coverage.read"), q(" debt-servicing capacity.")))

    g.chart(de, "Leverage trend (D/E)", de, de, height=7)
    g.chart(ic, "Interest coverage", ic, ic, height=7)
    g.finalize()
    return sh
