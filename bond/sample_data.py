"""Sample bond + issuer data for the Bond Analyzer (all inputs, easily replaced)."""

from __future__ import annotations

from datetime import date


def build_sample() -> dict:
    return {
        "terms": {
            "issuer": "Atlas Manufacturing Corp",
            "bond_name": "ATLAS 5.00% 15-Jan-2030",
            "isin": "US000000AT30",
            "currency": "USD",
            "face": 100.0,
            "coupon": 0.05,
            "freq_name": "Semiannual",
            "basis": 0,
            "issue": date(2023, 1, 15),
            "settle": date(2025, 3, 20),
            "maturity": date(2030, 1, 15),
            "mkt_clean": 98.50,
            "bench_yield": 0.042,
            "rating": "BBB",
            "seniority": "Senior",
            "secured": "Unsecured",
            "callable": "Yes",
            "call_date": date(2028, 1, 15),
            "call_price": 102.0,
            "sector": "Industrials",
            "analyst": "",
            "analysis_date": date(2025, 3, 20),
        },
        # Issuer Financial Strength (currency millions)
        "issuer": {
            "revenue": 4200.0, "ebitda": 780.0, "ebit": 560.0, "cash": 350.0,
            "total_debt": 2100.0, "st_debt": 300.0, "lt_debt": 1800.0,
            "interest_expense": 130.0, "operating_cf": 610.0, "capex": 280.0,
            "credit_lines": 500.0, "debt_due_12m": 300.0,
        },
        # Maturity wall (currency millions)
        "wall": {"y1": 300.0, "y2": 250.0, "y3": 400.0, "y4": 350.0, "y5": 300.0, "after5": 500.0},
    }


def empty_like_sample() -> dict:
    """A clean template: valid placeholder terms (so nothing errors) + blank optional sections."""
    s = build_sample()
    t = dict(s["terms"])
    t.update(issuer="<Issuer name>", bond_name="<Bond name>", isin="", sector="",
             rating="", analyst="", mkt_clean=100.0, bench_yield=0.04,
             callable="No", coupon=0.05, freq_name="Semiannual", basis=0, face=100.0)
    issuer = {k: None for k in s["issuer"]}
    wall = {k: None for k in s["wall"]}
    return {"terms": t, "issuer": issuer, "wall": wall}
