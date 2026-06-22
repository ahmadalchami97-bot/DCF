"""
Sensitivity Analysis (Sheet 9).

Two-way sensitivity grids for the terminal (year-N) outputs. openpyxl cannot emit
native Excel data tables, so each cell is a live formula that recomputes the
output for its row/column pair using a transparent constant-growth terminal model
(clearly labelled). A heat-map shades each grid.
"""

from __future__ import annotations

from openpyxl.formatting.rule import ColorScaleRule

from dcf.config import Fmt
from .. import common
from ..config import Palette

LEFT = 2
M, PCT, MULT = Fmt.MONEY, Fmt.PCT, Fmt.MULT2


def build(sh, ctx):
    refs = ctx.refs
    N = ctx.fcst
    li = ctx.last_hist
    H = lambda k: refs.ref(f"h.{k}@{li}")        # noqa: E731
    AB = lambda k: refs.ref(f"a.{k}.base")       # noqa: E731

    R0 = H("revenue")
    da, capexb, taxb, mb, intr, debt = (AB("da_pct"), AB("capex_pct"), AB("tax_rate"),
                                        AB("ebitda_margin"), AB("int_rate"), H("total_debt"))

    def revN(g):
        return f"{R0}*(1+{g})^{N}"

    def f_ebitda(g, m):
        return f"=IFERROR({revN(g)}*{m},\"\")"

    def f_ni_gm(g, m):
        return f"=IFERROR(({revN(g)}*{m}-{revN(g)}*{da}-{intr}*{debt})*(1-{taxb}),\"\")"

    def f_fcf_gm(g, m):
        return f"=IFERROR(({revN(g)}*{m}-{revN(g)}*{da}-{intr}*{debt})*(1-{taxb})+{revN(g)}*{da}-{revN(g)}*{capexb},\"\")"

    def f_ni_gt(g, tax):
        return f"=IFERROR(({revN(g)}*{mb}-{revN(g)}*{da}-{intr}*{debt})*(1-{tax}),\"\")"

    def f_fcf_gc(g, capex):
        return f"=IFERROR(({revN(g)}*{mb}-{revN(g)}*{da}-{intr}*{debt})*(1-{taxb})+{revN(g)}*{da}-{revN(g)}*{capex},\"\")"

    common.title_block(sh, "SENSITIVITY ANALYSIS",
                       "Terminal-year outputs across key assumptions (live formula grids)", last_col=8)
    common.nav_bar(sh, 5)
    r = 7
    sh.put(r, 1, "Each cell recomputes the terminal-year output with a transparent "
                 "constant-growth model. Centre = base assumptions.", role="note")
    sh.merge(r, 1, r, 8)
    r += 2
    sh.col_width(1, 22)
    for c in range(2, 9):
        sh.col_width(c, 12)

    gO = [-0.02, -0.01, 0, 0.01, 0.02]
    mO = [-0.02, -0.01, 0, 0.01, 0.02]
    tO = [-0.04, -0.02, 0, 0.02, 0.04]
    cO = [-0.015, -0.0075, 0, 0.0075, 0.015]
    g_base = AB("rev_growth")

    r = common.section(sh, r, "Revenue growth (down) × EBITDA margin (across) → terminal EBITDA", c1=1, c2=8)
    r = _grid(sh, r, g_base, mb, gO, mO, PCT, PCT, f_ebitda, "EBITDA")
    r += 1
    r = common.section(sh, r, "Revenue growth × EBITDA margin → terminal Net income", c1=1, c2=8)
    r = _grid(sh, r, g_base, mb, gO, mO, PCT, PCT, f_ni_gm, "Net income")
    r += 1
    r = common.section(sh, r, "Revenue growth × EBITDA margin → terminal Free cash flow", c1=1, c2=8)
    r = _grid(sh, r, g_base, mb, gO, mO, PCT, PCT, f_fcf_gm, "FCF")
    r += 1
    r = common.section(sh, r, "Revenue growth × Tax rate → terminal Net income", c1=1, c2=8)
    r = _grid(sh, r, g_base, taxb, gO, tO, PCT, PCT, f_ni_gt, "Net income")
    r += 1
    r = common.section(sh, r, "Revenue growth × Capex % → terminal Free cash flow", c1=1, c2=8)
    r = _grid(sh, r, g_base, capexb, gO, cO, PCT, PCT, f_fcf_gc, "FCF")
    r += 1
    sh.put(r, 1, "Note: a simplified constant-growth terminal model is used for the grids; "
                 "the integrated Forecast sheet is the full model.", role="note")
    sh.merge(r, 1, r, 8)
    return sh


def _grid(sh, top, base_row, base_col, row_off, col_off, rfmt, cfmt, cell_fn, corner):
    sh.put(top, 1, corner, role="colhdr")
    for j, off in enumerate(col_off):
        sign = "+" if off >= 0 else ""
        sh.put(top, LEFT + j, f"={base_col}{sign}{off}", role="colhdr_r", fmt=cfmt)
    first = top + 1
    for i, ro in enumerate(row_off):
        rr = first + i
        sign = "+" if ro >= 0 else ""
        sh.put(rr, 1, f"={base_row}{sign}{ro}", role="colhdr_r", fmt=rfmt)
        for j in range(len(col_off)):
            cc = LEFT + j
            cell = sh.put(rr, cc, cell_fn(sh.local(rr, 1), sh.local(top, cc)), role="formula", fmt=Fmt.MONEY)
            if ro == 0 and col_off[j] == 0:
                from ..style import B_BOX
                cell.border = B_BOX
    rng = f"{sh.coord(first, LEFT)}:{sh.coord(first + len(row_off) - 1, LEFT + len(col_off) - 1)}"
    sh.ws.conditional_formatting.add(rng, ColorScaleRule(
        start_type="min", start_color=Palette.BAD_FILL, mid_type="percentile", mid_value=50,
        mid_color="FFF1C2", end_type="max", end_color=Palette.GOOD_FILL))
    return first + len(row_off)
