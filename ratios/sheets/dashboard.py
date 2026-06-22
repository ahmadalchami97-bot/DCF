"""
Executive Dashboard (Sheet 2).

A one-screen scorecard: six category scores (0–100) with data-bar progress bars
and traffic-light assessments, an overall quality score, key-metric trend arrows,
and formula-driven observations that read live from the analysis sheets.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..formulas import arrow, classify_bands, q, sentence, text

LAST = 9


def build(sh, ctx):
    refs = ctx.refs
    li = ctx.last_hist_idx
    P = lambda k: refs.ref(f"prof.{k}@{li}")     # noqa: E731
    wacc = refs.ref("coc.wacc")

    common.title_block(sh, "EXECUTIVE DASHBOARD",
                       f"{ctx.data['meta'].get('name','Company')} — quality scorecard & key signals",
                       last_col=LAST)
    common.nav_bar(sh, 5, exclude={"Home"})
    r = 7

    # ---- scorecard ----
    common.section(sh, r, "Quality Scorecard  (0–100, higher = better)", c1=1, c2=5)
    common.section(sh, r, "Key-Metric Trends", c1=6, c2=LAST)
    r += 1
    sh.put(r, 1, "Category", role="colhdr")
    sh.put(r, 2, "Score", role="colhdr_r")
    sh.put(r, 3, "Assessment", role="colhdr")
    sh.merge(r, 3, r, 5)
    sh.put(r, 6, "Metric", role="colhdr")
    sh.put(r, 7, "Latest", role="colhdr_r")
    sh.put(r, 8, "Trend", role="colhdr")
    sh.put(r, 9, "Read", role="colhdr")
    hdr = r
    r += 1

    avg = lambda terms: '=IFERROR(ROUND(AVERAGE(' + ",".join(terms) + ')*100,0),"")'  # noqa: E731
    scores = [
        ("Profitability", avg([f"MIN({P('net_margin')}/0.2,1)", f"MIN({P('roe')}/0.15,1)",
                               f"MIN({P('roic')}/0.12,1)", f"MIN({P('operating_margin')}/0.18,1)"])),
        ("Liquidity", avg([f"MIN({refs.ref(f'liq.current_ratio@{li}')}/2,1)",
                           f"MIN({refs.ref(f'liq.cash_ratio@{li}')}/0.5,1)",
                           f"MIN({refs.ref(f'liq.ocf_ratio@{li}')}/1,1)"])),
        ("Solvency", avg([f"MIN({refs.ref(f'solv.interest_coverage@{li}')}/6,1)",
                          f"MIN({refs.ref(f'solv.equity_ratio@{li}')},1)",
                          f"MIN(MAX(0,1-{refs.ref(f'solv.net_debt_ebitda@{li}')}/4),1)"])),
        ("Efficiency", avg([f"MIN({refs.ref(f'eff.asset_turnover@{li}')}/1,1)",
                            f"MIN({refs.ref(f'eff.inventory_turnover@{li}')}/8,1)",
                            f"MIN({refs.ref(f'eff.receivable_turnover@{li}')}/10,1)"])),
        ("Growth", avg([f"MIN({refs.ref('grow.cagr5.revenue')}/0.1,1)",
                        f"MIN({refs.ref('grow.cagr5.net_income')}/0.1,1)"])),
        ("Valuation (cheapness)", avg([f"MIN({refs.ref(f'val.fcf_yield@{li}')}/0.06,1)",
                                       f"MIN({refs.ref(f'val.earnings_yield@{li}')}/0.05,1)"])),
    ]
    score_first = r
    for name, formula in scores:
        sh.put(r, 1, name, role="label")
        sh.put(r, 2, formula, role="output", fmt=Fmt.INT, key=f"db.score.{name[:4]}")
        sc = sh.local(r, 2)
        sh.put(r, 3, classify_bands(sc, 40, 70, ("Weak", "Moderate", "Strong")), role="status")
        sh.merge(r, 3, r, 5)
        r += 1
    score_last = r - 1
    sh.put(r, 1, "OVERALL QUALITY SCORE", role="label_b")
    overall = f'=IFERROR(ROUND(AVERAGE(B{score_first}:B{score_last}),0),"")'
    sh.put(r, 2, overall, role="output", fmt=Fmt.INT, key="db.score.overall")
    osc = sh.local(r, 2)
    sh.put(r, 3, classify_bands(osc, 40, 70, ("Weak", "Moderate", "Strong")), role="status")
    sh.merge(r, 3, r, 5)
    overall_row = r
    common.data_bars(sh, f"B{score_first}:B{overall_row}")
    common.traffic_light(sh, f"C{score_first}:C{overall_row}", f"C{score_first}")

    # ---- key-metric trends (right panel, aligned to scorecard rows) ----
    metrics = [
        ("ROE", P("roe"), refs.ref(f"prof.roe@{li-1}"), Fmt.PCT, refs.ref("prof.roe.read")),
        ("Operating margin", P("operating_margin"), refs.ref(f"prof.operating_margin@{li-1}"), Fmt.PCT, refs.ref("prof.operating_margin.read")),
        ("Revenue growth", refs.ref(f"grow.revenue@{li}"), refs.ref(f"grow.revenue@{li-1}"), Fmt.PCT, refs.ref("grow.revenue.read")),
        ("Net debt / EBITDA", refs.ref(f"solv.net_debt_ebitda@{li}"), refs.ref(f"solv.net_debt_ebitda@{li-1}"), Fmt.MULT2, refs.ref("solv.net_debt_ebitda.read")),
        ("FCF margin", P("fcf_margin"), refs.ref(f"prof.fcf_margin@{li-1}"), Fmt.PCT, refs.ref("prof.fcf_margin.read")),
        ("ROIC", P("roic"), refs.ref(f"prof.roic@{li-1}"), Fmt.PCT, refs.ref("prof.roic.read")),
    ]
    mr = hdr + 1
    km_reads = []
    for label, latest, prior, fmt, read in metrics:
        sh.put(mr, 6, label, role="label")
        sh.put(mr, 7, f"={latest}", role="output", fmt=fmt)
        sh.put(mr, 8, arrow(latest, prior), role="status")
        sh.put(mr, 9, f"={read}", role="status")
        km_reads.append(mr)
        mr += 1
    common.traffic_light(sh, f"I{km_reads[0]}:I{km_reads[-1]}", f"I{km_reads[0]}")
    r = max(r, mr) + 1

    # ---- headline metrics strip ----
    common.section(sh, r, "Headline Metrics (latest year)", c1=1, c2=LAST)
    r += 1
    kpis = [
        ("Revenue", f"={refs.ref(f'in.revenue@{li}')}", Fmt.MONEY),
        ("Net income", f"={refs.ref(f'in.net_income@{li}')}", Fmt.MONEY),
        ("FCF", f"={refs.ref(f'in.fcf@{li}')}", Fmt.MONEY),
        ("ROIC − WACC", f"=IFERROR({P('roic')}-{wacc},\"\")", Fmt.PCT),
        ("Altman Z", f"={refs.ref(f'qual.z@{li}')}", Fmt.FLOAT2),
        ("Piotroski F", f"={refs.ref(f'qual.f@{li}')}", Fmt.INT),
    ]
    cc = 1
    for label, formula, fmt in kpis:
        sh.put(r, cc, label, role="colhdr")
        sh.put(r + 1, cc, formula, role="kpi", fmt=fmt)
        sh.merge(r, cc, r, cc + 0)
        cc += 1
        if cc > LAST:
            cc = 1
    sh.row_height(r + 1, 28)
    r += 3

    # ---- automated observations ----
    common.section(sh, r, "Automated Observations", c1=1, c2=LAST)
    r += 1
    obs = [
        sentence(q("» Profitability: ROE "), text(P("roe"), "0.0%"), q(" ("), refs.ref("prof.roe.read"),
                 q("), ROIC "), text(P("roic"), "0.0%"), q(" vs WACC "), text(wacc, "0.0%"), q("."),),
        sentence(q("» Margins: operating margin "), text(P("operating_margin"), "0.0%"),
                 q(" — "), refs.ref("prof.operating_margin.read"), q(" versus history."),),
        sentence(q("» Leverage: net debt / EBITDA "), text(refs.ref(f"solv.net_debt_ebitda@{li}"), "0.0"),
                 q("x — "), refs.ref("solv.net_debt_ebitda.read"), q(" risk."),),
        sentence(q("» Cash: FCF margin "), text(P("fcf_margin"), "0.0%"), q(" ("),
                 refs.ref("prof.fcf_margin.read"), q("); FCF "), text(refs.ref(f"in.fcf@{li}"), "#,##0"), q("."),),
        sentence(q("» Quality: Altman Z "), text(refs.ref(f"qual.z@{li}"), "0.0"), q(" ("),
                 refs.ref("qual.z.read"), q("), Piotroski "), text(refs.ref(f"qual.f@{li}"), "0"),
                 q("/9, Beneish "), refs.ref("qual.m.read"), q("."),),
        sentence(q("» Data health: "), refs.ref("qc.verdict"), q("."),),
    ]
    for o in obs:
        sh.put(r, 1, o, role="panel", align="lw")
        sh.merge(r, 1, r, LAST)
        sh.row_height(r, 18)
        r += 1

    sh.col_width(1, 22)
    for c in range(2, LAST + 1):
        sh.col_width(c, 13)
    return sh
