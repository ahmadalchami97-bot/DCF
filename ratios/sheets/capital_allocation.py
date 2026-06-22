"""Capital Allocation Analysis (Sheet 11)."""

from __future__ import annotations

from dcf.config import Fmt
from ..formulas import classify_bands, div, growth, q, sentence, text
from ..render import Grid

PCT, MULT = Fmt.PCT, Fmt.MULT2


def build(sh, ctx):
    g = Grid(sh, ctx, "cap")
    R, S = g.R, g.S
    li = ctx.last_hist_idx
    wacc = ctx.refs.ref("coc.wacc")
    roic = ctx.refs.ref(f"prof.roic@{li}")
    g.title("CAPITAL ALLOCATION ANALYSIS", "Distributions, buybacks, reinvestment and discipline")
    g.yearhead("Capital-allocation metric")

    g.section("Distributions")
    pr = g.ratio("payout", "Dividend payout ratio", lambda i: div(R("dividends_paid", i), R("net_income", i)),
                 PCT, ("trend", ("Falling", "Stable", "Rising")))
    g.ratio("div_growth", "Dividend per share growth", lambda i: growth(R("dps", i), R("dps", i - 1)),
            PCT, ("trend", ("Falling", "Stable", "Rising")), start=1)
    g.ratio("buybacks", "Share buybacks", lambda i: f"={R('buybacks', i)}", Fmt.MONEY,
            ("trend", ("Falling", "Stable", "Rising")))
    g.ratio("share_change", "Share count change (− = buyback)", lambda i: growth(R("shares_outstanding", i), R("shares_outstanding", i - 1)),
            PCT, ("bandc", 0, 0.000001, ("Reducing", "Flat", "Diluting")), start=1, reverse=True)
    g.ratio("total_payout", "Total payout (div + buyback) / NI",
            lambda i: div(f'({R("dividends_paid", i)}+{R("buybacks", i)})', R("net_income", i)),
            PCT, ("trend", ("Falling", "Stable", "Rising")))
    g.blank()

    g.section("Reinvestment & Conversion")
    g.ratio("retention", "Retention ratio (1 − payout)",
            lambda i: f'=IFERROR(1-{R("dividends_paid", i)}/{R("net_income", i)},"")', PCT, None)
    g.ratio("fcf_conversion", "FCF conversion (FCF / net income)", lambda i: div(R("fcf", i), R("net_income", i)),
            PCT, ("trend", ("Weak", "Stable", "Strong")))
    g.blank()

    # --- capital allocation score (latest year) ---
    g.section("Capital Allocation Score  (latest year, 0–5)")
    comps = [
        ("Converts ≥80% of profit to FCF", f'=({S("fcf_conversion", li)}>=0.8)*1'),
        ("Reducing share count", f'=({R("shares_outstanding", li)}<{R("shares_outstanding", li-1)})*1'),
        ("ROIC above WACC", f'=({roic}>{wacc})*1'),
        ("Dividend per share rising", f'=({R("dps", li)}>{R("dps", li-1)})*1'),
        ("Disciplined payout (20–100%)", f'=AND({S("total_payout", li)}>=0.2,{S("total_payout", li)}<=1)*1'),
    ]
    comp_first = g.r
    for label, formula in comps:
        sh.put(g.r, 1, "  " + label, role="sublabel")
        sh.put(g.r, 2, formula, role="formula", fmt=Fmt.INT, key=f"cap.comp{g.r}")
        g.r += 1
    comp_last = g.r - 1
    sh.put(g.r, 1, "Capital Allocation Score (/5)", role="label_b")
    sh.put(g.r, 2, f"=SUM(B{comp_first}:B{comp_last})", role="output", fmt=Fmt.INT, key="cap.score")
    sc_cell = sh.local(g.r, 2)
    sh.put(g.r, 3, classify_bands(sc_cell, 2, 4, ("Weak", "Adequate", "Strong")), role="status", key="cap.score.read")
    g._reads.append((g.r, 3))
    g.r += 1
    g.blank()

    g.section("Automated Observations")
    g.commentary(sentence(
        q("» Capital allocation scores "), text(ctx.refs.ref("cap.score"), "0"), q("/5 — "),
        ctx.refs.ref("cap.score.read"), q(". Total payout is "),
        text(S("total_payout", li), "0%"), q(" of net income.")))
    g.commentary(sentence(
        q("» Share count "),
        f'IF({R("shares_outstanding", li)}<{R("shares_outstanding", 0)},"fell from ","rose from ")',
        text(R("shares_outstanding", 0), "#,##0"), q(" to "), text(R("shares_outstanding", li), "#,##0"),
        q("m over the period.")))

    g.chart(comp_first, "Dividend payout ratio", pr, pr, height=7)
    g.finalize()
    return sh
