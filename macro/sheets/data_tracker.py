"""S02 Data Tracker -- the structured log of macro releases (the main input sheet)."""

from __future__ import annotations

from .. import common
from ..common import dropdown, dropdown_ref
from ..config import (FIRST_ROW, HDR_ROW, LIST_COUNTRY, LIST_FREQUENCY, NROWS, TRK,
                      F_DATE, F_NUM2, F_SIGNED)

LAST = TRK.LAST


def build(sh, ctx):
    rel = ctx.data["releases"]
    common.title_block(sh, "MACRO DATA TRACKER", "Log every release here - this and the Fed sheet are your inputs",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    sh.merge(6, 1, 6, LAST)
    sh.put(6, 1, "Type releases in the yellow cells. Surprise, Hot/Cold and Importance fill in automatically. Pick the "
                 "indicator from the dropdown so it matches the Impact Library. Blank rows are yours to fill.",
           role="note_l")

    hdr = HDR_ROW
    heads = [(TRK.DATE, "Date"), (TRK.COUNTRY, "Country"), (TRK.INDIC, "Indicator"), (TRK.ACTUAL, "Actual"),
             (TRK.FCST, "Forecast"), (TRK.PREV, "Previous"), (TRK.UNIT, "Unit"), (TRK.FREQ, "Frequency"),
             (TRK.SURP, "Surprise"), (TRK.HOT, "Hot/Cold"), (TRK.IMP, "Imp"), (TRK.SRC, "Source"),
             (TRK.NOTES, "Notes")]
    for c, tx in heads:
        sh.put(hdr, c, tx, role="colhdr_l" if c in (TRK.INDIC, TRK.SRC, TRK.NOTES) else "colhdr")
    sh.row_height(hdr, 16)

    D, E, F = "D", "E", "F"  # indicator, actual, forecast column letters
    for i in range(NROWS):
        r = FIRST_ROW + i
        sample = rel[i] if i < len(rel) else None
        # inputs
        sh.put(r, TRK.DATE, sample[0] if sample else None, role="input_c", fmt=F_DATE)
        sh.put(r, TRK.COUNTRY, sample[1] if sample else None, role="input_c")
        sh.put(r, TRK.INDIC, sample[2] if sample else None, role="input_l")
        sh.put(r, TRK.ACTUAL, sample[3] if sample else None, role="input", fmt=F_NUM2)
        sh.put(r, TRK.FCST, sample[4] if sample else None, role="input", fmt=F_NUM2)
        sh.put(r, TRK.PREV, sample[5] if sample else None, role="input", fmt=F_NUM2)
        indic = sample[2] if sample else ""
        freq = ("Weekly" if "claims" in indic.lower() else "Quarterly" if "GDP" in indic
                else "Monthly") if sample else None
        sh.put(r, TRK.UNIT, sample[6] if sample else None, role="input_c")
        sh.put(r, TRK.FREQ, freq, role="input_c")
        sh.put(r, TRK.SRC, sample[7] if sample else None, role="input_l")
        sh.put(r, TRK.NOTES, sample[8] if sample else None, role="input_l")
        # derived
        sh.put(r, TRK.SURP, f'=IF(${D}{r}="","",${E}{r}-${F}{r})', role="formula", fmt=F_SIGNED)
        sh.put(r, TRK.HOT,
               f'=IF(${D}{r}="","",IF(ABS(IFERROR((${E}{r}-${F}{r})/INDEX(Lib_Scale,MATCH(${D}{r},Lib_Name,0)),0))'
               f'<0.5,"Neutral",IF(${E}{r}>${F}{r},"Hot","Cold")))', role="formula", align="c")
        sh.put(r, TRK.IMP,
               f'=IF(${D}{r}="","",IFERROR(INDEX(Lib_Importance,MATCH(${D}{r},Lib_Name,0)),""))',
               role="formula", align="c")
        # dropdowns
        dropdown(sh, r, TRK.COUNTRY, LIST_COUNTRY)
        dropdown_ref(sh, r, TRK.INDIC, "Lib_Name")
        dropdown(sh, r, TRK.FREQ, LIST_FREQUENCY)

    last = FIRST_ROW + NROWS - 1
    common.word_cf(sh, f"K{FIRST_ROW}:K{last}", common.CF_HOT)

    sh.freeze("E9")
    widths = {TRK.DATE: 12, TRK.COUNTRY: 9, TRK.INDIC: 22, TRK.ACTUAL: 9, TRK.FCST: 9, TRK.PREV: 9,
              TRK.UNIT: 9, TRK.FREQ: 11, TRK.SURP: 10, TRK.HOT: 9, TRK.IMP: 6, TRK.SRC: 10, TRK.NOTES: 24}
    for c, w in widths.items():
        sh.col_width(c, w)
    return sh
