"""Sheet 6: Rate Shock Analysis -- price impact if yields move."""

from __future__ import annotations

from bond.config import Fmt
from .. import common

LAST = 8
SHOCKS = [-100, -50, -25, 0, 25, 50, 100]


def build(sh, ctx):
    common.title_block(sh, "RATE SHOCK ANALYSIS", "What happens to the price if yields move up or down", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "This table is the bond's interest-rate sensitivity in action. If yields RISE, the price usually FALLS; if "
        "yields FALL, the price RISES. Longer-duration bonds move more.",
        "'Duration only' is the straight-line estimate; 'duration + convexity' adds the curve correction and is more "
        "accurate for bigger moves.",
    ], last_col=LAST)
    r += 1

    hdr = r
    for c, tx in enumerate(["Scenario", "Yield shock", "New yield", "Price chg\n(duration)",
                            "Price chg\n(dur + convexity)", "Est. new clean price", "Gain / loss\n(%)",
                            "Interpretation"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c != 8 else "colhdr_l")
    sh.row_height(hdr, 26)
    r += 1
    first = r
    for bps in SHOCKS:
        if bps < 0:
            lab = f"Yield falls {abs(bps)} bps"
        elif bps > 0:
            lab = f"Yield rises {bps} bps"
        else:
            lab = "No change"
        dy = f"({bps / 10000.0})"
        sh.put(r, 1, lab, role="label_b" if bps == 0 else "label")
        sh.put(r, 2, f"{'+' if bps > 0 else ''}{bps} bps", role="formula", align="c")
        sh.put(r, 3, f"=YTM+{bps / 10000.0}", role="formula", fmt=Fmt.PCT3)
        sh.put(r, 4, f"=-ModDur*{dy}*CleanPrice", role="formula", fmt=Fmt.PRICE)
        sh.put(r, 5, f"=(-ModDur*{dy}+0.5*Convexity*{dy}^2)*CleanPrice", role="formula", fmt=Fmt.PRICE)
        sh.put(r, 6, f"=CleanPrice+{sh.local(r, 5)}", role="output", fmt=Fmt.PRICE)
        sh.put(r, 7, f"=IFERROR({sh.local(r, 5)}/CleanPrice,0)", role="formula", fmt=Fmt.PCT2)
        sh.put(r, 8, f'=IF({bps}<0,"Yields fall -> price rises (gain)",IF({bps}>0,"Yields rise -> price falls (loss)","No change"))',
               role="formula_l")
        r += 1
    down_row, up_row = first, r - 1  # -100 bps (biggest gain) and +100 bps (biggest loss)
    r += 1

    r = common.section(sh, r, "Conclusion", c1=1, c2=LAST)
    sh.put(r, 1, "Biggest upside", role="label_b")
    sh.put(r, 2, f'="Yields fall 100 bps -> price about "&TEXT({sh.local(down_row,6)},"0.00")&" (+"&TEXT({sh.local(down_row,7)},"0.0%")&")"',
           role="formula_l"); sh.merge(r, 2, r, LAST); r += 1
    sh.put(r, 1, "Biggest downside", role="label_b")
    sh.put(r, 2, f'="Yields rise 100 bps -> price about "&TEXT({sh.local(up_row,6)},"0.00")&" ("&TEXT({sh.local(up_row,7)},"0.0%")&")"',
           role="formula_l"); sh.merge(r, 2, r, LAST); r += 1
    sh.put(r, 1, "Main risk", role="label_b")
    sh.put(r, 2, '=IF(ModDur>7,"Rising yields - this is a longer-duration bond, so a yield rise hurts the price a lot.",'
                 '"Rising yields would lower the price, but the duration here is moderate.")', role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1
    r = common.interp(sh, r, [
        "How to read it: the '+100 bps' row is your downside if rates rise; the '-100 bps' row is your upside if rates "
        "fall. Notice the gain on a fall is slightly bigger than the loss on an equal rise - that is positive convexity.",
    ], last_col=LAST)

    sh.freeze("A6")
    sh.col_width(1, 20); sh.col_width(2, 11); sh.col_width(3, 11); sh.col_width(4, 12)
    sh.col_width(5, 15); sh.col_width(6, 16); sh.col_width(7, 11); sh.col_width(8, 30)
    return sh
