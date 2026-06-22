"""
Test suite for the Institutional Forecasting Engine (rebuilt).

Verifies the generated workbook with the dependency-free Excel evaluator: there
are no errors and no circular references; the pasted actuals tie; the integrated
forecast reconciles every year WITHOUT a plug; one driver drives each line; the
bridge decompositions tie; the timeline is auto-detected; adding a year of
actuals shifts the forecast forward; and the blank template degrades gracefully.

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
    assert len(ev._memo) > 800


def test_historical_actuals_tie():
    """Balance check, asset-build check and liability-build check are 0 every actual year."""
    data = build_sample()
    ev, ctx, _ = _eval(data)
    for j in range(data["actual_years"]):
        for k in ("balance_check", "asset_check", "liab_check"):
            assert abs(float(_g(ev, ctx, f"h.{k}@{j}"))) < 1e-6, f"{k} off at year {j}"


def test_forecast_reconciles_without_plug():
    """Assets = Liabilities + Equity must hold every forecast year, to the cent."""
    data = build_sample()
    ev, ctx, _ = _eval(data)
    for t in range(1, data["horizon"] + 1):
        assert abs(float(_g(ev, ctx, f"f.balance_check@{t}"))) < 1e-6, f"imbalance year {t}"


def test_revenue_drives_off_growth():
    data = build_sample()
    ev, ctx, _ = _eval(data)
    rev0 = _g(ev, ctx, "f.revenue@0")
    g1 = _g(ev, ctx, "a.rev_growth@1")
    assert abs(_g(ev, ctx, "f.revenue@1") - rev0 * (1 + g1)) < 1e-6


def test_net_interest_on_opening_net_debt():
    """No circularity: net interest = rate x opening (prior-year) net debt."""
    data = build_sample()
    ev, ctx, _ = _eval(data)
    rate = _g(ev, ctx, "a.net_int_rate@1")
    nd0 = _g(ev, ctx, "f.net_debt@0")
    assert abs(_g(ev, ctx, "f.net_interest@1") - rate * nd0) < 1e-6


def test_forecast_bridge_ties():
    data = build_sample()
    ev, ctx, path = _eval(data)
    wf = openpyxl.load_workbook(path)
    ws = wf["Bridge"]
    n = 0
    for row in ws.iter_rows(min_col=1, max_col=1):
        if isinstance(row[0].value, str) and row[0].value.startswith("Check (effects"):
            for c in range(2, 2 + data["horizon"]):
                v = ev.value("Bridge", f"{openpyxl.utils.get_column_letter(c)}{row[0].row}")
                assert abs(v) < 1e-6, f"bridge check off at col {c}: {v}"
                n += 1
    assert n == 4 * data["horizon"], "expected four bridge blocks"


def test_timeline_autodetected():
    data = build_sample()
    ev, ctx, _ = _eval(data)
    fy = data["first_year"]
    assert _g(ev, ctx, "t.count") == data["actual_years"]
    assert _g(ev, ctx, "t.last_actual") == fy + data["actual_years"] - 1
    assert _g(ev, ctx, "t.fcst_start") == fy + data["actual_years"]


def test_adding_actual_shifts_forecast():
    """Pasting a new year of actuals must move the forecast start forward by one."""
    data = build_sample()
    wb, ctx = assemble(data)
    path = os.path.join(TMP, "shift.xlsx")
    wb.save(path)
    spare_sheet, spare_coord = ctx.refs._map[f"h.revenue@{data['actual_years']}"]

    ev0 = evaluate_workbook(path)
    assert _g(ev0, ctx, "t.fcst_start") == data["first_year"] + data["actual_years"]

    wf = openpyxl.load_workbook(path)
    wf[spare_sheet][spare_coord] = 9999
    wf.save(path)
    ev1 = evaluate_workbook(path)
    assert _g(ev1, ctx, "t.count") == data["actual_years"] + 1
    assert _g(ev1, ctx, "t.fcst_start") == data["first_year"] + data["actual_years"] + 1
    assert abs(_g(ev1, ctx, "f.revenue@0") - 9999) < 1e-6  # base anchor follows the new actual


def test_health_score_full_on_sample():
    ev, ctx, _ = _eval(build_sample())
    assert _g(ev, ctx, "d.health") == 100


def test_blank_template_degrades():
    ev, ctx, _ = _eval(empty_like_sample())
    errs = [(s, c, v) for (s, c), v in ev._memo.items() if isinstance(v, XlError)]
    assert not errs, f"blank should not error: {errs[:10]}"
    assert _g(ev, ctx, "d.health") < 100  # the data-present check flags the gap


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
