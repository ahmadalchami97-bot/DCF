"""
Test suite for the US Treasury Bond Analyzer.

The workbook uses Excel's native bond functions, so the analytics are verified
with the independent Python reference (bond.bondmath) -- internal consistency plus
known cases for both a coupon Treasury note and a zero-coupon bill -- and we check
that the workbook builds and wires up its named ranges.

Run: ``python tests/test_ustreasury.py``  (or ``pytest -q tests/test_ustreasury.py``).
"""

from __future__ import annotations

import os
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl  # noqa: E402

from bond import bondmath as bm  # noqa: E402
from ustreasury.sample_data import build_sample, empty_like_sample  # noqa: E402
from ustreasury.workbook import assemble  # noqa: E402

# Sample T-Note 4% 2034, semiannual, Actual/Actual
S, M = date(2025, 3, 20), date(2034, 2, 15)


def test_note_price_reconciles():
    a = bm.analytics(S, M, 0.04, 96.50, 2, 1)
    assert abs(bm.price_clean(S, M, 0.04, a["ytm"], 2, 1) - 96.50) < 1e-6
    assert abs(a["total_pv"] - a["dirty"]) < 1e-9


def test_note_discount_means_yield_above_coupon():
    a = bm.analytics(S, M, 0.04, 96.50, 2, 1)   # price < 100 -> discount
    assert a["ytm"] > 0.04


def test_modified_and_dv01():
    a = bm.analytics(S, M, 0.04, 96.50, 2, 1)
    assert abs(a["modified"] - a["macaulay"] / (1 + a["ytm"] / 2)) < 1e-9
    bump = (bm.price_clean(S, M, 0.04, a["ytm"] - 1e-4, 2, 1)
            - bm.price_clean(S, M, 0.04, a["ytm"] + 1e-4, 2, 1)) / 2
    assert abs(a["dv01"] - bump) < 5e-4 and a["dv01"] > 0


def test_convexity_positive():
    assert bm.analytics(S, M, 0.04, 96.50, 2, 1)["convexity"] > 0


def test_bill_duration_equals_maturity():
    z = bm.zero_analytics(date(2025, 3, 20), date(2025, 9, 18), 97.90, 1)
    assert abs(z["macaulay"] - z["years"]) < 1e-9
    assert z["accrued"] == 0.0 and z["ytm"] > 0


def test_known_note_values():
    a = bm.analytics(S, M, 0.04, 96.50, 2, 1)
    assert 0.043 < a["ytm"] < 0.047
    assert 7.0 < a["macaulay"] < 8.0
    assert 0.05 < a["dv01"] < 0.09


def test_stress_monotonic():
    a = bm.analytics(S, M, 0.04, 96.50, 2, 1)
    up = bm.price_clean(S, M, 0.04, a["ytm"] + 0.01, 2, 1)
    down = bm.price_clean(S, M, 0.04, a["ytm"] - 0.01, 2, 1)
    assert up < 96.50 < down  # yields up -> price down, yields down -> price up


def test_workbook_builds_and_wires_up():
    for data in (build_sample(), empty_like_sample()):
        wb, ctx = assemble(data)
        path = os.path.join(tempfile.mkdtemp(), "t.xlsx")
        wb.save(path)
        wb2 = openpyxl.load_workbook(path)
        assert len(wb2.sheetnames) == 12
        for nm in ("SecType", "Settle", "Maturity", "YTM", "Dirty", "MacDur", "ModDur",
                   "Convexity", "DV01", "Spread", "Y10Y", "Y2Y", "FreqWarn", "YearsToMat"):
            assert nm in wb2.defined_names, f"missing named range {nm}"


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
    print(f"Running {__file__}\n")
    sys.exit(0 if _run_all() else 1)
