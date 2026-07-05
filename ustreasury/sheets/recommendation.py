"""Sheet 9: Recommendation -- one-page summary. Final Buy/Hold/Avoid stays manual."""

from __future__ import annotations

from bond.config import Fmt
from .. import common

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "RECOMMENDATION", "One-page US Treasury summary and analyst view", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "A one-page summary of price, yield, duration and curve context. The hints below are automatic; the final "
        "Buy / Hold / Avoid call is yours (a manual input).",
    ], last_col=LAST)
    r += 1

    sh.put(r, 1, "Recommendation", role="label_b")
    sh.put(r, 2, "Hold", role="input_c")
    common.dropdown(sh, r, 2, ["Buy", "Hold", "Avoid"])
    sh.merge(r, 2, r, 3)
    sh.put(r, 4, "Your call. Use the summary and hints below to justify it.", role="note_l")
    sh.merge(r, 4, r, LAST)
    r += 2

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

    r = common.section(sh, r, "Automatic interpretation (hints)", c1=1, c2=LAST)

    def hint(formula):
        nonlocal r
        sh.put(r, 1, formula, role="formula_l")
        sh.merge(r, 1, r, LAST)
        r += 1
    hint('=IF(ModDur<3,"Rate sensitivity: LOW (short duration) - suits an investor wanting little rate risk.",'
         'IF(ModDur<8,"Rate sensitivity: MODERATE (intermediate duration).",'
         '"Rate sensitivity: HIGH (long duration) - big price moves if yields change."))')
    hint('=IF(IsZero=1,"Treasury Bill: low duration and high liquidity - good for parking cash.",'
         'IF(MktClean>Face,"Priced at a premium (coupon above current yields).",'
         'IF(MktClean<Face,"Priced at a discount (coupon below current yields).","Priced near par.")))')
    hint('=IF(N(Y10Y)=0,"Add curve yields on the Yield Curve sheet for curve context.",'
         'IF(Y10Y-Y2Y<-0.001,"Curve is inverted - long bonds yield less than short; weigh reinvestment vs price risk.",'
         '"Curve is normal/flat - longer maturities generally offer more yield for more duration risk."))')
    r += 1

    r = common.section(sh, r, "Guidance", c1=1, c2=LAST)
    for g in [
        "A short-duration Treasury (or a bill) suits an investor who wants low interest-rate sensitivity and liquidity.",
        "A long-duration Treasury suits an investor who expects yields to FALL (prices would rise more).",
        "A long Treasury bond carries higher price risk if yields RISE.",
    ]:
        sh.put(r, 1, "-  " + g, role="note_l"); sh.merge(r, 1, r, LAST); sh.row_height(r, 24); r += 1
    r += 1

    r = common.section(sh, r, "Analyst view (manual)", c1=1, c2=LAST)
    for label in ("Main risks", "Final analyst comment"):
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, "", role="input_l")
        sh.merge(r, 2, r, LAST)
        sh.row_height(r, 28)
        r += 1
    sh.put(r + 1, 1, "Reminder: this is a decision-support summary, not investment advice.", role="note")
    sh.merge(r + 1, 1, r + 1, LAST)

    sh.freeze("A6")
    sh.col_width(1, 20); sh.col_width(2, 14); sh.col_width(3, 8)
    sh.col_width(4, 20); sh.col_width(5, 14); sh.col_width(6, 10)
    return sh
