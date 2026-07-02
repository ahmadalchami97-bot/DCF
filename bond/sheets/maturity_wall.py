"""Sheet 8: Maturity Wall -- debt maturity schedule + refinancing-risk read."""

from __future__ import annotations

from openpyxl.chart import Reference

from .. import common
from ..common import define_name
from ..config import Fmt

LAST = 6
BUCKETS = [("Year 1", "MW1", "y1"), ("Year 2", "MW2", "y2"), ("Year 3", "MW3", "y3"),
           ("Year 4", "MW4", "y4"), ("Year 5", "MW5", "y5"), ("After Year 5", "MWAfter", "after5")]


def build(sh, ctx):
    d = ctx.data["wall"]
    common.title_block(sh, "MATURITY WALL", "When the issuer's debt comes due, and near-term refinancing risk",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "WHAT THIS SHOWS:  how much of the issuer's total debt matures each year. A big 'wall' in the near term "
        "means the issuer must refinance a lot soon - riskier if markets are tight or liquidity is low.",
        "Enter debt maturing in each bucket (same units as the Issuer sheet). The chart and the risk read update.",
    ], last_col=LAST)
    r += 1

    r = common.section(sh, r, "Debt maturities", c1=1, c2=LAST)
    hdr = r
    sh.put(hdr, 1, "Bucket", role="colhdr_l")
    sh.put(hdr, 2, "Debt maturing", role="colhdr")
    r += 1
    first = r
    for label, name, key in BUCKETS:
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, d.get(key), role="input", fmt=Fmt.MONEY0)
        define_name(sh, name, r, 2)
        r += 1
    last = r - 1
    sh.put(r, 1, "Total", role="total_l")
    sh.put(r, 2, f"=SUM(B{first}:B{last})", role="total", fmt=Fmt.MONEY0)
    define_name(sh, "TotalMaturities", r, 2)
    r += 2

    r = common.section(sh, r, "Near-term refinancing risk", c1=1, c2=LAST)
    sh.put(r, 1, "Year 1 vs liquidity", role="label_b")
    sh.put(r, 2, '=IF(N(Liquidity)<=0,"Enter liquidity on the Issuer sheet to assess this",'
                 'IF(MW1>Liquidity,"High near-term refinancing risk (Year 1 maturities exceed liquidity)",'
                 'IF(MW1>0.5*Liquidity,"Medium near-term refinancing risk","Lower refinancing risk - well covered")))',
           role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1
    sh.put(r, 1, "Rule used", role="sublabel")
    sh.put(r, 2, "High if Year 1 > liquidity; Medium if Year 1 > half of liquidity; otherwise Lower.", role="note_l")
    sh.merge(r, 2, r, LAST); r += 2

    # bar chart
    cats = Reference(sh.ws, min_col=1, min_row=first, max_row=last)
    data = Reference(sh.ws, min_col=2, min_row=hdr, max_row=last)
    common.bar_chart(sh, f"D{first}", "Debt maturities by year", cats_ref=cats, data_ref=data, width=13, height=8)

    sh.freeze("A6")
    sh.col_width(1, 16)
    sh.col_width(2, 14)
    for c in range(3, LAST + 1):
        sh.col_width(c, 12)
    return sh
