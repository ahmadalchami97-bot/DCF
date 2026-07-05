"""Sheet 1: Start Here / Beginner Guide -- read this first, assume you know nothing."""

from __future__ import annotations

from .. import common

LAST = 8

SHEET_MAP = [
    ("Start Here", "This page - what bonds are and how to use the workbook."),
    ("Inputs", "The ONLY page you type on. Enter your bond in the yellow cells."),
    ("Cash Flows", "The payments you will receive, and what they are worth today."),
    ("Price Basics", "Clean price, dirty price and accrued interest - the price you really pay."),
    ("Yield Basics", "Your return: yield to maturity, current yield and spread."),
    ("Price & Yield", "A calculator: price from a yield, yield from a price, both ways."),
    ("Duration", "How sensitive your bond is to interest-rate moves."),
    ("DV01", "That same risk, but in money terms, per 1 basis point."),
    ("Convexity", "Why duration is not perfect - and why that helps you."),
    ("Rate Shock", "What happens to the price if yields jump up or down."),
    ("Yield Curve", "Government yields by maturity, and where your bond sits."),
    ("Valuation Summary", "The whole bond at a glance, with plain-English reads."),
    ("Is It Attractive", "A simple score out of 10 - is the yield worth the risk?"),
    ("Recommendation", "Your final Buy / Hold / Avoid call (you decide)."),
    ("Glossary", "Every term defined in simple language."),
    ("Formula Explanations", "Every formula, explained in plain English."),
    ("Quality Check", "15 checks that the maths is correct."),
    ("Limitations", "What this simple workbook does not try to do."),
]

WORDS = [
    ("Face value", "The amount repaid at the end (e.g. 100). Interest is based on it. Prices are quoted per 100 face."),
    ("Coupon", "The regular interest payment - usually twice a year for government notes and bonds."),
    ("Coupon rate", "The annual interest rate. A 4% coupon on 100 face pays 4 per year (2 + 2 for semiannual)."),
    ("Maturity", "The date the government repays the face value and the loan ends."),
    ("Price", "What the bond costs today, quoted per 100 of face value. It can be above or below 100."),
    ("Yield", "Your return as an annual percentage. The headline one is 'yield to maturity' (YTM)."),
]


def build(sh, ctx):
    common.title_block(sh, "START HERE - BEGINNER GUIDE", "New to bonds? Read this page first. It assumes you know "
                       "nothing.", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 8, [
        "Welcome. This workbook is a beginner course AND a working government-bond calculator in one. You will learn "
        "what a bond is, how it is priced, what its yield means, and how risky it is - one sheet at a time.",
        "You only ever type in ONE place: the Inputs sheet (the yellow cells). Everything else updates automatically. "
        "Yellow = you type here.  Black = a formula.  Green = a key answer.  Grey = a note or explanation.",
    ], last_col=LAST)
    r += 1

    # --- Bonds in 60 seconds ---
    r = common.section(sh, r, "1.  What is a bond?", c1=1, c2=LAST)
    for line in [
        "A bond is a loan. When you buy a bond, you are lending money to a borrower. In return they promise to pay you "
        "interest along the way and to repay the amount borrowed on a set date in the future.",
        "A GOVERNMENT bond is a loan to a national government (through its treasury). Because major governments can "
        "tax and print their own currency, their bonds are treated as very low risk - the safest bonds you can buy. "
        "This workbook covers government bonds ONLY.",
        "You make money two ways: the regular interest payments (coupons), and any difference between what you pay now "
        "and the face value you get back at maturity.",
    ]:
        sh.put(r, 1, line, role="note_l"); sh.merge(r, 1, r, LAST)
        sh.row_height(r, max(15, 13 + 12 * (len(line) // 110))); r += 1
    r += 1

    # --- Three types ---
    r = common.section(sh, r, "2.  The three government bonds in this workbook", c1=1, c2=LAST)
    for name, desc in [
        ("Treasury Bill (zero-coupon)", "Short term (a year or less). Pays NO coupons. You buy it below 100 and get "
         "100 back at maturity - the gain is your return."),
        ("Treasury Note (fixed coupon)", "Medium term (about 2-10 years). Pays a fixed coupon, usually twice a year, "
         "plus the face value at maturity."),
        ("Treasury Bond (fixed coupon)", "Long term (often 20-30 years). Same idea as a note but longer, so its price "
         "moves more when yields change."),
    ]:
        sh.put(r, 1, name, role="label_b")
        sh.put(r, 2, desc, role="note_l"); sh.merge(r, 2, r, LAST)
        sh.row_height(r, max(15, 13 + 12 * (len(desc) // 92))); r += 1
    r += 1

    # --- Key words ---
    r = common.section(sh, r, "3.  The words you must know", c1=1, c2=LAST)
    for word, meaning in WORDS:
        sh.put(r, 1, word, role="label_b")
        sh.put(r, 2, meaning, role="note_l"); sh.merge(r, 2, r, LAST)
        sh.row_height(r, max(15, 13 + 12 * (len(meaning) // 92))); r += 1
    r += 1

    # --- Golden rule ---
    r = common.section(sh, r, "4.  The one golden rule of bonds", c1=1, c2=LAST)
    r = common.interp(sh, r, [
        "PRICE and YIELD move in OPPOSITE directions. When yields (market interest rates) go UP, bond prices go DOWN. "
        "When yields go DOWN, bond prices go UP.",
        "Why? A bond's coupons are fixed. If new bonds start paying more, yours looks less attractive, so its price "
        "must fall until its return matches the market. If new bonds pay less, yours looks better, so its price rises.",
        "Simple example: you own a bond paying 4%. If market yields rise to 5%, no one will pay full price for your 4% "
        "bond, so its price drops. That price drop is the main risk of owning a bond - and it is what 'duration' on "
        "the later sheets measures.",
    ], last_col=LAST, title="Remember this one thing")

    # --- How to use ---
    r = common.section(sh, r, "5.  How to use this workbook (8 steps)", c1=1, c2=LAST)
    steps = [
        "Open the Inputs sheet and enter your bond in the yellow cells (name, dates, coupon, price).",
        "Read Cash Flows to see every payment you will receive and its value today.",
        "Read Price Basics to learn the difference between the clean price and the price you actually pay (dirty).",
        "Read Yield Basics to see your return - the yield to maturity.",
        "Use the Price & Yield Calculator to test: what price does a yield imply, and is the bond cheap or expensive?",
        "Check Duration, DV01 and Convexity to understand how risky the bond is.",
        "Look at Rate Shock and the Yield Curve to see the bigger interest-rate picture.",
        "Finish on Is It Attractive? and Recommendation to form your own Buy / Hold / Avoid view.",
    ]
    for i, step in enumerate(steps, 1):
        sh.put(r, 1, f"Step {i}", role="label_b")
        sh.put(r, 2, step, role="note_l"); sh.merge(r, 2, r, LAST)
        sh.row_height(r, max(15, 13 + 12 * (len(step) // 92))); r += 1
    r += 1

    # --- Sheet map ---
    r = common.section(sh, r, "6.  A map of every sheet", c1=1, c2=LAST)
    for name, desc in SHEET_MAP:
        c = sh.put(r, 1, name, role="formula_l")
        c.hyperlink = f"#'{name}'!A1"
        sh.put(r, 2, desc, role="note_l"); sh.merge(r, 2, r, LAST)
        sh.row_height(r, max(15, 13 + 12 * (len(desc) // 92))); r += 1
    r += 1

    common.interp(sh, r, [
        "Take it slowly and in order - each sheet builds on the one before. By the end you will understand what a "
        "government bond is worth, what it yields, how risky it is, and whether it looks attractive to you.",
        "This is an educational tool, not investment advice.",
    ], last_col=LAST, title="Final tip")

    sh.freeze("A6")
    sh.col_width(1, 22)
    for c in range(2, LAST + 1):
        sh.col_width(c, 13)
    return sh
