"""S05 Fed & Central Bank Tracker -- policy state + the hawkish/dovish composite score."""

from __future__ import annotations

from .. import common
from ..common import define_name, dropdown
from ..config import (FED_BANDS, FED_SUBSCORES, LIST_CBBIAS, LIST_DECISION, LIST_DOTPLOT, LIST_SCORE5,
                      F_DATE, F_INT, F_NUM2, F_SCORE)

LAST = 8


def _ladder(cell):
    """Map a bps move to a -2..+2 sub-score."""
    return (f'=IF({cell}>=15,2,IF({cell}>=5,1,IF({cell}>-5,0,IF({cell}>-15,-1,-2))))')


def _band(cell):
    expr = '"Dovish"'
    for lo, lab in reversed(FED_BANDS):
        expr = f'IF({cell}>={lo},"{lab}",{expr})'
    return "=" + expr


def build(sh, ctx):
    st = ctx.data["fed_state"]
    speeches = ctx.data["fed_speeches"]
    cbs = ctx.data["global_cb"]
    common.title_block(sh, "FED & CENTRAL BANK TRACKER", "What the Fed is doing, saying, and our hawkish/dovish score",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "The score blends seven inputs (each -2 dovish .. +2 hawkish): inflation, labor and growth surprises come "
        "straight from the Surprise Engine; the rest you set from Fed speeches and market moves. Weights live on "
        "Settings. Composite >= +1 = Hawkish, <= -1 = Dovish.",
    ], last_col=LAST)
    r += 1

    def inrow(label, value, role="input", fmt=None, note="", options=None):
        nonlocal r
        sh.put(r, 1, label, role="label_b")
        cell = sh.put(r, 3, value, role=role, fmt=fmt)
        sh.merge(r, 3, r, 4)
        if options:
            dropdown(sh, r, 3, options)
        if note:
            sh.put(r, 5, note, role="note_l"); sh.merge(r, 5, r, LAST)
        r += 1
        return cell

    # --- policy state ---
    r = common.section(sh, r, "Policy state", c1=1, c2=LAST)
    sh.put(r, 1, "Fed funds target range", role="label_b")
    sh.put(r, 3, st["target_low"], role="input", fmt=F_NUM2)
    sh.put(r, 4, st["target_high"], role="input", fmt=F_NUM2)
    sh.put(r, 5, "% lower / upper bound", role="note_l"); sh.merge(r, 5, r, LAST); r += 1
    inrow("Last decision", st["last_decision"], role="input_c", options=LIST_DECISION)
    inrow("Last meeting date", st["last_date"], role="input_c", fmt=F_DATE)
    next_cell = inrow("Next FOMC date", st["next_fomc"], role="input_c", fmt=F_DATE)
    sh.put(r, 1, "Days to next FOMC", role="label_b")
    sh.put(r, 3, f"=IF({next_cell.coordinate}=\"\",\"\",{next_cell.coordinate}-TODAY())", role="formula", fmt=F_INT)
    sh.merge(r, 3, r, 4)
    sh.put(r, 5, "counts down automatically", role="note_l"); sh.merge(r, 5, r, LAST); r += 1
    implied_cell = inrow("Market-implied path change (bps)", st["implied_bps"], fmt=F_INT,
                         note="+ = market priced more hawkish since last meeting")
    inrow("Cuts priced this year", st["expected_cuts"], fmt=F_INT)
    inrow("Dot-plot direction", st["dotplot"], role="input_c", options=LIST_DOTPLOT)
    curve_cell = inrow("2Y yield move since last (bps)", st["curve_2y_bps"], fmt=F_INT)
    real_cell = inrow("10Y real-yield move (bps)", st["real_10y_bps"], fmt=F_INT)
    sh.put(r, 1, "Balance sheet / QT", role="label_b")
    sh.put(r, 3, st["qt_note"], role="input_l"); sh.merge(r, 3, r, LAST); r += 2

    # --- speeches (feed sub-score 4) ---
    r = common.section(sh, r, "Fed speech log (tone: -2 dovish .. +2 hawkish)", c1=1, c2=LAST)
    sh.put(r, 1, "Date", role="colhdr_l"); sh.put(r, 2, "Speaker", role="colhdr_l")
    sh.put(r, 4, "Tone", role="colhdr"); sh.put(r, 5, "Comment / takeaway", role="colhdr_l")
    sh.merge(r, 2, r, 3); sh.merge(r, 5, r, LAST)
    r += 1
    sp_first = r
    n_speech_rows = max(6, len(speeches) + 2)
    for i in range(n_speech_rows):
        s = speeches[i] if i < len(speeches) else None
        sh.put(r, 1, s[0] if s else None, role="input_c", fmt=F_DATE)
        sh.put(r, 2, s[1] if s else None, role="input_l"); sh.merge(r, 2, r, 3)
        sh.put(r, 4, s[2] if s else None, role="input", fmt=F_INT)
        dropdown(sh, r, 4, LIST_SCORE5)
        txt = f"{s[3]}  ->  {s[4]}" if s else None
        sh.put(r, 5, txt, role="input_l"); sh.merge(r, 5, r, LAST)
        r += 1
    sp_last = r - 1
    tone_range = f"D{sp_first}:D{sp_last}"
    r += 1

    # --- score ---
    r = common.section(sh, r, "Hawkish / dovish score", c1=1, c2=LAST)
    sh.put(r, 1, "Sub-score", role="colhdr_l")
    sh.put(r, 3, "Score", role="colhdr"); sh.put(r, 4, "Weight", role="colhdr")
    sh.put(r, 5, "Contribution", role="colhdr"); sh.put(r, 6, "Source", role="colhdr_l")
    sh.merge(r, 6, r, LAST)
    r += 1
    sc_first = r
    formulas = [
        '=MEDIAN(-2,IFERROR(AVERAGEIF(SUR_CAT,"Inflation",SUR_INFLIMP),0),2)',
        '=MEDIAN(-2,IFERROR(AVERAGEIF(SUR_CAT,"Labor",SUR_INFLIMP),0),2)',
        '=MEDIAN(-2,IFERROR(AVERAGEIF(SUR_CAT,"Growth",SUR_GROWIMP),0),2)',
        f'=MEDIAN(-2,IFERROR(AVERAGE({tone_range}),0),2)',
        _ladder(implied_cell.coordinate),
        _ladder(curve_cell.coordinate),
        _ladder(real_cell.coordinate),
    ]
    sources = ["Surprise Engine - Inflation category", "Surprise Engine - Labor category",
               "Surprise Engine - Growth category", "average of the speech tones above",
               "market-implied path change (bps)", "2Y yield move (bps)", "10Y real-yield move (bps)"]
    for k, ((label, _w), fla, src) in enumerate(zip(FED_SUBSCORES, formulas, sources)):
        sh.put(r, 1, label, role="label_b"); sh.merge(r, 1, r, 2)
        sh.put(r, 3, fla, role="formula", fmt=F_SCORE)
        sh.put(r, 4, f"=INDEX(Fed_Weights,{k + 1})", role="formula", fmt=F_NUM2)
        sh.put(r, 5, f"=C{r}*D{r}", role="formula", fmt=F_SCORE)
        sh.put(r, 6, src, role="note_l"); sh.merge(r, 6, r, LAST)
        r += 1
    sc_last = r - 1
    define_name(sh, "Fed_SubScores", sc_first, 3, sc_last, 3)

    sh.put(r, 1, "COMPOSITE FED SCORE", role="total_l"); sh.merge(r, 1, r, 2)
    comp = sh.put(r, 3, "=SUMPRODUCT(Fed_SubScores,Fed_Weights)", role="total", fmt=F_SCORE)
    define_name(sh, "Score_Fed", r, 3)
    sh.put(r, 5, f"=SUM(E{sc_first}:E{sc_last})", role="total", fmt=F_SCORE)
    sh.put(r, 6, "(equals SUMPRODUCT of scores x weights)", role="note_l"); sh.merge(r, 6, r, LAST)
    r += 1
    sh.put(r, 1, "FED POLICY BIAS", role="label_b"); sh.merge(r, 1, r, 2)
    sh.put(r, 3, _band(comp.coordinate), role="result", align="c"); sh.merge(r, 3, r, 4)
    define_name(sh, "Fed_Bias_Label", r, 3)
    common.word_cf(sh, f"C{r}:C{r}", common.CF_FED)
    sh.put(r, 5, '="Score "&TEXT(Score_Fed,"+0.00;-0.00;0.00")&" / band from Settings"', role="formula_l")
    sh.merge(r, 5, r, LAST)
    r += 2

    # --- global CBs ---
    r = common.section(sh, r, "Other major central banks", c1=1, c2=LAST)
    sh.put(r, 1, "Central bank", role="colhdr_l"); sh.put(r, 3, "Bias", role="colhdr")
    sh.put(r, 5, "Note", role="colhdr_l"); sh.merge(r, 5, r, LAST)
    r += 1
    for name, bias, note in cbs:
        sh.put(r, 1, name, role="label_b")
        sh.put(r, 3, bias, role="input_c"); sh.merge(r, 3, r, 4)
        dropdown(sh, r, 3, LIST_CBBIAS)
        common.word_cf(sh, f"C{r}:C{r}", common.CF_FED)
        sh.put(r, 5, note, role="input_l"); sh.merge(r, 5, r, LAST)
        r += 1

    sh.freeze("A6")
    sh.col_width(1, 26); sh.col_width(2, 10); sh.col_width(3, 10); sh.col_width(4, 10); sh.col_width(5, 16)
    for c in range(6, LAST + 1):
        sh.col_width(c, 12)
    return sh
