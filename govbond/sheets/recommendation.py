"""Sheet 9: Recommendation Summary -- one page. Buy/Hold/Avoid stays manual."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import attractiveness_cf

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "RECOMMENDATION SUMMARY", "One-page view of the bond and the analyst's call", last_col=LAST)
    common.nav_bar(sh, 5)
    r = 7

    # top: the two headline calls
    sh.put(r, 1, "Final recommendation", role="label_b")
    sh.put(r, 3, "Hold", role="input_c")
    common.dropdown(sh, r, 3, ["Buy", "Hold", "Avoid"])
    sh.merge(r, 3, r, 4)
    sh.put(r, 5, "Manual - your trading call.", role="note_l"); sh.merge(r, 5, r, LAST)
    r += 1
    sh.put(r, 1, "Investment attractiveness", role="label_b")
    sh.put(r, 3, "=FinalView", role="result", align="c")
    sh.merge(r, 3, r, 4)
    attractiveness_cf(sh, f"C{r}")
    sh.put(r, 5, "From the Investment Attractiveness sheet.", role="note_l"); sh.merge(r, 5, r, LAST)
    r += 2

    def pair(rr, col, label, formula, fmt, role="link"):
        sh.put(rr, col, label, role="label_b")
        sh.put(rr, col + 1, formula, role=role, fmt=fmt)

    top = r
    common.section(sh, top, "Bond & pricing", c1=1, c2=3)
    common.section(sh, top, "Risk & context", c1=4, c2=LAST)
    r = top + 1
    left = [
        ("Bond name", "=BondName", None), ("Issuer", "=Issuer", None), ("Currency", "=Ccy", None),
        ("Maturity", "=Maturity", Fmt.DATE), ("Coupon rate", "=CouponRate", Fmt.PCT2),
        ("Clean price", "=MktClean", Fmt.PRICE), ("Dirty price", "=Dirty", Fmt.PRICE),
        ("Yield to maturity", "=YTM", Fmt.PCT3), ("Current yield", "=CurrentYield", Fmt.PCT2),
        ("Spread (bps)", "=SpreadBps", Fmt.BPS),
    ]
    right = [
        ("Macaulay duration", "=MacDur", Fmt.YEARS), ("Modified duration", "=ModDur", Fmt.RATIO),
        ("Convexity", "=Convexity", Fmt.RATIO), ("DV01 (per 100)", "=DV01", Fmt.NUM4),
        ("Price if +100 bps", "=CleanPrice+(-ModDur*0.01+0.5*Convexity*0.01^2)*CleanPrice", Fmt.PRICE),
        ("Yield curve view", "=CurveShape", None),
        ("Maturity bucket", '=IF(YearsToMat<=3,"Short-term",IF(YearsToMat<=10,"Intermediate-term","Long-term"))', None),
        ("Attractiveness score", '=AttractScore&" / 10"', None),
    ]
    for i in range(max(len(left), len(right))):
        rr = r + i
        if i < len(left):
            pair(rr, 1, left[i][0], left[i][1], left[i][2])
        if i < len(right):
            pair(rr, 4, right[i][0], right[i][1], right[i][2])
    r += max(len(left), len(right)) + 1

    r = common.section(sh, r, "Positives, risks & comment", c1=1, c2=LAST)
    sh.put(r, 1, "Main positive factor", role="label_b")
    sh.put(r, 2, '=IF(YTM>=BenchYield,"Yield of "&TEXT(YTM,"0.00%")&" is at or above the benchmark - decent income.",'
                 '"Simple, liquid, default-free government bond exposure.")', role="formula_l")
    sh.merge(r, 2, r, LAST); sh.row_height(r, 24); r += 1
    sh.put(r, 1, "Main risk", role="label_b")
    sh.put(r, 2, '=IF(ModDur>7,"High duration - price is very sensitive to rising yields.",'
                 '"Interest-rate risk - the price falls if yields rise.")', role="formula_l")
    sh.merge(r, 2, r, LAST); sh.row_height(r, 24); r += 1
    sh.put(r, 1, "Final analyst comment", role="label_b")
    sh.put(r, 2, "", role="input_l"); sh.merge(r, 2, r, LAST); sh.row_height(r, 28); r += 2

    common.interp(sh, r, [
        "BUY = the bond looks attractive on the model and your view. HOLD = acceptable, but not clearly attractive. "
        "AVOID = the return does not look like enough for the interest-rate risk.",
        "The Buy / Hold / Avoid call is deliberately left as YOUR manual input - the model informs it but does not "
        "make it.",
    ], last_col=LAST, title="How to read Buy / Hold / Avoid")

    sh.freeze("A6")
    sh.col_width(1, 22); sh.col_width(2, 14); sh.col_width(3, 8)
    sh.col_width(4, 20); sh.col_width(5, 14); sh.col_width(6, 12)
    return sh
