"""
Profitability Ratios (Sheet 5).

Margins, returns on capital and a 3-step DuPont decomposition of ROE. Returns use
the average-balance helpers from the Inputs sheet, so each ratio is a single short
division. Includes trend arrows, traffic-light classification, heat-maps, trend
charts and formula-driven commentary.
"""

from __future__ import annotations

from dcf.config import Fmt
from ..formulas import dirword, div, pick, q, sentence, text
from ..render import Grid

PCT, MULT = Fmt.PCT, Fmt.MULT2


def build(sh, ctx):
    g = Grid(sh, ctx, "prof")
    R, S = g.R, g.S
    li = ctx.last_hist_idx
    g.title("PROFITABILITY RATIOS",
            "Margins, returns on capital and DuPont decomposition")
    g.yearhead("Profitability ratio")

    g.section("Margins")
    g.ratio("gross_margin", "Gross margin", lambda i: div(R("gross_profit", i), R("revenue", i)),
            PCT, ("bands", "gross_margin"))
    m_first = g.r - 1
    g.ratio("ebitda_margin", "EBITDA margin", lambda i: div(R("ebitda", i), R("revenue", i)),
            PCT, ("trend", ("Compressing", "Stable", "Expanding")))
    g.ratio("operating_margin", "Operating margin (EBIT)",
            lambda i: div(R("ebit", i), R("revenue", i)), PCT, ("bands", "operating_margin"))
    g.ratio("pretax_margin", "Pre-tax margin", lambda i: div(R("pretax", i), R("revenue", i)),
            PCT, ("trend", ("Compressing", "Stable", "Expanding")))
    g.ratio("net_margin", "Net margin", lambda i: div(R("net_income", i), R("revenue", i)),
            PCT, ("bands", "net_margin"))
    g.ratio("fcf_margin", "FCF margin", lambda i: div(R("fcf", i), R("revenue", i)),
            PCT, ("bands", "fcf_margin"))
    m_last = g.r - 1
    g.blank()

    g.section("Returns on Capital")
    roe_row = g.ratio("roe", "Return on equity (ROE)", lambda i: div(R("net_income", i), R("avg_equity", i)),
                      PCT, ("bands", "roe"), start=1)
    g.ratio("roa", "Return on assets (ROA)", lambda i: div(R("net_income", i), R("avg_assets", i)),
            PCT, ("bands", "roa"), start=1)
    roic_row = g.ratio("roic", "Return on invested capital (ROIC)",
                       lambda i: div(R("nopat", i), R("avg_invested_capital", i)),
                       PCT, ("bands", "roic"), start=1)
    g.ratio("roce", "Return on capital employed (ROCE)",
            lambda i: div(R("ebit", i), R("capital_employed", i)), PCT, ("bands", "roce"))
    g.ratio("cash_roic", "Cash ROIC (FCF / invested capital)",
            lambda i: div(R("fcf", i), R("invested_capital", i)), PCT,
            ("trend", ("Weak", "Stable", "Strong")))
    g.blank()

    g.section("DuPont Decomposition   (ROE = Net margin × Asset turnover × Equity multiplier)")
    g.ratio("dp_margin", "Net profit margin", lambda i: div(R("net_income", i), R("revenue", i)), PCT, None)
    g.ratio("dp_turnover", "Asset turnover", lambda i: div(R("revenue", i), R("avg_assets", i)),
            MULT, None, start=1)
    g.ratio("dp_leverage", "Equity multiplier (leverage)", lambda i: div(R("avg_assets", i), R("avg_equity", i)),
            MULT, None, start=1)
    g.ratio("dp_roe", "ROE (DuPont, computed)",
            lambda i: f'=IFERROR({S("dp_margin", i)}*{S("dp_turnover", i)}*{S("dp_leverage", i)},"")',
            PCT, None, start=1, total=True)
    g.note("DuPont ROE should equal the ROE above — a built-in audit of the decomposition.")
    g.blank()

    g.section("Capital Retention")
    g.ratio("retention", "Retention ratio (1 − payout)",
            lambda i: f'=IFERROR(1-{R("dividends_paid", i)}/{R("net_income", i)},"")',
            PCT, ("trend", ("Falling", "Stable", "Rising")))
    g.blank()

    g.section("Automated Observations")
    op_lat, op_base = S("operating_margin", li), S("operating_margin", 0)
    g.commentary(sentence(
        q("» Operating margin "), dirword(op_lat, op_base, ("contracted", "was broadly flat", "expanded")),
        q(" by "), f'TEXT(ABS(({op_lat}-{op_base})*10000),"#,##0")', q(" bps over the historical period, to "),
        text(op_lat, "0.0%"), q(".")))
    roic_lat, wacc = S("roic", li), ctx.refs.ref("coc.wacc")
    g.commentary(sentence(
        q("» ROIC of "), text(roic_lat, "0.0%"), q(" is "), pick(f"{roic_lat}>{wacc}", q("above"), q("below")),
        q(" the WACC of "), text(wacc, "0.0%"), q(" — "),
        pick(f"{roic_lat}>{wacc}", q("the business is creating economic value."),
             q("the business is not covering its cost of capital."))))
    g.commentary(sentence(
        q("» Net margin is currently "), text(S("net_margin", li), "0.0%"), q(" — assessed "),
        ctx.refs.ref("prof.net_margin.read"), q(".")))

    g.chart(m_first, "Margin trends", m_first, m_last, height=8)
    g.chart(roe_row, "Returns on capital", roe_row, roic_row, height=8)

    g.finalize()
    return sh
