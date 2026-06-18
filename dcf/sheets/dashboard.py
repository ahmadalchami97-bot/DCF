"""
Dashboard sheet -- the one-page investment tearsheet.

Pulls the headline numbers and plain-English reads from every other sheet into a
clean, two-panel summary: company snapshot, headline valuation, operating KPIs,
returns & balance-sheet health, the DCF bridge, the scenario range, a risk-flag
panel and a single formula-driven investment view. Nothing is recomputed here
that already lives elsewhere — the dashboard links, so it always agrees with the
detail sheets.
"""

from __future__ import annotations

from ..config import Fmt, SCENARIOS, Thresholds as T
from ..utils import label_compare
from . import common

# two side-by-side panels
L1, V1, R1, GAP, L2, V2, R2 = 1, 2, 3, 4, 5, 6, 7
LASTCOL = 7


def build(sh, ctx: common.Context):
    refs = ctx.refs
    last = ctx.n_hist - 1
    I = lambda k: refs.ref(f"in.{k}")           # noqa: E731 scalar input
    R = lambda k, p: refs.ref(f"in.{k}@{p}")    # noqa: E731
    H = lambda k, p: refs.ref(f"h.{k}@{p}")     # noqa: E731
    HL = lambda k: refs.ref(f"h.lbl.{k}")       # noqa: E731 historical label
    Dk = lambda k: refs.ref(f"dcf.{k}")         # noqa: E731
    SC = lambda s, k: refs.ref(f"sc.{s}.{k}")   # noqa: E731

    sh.hide_gridlines()
    for c, w in ((L1, 30), (V1, 13), (R1, 17), (GAP, 3), (L2, 28), (V2, 13), (R2, 15)):
        sh.col_width(c, w)
    r = common.title_block(sh, "INVESTMENT DASHBOARD",
                           f"{ctx.data['meta'].get('name','Company')} — summary analysis pack",
                           last_col=LASTCOL)
    r += 1
    read_rows = []

    def kpi(row, base, label, value, fmt=Fmt.MONEY, read=None, vrole="link", bold=False):
        sh.put(row, base, label, role="label_b" if bold else "label")
        if value is not None:
            sh.put(row, base + 1, value, role=vrole, fmt=fmt, bold=bold or None)
        if read is not None:
            sh.put(row, base + 2, read, role="link", align="c")
            read_rows.append((row, base + 2))
        return row + 1

    # ===== band 1: snapshot (left) + headline valuation (right) ==========
    common.subsection(sh, r, "Company Snapshot", c1=L1, c2=R1)
    common.subsection(sh, r, "Headline Valuation", c1=L2, c2=R2)
    r += 1
    lr = r
    lr = kpi(lr, L1, "Company", f"={I('name')}", Fmt.TEXT, vrole="link")
    lr = kpi(lr, L1, "Ticker", f"={I('ticker')}", Fmt.TEXT)
    lr = kpi(lr, L1, "Business type", f"={I('business_type')}", Fmt.TEXT)
    lr = kpi(lr, L1, "Currency / units", f'={I("currency")}&" "&{I("units")}', Fmt.TEXT)
    lr = kpi(lr, L1, "Fiscal year end", f"={I('fye')}", Fmt.TEXT)
    lr = kpi(lr, L1, f"Revenue ({ctx.last_hist_label})", f"={R('revenue', last)}", Fmt.MONEY)

    rr = r
    rr = kpi(rr, L2, "DCF value per share", f"={Dk('value_per_share')}", Fmt.PER_SHARE,
             vrole="result", bold=True)
    rr = kpi(rr, L2, "Current share price", f"={Dk('current_price')}", Fmt.PER_SHARE)
    rr = kpi(rr, L2, "Upside / (downside)", f"={Dk('upside')}", Fmt.PCT, vrole="output", bold=True)
    sh.put(rr, L2, "Valuation read", role="label_b")
    sh.put(rr, V2, f"={Dk('val_label')}", role="link", align="c")
    read_rows.append((rr, V2))
    sh.merge(rr, V2, rr, R2)
    rr += 1
    rr = kpi(rr, L2, "WACC", f"={refs.ref('wacc.value')}", Fmt.PCT2)
    rr = kpi(rr, L2, "Enterprise value", f"={Dk('ev')}", Fmt.MONEY)
    r = max(lr, rr) + 1

    # ===== band 2: operating KPIs (left) + returns/leverage (right) ======
    common.subsection(sh, r, "Operating KPIs (latest)", c1=L1, c2=R1)
    common.subsection(sh, r, "Returns & Balance-Sheet Health", c1=L2, c2=R2)
    r += 1
    lr = rr = r
    lr = kpi(lr, L1, "Revenue growth", f"={H('rev_growth', last)}", Fmt.PCT, read=f"={HL('rev_growth')}")
    lr = kpi(lr, L1, "Gross margin", f"={H('gross_margin', last)}", Fmt.PCT, read=f"={HL('gross_margin')}")
    lr = kpi(lr, L1, "EBITDA margin", f"={H('ebitda_margin', last)}", Fmt.PCT, read=f"={HL('ebitda_margin')}")
    lr = kpi(lr, L1, "EBIT margin", f"={H('ebit_margin', last)}", Fmt.PCT, read=f"={HL('ebit_margin')}")
    lr = kpi(lr, L1, "Net margin", f"={H('net_margin', last)}", Fmt.PCT, read=f"={HL('net_margin')}")
    lr = kpi(lr, L1, "FCF margin", f"={H('fcf_margin', last)}", Fmt.PCT, read=f"={HL('fcf_margin')}")

    rr = kpi(rr, L2, "ROE", f"={H('roe', last)}", Fmt.PCT, read=f"={HL('roe')}")
    rr = kpi(rr, L2, "ROIC", f"={H('roic', last)}", Fmt.PCT, read=f"={HL('roic')}")
    rr = kpi(rr, L2, "ROIC vs WACC",
             f'=IFERROR({H("roic", last)}-{refs.ref("wacc.value")},"n/a")', Fmt.PCT,
             read=label_compare(H("roic", last), refs.ref("wacc.value"), 0.01))
    rr = kpi(rr, L2, "Net debt / EBITDA", f"={H('net_debt_ebitda', last)}", Fmt.MULT,
             read=f"={HL('net_debt_ebitda')}")
    rr = kpi(rr, L2, "Interest coverage", f"={H('interest_coverage', last)}", Fmt.MULT,
             read=f"={HL('interest_coverage')}")
    rr = kpi(rr, L2, "Current ratio", f"={H('current_ratio', last)}", Fmt.MULT2,
             read=f"={HL('current_ratio')}")
    r = max(lr, rr) + 1

    # ===== band 3: DCF bridge (left) + scenario range (right) ============
    common.subsection(sh, r, "DCF Bridge", c1=L1, c2=R1)
    common.subsection(sh, r, "Scenario Range (value / share)", c1=L2, c2=R2)
    r += 1
    lr = rr = r
    lr = kpi(lr, L1, "Σ PV explicit FCFF", f"={Dk('sum_pv_fcff')}", Fmt.MONEY)
    lr = kpi(lr, L1, "(+) PV terminal value", f"={Dk('pv_tv')}", Fmt.MONEY)
    lr = kpi(lr, L1, "Enterprise value", f"={Dk('ev')}", Fmt.MONEY, bold=True)
    lr = kpi(lr, L1, "(−) Net debt", f"={Dk('net_debt')}", Fmt.MONEY)
    lr = kpi(lr, L1, "Equity value", f"={Dk('equity_value')}", Fmt.MONEY, bold=True)
    lr = kpi(lr, L1, "TV % of EV", f"={Dk('tv_share')}", Fmt.PCT)

    for s in SCENARIOS:
        rr = kpi(rr, L2, f"{s}", f"={SC(s, 'per_share')}", Fmt.PER_SHARE,
                 read=f"={SC(s, 'upside')}", vrole="link")
        # show upside as % read; recolour numerically below
        sh.ws.cell(row=rr - 1, column=R2).number_format = Fmt.PCT
        read_rows.pop()  # upside is numeric, not a word -> don't colour as label
    r = max(lr, rr) + 1

    # ===== band 4: risk flags ============================================
    common.section(sh, r, "Risk Flags", c1=1, c2=LASTCOL)
    r += 1
    flags = [
        ("Leverage (net debt / EBITDA)", f"={HL('net_debt_ebitda')}"),
        ("Interest coverage", f"={HL('interest_coverage')}"),
        ("Liquidity (current ratio)", f"={HL('current_ratio')}"),
        ("Revenue growth trend", f"={HL('rev_growth')}"),
        ("Margin trend (gross)", f"={HL('gross_margin')}"),
        ("Capital efficiency (ROIC)", f"={HL('roic')}"),
        ("Value creation (ROIC vs WACC)",
         label_compare(H("roic", last), refs.ref("wacc.value"), 0.01)),
        ("Valuation vs price", f"={Dk('val_label')}"),
        ("Data & model health", f"={refs.ref('chk.verdict')}"),
    ]
    fr = r
    for i, (label, formula) in enumerate(flags):
        base = L1 if i % 2 == 0 else L2
        row = fr + i // 2
        sh.put(row, base, label, role="label")
        sh.put(row, base + 1, formula, role="link", align="c")
        sh.merge(row, base + 1, row, base + 2)
        read_rows.append((row, base + 1))
    r = fr + (len(flags) + 1) // 2 + 1

    # ===== band 5: investment view =======================================
    common.section(sh, r, "Investment View", c1=1, c2=LASTCOL)
    r += 1
    up = Dk("upside")
    roic = H("roic", last)
    wv = refs.ref("wacc.value")
    view = (
        f'=IF(ISNUMBER({up}),IF({up}>{T.VAL_BAND},"The shares look UNDERVALUED on this DCF",'
        f'IF({up}<-{T.VAL_BAND},"The shares look EXPENSIVE on this DCF","The shares look ~FAIRLY VALUED")),'
        f'"No market price entered — see DCF value per share")'
        f'&" ("&TEXT({Dk("value_per_share")},"0.00")&" vs "&'
        f'IF(ISNUMBER({Dk("current_price")}),TEXT({Dk("current_price")},"0.00"),"n/a")&"). "'
        f'&IF(AND(ISNUMBER({roic}),{roic}>{wv}+0.01),"Returns are above the cost of capital (value-creating); ",'
        f'IF(AND(ISNUMBER({roic}),{roic}<{wv}-0.01),"Returns are below the cost of capital; ","Returns ~ cost of capital; "))'
        f'&"see the Conclusion sheet for the full thesis."'
    )
    sh.put(r, 1, view, role="output", align="ltw")
    sh.merge(r, 1, r + 2, LASTCOL)
    sh.row_height(r, 20)
    r += 3
    sh.put(r, 1, "Tip: change the scenario selector on the Assumptions sheet (1–4) to flex the "
                 "whole model; every figure here updates automatically.", role="note")
    sh.merge(r, 1, r, LASTCOL)

    # colour all word-based reads
    for (row, col) in read_rows:
        coord = sh.coord(row, col)
        common.add_label_coloring(sh, f"{coord}:{coord}", coord)
    sh.freeze("A5")
    return sh
