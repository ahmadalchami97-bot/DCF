"""Sheet 7: Yield Curve Context."""

from __future__ import annotations

from openpyxl.chart import Reference

from bond.config import Fmt
from .. import common
from ..common import define_name

LAST = 6
TENORS = [("3-month", "Y3M", "m3"), ("2-year", "Y2Y", "y2"), ("5-year", "Y5Y", "y5"),
          ("10-year", "Y10Y", "y10"), ("30-year", "Y30Y", "y30")]


def build(sh, ctx):
    d = ctx.data["curve"]
    common.title_block(sh, "YIELD CURVE", "Where this bond sits on the US Treasury curve", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "WHAT THIS SHOWS:  the Treasury yield curve (yield by maturity) and where your bond sits on it.",
        "A NORMAL curve slopes up (longer = higher yield). A FLAT curve is roughly level. An INVERTED curve "
        "slopes down (short yields above long yields) - often a recession signal.",
        "Enter current Treasury yields in the yellow cells; the chart and the read update.",
    ], last_col=LAST)
    r += 1

    r = common.section(sh, r, "Treasury yields", c1=1, c2=LAST)
    hdr = r
    sh.put(hdr, 1, "Tenor", role="colhdr_l")
    sh.put(hdr, 2, "Yield", role="colhdr")
    r += 1
    first = r
    for label, name, key in TENORS:
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, d.get(key), role="input", fmt=Fmt.PCT2)
        define_name(sh, name, r, 2)
        r += 1
    last = r - 1
    r += 1

    r = common.section(sh, r, "Where this bond sits", c1=1, c2=LAST)
    sh.put(r, 1, "Years to maturity", role="label_b")
    sh.put(r, 2, "=YearsToMat", role="link", fmt=Fmt.YEARS); r += 1
    sh.put(r, 1, "Maturity bucket", role="label_b")
    sh.put(r, 2, '=IF(YearsToMat<=3,"Short-term",IF(YearsToMat<=10,"Intermediate-term","Long-term"))',
           role="output_l"); sh.merge(r, 2, r, 3); r += 1
    sh.put(r, 1, "Curve slope (10y - 2y)", role="label_b")
    sh.put(r, 2, "=(Y10Y-Y2Y)*10000", role="formula", fmt=Fmt.BPS); r += 1
    sh.put(r, 1, "Curve shape", role="label_b")
    sh.put(r, 2, '=IF(N(Y10Y)=0,"Enter curve yields above",'
                 'IF(Y10Y-Y2Y>0.001,"Normal (upward-sloping)",'
                 'IF(Y10Y-Y2Y<-0.001,"Inverted (downward-sloping)","Flat")))', role="output_l")
    sh.merge(r, 2, r, 4)
    common.traffic_light(sh, f"B{r}:B{r}", f"B{r}")
    r += 2

    cats = Reference(sh.ws, min_col=1, min_row=first, max_row=last)
    data = Reference(sh.ws, min_col=2, min_row=hdr, max_row=last)
    common.line_chart(sh, f"D{first}", "US Treasury yield curve", cats_ref=cats, data_ref=data, width=14, height=8)

    sh.freeze("A6")
    sh.col_width(1, 22); sh.col_width(2, 12)
    for c in range(3, LAST + 1):
        sh.col_width(c, 12)
    return sh
