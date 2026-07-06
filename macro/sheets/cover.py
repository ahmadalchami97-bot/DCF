"""S00 Cover & User Guide -- front door, legend, contents, how to use."""

from __future__ import annotations

from .. import common
from ..config import DISCLAIMER, FUTURE_SHEETS, SHEET_ORDER

LAST = 8

BUILT = {
    "Cover": "This page - guide, legend and contents.",
    "Settings": "Control panel: dropdown lists, Fed score weights, thresholds.",
    "Impact Library": "How each of 21 macro indicators usually moves markets.",
    "Data Tracker": "Log every release here (an input sheet).",
    "Surprise Engine": "Scores each release: surprise vs forecast -> signals -> asset arrows.",
    "Fed Tracker": "Fed policy state, speeches, and the hawkish/dovish score.",
}


def build(sh, ctx):
    common.title_block(sh, "MACRO MARKET INTELLIGENCE SYSTEM", "Core engine (Phase 1-2) - read this first", last_col=LAST)
    r = common.explain_box(sh, 5, [
        "This workbook helps you monitor the macro environment and translate it into market and portfolio "
        "implications. This is the CORE build: the input log and the first two scoring engines (data surprise and "
        "Fed bias). The market modules, scenario tools and executive dashboard follow in the next phase.",
        "You maintain just two sheets: the Data Tracker (releases) and the Fed Tracker (policy). Everything else "
        "calculates. Tune all weights and lists on the Settings sheet.",
    ], last_col=LAST, title="What this is")
    r += 1

    r = common.section(sh, r, "Colour legend", c1=1, c2=LAST)
    for txt, role in [("Input - you type here", "input_c"), ("Formula / derived", "formula_l"),
                      ("Linked from another sheet", "link"), ("Key output / score", "output_l")]:
        sh.put(r, 1, txt, role="label_b")
        sh.put(r, 3, "example", role=role); sh.merge(r, 3, r, 4)
        r += 1
    r += 1

    r = common.section(sh, r, "How it flows (3 layers)", c1=1, c2=LAST)
    for line in [
        "INPUT  ->  Data Tracker, Fed Tracker, Settings  (you maintain these)",
        "ENGINE ->  Surprise Engine, Fed bias score  (formulas score the inputs)",
        "OUTPUT ->  signals and arrows you read, and - in the next phase - a one-page dashboard",
    ]:
        sh.put(r, 1, line, role="note_l"); sh.merge(r, 1, r, LAST); r += 1
    r += 1

    r = common.section(sh, r, "Contents (click to jump)", c1=1, c2=LAST)
    for name in SHEET_ORDER:
        c = sh.put(r, 1, name, role="formula_l")
        c.hyperlink = f"#'{name}'!A1"
        sh.put(r, 3, BUILT.get(name, ""), role="note_l"); sh.merge(r, 3, r, LAST)
        r += 1
    r += 1

    r = common.section(sh, r, "Coming in the next build phase", c1=1, c2=LAST)
    sh.merge(r, 1, r, LAST)
    sh.put(r, 1, "  ·  ".join(FUTURE_SHEETS), role="note_l")
    r += 2

    r = common.section(sh, r, "How to update", c1=1, c2=LAST)
    for line in [
        "Daily/on release: add a row to the Data Tracker (pick the indicator from the dropdown), enter Actual / "
        "Forecast / Previous. The Surprise Engine scores it instantly.",
        "Weekly: update the Fed Tracker (speeches, implied path, yield moves) and re-read the Fed bias score.",
        "As needed: adjust weights, lists or indicator polarity on Settings / Impact Library.",
    ]:
        sh.put(r, 1, line, role="note_l"); sh.merge(r, 1, r, LAST)
        sh.row_height(r, max(14, 13 + 12 * (len(line) // 110))); r += 1
    r += 1

    common.interp(sh, r, [DISCLAIMER], last_col=LAST, title="Disclaimer")

    sh.col_width(1, 20); sh.col_width(2, 3)
    for c in range(3, LAST + 1):
        sh.col_width(c, 14)
    return sh
