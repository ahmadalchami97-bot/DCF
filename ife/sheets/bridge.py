"""
Forecast Bridge (Sheet 6).

Explains exactly WHY revenue, EBITDA and net income change year-over-year by
decomposing each YoY move into clean effects that sum back to the actual change:

  Revenue   : growth effect.
  EBITDA    : revenue (volume) effect + margin effect.
  Net income: EBITDA effect + D&A effect + financing effect + tax-rate effect.

Each block ends with a check row (sum of effects − actual change = 0).
"""

from __future__ import annotations

from dcf.config import Fmt
from .. import common

M = Fmt.MONEY


def build(sh, ctx):
    refs = ctx.refs
    N = ctx.fcst
    F = lambda k, t: refs.ref(f"f.{k}@{t}")     # noqa: E731

    def fc(t):
        return common.FIRST_COL + t - 1  # forecast years in cols 2..N+1

    last = fc(N)
    common.title_block(sh, "FORECAST BRIDGE",
                       "Why revenue, EBITDA and net income change each year — effect decomposition",
                       last_col=last)
    common.nav_bar(sh, 5)
    r = 7
    sh.put(r, 1, common.units_note(ctx), role="note")
    sh.merge(r, 1, r, last)
    r += 1
    sh.put(r, 1, "Effect", role="colhdr")
    for t in range(1, N + 1):
        sh.put(r, fc(t), ctx.fcst_periods[t - 1], role="colhdr_r")
    r += 1

    def block(title, lines, check_actual):
        nonlocal r
        r = common.section(sh, r, title, c1=1, c2=last)
        first = r
        for label, role, builder in lines:
            sh.put(r, 1, label, role=("label_b" if role == "total" else "label"))
            for t in range(1, N + 1):
                sh.put(r, fc(t), builder(t), role=role, fmt=M)
            r += 1
        sh.put(r, 1, "Check (effects − actual Δ)", role="sublabel")
        for t in range(1, N + 1):
            eff = "+".join(sh.local(rr, fc(t)) for rr in range(first + 1, first + len(lines) - 1))
            sh.put(r, fc(t), f"=({eff})-({check_actual(t)})", role="formula", fmt=M)
        r += 2

    def taxr(t):
        return f"IFERROR({F('tax', t)}/{F('pretax', t)},0)"

    def mgn(k, t):
        return f"IFERROR({F(k, t)}/{F('revenue', t)},0)"

    block("Revenue Bridge", [
        ("Prior-year revenue", "formula", lambda t: f"={F('revenue', t-1)}"),
        ("(+) Growth effect", "formula", lambda t: f"={F('revenue', t)}-{F('revenue', t-1)}"),
        ("(=) Current revenue", "total", lambda t: f"={F('revenue', t)}"),
    ], lambda t: f"{F('revenue', t)}-{F('revenue', t-1)}")

    block("EBITDA Bridge", [
        ("Prior-year EBITDA", "formula", lambda t: f"={F('ebitda', t-1)}"),
        ("(+) Revenue (volume) effect", "formula",
         lambda t: f"=({F('revenue', t)}-{F('revenue', t-1)})*{mgn('ebitda', t-1)}"),
        ("(+) Margin effect", "formula",
         lambda t: f"=({mgn('ebitda', t)}-{mgn('ebitda', t-1)})*{F('revenue', t)}"),
        ("(=) Current EBITDA", "total", lambda t: f"={F('ebitda', t)}"),
    ], lambda t: f"{F('ebitda', t)}-{F('ebitda', t-1)}")

    block("Net Income Bridge", [
        ("Prior-year net income", "formula", lambda t: f"={F('net_income', t-1)}"),
        ("(+) EBITDA effect", "formula",
         lambda t: f"=({F('ebitda', t)}-{F('ebitda', t-1)})*(1-{taxr(t-1)})"),
        ("(−) D&A effect", "formula",
         lambda t: f"=-({F('depreciation', t)}-{F('depreciation', t-1)})*(1-{taxr(t-1)})"),
        ("(−) Financing effect", "formula",
         lambda t: (f"=-(({F('interest_expense', t)}-{F('interest_income', t)})"
                    f"-({F('interest_expense', t-1)}-{F('interest_income', t-1)}))*(1-{taxr(t-1)})")),
        ("(−) Tax-rate effect", "formula",
         lambda t: f"=-{F('pretax', t)}*({taxr(t)}-{taxr(t-1)})"),
        ("(=) Current net income", "total", lambda t: f"={F('net_income', t)}"),
    ], lambda t: f"{F('net_income', t)}-{F('net_income', t-1)}")

    sh.freeze("B10")
    sh.col_width(1, 30)
    for t in range(1, N + 1):
        sh.col_width(fc(t), 11)
    return sh
