"""
Test suite for the company analysis engine.

Verifies the GENERATED workbook by evaluating its live formulas with the
dependency-free Excel evaluator in ``tests/xlcalc.py`` and cross-checking against
the independent roll-forward in ``dcf.sample_data``. Agreement between the two
validates the formulas (and the evaluator) simultaneously.

Run with pytest (``pytest -q``) or directly (``python tests/test_model.py``).
"""

from __future__ import annotations

import copy
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dcf.sample_data import build_sample, empty_like_sample  # noqa: E402
from dcf.workbook import assemble  # noqa: E402
from tests.xlcalc import Evaluator, XlError, evaluate_workbook  # noqa: E402

TMP = tempfile.mkdtemp(prefix="dcf_test_")


def _build_and_eval(data):
    path = os.path.join(TMP, "wb.xlsx")
    wb, ctx = assemble(data)
    wb.save(path)
    ev = evaluate_workbook(path)
    return ev, ctx, path


def _g(ev, ctx, key):
    sheet, coord = ctx.refs._map[key]
    return ev.value(sheet, coord)


def test_sample_has_no_formula_errors_or_cycles():
    ev, ctx, _ = _build_and_eval(build_sample())
    errors = [(s, c, v) for (s, c), v in ev._memo.items() if isinstance(v, XlError)]
    assert not ev.cycles, f"circular references: {ev.cycles}"
    assert not errors, f"formula errors: {errors[:10]}"
    assert len(ev._memo) > 800, "expected a substantial number of live formulas"


def test_inputs_subtotals_match_rollforward():
    """Sheet formulas must reproduce the independent roll-forward exactly."""
    data = build_sample()
    ev, ctx, _ = _build_and_eval(data)
    der = data["derived"]
    n = len(data["periods"])
    for metric in ("gross_profit", "ebit", "ebitda", "net_income", "pretax_income",
                   "cfo", "cfi", "cff", "net_change_cash"):
        for p in range(n):
            got = _g(ev, ctx, f"in.{metric}@{p}")
            assert abs(float(got) - float(der[metric][p])) < 1e-6, \
                f"{metric}@{p}: {got} != {der[metric][p]}"


def test_balance_sheet_balances_every_year():
    data = build_sample()
    ev, ctx, _ = _build_and_eval(data)
    for p in range(len(data["periods"])):
        ta = float(_g(ev, ctx, f"in.total_assets@{p}"))
        tle = float(_g(ev, ctx, f"in.total_liab_equity@{p}"))
        assert abs(ta - tle) < 1e-6, f"balance sheet off in period {p}: {ta} vs {tle}"


def test_wacc_build_up():
    ev, ctx, _ = _build_and_eval(build_sample())
    ke = _g(ev, ctx, "wacc.ke")
    rf, beta, erp = (_g(ev, ctx, k) for k in ("wacc.rf", "wacc.beta", "wacc.erp"))
    assert abs(ke - (rf + beta * erp)) < 1e-9, "Ke must equal CAPM build-up"
    wacc = _g(ev, ctx, "wacc.value")
    assert 0.04 <= wacc <= 0.18, f"WACC out of plausible range: {wacc}"


def test_dcf_outputs_sane():
    ev, ctx, _ = _build_and_eval(build_sample())
    for key in ("dcf.ev", "dcf.equity_value", "dcf.value_per_share"):
        v = _g(ev, ctx, key)
        assert isinstance(v, float) and v > 0, f"{key} should be positive: {v}"
    tv_share = _g(ev, ctx, "dcf.tv_share")
    assert 0 < tv_share < 1, f"TV share should be a fraction: {tv_share}"


def test_scenario_base_matches_headline():
    ev, ctx, _ = _build_and_eval(build_sample())
    assert abs(_g(ev, ctx, "sc.Base.per_share") - _g(ev, ctx, "dcf.value_per_share")) < 0.01
    # ordering: bull >= base >= bear >= downside
    bull = _g(ev, ctx, "sc.Bull.per_share")
    base = _g(ev, ctx, "sc.Base.per_share")
    bear = _g(ev, ctx, "sc.Bear.per_share")
    down = _g(ev, ctx, "sc.Downside.per_share")
    assert bull >= base >= bear >= down, f"scenario ordering wrong: {bull,base,bear,down}"


def test_sensitivity_centre_matches_dcf():
    """The boxed centre of Table 1 (base WACC, base g) must equal the headline."""
    import openpyxl

    data = build_sample()
    ev, ctx, path = _build_and_eval(data)
    headline = _g(ev, ctx, "dcf.value_per_share")
    wf = openpyxl.load_workbook(path)
    ws = wf["Sensitivity"]
    # find first 'Value / share' corner, centre is +3 rows / +3 cols
    for row in ws.iter_rows(min_col=1, max_col=1):
        if row[0].value == "Value / share":
            hr = row[0].row
            centre = ev.value("Sensitivity", f"E{hr + 3}")  # col E = 3rd data col
            assert abs(centre - headline) < 0.01, f"sensitivity centre {centre} != {headline}"
            return
    raise AssertionError("could not locate a sensitivity table")


def test_checks_pass_on_consistent_sample():
    ev, ctx, _ = _build_and_eval(build_sample())
    assert _g(ev, ctx, "chk.fail") == 0
    verdict = _g(ev, ctx, "chk.verdict")
    assert "PASS" in verdict, f"expected PASS verdict, got {verdict!r}"


def test_blank_template_degrades_gracefully():
    """No data -> no formula errors, and the diagnostics flag the gaps."""
    ev, ctx, _ = _build_and_eval(empty_like_sample())
    errors = [(s, c, v) for (s, c), v in ev._memo.items() if isinstance(v, XlError)]
    assert not errors, f"blank template should not error: {errors[:10]}"
    assert "FAIL" in _g(ev, ctx, "chk.verdict")


def test_scenario_selector_drives_model():
    """Changing the selector cell flips the whole DCF to that scenario."""
    import openpyxl

    data = build_sample()
    wb, ctx = assemble(data)
    path = os.path.join(TMP, "sw.xlsx")
    wb.save(path)
    sheet, coord = ctx.refs._map["as.scenario_sel"]
    wf = openpyxl.load_workbook(path)
    wf[sheet][coord] = 4  # Downside
    wf.save(path)
    ev = evaluate_workbook(path)
    assert ev.value(*ctx.refs._map["as.scenario_name"]) == "Downside"
    headline = ev.value(*ctx.refs._map["dcf.value_per_share"])
    downside = ev.value(*ctx.refs._map["sc.Downside.per_share"])
    assert abs(headline - downside) < 0.01


def test_partial_data_no_market_price():
    """Missing market data uses fallbacks; missing price yields n/a, not errors."""
    d = copy.deepcopy(build_sample())
    d["market"]["mkt_share_price"] = None
    d["market"]["mkt_shares_out"] = None
    ev, ctx, _ = _build_and_eval(d)
    errors = [(s, c, v) for (s, c), v in ev._memo.items() if isinstance(v, XlError)]
    assert not errors, f"partial data should not error: {errors[:10]}"
    assert _g(ev, ctx, "dcf.upside") == "n/a"
    assert isinstance(_g(ev, ctx, "dcf.value_per_share"), float)


def _run_all():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed.")
    return passed == len(tests)


if __name__ == "__main__":
    print(f"Running {__file__} (artifacts in {TMP})\n")
    sys.exit(0 if _run_all() else 1)
