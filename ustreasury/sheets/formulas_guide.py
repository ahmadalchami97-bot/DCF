"""Sheet 10: Formula Explanations."""

from __future__ import annotations

from .. import common

LAST = 10

ENTRIES = [
    ("Clean price", "Quoted price, excludes accrued interest",
     "The price you see quoted for the Treasury.",
     "What you compare across bonds; accrued is added on top to get what you pay."),
    ("Dirty price", "Clean price + accrued interest",
     "The actual cash you pay to settle the trade (the invoice price).",
     "This is the true cost and what the cash flows discount back to."),
    ("Accrued interest", "(days since last coupon / days in period) x periodic coupon",
     "The slice of the next coupon the seller has earned and you reimburse.",
     "Zero for a Treasury Bill (no coupons)."),
    ("Yield to maturity", "Rate that makes PV of cash flows = price (Excel YIELD)",
     "The annual return if you hold to maturity and reinvest coupons at that rate.",
     "The headline yield. Higher price -> lower yield."),
    ("Current yield", "Annual coupon / clean price",
     "A quick income measure (coupon vs price).",
     "Ignores capital gain/loss and timing. N/A for a Treasury Bill."),
    ("Treasury Bill yield", "(Face / Price) ^ (1 / Years) - 1",
     "A bill pays no coupon; its return is the discount from face, annualised.",
     "Computed from price, face and time to maturity (effective annual)."),
    ("Premium / discount to par", "Clean price - 100",
     "Whether the bond trades above (premium) or below (discount) face value.",
     "Coupon above current yields -> premium; below -> discount."),
    ("Macaulay duration", "sum(time x PV) / sum(PV)  (Excel DURATION)",
     "Weighted-average time (years) to receive the cash flows.",
     "For a Treasury Bill it equals the time to maturity."),
    ("Modified duration", "Macaulay / (1 + yield/2)  (Excel MDURATION)",
     "Approximate % price change for a 1% (100 bps) yield move.",
     "The main interest-rate risk number. 7 => ~7% price fall if yields rise 1%."),
    ("Convexity", "sum(CF x t x (t+1)/(1+y/2)^(t+2)) / (price x 4)",
     "Corrects the duration estimate because price/yield is curved.",
     "Positive for a normal Treasury; helps on rallies, cushions sell-offs."),
    ("DV01", "Modified duration x dirty price x 0.0001",
     "Price change for a 1 basis-point (0.01%) yield move.",
     "A price-risk measure; quoted as a positive number."),
    ("Price impact from rate shocks", "- Modified x (yield change) + 0.5 x convexity x (yield change)^2",
     "Estimated % price change when the yield moves, from duration and convexity.",
     "Yields up -> price down. Bigger duration -> bigger move."),
]


def build(sh, ctx):
    common.title_block(sh, "FORMULA EXPLANATIONS", "Every key calculation in plain English", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "Read this once and you can audit any number in the workbook. Each row gives the formula, what it means, "
        "and how to read it.",
    ], last_col=LAST)
    r += 1

    hdr = r
    sh.put(hdr, 1, "Concept", role="colhdr_l"); sh.merge(hdr, 1, hdr, 2)
    sh.put(hdr, 3, "Formula", role="colhdr_l"); sh.merge(hdr, 3, hdr, 5)
    sh.put(hdr, 6, "What it means", role="colhdr_l"); sh.merge(hdr, 6, hdr, 7)
    sh.put(hdr, 8, "How to read it", role="colhdr_l"); sh.merge(hdr, 8, hdr, LAST)
    r += 1
    for concept, formula, meaning, interp in ENTRIES:
        sh.put(r, 1, concept, role="label_b"); sh.merge(r, 1, r, 2)
        sh.put(r, 3, formula, role="formula_l"); sh.merge(r, 3, r, 5)
        sh.put(r, 6, meaning, role="note_l"); sh.merge(r, 6, r, 7)
        sh.put(r, 8, interp, role="note_l"); sh.merge(r, 8, r, LAST)
        sh.row_height(r, max(30, 14 + 13 * (max(len(meaning), len(interp)) // 34)))
        r += 1

    sh.freeze("A6")
    sh.col_width(1, 13); sh.col_width(2, 10)
    for c in range(3, LAST + 1):
        sh.col_width(c, 12)
    return sh
