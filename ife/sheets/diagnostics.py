"""
Forecast Diagnostics (Sheet 7).

A comprehensive audit: accounting integrity plus reasonableness checks on growth,
margins, cash, equity, debt, working capital, capex and tax. Each shows a value,
a PASS / WARN / FAIL status and a plain-English description. A Forecast Health
Score (0–100) summarises the result.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..config import Thresholds as T

NAME, VAL, STAT, DESC = 1, 2, 3, 4


def build(sh, ctx):
    refs = ctx.refs
    N = ctx.fcst
    li = ctx.last_hist
    fr = lambda k: refs.range(f"f.{k}@1", f"f.{k}@{N}")     # noqa: E731 forecast range
    ar = lambda k: refs.range(f"a.{k}@1", f"a.{k}@{N}")     # noqa: E731 driver range
    A = lambda k, t: refs.ref(f"a.{k}@{t}")                 # noqa: E731
    F = lambda k, t: refs.ref(f"f.{k}@{t}")                 # noqa: E731

    common.title_block(sh, "FORECAST DIAGNOSTICS",
                       "Accounting integrity, reasonableness checks and the Forecast Health Score",
                       last_col=DESC)
    common.nav_bar(sh, 5)
    r = 7
    sh.col_width(NAME, 34)
    sh.col_width(VAL, 14)
    sh.col_width(STAT, 12)
    sh.col_width(DESC, 74)

    common.section(sh, r, "Forecast Health", c1=1, c2=DESC)
    r += 1
    sh.put(r, NAME, "Forecast Health Score (0–100)", role="label_b")
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
    hrev, heq = refs.ref(f"h.revenue@{li}"), refs.ref(f"h.equity@{li}")
    check("Historical data present", f"={hrev}", Fmt.MONEY,
          f'=IF(AND(ISNUMBER({hrev}),ISNUMBER({heq})),"PASS","FAIL")',
          "Fails until the historical statements (Sheet 2) are populated.")
    bal = f"MAX(MAX({fr('balance_check')}),-MIN({fr('balance_check')}))"
    check("Assets = Liabilities + Equity", f"={bal}", Fmt.MONEY,
          f'=IF({v()}<={T.BALANCE_TOL},"PASS","FAIL")',
          "Largest absolute balance-sheet imbalance across the forecast (should be 0).")
    r += 1

    common.section(sh, r, "Forecast Reasonableness", c1=1, c2=DESC)
    r += 1
    check("Revenue growth", f"=MAX({ar('rev_growth')})", Fmt.PCT,
          f'=IF(AND(MAX({ar("rev_growth")})<={T.REV_GROWTH_HI},MIN({ar("rev_growth")})>={T.REV_GROWTH_LO}),"PASS","WARN")',
          f"Warns if any year's growth exceeds {int(T.REV_GROWTH_HI*100)}% or falls below {int(T.REV_GROWTH_LO*100)}%.")
    exp = f"({F('ebitda', N)}/{F('revenue', N)}-{F('ebitda', 1)}/{F('revenue', 1)})/{N-1}"
    check("EBITDA-margin drift (per year)", f"=IFERROR({exp},0)", Fmt.PCT,
          f'=IF(ABS({v()})<={T.MARGIN_EXPAND_BPS},"PASS","WARN")',
          "Warns if margins expand/contract too mechanically (avg annual change too large).")
    check("Positive cash", f"=MIN({fr('cash')})", Fmt.MONEY,
          f'=IF({v()}>=0,"PASS","FAIL")', "Fails if the forecast runs the cash balance negative (no revolver plug).")
    check("Positive equity", f"=MIN({fr('equity')})", Fmt.MONEY,
          f'=IF({v()}>=0,"PASS","FAIL")', "Fails if forecast equity turns negative.")
    check("Non-negative debt", f"=MIN({fr('long_term_debt')})", Fmt.MONEY,
          f'=IF({v()}>=0,"PASS","WARN")', "Warns if repayment over-runs the debt balance.")
    ccc = f"{A('dso', N)}+{A('dio', N)}-{A('dpo', N)}"
    check("Working-capital cycle (days)", f"={ccc}", Fmt.FLOAT1,
          f'=IF({v()}<={T.WC_DAYS_HI},"PASS","WARN")', "Warns if the cash-conversion cycle is implausibly long.")
    check("Capex intensity", f"=MAX({ar('capex_pct')})", Fmt.PCT,
          f'=IF({v()}<={T.CAPEX_PCT_HI},"PASS","WARN")', f"Warns if capex exceeds {int(T.CAPEX_PCT_HI*100)}% of revenue.")
    check("Tax rate", f"=MAX({ar('tax_rate')})", Fmt.PCT,
          f'=IF(AND(MAX({ar("tax_rate")})<={T.TAX_HI},MIN({ar("tax_rate")})>={T.TAX_LO}),"PASS","WARN")',
          f"Warns if the tax rate falls outside {int(T.TAX_LO*100)}–{int(T.TAX_HI*100)}%.")
    r += 1

    rng = f"{sh.coord(rows[0], STAT)}:{sh.coord(rows[-1], STAT)}"
    common.traffic_light(sh, rng, sh.coord(rows[0], STAT))
    total = len(rows)
    health = (f'=ROUND((COUNTIF({rng},"PASS")+0.5*COUNTIF({rng},"WARN"))/{total}*100,0)')
    sh.put(health_row, VAL, health, role="kpi", fmt=Fmt.INT, key="d.health")
    sh.merge(health_row, VAL, health_row, STAT)
    sh.put(health_row, DESC, "100 = every check passes. WARN counts as half; FAIL as zero.", role="note")
    sh.put(health_row + 1, NAME, "Checks failed / to review", role="label")
    sh.put(health_row + 1, VAL, f'=COUNTIF({rng},"FAIL")&" / "&COUNTIF({rng},"WARN")',
           role="formula_l", key="d.fails")
    sh.merge(health_row + 1, VAL, health_row + 1, STAT)
    return sh
