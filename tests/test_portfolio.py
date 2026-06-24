"""
Test suite for the Portfolio Allocation Optimizer.

Verifies the generated workbook with the dependency-free Excel evaluator: no
errors and no circular references; the scenario return decomposition ties; the
currency-adjusted and bond formulas are correct; every allocation sums to 100%;
the min-volatility mix really is the lowest-risk one; the scenario-stressed
recommendation respects the min/max limits; rebalancing trades net to zero; and
the blank template degrades gracefully.

Run: ``python tests/test_portfolio.py``  (or ``pytest -q tests/test_portfolio.py``).
"""

from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portfolio.config import ASSET_KEYS  # noqa: E402
from portfolio.sample_data import build_sample, empty_like_sample  # noqa: E402
from portfolio.workbook import assemble  # noqa: E402
from tests.xlcalc import XlError, evaluate_workbook  # noqa: E402

TMP = tempfile.mkdtemp(prefix="pf_test_")
ALLOCS = ["current", "equal", "target", "sharpe", "minvol", "scenario"]


def _eval(data):
    path = os.path.join(TMP, "wb.xlsx")
    wb, ctx = assemble(data)
    wb.save(path)
    return evaluate_workbook(path), ctx, path


def _g(ev, ctx, key):
    s, c = ctx.refs._map[key]
    return ev.value(s, c)


def test_sample_no_errors_or_cycles():
    ev, ctx, _ = _eval(build_sample())
    errs = [(s, c, v) for (s, c), v in ev._memo.items() if isinstance(v, XlError)]
    assert not ev.cycles, f"circular references: {ev.cycles}"
    assert not errs, f"formula errors: {errs[:10]}"
    assert len(ev._memo) > 400


def test_currency_adjusted_return():
    ev, ctx, _ = _eval(build_sample())
    for k in ASSET_KEYS:
        local = _g(ev, ctx, f"out.local@{k}")
        fx = _g(ev, ctx, f"out.fx@{k}")
        adj = _g(ev, ctx, f"out.curradj@{k}")
        assert abs(adj - ((1 + local) * (1 + fx) - 1)) < 1e-9, f"curradj wrong for {k}"


def test_portfolio_return_ties():
    """Portfolio return = sum of contributions = end value / start value - 1."""
    ev, ctx, _ = _eval(build_sample())
    pr = _g(ev, ctx, "out.port_return")
    contribs = sum(_g(ev, ctx, f"out.contrib@{k}") for k in ASSET_KEYS)
    crosscheck = _g(ev, ctx, "out.end_total") / _g(ev, ctx, "out.start_total") - 1
    assert abs(pr - contribs) < 1e-9
    assert abs(pr - crosscheck) < 1e-9


def test_bond_return_formula():
    ev, ctx, _ = _eval(build_sample())
    b = build_sample()["bond"]
    coupon = b["face"] * b["coupon_rate"] * b["holding_days"] / 365
    expect = (b["end_price"] - b["start_price"] + coupon) / b["start_price"]
    assert abs(_g(ev, ctx, "bond.total_return") - expect) < 1e-9


def test_allocations_sum_to_one():
    ev, ctx, _ = _eval(build_sample())
    for a in ALLOCS:
        s = sum(_g(ev, ctx, f"al.w@{a}_{k}") for k in ASSET_KEYS)
        assert abs(s - 1.0) < 1e-6, f"{a} weights sum to {s}"


def test_minvol_is_lowest_risk():
    ev, ctx, _ = _eval(build_sample())
    vols = {a: _g(ev, ctx, f"al.vol@{a}") for a in ALLOCS}
    assert vols["minvol"] == min(vols.values()), f"min-vol not lowest: {vols}"


def test_scenario_respects_limits():
    ev, ctx, _ = _eval(build_sample())
    for k in ASSET_KEYS:
        w = _g(ev, ctx, f"al.w@scenario_{k}")
        lo = _g(ev, ctx, f"in.min_w@{k}")
        hi = _g(ev, ctx, f"in.max_w@{k}")
        # two fitting rounds leave at most a sub-1% residual (flagged on the sheet)
        assert lo - 0.006 <= w <= hi + 0.006, f"{k} weight {w} outside [{lo},{hi}]"


def test_recommended_defaults_to_scenario():
    ev, ctx, _ = _eval(build_sample())
    assert _g(ev, ctx, "al.rec_basis") == len(ALLOCS)  # 6 = scenario-stressed
    for k in ASSET_KEYS:
        assert abs(_g(ev, ctx, f"al.rec_w@{k}") - _g(ev, ctx, f"al.w@scenario_{k}")) < 1e-9


def test_rebalancing_trades_net_to_zero():
    ev, ctx, _ = _eval(build_sample())
    total = sum(_g(ev, ctx, f"rb.trade@{k}") for k in ASSET_KEYS)
    assert abs(total) < 1e-6, f"trades net to {total}, not 0"


def test_indicators_not_holdings():
    ev, ctx, _ = _eval(build_sample())
    # indicators default to non-investable and never appear as allocation weights
    assert _g(ev, ctx, "in.investable@dxy") == "No"
    assert not ctx.refs.has("al.w@current_dxy")


def test_blank_template_degrades():
    ev, ctx, _ = _eval(empty_like_sample())
    errs = [(s, c, v) for (s, c), v in ev._memo.items() if isinstance(v, XlError)]
    assert not errs, f"blank should not error: {errs[:10]}"


def _run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            ok += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{ok}/{len(tests)} tests passed.")
    return ok == len(tests)


if __name__ == "__main__":
    print(f"Running {__file__} (artifacts in {TMP})\n")
    sys.exit(0 if _run_all() else 1)
