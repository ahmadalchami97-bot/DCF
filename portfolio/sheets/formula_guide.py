"""
Formula Guide.

Every calculation in the workbook, explained in plain language with its formula
and a worked meaning. Designed so a non-quant user can audit the tool.
"""

from __future__ import annotations

from .. import common

LAST = 10

ENTRIES = [
    ("Asset return (local)",
     "End price / Start price - 1",
     "The price move in the asset's own currency over the scenario. Example: 110/100 - 1 = +10%."),
    ("FX return",
     "End FX rate / Start FX rate - 1",
     "The change in the value of the asset's currency against your base currency. If your base currency "
     "strengthens, foreign assets are worth less to you (a negative FX return)."),
    ("Currency-adjusted return",
     "(1 + Asset return) x (1 + FX return) - 1",
     "What you actually earned in your own currency: the price move and the currency move combined. "
     "Example: (1+10%) x (1+2%) - 1 = +12.2%."),
    ("Weight",
     "Asset value / Total portfolio value",
     "Each asset's share of the portfolio. All weights add up to 100%."),
    ("Contribution to return",
     "Weight x Currency-adjusted return",
     "How much an asset added to the total return. A 20% weight earning +12% contributes +2.4%."),
    ("Portfolio return",
     "Sum of all contributions",
     "Add up every asset's contribution to get the whole portfolio's return for the scenario."),
    ("Bond return",
     "(End price - Start price + Coupon earned) / Start price",
     "Bonds earn a coupon as well as moving in price. Coupon earned = Face x Coupon rate x (Days held / 365). "
     "Adding the coupon to the price change gives the bond's total return."),
    ("Expected return (long-term)",
     "Your annual view per asset (an input)",
     "The long-run return you expect from each asset, separate from the one-off scenario. Used for the "
     "recommendation."),
    ("Volatility (risk)",
     "How much an asset's return bounces around (an input, annual)",
     "A higher number means a bumpier ride. It is the standard measure of risk."),
    ("Correlation",
     "How two assets move together (-1 to +1)",
     "+1 = always move together, 0 = unrelated, -1 = move opposite. Mixing low-correlation assets lowers "
     "portfolio risk -- that is diversification."),
    ("Portfolio volatility",
     "Built from the weights and the covariance table",
     "Covariance = Vol(i) x Vol(j) x Correlation(i,j). The portfolio's risk adds up every pair's combined risk, "
     "and falls when assets do not move together. Shown on the Allocation sheet for each allocation."),
    ("Sharpe ratio",
     "(Expected return - Risk-free rate) / Volatility",
     "Return earned per unit of risk. Higher is better. It lets you compare portfolios fairly when one has "
     "more risk than another."),
    ("Max-Sharpe weight (simplified)",
     "score / sum of scores,  where score = max(0, Expected - Risk-free) / Volatility^2",
     "Gives more weight to assets with the best return per unit of risk. A simple, transparent rule -- not a "
     "Solver optimisation."),
    ("Min-volatility weight (simplified)",
     "(1 / Volatility^2) / sum of (1 / Volatility^2)",
     "Gives more weight to the calmer assets, to reduce overall risk."),
    ("Scenario-stressed weight",
     "Max-Sharpe base x (1 + capped tilt), then clamp to your min/max and re-normalise",
     "Starts from the long-term Max-Sharpe mix and leans modestly toward assets that did well in the scenario. "
     "The tilt is capped so it never chases short-term moves, and your min/max limits are always respected."),
    ("Risk/return map (efficient frontier idea)",
     "Plot each portfolio as (volatility, expected return)",
     "The map shows the trade-off: for a given level of risk you want the highest return. Portfolios toward the "
     "top-left (more return, less risk) are more efficient."),
    ("Rebalancing trade",
     "Target value - Current value;  Target value = Recommended weight x Total invested",
     "The amount to buy (positive) or sell (negative) to reach the recommended allocation. Small gaps are left "
     "as Hold so you do not trade on noise."),
]


def build(sh, ctx):
    common.title_block(sh, "FORMULA GUIDE", "Every calculation, in plain language", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "This sheet explains every formula the workbook uses. Read it once and you can audit any number in the tool.",
    ], last_col=LAST)
    r += 1

    hdr = r
    sh.put(hdr, 1, "Concept", role="colhdr_l")
    sh.put(hdr, 3, "Formula", role="colhdr_l")
    sh.put(hdr, 6, "What it means", role="colhdr_l")
    sh.merge(hdr, 1, hdr, 2)
    sh.merge(hdr, 3, hdr, 5)
    sh.merge(hdr, 6, hdr, LAST)
    r += 1
    for concept, formula, meaning in ENTRIES:
        sh.put(r, 1, concept, role="label_b")
        sh.merge(r, 1, r, 2)
        sh.put(r, 3, formula, role="formula_l")
        sh.merge(r, 3, r, 5)
        sh.put(r, 6, meaning, role="note_l")
        sh.merge(r, 6, r, LAST)
        sh.row_height(r, max(28, 14 + 13 * (len(meaning) // 70)))
        r += 1

    sh.freeze("A6")
    sh.col_width(1, 18)
    sh.col_width(2, 6)
    for c in range(3, 6):
        sh.col_width(c, 13)
    for c in range(6, LAST + 1):
        sh.col_width(c, 12)
    return sh
