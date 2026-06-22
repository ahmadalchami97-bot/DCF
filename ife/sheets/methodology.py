"""
Forecast Methodology.

A plain-English account of how the model works -- so anyone can audit it without
reverse-engineering a single cell. It states the design philosophy, how the
dynamic Actual/Forecast timeline is detected, the one-driver-per-line rule (with
every forecast formula written out in words), and why the model balances with no
plug and no circular reference.
"""

from __future__ import annotations

from .. import common
from ..common import FY_FMT
from ..config import DRIVERS

LAST = 10


def build(sh, ctx):
    common.title_block(sh, "FORECAST METHODOLOGY",
                       "How this model works -- and how to audit and update it", last_col=LAST)
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

    head("Design philosophy")
    para("This workbook prioritises, in strict order: TRANSPARENCY, CLARITY, AUDITABILITY and "
         "USABILITY -- ahead of sophistication, automation and flexibility. If a forecast number "
         "would require tracing through several layers, or a formula would need a paragraph to "
         "explain, the design was reconsidered instead. Every forecast line is one short formula "
         "driven by one assumption.", height=46)

    head("Two layers: historical = input, forecast = output")
    para("HISTORICAL (the Historical sheet) is the ACTUAL layer: every figure -- including the "
         "subtotals (gross profit, EBITDA, EBIT, net income, total assets, total liabilities) -- is "
         "a hard-coded blue input, pasted from the filings. Nothing on that sheet is reconstructed "
         "by a formula except explicit audit checks.", height=46)
    para("FORECAST (the Forecast sheet) is the OUTPUT layer: every figure is a formula. The two are "
         "never mixed, and they are shaded differently (blue 'Actual' headers vs green 'Forecast' "
         "headers) so they can never be confused.", height=32)
    para("Colour code:  blue = input  -  black = formula  -  green = key output  -  red = warning.",
         role="note_l")

    head("The dynamic timeline (forecasts begin after the last reported year)")
    para("The model counts the reported years on the Historical sheet and derives the last actual "
         "year automatically; the forecast begins the very next year. Paste in another year of "
         "actuals and the forecast shifts forward on its own -- no other edits, no overlap with a "
         "year that is now reported.", height=46)
    sh.put(r, 1, "First fiscal year", role="label_b")
    sh.put(r, 3, "=FirstYear", role="formula", fmt=FY_FMT)
    sh.put(r, 5, "(input on the Historical sheet)", role="note_l"); sh.merge(r, 5, r, LAST); r += 1
    sh.put(r, 1, "Last actual year", role="label_b")
    sh.put(r, 3, "=LastActual", role="output", fmt=FY_FMT)
    sh.put(r, 5, "auto-detected = FirstYear + reported years - 1", role="note_l"); sh.merge(r, 5, r, LAST); r += 1
    sh.put(r, 1, "Forecast window", role="label_b")
    sh.put(r, 3, f'="FY"&(LastActual+1)&"  to  FY"&(LastActual+{ctx.horizon})', role="output_l")
    sh.merge(r, 3, r, LAST); r += 2

    head("One driver per line")
    para("Each forecast line reads exactly one assumption from the Assumptions sheet. There is no "
         "scenario selector and no method engine -- to change the forecast you change a driver, and "
         "the link is a single visible hop.", height=32)
    sh.put(r, 1, "Driver", role="colhdr"); sh.merge(r, 1, r, 3)
    sh.put(r, 4, "Drives this forecast line", role="colhdr"); sh.merge(r, 4, r, LAST)
    r += 1
    for _key, label, _kind, drives in DRIVERS:
        sh.put(r, 1, label, role="label_b"); sh.merge(r, 1, r, 3)
        sh.put(r, 4, drives, role="note_l"); sh.merge(r, 4, r, LAST)
        r += 1
    r += 1

    head("The forecast, written out (t = each forecast year)")
    for line in [
        "Revenue        = prior revenue x (1 + revenue growth)",
        "EBITDA         = revenue x EBITDA margin",
        "D&A            = revenue x D&A%        EBIT = EBITDA - D&A",
        "Net interest   = net interest rate x OPENING net debt   (so there is no circularity)",
        "Pre-tax        = EBIT - net interest     Tax = tax rate x pre-tax     Net income = pre-tax - tax",
        "Net working capital = revenue x NWC%",
        "Net PP&E       = prior net PP&E + capex - D&A          Capex = revenue x capex%",
        "Other assets / other liabilities = held flat at the last actual",
        "Total debt     = prior debt + net new debt",
        "Equity         = prior equity + net income - dividends   Dividends = payout x max(0, net income)",
        "Cash           = prior cash + CFO + CFI + CFF            (the residual -- no plug)",
        "CFO = net income + D&A - increase in NWC ;  CFI = -capex ;  CFF = net new debt - dividends",
    ]:
        para(line, role="formula_l")
    r += 1

    head("Why it balances -- with no plug and no circular reference")
    para("Every non-cash balance-sheet movement flows through the cash-flow statement, and cash is "
         "their residual. So the change in assets always equals the change in liabilities plus "
         "equity, and Assets = Liabilities + Equity holds to the cent every year -- the balance "
         "check is exactly 0. Because net interest is charged on the OPENING net-debt balance "
         "(last year's closing figure, already known), the interest-debt-cash loop never forms: no "
         "iterative calculation, no macros, no VBA.", height=60)

    head("How to update")
    para("1) Paste a new year of reported actuals into the next empty column on the Historical "
         "sheet -- the forecast extends and shifts automatically.   2) Review the Assumptions grid "
         "(one driver per row).   3) Read the Forecast, Bridge and Diagnostics. The Diagnostics "
         "Health Score should be 100; investigate any WARN or FAIL.", height=46)

    head("Limitations")
    para("Net interest uses opening balances (an institutional norm that keeps the model "
         "circularity-free). Other assets and other liabilities are held flat -- adjust on the "
         "Forecast sheet if they are material to your company. This is an analytical tool to support "
         "judgement, not investment advice.", height=46)

    sh.col_width(1, 22)
    for c in range(2, LAST + 1):
        sh.col_width(c, 11)
    return sh
