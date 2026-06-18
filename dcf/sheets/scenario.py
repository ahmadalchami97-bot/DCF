"""
Scenario sheet -- Base / Bull / Bear / Downside, valued side by side.

Each scenario gets its own full forecast built with the *same staged fade* as the
main Forecast/DCF (so the Base column reproduces the headline value to the cent),
driven by that scenario's growth, margin and terminal-growth assumptions. The
revenue and FCFF paths are shown explicitly, then bridged to an implied value per
share and an upside/downside vs the current price.
"""

from __future__ import annotations

from ..config import Fmt, SCENARIOS, Thresholds as T
from ..utils import label_valuation
from . import common

LBL = 1
COL0 = 2  # first scenario column (Base)


def build(sh, ctx: common.Context):
    refs = ctx.refs
    N = ctx.n_fcst
    last = ctx.n_hist - 1
    R = lambda k, p: refs.ref(f"in.{k}@{p}")    # noqa: E731
    H = lambda k, p: refs.ref(f"h.{k}@{p}")     # noqa: E731
    A = lambda k: refs.ref(f"as.{k}")           # noqa: E731
    F = lambda k, t: refs.ref(f"fc.{k}@{t}")    # noqa: E731

    tax, da, capex, nwc = A("tax"), A("da_pct_used"), A("capex_pct_used"), A("nwc_pct_used")
    wacc = refs.ref("wacc.value")
    nd, mi = H("net_debt", last), R("minority_equity", last)
    shares = refs.ref("dcf.shares")
    price = refs.ref("mkt.mkt_share_price")
    R0 = F("revenue", 0)
    m0 = F("ebit_margin", 0)
    scen_col = {s: COL0 + i for i, s in enumerate(SCENARIOS)}
    last_col = COL0 + len(SCENARIOS) - 1

    sh.hide_gridlines()
    sh.col_width(LBL, 34)
    for c in scen_col.values():
        sh.col_width(c, 15)
    sh.col_width(last_col + 1, 40)
    r = common.title_block(sh, "SCENARIO ANALYSIS",
                           "Four full DCF runs — base, bull, bear and downside stress",
                           last_col=last_col + 1)
    r += 1

    def scen_header(row):
        sh.put(row, LBL, "", role="colhdr")
        for s, c in scen_col.items():
            sh.put(row, c, s, role="colhdr_r")
        return row + 1

    # ---- per-scenario assumptions ---------------------------------------
    r = common.section(sh, r, "Scenario Assumptions", c1=1, c2=last_col + 1)
    r = scen_header(r)
    for label, key, fmt in (("Year-1 revenue growth", "start_growth", Fmt.PCT),
                            ("Terminal growth (g)", "tv_growth", Fmt.PCT),
                            ("Terminal EBIT margin", "target_margin", Fmt.PCT)):
        sh.put(r, LBL, label, role="label")
        for s, c in scen_col.items():
            sh.put(r, c, f"={A(f'{key}.{s}')}", role="link", fmt=fmt)
        r += 1
    r += 1

    # ---- revenue path ----------------------------------------------------
    r = common.section(sh, r, "Revenue by Forecast Year", c1=1, c2=last_col + 1)
    r = scen_header(r)
    for t in range(1, N + 1):
        sh.put(r, LBL, ctx.fcst_labels[t - 1], role="label")
        fracg = 0.0 if N == 1 else (t - 1) / (N - 1)
        for s, c in scen_col.items():
            start = A(f"start_growth.{s}")
            termg = A(f"tv_growth.{s}")
            prev = refs.ref(f"sc.rev.{s}@{t-1}") if t > 1 else R0
            growth = f"({start}+({termg}-{start})*{fracg:.6f})"
            sh.put(r, c, f"={prev}*(1+{growth})", role="calc", fmt=Fmt.MONEY,
                   key=f"sc.rev.{s}@{t}")
        r += 1
    r += 1

    # ---- FCFF path -------------------------------------------------------
    r = common.section(sh, r, "Unlevered Free Cash Flow by Year", c1=1, c2=last_col + 1)
    r = scen_header(r)
    for t in range(1, N + 1):
        sh.put(r, LBL, ctx.fcst_labels[t - 1], role="label")
        fracm = 0.0 if N == 0 else t / N
        for s, c in scen_col.items():
            tgt = A(f"target_margin.{s}")
            rev = refs.ref(f"sc.rev.{s}@{t}")
            prev = refs.ref(f"sc.rev.{s}@{t-1}") if t > 1 else R0
            m = f"({m0}+({tgt}-{m0})*{fracm:.6f})"
            fcff = (f"={rev}*{m}*(1-{tax})+{rev}*{da}-{rev}*{capex}"
                    f"-{nwc}*({rev}-{prev})")
            sh.put(r, c, fcff, role="calc", fmt=Fmt.MONEY, key=f"sc.fcff.{s}@{t}")
        r += 1
    r += 1

    # ---- valuation bridge ------------------------------------------------
    r = common.section(sh, r, "Valuation by Scenario", c1=1, c2=last_col + 1)
    r = scen_header(r)

    def vrow(row, label, fn, fmt, role="calc", bold=False, regkey=None):
        sh.put(row, LBL, label, role="label_b" if bold else "label")
        for s, c in scen_col.items():
            key = f"sc.{s}.{regkey}" if regkey else None
            sh.put(row, c, fn(s), role=role, fmt=fmt, key=key, bold=bold or None)
        return row + 1

    def pv_explicit(s):
        return "+".join(f"{refs.ref(f'sc.fcff.{s}@{t}')}/(1+{wacc})^{t}" for t in range(1, N + 1))

    r = vrow(r, "Σ PV of explicit FCFF", lambda s: f"=({pv_explicit(s)})", Fmt.MONEY, regkey="pv_exp")
    r = vrow(r, "Terminal value (perpetuity)",
             lambda s: f'=IFERROR({refs.ref(f"sc.fcff.{s}@{N}")}*(1+{A(f"tv_growth.{s}")})'
                       f'/({wacc}-{A(f"tv_growth.{s}")}),"n/m")', Fmt.MONEY, regkey="tv")
    r = vrow(r, "PV of terminal value",
             lambda s: f"={refs.ref(f'sc.{s}.tv')}/(1+{wacc})^{N}", Fmt.MONEY, regkey="pv_tv")
    r = vrow(r, "Enterprise value",
             lambda s: f"={refs.ref(f'sc.{s}.pv_exp')}+{refs.ref(f'sc.{s}.pv_tv')}",
             Fmt.MONEY, role="output", bold=True, regkey="ev")
    r = vrow(r, "Equity value",
             lambda s: f"={refs.ref(f'sc.{s}.ev')}-{nd}-{mi}", Fmt.MONEY, regkey="equity")
    r = vrow(r, "Implied value per share",
             lambda s: f'=IFERROR({refs.ref(f"sc.{s}.equity")}/{shares},"n/m")',
             Fmt.PER_SHARE, role="result", bold=True, regkey="per_share")
    r = vrow(r, "Upside / (downside) vs price",
             lambda s: f'=IFERROR({refs.ref(f"sc.{s}.per_share")}/{price}-1,"n/a")',
             Fmt.PCT, role="output", regkey="upside")
    label_row = r
    r = vrow(r, "Valuation read",
             lambda s: label_valuation(refs.ref(f"sc.{s}.per_share"), price, T.VAL_BAND),
             Fmt.TEXT, role="link", regkey="label")
    common.add_label_coloring(sh, f"{sh.coord(label_row, COL0)}:{sh.coord(label_row, last_col)}",
                              sh.coord(label_row, COL0))
    r += 1

    sh.put(r, LBL, "Current share price (reference):", role="label")
    sh.put(r, COL0, f"={price}", role="link", fmt=Fmt.PER_SHARE)
    r += 2
    sh.put(r, LBL, "Base reproduces the headline DCF; Downside is a stress case "
                   "(low growth, compressed margins).", role="note")
    sh.merge(r, LBL, r, last_col + 1)
    return sh
