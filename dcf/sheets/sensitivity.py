"""
Sensitivity sheet -- three two-way tables, each cell a live formula.

openpyxl cannot emit native Excel data tables, so every grid cell instead holds
a complete formula that recomputes the implied value per share for its row/column
axis pair. This is fully transparent and recalculates live when inputs change.

  Table 1  WACC × terminal growth        — EXACT (reuses the forecast FCFFs)
  Table 2  WACC × exit EBITDA multiple    — EXACT (reuses the forecast FCFFs)
  Table 3  Start growth × terminal margin — a clearly-labelled simplified
           constant-growth model (the FCFFs themselves move with these levers,
           so a compact closed form is used for the 2-way view).

A 3-colour heat-map (conditional formatting) makes the gradient readable; the
base-case centre cell is boxed.
"""

from __future__ import annotations

from openpyxl.formatting.rule import ColorScaleRule

from ..config import Fmt, Palette
from ..styles import BORDER_BOX
from . import common

LEFT = 2  # left header column for grids


def build(sh, ctx: common.Context):
    refs = ctx.refs
    N = ctx.n_fcst
    last = ctx.n_hist - 1
    R = lambda k, p: refs.ref(f"in.{k}@{p}")    # noqa: E731
    H = lambda k, p: refs.ref(f"h.{k}@{p}")     # noqa: E731
    A = lambda k: refs.ref(f"as.{k}")           # noqa: E731
    F = lambda k, t: refs.ref(f"fc.{k}@{t}")    # noqa: E731
    shares = refs.ref("dcf.shares")
    nd = H("net_debt", last)
    mi = R("minority_equity", last)

    sh.hide_gridlines()
    sh.col_width(1, 26)
    for c in range(2, 9):
        sh.col_width(c, 13)
    r = common.title_block(sh, "SENSITIVITY ANALYSIS",
                           "Implied value per share across key assumptions",
                           last_col=8)
    sh.put(r, 1, "Each cell recomputes the full valuation for its row/column pair. "
                 "Centre cell (boxed) = active base case.", role="note")
    sh.merge(r, 1, r, 8)
    r += 2

    pv_explicit = "+".join(f"{F('fcff', t)}/(1+{{w}})^{t}" for t in range(1, N + 1))

    def perp_cell(w, gg):
        tv = f"{F('fcff', N)}*(1+{gg})/({w}-{gg})"
        eq = f"(({pv_explicit.format(w=w)})+({tv})/(1+{w})^{N})-{nd}-{mi}"
        return f'=IF({w}-{gg}<=0.005,"n/m",IFERROR(({eq})/{shares},"n/m"))'

    def exit_cell(w, mult):
        tv = f"{F('ebitda', N)}*{mult}"
        eq = f"(({pv_explicit.format(w=w)})+({tv})/(1+{w})^{N})-{nd}-{mi}"
        return f'=IFERROR(({eq})/{shares},"n/m")'

    # ---- Table 1: WACC × terminal growth --------------------------------
    r = common.section(sh, r, "Table 1 · WACC (down) × Terminal growth g (across)", c1=1, c2=8)
    r = _grid(sh, r, base_row=refs.ref("wacc.value"), base_col=A("act_tv_growth"),
              row_offsets=[-0.015, -0.0075, 0, 0.0075, 0.015],
              col_offsets=[-0.010, -0.005, 0, 0.005, 0.010],
              row_fmt=Fmt.PCT2, col_fmt=Fmt.PCT, cell_fn=perp_cell,
              corner="Value / share")
    r += 1

    # ---- Table 2: WACC × exit multiple ----------------------------------
    r = common.section(sh, r, "Table 2 · WACC (down) × Exit EBITDA multiple (across)", c1=1, c2=8)
    r = _grid(sh, r, base_row=refs.ref("wacc.value"), base_col=A("exit_multiple"),
              row_offsets=[-0.015, -0.0075, 0, 0.0075, 0.015],
              col_offsets=[-2, -1, 0, 1, 2],
              row_fmt=Fmt.PCT2, col_fmt=Fmt.MULT, cell_fn=exit_cell,
              corner="Value / share")
    sh.put(r, 1, "Exit-multiple TV is a cross-check; the headline uses the perpetuity method.",
           role="note")
    sh.merge(r, 1, r, 8)
    r += 2

    # ---- Table 3: start growth × terminal margin (simplified) -----------
    r = common.section(sh, r, "Table 3 · Start revenue growth (down) × Terminal EBIT margin (across)",
                       c1=1, c2=8)
    tax = A("tax")
    da = A("da_pct_used")
    capex = A("capex_pct_used")
    nwc = A("nwc_pct_used")
    R0 = F("revenue", 0)
    w0 = refs.ref("wacc.value")
    gt = A("act_tv_growth")

    def gm_cell(gs, m):
        # Closed-form constant-growth, constant-margin two-stage value.
        a = f"({m}*(1-{tax})+{da}-{capex})"
        b = f"((1+{gs})*{a}-{nwc}*{gs})"
        x = f"((1+{gs})/(1+{w0}))"
        pvexp = f"({R0}*{b}/(1+{w0}))*(1-{x}^{N})/(1-{x})"
        fcff_n = f"{R0}*{b}*(1+{gs})^{N - 1}"
        tv = f"{fcff_n}*(1+{gt})/({w0}-{gt})"
        eq = f"(({pvexp})+({tv})/(1+{w0})^{N})-{nd}-{mi}"
        return f'=IFERROR(({eq})/{shares},"n/m")'

    r = _grid(sh, r, base_row=A("act_start_growth"), base_col=A("act_target_margin"),
              row_offsets=[-0.03, -0.015, 0, 0.015, 0.03],
              col_offsets=[-0.03, -0.015, 0, 0.015, 0.03],
              row_fmt=Fmt.PCT, col_fmt=Fmt.PCT, cell_fn=gm_cell,
              corner="Value / share")
    sh.put(r, 1, "Simplified constant-growth model for this 2-way view (the staged DCF "
                 "fades growth & margin, so levels differ slightly from the headline).",
           role="note")
    sh.merge(r, 1, r, 8)
    return sh


def _grid(sh, top, *, base_row, base_col, row_offsets, col_offsets, row_fmt, col_fmt,
          cell_fn, corner):
    """Render a 2-way table. Row headers down column LEFT, col headers across the top."""
    nr, nc = len(row_offsets), len(col_offsets)
    hdr_row = top
    # corner label
    sh.put(hdr_row, 1, corner, role="subheader")
    sh.put(hdr_row, LEFT, "", role="subheader")
    # column headers
    for j, off in enumerate(col_offsets):
        sign = "+" if off >= 0 else ""
        formula = f"={base_col}{sign}{off}"
        sh.put(hdr_row, LEFT + 1 + j, formula, role="colhdr_r", fmt=col_fmt)
    # rows
    first_data_row = hdr_row + 1
    for i, roff in enumerate(row_offsets):
        rr = first_data_row + i
        sign = "+" if roff >= 0 else ""
        sh.put(rr, LEFT, f"={base_row}{sign}{roff}", role="colhdr_r", fmt=row_fmt)
        for j in range(nc):
            cc = LEFT + 1 + j
            w_ref = sh.local(rr, LEFT)          # this row's header cell
            c_ref = sh.local(hdr_row, cc)        # this column's header cell
            cell = sh.put(rr, cc, cell_fn(w_ref, c_ref), role="calc", fmt=Fmt.PER_SHARE)
            # box the base-case centre
            if roff == 0 and col_offsets[j] == 0:
                cell.border = BORDER_BOX
    # heat-map across the data block
    data_range = f"{sh.coord(first_data_row, LEFT + 1)}:{sh.coord(first_data_row + nr - 1, LEFT + nc)}"
    sh.ws.conditional_formatting.add(
        data_range,
        ColorScaleRule(start_type="min", start_color=Palette.BAD_FILL,
                       mid_type="percentile", mid_value=50, mid_color=Palette.WARN_FILL,
                       end_type="max", end_color=Palette.GOOD_FILL),
    )
    return first_data_row + nr + 1
