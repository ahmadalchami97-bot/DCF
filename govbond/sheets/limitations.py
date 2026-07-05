"""Sheet 12: Limitations / Future Upgrades."""

from __future__ import annotations

from .. import common
from ..config import DISCLAIMER, EXCLUDED, FUTURE_UPGRADES

LAST = 8


def build(sh, ctx):
    common.title_block(sh, "LIMITATIONS / FUTURE UPGRADES", "What this simple model does not cover", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "This model is intentionally simple: one plain government bond (fixed-coupon note/bond or zero-coupon bill). "
        "The items below are deliberately left out to keep it correct and easy to audit.",
    ], last_col=LAST)
    r += 1

    r = common.section(sh, r, "Not covered in this version", c1=1, c2=LAST)
    for item in EXCLUDED:
        sh.put(r, 1, "-  " + item, role="note_l"); sh.merge(r, 1, r, LAST); r += 1
    r += 1

    r = common.section(sh, r, "Possible future upgrades", c1=1, c2=LAST)
    for item in FUTURE_UPGRADES:
        sh.put(r, 1, "-  " + item, role="note_l"); sh.merge(r, 1, r, LAST); r += 1
    r += 1

    common.interp(sh, r, [DISCLAIMER], last_col=LAST, title="In short")

    sh.col_width(1, 30)
    for c in range(2, LAST + 1):
        sh.col_width(c, 12)
    return sh
