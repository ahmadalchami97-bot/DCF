"""
Assumption Center (Sheet 4) — the most important sheet; everything flows from here.

Three layers:
  1. Historical Reference: 3/5/10-year averages of every driver (from Analysis).
  2. Manual Assumptions: Bear / Base / Bull targets (blue inputs) + the
     scenario-selected value.
  3. Active Forecast Drivers: the per-year value the Forecast actually uses,
     resolved by the Method × Scenario engine via CHOOSE() over named ranges:

        Historical Trend -> the 5-year average (flat)
        Manual           -> the selected scenario target (flat)
        Hybrid           -> fades from the 5y average to the target over the horizon

Method and Scenario are real dropdowns backed by named ranges, so changing either
re-prices every downstream sheet instantly.
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common
from ..config import METHODS, SCENARIOS, DEFAULT_METHOD, DEFAULT_SCENARIO

PCT, DAYS, MONEY = Fmt.PCT, Fmt.DAYS, Fmt.MONEY

# (key, label, fmt, ha_metric)  — Group 1 (method+scenario, has history)
G1 = [
    ("rev_growth", "Revenue growth %", PCT, "rev_growth"),
    ("gross_margin", "Gross margin %", PCT, "gross_margin"),
    ("ebitda_margin", "EBITDA margin %", PCT, "ebitda_margin"),
    ("tax_rate", "Tax rate %", PCT, "tax_rate"),
    ("dso", "Receivable days", DAYS, "dso"),
    ("dio", "Inventory days", DAYS, "dio"),
    ("dpo", "Payable days", DAYS, "dpo"),
    ("capex_pct", "Capex % revenue", PCT, "capex_pct"),
    ("da_pct", "D&A % revenue", PCT, "da_pct"),
    ("cash_pct", "Cash % revenue", PCT, "cash_pct"),
    ("oa_pct", "Other assets % revenue", PCT, "oa_pct"),
    ("ol_pct", "Other liabilities % revenue", PCT, "ol_pct"),
    ("int_rate", "Interest rate %", PCT, "int_rate"),
]
# (key, label, fmt) — Group 2 (scenario-only, no historical anchor)
G2 = [
    ("dividend_payout", "Dividend payout %", PCT),
    ("debt_repay_pct", "Debt repayment % (of LT debt)", PCT),
    ("new_debt", "New debt raised (amount/yr)", MONEY),
    ("cash_yield", "Yield on cash %", PCT),
]


def build(sh, ctx):
    refs = ctx.refs
    N = ctx.fcst
    li = ctx.last_hist
    A = lambda k: refs.ref(f"a.{k}")            # noqa: E731
    HA = lambda m, a, b: refs.range(f"ha.{m}@{a}", f"ha.{m}@{b}")  # noqa: E731
    last = common.FIRST_COL + N - 1

    common.title_block(sh, "ASSUMPTION CENTER",
                       "Drivers, scenarios and the forecast-method engine — everything flows from here",
                       last_col=max(last, 11))
    common.nav_bar(sh, 5)
    r = 7

    # ---- forecast controls ----
    r = common.section(sh, r, "Forecast Controls", c1=1, c2=11)
    sh.put(r, 1, "Forecast method", role="label_b")
    sh.put(r, 2, METHODS[DEFAULT_METHOD - 1], role="input_l", key="a.method_name")
    common.dropdown(sh, r, 2, METHODS)
    sh.merge(r, 2, r, 4)
    sh.put(r, 5, DEFAULT_METHOD, role="input", fmt=Fmt.INT, key="a.method")
    sh.put(r, 6, "← method # (1=Trend, 2=Manual, 3=Hybrid)", role="note_l")
    sh.merge(r, 6, r, 11)
    common.define_name(sh, "Method", r, 5)
    common.dropdown(sh, r, 5, ["1", "2", "3"])
    r += 1
    sh.put(r, 1, "Scenario", role="label_b")
    sh.put(r, 2, SCENARIOS[DEFAULT_SCENARIO - 1], role="input_l", key="a.scenario_name")
    common.dropdown(sh, r, 2, SCENARIOS)
    sh.merge(r, 2, r, 4)
    sh.put(r, 5, DEFAULT_SCENARIO, role="input", fmt=Fmt.INT, key="a.scenario")
    sh.put(r, 6, "← scenario # (1=Bear, 2=Base, 3=Bull)", role="note_l")
    sh.merge(r, 6, r, 11)
    common.define_name(sh, "Scenario", r, 5)
    common.dropdown(sh, r, 5, ["1", "2", "3"])
    r += 1
    sh.put(r, 1, "Forecast horizon (years)", role="label")
    sh.put(r, 2, N, role="formula", fmt=Fmt.INT, key="a.horizon")
    r += 2

    # ---- historical reference ----
    r = common.section(sh, r, "Historical Reference — Averages (from Analysis)", c1=1, c2=11)
    sh.put(r, 1, "Driver", role="colhdr")
    sh.put(r, 2, "3-Year", role="colhdr_r")
    sh.put(r, 3, "5-Year", role="colhdr_r")
    sh.put(r, 4, "10-Year", role="colhdr_r")
    r += 1
    for key, label, fmt, m in G1:
        sh.put(r, 1, label, role="label")
        sh.put(r, 2, f'=IFERROR(AVERAGE({HA(m, li-2, li)}),"")', role="formula", fmt=fmt, key=f"a.{key}.avg3")
        sh.put(r, 3, f'=IFERROR(AVERAGE({HA(m, li-4, li)}),"")', role="formula", fmt=fmt, key=f"a.{key}.avg5")
        sh.put(r, 4, f'=IFERROR(AVERAGE({HA(m, 0, li)}),"")', role="formula", fmt=fmt, key=f"a.{key}.avg10")
        r += 1
    r += 1

    # ---- manual assumptions ----
    r = common.section(sh, r, "Manual Assumptions by Scenario  (blue = input)", c1=1, c2=11)
    for col, t in ((1, "Driver"), (2, "Bear"), (3, "Base"), (4, "Bull"), (5, "Selected")):
        sh.put(r, col, t, role="colhdr" if col == 1 else "colhdr_r")
    r += 1
    asm = ctx.data.get("assumptions", {})
    for key, label, fmt, *_ in [(k, l, f, None) for (k, l, f, _) in G1] + [(k, l, f, None) for (k, l, f) in G2]:
        bear, base, bull = asm.get(key, (None, None, None))
        sh.put(r, 1, label, role="label")
        sh.put(r, 2, bear, role="input", fmt=fmt, key=f"a.{key}.bear")
        sh.put(r, 3, base, role="input", fmt=fmt, key=f"a.{key}.base")
        sh.put(r, 4, bull, role="input", fmt=fmt, key=f"a.{key}.bull")
        sh.put(r, 5, f"=CHOOSE(Scenario,{A(key+'.bear')},{A(key+'.base')},{A(key+'.bull')})",
               role="formula", fmt=fmt, key=f"a.{key}.sel")
        r += 1
    r += 1

    # ---- active forecast drivers ----
    r = common.section(sh, r, "Active Forecast Drivers  (resolved by Method × Scenario)", c1=1, c2=last)
    sh.put(r, 1, "Driver", role="colhdr")
    for t in range(1, N + 1):
        sh.put(r, common.FIRST_COL + t - 1, ctx.fcst_periods[t - 1], role="colhdr_r")
    r += 1
    for key, label, fmt, m in G1:
        sh.put(r, 1, label, role="label")
        avg5, sel = A(f"{key}.avg5"), A(f"{key}.sel")
        for t in range(1, N + 1):
            frac = t / N
            # robust to missing history: if no average, use the manual value
            f = (f"=IF(ISNUMBER({avg5}),CHOOSE(Method,{avg5},{sel},{avg5}+({sel}-{avg5})*{frac:.4f}),{sel})")
            sh.put(r, common.FIRST_COL + t - 1, f, role="output", fmt=fmt, key=f"a.{key}@{t}")
        r += 1
    for key, label, fmt in G2:
        sh.put(r, 1, label, role="label")
        sel = A(f"{key}.sel")
        for t in range(1, N + 1):
            sh.put(r, common.FIRST_COL + t - 1, f"={sel}", role="output", fmt=fmt, key=f"a.{key}@{t}")
        r += 1
    r += 1
    sh.put(r, 1, "Tip: change Method or Scenario above — every forecast, diagnostic and chart "
                 "updates automatically.", role="note")
    sh.merge(r, 1, r, last)

    sh.col_width(1, 30)
    for c in range(2, max(last, 11) + 1):
        sh.col_width(c, 10)
    sh.freeze("B7")
    return sh
