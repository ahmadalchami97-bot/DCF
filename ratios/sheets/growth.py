"""Growth Analysis (Sheet 9): year-on-year growth + a 3/5/10-year CAGR scorecard."""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..formulas import cagr, growth, q, sentence, text
from ..render import Grid

PCT = Fmt.PCT
ACCEL = ("Decelerating", "Stable", "Accelerating")


def build(sh, ctx):
    g = Grid(sh, ctx, "grow")
    R, S = g.R, g.S
    li = ctx.last_hist_idx
    g.title("GROWTH ANALYSIS", "Year-on-year growth and compound annual growth rates")
    g.yearhead("Growth metric")

    g.section("Year-on-Year Growth")
    rev = g.ratio("revenue", "Revenue growth", lambda i: growth(R("revenue", i), R("revenue", i - 1)),
                  PCT, ("trend", ACCEL), start=1)
    g.ratio("ebitda", "EBITDA growth", lambda i: growth(R("ebitda", i), R("ebitda", i - 1)), PCT, ("trend", ACCEL), start=1)
    g.ratio("ebit", "EBIT growth", lambda i: growth(R("ebit", i), R("ebit", i - 1)), PCT, ("trend", ACCEL), start=1)
    g.ratio("net_income", "Net income growth", lambda i: growth(R("net_income", i), R("net_income", i - 1)), PCT, ("trend", ACCEL), start=1)
    g.ratio("fcf", "Free cash flow growth", lambda i: growth(R("fcf", i), R("fcf", i - 1)), PCT, ("trend", ACCEL), start=1)
    g.ratio("assets", "Asset growth", lambda i: growth(R("total_assets", i), R("total_assets", i - 1)), PCT, ("trend", ACCEL), start=1)
    eq = g.ratio("equity", "Equity growth", lambda i: growth(R("equity", i), R("equity", i - 1)), PCT, ("trend", ACCEL), start=1)
    g.blank()

    g.section("Compound Annual Growth (CAGR)")
    sh.put(g.r, 1, "Metric", role="colhdr")
    sh.put(g.r, 2, "3-Year", role="colhdr_r")
    sh.put(g.r, 3, "5-Year", role="colhdr_r")
    sh.put(g.r, 4, f"10-Year ({ctx.periods[0]}–{ctx.periods[li]})", role="colhdr_r")
    sh.merge(g.r, 4, g.r, 6)
    g.r += 1
    metrics = [("Revenue", "revenue"), ("EBITDA", "ebitda"), ("EBIT", "ebit"),
               ("Net income", "net_income"), ("Free cash flow", "fcf"),
               ("Total assets", "total_assets"), ("Equity", "equity")]
    cagr_first = g.r
    for label, key in metrics:
        sh.put(g.r, 1, label, role="label")
        sh.put(g.r, 2, cagr(R(key, li), R(key, li - 3), 3), role="output", fmt=PCT, key=f"grow.cagr3.{key}")
        sh.put(g.r, 3, cagr(R(key, li), R(key, li - 5), 5), role="output", fmt=PCT, key=f"grow.cagr5.{key}")
        sh.put(g.r, 4, cagr(R(key, li), R(key, 0), li), role="output", fmt=PCT, key=f"grow.cagr10.{key}")
        sh.merge(g.r, 4, g.r, 6)
        g.r += 1
    common.heat_map(sh, f"B{cagr_first}:D{g.r-1}")
    g.blank()

    g.section("Automated Observations")
    g.commentary(sentence(
        q("» Revenue compounded at "), text(ctx.refs.ref("grow.cagr5.revenue"), "0.0%"),
        q(" over 5 years and "), text(ctx.refs.ref("grow.cagr10.revenue"), "0.0%"),
        q(" over the full window; latest-year growth is "), text(S("revenue", li), "0.0%"), q(".")))
    g.commentary(sentence(
        q("» Net income grew "), text(ctx.refs.ref("grow.cagr5.net_income"), "0.0%"),
        q(" (5y CAGR) vs revenue "), text(ctx.refs.ref("grow.cagr5.revenue"), "0.0%"),
        q(" — profit "),
        f'IF({ctx.refs.ref("grow.cagr5.net_income")}>{ctx.refs.ref("grow.cagr5.revenue")},"outgrew","lagged")',
        q(" the top line.")))

    g.chart(rev, "Revenue & earnings growth", rev, eq, height=8)
    g.finalize()
    return sh
