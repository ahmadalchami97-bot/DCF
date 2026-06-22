"""
Forecast Diagnostics.

A focused audit: accounting integrity (do the actuals tie? does the forecast
balance sheet balance?) plus reasonableness checks on growth, margins, cash,
equity, debt, working capital, capex and tax. Each row shows a value, a
PASS / WARN / FAIL status and a plain-English description. A Forecast Health
Score (0-100) summarises the result.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..config import Thresholds as T

NAME, VAL, STAT, DESC = 1, 2, 3, 4


def build(sh, ctx):
    refs = ctx.refs
    N = ctx.horizon
    slots = ctx.hist_slots
    fr = lambda k: refs.range(f"f.{k}@1", f"f.{k}@{N}")              # noqa: E731
    ar = lambda k: refs.range(f"a.{k}@1", f"a.{k}@{N}")             # noqa: E731
    hr = lambda k: refs.range(f"h.{k}@0", f"h.{k}@{slots - 1}")     # noqa: E731
    F = lambda k, t: refs.ref(f"f.{k}@{t}")                          # noqa: E731

    common.title_block(sh, "FORECAST DIAGNOSTICS",
                       "Accounting integrity, reasonableness checks and the Forecast Health Score",
                       last_col=DESC)
    common.nav_bar(sh, 5)
    r = 7
    sh.col_width(NAME, 34)
    sh.col_width(VAL, 14)
    sh.col_width(STAT, 12)
    sh.col_width(DESC, 76)

    common.section(sh, r, "Forecast Health", c1=1, c2=DESC)
    r += 1
    sh.put(r, NAME, "Forecast Health Score (0-100)", role="label_b")
    health_row = r
    r += 2

    rows = []

    def check(name, value, fmt, status, desc):
        nonlocal r
        sh.put(r, NAME, name, role="label")
        if value is not None:
            sh.put(r, VAL, value, role="formula", fmt=fmt)
        sh.put(r, STAT, status, role="status")
        sh.put(r, DESC, desc, role="note", align="lw")
        rows.append(r)
        r += 1

    def v():
        return sh.local(r, VAL)

    common.section(sh, r, "Accounting Integrity", c1=1, c2=DESC)
    r += 1
    cnt = refs.ref("t.count")
    check("Historical data present", f"={cnt}", Fmt.INT,
          f'=IF({v()}>=1,"PASS","FAIL")',
          "Counts the reported years entered on the Historical sheet. Fails on a blank template.")
    htie = f"MAX(MAX({hr('balance_check')}),-MIN({hr('balance_check')}))"
    check("Historical statements tie", f"={htie}", Fmt.MONEY,
          f'=IF({v()}<={T.BALANCE_TOL},"PASS","FAIL")',
          "Largest |assets - (liabilities + equity)| across the actual years (should be 0).")
    btie = f"MAX(MAX({fr('balance_check')}),-MIN({fr('balance_check')}))"
    check("Forecast Assets = Liab + Equity", f"={btie}", Fmt.MONEY,
          f'=IF({v()}<={T.BALANCE_TOL},"PASS","FAIL")',
          "Largest forecast imbalance (the model reconciles with no plug, so this is 0).")
    r += 1

    common.section(sh, r, "Forecast Reasonableness", c1=1, c2=DESC)
    r += 1
    check("Revenue growth", f"=MAX({ar('rev_growth')})", Fmt.PCT,
          f'=IF(AND(MAX({ar("rev_growth")})<={T.REV_GROWTH_HI},MIN({ar("rev_growth")})>={T.REV_GROWTH_LO}),"PASS","WARN")',
          f"Warns if any year's growth exceeds {int(T.REV_GROWTH_HI*100)}% or falls below {int(T.REV_GROWTH_LO*100)}%.")
    drift = f"(IFERROR({F('ebitda', N)}/{F('revenue', N)},0)-IFERROR({F('ebitda', 1)}/{F('revenue', 1)},0))/{max(N-1,1)}"
    check("EBITDA-margin drift (per year)", f"={drift}", Fmt.PCT,
          f'=IF(ABS({v()})<={T.MARGIN_DRIFT_BPS},"PASS","WARN")',
          f"Warns if EBITDA margin drifts more than {int(T.MARGIN_DRIFT_BPS*10000)} bps per year on average.")
    check("Positive cash", f"=MIN({fr('cash')})", Fmt.MONEY,
          f'=IF({v()}>=0,"PASS","FAIL")', "Fails if the forecast runs cash negative (there is no revolver plug).")
    check("Positive equity", f"=MIN({fr('equity')})", Fmt.MONEY,
          f'=IF({v()}>=0,"PASS","FAIL")', "Fails if forecast equity turns negative.")
    check("Non-negative debt", f"=MIN({fr('total_debt')})", Fmt.MONEY,
          f'=IF({v()}>=0,"PASS","WARN")', "Warns if net repayment drives the debt balance below zero.")
    check("Working capital intensity", f"=MAX({ar('nwc_pct')})", Fmt.PCT,
          f'=IF({v()}<={T.NWC_PCT_HI},"PASS","WARN")', f"Warns if net working capital exceeds {int(T.NWC_PCT_HI*100)}% of revenue.")
    check("Capex intensity", f"=MAX({ar('capex_pct')})", Fmt.PCT,
          f'=IF({v()}<={T.CAPEX_PCT_HI},"PASS","WARN")', f"Warns if capex exceeds {int(T.CAPEX_PCT_HI*100)}% of revenue.")
    check("Tax rate", f"=MAX({ar('tax_rate')})", Fmt.PCT,
          f'=IF(AND(MAX({ar("tax_rate")})<={T.TAX_HI},MIN({ar("tax_rate")})>={T.TAX_LO}),"PASS","WARN")',
          f"Warns if the tax rate falls outside {int(T.TAX_LO*100)}-{int(T.TAX_HI*100)}%.")
    r += 1

    rng = f"{sh.coord(rows[0], STAT)}:{sh.coord(rows[-1], STAT)}"
    common.traffic_light(sh, rng, sh.coord(rows[0], STAT))
    total = len(rows)
    health = f'=ROUND((COUNTIF({rng},"PASS")+0.5*COUNTIF({rng},"WARN"))/{total}*100,0)'
    sh.put(health_row, VAL, health, role="kpi", fmt=Fmt.INT, key="d.health")
    sh.merge(health_row, VAL, health_row, STAT)
    sh.put(health_row, DESC, "100 = every check passes. WARN counts as half; FAIL as zero.", role="note")
    sh.put(health_row + 1, NAME, "Checks failed / to review", role="label")
    sh.put(health_row + 1, VAL, f'=COUNTIF({rng},"FAIL")&" / "&COUNTIF({rng},"WARN")',
           role="formula_l", key="d.fails")
    sh.merge(health_row + 1, VAL, health_row + 1, STAT)
    return sh
