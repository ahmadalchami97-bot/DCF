"""
Test suite for the Institutional Forecasting Engine.

Verifies the generated workbook with the dependency-free Excel evaluator: the
integrated 3-statement model reconciles every year WITHOUT a plug, there are no
circular references, the forecast bridge ties, the scenario engine's Base column
reconciles with the main forecast, the method/scenario selectors re-price the
model, and the blank template degrades gracefully.

Run: ``python tests/test_ife.py``  (or ``pytest -q tests/test_ife.py``).
"""

from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl  # noqa: E402

from ife.sample_data import build_sample, empty_like_sample  # noqa: E402
from ife.workbook import assemble  # noqa: E402
from tests.xlcalc import XlError, evaluate_workbook  # noqa: E402

TMP = tempfile.mkdtemp(prefix="ife_test_")


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
    assert len(ev._memo) > 2500


def test_historical_balance_sheet_balances():
    data = build_sample()
    ev, ctx, _ = _eval(data)
    for i in range(data["hist_years"]):
        assert abs(float(_g(ev, ctx, f"h.balance_check@{i}"))) < 1e-6


def test_forecast_reconciles_without_plug():
    """Assets = Liabilities + Equity must hold every forecast year, to the cent."""
    data = build_sample()
    ev, ctx, _ = _eval(data)
    for t in range(1, data["fcst_years"] + 1):
        assert abs(float(_g(ev, ctx, f"f.balance_check@{t}"))) < 1e-6, f"imbalance year {t}"


def test_revenue_drives_off_active_growth():
    data = build_sample()
    ev, ctx, _ = _eval(data)
    rev0 = _g(ev, ctx, "f.revenue@0")
    g1 = _g(ev, ctx, "a.rev_growth@1")
    assert abs(_g(ev, ctx, "f.revenue@1") - rev0 * (1 + g1)) < 1e-6


def test_forecast_bridge_ties():
    """Each bridge block's effects must sum to the actual YoY change."""
    data = build_sample()
    ev, ctx, path = _eval(data)
    wf = openpyxl.load_workbook(path)
    ws = wf["Bridge"]
    for row in ws.iter_rows(min_col=1, max_col=1):
        if isinstance(row[0].value, str) and row[0].value.startswith("Check (effects"):
            for c in range(2, 2 + data["fcst_years"]):
                v = ev.value("Bridge", f"{openpyxl.utils.get_column_letter(c)}{row[0].row}")
                assert abs(v) < 1e-6, f"bridge check off at {c}: {v}"


def test_scenario_base_reconciles_with_forecast():
    data = build_sample()
    ev, ctx, _ = _eval(data)
    N = data["fcst_years"]
    for fk, sk in (("revenue", "revenue"), ("net_income", "ni"), ("equity", "equity"),
                   ("fcf", "fcf"), ("ebitda", "ebitda")):
        a = _g(ev, ctx, f"f.{fk}@{N}")
        b = _g(ev, ctx, f"sc.base.{sk}@{N}")
        assert abs(a - b) < 1e-6, f"{fk}: forecast {a} != scenario base {b}"


def test_scenario_ordering():
    data = build_sample()
    ev, ctx, path = _eval(data)
    wf = openpyxl.load_workbook(path)
    ws = wf["Scenario"]
    for row in ws.iter_rows(min_col=1, max_col=1):
        if row[0].value == "Revenue CAGR":
            rr = row[0].row
            bear, base, bull = (ev.value("Scenario", f"{openpyxl.utils.get_column_letter(c)}{rr}")
                                for c in (2, 3, 4))
            assert bear <= base <= bull, f"scenario ordering wrong: {bear,base,bull}"
            return
    raise AssertionError("Revenue CAGR row not found")


def test_health_score_full_on_sample():
    ev, ctx, _ = _eval(build_sample())
    assert _g(ev, ctx, "d.health") == 100


def test_method_and_scenario_switch_reprice():
    """Changing the Scenario named range must change the forecast."""
    data = build_sample()
    wb, ctx = assemble(data)
    path = os.path.join(TMP, "sw.xlsx")
    wb.save(path)
    N = data["fcst_years"]
    base_rev_cell = ctx.refs._map[f"f.revenue@{N}"]
    msheet, mcoord = ctx.refs._map["a.scenario"]
    for scen, expect in ((1, "lower"), (3, "higher")):
        wf = openpyxl.load_workbook(path)
        wf[msheet][mcoord] = scen
        wf.save(path)
        ev = evaluate_workbook(path)
        rev = ev.value(*base_rev_cell)
        if scen == 1:
            bear = rev
        else:
            bull = rev
    assert bear < bull, f"bull revenue {bull} should exceed bear {bear}"


def test_blank_template_degrades():
    ev, ctx, _ = _eval(empty_like_sample())
    errs = [(s, c, v) for (s, c), v in ev._memo.items() if isinstance(v, XlError)]
    assert not errs, f"blank should not error: {errs[:10]}"
    assert _g(ev, ctx, "d.health") < 100  # data-present check flags the gap


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
