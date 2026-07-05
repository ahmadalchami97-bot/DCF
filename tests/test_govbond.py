"""
Test suite for the Government Bond Analyzer.

The workbook uses Excel's native bond functions, so analytics are verified with
the independent Python reference (bond.bondmath): internal consistency, the
two-way price<->yield relationship, and the cheap/fair/expensive direction, for a
coupon note and a zero-coupon bill. Also checks the workbook builds and wires up
its named ranges.

Run: ``python tests/test_govbond.py``  (or ``pytest -q tests/test_govbond.py``).
"""

from __future__ import annotations

import os
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl  # noqa: E402

from bond import bondmath as bm  # noqa: E402
from govbond.sample_data import build_sample, empty_like_sample  # noqa: E402
from govbond.workbook import assemble  # noqa: E402

S, M = date(2025, 3, 20), date(2034, 2, 15)


def test_price_reconciles():
    a = bm.analytics(S, M, 0.04, 96.50, 2, 1)
    assert abs(bm.price_clean(S, M, 0.04, a["ytm"], 2, 1) - 96.50) < 1e-6
    assert abs(a["total_pv"] - a["dirty"]) < 1e-9


def test_two_way_price_yield():
    """Price at the implied yield returns the market price; a lower test yield -> higher price."""
    a = bm.analytics(S, M, 0.04, 96.50, 2, 1)
    assert abs(bm.price_clean(S, M, 0.04, a["ytm"], 2, 1) - 96.50) < 1e-6          # yield->price->same
    theo_bench = bm.price_clean(S, M, 0.04, 0.043, 2, 1)                            # test at benchmark
    assert theo_bench > 96.50            # bond yields > benchmark -> theoretical price above market -> "cheap"


def test_price_yield_direction():
    a = bm.analytics(S, M, 0.04, 96.50, 2, 1)
    up = bm.price_clean(S, M, 0.04, a["ytm"] + 0.005, 2, 1)
    down = bm.price_clean(S, M, 0.04, a["ytm"] - 0.005, 2, 1)
    assert up < 96.50 < down


def test_duration_dv01_convexity():
    a = bm.analytics(S, M, 0.04, 96.50, 2, 1)
    assert abs(a["modified"] - a["macaulay"] / (1 + a["ytm"] / 2)) < 1e-9
    assert a["dv01"] > 0 and a["convexity"] > 0


def test_bill_duration_equals_maturity():
    z = bm.zero_analytics(date(2025, 3, 20), date(2025, 9, 18), 97.90, 1)
    assert abs(z["macaulay"] - z["years"]) < 1e-9 and z["accrued"] == 0.0


def test_known_values():
    a = bm.analytics(S, M, 0.04, 96.50, 2, 1)
    assert 0.043 < a["ytm"] < 0.047 and 7.0 < a["macaulay"] < 8.0 and 0.05 < a["dv01"] < 0.09


def test_workbook_builds_and_wires_up():
    for data in (build_sample(), empty_like_sample()):
        wb, ctx = assemble(data)
        path = os.path.join(tempfile.mkdtemp(), "g.xlsx")
        wb.save(path)
        wb2 = openpyxl.load_workbook(path)
        assert len(wb2.sheetnames) == 12
        for nm in ("BondName", "Settle", "Maturity", "YTM", "Dirty", "Accrued", "TestYield", "TheoClean",
                   "CheapFair", "MacDur", "ModDur", "Convexity", "DV01", "Spread", "Y10Y", "Y2Y",
                   "CurveShape", "AttractScore", "ModelView", "FinalView", "RateOutlook"):
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
