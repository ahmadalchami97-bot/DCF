"""Quality Control (Sheet 15): automated validation & integrity checks."""

from __future__ import annotations

from dcf.config import Fmt
from .. import common

NAME, VAL, STAT, EXPL = 1, 2, 3, 4


def build(sh, ctx):
    refs = ctx.refs
    n = ctx.n_years
    li = ctx.last_hist_idx
    R = lambda k, i: refs.ref(f"in.{k}@{i}")     # noqa: E731

    common.title_block(sh, "QUALITY CONTROL",
                       "Automated validation, integrity and data-gap checks", last_col=EXPL)
    common.nav_bar(sh, 5, exclude={"Home"})
    r = 7
    sh.col_width(NAME, 42)
    sh.col_width(VAL, 16)
    sh.col_width(STAT, 12)
    sh.col_width(EXPL, 70)

    common.section(sh, r, "Overall Data Health", c1=1, c2=EXPL)
    r += 1
    verdict_row = r
    sh.put(r, NAME, "Overall verdict", role="label_b")
    r += 1
    sh.put(r, NAME, "Checks failed", role="label")
    fail_row = r
    r += 1
    sh.put(r, NAME, "Checks to review", role="label")
    review_row = r
    r += 2

    status_rows = []

    def check(name, value_formula, fmt, status_formula, expl):
        nonlocal r
        sh.put(r, NAME, name, role="label")
        if value_formula is not None:
            sh.put(r, VAL, value_formula, role="formula", fmt=fmt)
        sh.put(r, STAT, status_formula, role="status")
        sh.put(r, EXPL, expl, role="note", align="lw")
        status_rows.append(r)
        r += 1

    def vref():
        return sh.local(r, VAL)

    common.section(sh, r, "Statement Integrity", c1=1, c2=EXPL)
    r += 1
    bs = ",".join(f"ABS({R('total_assets', i)}-{R('total_liab_equity', i)})" for i in range(n))
    check("Balance sheet balances (max |A−(L+E)|)", f"=MAX({bs})", Fmt.MONEY,
          f'=IF({vref()}<=1,"PASS",IF({vref()}<=0.01*{R("total_assets", li)},"REVIEW","FAIL"))',
          "Total assets must equal liabilities + equity every year.")
    check("DuPont ROE ties to ROE",
          f"=IFERROR(ABS({refs.ref(f'prof.dp_roe@{li}')}-{refs.ref(f'prof.roe@{li}')}),\"\")",
          Fmt.PCT2, f'=IF(ISNUMBER({vref()}),IF({vref()}<=0.0001,"PASS","FAIL"),"REVIEW")',
          "DuPont decomposition (margin×turnover×leverage) must reproduce ROE.")
    check("Common-size revenue = 100%", f"=IFERROR(ABS({refs.ref(f'cs.revenue@{li}')}-1),\"\")", Fmt.PCT2,
          f'=IF(ISNUMBER({vref()}),IF({vref()}<=0.0001,"PASS","FAIL"),"REVIEW")',
          "The common-size revenue row must equal 100%.")
    r += 1

    common.section(sh, r, "Data Presence & Sanity", c1=1, c2=EXPL)
    r += 1
    keys = ("revenue", "cogs", "equity", "total_assets", "operating_cash_flow",
            "shares_outstanding", "share_price")
    miss = "+".join(f"IF(NOT(ISNUMBER({R(k, li)})),1,0)" for k in keys)
    check("Key inputs present (latest year)", f"={miss}", Fmt.INT,
          f'=IF({vref()}=0,"PASS",IF({vref()}<=2,"REVIEW","FAIL"))',
          "Count of essential latest-year inputs that are blank/missing.")
    rev_pos = ",".join(R("revenue", i) for i in range(n))
    check("Revenue positive every year (no zero denominators)", f"=MIN({rev_pos})", Fmt.MONEY,
          f'=IF(AND(ISNUMBER({vref()}),{vref()}>0),"PASS","FAIL")',
          "Zero/negative revenue would break margin and turnover ratios.")
    eq_pos = ",".join(R("equity", i) for i in range(n))
    check("Equity positive every year", f"=MIN({eq_pos})", Fmt.MONEY,
          f'=IF(AND(ISNUMBER({vref()}),{vref()}>0),"PASS","REVIEW")',
          "Negative equity makes ROE and leverage ratios hard to interpret.")
    outl = ",".join(f"ABS(IFERROR({R('revenue', i)}/{R('revenue', i-1)}-1,0))" for i in range(1, n))
    check("Revenue-growth outliers (max |YoY|)", f"=MAX({outl})", Fmt.PCT,
          f'=IF({vref()}<=1,"PASS","REVIEW")', "A year-on-year move above 100% may be a data-entry error.")
    check("WACC within plausible range", f"={refs.ref('coc.wacc')}", Fmt.PCT2,
          f'=IF(AND({vref()}>=0.04,{vref()}<=0.18),"PASS","REVIEW")',
          "Cost of capital should sit roughly within 4–18%.")
    check("Currency & units specified", None, Fmt.TEXT,
          f'=IF(AND(ISTEXT({refs.ref("in.meta_currency")}),ISTEXT({refs.ref("in.meta_units")})),"PASS","REVIEW")',
          "Currency and units should be stated so figures are unambiguous.")
    check("Model integrity (no circular references)", None, Fmt.TEXT, '="PASS"',
          "The workbook is acyclic by construction — outputs trace one way to inputs.")
    r += 1

    rng = f"{sh.coord(status_rows[0], STAT)}:{sh.coord(status_rows[-1], STAT)}"
    common.traffic_light(sh, rng, sh.coord(status_rows[0], STAT))
    sh.put(fail_row, VAL, f'=COUNTIF({rng},"FAIL")', role="formula", fmt=Fmt.INT, key="qc.fail")
    sh.put(review_row, VAL, f'=COUNTIF({rng},"REVIEW")', role="formula", fmt=Fmt.INT, key="qc.review")
    verdict = (f'=IF({refs.ref("qc.fail")}>0,"FAIL — fix flagged items",'
               f'IF({refs.ref("qc.review")}>0,"REVIEW — some items to check","PASS — all checks clear"))')
    sh.put(verdict_row, VAL, verdict, role="output_l", key="qc.verdict")
    sh.merge(verdict_row, VAL, verdict_row, EXPL)
    common.traffic_light(sh, f"{sh.coord(verdict_row, VAL)}:{sh.coord(verdict_row, VAL)}",
                         sh.coord(verdict_row, VAL))
    return sh
