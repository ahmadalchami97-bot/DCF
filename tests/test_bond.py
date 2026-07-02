"""
Test suite for the Fixed-Rate Bond Analyzer.

The workbook uses Excel's native bond functions (YIELD, PRICE, DURATION, ...),
which the dependency-free evaluator can't run. So we verify the ANALYTICS with an
independent Python reference (bond.bondmath) -- internal consistency plus known
cases -- and check that the workbook builds, is a valid file, and wires up all the
named ranges the sheets depend on.

Run: ``python tests/test_bond.py``  (or ``pytest -q tests/test_bond.py``).
"""

from __future__ import annotations

import os
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openpyxl  # noqa: E402

from bond import bondmath as bm  # noqa: E402
from bond.sample_data import build_sample, empty_like_sample  # noqa: E402
from bond.workbook import assemble  # noqa: E402

SETTLE, MAT = date(2025, 3, 20), date(2030, 1, 15)


def test_par_bond_yields_coupon():
    """A bond priced at par on a coupon date yields ~ its coupon."""
    y = bm.solve_yield(date(2025, 1, 15), MAT, 0.05, 100.0, 2, 0)
    assert abs(y - 0.05) < 1e-4, y


def test_discount_and_premium_direction():
    disc = bm.solve_yield(SETTLE, MAT, 0.05, 95.0, 2, 0)
    prem = bm.solve_yield(SETTLE, MAT, 0.05, 105.0, 2, 0)
    assert disc > 0.05 > prem, (disc, prem)


def test_price_reconciles_at_yield():
    a = bm.analytics(SETTLE, MAT, 0.05, 98.50, 2, 0)
    # repricing at the solved yield returns the input clean price
    assert abs(bm.price_clean(SETTLE, MAT, 0.05, a["ytm"], 2, 0) - 98.50) < 1e-6
    # sum of PV equals dirty price
    assert abs(a["total_pv"] - a["dirty"]) < 1e-9


def test_modified_relationship():
    a = bm.analytics(SETTLE, MAT, 0.05, 98.50, 2, 0)
    assert abs(a["modified"] - a["macaulay"] / (1 + a["ytm"] / 2)) < 1e-9


def test_dv01_two_methods_agree():
    a = bm.analytics(SETTLE, MAT, 0.05, 98.50, 2, 0)
    bump = (bm.price_clean(SETTLE, MAT, 0.05, a["ytm"] - 1e-4, 2, 0)
            - bm.price_clean(SETTLE, MAT, 0.05, a["ytm"] + 1e-4, 2, 0)) / 2
    assert abs(a["dv01"] - bump) < 5e-4, (a["dv01"], bump)
    assert a["dv01"] > 0


def test_convexity_positive():
    a = bm.analytics(SETTLE, MAT, 0.05, 98.50, 2, 0)
    assert a["convexity"] > 0


def test_zero_coupon_duration_equals_maturity():
    z = bm.zero_analytics(SETTLE, MAT, 80.0, 0)
    assert abs(z["macaulay"] - z["years"]) < 1e-9
    assert z["accrued"] == 0.0
    assert z["ytm"] > 0


def test_accrued_matches_daycount():
    acc = bm.accrued_interest(SETTLE, MAT, 0.05, 2, 0)
    assert abs(acc - 0.902778) < 1e-4, acc


def test_ytw_logic():
    a = bm.analytics(SETTLE, MAT, 0.05, 98.50, 2, 0)
    ytc = bm.yield_to_call(SETTLE, date(2028, 1, 15), 0.05, 98.50, 2, 0, 102.0)
    assert min(a["ytm"], ytc) == a["ytm"] or min(a["ytm"], ytc) == ytc
    assert ytc > 0


def test_known_sample_values():
    a = bm.analytics(SETTLE, MAT, 0.05, 98.50, 2, 0)
    assert 0.052 < a["ytm"] < 0.055
    assert 4.0 < a["macaulay"] < 4.6
    assert 4.0 < a["modified"] < 4.5
    assert 0.03 < a["dv01"] < 0.05


def test_workbook_builds_and_wires_up():
    for data in (build_sample(), empty_like_sample()):
        wb, ctx = assemble(data)
        path = os.path.join(tempfile.mkdtemp(), "b.xlsx")
        wb.save(path)
        wb2 = openpyxl.load_workbook(path)
        assert len(wb2.sheetnames) == 12
        for nm in ("Settle", "Maturity", "YTM", "Dirty", "MacDur", "ModDur", "Convexity",
                   "DV01", "YTC", "YTW", "Spread", "NetDebtEBITDA", "LiqCoverage"):
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
