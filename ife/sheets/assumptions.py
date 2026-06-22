"""
Forecast Assumptions (the DRIVERS).

One input per forecast line -- nothing more. Each row is a single driver; each
cell is a plain blue input you can edit per year (pre-filled with a base case).
There is no scenario selector, no method engine, no resolved-driver layer: the
Forecast sheet reads these cells directly, so the assumption -> output link is a
single hop you can always see. The "Drives" column states, in words, the exact
formula each driver feeds.

Columns are the forecast years (= LastActual + 1, +2, ...), so if you add a year
of actuals the whole grid relabels and the forecast shifts forward automatically.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..common import FIRST_COL, FY_FMT
from ..config import DRIVERS

FMT = {"pct": Fmt.PCT, "money": Fmt.MONEY}


def build(sh, ctx):
    N = ctx.horizon
    drivers = ctx.data.get("drivers", {})
    last = FIRST_COL + N - 1
    note_col = last + 1

    common.title_block(sh, "FORECAST ASSUMPTIONS  (DRIVERS)",
                       "One editable input per line -- the Forecast sheet reads these cells directly",
                       last_col=note_col)
    common.nav_bar(sh, 5)
    sh.put(7, 1, common.units_note(ctx), role="note")
    sh.merge(7, 1, 7, note_col)

    common.section(sh, 9, "Forecast Drivers", c1=1, c2=note_col)
    hdr = 10
    sh.put(hdr, 1, "Driver", role="colhdr")
    for t in range(1, N + 1):
        col = FIRST_COL + t - 1
        f = "=LastActual+1" if t == 1 else f"={sh.local(hdr, col - 1)}+1"
        sh.put(hdr, col, f, role="fcst_hdr", fmt=FY_FMT)
    sh.put(hdr, note_col, "Drives  (what this assumption feeds)", role="colhdr")
    r = hdr + 1

    for key, label, kind, drives in DRIVERS:
        sh.put(r, 1, label, role="label_b")
        base = drivers.get(key)
        for t in range(1, N + 1):
            sh.put(r, FIRST_COL + t - 1, base, role="input", fmt=FMT[kind], key=f"a.{key}@{t}")
        sh.put(r, note_col, drives, role="note_l")
        r += 1

    r += 1
    sh.put(r, 1, "How to use: edit any cell. Each driver maps to exactly one forecast line "
                 "(see the Drives column and the Methodology sheet). To change a single year, "
                 "just overwrite that year's cell.", role="note")
    sh.merge(r, 1, r, note_col)

    sh.freeze(f"B{hdr + 1}")
    sh.col_width(1, 34)
    for t in range(1, N + 1):
        sh.col_width(FIRST_COL + t - 1, 10)
    sh.col_width(note_col, 52)
    return sh
