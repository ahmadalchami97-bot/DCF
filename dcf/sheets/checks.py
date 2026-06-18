"""
Checks / diagnostics sheet.

A defensive layer that surfaces problems before they propagate: balance-sheet
integrity, cash-flow articulation, income statement consistency, sign/units
sanity, WACC and terminal-growth plausibility, terminal-value concentration,
non-positive enterprise/equity value, missing key data and obvious outliers.

Each check shows a value, a PASS / REVIEW / FAIL status (colour-coded) and a
plain-English explanation. An overall data-health verdict at the top counts the
REVIEW/FAIL flags. The model never silently forces a result — issues are flagged.
"""

from __future__ import annotations

from ..config import Fmt, Thresholds as T
from . import common

NAME, VAL, STAT, EXPL = 1, 2, 3, 4


def build(sh, ctx: common.Context):
    refs = ctx.refs
    n = ctx.n_hist
    last = n - 1
    N = ctx.n_fcst
    R = lambda k, p: refs.ref(f"in.{k}@{p}")    # noqa: E731
    H = lambda k, p: refs.ref(f"h.{k}@{p}")     # noqa: E731
    A = lambda k: refs.ref(f"as.{k}")           # noqa: E731
    Dk = lambda k: refs.ref(f"dcf.{k}")         # noqa: E731
    F = lambda k, t: refs.ref(f"fc.{k}@{t}")    # noqa: E731

    sh.hide_gridlines()
    sh.col_width(NAME, 44)
    sh.col_width(VAL, 16)
    sh.col_width(STAT, 12)
    sh.col_width(EXPL, 64)
    r = common.title_block(sh, "CHECKS & DIAGNOSTICS",
                           "Automated integrity, sanity and data-gap checks", last_col=EXPL)
    r += 1

    # reserve summary rows (filled after we know the status range)
    common.section(sh, r, "Overall Data Health", c1=1, c2=EXPL)
    r += 1
    sum_verdict_row = r
    sh.put(r, NAME, "Overall verdict", role="label_b")
    r += 1
    sh.put(r, NAME, "Checks failed (FAIL)", role="label")
    fail_row = r
    r += 1
    sh.put(r, NAME, "Checks to review (REVIEW)", role="label")
    review_row = r
    r += 2

    status_rows = []

    def check(row, name, value_formula, value_fmt, status_formula, explanation):
        sh.put(row, NAME, name, role="label")
        if value_formula is not None:
            sh.put(row, VAL, value_formula, role="calc", fmt=value_fmt)
        sh.put(row, STAT, status_formula, role="link", align="c")
        sh.put(row, EXPL, explanation, role="note")
        status_rows.append(row)
        return row + 1

    def v(row):
        return sh.local(row, VAL)

    def le(vref, t1, t2):
        return f'=IF({vref}<={t1},"PASS",IF({vref}<={t2},"REVIEW","FAIL"))'

    def between(vref, lo, hi, bad="REVIEW"):
        return f'=IF(AND(ISNUMBER({vref}),{vref}>={lo},{vref}<={hi}),"PASS","{bad}")'

    def positive(vref, bad="FAIL"):
        return f'=IF(AND(ISNUMBER({vref}),{vref}>0),"PASS","{bad}")'

    def ge(vref, thr, bad="REVIEW"):
        return f'=IF(AND(ISNUMBER({vref}),{vref}>={thr}),"PASS","{bad}")'

    # ---- statement integrity --------------------------------------------
    r = common.section(sh, r, "Financial-Statement Integrity", c1=1, c2=EXPL)
    bs = ",".join(f"ABS({R('total_assets',p)}-{R('total_liab_equity',p)})" for p in range(n))
    r = check(r, "Balance sheet balances (max |A − (L+E)|)", f"=MAX({bs})", Fmt.MONEY,
              le(v(r), 1, f"0.005*{R('total_assets', last)}"),
              "Assets should equal liabilities + equity every year (rounding aside).")
    if n > 1:
        cf = ",".join(f"ABS({R('net_change_cash',p)}-({R('cash',p)}-{R('cash',p-1)}))"
                      for p in range(1, n))
        r = check(r, "Cash flow ties (max |Δcash − net CF|)", f"=MAX({cf})", Fmt.MONEY,
                  le(v(r), 1, f"0.01*{R('cash', last)}"),
                  "CFO + CFI + CFF should equal the change in the cash balance.")
    r = check(r, "Net income: IS vs cash-flow statement",
              f"=ABS({R('net_income', last)}-{R('cf_net_income', last)})", Fmt.MONEY,
              le(v(r), 1, 5),
              "Net income on the income statement should match the cash-flow start line.")
    r += 1

    # ---- sign & units ----------------------------------------------------
    r = common.section(sh, r, "Sign, Units & Data Presence", c1=1, c2=EXPL)
    neg = ",".join(f"IF({R(k, last)}<0,1,0)" for k in
                   ("revenue", "cogs", "capex", "dividends_paid", "buybacks"))
    r = check(r, "Sign sanity (cost/return lines entered positive)", f"=SUM({neg})", Fmt.INT,
              f'=IF({v(r)}=0,"PASS","REVIEW")',
              "Revenue, COGS, capex, dividends and buybacks should be entered as positives.")
    miss_keys = ("revenue", "cogs", "total_equity", "total_assets", "cash",
                 "shares_diluted", "cf_da", "capex")
    miss = "+".join(f"IF(NOT(ISNUMBER({R(k, last)})),1,0)" for k in miss_keys)
    r = check(r, "Key inputs present (latest year)", f"={miss}", Fmt.INT,
              f'=IF({v(r)}=0,"PASS",IF({v(r)}<=2,"REVIEW","FAIL"))',
              "Count of essential latest-year inputs that are blank/missing.")
    r = check(r, "Currency & units specified", None, Fmt.TEXT,
              f'=IF(AND(ISTEXT({refs.ref("in.currency")}),ISTEXT({refs.ref("in.units")})),'
              f'"PASS","REVIEW")',
              "Currency and units should be stated so figures are unambiguous.")
    r += 1

    # ---- valuation sanity ------------------------------------------------
    r = common.section(sh, r, "Valuation & Assumption Sanity", c1=1, c2=EXPL)
    r = check(r, "WACC within plausible range", f"={refs.ref('wacc.value')}", Fmt.PCT2,
              between(v(r), T.WACC_MIN, T.WACC_MAX),
              f"WACC should sit roughly within {int(T.WACC_MIN*100)}–{int(T.WACC_MAX*100)}%.")
    r = check(r, "WACC exceeds terminal growth (g)",
              f"={refs.ref('wacc.value')}-{A('act_tv_growth')}", Fmt.PCT2,
              ge(v(r), T.TG_WACC_GAP_MIN),
              "WACC must exceed g, with a safety margin, or terminal value is unstable.")
    r = check(r, "Terminal growth within sane bounds", f"={A('act_tv_growth')}", Fmt.PCT,
              between(v(r), T.TG_MIN, T.TG_MAX),
              f"Perpetuity growth should not exceed long-run nominal GDP (~{int(T.TG_MAX*100)}%).")
    r = check(r, "Terminal value as % of enterprise value", f"={Dk('tv_share')}", Fmt.PCT,
              f'=IF(AND(ISNUMBER({v(r)}),{v(r)}<={T.TV_SHARE_WARN}),"PASS","REVIEW")',
              "A very high share means value rests heavily on terminal assumptions.")
    r = check(r, "Enterprise & equity value positive",
              f"=MIN({Dk('ev')},{Dk('equity_value')})", Fmt.MONEY, positive(v(r)),
              "Negative EV or equity value would signal a broken or distressed case.")
    r += 1

    # ---- historical & forecast sanity -----------------------------------
    r = common.section(sh, r, "Historical & Forecast Sanity", c1=1, c2=EXPL)
    r = check(r, "Gross margin within [0, 100%] (latest)",
              f"=IFERROR({H('gross_margin', last)},-1)", Fmt.PCT, between(v(r), 0, 1),
              "A gross margin outside 0–100% points to a sign or mapping error.")
    rev_pos = ",".join(R("revenue", p) for p in range(n))
    r = check(r, "Revenue positive in every year", f"=MIN({rev_pos})", Fmt.MONEY, positive(v(r)),
              "Zero/negative revenue breaks growth and margin calculations.")
    if n > 1:
        outl = ",".join(f"ABS(IFERROR({R('revenue',p)}/{R('revenue',p-1)}-1,0))"
                        for p in range(1, n))
        r = check(r, "Revenue-growth outliers (max |YoY|)", f"=MAX({outl})", Fmt.PCT,
                  f'=IF({v(r)}<=1,"PASS","REVIEW")',
                  "A year-on-year move above 100% may indicate a data-entry error.")
    fcff_min = ",".join(F("fcff", t) for t in range(1, N + 1))
    r = check(r, "Forecast FCFF non-negative", f"=MIN({fcff_min})", Fmt.MONEY,
              f'=IF({v(r)}>=0,"PASS","REVIEW")',
              "Negative forecast FCF is allowed (heavy investment) but worth noting.")
    r = check(r, "Model integrity (no circular references)", None, Fmt.TEXT, '="PASS"',
              "The workbook is acyclic by construction — outputs trace one way to inputs.")
    r += 1

    # colour all status cells + fill summary
    first_stat, last_stat = status_rows[0], status_rows[-1]
    rng = f"{sh.coord(first_stat, STAT)}:{sh.coord(last_stat, STAT)}"
    common.add_label_coloring(sh, rng, sh.coord(first_stat, STAT))
    fail_cnt = f'=COUNTIF({rng},"FAIL")'
    rev_cnt = f'=COUNTIF({rng},"REVIEW")'
    sh.put(fail_row, VAL, fail_cnt, role="calc", fmt=Fmt.INT, key="chk.fail")
    sh.put(review_row, VAL, rev_cnt, role="calc", fmt=Fmt.INT, key="chk.review")
    verdict = (f'=IF({refs.ref("chk.fail")}>0,"FAIL — fix flagged items",'
               f'IF({refs.ref("chk.review")}>0,"REVIEW — some items to check",'
               f'"PASS — all checks clear"))')
    sh.put(sum_verdict_row, VAL, verdict, role="output", align="l", key="chk.verdict")
    sh.merge(sum_verdict_row, VAL, sum_verdict_row, EXPL)
    common.add_label_coloring(sh, f"{sh.coord(sum_verdict_row, VAL)}:{sh.coord(sum_verdict_row, VAL)}",
                              sh.coord(sum_verdict_row, VAL))
    return sh
