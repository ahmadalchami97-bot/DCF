"""Sample government bond + yield-curve data (all inputs, easily replaced)."""

from __future__ import annotations

from datetime import date


def build_sample() -> dict:
    return {
        "terms": {
            "name": "US Treasury Note 4.000% 15-Feb-2034",
            "issuer": "US Treasury (United States)",
            "currency": "USD",
            "sec_type": "Treasury Note",
            "face": 100.0,
            "position": 100000.0,
            "coupon": 0.04,
            "freq_name": "Semiannual",
            "basis": 1,
            "issue": date(2024, 2, 15),
            "settle": date(2025, 3, 20),
            "maturity": date(2034, 2, 15),
            "mkt_clean": 96.50,
            "mkt_ytm": 0.0448,
            "bench_yield": 0.0430,
            "outlook": "Yields Stable",
            "analyst": "",
            "analysis_date": date(2025, 3, 20),
        },
        "curve": {"m3": 0.0435, "y2": 0.0415, "y5": 0.0420, "y10": 0.0445, "y30": 0.0465},
    }


def empty_like_sample() -> dict:
    s = build_sample()
    t = dict(s["terms"])
    t.update(name="<Bond name>", issuer="", analyst="", mkt_clean=100.0, mkt_ytm=None,
             bench_yield=0.043, position=None)
    curve = {k: None for k in s["curve"]}
    return {"terms": t, "curve": curve}
