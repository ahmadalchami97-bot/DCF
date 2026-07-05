"""Sheet 16: Formula Explanations -- every formula in the workbook, in plain English."""

from __future__ import annotations

from .. import common

LAST = 10

# (name, the Excel formula used, what it does, how to read / interpret the answer)
FORMULAS = [
    ("Years to maturity",
     "=YEARFRAC(Settle, Mat, Basis)",
     "Counts the time in years between your settlement date and the maturity date, using the chosen day-count basis.",
     "Bigger = longer until you are repaid = usually more interest-rate risk."),
    ("Number of coupons left",
     "=COUPNUM(Settle, Mat, Freq, Basis)",
     "Counts how many coupon payments are still to come between settlement and maturity.",
     "Each one is a future cash flow the workbook discounts back to today."),
    ("Accrued interest",
     "=COUPDAYBS(...) / COUPDAYS(...) * Cpn/Freq * Face",
     "Takes the fraction of the current coupon period that has already passed and multiplies it by one coupon. "
     "COUPDAYBS = days since the last coupon; COUPDAYS = days in the whole period.",
     "This is the slice of the next coupon you must pay back to the seller. Zero for a bill."),
    ("Dirty price",
     "=MktClean + Accrued",
     "Adds accrued interest to the quoted clean price to get the actual cash you pay.",
     "Always a little above the clean price between coupon dates."),
    ("Yield to maturity (coupon bond)",
     "=YIELD(Settle, Mat, Cpn, MktClean, Face, Freq, Basis)",
     "Solves for the single annual return that makes the price fair, given all the future coupons and the repayment.",
     "Higher when the price is lower. This is your return if you hold to maturity."),
    ("Yield to maturity (zero-coupon)",
     "=(Face / MktClean)^(1 / YrsToMat) - 1",
     "For a bill with no coupons, the yield is just the growth rate from today's price up to the face value.",
     "One payment only, so no coupon reinvestment to worry about."),
    ("Current yield",
     "=Cpn * Face / MktClean",
     "Divides the annual coupon cash by the current price - a quick income snapshot.",
     "Ignores the pull-to-par gain or loss, so YTM is the fuller measure. N/A for a zero."),
    ("Price from a yield (coupon bond)",
     "=PRICE(Settle, Mat, Cpn, yield, Face, Freq, Basis)",
     "The reverse of YIELD: given a yield, it returns the clean price that yield implies.",
     "Type a yield you think is fair and compare the price it gives to the market price."),
    ("Price from a yield (zero-coupon)",
     "=Face / (1 + yield)^YrsToMat",
     "Discounts the single face-value payment back to today at the yield you choose.",
     "The only cash flow is the face value at maturity."),
    ("Macaulay duration",
     "=DURATION(Settle, Mat, Cpn, YTM, Freq, Basis)",
     "The weighted-average time (in years) to receive the bond's cash flows, each weighted by its present value.",
     "Longer = your money comes back later on average. A zero's duration equals its maturity."),
    ("Modified duration",
     "=MDURATION(Settle, Mat, Cpn, YTM, Freq, Basis)",
     "Macaulay duration divided by (1 + yield/frequency). It estimates the % price change for a 1% yield move.",
     "If it is 7, a 1% rise in yield cuts the price about 7%. Bigger = more rate risk."),
    ("DV01 (per 100 face)",
     "=ModDur * Dirty * 0.0001",
     "Turns modified duration into money: the price change for a 1 basis-point (0.01%) move in yield.",
     "Always positive; a bigger DV01 means bigger profit or loss per basis point."),
    ("Convexity (from the schedule)",
     "=SUM( CF x t x (t+1) / (1+y/f)^(t+2) ) / (Price x f^2)",
     "Measures how duration itself changes as yields move - the curve that duration (a straight line) misses.",
     "Positive for normal bonds: it adds to gains when yields fall and softens losses when yields rise."),
    ("Rate-shock price change",
     "=(-ModDur x dy + 0.5 x Convexity x dy^2) x Price",
     "Estimates the price change for a yield move 'dy' using duration plus the convexity correction.",
     "The duration part is the straight-line guess; convexity makes it more accurate for big moves."),
    ("Spread over benchmark",
     "=YTM - BenchYield",
     "Subtracts a similar-maturity government benchmark yield from your bond's yield.",
     "Positive = you earn a little more than the benchmark. For governments it is usually small."),
    ("Curve shape",
     '=IF(Y10Y-Y2Y>0.001,"Normal", IF(Y10Y-Y2Y<-0.001,"Inverted","Flat"))',
     "Compares the 10-year and 2-year yields to label the curve.",
     "Normal = up-sloping (usual); Inverted = down-sloping (watched as a recession signal); Flat = close together."),
    ("Attractiveness score",
     "=SUM of the five category points (yield, duration, DV01, curve, outlook fit)",
     "Adds simple, visible points across five categories to a total out of 10.",
     "8-10 = Attractive, 5-7 = Neutral, 0-4 = Not Attractive. Fully editable and overridable."),
]


def build(sh, ctx):
    common.title_block(sh, "FORMULA EXPLANATIONS", "Every formula in the workbook, explained in plain English",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "Curious what a cell actually calculates? This sheet lists each formula the workbook uses, what it does, and "
        "how to read the answer. Nothing here is hidden - you can open any cell and see the same formula.",
    ], last_col=LAST)
    r += 1

    hdr = r
    for c, tx in enumerate(["Concept", "Formula used", "What it does", "How to read it"], 1):
        sh.put(hdr, c, tx, role="colhdr_l")
    sh.merge(hdr, 3, hdr, 6)
    sh.merge(hdr, 7, hdr, LAST)
    sh.row_height(hdr, 16)
    r += 1

    for name, excel, does, read in FORMULAS:
        # Strip any leading "=" so the formula is shown as descriptive TEXT, not
        # evaluated by Excel (the column header already says "Formula used").
        display = excel[1:] if excel.startswith("=") else excel
        sh.put(r, 1, name, role="label_b")
        sh.put(r, 2, display, role="formula_l")
        sh.put(r, 3, does, role="note_l"); sh.merge(r, 3, r, 6)
        sh.put(r, 7, read, role="note_l"); sh.merge(r, 7, r, LAST)
        sh.row_height(r, max(28, 13 + 12 * (max(len(does) // 42, len(read) // 34))))
        r += 1

    sh.freeze("A7")
    sh.col_width(1, 22); sh.col_width(2, 34)
    for c in range(3, LAST + 1):
        sh.col_width(c, 11)
    return sh
