"""
Worked example for the Portfolio Allocation Optimizer.

A KWD-based investor holding Swiss and US assets, stressed through the
"Since Fed Rate Decision" scenario. All numbers are illustrative and internally
consistent so the user can see how the tool behaves before replacing the data.

Everything here is just *input* values; every result in the workbook is a live
Excel formula, not a number baked in by Python.
"""

from __future__ import annotations

from .config import ASSET_KEYS, BASE_CURRENCY, Defaults

# Correlation matrix, rows/cols in ASSET_KEYS order: smi, sp500, sxi_re, gold, ust
CORRELATIONS = [
    [1.00,  0.80,  0.55,  0.15, -0.10],
    [0.80,  1.00,  0.45,  0.10, -0.15],
    [0.55,  0.45,  1.00,  0.20,  0.10],
    [0.15,  0.10,  0.20,  1.00,  0.25],
    [-0.10, -0.15, 0.10,  0.25,  1.00],
]


def build_sample() -> dict:
    scenario = {
        "name": "Since Fed Rate Decision",
        "start_date": "2024-09-18",
        "end_date": "2024-12-15",
        "holding_days": 88,
        "base_currency": BASE_CURRENCY,
    }
    # key: name, currency, start/end price (local), start/end FX (value of 1 unit
    # of the asset currency in KWD), invested (KWD), target weight, min, max,
    # long-run expected annual return, annual volatility.
    assets = {
        "smi":    dict(start_price=12000.0, end_price=11600.0, start_fx=0.3600, end_fx=0.3550,
                       invested=25000.0, target_w=0.18, min_w=0.05, max_w=0.30,
                       exp_return=0.060, volatility=0.140),
        "sp500":  dict(start_price=5600.0, end_price=5950.0, start_fx=0.3070, end_fx=0.3100,
                       invested=40000.0, target_w=0.32, min_w=0.10, max_w=0.40,
                       exp_return=0.075, volatility=0.160),
        "sxi_re": dict(start_price=530.0, end_price=545.0, start_fx=0.3600, end_fx=0.3550,
                       invested=15000.0, target_w=0.12, min_w=0.05, max_w=0.25,
                       exp_return=0.045, volatility=0.090),
        "gold":   dict(start_price=2580.0, end_price=2650.0, start_fx=0.3070, end_fx=0.3100,
                       invested=12000.0, target_w=0.10, min_w=0.05, max_w=0.20,
                       exp_return=0.040, volatility=0.150),
        "ust":    dict(start_price=99.0, end_price=98.0, start_fx=0.3070, end_fx=0.3100,
                       invested=18000.0, target_w=0.28, min_w=0.10, max_w=0.40,
                       exp_return=0.030, volatility=0.060),
    }
    indicators = {
        "dxy":     dict(start=101.0, end=107.0),
        "chf_usd": dict(start=1.180, end=1.140),
        "usd_kwd": dict(start=0.3070, end=0.3100),
        "chf_kwd": dict(start=0.3600, end=0.3550),
    }
    bond = dict(start_price=99.0, end_price=98.0, face=100.0, coupon_rate=0.040,
                holding_days=88, frequency=2)

    return {
        "scenario": scenario,
        "assets": assets,
        "indicators": indicators,
        "correlations": CORRELATIONS,
        "bond": bond,
        "risk_free": Defaults.RISK_FREE,
    }


def empty_like_sample() -> dict:
    """A blank template with the structure but no data."""
    s = build_sample()
    scen = dict(s["scenario"])
    scen.update(name="<Scenario name>", start_date="", end_date="", holding_days=None)
    assets = {k: {kk: None for kk in v} for k, v in s["assets"].items()}
    indicators = {k: {"start": None, "end": None} for k in s["indicators"]}
    bond = {k: None for k in s["bond"]}
    corr = [[1.0 if i == j else None for j in range(len(ASSET_KEYS))]
            for i in range(len(ASSET_KEYS))]
    return {"scenario": scen, "assets": assets, "indicators": indicators,
            "correlations": corr, "bond": bond, "risk_free": None}


if __name__ == "__main__":
    d = build_sample()
    inv = {k: d["assets"][k]["invested"] for k in ASSET_KEYS}
    tot = sum(inv.values())
    print("Scenario:", d["scenario"]["name"], "| total invested:", tot, d["scenario"]["base_currency"])
    for k in ASSET_KEYS:
        print(f"  {k:7} weight {inv[k]/tot:6.1%}")
