"""Sheet 10: Rate Shock Analysis -- what happens to the price if yields move."""

from __future__ import annotations

from bond.config import Fmt
from .. import common

LAST = 9
SHOCKS = [-100, -50, -25, 0, 25, 50, 100]


def build(sh, ctx):
    common.title_block(sh, "RATE SHOCK ANALYSIS", "What happens to the price if yields move up or down", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "This table shows the bond's interest-rate risk. If yields RISE, the bond price usually FALLS; if yields FALL, "
        "the price RISES. Longer-duration bonds move more.",
        "'Duration only' is the straight-line estimate; 'duration + convexity' adds the curve correction and is more "
        "accurate for bigger moves. The last column scales the gain/loss to your position size (if entered).",
    ], last_col=LAST)
    r += 1

    hdr = r
    for c, tx in enumerate(["Scenario", "Yield shock", "New yield", "Chg\n(duration)", "Chg\n(dur + convexity)",
                            "Est. new price", "Gain/loss\n(%)", "Gain/loss\n(position)", "Interpretation"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c != 9 else "colhdr_l")
    sh.row_height(hdr, 26)
    r += 1
    first = r
    for bps in SHOCKS:
        lab = "No change" if bps == 0 else (f"Yield falls {abs(bps)} bps" if bps < 0 else f"Yield rises {bps} bps")
        dy = f"({bps / 10000.0})"
        sh.put(r, 1, lab, role="label_b" if bps == 0 else "label")
        sh.put(r, 2, f"{'+' if bps > 0 else ''}{bps} bps", role="formula", align="c")
        sh.put(r, 3, f"=YTM+{bps / 10000.0}", role="formula", fmt=Fmt.PCT3)
        sh.put(r, 4, f"=-ModDur*{dy}*CleanPrice", role="formula", fmt=Fmt.PRICE)
        sh.put(r, 5, f"=(-ModDur*{dy}+0.5*Convexity*{dy}^2)*CleanPrice", role="formula", fmt=Fmt.PRICE)
        sh.put(r, 6, f"=CleanPrice+{sh.local(r, 5)}", role="output", fmt=Fmt.PRICE)
        sh.put(r, 7, f"=IFERROR({sh.local(r, 5)}/CleanPrice,0)", role="formula", fmt=Fmt.PCT2)
        sh.put(r, 8, f'=IF(N(PosSize)=0,"-",{sh.local(r, 5)}*PosSize/100)', role="formula", fmt=Fmt.MONEY)
        sh.put(r, 9, f'=IF({bps}<0,"Yields fall -> price rises (gain)",IF({bps}>0,"Yields rise -> price falls (loss)","No change"))',
               role="formula_l")
        r += 1
    down_row, up_row = first, r - 1
    r += 1

    r = common.section(sh, r, "Conclusion", c1=1, c2=LAST)
    sh.put(r, 1, "Biggest upside", role="label_b")
    sh.put(r, 2, f'="Yields fall 100 bps -> price ~ "&TEXT({sh.local(down_row,6)},"0.00")&" (+"&TEXT({sh.local(down_row,7)},"0.0%")&")"',
           role="formula_l"); sh.merge(r, 2, r, LAST); r += 1
    sh.put(r, 1, "Biggest downside", role="label_b")
    sh.put(r, 2, f'="Yields rise 100 bps -> price ~ "&TEXT({sh.local(up_row,6)},"0.00")&" ("&TEXT({sh.local(up_row,7)},"0.0%")&")"',
           role="formula_l"); sh.merge(r, 2, r, LAST); r += 1
    sh.put(r, 1, "What this tells you", role="label_b")
    sh.put(r, 2, '=IF(ModDur>7,"This is a longer-duration bond - rising yields hurt the price a lot. Rate risk is the main risk.",'
                 '"Duration is moderate - the price moves with yields, but not violently.")', role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1

    sh.freeze("A6")
    sh.col_width(1, 18); sh.col_width(2, 11); sh.col_width(3, 10); sh.col_width(4, 11)
    sh.col_width(5, 14); sh.col_width(6, 13); sh.col_width(7, 10); sh.col_width(8, 13); sh.col_width(9, 28)
    return sh
