"""
Sample dataset: "Helios Diversified Industries plc" (fictional).

ELEVEN years of *reported* historical statements (FY2015-FY2025) for a generic
diversified industrial. These are the numbers an analyst would paste in from
filings: on the Historical sheet every one of them is a hard-coded blue input.
They are produced here by the same articulated roll-forward the Forecast sheet
uses (so the example is internally consistent), then rounded to whole units with
equity set as the exact plug so the balance sheet ties to the unit every year.

The forecast itself is NOT built here -- it is live formulas in the workbook. All
this module supplies for the forecast is nine single base-case driver values.
"""

from __future__ import annotations

from .config import ACTUAL_YEARS, FIRST_YEAR, HORIZON

# Canonical historical line items, in display order. Everything here is a pure
# input on the Historical sheet; the keys are referenced by the Forecast anchor,
# the Bridge and the Diagnostics.
INCOME_LINES = ["revenue", "cogs", "gross_profit", "opex", "ebitda",
                "depreciation", "ebit", "net_interest", "pretax", "tax", "net_income"]
BALANCE_ASSETS = ["cash", "nwc", "net_ppe", "other_assets", "total_assets"]
BALANCE_LE = ["total_debt", "other_liabilities", "total_liabilities", "equity"]
CASHFLOW_LINES = ["operating_cash_flow", "capex", "fcf"]


def build_sample() -> dict:
    n_disp = ACTUAL_YEARS
    n = n_disp + 1                      # + one hidden seed year at index 0
    r = lambda x: int(round(x))         # noqa: E731

    # --- income statement drivers (gentle, realistic drift) ----------------
    g = [0.0, 0.06, 0.06, 0.05, 0.07, 0.05, 0.06, 0.05, 0.04, 0.05, 0.04, 0.04]
    revenue = [4200.0]
    for i in range(1, n):
        revenue.append(revenue[-1] * (1 + g[i]))

    def ramp(a, b):
        return [a + (b - a) * i / (n - 1) for i in range(n)]

    gm = ramp(0.340, 0.356)            # gross margin
    opex_p = ramp(0.196, 0.188)        # opex (ex-D&A) % of revenue
    dep_p = 0.050                      # D&A % of revenue
    capex_p = ramp(0.060, 0.052)       # capex % of revenue
    nwc_p = 0.120                      # net working capital % of revenue
    tax_rate = 0.25
    net_int_rate = 0.050
    payout = 0.65                      # historical dividend payout (keeps modest net debt)

    other_assets_v = 300.0
    other_liab_v = 250.0
    total_debt_sched = [1700, 1700, 1650, 1600, 1550, 1500, 1450, 1400, 1350, 1300, 1250, 1200]

    # revenue-driven series with no cash dependency
    nwc = [revenue[i] * nwc_p for i in range(n)]
    capex = [revenue[i] * capex_p[i] for i in range(n)]
    dep = [revenue[i] * dep_p for i in range(n)]
    gross = [revenue[i] * gm[i] for i in range(n)]
    cogs = [revenue[i] - gross[i] for i in range(n)]
    opex = [revenue[i] * opex_p[i] for i in range(n)]
    ebitda = [gross[i] - opex[i] for i in range(n)]
    ebit = [ebitda[i] - dep[i] for i in range(n)]
    ppe = [2000.0]
    for i in range(1, n):
        ppe.append(ppe[i - 1] + capex[i] - dep[i])

    # one forward pass: net interest uses OPENING net debt, so cash[i-1] is
    # always already known (exactly how the live forecast avoids circularity).
    cash = [300.0]
    net_int = [0.0] * n; pretax = [0.0] * n; tax = [0.0] * n; ni = [0.0] * n
    ocf = [0.0] * n; div = [0.0] * n; fcf = [0.0] * n
    for i in range(n):
        beg_net_debt = (total_debt_sched[i - 1] - cash[i - 1]) if i else (total_debt_sched[0] - cash[0])
        net_int[i] = net_int_rate * beg_net_debt
        pretax[i] = ebit[i] - net_int[i]
        tax[i] = pretax[i] * tax_rate
        ni[i] = pretax[i] - tax[i]
        div[i] = payout * ni[i]
        if i:
            d_nwc = nwc[i] - nwc[i - 1]
            ocf[i] = ni[i] + dep[i] - d_nwc
            fcf[i] = ocf[i] - capex[i]
            new_debt = total_debt_sched[i] - total_debt_sched[i - 1]
            cash.append(cash[i - 1] + ocf[i] - capex[i] + new_debt - div[i])

    # --- round to whole units; equity is the exact plug so the BS ties ------
    disp = slice(1, n)

    def s(a):
        return [r(x) for x in a[disp]]

    revenue_, cogs_, opex_, dep_, net_int_v = (s(x) for x in (revenue, cogs, opex, dep, net_int))
    tax_, capex_, ocf_, fcf_ = (s(x) for x in (tax, capex, ocf, fcf))
    cash_, nwc_, ppe_ = s(cash), s(nwc), s(ppe)
    gross_ = [revenue_[i] - cogs_[i] for i in range(n_disp)]
    ebitda_ = [gross_[i] - opex_[i] for i in range(n_disp)]
    ebit_ = [ebitda_[i] - dep_[i] for i in range(n_disp)]
    pretax_ = [ebit_[i] - net_int_v[i] for i in range(n_disp)]
    ni_ = [pretax_[i] - tax_[i] for i in range(n_disp)]
    other_assets_ = [r(other_assets_v)] * n_disp
    other_liab_ = [r(other_liab_v)] * n_disp
    total_debt_ = [total_debt_sched[i] for i in range(1, n)]
    total_assets_ = [cash_[i] + nwc_[i] + ppe_[i] + other_assets_[i] for i in range(n_disp)]
    total_liab_ = [total_debt_[i] + other_liab_[i] for i in range(n_disp)]
    equity_ = [total_assets_[i] - total_liab_[i] for i in range(n_disp)]

    # integrity assertion (the example must itself be flawless)
    for i in range(n_disp):
        assert total_assets_[i] == cash_[i] + nwc_[i] + ppe_[i] + other_assets_[i]
        assert total_liab_[i] == total_debt_[i] + other_liab_[i]
        assert total_assets_[i] == total_liab_[i] + equity_[i], f"BS imbalance yr {i}"

    hist = {
        "revenue": revenue_, "cogs": cogs_, "gross_profit": gross_, "opex": opex_,
        "ebitda": ebitda_, "depreciation": dep_, "ebit": ebit_, "net_interest": net_int_v,
        "pretax": pretax_, "tax": tax_, "net_income": ni_,
        "cash": cash_, "nwc": nwc_, "net_ppe": ppe_, "other_assets": other_assets_,
        "total_assets": total_assets_,
        "total_debt": total_debt_, "other_liabilities": other_liab_,
        "total_liabilities": total_liab_, "equity": equity_,
        "operating_cash_flow": ocf_, "capex": capex_, "fcf": fcf_,
    }
    meta = {
        "name": "Helios Diversified Industries plc", "ticker": "HELI",
        "currency": "USD", "units": "millions", "fiscal_year_end": "31 December",
        "description": "Fictional diversified industrial used as a worked example; all figures illustrative.",
    }
    # One base-case value per driver. These pre-fill the (fully editable)
    # per-year Assumptions grid; there is no scenario machinery.
    drivers = {
        "rev_growth": 0.045, "ebitda_margin": 0.168, "da_pct": 0.050,
        "capex_pct": 0.052, "nwc_pct": 0.120, "net_int_rate": 0.050,
        "tax_rate": 0.250, "payout": 0.500, "net_new_debt": -50,
    }
    return {"meta": meta, "first_year": FIRST_YEAR, "actual_years": n_disp,
            "horizon": HORIZON, "hist": hist, "drivers": drivers}


def empty_like_sample() -> dict:
    """A blank template: same structure, no data -- to prove graceful degrading."""
    s = build_sample()
    hist = {k: [None] * s["actual_years"] for k in s["hist"]}
    drivers = {k: None for k in s["drivers"]}
    meta = dict(s["meta"])
    meta.update(name="<Company name>", ticker="<TICKER>",
                description="Blank template -- paste reported actuals into the Historical sheet.")
    return {"meta": meta, "first_year": FIRST_YEAR, "actual_years": s["actual_years"],
            "horizon": HORIZON, "hist": hist, "drivers": drivers}


if __name__ == "__main__":
    d = build_sample()
    h = d["hist"]
    print("Built:", d["meta"]["name"], "| actual years:", d["actual_years"])
    print(f"FY{FIRST_YEAR + d['actual_years'] - 1} revenue:", h["revenue"][-1],
          "| equity:", h["equity"][-1], "| total assets:", h["total_assets"][-1])
