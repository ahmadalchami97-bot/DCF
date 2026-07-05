"""Sample US Treasury + yield-curve data (all inputs, easily replaced)."""

from __future__ import annotations

from datetime import date


def build_sample() -> dict:
    return {
        "terms": {
            "name": "US Treasury Note 4.000% 15-Feb-2034",
            "cusip": "91282CJZ9",
            "sec_type": "Treasury Note",
            "currency": "USD",
            "face": 100.0,
            "coupon": 0.04,
            "freq_name": "Semiannual",
            "basis": 1,
            "issue": date(2024, 2, 15),
            "settle": date(2025, 3, 20),
            "maturity": date(2034, 2, 15),
            "mkt_clean": 96.50,
            "bench_yield": 0.0430,
            "analyst": "",
            "analysis_date": date(2025, 3, 20),
        },
        # Treasury yield curve (annual yields)
        "curve": {"m3": 0.0435, "y2": 0.0415, "y5": 0.0420, "y10": 0.0445, "y30": 0.0465},
        # Risk checklist assessments (editable)
        "risk": {
            "Interest-rate risk": ("Medium", "~7.4y modified duration; a 1% rate rise cuts the price ~7%."),
            "Duration risk": ("Medium", "Intermediate maturity - meaningful price sensitivity to yields."),
            "Reinvestment risk": ("Medium", "Semiannual coupons must be reinvested, possibly at lower rates."),
            "Inflation risk": ("Medium", "Fixed coupons lose real value if inflation rises (nominal Treasury)."),
            "Opportunity cost risk": ("Medium", "If yields rise you are locked into a lower coupon."),
            "Liquidity risk": ("Low", "US Treasuries are among the most liquid securities in the world."),
            "Curve risk": ("Low", "Value depends on the part of the curve this maturity sits on."),
        },
    }


def empty_like_sample() -> dict:
    s = build_sample()
    t = dict(s["terms"])
    t.update(name="<Security name>", cusip="", analyst="", mkt_clean=100.0, bench_yield=0.043)
    curve = {k: None for k in s["curve"]}
    risk = {k: ("Medium", "") for k in s["risk"]}
    return {"terms": t, "curve": curve, "risk": risk}
