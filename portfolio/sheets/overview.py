"""
Overview  (start here).

A plain-English cover: what the tool does, the order to use the sheets, the asset
universe, the colour legend and the model-based disclaimer.
"""

from __future__ import annotations

from .. import common
from ..config import ALLOCATIONS, ASSETS, DISCLAIMER, INDICATORS

LAST = 10


def build(sh, ctx):
    common.title_block(sh, "PORTFOLIO ALLOCATION OPTIMIZER",
                       "Scenario analysis, risk/return and recommended rebalancing", last_col=LAST)
    common.nav_bar(sh, 5)
    r = 7

    def para(text, role="note", height=None):
        nonlocal r
        sh.put(r, 1, text, role=role, align="lw")
        sh.merge(r, 1, r, LAST)
        if height:
            sh.row_height(r, height)
        r += 1

    def head(text):
        nonlocal r
        r = common.section(sh, r, text, c1=1, c2=LAST)

    head("What this tool does")
    para("It helps you understand four things, simply and transparently: (1) your CURRENT allocation, "
         "(2) the IMPACT of a market scenario on each asset and the whole portfolio, (3) the RISK and RETURN "
         "trade-off across allocation choices, and (4) a recommended set of REBALANCING actions.", height=46)
    para("It is a clean, explainable Excel tool -- not a black-box quant model. Every result is a short, visible "
         "formula you can follow and audit.", height=30)

    head("How to use it (in order)")
    for i, (name, desc) in enumerate([
        ("Scenario Inputs", "Type your scenario: dates, each asset's start/end price and FX rate, amounts invested, and target/min/max weights. Includes a small bond calculator."),
        ("Scenario Output", "See each asset's local return, FX effect, currency-adjusted return and contribution to the portfolio return."),
        ("Risk & Return", "Enter long-term expected return, volatility and correlations -- the inputs behind the recommendation."),
        ("Allocation", "Compare six allocations and build the scenario-stressed recommendation; pick which one to rebalance toward."),
        ("Rebalancing", "Get the buy/sell/hold actions and the reason for each."),
        ("Dashboard", "See it all visually: allocation pies, scenario bars and a risk/return map."),
        ("Formula Guide", "Every formula explained in plain language."),
    ], 1):
        sh.put(r, 1, f"{i}.  {name}", role="label_b")
        sh.put(r, 3, desc, role="note_l")
        sh.merge(r, 3, r, LAST)
        sh.row_height(r, 26)
        r += 1
    r += 1

    head("Investable assets")
    for key, name, ccy in ASSETS:
        sh.put(r, 1, name, role="label_b")
        sh.put(r, 4, f"native currency: {ccy}", role="note_l")
        sh.merge(r, 4, r, LAST)
        r += 1
    r += 1
    head("Market indicators  (context / drivers only -- not holdings unless you mark them investable)")
    for key, name, note in INDICATORS:
        sh.put(r, 1, name, role="label_b")
        sh.put(r, 4, note, role="note_l")
        sh.merge(r, 4, r, LAST)
        r += 1
    r += 1

    head("The six allocations compared")
    for key, label, note in ALLOCATIONS:
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 4, note, role="note_l")
        sh.merge(r, 4, r, LAST)
        r += 1
    r += 1

    common.legend(sh, r, LAST)
    r += 2
    common.explain_box(sh, r, [DISCLAIMER], last_col=LAST, title="Important")

    sh.col_width(1, 22)
    sh.col_width(2, 6)
    sh.col_width(3, 14)
    for c in range(4, LAST + 1):
        sh.col_width(c, 11)
    return sh
