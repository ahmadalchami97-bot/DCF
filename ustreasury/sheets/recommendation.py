"""Sheet 9: Recommendation -- summary, an Investment Attractiveness View, and a
manual Buy/Hold/Avoid call. The attractiveness score is a simple, transparent
framework; the final views stay editable by the analyst."""

from __future__ import annotations

from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Font, PatternFill

from bond.config import Fmt, Palette
from .. import common
from ..common import define_name

LAST = 6


def _attractiveness_cf(sh, cell):
    """Colour a cell green/amber/red for Attractive / Neutral / Not Attractive (exact match)."""
    rng = f"{cell}:{cell}"
    for word, fc, fl in (("Attractive", Palette.GOOD, Palette.GOOD_FILL),
                         ("Neutral", Palette.WARN, Palette.WARN_FILL),
                         ("Not Attractive", Palette.BAD, Palette.BAD_FILL)):
        sh.ws.conditional_formatting.add(rng, CellIsRule(
            operator="equal", formula=[f'"{word}"'],
            font=Font(name="Calibri", size=10, bold=True, color=fc),
            fill=PatternFill(start_color=fl, end_color=fl, fill_type="solid")))


def build(sh, ctx):
    common.title_block(sh, "RECOMMENDATION", "One-page US Treasury summary and analyst view", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "A one-page summary of price, yield, duration and curve context, plus a simple Investment Attractiveness "
        "View. The hints and score are automatic; the final views (Buy/Hold/Avoid and Attractive/Neutral/Not "
        "Attractive) are yours to set.",
    ], last_col=LAST)
    r += 1

    sh.put(r, 1, "Recommendation (Buy/Hold/Avoid)", role="label_b")
    sh.put(r, 3, "Hold", role="input_c")
    common.dropdown(sh, r, 3, ["Buy", "Hold", "Avoid"])
    sh.merge(r, 3, r, 4)
    sh.put(r, 5, "Your trading call - manual.", role="note_l")
    sh.merge(r, 5, r, LAST)
    r += 2

    # ---- summary metrics ----
    def pair(rr, col, label, formula, fmt, role="link"):
        sh.put(rr, col, label, role="label_b")
        sh.put(rr, col + 1, formula, role=role, fmt=fmt)

    top = r
    common.section(sh, top, "Security & pricing", c1=1, c2=3)
    common.section(sh, top, "Risk & curve", c1=4, c2=LAST)
    r = top + 1
    left = [
        ("Security", "=SecName", None), ("Type", "=SecType", None), ("Maturity", "=Maturity", Fmt.DATE),
        ("Coupon", "=CouponRate", Fmt.PCT2), ("Clean price", "=MktClean", Fmt.PRICE),
        ("Dirty price", "=Dirty", Fmt.PRICE), ("Yield to maturity", "=YTM", Fmt.PCT3),
        ("Current yield", "=CurrentYield", Fmt.PCT2),
    ]
    right = [
        ("Macaulay duration", "=MacDur", Fmt.YEARS), ("Modified duration", "=ModDur", Fmt.RATIO),
        ("Convexity", "=Convexity", Fmt.RATIO), ("DV01 (per 100)", "=DV01", Fmt.NUM4),
        ("Price if +100 bps", "=(-ModDur*0.01+0.5*Convexity*0.01^2)*CleanPrice", Fmt.PRICE),
        ("Maturity bucket", '=IF(YearsToMat<=3,"Short-term",IF(YearsToMat<=10,"Intermediate-term","Long-term"))', None),
        ("Curve slope 10y-2y", "=(Y10Y-Y2Y)*10000", Fmt.BPS), ("Spread (bps)", "=SpreadBps", Fmt.BPS),
    ]
    for i in range(max(len(left), len(right))):
        rr = r + i
        if i < len(left):
            pair(rr, 1, left[i][0], left[i][1], left[i][2])
        if i < len(right):
            pair(rr, 4, right[i][0], right[i][1], right[i][2])
    r += max(len(left), len(right)) + 1

    # ---- automatic interpretation hints ----
    r = common.section(sh, r, "Automatic interpretation (hints)", c1=1, c2=LAST)

    def hint(formula):
        nonlocal r
        sh.put(r, 1, formula, role="formula_l")
        sh.merge(r, 1, r, LAST)
        r += 1
    hint('=IF(ModDur<3,"Rate sensitivity: LOW (short duration) - little price risk if yields move.",'
         'IF(ModDur<8,"Rate sensitivity: MODERATE (intermediate duration).",'
         '"Rate sensitivity: HIGH (long duration) - big price moves if yields change."))')
    hint('=IF(IsZero=1,"Treasury Bill: low duration and high liquidity - good for parking cash.",'
         'IF(MktClean>Face,"Priced at a premium (coupon above current yields).",'
         'IF(MktClean<Face,"Priced at a discount (coupon below current yields).","Priced near par.")))')
    r += 1

    # ================= INVESTMENT ATTRACTIVENESS VIEW =================
    r = common.section(sh, r, "INVESTMENT ATTRACTIVENESS VIEW", c1=1, c2=LAST)
    r = common.explain_box(sh, r, [
        "Is this bond a good investment? This is a SIMPLE, transparent score based only on the bond's yield, "
        "duration/rate risk, price sensitivity, curve context and the fact that it is a liquid Treasury. It cannot "
        "know your personal situation - use it as a starting point, not an answer.",
    ], last_col=LAST, title="What this view is (and is not)")

    # scoring table
    hdr = r
    for c, tx in enumerate(["Category", "Score", "Max", "How it is scored"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c not in (1, 4) else "colhdr_l")
    r += 1
    sc_first = r
    rows = [
        ("Yield attractiveness", "=IF(YTM>=0.045,3,IF(YTM>=0.035,2,IF(YTM>=0.025,1,0)))", 3,
         "3 if YTM >= 4.5%, 2 if >= 3.5%, 1 if >= 2.5%, else 0 (higher yield = more income)."),
        ("Duration / rate risk", "=IF(ModDur<=3,3,IF(ModDur<=7,2,IF(ModDur<=12,1,0)))", 3,
         "Lower duration scores higher (less rate risk): 3 if <= 3, 2 if <= 7, 1 if <= 12, else 0."),
        ("Price sensitivity (DV01)", "=IF(DV01<=0.03,2,IF(DV01<=0.08,1,0))", 2,
         "Lower DV01 = smaller price move per 1 bp: 2 if <= 0.03, 1 if <= 0.08, else 0."),
        ("Yield curve context", "=IF(N(Y10Y)=0,0,IF(Y10Y>Y2Y,1,0))", 1,
         "1 if the curve is normal/upward (positive roll-down); 0 if flat/inverted or no curve entered."),
        ("Liquidity / simplicity", "=1", 1,
         "US Treasuries are highly liquid and simple, so this scores 1."),
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

    # model suggestion + reason + factor/risk
    sh.put(r, 1, "Model suggests", role="label_b")
    sh.put(r, 2, '=IF(AttractScore>=8,"Attractive",IF(AttractScore>=5,"Neutral","Not Attractive"))',
           role="result", align="c")
    define_name(sh, "ModelView", r, 2)
    sh.merge(r, 2, r, 3)
    _attractiveness_cf(sh, sh.local(r, 2).replace("$", ""))
    sh.put(r, 4, '="Score "&AttractScore&" / 10"', role="formula_l")
    sh.merge(r, 4, r, LAST)
    r += 1
    sh.put(r, 1, "Main reason", role="label_b")
    sh.put(r, 2, '=IF(AttractScore>=8,"Attractive because the yield is reasonable and the rate risk is manageable.",'
                 'IF(AttractScore>=5,IF(ModDur>7,"Neutral because the yield is acceptable, but price sensitivity to '
                 'rates is high.","Neutral because the yield and the rate risk are broadly balanced."),'
                 '"Not attractive because the yield does not compensate enough for the duration / rate risk."))',
           role="formula_l")
    sh.merge(r, 2, r, LAST); sh.row_height(r, 26); r += 1
    sh.put(r, 1, "Key supporting factor", role="label_b")
    sh.put(r, 2, '=IF(YTM>=0.04,"Yield of "&TEXT(YTM,"0.00%")&" gives reasonable income for a government bond.",'
                 'IF(ModDur<=3,"Low rate risk - modified duration is only "&TEXT(ModDur,"0.0")&".",'
                 '"Highly liquid, simple, default-free US Treasury exposure."))', role="formula_l")
    sh.merge(r, 2, r, LAST); sh.row_height(r, 24); r += 1
    sh.put(r, 1, "Key risk", role="label_b")
    sh.put(r, 2, '=IF(ModDur>7,"High duration ("&TEXT(ModDur,"0.0")&") - the price falls a lot if yields rise.",'
                 'IF(YTM<0.03,"Low yield - limited income for the interest-rate risk taken.",'
                 'IF(AND(N(Y10Y)>0,Y10Y<Y2Y),"Inverted curve - a possible macro / recession signal.",'
                 '"Interest-rate risk - the price moves opposite to yields.")))', role="formula_l")
    sh.merge(r, 2, r, LAST); sh.row_height(r, 24); r += 2

    # rate outlook link
    r = common.section(sh, r, "Your rate outlook (optional)", c1=1, c2=LAST)
    sh.put(r, 1, "Rate outlook", role="label_b")
    sh.put(r, 3, "Expect yields to stay stable", role="input_l")
    common.dropdown(sh, r, 3, ["Expect yields to rise", "Expect yields to fall", "Expect yields to stay stable"])
    define_name(sh, "RateOutlook", r, 3)
    sh.merge(r, 3, r, LAST)
    r += 1
    sh.put(r, 1, "What that implies", role="label_b")
    sh.put(r, 2, '=IF(RateOutlook="Expect yields to rise","If yields rise, SHORTER-duration bonds are usually more '
                 'attractive (less price loss). This bond has a modified duration of "&TEXT(ModDur,"0.0")&".",'
                 'IF(RateOutlook="Expect yields to fall","If yields fall, LONGER-duration bonds usually gain more. '
                 'This bond has a modified duration of "&TEXT(ModDur,"0.0")&".",'
                 '"If yields stay stable, the yield you earn (carry) matters most. This bond has a YTM of "'
                 '&TEXT(YTM,"0.00%")&"."))', role="formula_l")
    sh.merge(r, 2, r, LAST); sh.row_height(r, 26); r += 2

    # analyst override + final view
    r = common.section(sh, r, "Analyst override & final view", c1=1, c2=LAST)
    sh.put(r, 1, "Analyst override", role="label_b")
    sh.put(r, 3, "Use model view", role="input_l")
    common.dropdown(sh, r, 3, ["Use model view", "Attractive", "Neutral", "Not Attractive"])
    define_name(sh, "AnalystOverride", r, 3)
    sh.merge(r, 3, r, 4)
    sh.put(r, 5, "Override the model if you disagree.", role="note_l")
    sh.merge(r, 5, r, LAST)
    r += 1
    sh.put(r, 1, "Final investment view", role="label_b")
    sh.put(r, 2, '=IF(AnalystOverride="Use model view",ModelView,AnalystOverride)', role="result", align="c")
    sh.merge(r, 2, r, 3)
    _attractiveness_cf(sh, sh.local(r, 2).replace("$", ""))
    r += 2

    # final sentence
    sh.put(r, 1, "Final output", role="label_b")
    sh.put(r, 2, '="Based on this simple framework, this bond currently appears: "&ModelView&"."',
           role="output_l")
    sh.merge(r, 2, r, LAST); sh.row_height(r, 20); r += 2

    # manual final comment
    sh.put(r, 1, "Final analyst comment", role="label_b")
    sh.put(r, 2, "", role="input_l")
    sh.merge(r, 2, r, LAST)
    sh.row_height(r, 28)
    r += 2

    common.explain_box(sh, r, [
        "This is not a guaranteed investment recommendation. It is a structured view based on the bond's yield, "
        "duration, price sensitivity, and market-rate assumptions. A bond may be attractive for one investor and "
        "unsuitable for another depending on investment horizon, liquidity needs, and rate outlook.",
    ], last_col=LAST, title="Important")

    sh.freeze("A6")
    sh.col_width(1, 22); sh.col_width(2, 14); sh.col_width(3, 8)
    sh.col_width(4, 16); sh.col_width(5, 14); sh.col_width(6, 12)
    return sh
