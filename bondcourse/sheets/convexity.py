"""Sheet 9: Convexity -- why duration is not perfect."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import define_name

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "CONVEXITY", "Why duration is not perfect - and why that is good for you", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "Duration gives a STRAIGHT-LINE estimate of how the price changes when yields move. But bond prices actually "
        "move in a CURVE, not a straight line. CONVEXITY measures that curve and improves the estimate, especially "
        "when yields move a lot.",
        "Keep it simple: convexity is a small 'bonus' correction on top of duration.",
    ], last_col=LAST)
    r += 1

    def row(label, name, formula, fmt, role="output"):
        nonlocal r
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, formula, role=role, fmt=fmt)
        sh.merge(r, 2, r, 3)
        if name:
            define_name(sh, name, r, 2)
        r += 1

    r = common.section(sh, r, "Convexity", c1=1, c2=LAST)
    row("Convexity", "ConvexityView", "=Convexity", Fmt.RATIO, role="result")
    r = common.interp(sh, r, [
        "For normal fixed-rate government bonds, convexity is POSITIVE, and positive convexity is generally GOOD for "
        "you. It means the bond gains slightly MORE when yields fall and loses slightly LESS when yields rise than "
        "duration alone would predict."], last_col=LAST)

    # a simple worked comparison for a +100 bps move
    r = common.section(sh, r, "See it: estimate a 1% (100 bps) yield RISE", c1=1, c2=LAST)
    row("Price change - duration only", None, "=-ModDur*0.01*CleanPrice", Fmt.PRICE, role="formula")
    row("Price change - duration + convexity", None, "=(-ModDur*0.01+0.5*Convexity*0.01^2)*CleanPrice", Fmt.PRICE,
        role="output")
    r = common.interp(sh, r, [
        "Both estimate the price drop if yields rise 1%. The 'duration only' number is the straight-line guess; the "
        "'duration + convexity' number is a bit less negative - that smaller loss is the benefit of positive "
        "convexity. On a yield FALL, convexity makes the gain a bit bigger."], last_col=LAST)

    sh.freeze("A6")
    sh.col_width(1, 30); sh.col_width(2, 14); sh.col_width(3, 8)
    for c in range(4, LAST + 1):
        sh.col_width(c, 14)
    return sh
