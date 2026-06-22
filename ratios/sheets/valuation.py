"""Valuation Ratios (Sheet 10) with a fully transparent enterprise-value build."""

from __future__ import annotations

from dcf.config import Fmt
from ..formulas import div, q, sentence, text
from ..render import Grid

MULT, PCT, X = Fmt.MULT2, Fmt.PCT, Fmt.PER_SHARE
# valuation reads are relative to the company's OWN history
CHEAP = ("Below avg", "In-line", "Above avg")
YIELDW = ("Low", "Average", "High")


def build(sh, ctx):
    g = Grid(sh, ctx, "val")
    R, S = g.R, g.S
    n, li = ctx.n_years, ctx.last_hist_idx
    g.title("VALUATION RATIOS", "Multiples and yields with a transparent EV bridge")
    g.yearhead("Valuation metric")

    g.section("Enterprise Value Build  (every step shown)")
    g.ratio("market_cap", "Market capitalisation", lambda i: f"={R('market_cap', i)}", Fmt.MONEY, None, arrow=False, heat=False)
    g.ratio("plus_debt", "(+) Total debt", lambda i: f"={R('total_debt', i)}", Fmt.MONEY, None, arrow=False, heat=False)
    g.ratio("less_cash", "(−) Cash & equivalents", lambda i: f"=-{R('cash', i)}", Fmt.MONEY, None, arrow=False, heat=False)
    g.ratio("ev", "(=) Enterprise value", lambda i: f"={R('enterprise_value', i)}", Fmt.MONEY, None, arrow=False, heat=False, total=True)
    g.blank()

    g.section("Earnings Multiples")
    pe = g.ratio("pe", "P / E", lambda i: div(R("market_cap", i), R("net_income", i)), MULT, ("trend", CHEAP), reverse=True)
    g.ratio("fwd_pe", "Forward P / E", lambda i: ('=""' if i >= n - 1 else div(R("market_cap", i), R("net_income", i + 1))),
            MULT, ("trend", CHEAP), reverse=True)
    g.ratio("peg", "PEG (P/E ÷ earnings growth)",
            lambda i: f'=IFERROR(({R("market_cap", i)}/{R("net_income", i)})/(({R("net_income", i)}/{R("net_income", i-1)}-1)*100),"")',
            MULT, None, start=1)
    g.ratio("earnings_yield", "Earnings yield", lambda i: div(R("net_income", i), R("market_cap", i)), PCT, ("trend", YIELDW))
    g.blank()

    g.section("Enterprise-Value Multiples")
    g.ratio("ev_rev", "EV / Revenue", lambda i: div(R("enterprise_value", i), R("revenue", i)), MULT, ("trend", CHEAP), reverse=True)
    evebitda = g.ratio("ev_ebitda", "EV / EBITDA", lambda i: div(R("enterprise_value", i), R("ebitda", i)), MULT, ("trend", CHEAP), reverse=True)
    g.ratio("ev_ebit", "EV / EBIT", lambda i: div(R("enterprise_value", i), R("ebit", i)), MULT, ("trend", CHEAP), reverse=True)
    g.ratio("ev_fcf", "EV / FCF", lambda i: div(R("enterprise_value", i), R("fcf", i)), MULT, ("trend", CHEAP), reverse=True)
    g.blank()

    g.section("Book & Cash-Flow Multiples / Yields")
    g.ratio("pb", "P / B", lambda i: div(R("market_cap", i), R("equity", i)), MULT, ("trend", CHEAP), reverse=True)
    g.ratio("ptbv", "P / Tangible book", lambda i: div(R("market_cap", i), R("tangible_book", i)), MULT, ("trend", CHEAP), reverse=True)
    g.ratio("pfcf", "P / FCF", lambda i: div(R("market_cap", i), R("fcf", i)), MULT, ("trend", CHEAP), reverse=True)
    g.ratio("fcf_yield", "FCF yield", lambda i: div(R("fcf", i), R("market_cap", i)), PCT, ("trend", YIELDW))
    g.ratio("div_yield", "Dividend yield", lambda i: div(R("dps", i), R("share_price", i)), PCT, ("trend", YIELDW))
    g.blank()

    g.section("Automated Observations")
    g.commentary(sentence(
        q("» Shares trade on "), text(S("ev_ebitda", li), "0.0"), q("x EV/EBITDA and "),
        text(S("pe", li), "0.0"), q("x P/E — "), ctx.refs.ref("val.ev_ebitda.read"),
        q(" versus the company's own history.")))
    g.commentary(sentence(
        q("» FCF yield is "), text(S("fcf_yield", li), "0.0%"), q(" and earnings yield "),
        text(S("earnings_yield", li), "0.0%"), q(", the inverse of the P/E.")))

    g.chart(pe, "P/E and EV/EBITDA", pe, pe, height=7)
    g.chart(evebitda, "EV / EBITDA", evebitda, evebitda, height=7)
    g.finalize()
    return sh
