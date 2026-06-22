"""
Executive Dashboard (Sheet 1).

An immediate summary built last so it can link every other sheet: company
overview, the dynamic forecast window, forecast-quality indicators (health score
and balance-sheet integrity), headline forecast-horizon CAGRs and auto-updating
trend charts.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..common import FIRST_COL, FY_FMT
from ..formulas import div

M, PCT = Fmt.MONEY, Fmt.PCT
LAST = 12


def build(sh, ctx):
    refs = ctx.refs
    N = ctx.horizon
    m = ctx.data["meta"]
    F = lambda k, t: refs.ref(f"f.{k}@{t}")     # noqa: E731

    def fc(t):
        return FIRST_COL + t

    common.title_block(sh, "EXECUTIVE DASHBOARD",
                       f"{m.get('name','Company')} -- forecast summary", last_col=LAST)
    common.nav_bar(sh, 5, exclude={"Dashboard"})
    r = 7

    # ---- company overview + quality (two panels) ----
    common.section(sh, r, "Company Overview", c1=1, c2=4)
    common.section(sh, r, "Forecast Quality", c1=6, c2=LAST)
    r += 1
    ov = [("Company name", "name", m.get("name")), ("Ticker", "ticker", m.get("ticker")),
          ("Currency", "currency", m.get("currency")), ("Fiscal year end", "fye", m.get("fiscal_year_end"))]
    rr = r
    for label, key, val in ov:
        sh.put(rr, 1, label, role="label")
        sh.put(rr, 2, val, role="input_l", key=f"db.{key}")
        sh.merge(rr, 2, rr, 4)
        rr += 1
    qr = r
    sh.put(qr, 6, "Forecast Health Score", role="label")
    sh.put(qr, 8, f"={refs.ref('d.health')}", role="kpi", fmt=Fmt.INT)
    sh.merge(qr, 8, qr, 9)
    qr += 1
    bc = refs.range("f.balance_check@1", f"f.balance_check@{N}")
    bal = f"MAX(MAX({bc}),-MIN({bc}))"
    sh.put(qr, 6, "Balance-sheet integrity", role="label")
    sh.put(qr, 8, f'=IF({bal}<=1,"PASS","FAIL")', role="status")
    common.traffic_light(sh, f"{sh.coord(qr,8)}:{sh.coord(qr,8)}", sh.coord(qr, 8))
    qr += 1
    sh.put(qr, 6, "Last actual year", role="label")
    sh.put(qr, 8, "=LastActual", role="output", fmt=FY_FMT)
    qr += 1
    sh.put(qr, 6, "Forecast window", role="label")
    sh.put(qr, 8, f'="FY"&(LastActual+1)&" - FY"&(LastActual+{N})', role="output_l")
    sh.merge(qr, 8, qr, LAST)
    r = max(rr, qr) + 1

    # ---- key forecast outputs (CAGRs over the horizon) ----
    r = common.section(sh, r, f"Key Forecast Outputs -- {N}-Year CAGR", c1=1, c2=LAST)
    cagrs = [("Revenue", "revenue"), ("EBITDA", "ebitda"), ("EBIT", "ebit"),
             ("Net income", "net_income"), ("Free cash flow", "fcf")]
    cc = 1
    for label, key in cagrs:
        sh.put(r, cc, label + " CAGR", role="colhdr")
        sh.put(r + 1, cc, f'=IFERROR(({F(key, N)}/{F(key, 0)})^(1/{N})-1,"")', role="kpi", fmt=PCT)
        sh.merge(r, cc, r, cc + 1)
        sh.merge(r + 1, cc, r + 1, cc + 1)
        cc += 2
    sh.row_height(r + 1, 26)
    r += 3

    # ---- chart data block (links to forecast) ----
    r = common.section(sh, r, "Forecast Trends", c1=1, c2=LAST)
    hdr = r
    sh.put(hdr, 1, "Metric", role="colhdr")
    sh.put(hdr, fc(0), "=LastActual", role="actual_hdr", fmt=FY_FMT)
    for t in range(1, N + 1):
        sh.put(hdr, fc(t), f"={sh.local(hdr, fc(t) - 1)}+1", role="fcst_hdr", fmt=FY_FMT)
    r += 1
    series = [("Revenue", lambda t: f"={F('revenue', t)}", M),
              ("EBITDA", lambda t: f"={F('ebitda', t)}", M),
              ("Net income", lambda t: f"={F('net_income', t)}", M),
              ("Free cash flow", lambda t: f"={F('fcf', t)}", M),
              ("EBITDA margin", lambda t: div(F('ebitda', t), F('revenue', t)), PCT),
              ("EBIT margin", lambda t: div(F('ebit', t), F('revenue', t)), PCT),
              ("Net margin", lambda t: div(F('net_income', t), F('revenue', t)), PCT)]
    rowmap = {}
    for label, fn, fmt in series:
        sh.put(r, 1, label, role="formula_l")
        for t in range(0, N + 1):
            sh.put(r, fc(t), fn(t), role="formula", fmt=fmt)
        rowmap[label] = r
        r += 1
    r += 1

    # ---- charts ----
    common.line_chart(sh, f"B{r}", "Revenue & EBITDA", rows=[rowmap["Revenue"], rowmap["EBITDA"]],
                      cat_row=hdr, first_col=fc(0), last_col=fc(N), width=14, height=8)
    common.line_chart(sh, f"H{r}", "Net income & Free cash flow",
                      rows=[rowmap["Net income"], rowmap["Free cash flow"]],
                      cat_row=hdr, first_col=fc(0), last_col=fc(N), width=14, height=8)
    common.line_chart(sh, f"B{r+16}", "Margin evolution",
                      rows=[rowmap["EBITDA margin"], rowmap["Net margin"]],
                      cat_row=hdr, first_col=fc(0), last_col=fc(N), width=14, height=8)

    sh.col_width(1, 20)
    for c in range(2, LAST + 1):
        sh.col_width(c, 11)
    return sh
