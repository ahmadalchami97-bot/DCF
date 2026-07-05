"""Sheet 8: Investment Attractiveness -- a simple, transparent /10 framework."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import attractiveness_cf, define_name

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "INVESTMENT ATTRACTIVENESS", "Is this bond a good investment? A simple, transparent view",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "This is a SIMPLE framework - not a guarantee. It scores the bond only on its yield, duration risk, price "
        "sensitivity (DV01), curve position and how well it fits your rate outlook. It helps you judge whether the "
        "yield is worth the interest-rate risk. It cannot know your personal situation.",
    ], last_col=LAST)
    r += 1

    hdr = r
    for c, tx in enumerate(["Category", "Score", "Max", "How it is scored"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c not in (1, 4) else "colhdr_l")
    r += 1
    sc_first = r
    rows = [
        ("Yield attractiveness", "=IF(YTM>=0.045,3,IF(YTM>=0.035,2,IF(YTM>=0.025,1,0)))", 3,
         "3 if YTM >= 4.5%, 2 if >= 3.5%, 1 if >= 2.5%, else 0 (more yield = more income)."),
        ("Duration risk", "=IF(ModDur<=3,3,IF(ModDur<=7,2,IF(ModDur<=12,1,0)))", 3,
         "Lower duration scores higher (less rate risk): 3 if <= 3, 2 if <= 7, 1 if <= 12, else 0."),
        ("Price sensitivity (DV01)", "=IF(DV01<=0.03,2,IF(DV01<=0.08,1,0))", 2,
         "Lower DV01 = smaller price move per 1 bp: 2 if <= 0.03, 1 if <= 0.08, else 0."),
        ("Yield curve context", "=IF(N(Y10Y)=0,0,IF(Y10Y>Y2Y,1,0))", 1,
         "1 if the curve is normal/upward (positive roll-down); 0 if flat/inverted or no curve entered."),
        ("Rate outlook fit",
         '=IF(RateOutlook="Yields Rise",IF(ModDur<=4,1,0),IF(RateOutlook="Yields Fall",IF(ModDur>=7,1,0),'
         'IF(YTM>=BenchYield,1,0)))', 1,
         "Rise -> short duration scores; Fall -> long duration scores; Stable -> carry (yield >= benchmark) scores."),
    ]
    for label, formula, mx, note in rows:
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, formula, role="formula", fmt=Fmt.INT)
        sh.put(r, 3, f"/ {mx}", role="note_l")
        sh.put(r, 4, note, role="note_l")
        sh.merge(r, 4, r, LAST)
        r += 1
    sc_last = r - 1
    sh.put(r, 1, "TOTAL SCORE", role="total_l")
    sh.put(r, 2, f"=SUM(B{sc_first}:B{sc_last})", role="total", fmt=Fmt.INT)
    define_name(sh, "AttractScore", r, 2)
    sh.put(r, 3, "/ 10", role="total")
    sh.put(r, 4, "8-10 = Attractive,  5-7 = Neutral,  0-4 = Not Attractive.", role="note_l")
    sh.merge(r, 4, r, LAST)
    r += 2

    r = common.interp(sh, r, [
        "The score adds points for a good yield, low duration/rate risk, low price sensitivity, a helpful curve, and a "
        "fit with your rate outlook. A higher score means the yield looks more worth the risk - but it is a starting "
        "point, not a personal recommendation.",
    ], last_col=LAST)

    r = common.section(sh, r, "Result", c1=1, c2=LAST)
    sh.put(r, 1, "Model suggests", role="label_b")
    sh.put(r, 2, '=IF(AttractScore>=8,"Attractive",IF(AttractScore>=5,"Neutral","Not Attractive"))',
           role="result", align="c")
    define_name(sh, "ModelView", r, 2)
    sh.merge(r, 2, r, 3)
    attractiveness_cf(sh, f"B{r}")
    sh.put(r, 4, '="Score "&AttractScore&" / 10"', role="formula_l"); sh.merge(r, 4, r, LAST)
    r += 1
    sh.put(r, 1, "Key supporting factor", role="label_b")
    sh.put(r, 2, '=IF(YTM>=0.04,"Yield of "&TEXT(YTM,"0.00%")&" gives reasonable income for a government bond.",'
                 'IF(ModDur<=3,"Low rate risk - modified duration is only "&TEXT(ModDur,"0.0")&".",'
                 '"Simple, default-free government bond exposure."))', role="formula_l")
    sh.merge(r, 2, r, LAST); sh.row_height(r, 24); r += 1
    sh.put(r, 1, "Key risk", role="label_b")
    sh.put(r, 2, '=IF(ModDur>7,"High duration ("&TEXT(ModDur,"0.0")&") - the price falls a lot if yields rise.",'
                 'IF(YTM<0.03,"Low yield - limited income for the interest-rate risk taken.",'
                 'IF(AND(N(Y10Y)>0,Y10Y<Y2Y),"Inverted curve - a possible macro / recession signal.",'
                 '"Interest-rate risk - the price moves opposite to yields.")))', role="formula_l")
    sh.merge(r, 2, r, LAST); sh.row_height(r, 24); r += 2

    r = common.section(sh, r, "Analyst override & final view", c1=1, c2=LAST)
    sh.put(r, 1, "Analyst override", role="label_b")
    sh.put(r, 3, "Use model view", role="input_l")
    common.dropdown(sh, r, 3, ["Use model view", "Attractive", "Neutral", "Not Attractive"])
    define_name(sh, "AnalystOverride", r, 3)
    sh.merge(r, 3, r, 4)
    sh.put(r, 5, "Override the model if you disagree.", role="note_l"); sh.merge(r, 5, r, LAST)
    r += 1
    sh.put(r, 1, "Final investment view", role="label_b")
    sh.put(r, 2, '=IF(AnalystOverride="Use model view",ModelView,AnalystOverride)', role="result", align="c")
    define_name(sh, "FinalView", r, 2)
    sh.merge(r, 2, r, 3)
    attractiveness_cf(sh, f"B{r}")
    r += 2

    sh.put(r, 1, "Final output", role="label_b")
    sh.put(r, 2, '="Based on this simple framework, this bond currently appears: "&FinalView&"."',
           role="output_l")
    sh.merge(r, 2, r, LAST); sh.row_height(r, 20); r += 2

    sh.put(r, 1, "Final analyst comment", role="label_b")
    sh.put(r, 2, "", role="input_l"); sh.merge(r, 2, r, LAST); sh.row_height(r, 28); r += 2

    common.interp(sh, r, [
        "Reminder: the attractiveness score is a simple, transparent framework, not a guarantee that the bond is a "
        "good investment. A bond can be right for one investor and wrong for another depending on horizon, cash needs "
        "and rate views. The final view above is editable - set it to whatever your judgement says.",
    ], last_col=LAST, title="Important")

    sh.freeze("A6")
    sh.col_width(1, 24); sh.col_width(2, 14); sh.col_width(3, 8)
    for c in range(4, LAST + 1):
        sh.col_width(c, 13)
    return sh
