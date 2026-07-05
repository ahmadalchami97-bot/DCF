"""Sheet 10: Explanations -- every concept in plain beginner English."""

from __future__ import annotations

from .. import common

LAST = 10

CONCEPTS = [
    ("Clean price", "The quoted market price (per 100 face)",
     "The price you see quoted. It leaves out the interest that has built up since the last coupon.",
     "It is what you compare across bonds and what screens show.",
     "Above 100 = premium; below 100 = discount.",
     "A note quoted at 96.50 has a clean price of 96.50."),
    ("Dirty price", "Dirty price = clean price + accrued interest",
     "The actual cash you pay, because it includes the accrued interest owed to the seller.",
     "It is the true cost of buying the bond.",
     "Always a bit above the clean price between coupons.",
     "Clean 96.50 + accrued 0.36 = dirty 96.86."),
    ("Accrued interest", "(days since last coupon / days in period) x periodic coupon",
     "The slice of the next coupon the seller has already earned and you pay back.",
     "It explains why you pay more than the quoted price; it is zero for a bill.",
     "Grows daily, resets to zero right after each coupon.",
     "Halfway through a period on a 4% coupon: about 1.0 per 100."),
    ("Yield to maturity (YTM)", "The rate that makes PV of cash flows = price",
     "The annual return you earn if you hold to maturity and receive all payments.",
     "It is the single best summary of the return you lock in today.",
     "Higher price -> lower YTM; lower price -> higher YTM.",
     "A bond at a discount has a YTM above its coupon."),
    ("Current yield", "Annual coupon / clean price",
     "Just the coupon divided by the price - a quick income snapshot.",
     "It shows cash income but ignores gain/loss to maturity.",
     "Only a rough guide; YTM is fuller. N/A for a zero-coupon bond.",
     "4% coupon at 96.50 -> current yield ~4.15%."),
    ("Premium / discount to par", "Clean price - 100",
     "Whether the bond trades above par (premium) or below par (discount).",
     "It tells you at a glance if the coupon is above or below market yields.",
     "Coupon above yield -> premium; coupon below yield -> discount.",
     "Price 96.50 = a 3.50-point discount."),
    ("Price-yield relationship", "Price and yield move in opposite directions",
     "When the market yield goes up, the bond's price goes down, and vice versa.",
     "It is the core of bond risk - it is why rising rates hurt bond prices.",
     "Rising yields = falling prices; falling yields = rising prices.",
     "If your bond's yield rises 1%, a 7-duration bond loses about 7%."),
    ("Macaulay duration", "sum(time x PV) / sum(PV)",
     "The weighted-average time to receive the bond's cash flows. For a zero it is close to the time to maturity; "
     "for a coupon bond it is a bit shorter than maturity because coupons come earlier.",
     "It is the base of interest-rate risk and a sense of how long your money is tied up.",
     "Measured in years; longer = cash is, on average, further away.",
     "A 10-year note might have a Macaulay duration of ~7.5 years."),
    ("Modified duration", "Macaulay duration / (1 + yield/frequency)",
     "The approximate % price change for a 1% (100 bps) move in yield. If it is 5, a 1% yield rise cuts the price ~5%.",
     "It is the main interest-rate risk number.",
     "Bigger = more price risk; longer bonds have larger modified duration.",
     "Modified duration 7.4 -> a 1% yield rise cuts the price ~7.4%."),
    ("Convexity", "sum(CF x t x (t+1)/(1+y/f)^(t+2)) / (price x f^2)",
     "How the bond's sensitivity itself changes as yields move. Duration is a straight line; prices curve, and "
     "convexity captures the curve.",
     "It makes price-change estimates more accurate for bigger moves and is a small plus for you.",
     "Positive for normal bonds; helps on rallies, cushions sell-offs.",
     "On +/-100 bps, the gain on the rally beats the loss on the sell-off a little."),
    ("DV01", "Modified duration x dirty price x 0.0001",
     "The money price change for a 1 basis-point (0.01%) yield move. If DV01 is 45, a 1 bp move changes the value by "
     "about 45.",
     "It turns rate risk into money terms - useful for sizing and hedging.",
     "Quoted positive; bigger DV01 = bigger P&L per basis point.",
     "DV01 0.07 per 100 -> ~0.07 price move per 1 bp."),
    ("Rate shock analysis", "price change ~ -Modified x (dy) + 0.5 x convexity x (dy)^2",
     "A what-if that estimates the price if the yield jumps up or down by a set amount, using duration plus convexity.",
     "It stress-tests the bond so you see the downside if rates rise and the upside if they fall.",
     "Yields up -> price down; longer duration -> bigger move.",
     "+100 bps on a 7.4-duration bond: roughly -7% from duration, softened by convexity."),
    ("Yield curve", "Government yields plotted by maturity",
     "The yield curve shows government bond yields across different maturities - the map of rates over time.",
     "It shows whether longer bonds pay more and where your bond sits.",
     "Compare short vs long yields to read its shape.",
     "2y at 4.1% and 10y at 4.5% -> an upward (normal) curve."),
    ("Normal yield curve", "Long-term yields higher than short-term yields",
     "A normal curve slopes up: you are paid more to lend for longer.",
     "It is the usual, healthy shape and means positive term premium.",
     "Upward-sloping = normal.",
     "3m 4.3%, 2y 4.1%... no; normal example: 2y 4.0%, 10y 4.6%."),
    ("Inverted yield curve", "Short-term yields higher than long-term yields",
     "An inverted curve slopes down - short maturities yield more than long ones.",
     "It is watched because inversions have often preceded recessions.",
     "Downward-sloping can signal expected rate cuts / a slowdown.",
     "2y 4.6% and 10y 4.3% -> inverted by 30 bps."),
    ("Flat yield curve", "Short and long yields are close together",
     "A flat curve means short-term and long-term yields are about the same.",
     "It often signals uncertainty or a turning point in rate expectations.",
     "Roughly level across maturities = flat.",
     "2y 4.3% and 10y 4.35% -> basically flat."),
    ("Benchmark yield", "The yield of a similar-maturity government bond",
     "The reference yield for a bond of similar maturity - usually the most recent (on-the-run) issue.",
     "It is the yardstick for judging whether your bond's yield is high, low or fair.",
     "Compare your YTM to it to see if you are paid more or less.",
     "10y benchmark 4.30%, your note 4.48% -> 18 bps more."),
    ("Spread over benchmark", "Spread = YTM - benchmark yield",
     "The extra yield your bond offers over a similar-maturity benchmark.",
     "For governments it is usually small; a positive spread can mean the bond is a touch cheap.",
     "Positive = you earn more than the benchmark; negative = less.",
     "A +18 bps spread = 0.18% more yield than the benchmark."),
    ("Investment attractiveness", "A simple score out of 10 across 5 categories",
     "A transparent score that adds points for yield, low duration risk, low DV01, a helpful curve, and fit with your "
     "rate outlook.",
     "It gives a consistent first read on whether the yield is worth the risk - without pretending to know you.",
     "8-10 = Attractive, 5-7 = Neutral, 0-4 = Not Attractive; the analyst can override it.",
     "8/10 (good yield, moderate duration) -> 'Attractive'."),
    ("Buy / Hold / Avoid recommendation", "A manual analyst decision",
     "The final trading call. The model gives hints and a score, but you make the Buy/Hold/Avoid decision.",
     "It keeps a human in the loop - the model informs, it does not decide.",
     "Buy = attractive; Hold = acceptable; Avoid = not enough return for the risk.",
     "Attractive score + you expect yields to fall -> you might lean Buy; you still choose."),
]


def build(sh, ctx):
    common.title_block(sh, "EXPLANATIONS", "Every concept in plain English - for a beginner government bond analyst",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "Read this once and you can understand every number in the workbook. For each idea you get the formula, a "
        "simple explanation, why it matters, how to read it, and a quick example.",
    ], last_col=LAST)
    r += 1

    def field(label, text, role="note_l"):
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
