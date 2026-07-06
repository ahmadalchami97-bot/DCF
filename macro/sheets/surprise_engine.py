"""S03 Surprise Engine -- surprise vs expectations -> inflation/growth signal -> asset arrows."""

from __future__ import annotations

from .. import common
from ..common import arrow, define_name
from ..config import FIRST_ROW, HDR_ROW, NROWS, SUR, F_DATE, F_NUM2, F_SCORE, F_SIGNED

LAST = SUR.LAST
TD = "'Data Tracker'!"


def build(sh, ctx):
    common.title_block(sh, "DATA SURPRISE ENGINE",
                       "Markets trade the surprise vs forecast - this scores it into signals and asset impacts",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    sh.merge(6, 1, 6, LAST)
    sh.put(6, 1, "Everything here is calculated from the Data Tracker (same rows). z = surprise / typical surprise. "
                 "Infl.imp = z x inflation-polarity x importance (this is the hawkish impulse that feeds the Fed "
                 "score). Arrows are the usual first-order reaction, not a prediction.", role="note_l")

    hdr = HDR_ROW
    heads = [(SUR.DATE, "Date"), (SUR.INDIC, "Indicator"), (SUR.CAT, "Category"), (SUR.ACTUAL, "Actual"),
             (SUR.FCST, "Fcst"), (SUR.PREV, "Prev"), (SUR.ABS, "Surprise"), (SUR.Z, "z"), (SUR.HOT, "Hot/Cold"),
             (SUR.INFLIMP, "Infl.imp"), (SUR.GROWIMP, "Grow.imp"), (SUR.INFL, "Inflation"), (SUR.GROW, "Growth"),
             (SUR.USD, "USD"), (SUR.UYLD, "UST yld"), (SUR.UPX, "UST px"), (SUR.GOLD, "Gold"), (SUR.OIL, "Oil"),
             (SUR.SPX, "S&P"), (SUR.EM, "EM"), (SUR.GCC, "GCC"), (SUR.TONE, "Risk tone"), (SUR.CONF, "Conf")]
    for c, tx in heads:
        sh.put(hdr, c, tx, role="colhdr_l" if c in (SUR.INDIC, SUR.CAT) else "colhdr")
    sh.row_height(hdr, 16)

    for i in range(NROWS):
        r = FIRST_ROW + i
        gate = f'{TD}$D{r}=""'          # blank when the Tracker row has no indicator
        eblank = f'$E{r}=""'            # blank when this row's Actual is blank
        # helper: MATCH index into the library (hidden col Z)
        sh.put(r, SUR.MIDX, f'=IF({gate},"",IFERROR(MATCH({TD}$D{r},Lib_Name,0),""))', role="formula")
        # mirror the tracker
        sh.put(r, SUR.DATE, f'=IF({gate},"",{TD}$B{r})', role="link", fmt=F_DATE)
        sh.put(r, SUR.INDIC, f'=IF({gate},"",{TD}$D{r})', role="link")
        sh.put(r, SUR.CAT, f'=IF($Z{r}="","",IFERROR(INDEX(Lib_Cat,$Z{r}),""))', role="formula", align="c")
        sh.put(r, SUR.ACTUAL, f'=IF({gate},"",{TD}$E{r})', role="link", fmt=F_NUM2)
        sh.put(r, SUR.FCST, f'=IF({gate},"",{TD}$F{r})', role="link", fmt=F_NUM2)
        sh.put(r, SUR.PREV, f'=IF({gate},"",{TD}$G{r})', role="link", fmt=F_NUM2)
        # surprise + z
        sh.put(r, SUR.ABS, f'=IF({eblank},"",$E{r}-$F{r})', role="formula", fmt=F_SIGNED)
        sh.put(r, SUR.Z, f'=IF({eblank},"",IFERROR($H{r}/INDEX(Lib_Scale,$Z{r}),0))', role="formula", fmt=F_SCORE)
        sh.put(r, SUR.HOT, f'=IF({eblank},"",IF(ABS($I{r})<0.5,"Neutral",IF($I{r}>0,"Hot","Cold")))',
               role="formula", align="c")
        # impulses (K = hawkish impulse feeds the Fed score)
        sh.put(r, SUR.INFLIMP, f'=IF({eblank},"",$I{r}*INDEX(Lib_PolInfl,$Z{r})*INDEX(Lib_Importance,$Z{r})/5)',
               role="formula", fmt=F_SCORE)
        sh.put(r, SUR.GROWIMP, f'=IF({eblank},"",$I{r}*INDEX(Lib_PolGrow,$Z{r})*INDEX(Lib_Importance,$Z{r})/5)',
               role="formula", fmt=F_SCORE)
        sh.put(r, SUR.INFL, f'=IF({eblank},"",IF($K{r}>0.5,"Inflationary",IF($K{r}<-0.5,"Disinflationary","Neutral")))',
               role="formula", align="c")
        sh.put(r, SUR.GROW, f'=IF({eblank},"",IF($L{r}>0.5,"Growth+",IF($L{r}<-0.5,"Growth-","Neutral")))',
               role="formula", align="c")
        # asset arrows (usual first-order reaction)
        sh.put(r, SUR.USD, f'=IF({eblank},"",{arrow(f"0.6*$K{r}+0.4*$L{r}")})', role="formula", align="c")
        sh.put(r, SUR.UYLD, f'=IF({eblank},"",{arrow(f"0.7*$K{r}+0.3*$L{r}")})', role="formula", align="c")
        sh.put(r, SUR.UPX, f'=IF({eblank},"",{arrow(f"-(0.7*$K{r}+0.3*$L{r})")})', role="formula", align="c")
        sh.put(r, SUR.GOLD, f'=IF({eblank},"",{arrow(f"-0.8*$K{r}")})', role="formula", align="c")
        sh.put(r, SUR.OIL, f'=IF({eblank},"",{arrow(f"0.5*$L{r}")})', role="formula", align="c")
        sh.put(r, SUR.SPX, f'=IF({eblank},"",{arrow(f"0.5*$L{r}-0.5*$K{r}")})', role="formula", align="c")
        sh.put(r, SUR.EM, f'=IF({eblank},"",{arrow(f"0.4*$L{r}-0.6*$K{r}")})', role="formula", align="c")
        sh.put(r, SUR.GCC, f'=IF({eblank},"",{arrow(f"0.5*$L{r}")})', role="formula", align="c")
        sh.put(r, SUR.TONE,
               f'=IF({eblank},"",IF(AND($L{r}>=0.5,$K{r}<=0.5),"Risk-on",'
               f'IF(OR($L{r}<=-0.5,$K{r}>=1),"Risk-off","Neutral")))', role="formula", align="c")
        sh.put(r, SUR.CONF,
               f'=IF({eblank},"",IF(AND(IFERROR(INDEX(Lib_Importance,$Z{r}),0)>=4,ABS($I{r})>=1),"High",'
               f'IF(ABS($I{r})<0.5,"Low","Medium")))', role="formula", align="c")

    last = FIRST_ROW + NROWS - 1
    define_name(sh, "SUR_CAT", FIRST_ROW, SUR.CAT, last, SUR.CAT)
    define_name(sh, "SUR_INFLIMP", FIRST_ROW, SUR.INFLIMP, last, SUR.INFLIMP)
    define_name(sh, "SUR_GROWIMP", FIRST_ROW, SUR.GROWIMP, last, SUR.GROWIMP)

    # colour the signal columns
    common.word_cf(sh, f"J{FIRST_ROW}:J{last}", common.CF_HOT)
    common.word_cf(sh, f"M{FIRST_ROW}:M{last}", common.CF_INFL)
    common.word_cf(sh, f"N{FIRST_ROW}:N{last}", common.CF_GROW)
    common.word_cf(sh, f"W{FIRST_ROW}:W{last}", common.CF_TONE)
    common.word_cf(sh, f"X{FIRST_ROW}:X{last}", common.CF_CONF)

    r = last + 2
    r = common.interp(sh, r, [
        "Arrows show the USUAL first-order reaction to that surprise: ⇈ strong up · ↑ up · ↔ neutral · ↓ down · "
        "⇊ strong down. UST px is the inverse of UST yld (prices fall when yields rise).",
        "Infl.imp (column K) is the hawkish impulse: positive = hawkish/inflationary, negative = dovish. The Fed "
        "Tracker averages these by category to build its bias score. GCC is shown as an oil/growth proxy - the "
        "dedicated GCC read comes with the Oil and USD modules in the next build phase.",
    ], last_col=LAST)

    sh.ws.column_dimensions["Z"].hidden = True
    sh.freeze("E9")
    for c in range(SUR.DATE, LAST + 1):
        sh.col_width(c, 8)
    sh.col_width(SUR.INDIC, 22); sh.col_width(SUR.CAT, 11); sh.col_width(SUR.HOT, 9)
    sh.col_width(SUR.INFL, 12); sh.col_width(SUR.GROW, 10); sh.col_width(SUR.TONE, 10)
    sh.col_width(SUR.UYLD, 8); sh.col_width(SUR.UPX, 8)
    return sh
