"""Sheet 11: Formula Explanations -- every key formula in plain English."""

from __future__ import annotations

from .. import common

LAST = 10

ENTRIES = [
    ("Clean price", "Quoted price, excludes accrued interest",
     "The price you see quoted. It does not include the coupon that has built up since the last payment.",
     "It is what you compare across bonds; the extra you actually pay (accrued) is added separately."),
    ("Dirty price", "Clean price + accrued interest",
     "The actual cash you pay (also called the invoice or settlement price).",
     "This is the true cost of the bond and what the cash flows discount back to."),
    ("Accrued interest", "(days since last coupon / days in period) x periodic coupon",
     "The slice of the next coupon that the seller has earned and you reimburse.",
     "Zero for a zero-coupon bond. Uses the chosen day-count basis."),
    ("Yield to maturity (YTM)", "The rate that makes PV of all cash flows = price",
     "The single annual return you earn if you hold to maturity and reinvest coupons at that rate.",
     "The headline yield. Higher price -> lower yield, and vice versa."),
    ("Current yield", "Annual coupon / clean price",
     "A quick income measure - just coupon versus price.",
     "Ignores capital gain/loss and timing, so it is only a rough guide. N/A for zero-coupon."),
    ("Spread", "YTM - benchmark government yield",
     "The extra yield over a safe government bond of similar maturity.",
     "Your pay for credit risk. Wider can mean cheaper - but only if the risk is acceptable."),
    ("Macaulay duration", "sum(time x PV) / sum(PV)",
     "The weighted-average time (years) to receive the bond's cash flows.",
     "Roughly how long your money is tied up. For a zero-coupon bond it equals time to maturity."),
    ("Modified duration", "Macaulay duration / (1 + YTM/frequency)",
     "The approximate % price change for a 1% (100 bps) move in yield.",
     "The main interest-rate risk number. 5 means a ~5% price fall if yields rise 1%."),
    ("Convexity", "sum(CF x t x (t+1) / (1+y/f)^(t+2)) / (price x f^2)",
     "Corrects the duration estimate because the price/yield relationship is curved.",
     "Positive for plain bonds; it helps you on big rallies and cushions big sell-offs."),
    ("DV01", "Modified duration x dirty price x 0.0001",
     "The price change for a 1 basis-point (0.01%) move in yield.",
     "A dollar/price risk measure; useful for sizing and hedging. Quoted as a positive number."),
    ("Yield to call (YTC)", "Yield using cash flows only to the call date + call price",
     "The return if the issuer calls the bond on the call date.",
     "Matters for callable bonds - the issuer calls when it suits them, not you."),
    ("Yield to worst (YTW)", "Lower of YTM and YTC",
     "The most conservative yield across the maturity and call scenarios.",
     "Always evaluate a callable bond on YTW, not YTM."),
    ("Net debt / EBITDA", "(total debt - cash) / EBITDA",
     "How many years of earnings it would take to repay net debt (leverage).",
     "Lower is safer. Very high is a red flag for credit risk."),
    ("Interest coverage", "EBITDA / interest expense (or EBIT / interest)",
     "How many times earnings cover the interest bill.",
     "Higher is safer. Near or below ~1.5x is a warning sign."),
    ("Liquidity coverage", "(cash + credit lines) / debt due in next 12 months",
     "Whether the issuer can cover near-term maturities without new borrowing.",
     "Below 1.0x means near-term debt exceeds available liquidity - a concern."),
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
    sh.col_width(1, 12); sh.col_width(2, 10)
    for c in range(3, LAST + 1):
        sh.col_width(c, 12)
    return sh
