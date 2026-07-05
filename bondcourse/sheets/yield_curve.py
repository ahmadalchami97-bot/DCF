"""Sheet 11: Yield Curve -- where is this bond on the curve?"""

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
    common.title_block(sh, "YIELD CURVE", "Where is this bond on the government yield curve?", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "The yield curve shows government bond yields across different maturities. It tells you whether longer bonds "
        "pay more, and where your bond sits.",
        "Enter today's government yields in the yellow cells; the chart and the read update automatically.",
    ], last_col=LAST)
    r += 1

    r = common.section(sh, r, "Government yields", c1=1, c2=LAST)
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
    sh.put(r, 2, "=YrsToMat", role="link", fmt=Fmt.YEARS); r += 1
    sh.put(r, 1, "Maturity bucket", role="label_b")
    sh.put(r, 2, '=IF(YrsToMat<=3,"Short-term",IF(YrsToMat<=10,"Intermediate-term","Long-term"))',
           role="output_l"); sh.merge(r, 2, r, 3); r += 1
    sh.put(r, 1, "Curve slope (10y - 2y)", role="label_b")
    sh.put(r, 2, "=(Y10Y-Y2Y)*10000", role="formula", fmt=Fmt.BPS); r += 1
    sh.put(r, 1, "Curve shape", role="label_b")
    sh.put(r, 2, '=IF(N(Y10Y)=0,"Enter curve yields above",'
                 'IF(Y10Y-Y2Y>0.001,"Normal",IF(Y10Y-Y2Y<-0.001,"Inverted","Flat")))', role="output_l")
    define_name(sh, "CurveShape", r, 2)
    sh.merge(r, 2, r, 4)
    common.traffic_light(sh, f"B{r}:B{r}", f"B{r}")
    r += 2

    cats = Reference(sh.ws, min_col=1, min_row=first, max_row=last)
    data = Reference(sh.ws, min_col=2, min_row=hdr, max_row=last)
    common.line_chart(sh, f"D{first}", "Government yield curve", cats_ref=cats, data_ref=data, width=14, height=8)

    r = common.interp(sh, r, [
        "NORMAL curve: long-term yields are HIGHER than short-term yields - investors are paid more for lending "
        "longer. This is the usual shape.",
        "INVERTED curve: short-term yields are HIGHER than long-term yields. The market may expect future rate cuts or "
        "slower growth (watched as a recession signal).",
        "FLAT curve: short and long yields are close - often a sign of uncertainty about future rates.",
        "For your bond: a longer maturity sits further right on the curve and carries more interest-rate risk; a "
        "short bill sits at the left with little rate risk.",
    ], last_col=LAST)

    sh.freeze("A6")
    sh.col_width(1, 22); sh.col_width(2, 12)
    for c in range(3, LAST + 1):
        sh.col_width(c, 12)
    return sh
