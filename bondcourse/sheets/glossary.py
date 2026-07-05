"""Sheet 15: Glossary / Bond Dictionary -- every term a beginner needs, plain English."""

from __future__ import annotations

from .. import common

LAST = 8

# (term, plain-English definition) -- kept alphabetical so it reads like a dictionary.
GLOSSARY = [
    ("Accrued interest",
     "The part of the next coupon the seller has already earned. When you buy between coupon dates you pay it to them, "
     "then collect the whole coupon next time."),
    ("Basis point (bp)",
     "One hundredth of one percent: 1 bp = 0.01%. Yields move in basis points - 25 bps means 0.25%."),
    ("Benchmark yield",
     "The market yield of a similar-maturity government bond, used as the yardstick to judge your bond's yield."),
    ("Bond",
     "A loan you make to a borrower. They pay you interest along the way and repay the amount borrowed at the end."),
    ("Clean price",
     "The quoted market price of a bond, per 100 of face value, NOT including accrued interest."),
    ("Convexity",
     "A measure of how a bond's price curve bends. It corrects duration's straight-line estimate and is a small plus "
     "for the holder of a normal bond."),
    ("Coupon",
     "The regular interest payment a bond makes, usually every six months for government notes and bonds."),
    ("Coupon rate",
     "The annual interest rate the bond pays on its face value. A 4% coupon on 100 face pays 4 per year."),
    ("Currency",
     "The money the bond is issued and pays in, such as USD, EUR or GBP."),
    ("Current yield",
     "The annual coupon divided by the current price - a quick income measure that ignores gain or loss to maturity."),
    ("Day-count basis",
     "The rule for counting days between dates (for accrued interest and yields). Governments usually use "
     "Actual/Actual."),
    ("Default risk",
     "The risk the borrower fails to pay. For major government bonds in their own currency this is treated as very "
     "low."),
    ("Discount (price)",
     "When a bond's price is below 100 (below par). It usually means the coupon is lower than current market yields."),
    ("Discount factor",
     "How much 1 unit of money received in the future is worth today. Future money is worth less than money now."),
    ("Dirty price",
     "The actual cash you pay for a bond = clean price + accrued interest."),
    ("Duration",
     "The main measure of interest-rate risk. Broadly, how much the price moves when yields move, and how long your "
     "money is tied up."),
    ("DV01",
     "The 'dollar value of 1 basis point' - how much the bond's value changes in money terms if the yield moves "
     "0.01%."),
    ("Face value (par)",
     "The amount the bond repays at maturity, and the base the coupon is calculated on. Prices are quoted per 100 "
     "face."),
    ("Flat yield curve",
     "When short-term and long-term yields are about the same - often a sign of uncertainty about future rates."),
    ("Interest-rate risk",
     "The risk that rising market yields push your bond's price down. It is the main risk for a government bond."),
    ("Inverted yield curve",
     "When short-term yields are higher than long-term yields. Watched closely because it has often preceded "
     "recessions."),
    ("Issue date",
     "The date the bond was first sold by the government."),
    ("Issuer",
     "Who borrowed the money - for a government bond, the national treasury or government."),
    ("Macaulay duration",
     "The weighted-average time, in years, to receive a bond's cash flows."),
    ("Maturity date",
     "The date the bond repays its face value and the loan ends."),
    ("Modified duration",
     "The estimated percentage change in price for a 1% (100 bps) change in yield. Bigger = more rate risk."),
    ("Normal yield curve",
     "When long-term yields are higher than short-term yields - the usual, healthy shape. You are paid more to lend "
     "for longer."),
    ("Par",
     "A price of exactly 100 - the face value. Above par = premium; below par = discount."),
    ("Premium (price)",
     "When a bond's price is above 100 (above par). It usually means the coupon is higher than current market "
     "yields."),
    ("Present value (PV)",
     "The value today of money you will receive in the future, after applying a discount factor."),
    ("Principal",
     "The amount borrowed and repaid at maturity - the same as the face value."),
    ("Reinvestment risk",
     "The risk that you have to reinvest coupons at lower rates than you hoped. Zero-coupon bonds avoid it (no "
     "coupons)."),
    ("Settlement date",
     "The date you actually buy and pay for the bond - usually today when you value it."),
    ("Spread",
     "Your bond's yield minus a benchmark government yield of similar maturity. Usually small for governments."),
    ("Treasury bill (T-bill)",
     "A short-term government security (a year or less) sold at a discount with no coupons - a zero-coupon bond."),
    ("Treasury bond",
     "A long-term government bond (often 20-30 years) that pays regular coupons."),
    ("Treasury note",
     "A medium-term government bond (about 2-10 years) that pays regular coupons."),
    ("Yield",
     "The return a bond gives you, expressed as an annual percentage."),
    ("Yield curve",
     "A chart of government yields across maturities. It shows whether longer bonds pay more and where your bond "
     "sits."),
    ("Yield to maturity (YTM)",
     "The annual return you earn if you buy at today's price and hold to maturity, receiving all payments. The main "
     "yield number."),
    ("Zero-coupon bond",
     "A bond with no coupons. You buy it below face value and get the full face value back at maturity; the gain is "
     "your return."),
]


def build(sh, ctx):
    common.title_block(sh, "GLOSSARY / BOND DICTIONARY", "Every term a beginner needs - in plain English",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "New to bonds? Keep this page handy. Every term used anywhere in the workbook is defined here in simple "
        "language, in alphabetical order.",
    ], last_col=LAST)
    r += 1

    hdr = r
    sh.put(hdr, 1, "Term", role="colhdr_l")
    sh.put(hdr, 2, "What it means", role="colhdr_l"); sh.merge(hdr, 2, hdr, LAST)
    r += 1

    for term, definition in GLOSSARY:
        sh.put(r, 1, term, role="label_b")
        sh.put(r, 2, definition, role="note_l"); sh.merge(r, 2, r, LAST)
        sh.row_height(r, max(15, 13 + 12 * (len(definition) // 92)))
        r += 1

    sh.freeze("A7")
    sh.col_width(1, 22)
    for c in range(2, LAST + 1):
        sh.col_width(c, 13)
    return sh
