"""Analyst Notes (Sheet 9): structured space for the written investment view."""

from __future__ import annotations

from .. import common

SECTIONS = [
    ("Investment Thesis", "Summarise the core reasons to own (or avoid) the stock."),
    ("Key Risks", "What could break the thesis? Demand, margins, leverage, capital allocation, governance."),
    ("Forecast Rationale", "Why the chosen growth, margin and capital assumptions are appropriate."),
    ("Management Commentary", "Relevant guidance, strategy and capital-allocation signals from management."),
    ("Earnings Review Notes", "Post-results observations: beats/misses vs forecast and what changed."),
]


def build(sh, ctx):
    LAST = 8
    common.title_block(sh, "ANALYST NOTES",
                       "Structured space for the written investment view", last_col=LAST)
    common.nav_bar(sh, 5)
    r = 7
    sh.put(r, 1, "Free-text input cells (blue). These travel with the model into the investment memo.",
           role="note")
    sh.merge(r, 1, r, LAST)
    r += 2
    for title, prompt in SECTIONS:
        r = common.section(sh, r, title, c1=1, c2=LAST)
        sh.put(r, 1, prompt, role="sublabel")
        sh.merge(r, 1, r, LAST)
        r += 1
        # a multi-line input area (top-aligned, wrapped)
        sh.put(r, 1, None, role="input_l", align="ltw")
        sh.merge(r, 1, r + 4, LAST)
        for rr in range(r, r + 5):
            sh.row_height(rr, 18)
        r += 6
    sh.col_width(1, 24)
    for c in range(2, LAST + 1):
        sh.col_width(c, 16)
    return sh
