"""Sheet 6: Call analysis -- Yield to Maturity, Yield to Call, Yield to Worst."""

from __future__ import annotations

from .. import common
from ..common import cell_comment, define_name
from ..config import Fmt

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "CALL & YIELD TO WORST", "What you earn if held to maturity vs called early",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "A CALLABLE bond can be repaid early by the issuer (usually when rates fall, which is bad for you).",
        "YIELD TO CALL (YTC) uses only the cash flows up to the call date, plus the call price you receive then.",
        "YIELD TO WORST (YTW) = the lower of YTM and YTC. It is the most conservative yield you should plan on - "
        "always judge a callable bond on its YTW, not its YTM.",
    ], last_col=LAST)
    r += 1

    def row(label, name, formula, fmt, note="", role="output"):
        nonlocal r
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, formula, role=role, fmt=fmt)
        sh.merge(r, 2, r, 3)
        if name:
            define_name(sh, name, r, 2)
        if note:
            sh.put(r, 4, note, role="note_l")
            sh.merge(r, 4, r, LAST)
        r += 1

    r = common.section(sh, r, "Yields", c1=1, c2=LAST)
    row("Callable?", None, "=CallableFlag", None, role="link")
    row("Yield to maturity (YTM)", None, "=YTM", Fmt.PCT3, "Return if held all the way to maturity.", role="link")
    row("Yield to call (YTC)", "YTC",
        '=IF(CallableFlag<>"Yes","Not callable",'
        'IF(IsZero=1,(CallPrice/MktClean)^(1/YearsToCall)-1,'
        'YIELD(Settle,CallDate,CouponRate,MktClean,CallPrice,Freq,Basis)))',
        Fmt.PCT3, "Return if the bond is called on the call date at the call price.")
    cell_comment(sh, r - 1, 2, "Same yield idea as YTM, but the bond 'matures' on the call date and pays the call "
                               "price instead of face. Shows 'Not callable' when Callable = No.")
    row("Yield to worst (YTW)", "YTW", '=IF(CallableFlag<>"Yes",YTM,MIN(YTM,YTC))', Fmt.PCT3,
        "The lower of YTM and YTC. Plan on this.")
    r += 1

    r = common.section(sh, r, "Call details & interpretation", c1=1, c2=LAST)
    row("Years to call", None, "=YearsToCall", Fmt.YEARS, role="link")
    row("Call price", None, '=IF(CallableFlag<>"Yes","n/a",CallPrice)', Fmt.PRICE, role="link")
    sh.put(r, 1, "What this means", role="label_b")
    sh.put(r, 2, '=IF(CallableFlag<>"Yes","Not callable - you should receive coupons through to maturity.",'
                 'IF(YTC<YTM,"Call risk: if called, your yield drops to the YTC - this limits your upside.",'
                 '"If called you would actually earn more than to maturity, so call risk is not a concern here."))',
           role="formula_l")
    sh.merge(r, 2, r, LAST); r += 1

    sh.freeze("A6")
    sh.col_width(1, 24)
    sh.col_width(2, 13)
    sh.col_width(3, 8)
    for c in range(4, LAST + 1):
        sh.col_width(c, 14)
    return sh
