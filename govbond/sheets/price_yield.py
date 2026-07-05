"""Sheet 2: Price and Yield Calculations (yield-from-price, price-from-yield, table)."""

from __future__ import annotations

from bond.config import Fmt
from .. import common
from ..common import cell_comment, clean_at, define_name

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "PRICE & YIELD", "Work out the yield from the price, and the price from a yield",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = 7

    def result(label, name, formula, fmt, role="output", note=""):
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

    def box(lines):
        nonlocal r
        r = common.interp(sh, r, lines, last_col=LAST)

    # =================== SECTION A: YIELD FROM PRICE ===================
    r = common.section(sh, r, "Section A - Yield from Price  (enter the market price, get the yield)", c1=1, c2=LAST)
    result("Market clean price", "CleanPrice", "=MktClean", Fmt.PRICE, role="link")
    box("Clean price is the quoted price, excluding accrued interest. Above 100 = the bond trades at a PREMIUM; "
        "below 100 = a DISCOUNT. Here it is "
        "well defined by your input on the Inputs sheet.")
    result("Accrued interest", "Accrued",
           "=IF(IsZero=1,0,COUPDAYBS(Settle,Maturity,Freq,Basis)/COUPDAYS(Settle,Maturity,Freq,Basis)*CouponRate/Freq*Face)",
           Fmt.PRICE)
    cell_comment(sh, r - 1, 2, "Accrued = (days since last coupon / days in the period) x periodic coupon.")
    box("Accrued interest is the coupon the seller has earned since the last coupon date. The buyer pays it back to "
        "the seller, so it is added on top of the quoted price. It is zero for a bill / zero-coupon bond.")
    result("Dirty price", "Dirty", "=MktClean+Accrued", Fmt.PRICE)
    box("Dirty price is the ACTUAL price the buyer pays = clean price + accrued interest. This is the real cash cost.")
    result("Implied yield to maturity", "YTM",
           "=IF(IsZero=1,(Face/MktClean)^(1/YearsToMat)-1,YIELD(Settle,Maturity,CouponRate,MktClean,Face,Freq,Basis))",
           Fmt.PCT3)
    cell_comment(sh, r - 1, 2, "Coupon bonds: Excel YIELD(). Bill/zero: (Face/Price)^(1/Years)-1.")
    box("Yield to maturity (YTM) is the annual return implied by today's price if you hold to maturity and receive "
        "all payments. It is the main yield number. Remember: higher price -> lower yield, lower price -> higher yield.")
    result("Current yield", "CurrentYield", '=IF(IsZero=1,"N/A",(CouponRate*Face)/MktClean)', Fmt.PCT2)
    box("Current yield = annual coupon / clean price. It shows the coupon income relative to today's price, but it "
        "does NOT capture the capital gain or loss you get by holding to maturity. N/A for a zero-coupon bond.")
    result("Premium / discount to par", "PremDisc", "=MktClean-Face", Fmt.PRICE)
    box("Premium = price above par (100). Discount = price below par. Near 100 = near par. A discount usually means "
        "the coupon is below current yields; a premium means the coupon is above them.")
    r += 1

    # =================== SECTION B: PRICE FROM YIELD ===================
    r = common.section(sh, r, "Section B - Price from Yield  (enter a yield, get the price it implies)", c1=1, c2=LAST)
    sh.put(r, 1, "Yield to test", role="label_b")
    sh.put(r, 2, "=BenchYield", role="input", fmt=Fmt.PCT3)
    define_name(sh, "TestYield", r, 2)
    sh.put(r, 4, "Editable. Default = benchmark yield. Try your own 'fair value' yield.", role="note_l")
    sh.merge(r, 2, r, 3); sh.merge(r, 4, r, LAST); r += 1
    result("Theoretical clean price", "TheoClean", f"={clean_at('TestYield')}", Fmt.PRICE)
    result("Accrued interest", None, "=Accrued", Fmt.PRICE, role="link")
    result("Theoretical dirty price", "TheoDirty", "=TheoClean+Accrued", Fmt.PRICE, role="formula")
    result("Market clean - theoretical", "PriceDiff", "=MktClean-TheoClean", Fmt.PRICE, role="formula")
    result("Cheap / fair / expensive", "CheapFair",
           '=IF(TheoClean-MktClean>0.25,"Cheap (worth more than its price)",'
           'IF(TheoClean-MktClean<-0.25,"Expensive (worth less than its price)","Fair (close to its price)"))',
           None, role="status")
    common.traffic_light(sh, f"{common.col_letter(2)}{r-1}:{common.col_letter(2)}{r-1}", f"B{r-1}")
    box("This section shows what the price SHOULD be for the yield you type. If the theoretical price is ABOVE the "
        "market price, the bond looks a little CHEAP (you get extra yield); if BELOW, it looks EXPENSIVE. This is a "
        "simple relative check at your chosen yield - not a guaranteed recommendation.")
    r += 1

    # =================== SECTION C: PRICE-YIELD TABLE ===================
    r = common.section(sh, r, "Section C - Price-Yield Table  (theoretical clean price at different yields)",
                       c1=1, c2=LAST)
    hdr = r
    for c, tx in enumerate(["Yield scenario", "Yield", "Theoretical clean price"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c > 1 else "colhdr_l")
    sh.merge(hdr, 3, hdr, LAST)
    r += 1
    for bps in (-100, -50, -25, 0, 25, 50, 100):
        lab = "Current YTM" if bps == 0 else f"YTM {'+' if bps > 0 else '-'}{abs(bps)} bps"
        sh.put(r, 1, lab, role="label_b" if bps == 0 else "label")
        y = f"(YTM+{bps / 10000.0})"
        sh.put(r, 2, f"={y}", role="formula", fmt=Fmt.PCT3)
        sh.put(r, 3, f"={clean_at(y)}", role="output" if bps == 0 else "formula", fmt=Fmt.PRICE)
        sh.merge(r, 3, r, LAST)
        r += 1
    box("Bond prices and yields move in OPPOSITE directions: if the yield RISES, the price FALLS; if the yield FALLS, "
        "the price RISES. The size of the move depends on the bond's duration (see the Duration sheet).")

    sh.freeze("A6")
    sh.col_width(1, 26); sh.col_width(2, 13); sh.col_width(3, 12)
    for c in range(4, LAST + 1):
        sh.col_width(c, 12)
    return sh
