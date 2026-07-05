"""Sheet 18: Limitations / Future Upgrades -- what this simple course does not cover."""

from __future__ import annotations

from .. import common
from ..config import DISCLAIMER, EXCLUDED, FUTURE_UPGRADES

LAST = 8


def build(sh, ctx):
    common.title_block(sh, "LIMITATIONS / FUTURE UPGRADES", "What this simple beginner workbook does not cover",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "This workbook is intentionally simple: one plain government bond (a fixed-coupon note / bond, or a zero-coupon "
        "bill). The items below are left out on purpose - to keep it correct, transparent and easy to learn from.",
        "As you grow more confident, the second list shows sensible next steps you could add later.",
    ], last_col=LAST)
    r += 1

    r = common.section(sh, r, "Not covered in this version (kept simple on purpose)", c1=1, c2=LAST)
    for item in EXCLUDED:
        sh.put(r, 1, "-  " + item, role="note_l"); sh.merge(r, 1, r, LAST); r += 1
    r += 1

    r = common.section(sh, r, "Things this workbook assumes", c1=1, c2=LAST)
    for item in [
        "The bond pays fixed coupons (or is a zero) and repays its face value in full at maturity.",
        "The government does not default and does not call the bond early.",
        "You enter one market clean price; the yield is implied from it (or you compare to a yield you type).",
        "One flat yield to maturity is used to discount every cash flow (no full curve of rates).",
        "Prices are quoted per 100 of face value.",
    ]:
        sh.put(r, 1, "-  " + item, role="note_l"); sh.merge(r, 1, r, LAST); r += 1
    r += 1

    r = common.section(sh, r, "Possible future upgrades (when you are ready)", c1=1, c2=LAST)
    for item in FUTURE_UPGRADES:
        sh.put(r, 1, "-  " + item, role="note_l"); sh.merge(r, 1, r, LAST); r += 1
    r += 1

    common.interp(sh, r, [DISCLAIMER], last_col=LAST, title="In short")

    sh.col_width(1, 30)
    for c in range(2, LAST + 1):
        sh.col_width(c, 12)
    return sh
