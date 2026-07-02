"""Sheet 10: Recommendation -- one-page summary. Final Buy/Hold/Sell/Avoid stays manual."""

from __future__ import annotations

from .. import common
from ..config import Fmt

LAST = 6


def build(sh, ctx):
    common.title_block(sh, "RECOMMENDATION", "One-page bond summary and analyst view", last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "A one-page summary that pulls together price, yield, risk and credit. The interpretation lines below are "
        "automatic hints - the final Buy / Hold / Sell / Avoid call is yours to make (it is a manual input).",
    ], last_col=LAST)
    r += 1

    # ---- manual recommendation (prominent) ----
    sh.put(r, 1, "Recommendation", role="label_b")
    sh.put(r, 2, "Hold", role="input_c")
    common.dropdown(sh, r, 2, ["Buy", "Hold", "Sell", "Avoid"])
    sh.merge(r, 2, r, 3)
    sh.put(r, 4, "Your call. Use the summary and hints below to justify it.", role="note_l")
    sh.merge(r, 4, r, LAST)
    r += 2

    def pair(lrow, col, label, formula, fmt, role="link"):
        sh.put(lrow, col, label, role="label_b")
        sh.put(lrow, col + 1, formula, role=role, fmt=fmt)

    top = r
    common.section(sh, top, "Bond & pricing", c1=1, c2=3)
    common.section(sh, top, "Risk & credit", c1=4, c2=LAST)
    r = top + 1
    left = [
        ("Issuer", "=Issuer", None), ("Bond", "=BondName", None), ("Rating", "=Rating", None),
        ("Clean price", "=MktClean", Fmt.PRICE), ("Dirty price", "=Dirty", Fmt.PRICE),
        ("YTM", "=YTM", Fmt.PCT3), ("Yield to call", '=IF(CallableFlag<>"Yes","Not callable",YTC)', Fmt.PCT3),
        ("Yield to worst", "=YTW", Fmt.PCT3), ("Spread (bps)", "=SpreadBps", Fmt.BPS),
        ("Current yield", "=CurrentYield", Fmt.PCT2),
    ]
    right = [
        ("Macaulay duration", "=MacDur", Fmt.YEARS), ("Modified duration", "=ModDur", Fmt.RATIO),
        ("Convexity", "=Convexity", Fmt.RATIO), ("DV01 (per 100)", "=DV01", Fmt.NUM4),
        ("Net debt / EBITDA", "=NetDebtEBITDA", Fmt.MULT), ("EBITDA / interest", "=EBITDACover", Fmt.MULT),
        ("Liquidity coverage", "=LiqCoverage", Fmt.MULT), ("Year-1 maturities", "=MW1", Fmt.MONEY0),
        ("Total debt maturities", "=TotalMaturities", Fmt.MONEY0), ("Sector", "=Sector", None),
    ]
    for i in range(max(len(left), len(right))):
        rr = r + i
        if i < len(left):
            pair(rr, 1, left[i][0], left[i][1], left[i][2])
        if i < len(right):
            pair(rr, 4, right[i][0], right[i][1], right[i][2])
    r = r + max(len(left), len(right)) + 1

    # ---- auto interpretation ----
    r = common.section(sh, r, "Automatic interpretation (hints)", c1=1, c2=LAST)
    def hint(formula):
        nonlocal r
        sh.put(r, 1, formula, role="formula_l")
        sh.merge(r, 1, r, LAST)
        r += 1
    hint('=IF(AND(ISNUMBER(NetDebtEBITDA),NetDebtEBITDA<=4,Spread>=0.015),'
         '"Valuation: decent spread and acceptable leverage - potentially attractive.",'
         'IF(OR(AND(ISNUMBER(NetDebtEBITDA),NetDebtEBITDA>4),AND(ISNUMBER(LiqCoverage),LiqCoverage<1)),'
         '"Valuation: high leverage or weak liquidity - caution.",'
         '"Valuation: mixed - weigh the spread against the credit quality."))')
    hint('=IF(Spread<0.005,"Compensation: thin spread - may not pay you enough for the risk.",'
         '"Compensation: the spread gives some extra yield for the credit risk.")')
    hint('=IF(AND(CallableFlag="Yes",ISNUMBER(YTC),YTC<YTM-0.0025),'
         '"Call risk: YTC is below YTM - early call would cap your upside; judge on YTW.",'
         '"Call risk: limited - YTW is at or near YTM.")')
    hint('=IF(ModDur>7,"Rate risk: long duration - quite sensitive to rate moves.",'
         'IF(ModDur>3,"Rate risk: moderate duration.","Rate risk: short duration - less rate sensitive."))')
    r += 1

    # ---- manual comment fields ----
    r = common.section(sh, r, "Analyst view (manual)", c1=1, c2=LAST)
    for label in ("Main positive factors", "Main risks", "Final analyst comment"):
        sh.put(r, 1, label, role="label_b")
        sh.put(r, 2, "", role="input_l")
        sh.merge(r, 2, r, LAST)
        sh.row_height(r, 28)
        r += 1

    sh.put(r + 1, 1, "Reminder: this is a decision-support summary, not investment advice.", role="note")
    sh.merge(r + 1, 1, r + 1, LAST)

    sh.freeze("A6")
    sh.col_width(1, 20)
    sh.col_width(2, 14)
    sh.col_width(3, 6)
    sh.col_width(4, 20)
    sh.col_width(5, 14)
    sh.col_width(6, 10)
    return sh
