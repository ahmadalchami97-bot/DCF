"""
DCF sheet -- the core valuation.

Discounts the unlevered free cash flows at WACC, adds a terminal value, and
bridges enterprise value to equity value and an implied per-share value. Every
step is explicit:

  PV(FCFF_t) = FCFF_t / (1 + WACC)^t
  TV_N (perpetuity) = FCFF_N x (1 + g) / (WACC - g)        [primary]
  TV_N (exit)       = EBITDA_N x exit multiple             [cross-check only]
  EV = Σ PV(FCFF) + PV(TV);   Equity = EV - net debt - minority

The (WACC - g) denominator is guarded; the Assumptions sheet already clamps g to
WACC-1%, but IFERROR keeps the model alive even if a user overrides it badly.
"""

from __future__ import annotations

from ..config import Fmt, Thresholds as T
from ..utils import label_valuation, ratio
from . import common

L = 1
YR0 = 2  # first forecast-year column


def build(sh, ctx: common.Context):
    refs = ctx.refs
    N = ctx.n_fcst
    last = ctx.n_hist - 1
    sum_col = YR0 + N
    note_col = sum_col + 1
    R = lambda k, p: refs.ref(f"in.{k}@{p}")    # noqa: E731
    H = lambda k, p: refs.ref(f"h.{k}@{p}")     # noqa: E731
    A = lambda k: refs.ref(f"as.{k}")           # noqa: E731
    F = lambda k, t: refs.ref(f"fc.{k}@{t}")    # noqa: E731
    DREF = lambda k: refs.ref(f"dcf.{k}")       # noqa: E731

    wacc = refs.ref("wacc.value")
    g = A("act_tv_growth")

    sh.hide_gridlines()
    sh.col_width(L, 38)
    for i in range(N + 1):
        sh.col_width(YR0 + i, 13)
    sh.col_width(note_col, 50)
    r = common.title_block(sh, "DCF VALUATION",
                           "Discounted unlevered free cash flow — every step shown",
                           last_col=note_col)
    sh.put(r, L, "Active scenario:", role="label")
    sh.put(r, YR0, f"={refs.ref('as.scenario_name')}", role="link", align="l")
    sh.put(r, note_col, common.money_units_note(ctx), role="note")
    r += 2

    # ---- 1. discounting --------------------------------------------------
    r = common.section(sh, r, "1 · Present Value of Explicit Free Cash Flows", c1=1, c2=note_col)
    sh.put(r, L, "Forecast year", role="colhdr")
    for t in range(1, N + 1):
        sh.put(r, YR0 + t - 1, ctx.fcst_labels[t - 1], role="colhdr_r")
    sh.put(r, sum_col, "Total", role="colhdr_r")
    r += 1

    sh.put(r, L, "Unlevered FCF (FCFF)", role="label")
    for t in range(1, N + 1):
        sh.put(r, YR0 + t - 1, f"={F('fcff', t)}", role="link", fmt=Fmt.MONEY)
    r += 1

    sh.put(r, L, "Discount period (years)", role="label")
    for t in range(1, N + 1):
        sh.put(r, YR0 + t - 1, t, role="calc", fmt=Fmt.FLOAT1, key=f"dcf.period@{t}")
    sh.put(r, note_col, "End-of-year discounting convention.", role="note")
    r += 1

    sh.put(r, L, "Discount factor = 1/(1+WACC)^t", role="label")
    for t in range(1, N + 1):
        sh.put(r, YR0 + t - 1, f"=1/(1+{wacc})^{DREF(f'period@{t}')}",
               role="calc", fmt=Fmt.FLOAT2, key=f"dcf.df@{t}")
    r += 1

    sh.put(r, L, "PV of FCFF", role="label_b")
    for t in range(1, N + 1):
        sh.put(r, YR0 + t - 1, f"={F('fcff', t)}*{DREF(f'df@{t}')}",
               role="calc", fmt=Fmt.MONEY, key=f"dcf.pv_fcff@{t}", bold=True)
    pv_range = f"{sh.local(r, YR0)}:{sh.local(r, YR0 + N - 1)}"
    sh.put(r, sum_col, f"=SUM({pv_range})", role="output", fmt=Fmt.MONEY,
           key="dcf.sum_pv_fcff", bold=True)
    sh.put(r, note_col, "Sum of discounted explicit-period cash flows.", role="note")
    r += 2

    # ---- 2. terminal value ----------------------------------------------
    r = common.section(sh, r, "2 · Terminal Value", c1=1, c2=note_col)

    def kv(row, label, formula, key, fmt=Fmt.MONEY, role="calc", note="", bold=False):
        sh.put(row, L, label, role="label_b" if bold else "label")
        sh.put(row, YR0, formula, role=role, fmt=fmt, key=f"dcf.{key}", bold=bold or None)
        if note:
            sh.put(row, note_col, note, role="note")
        return row + 1

    sh.put(r, L, "— Method A: Perpetuity growth (Gordon) —", role="subheader")
    sh.merge(r, L, r, note_col)
    r += 1
    r = kv(r, "Terminal-year FCFF (year N)", f"={F('fcff', N)}", "term_fcff",
           note="Last explicit-year unlevered cash flow.")
    r = kv(r, "Terminal growth (g)", f"={g}", "term_g", fmt=Fmt.PCT,
           note="Perpetuity growth, from active assumptions.")
    r = kv(r, "WACC", f"={wacc}", "wacc", fmt=Fmt.PCT, note="From the WACC sheet.")
    r = kv(r, "Terminal value at year N = FCFF×(1+g)/(WACC−g)",
           f'=IFERROR({DREF("term_fcff")}*(1+{DREF("term_g")})/({DREF("wacc")}-{DREF("term_g")}),"n/m")',
           "tv_perp", role="output", bold=True,
           note="Gordon growth perpetuity, valued as of year N.")
    r = kv(r, "PV of terminal value", f"={DREF('tv_perp')}*{DREF(f'df@{N}')}", "pv_tv",
           role="output", bold=True, note="Terminal value discounted to today.")
    r += 1
    sh.put(r, L, "— Method B: Exit multiple (cross-check only) —", role="subheader")
    sh.merge(r, L, r, note_col)
    r += 1
    r = kv(r, "Terminal-year EBITDA", f"={F('ebitda', N)}", "term_ebitda",
           note="Year-N EBITDA from the forecast.")
    r = kv(r, "Exit EBITDA multiple", f"={A('exit_multiple')}", "exit_mult", fmt=Fmt.MULT,
           note="Generic assumption; not used in the headline value.")
    r = kv(r, "TV (exit multiple) at year N", f"={DREF('term_ebitda')}*{DREF('exit_mult')}",
           "tv_exit", note="Sanity check against the perpetuity TV.")
    r = kv(r, "PV of TV (exit multiple)", f"={DREF('tv_exit')}*{DREF(f'df@{N}')}", "pv_tv_exit",
           note="For comparison with the perpetuity PV of TV.")
    r += 2

    # ---- 3. enterprise & equity value -----------------------------------
    r = common.section(sh, r, "3 · Enterprise Value → Equity Value → Per Share", c1=1, c2=note_col)
    r = kv(r, "Σ PV of explicit FCFF", f"={DREF('sum_pv_fcff')}", "ev_explicit",
           note="From section 1.")
    r = kv(r, "(+) PV of terminal value", f"={DREF('pv_tv')}", "ev_terminal",
           note="Perpetuity method (section 2A).")
    r = kv(r, "Enterprise value (EV)", f"={DREF('ev_explicit')}+{DREF('ev_terminal')}", "ev",
           role="output", bold=True, note="Value of the operating business to all capital providers.")
    r = kv(r, "(−) Net debt", f"=-{H('net_debt', last)}", "net_debt",
           note="Total debt less cash & investments (latest balance sheet).")
    r = kv(r, "(−) Minority interest", f"=-{R('minority_equity', last)}", "minority",
           note="Equity not attributable to shareholders.")
    r = kv(r, "Equity value", f"={DREF('ev')}+{DREF('net_debt')}+{DREF('minority')}", "equity_value",
           role="output", bold=True, note="Intrinsic value attributable to shareholders.")
    shares = (f"=IF(ISNUMBER({refs.ref('mkt.mkt_shares_out')}),{refs.ref('mkt.mkt_shares_out')},"
              f"{R('shares_diluted', last)})")
    r = kv(r, "Shares outstanding", shares, "shares", fmt=Fmt.INT,
           note="Current shares; falls back to diluted weighted-average.")
    r = kv(r, "Implied value per share", ratio(DREF("equity_value"), DREF("shares")),
           "value_per_share", fmt=Fmt.PER_SHARE, role="result", bold=True,
           note="Headline DCF output.")
    r += 1

    # ---- 4. cross-checks & valuation read -------------------------------
    r = common.section(sh, r, "4 · Cross-Checks & Valuation Read", c1=1, c2=note_col)
    r = kv(r, "Current share price", f"={refs.ref('mkt.mkt_share_price')}", "current_price",
           fmt=Fmt.PER_SHARE, role="link", note="Market reference input (blank if unknown).")
    r = kv(r, "Upside / (downside) to DCF value",
           f'=IFERROR({DREF("value_per_share")}/{DREF("current_price")}-1,"n/a")',
           "upside", fmt=Fmt.PCT, role="output", bold=True,
           note="How far the price sits from intrinsic value.")
    lab = label_valuation(DREF("value_per_share"), DREF("current_price"), T.VAL_BAND)
    sh.put(r, L, "Valuation read", role="label_b")
    sh.put(r, YR0, lab, role="link", align="l", key="dcf.val_label")
    sh.merge(r, YR0, r, YR0 + 2)
    common.add_label_coloring(sh, f"{sh.coord(r, YR0)}:{sh.coord(r, YR0)}", sh.coord(r, YR0))
    sh.put(r, note_col, f"±{int(T.VAL_BAND*100)}% band around the price defines 'fairly valued'.",
           role="note")
    r += 2

    r = kv(r, "Terminal value as % of EV", ratio(DREF("ev_terminal"), DREF("ev")),
           "tv_share", fmt=Fmt.PCT, note="High share = value rests heavily on the terminal year.")
    sh.put(r - 1, note_col,
           f'=IF({DREF("tv_share")}>{T.TV_SHARE_WARN},"TV-heavy — scrutinise terminal assumptions",'
           f'"Reasonable split between explicit and terminal value")', role="note")
    common.add_label_coloring(sh, f"{sh.coord(r-1, note_col)}:{sh.coord(r-1, note_col)}",
                              sh.coord(r - 1, note_col))
    r = kv(r, "Implied exit multiple (from perpetuity TV)",
           ratio(DREF("tv_perp"), DREF("term_ebitda")), "implied_exit", fmt=Fmt.MULT,
           note="Cross-check: compare with the assumed exit multiple above.")
    r = kv(r, "EV / next-year EBITDA", ratio(DREF("ev"), F("ebitda", 1)), "ev_ebitda",
           fmt=Fmt.MULT, note="Forward valuation multiple implied by the DCF.")
    return sh
