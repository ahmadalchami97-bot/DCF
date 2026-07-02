"""Sheet 9: Risks -- a structured Low/Medium/High checklist."""

from __future__ import annotations

from .. import common

LAST = 5

RISKS = [
    ("Interest-rate risk", "Price falls when market yields rise (see Modified duration & the stress table).",
     "Medium", "Modified duration ~4.2 - a 1% rate rise cuts the price ~4%.", "Hold to maturity to recover price."),
    ("Credit risk", "The issuer may fail to pay coupons or principal.",
     "Medium", "BBB issuer; leverage and coverage look acceptable.", "Investment-grade rating; senior ranking."),
    ("Liquidity risk", "You may not be able to sell quickly at a fair price.",
     "Medium", "Single corporate bond; check trading volume.", "Size position so you can hold to maturity."),
    ("Refinancing risk", "The issuer may struggle to refinance maturing debt.",
     "Low", "See the Maturity Wall vs liquidity.", "Debt maturities are spread out."),
    ("Call risk", "The issuer can repay early, capping your upside (see YTC/YTW).",
     "Medium", "Callable in 2028 at 102; YTW governs.", "Call price above par gives some compensation."),
    ("Currency risk", "FX moves affect value if the bond is not in your currency.",
     "Low", "USD bond; only relevant for non-USD investors.", "Hedge FX or match to USD liabilities."),
    ("Sector risk", "Sector-specific pressures (demand, input costs, regulation).",
     "Medium", "Industrials - cyclical demand.", "Diversify across sectors."),
    ("Covenant risk", "Weak bondholder protections in the bond documents.",
     "Medium", "Review the offering memorandum.", "Senior unsecured ranking."),
    ("Downgrade risk", "A rating cut would widen the spread and lower the price.",
     "Medium", "BBB is one notch above high yield - watch the trend.", "Monitor the credit ratios each quarter."),
]


def build(sh, ctx):
    common.title_block(sh, "RISKS", "A simple risk checklist - set each to Low / Medium / High and add your view",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "For each risk, pick Low / Medium / High (drop-down), then add a short comment and a mitigating factor. "
        "The sample text is a starting point - edit it for your bond.",
        "The colour of the assessment updates automatically (green = Low, amber = Medium, red = High).",
    ], last_col=LAST)
    r += 1

    hdr = r
    for c, tx in enumerate(["Risk", "Description", "Assessment", "Analyst comment", "Mitigating factor"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c != 2 else "colhdr_l")
    sh.row_height(hdr, 18)
    r += 1
    first = r
    for name, desc, level, comment, mitig in RISKS:
        sh.put(r, 1, name, role="label_b")
        sh.put(r, 2, desc, role="note_l")
        sh.put(r, 3, level, role="input_c")
        common.dropdown(sh, r, 3, ["Low", "Medium", "High"])
        sh.put(r, 4, comment, role="input_l")
        sh.put(r, 5, mitig, role="input_l")
        sh.row_height(r, 30)
        r += 1
    last = r - 1
    common.traffic_light(sh, f"C{first}:C{last}", f"C{first}")

    sh.freeze("A6")
    sh.col_width(1, 18)
    sh.col_width(2, 46)
    sh.col_width(3, 12)
    sh.col_width(4, 34)
    sh.col_width(5, 34)
    return sh
