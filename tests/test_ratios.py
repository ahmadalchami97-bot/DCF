"""
Test suite for the Financial Ratio Analysis workbook.

Verifies the generated workbook with the dependency-free Excel evaluator and
cross-checks selected ratios against values recomputed directly from the sample
series (an independent source of truth).

Run: ``python tests/test_ratios.py``  (or ``pytest -q tests/test_ratios.py``).
"""

from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ratios.sample_data import build_sample, empty_like_sample  # noqa: E402
from ratios.workbook import assemble  # noqa: E402
from tests.xlcalc import XlError, evaluate_workbook  # noqa: E402

TMP = tempfile.mkdtemp(prefix="ratios_test_")


def _eval(data):
    path = os.path.join(TMP, "wb.xlsx")
    wb, ctx = assemble(data)
    wb.save(path)
    return evaluate_workbook(path), ctx


def _g(ev, ctx, key):
    s, c = ctx.refs._map[key]
    return ev.value(s, c)


def test_sample_no_errors_or_cycles():
    ev, ctx = _eval(build_sample())
    errs = [(s, c, v) for (s, c), v in ev._memo.items() if isinstance(v, XlError)]
    assert not ev.cycles, f"circular refs: {ev.cycles}"
    assert not errs, f"formula errors: {errs[:10]}"
    assert len(ev._memo) > 2500


def test_balance_sheet_balances_exactly():
    data = build_sample()
    ev, ctx = _eval(data)
    for i in range(len(data["periods"])):
        a = float(_g(ev, ctx, f"in.total_assets@{i}"))
        le = float(_g(ev, ctx, f"in.total_liab_equity@{i}"))
        assert abs(a - le) < 1e-6, f"balance off in period {i}: {a} vs {le}"


def test_ratios_match_independent_recompute():
    data = build_sample()
    ev, ctx = _eval(data)
    s = data["series"]
    li = data["hist_years"] - 1

    def ni(i):
        gross = s["revenue"][i] - s["cogs"][i]
        ebitda = gross - s["opex"][i]
        ebit = ebitda - s["depreciation"][i]
        pretax = ebit - s["interest_expense"][i] + s["other_income"][i]
        return pretax - s["tax_expense"][i]

    gm = (s["revenue"][li] - s["cogs"][li]) / s["revenue"][li]
    assert abs(_g(ev, ctx, f"prof.gross_margin@{li}") - gm) < 1e-6
    nm = ni(li) / s["revenue"][li]
    assert abs(_g(ev, ctx, f"prof.net_margin@{li}") - nm) < 1e-6
    ca = s["cash"][li] + s["receivables"][li] + s["inventory"][li] + s["other_current_assets"][li]
    cl = s["accounts_payable"][li] + s["short_term_debt"][li] + s["other_current_liabilities"][li]
    assert abs(_g(ev, ctx, f"liq.current_ratio@{li}") - ca / cl) < 1e-6
    de = (s["short_term_debt"][li] + s["long_term_debt"][li]) / s["equity"][li]
    assert abs(_g(ev, ctx, f"solv.debt_to_equity@{li}") - de) < 1e-6


def test_dupont_reproduces_roe():
    data = build_sample()
    ev, ctx = _eval(data)
    li = data["hist_years"] - 1
    assert abs(_g(ev, ctx, f"prof.dp_roe@{li}") - _g(ev, ctx, f"prof.roe@{li}")) < 1e-9


def test_common_size_revenue_is_100pct():
    data = build_sample()
    ev, ctx = _eval(data)
    li = data["hist_years"] - 1
    assert abs(_g(ev, ctx, f"cs.revenue@{li}") - 1.0) < 1e-9


def test_quality_scores_finite_and_sane():
    data = build_sample()
    ev, ctx = _eval(data)
    li = data["hist_years"] - 1
    z = _g(ev, ctx, f"qual.z@{li}")
    f = _g(ev, ctx, f"qual.f@{li}")
    m = _g(ev, ctx, f"qual.m@{li}")
    assert isinstance(z, float) and z > 0
    assert isinstance(f, float) and 0 <= f <= 9
    assert isinstance(m, float) and -10 < m < 5


def test_benchmarking_ranks_company():
    data = build_sample()
    ev, ctx = _eval(data)
    # company ROIC exceeds every peer -> best-in-class
    assert _g(ev, ctx, "bm.best.roic") == "Best-in-Class"


def test_dashboard_overall_score_in_range():
    data = build_sample()
    ev, ctx = _eval(data)
    score = _g(ev, ctx, "db.score.overall")
    assert isinstance(score, float) and 0 <= score <= 100


def test_quality_control_verdict():
    ev, ctx = _eval(build_sample())
    assert "PASS" in _g(ev, ctx, "qc.verdict")


def test_blank_template_degrades_gracefully():
    ev, ctx = _eval(empty_like_sample())
    errs = [(s, c, v) for (s, c), v in ev._memo.items() if isinstance(v, XlError)]
    assert not errs, f"blank should not error: {errs[:10]}"
    assert "FAIL" in _g(ev, ctx, "qc.verdict")


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
