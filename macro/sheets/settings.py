"""S17 Settings & Lists -- the control panel: vocab lists, weights, thresholds."""

from __future__ import annotations

from .. import common
from ..common import define_name
from ..config import (FED_BANDS, FED_SUBSCORES, LIST_CATEGORY, LIST_CBBIAS, LIST_CONFIDENCE,
                      LIST_COUNTRY, LIST_DECISION, LIST_DIRECTION, LIST_DOTPLOT, LIST_FEDBIAS,
                      LIST_FREQUENCY, LIST_IMPORTANCE, LIST_SCORE5, F_NUM2)

LAST = 9


def build(sh, ctx):
    common.title_block(sh, "SETTINGS & LISTS", "One control panel: every dropdown list, weight and threshold",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "Nothing analytical is hidden. Tune the model here: change a weight or a list and every sheet that uses it "
        "updates. The Fed weights below are the only numbers that change how the Fed bias score is calculated.",
    ], last_col=LAST)
    r += 1

    # --- Fed weights (named range Fed_Weights) ---
    r = common.section(sh, r, "Fed bias score - sub-score weights (must sum to 1.00)", c1=1, c2=LAST)
    sh.put(r, 1, "Sub-score", role="colhdr_l")
    sh.put(r, 2, "Weight", role="colhdr")
    sh.merge(r, 3, r, LAST)
    sh.put(r, 3, "What it captures", role="colhdr_l")
    r += 1
    w_first = r
    notes = ["CPI / Core CPI / PCE surprises (from the Surprise Engine)",
             "payrolls / unemployment / wages / claims / JOLTS surprises",
             "GDP / ISM / PMI / retail growth surprises",
             "your read of recent Fed speeches (-2..+2)",
             "change in the market-implied policy path (bps)",
             "2Y Treasury yield move since the last meeting (bps)",
             "10Y real-yield move (bps)"]
    for (label, weight), note in zip(FED_SUBSCORES, notes):
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, weight, role="input", fmt=F_NUM2)
        sh.merge(r, 3, r, LAST)
        sh.put(r, 3, note, role="note_l")
        r += 1
    w_last = r - 1
    define_name(sh, "Fed_Weights", w_first, 2, w_last, 2)
    sh.put(r, 1, "Total", role="total_l")
    sh.put(r, 2, f"=SUM(B{w_first}:B{w_last})", role="total", fmt=F_NUM2)
    sh.put(r, 3, f'=IF(ABS(B{r}-1)<0.001,"OK - weights sum to 1.00","WARNING: weights must sum to 1.00")',
           role="status")
    sh.merge(r, 3, r, LAST)
    common.word_cf(sh, f"C{r}:C{r}", [("OK - weights sum to 1.00", common.GREEN)])
    r += 2

    # --- Fed bias bands (documentation) ---
    r = common.section(sh, r, "Fed bias bands (applied to the composite score)", c1=1, c2=LAST)
    band_txt = "  ·  ".join([f"score >= {lo:+.2f} -> {lab}" for lo, lab in FED_BANDS] + ["below -1.00 -> Dovish"])
    sh.merge(r, 1, r, LAST)
    sh.put(r, 1, band_txt, role="note_l")
    r += 1
    sh.merge(r, 1, r, LAST)
    sh.put(r, 1, "Surprise Engine z-score bands:  |z| < 0.5 = Neutral · z >= 0.5 = Hot (above forecast) · "
                 "z <= -0.5 = Cold (below forecast).", role="note_l")
    r += 2

    # --- Dropdown lists ---
    r = common.section(sh, r, "Dropdown lists (reference)", c1=1, c2=LAST)
    lists = [("Country/Region", LIST_COUNTRY), ("Frequency", LIST_FREQUENCY),
             ("Importance", LIST_IMPORTANCE), ("Confidence", LIST_CONFIDENCE),
             ("Fed / CB bias", LIST_FEDBIAS), ("Direction", LIST_DIRECTION),
             ("Speech tone (-2..+2)", LIST_SCORE5), ("Dot-plot", LIST_DOTPLOT),
             ("Decision", LIST_DECISION), ("Category", LIST_CATEGORY), ("CB bias", LIST_CBBIAS)]
    # lay the lists out in three columns of stacked blocks
    col_slots = [1, 4, 7]
    row_slots = [r, r, r]
    for i, (name, vals) in enumerate(lists):
        slot = i % 3
        cc = col_slots[slot]
        rr = row_slots[slot]
        sh.put(rr, cc, name, role="label_b")
        sh.merge(rr, cc, rr, cc + 1)
        rr += 1
        for v in vals:
            sh.put(rr, cc, v, role="note_l")
            rr += 1
        row_slots[slot] = rr + 1

    sh.freeze("A6")
    sh.col_width(1, 22); sh.col_width(2, 10); sh.col_width(3, 20)
    for c in range(4, LAST + 1):
        sh.col_width(c, 14)
    return sh
