"""
Sample dataset for the ratio workbook: "Vanta Software Group plc" (fictional).

Built by an articulated roll-forward (10 historical + 5 forecast years, plus one
hidden anchor year used to seed averages/growth). Every balance-sheet movement
flows through the cash-flow statement, so for every displayed year:

    Total assets == Total liabilities + equity
    Operating cash flow + investing + financing == change in cash

These identities are asserted at build time. Profile: a high-quality,
asset-light software compounder with decelerating but strong growth, expanding
margins, negative working capital (deferred revenue), low leverage and rising
shareholder returns -- ideal for exercising every ratio, score and read.
"""

from __future__ import annotations

HIST_YEARS = 10
FCST_YEARS = 5


def build_sample() -> dict:
    n_disp = HIST_YEARS + FCST_YEARS          # 15 displayed
    n = n_disp + 1                            # + hidden anchor at index 0
    r = lambda x: int(round(x))               # noqa: E731

    # growth path (index 0 = anchor). Decelerating from ~21% to ~7%.
    g = [0.21, 0.20, 0.19, 0.18, 0.16, 0.15, 0.14, 0.12, 0.11, 0.10,
         0.09, 0.09, 0.085, 0.08, 0.075, 0.07]
    revenue = [800.0]
    for i in range(1, n):
        revenue.append(revenue[-1] * (1 + g[i]))

    # margins improving over time (operating leverage)
    def ramp(a, b):
        return [a + (b - a) * i / (n - 1) for i in range(n)]

    gm = ramp(0.55, 0.60)            # gross margin
    opex_p = ramp(0.33, 0.30)        # operating expense % (ex-D&A)
    dep_p = ramp(0.050, 0.045)       # depreciation %
    acq_p = ramp(0.035, 0.020)       # acquisitions % of revenue (grows goodwill)
    dso, dio, dpo = 55, 12, 42
    oca_p = 0.03
    ocl_p = ramp(0.14, 0.18)         # deferred revenue grows -> light WC
    capex_p = ramp(0.070, 0.055)
    tax_rate = 0.21
    int_rate = 0.045

    long_term_debt = [0, 0, 0, 0, 0, 60, 90, 120, 150, 180, 180, 175, 165, 150, 135, 120]
    short_term_debt = [0] * n
    payout = [0, 0, 0, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20,
              0.20, 0.21, 0.22, 0.23, 0.24, 0.24]
    bb_p = [0, 0, 0, 0, 0, 0.05, 0.08, 0.10, 0.12, 0.15, 0.15, 0.16, 0.17, 0.18, 0.18, 0.18]
    pe_target = [0, 28, 30, 32, 33, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24]

    # flat / anchored balances
    other_nca = 50
    other_ncl = 40
    cash = [200.0]
    ppe = [120.0]
    goodwill = [300.0]               # grows via acquisitions (cash -> goodwill)
    shares = [500.0]
    price = [20.0]

    # income statement
    cogs = [0.0] * n
    gross = [0.0] * n
    opex = [0.0] * n
    ebitda = [0.0] * n
    dep = [0.0] * n
    ebit = [0.0] * n
    intexp = [0.0] * n
    pretax = [0.0] * n
    tax = [0.0] * n
    ni = [0.0] * n
    for i in range(n):
        gross[i] = revenue[i] * gm[i]
        cogs[i] = revenue[i] - gross[i]
        opex[i] = revenue[i] * opex_p[i]
        ebitda[i] = gross[i] - opex[i]
        dep[i] = revenue[i] * dep_p[i]
        ebit[i] = ebitda[i] - dep[i]
        prior_debt = (long_term_debt[i - 1] + short_term_debt[i - 1]) if i else \
            (long_term_debt[i] + short_term_debt[i])
        intexp[i] = int_rate * prior_debt
        pretax[i] = ebit[i] - intexp[i]
        tax[i] = pretax[i] * tax_rate
        ni[i] = pretax[i] - tax[i]

    # working capital & ppe roll
    recv = [revenue[i] * dso / 365 for i in range(n)]
    inv = [cogs[i] * dio / 365 for i in range(n)]
    oca = [revenue[i] * oca_p for i in range(n)]
    ap = [(cogs[i] + opex[i]) * dpo / 365 for i in range(n)]
    ocl = [revenue[i] * ocl_p[i] for i in range(n)]
    capex = [revenue[i] * capex_p[i] for i in range(n)]
    acq = [revenue[i] * acq_p[i] for i in range(n)]
    for i in range(1, n):
        ppe.append(ppe[i - 1] + capex[i] - dep[i])
        goodwill.append(goodwill[i - 1] + acq[i])

    # cash flow, cash & equity roll
    ocf = [0.0] * n
    div = [0.0] * n
    bb = [0.0] * n
    for i in range(1, n):
        d_wc = -((recv[i] - recv[i - 1]) + (inv[i] - inv[i - 1]) + (oca[i] - oca[i - 1])) \
            + ((ap[i] - ap[i - 1]) + (ocl[i] - ocl[i - 1]))
        ocf[i] = ni[i] + dep[i] + d_wc
        div[i] = payout[i] * ni[i]
        bb[i] = bb_p[i] * ni[i]
        debt_chg = (long_term_debt[i] + short_term_debt[i]) - \
                   (long_term_debt[i - 1] + short_term_debt[i - 1])
        net_chg = ocf[i] - capex[i] - acq[i] + (debt_chg - div[i] - bb[i])
        cash.append(cash[i - 1] + net_chg)
        shares.append(shares[i - 1] - bb[i] / price[i - 1])     # buybacks at prior price
        price.append(max(1.0, pe_target[i] * ni[i] / shares[i]))

    # equity & retained earnings roll (anchor equity = balancing plug)
    def assets(i):
        return cash[i] + recv[i] + inv[i] + oca[i] + ppe[i] + goodwill[i] + other_nca

    def liabs(i):
        return ap[i] + short_term_debt[i] + ocl[i] + long_term_debt[i] + other_ncl

    equity = [assets(0) - liabs(0)]
    retained = [150.0]
    for i in range(1, n):
        equity.append(equity[i - 1] + ni[i] - div[i] - bb[i])
        retained.append(retained[i - 1] + ni[i] - div[i])

    # integrity assertions
    for i in range(1, n):
        assert abs(assets(i) - (liabs(i) + equity[i])) < 1e-6, f"BS imbalance yr {i}"
        assert abs((cash[i] - cash[i - 1]) -
                   (ocf[i] - capex[i] - acq[i] + ((long_term_debt[i] + short_term_debt[i]) -
                    (long_term_debt[i - 1] + short_term_debt[i - 1])) - div[i] - bb[i]))\
            < 1e-6, f"CF tie yr {i}"

    disp = slice(1, n)
    yrs = list(range(2015, 2015 + n_disp))
    periods = [f"FY{y}" for y in yrs]

    def s(a, rnd=True):
        return [r(x) if rnd else round(x, 2) for x in a[disp]]

    # Round each balance-sheet component, then set equity as the exact integer
    # plug so the balance sheet balances to the unit after rounding.
    cash_, ar_, inv_, oca_, ppe_, gw_ = (s(x) for x in (cash, recv, inv, oca, ppe, goodwill))
    ap_, std_, ocl_, ltd_ = (s(x) for x in (ap, short_term_debt, ocl, long_term_debt))
    equity_disp = [(cash_[i] + ar_[i] + inv_[i] + oca_[i] + ppe_[i] + gw_[i] + other_nca)
                   - (ap_[i] + std_[i] + ocl_[i] + ltd_[i] + other_ncl) for i in range(n_disp)]

    series = {
        "revenue": s(revenue), "cogs": s(cogs), "opex": s(opex), "depreciation": s(dep),
        "interest_expense": s(intexp), "other_income": [0] * n_disp, "tax_expense": s(tax),
        "cash": cash_, "receivables": ar_, "inventory": inv_,
        "other_current_assets": oca_, "ppe": ppe_,
        "goodwill_intangibles": gw_, "other_noncurrent_assets": [other_nca] * n_disp,
        "accounts_payable": ap_, "short_term_debt": std_,
        "other_current_liabilities": ocl_, "long_term_debt": ltd_,
        "other_noncurrent_liabilities": [other_ncl] * n_disp,
        "equity": equity_disp, "retained_earnings": s(retained),
        "operating_cash_flow": s(ocf), "capex": s(capex),
        "dividends_paid": s(div), "buybacks": s(bb),
        "share_price": s(price, rnd=False), "shares_outstanding": [r(x) for x in shares[disp]],
    }
    scalars = {"rf": 0.04, "erp": 0.05, "beta": 1.10, "pretax_kd": 0.05, "tax_rate": 0.21}
    # Peer ratios (latest year) for the benchmarking sheet — analyst inputs.
    peers = {
        "names": ["Peer A", "Peer B", "Peer C", "Peer D", "Peer E"],
        "gross_margin": [0.55, 0.62, 0.58, 0.50, 0.60],
        "operating_margin": [0.20, 0.25, 0.18, 0.15, 0.22],
        "net_margin": [0.15, 0.18, 0.14, 0.11, 0.16],
        "roe": [0.16, 0.22, 0.14, 0.12, 0.19],
        "roic": [0.20, 0.30, 0.18, 0.15, 0.25],
        "current_ratio": [2.0, 1.8, 2.5, 1.5, 2.2],
        "net_debt_ebitda": [0.5, -1.0, 1.5, 2.0, 0.0],
        "rev_cagr5": [0.10, 0.14, 0.08, 0.06, 0.12],
        "fcf_margin": [0.15, 0.20, 0.12, 0.10, 0.18],
        "ev_ebitda": [18.0, 22.0, 15.0, 12.0, 20.0],
    }
    meta = {
        "name": "Vanta Software Group plc", "ticker": "VNTA",
        "industry": "Application Software", "currency": "USD", "units": "millions",
        "fiscal_year_end": "31 December",
        "analysis_date": "=TEXT(TODAY(),\"dd mmm yyyy\")",
        "description": ("Fictional enterprise application-software company used as a "
                        "worked example. All figures are illustrative."),
    }
    return {"meta": meta, "periods": periods, "series": series, "scalars": scalars,
            "peers": peers, "hist_years": HIST_YEARS, "fcst_years": FCST_YEARS}


def empty_like_sample() -> dict:
    s = build_sample()
    series = {k: [None] * len(s["periods"]) for k in s["series"]}
    scalars = {k: None for k in s["scalars"]}
    peers = {k: ([None] * 5 if k != "names" else s["peers"]["names"]) for k in s["peers"]}
    meta = dict(s["meta"])
    meta.update(name="<Company name>", ticker="<TICKER>", industry="<Industry>",
                description="<Business description>")
    return {"meta": meta, "periods": s["periods"], "series": series, "scalars": scalars,
            "peers": peers, "hist_years": HIST_YEARS, "fcst_years": FCST_YEARS}


if __name__ == "__main__":
    d = build_sample()
    print("Built:", d["meta"]["name"], "| years:", len(d["periods"]))
    print("FY2024 revenue:", d["series"]["revenue"][9])
