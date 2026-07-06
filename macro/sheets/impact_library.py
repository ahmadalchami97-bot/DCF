"""S04 Impact Library -- the reference brain: how each indicator usually moves markets."""

from __future__ import annotations

from .. import common
from ..common import define_name
from ..config import LIB

LAST = LIB.LAST
POL = "+0;-0;0"


def build(sh, ctx):
    inds = ctx.data["indicators"]
    common.title_block(sh, "INDICATOR IMPACT LIBRARY",
                       "How each macro indicator usually affects markets (the reference the engines look up)",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    sh.merge(6, 1, 6, LAST)
    sh.put(6, 1, "One row per indicator. The Surprise Engine and Fed Tracker look up the polarity, importance and "
                 "scale columns from here. Edit the text and numbers to fit your own playbook.", role="note_l")

    # header
    hdr = LIB.HDR
    cols = [(LIB.INDIC, "Indicator"), (LIB.MEAS, "What it measures"), (LIB.WHY, "Why it matters"),
            (LIB.HIGH, "Higher-than-expected read"), (LIB.LOW, "Lower-than-expected read"),
            (LIB.CAT, "Category"), (LIB.FED, "Fed impact"), (LIB.USD, "USD"), (LIB.UYLD, "UST yld"),
            (LIB.UPX, "UST px"), (LIB.EQ, "Equities"), (LIB.GOLD, "Gold"), (LIB.OIL, "Oil"),
            (LIB.GCC, "GCC"), (LIB.PINF, "Pol.Infl"), (LIB.PGRO, "Pol.Grow"), (LIB.IMP, "Imp"),
            (LIB.SCALE, "Scale"), (LIB.EXC, "Exceptions / context")]
    for c, tx in cols:
        sh.put(hdr, c, tx, role="colhdr_l" if c in (LIB.INDIC, LIB.MEAS, LIB.WHY, LIB.HIGH, LIB.LOW, LIB.EXC)
               else "colhdr", align="lw")
    sh.row_height(hdr, 28)

    r = LIB.FIRST
    for d in inds:
        sh.put(r, LIB.INDIC, d["name"], role="label_b")
        sh.put(r, LIB.MEAS, d["meas"], role="note_l", align="lw")
        sh.put(r, LIB.WHY, d["why"], role="note_l", align="lw")
        sh.put(r, LIB.HIGH, d["high"], role="note_l", align="lw")
        sh.put(r, LIB.LOW, d["low"], role="note_l", align="lw")
        sh.put(r, LIB.CAT, d["cat"], role="formula", align="c")
        sh.put(r, LIB.FED, d["fed"], role="note_l", align="lw")
        for col, key in ((LIB.USD, "usd"), (LIB.UYLD, "uyld"), (LIB.UPX, "upx"), (LIB.EQ, "eq"),
                         (LIB.GOLD, "gold"), (LIB.OIL, "oil"), (LIB.GCC, "gcc")):
            sh.put(r, col, d[key], role="formula", align="c")
        sh.put(r, LIB.PINF, d["pinf"], role="formula", fmt=POL, align="c")
        sh.put(r, LIB.PGRO, d["pgro"], role="formula", fmt=POL, align="c")
        sh.put(r, LIB.IMP, d["imp"], role="formula", align="c")
        sh.put(r, LIB.SCALE, d["scale"], role="formula", align="c")
        sh.put(r, LIB.EXC, d["exc"], role="note_l", align="lw")
        sh.row_height(r, 42)
        r += 1
    last = r - 1

    # named ranges the Data Tracker / Surprise Engine / Fed sheet look up
    define_name(sh, "Lib_Name", LIB.FIRST, LIB.INDIC, last, LIB.INDIC)
    define_name(sh, "Lib_Cat", LIB.FIRST, LIB.CAT, last, LIB.CAT)
    define_name(sh, "Lib_Interp_Higher", LIB.FIRST, LIB.HIGH, last, LIB.HIGH)
    define_name(sh, "Lib_Interp_Lower", LIB.FIRST, LIB.LOW, last, LIB.LOW)
    define_name(sh, "Lib_PolInfl", LIB.FIRST, LIB.PINF, last, LIB.PINF)
    define_name(sh, "Lib_PolGrow", LIB.FIRST, LIB.PGRO, last, LIB.PGRO)
    define_name(sh, "Lib_Importance", LIB.FIRST, LIB.IMP, last, LIB.IMP)
    define_name(sh, "Lib_Scale", LIB.FIRST, LIB.SCALE, last, LIB.SCALE)

    sh.freeze(f"C{LIB.FIRST}")
    widths = {LIB.INDIC: 20, LIB.MEAS: 26, LIB.WHY: 26, LIB.HIGH: 30, LIB.LOW: 30, LIB.CAT: 11,
              LIB.FED: 20, LIB.USD: 7, LIB.UYLD: 7, LIB.UPX: 7, LIB.EQ: 9, LIB.GOLD: 7, LIB.OIL: 7,
              LIB.GCC: 12, LIB.PINF: 8, LIB.PGRO: 8, LIB.IMP: 6, LIB.SCALE: 7, LIB.EXC: 34}
    for c, w in widths.items():
        sh.col_width(c, w)
    return sh
