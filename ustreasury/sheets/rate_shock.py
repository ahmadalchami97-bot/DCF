"""Sheet 6: Rate Shock / Scenario Analysis."""

from __future__ import annotations

from bond.config import Fmt
from .. import common

LAST = 6
SHOCKS = [-100, -50, -25, 25, 50, 100]


def build(sh, ctx):
    common.title_block(sh, "RATE SHOCK", "Estimated price impact if Treasury yields move", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "WHAT THIS SHOWS:  how the clean price would change if the yield moved up or down. The estimate uses "
        "modified duration (the straight-line effect) and then adds convexity (the curve correction).",
        "If yields RISE, Treasury prices FALL; if yields FALL, prices RISE. Longer-duration bonds move more.",
        "These are approximations from duration and convexity, not a full reprice - good for small/medium moves.",
    ], last_col=LAST)
    r += 1

    hdr = r
    for c, tx in enumerate(["Yield shock", "New est. yield", "Price change\n(duration only)",
                            "Price change\n(dur + convexity)", "Est. new clean price", "Interpretation"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c not in (6,) else "colhdr_l")
    sh.row_height(hdr, 26)
    r += 1
    for bps in SHOCKS:
        sign = "+" if bps > 0 else ""
        sh.put(r, 1, f"{sign}{bps} bps", role="label_b")
        sh.put(r, 2, f"=YTM+{bps / 10000.0}", role="formula", fmt=Fmt.PCT3)
        dy = f"({bps / 10000.0})"
        sh.put(r, 3, f"=-ModDur*{dy}*CleanPrice", role="formula", fmt=Fmt.PRICE)
        sh.put(r, 4, f"=(-ModDur*{dy}+0.5*Convexity*{dy}^2)*CleanPrice", role="formula", fmt=Fmt.PRICE)
        sh.put(r, 5, f"=CleanPrice+{sh.local(r,4)}", role="output", fmt=Fmt.PRICE)
        sh.put(r, 6, f'=IF({bps}>0,"Yields up -> price falls","Yields down -> price rises")', role="formula_l")
        r += 1
    sh.put(r, 1, "Note: change applied to the clean price using modified duration and convexity. "
                 "Convexity makes the gain on a rally slightly larger than the loss on an equal sell-off.", role="note")
    sh.merge(r, 1, r, LAST)

    sh.freeze("A6")
    sh.col_width(1, 14); sh.col_width(2, 14); sh.col_width(3, 16); sh.col_width(4, 16)
    sh.col_width(5, 18); sh.col_width(6, 30)
    return sh
