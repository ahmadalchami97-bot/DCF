"""Sheet 8: DV01 -- how much money do I gain or lose per 1 basis point?"""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import cell_comment, define_name

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "DV01", "How much money do I gain or lose if the yield moves 1 basis point?",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "DV01 means 'Dollar Value of 1 basis point'. It tells you how much the bond's value changes if the yield "
        "moves by 0.01%. It turns interest-rate risk into MONEY terms.",
        "Basis points:  1 bp = 0.01%.   10 bps = 0.10%.   100 bps = 1.00%.",
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

    def box(lines):
        nonlocal r
        r = common.interp(sh, r, lines, last_col=LAST)

    r = common.section(sh, r, "DV01", c1=1, c2=LAST)
    row("DV01 (per 100 face)", "DV01", "=ModDur*Dirty*0.0001", Fmt.NUM4, role="result")
    cell_comment(sh, r - 1, 2, "DV01 = Modified duration x Dirty price x 0.0001.")
    box(["What it means: the price change for a 1 bp yield move, per 100 of face value. Example: if DV01 is 0.07, a "
         "1 bp RISE in yield lowers the price by about 0.07 per 100 face, and a 1 bp FALL raises it by about 0.07.",
         "Interpretation: HIGHER DV01 = bigger money risk for a small yield move. It is always quoted as a positive "
         "number (the size of the risk)."])
    row("DV01 for your position", "DV01Pos", '=IF(N(PosSize)=0,"Enter position size on Inputs",DV01*PosSize/100)',
        Fmt.MONEY, role="result")
    box(["This scales DV01 up to the size you actually hold. Because DV01 is per 100 face, we multiply by "
         "(position size / 100). Example: DV01 0.07 per 100 and a 100,000 face position -> about 0.07 x 1,000 = ~70 "
         "of value change per 1 bp."])

    sh.freeze("A6")
    sh.col_width(1, 26); sh.col_width(2, 15); sh.col_width(3, 8)
    for c in range(4, LAST + 1):
        sh.col_width(c, 14)
    return sh
