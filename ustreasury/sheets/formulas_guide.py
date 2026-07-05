"""Sheet 10: Formula & Concept Explanations -- full beginner explanations.

Each concept is a small block: the formula, a plain-English explanation, why it
matters for a US Treasury analyst, how to read the result, and a simple example.
"""

from __future__ import annotations

from .. import common

LAST = 10

# (concept, formula, plain-English, why it matters, how to interpret, example)
CONCEPTS = [
    ("Clean price", "The quoted market price (per 100 face)",
     "Clean price is the quoted market price of the bond. It does not include the interest that has built up since "
     "the last coupon.",
     "It is what you compare across bonds and what screens and brokers show.",
     "Above 100 = premium, below 100 = discount.",
     "A note quoted at 96.50 has a clean price of 96.50 per 100 of face value."),
    ("Dirty price", "Dirty price = clean price + accrued interest",
     "Dirty price is the actual amount the buyer pays, because it includes the accrued interest owed to the seller.",
     "It is the real cash cost of buying the bond - the amount that changes hands on settlement.",
     "Always a bit higher than the clean price between coupon dates (equal to it right after a coupon).",
     "Clean 96.50 + accrued 0.36 = dirty 96.86 - you pay 96.86."),
    ("Accrued interest", "(days since last coupon / days in period) x periodic coupon",
     "Accrued interest is the slice of the next coupon that the seller has already earned by holding the bond, and "
     "which you reimburse when you buy.",
     "It explains why you pay more than the quoted price, and it is zero for a Treasury Bill (no coupons).",
     "Grows a little each day and resets to zero right after each coupon is paid.",
     "Halfway through a semiannual period on a 4% coupon: about half of 2.0 = ~1.0 per 100."),
    ("Yield to maturity (YTM)", "The rate that makes PV of cash flows = price (Excel YIELD)",
     "Yield to maturity is the annual return implied by the bond's current price if you hold it to maturity and "
     "receive all payments as expected.",
     "It is the single best summary of the return you lock in today - the main number analysts compare.",
     "Higher price means lower YTM, and lower price means higher YTM. It assumes you hold to maturity.",
     "A note at a discount (below 100) has a YTM above its coupon rate."),
    ("Current yield", "Annual coupon / clean price",
     "Current yield is just the annual coupon divided by the price - a quick snapshot of the income you get.",
     "It shows the cash income yield, but it ignores any gain or loss versus par and the timing of cash flows.",
     "Only a rough guide; YTM is the fuller measure. It is N/A for a Treasury Bill (no coupon).",
     "A 4% coupon bond priced at 96.50 has a current yield of 4 / 96.50 = ~4.15%."),
    ("Premium / discount to par", "Clean price - 100",
     "Whether the bond trades above par (premium) or below par (discount).",
     "It tells you at a glance whether the coupon is above or below current market yields.",
     "Premium: coupon is higher than the yield. Discount: coupon is lower than the yield.",
     "Price 102 = 2-point premium; price 96.50 = 3.50-point discount."),
    ("Macaulay duration", "sum(time x PV) / sum(PV)  (Excel DURATION)",
     "Macaulay duration is the weighted-average time it takes to receive the bond's cash flows. For a zero-coupon "
     "bond it is close to the time to maturity because all the cash is received at the end; for a coupon bond it is "
     "usually shorter than maturity because some cash arrives earlier through coupons.",
     "It is the foundation of interest-rate risk and a quick sense of how long your money is tied up.",
     "Measured in years. Longer duration = the bond's cash is, on average, further away.",
     "A 10-year Treasury note might have a Macaulay duration of ~7.5 years."),
    ("Modified duration", "Macaulay duration / (1 + yield/2)  (Excel MDURATION)",
     "Modified duration shows the approximate percentage price change for a 1% (100 bps) move in yield. If modified "
     "duration is 5, then a 1% rise in yield would reduce the price by about 5%, before considering convexity.",
     "It is the main interest-rate risk number - how much price you can gain or lose when rates move.",
     "Bigger modified duration = more price risk. Longer bonds have larger modified duration.",
     "Modified duration 7.4 -> a 1% yield rise cuts the price by roughly 7.4%."),
    ("Convexity", "sum(CF x t x (t+1)/(1+y/2)^(t+2)) / (price x 4)",
     "Convexity measures how much the bond's duration changes when yields move. Duration gives a straight-line "
     "estimate of price sensitivity, but bond prices do not move in a perfect straight line. Convexity improves the "
     "estimate, especially when yields move a lot. For normal fixed-rate US Treasuries, convexity is usually "
     "positive, meaning the bond gains a bit more when yields fall and loses a bit less when yields rise compared "
     "with duration-only estimates.",
     "It makes your price-change estimates more accurate for larger rate moves, and it is a (small) plus for holders.",
     "Positive convexity is good for you. It matters most for big yield moves and long bonds.",
     "For a +/-100 bps move, duration-only under-states the gain on the rally and over-states the loss on the sell-off."),
    ("DV01", "Modified duration x dirty price x 0.0001",
     "DV01 shows the approximate price change for a 1 basis-point (0.01%) move in yield. If DV01 is 45, then a 1 bp "
     "rise in yield would reduce the bond value by about 45, while a 1 bp fall would increase it by about 45. It "
     "turns duration risk into money terms.",
     "It converts abstract duration into a concrete price/dollar risk per 1 bp - useful for sizing and hedging.",
     "Quoted as a positive number. Bigger DV01 = more price risk per basis point.",
     "DV01 of 0.07 per 100 face means ~0.07 price move for each 1 bp change in yield."),
    ("Rate shock analysis", "price change ~ -Modified x (dy) + 0.5 x convexity x (dy)^2",
     "A rate shock estimates how the price would change if the yield jumped up or down by a set amount, using "
     "duration (the straight-line part) plus convexity (the curve correction).",
     "It stress-tests the bond so you can see the downside if rates rise and the upside if they fall.",
     "Yields up -> price down; yields down -> price up. Longer-duration bonds move more.",
     "+100 bps on a 7.4-duration bond: roughly -7.4% from duration, softened a little by convexity."),
    ("Yield curve", "Treasury yields plotted by maturity (3m, 2y, 5y, 10y, 30y)",
     "The yield curve shows the yield you can earn at different maturities. It is the map of interest rates across time.",
     "It tells you whether longer bonds pay you more (normal) and where your bond sits versus other maturities.",
     "Normal = upward-sloping (longer = higher yield). Flat = roughly level.",
     "If the 2y is 4.1% and the 10y is 4.5%, the curve is normal and upward-sloping."),
    ("Inverted yield curve", "Short-term yields higher than long-term yields (e.g. 2y > 10y)",
     "An inverted curve is when short maturities yield MORE than long maturities - the opposite of normal.",
     "It is watched closely because inversions have often (not always) preceded recessions.",
     "Inverted (downward-sloping) can signal that markets expect rate cuts / a slowdown.",
     "If the 2y is 4.6% and the 10y is 4.3%, the curve is inverted by 30 bps."),
    ("Treasury bill / zero-coupon bond", "Yield = (Face / Price)^(1/Years) - 1",
     "A Treasury Bill (or any zero-coupon bond) pays no coupons. You buy it below face value and get 100 back at "
     "maturity; the whole return is the discount.",
     "Bills are short, simple and very liquid - a common place to park cash with little rate risk.",
     "Accrued interest is zero, and the duration is essentially the time to maturity.",
     "Buy a 1-year bill at 96, get 100 at maturity -> return of about 4.2%."),
    ("Benchmark Treasury yield", "The yield of a similar-maturity Treasury you compare against",
     "The benchmark yield is the reference rate for a bond of similar maturity - usually the on-the-run (most recent) "
     "Treasury.",
     "It is the yardstick for judging whether your bond's yield is high, low or fair for its maturity.",
     "Compare your bond's YTM to this benchmark to see if you are paid more or less.",
     "If the 10y benchmark is 4.30% and your note yields 4.48%, you earn 18 bps more."),
    ("Spread versus benchmark", "Spread = YTM - benchmark yield  (in bps = x 10000)",
     "The spread is the extra yield your bond offers over the benchmark Treasury of similar maturity.",
     "For a Treasury it is usually small; a positive spread can mean the bond is a touch cheap (e.g. off-the-run).",
     "Positive = you earn more than the benchmark; negative = you earn less.",
     "A +18 bps spread means 0.18% more yield than the benchmark."),
    ("Investment attractiveness score", "Total of 5 simple category scores, out of 10",
     "A simple, transparent score that adds up points for yield, low duration risk, low price sensitivity, a helpful "
     "curve, and Treasury liquidity. It is a starting point, not a personalised recommendation.",
     "It gives a consistent, explainable first read on whether a bond looks attractive - without pretending to know "
     "your situation.",
     "8-10 = Attractive, 5-7 = Neutral, 0-4 = Not Attractive. The analyst can override it.",
     "A bond scoring 8/10 (good yield, moderate duration, liquid) shows as 'Attractive'."),
    ("Buy / Hold / Avoid recommendation", "A manual analyst decision",
     "The final trading call. The model gives hints and an attractiveness score, but the Buy/Hold/Avoid decision is "
     "left to you.",
     "It keeps a human in the loop - the model informs the decision but does not make it.",
     "Combine the attractiveness view, your rate outlook and your own constraints to decide.",
     "Attractive score + you expect yields to fall -> you might lean Buy; you still decide."),
]


def build(sh, ctx):
    common.title_block(sh, "FORMULA & CONCEPT EXPLANATIONS",
                       "Every key idea in plain English - for a beginner bond analyst", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "Read this once and you can understand every number in the workbook. For each concept you get the formula, "
        "a simple explanation, why a US Treasury analyst cares, how to read it, and a quick example.",
    ], last_col=LAST)
    r += 1

    def field(label, text, role="note_l", height_per=34):
        nonlocal r
        sh.put(r, 1, label, role="sublabel")
        sh.put(r, 2, text, role=role)
        sh.merge(r, 2, r, LAST)
        sh.row_height(r, max(15, 13 + 12 * (len(text) // 95)))
        r += 1

    for concept, formula, plain, why, interp, example in CONCEPTS:
        r = common.section(sh, r, concept, c1=1, c2=LAST)
        field("Formula", formula, role="formula_l")
        field("In plain English", plain)
        field("Why it matters", why)
        field("How to interpret", interp)
        if example:
            field("Example", example)
        r += 1

    sh.freeze("A6")
    sh.col_width(1, 16)
    for c in range(2, LAST + 1):
        sh.col_width(c, 12)
    return sh
