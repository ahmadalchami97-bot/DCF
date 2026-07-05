"""Sheet 8: Risk Summary -- a simple Treasury risk checklist."""

from __future__ import annotations

from .. import common

LAST = 4

DESCRIPTIONS = {
    "Interest-rate risk": "Price falls when market yields rise. This is the MAIN risk for a US Treasury.",
    "Duration risk": "Longer duration means bigger price swings for a given yield move.",
    "Reinvestment risk": "Coupons (and principal at maturity) may have to be reinvested at lower rates.",
    "Inflation risk": "Fixed nominal coupons lose purchasing power if inflation rises.",
    "Opportunity cost risk": "Locking in today's yield; if yields rise later you miss the higher income.",
    "Liquidity risk": "Ability to sell quickly at a fair price. Treasuries are highly liquid, so usually low.",
    "Curve risk": "Value depends on the shape and shifts of the yield curve at this maturity.",
}


def build(sh, ctx):
    risk = ctx.data["risk"]
    common.title_block(sh, "RISK SUMMARY", "The main risks of holding a US Treasury bond", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "For a US Treasury, the main risks are INTEREST-RATE and INFLATION risk - not credit risk. The US "
        "government's own securities are treated as the risk-free benchmark, so default/credit risk is not the focus.",
        "Set each risk to Low / Medium / High (drop-down) and add a short comment. The sample text is a starting point.",
    ], last_col=LAST)
    r += 1

    hdr = r
    for c, tx in enumerate(["Risk", "Description", "Assessment", "Analyst comment"], 1):
        sh.put(hdr, c, tx, role="colhdr" if c != 2 else "colhdr_l")
    sh.row_height(hdr, 18)
    r += 1
    first = r
    for name, desc in DESCRIPTIONS.items():
        level, comment = risk.get(name, ("Medium", ""))
        sh.put(r, 1, name, role="label_b")
        sh.put(r, 2, desc, role="note_l")
        sh.put(r, 3, level, role="input_c")
        common.dropdown(sh, r, 3, ["Low", "Medium", "High"])
        sh.put(r, 4, comment, role="input_l")
        sh.row_height(r, 30)
        r += 1
    last = r - 1
    common.traffic_light(sh, f"C{first}:C{last}", f"C{first}")
    sh.put(r + 1, 1, "Note: credit risk is not a major section for US Treasuries - it is the benchmark against which "
                     "other bonds' credit risk is measured.", role="note")
    sh.merge(r + 1, 1, r + 1, LAST)

    sh.freeze("A6")
    sh.col_width(1, 22); sh.col_width(2, 60); sh.col_width(3, 12); sh.col_width(4, 44)
    return sh
