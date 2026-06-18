"""
Sample company dataset: "Meridian Industrial Components plc" (fictional).

The data is produced by an *articulated roll-forward*, not hand-typed. Every
balance-sheet movement is mirrored in the cash-flow statement, so:

    Total assets == Total liabilities + equity            (every year)
    CFO + CFI + CFF == change in cash                      (every year)

This is asserted at build time, so the shipped example is guaranteed to pass the
model's own diagnostics. It also means the file is a faithful demonstration of
"don't invent numbers": the statements are internally consistent.

Profile: a mature industrial manufacturer with mid-single-digit, decelerating
revenue growth, broadly stable but slightly compressing margins, moderate
leverage, real capex, dividends and modest buybacks -- i.e. a dataset that
exercises every part of the engine (turnover ratios, leverage, returns, FCF).
"""

from __future__ import annotations


def build_sample() -> dict:
    # Internal years include a hidden 2019 anchor (index 0) used only to roll
    # the first displayed year's cash flow. Displayed = indices 1..5.
    years_all = [2019, 2020, 2021, 2022, 2023, 2024]
    n = len(years_all)

    # --- driver assumptions (index 0 = 2019 anchor) ------------------------
    revenue = [3650, 3900, 4200, 4600, 4900, 5100]
    gross_m = [0.351, 0.350, 0.352, 0.355, 0.353, 0.350]
    sga_p = [0.201, 0.200, 0.199, 0.198, 0.200, 0.202]
    rd_p = [0.030, 0.030, 0.030, 0.031, 0.031, 0.032]
    other_op_p = [0.005] * n
    da_p = [0.060, 0.060, 0.060, 0.059, 0.060, 0.061]
    capex_p = [0.066, 0.065, 0.064, 0.063, 0.062, 0.060]
    dso = [45, 45, 46, 45, 45, 46]
    dio = [63, 64, 64, 65, 64, 65]
    dpo = [47, 48, 48, 49, 48, 48]
    oca_p = [0.020] * n
    ocl_p = [0.060] * n
    st_debt = [145, 150, 150, 160, 170, 170]
    lt_debt = [1230, 1250, 1300, 1350, 1300, 1250]
    payout = [0.28, 0.29, 0.30, 0.30, 0.31, 0.31]
    buyback = [30, 40, 45, 50, 55, 60]
    shares_basic = [507, 505, 503, 501, 499, 497]

    tax_rate = 0.255
    int_rate_debt = 0.050
    int_rate_cash = 0.015
    dil_add = 6  # diluted = basic + this

    # Flat balance-sheet items (no cash impact -> articulation holds).
    st_inv = 110
    goodwill = 1200
    other_nca = 180
    other_ncl = 380

    # Anchor (2019) balances set directly.
    cash0 = 340
    ppe0 = 1760

    r = lambda x: int(round(x))  # noqa: E731  -- round to whole $m

    # --- income statement --------------------------------------------------
    gross_profit, cogs, sga, rd, other_op, ebit, da, ebitda = ([0] * n for _ in range(8))
    int_exp, int_inc, pretax, tax, net_income = ([0] * n for _ in range(5))
    for i in range(n):
        gross_profit[i] = r(revenue[i] * gross_m[i])
        cogs[i] = revenue[i] - gross_profit[i]
        sga[i] = r(revenue[i] * sga_p[i])
        rd[i] = r(revenue[i] * rd_p[i])
        other_op[i] = r(revenue[i] * other_op_p[i])
        ebit[i] = gross_profit[i] - sga[i] - rd[i] - other_op[i]
        da[i] = r(revenue[i] * da_p[i])
        ebitda[i] = ebit[i] + da[i]

    # --- working capital & ppe --------------------------------------------
    ar = [r(dso[i] / 365 * revenue[i]) for i in range(n)]
    inv = [r(dio[i] / 365 * cogs[i]) for i in range(n)]
    ap = [r(dpo[i] / 365 * cogs[i]) for i in range(n)]
    oca = [r(oca_p[i] * revenue[i]) for i in range(n)]
    ocl = [r(ocl_p[i] * revenue[i]) for i in range(n)]
    capex = [r(capex_p[i] * revenue[i]) for i in range(n)]

    ppe = [0] * n
    ppe[0] = ppe0
    for i in range(1, n):
        ppe[i] = ppe[i - 1] + capex[i] - da[i]

    # --- interest, tax, NI (needs prior balances) --------------------------
    cash = [0] * n
    cash[0] = cash0
    for i in range(n):
        prior_debt = (st_debt[i - 1] + lt_debt[i - 1]) if i > 0 else (st_debt[i] + lt_debt[i])
        prior_liquid = (cash[i - 1] + st_inv) if i > 0 else (cash[i] + st_inv)
        int_exp[i] = r(int_rate_debt * prior_debt)
        int_inc[i] = r(int_rate_cash * prior_liquid)
        pretax[i] = ebit[i] - int_exp[i] + int_inc[i]
        tax[i] = r(tax_rate * pretax[i])
        net_income[i] = pretax[i] - tax[i]
        if i > 0:  # roll cash once flows are known below; placeholder here
            pass

    # --- cash-flow statement & cash roll-forward ---------------------------
    cf_wc = [0] * n
    cfo = [0] * n
    cfi = [0] * n
    cff = [0] * n
    net_change = [0] * n
    dividends = [0] * n
    debt_change = [0] * n
    for i in range(1, n):
        d_ar = ar[i] - ar[i - 1]
        d_inv = inv[i] - inv[i - 1]
        d_oca = oca[i] - oca[i - 1]
        d_ap = ap[i] - ap[i - 1]
        d_ocl = ocl[i] - ocl[i - 1]
        cf_wc[i] = -(d_ar + d_inv + d_oca) + (d_ap + d_ocl)
        cfo[i] = net_income[i] + da[i] + cf_wc[i]
        cfi[i] = -capex[i]
        debt_change[i] = (st_debt[i] + lt_debt[i]) - (st_debt[i - 1] + lt_debt[i - 1])
        dividends[i] = r(payout[i] * net_income[i])
        cff[i] = debt_change[i] - dividends[i] - buyback[i]
        net_change[i] = cfo[i] + cfi[i] + cff[i]
        cash[i] = cash[i - 1] + net_change[i]

    # --- equity roll-forward (anchor = plug) -------------------------------
    def total_assets(i):
        return cash[i] + st_inv + ar[i] + inv[i] + oca[i] + ppe[i] + goodwill + other_nca

    def total_liabs(i):
        return ap[i] + st_debt[i] + ocl[i] + lt_debt[i] + other_ncl

    equity = [0] * n
    equity[0] = total_assets(0) - total_liabs(0)  # plug for the hidden anchor
    for i in range(1, n):
        equity[i] = equity[i - 1] + net_income[i] - dividends[i] - buyback[i]

    # --- integrity assertions (the whole point of the roll-forward) --------
    for i in range(1, n):
        assert total_assets(i) == total_liabs(i) + equity[i], (
            f"balance sheet does not balance in {years_all[i]}: "
            f"A={total_assets(i)} vs L+E={total_liabs(i) + equity[i]}"
        )
        assert cash[i] - cash[i - 1] == net_change[i], (
            f"cash flow does not tie in {years_all[i]}"
        )

    # --- assemble displayed series (indices 1..5) --------------------------
    disp = slice(1, n)
    periods = [f"FY{y}" for y in years_all[1:]]

    def s(arr):
        return list(arr[disp])

    price = [100.0, 101.5, 103.0, 105.0, 107.0, 108.0]
    volume = [round(revenue[i] / price[i], 1) for i in range(n)]

    series = {
        # income statement (inputs only; subtotals are sheet formulas)
        "revenue": s(revenue),
        "cogs": s(cogs),
        "sga": s(sga),
        "rd": s(rd),
        "other_operating": s(other_op),
        "interest_expense": s(int_exp),
        "interest_income": s(int_inc),
        "other_nonoperating": [0, 0, 0, 0, 0],
        "tax_expense": s(tax),
        "minority_interest": [0, 0, 0, 0, 0],
        # balance sheet
        "cash": s(cash),
        "st_investments": [st_inv] * 5,
        "accounts_receivable": s(ar),
        "inventory": s(inv),
        "other_current_assets": s(oca),
        "ppe_net": s(ppe),
        "goodwill_intangibles": [goodwill] * 5,
        "other_noncurrent_assets": [other_nca] * 5,
        "accounts_payable": s(ap),
        "short_term_debt": s(st_debt),
        "other_current_liabilities": s(ocl),
        "long_term_debt": s(lt_debt),
        "other_noncurrent_liabilities": [other_ncl] * 5,
        "total_equity": s(equity),
        "minority_equity": [0, 0, 0, 0, 0],
        # cash flow
        "cf_net_income": s(net_income),
        "cf_da": s(da),
        "cf_wc_change": s(cf_wc),
        "cf_other_operating": [0, 0, 0, 0, 0],
        "capex": s(capex),
        "acquisitions": [0, 0, 0, 0, 0],
        "other_investing": [0, 0, 0, 0, 0],
        "debt_change": s(debt_change),
        "dividends_paid": s(dividends),
        "buybacks": s(buyback),
        "other_financing": [0, 0, 0, 0, 0],
        # shares & drivers
        "shares_basic": s(shares_basic),
        "shares_diluted": [x + dil_add for x in s(shares_basic)],
        "driver_volume": s(volume),
        "driver_price": s(price),
    }

    market = {
        "mkt_share_price": 17.50,
        "mkt_shares_out": 497,
        "mkt_beta": 1.05,
        "mkt_risk_free": 0.042,
        "mkt_erp": 0.052,
        "mkt_pretax_kd": 0.052,
        "mkt_tax_rate": 0.255,
    }

    meta = {
        "name": "Meridian Industrial Components plc",
        "ticker": "MICP",
        "currency": "USD",
        "units": "millions",
        "business_type": "Industrial / Manufacturing",
        "fiscal_year_end": "31 December",
        "description": (
            "Fictional designer and manufacturer of precision components and "
            "engineered subsystems for industrial machinery, automation and "
            "transportation OEMs. Sells globally through direct and distributor "
            "channels. Used here as a worked example; all figures are illustrative."
        ),
        "industry_note": (
            "Industrial / manufacturing: revenue is driven by unit volume x price "
            "and the capex cycle; margins are sensitive to input costs, capacity "
            "utilisation and operating leverage."
        ),
    }

    # derived values kept for tests / verification (not written as inputs)
    derived = {
        "periods": periods,
        "gross_profit": s(gross_profit),
        "ebit": s(ebit),
        "ebitda": s(ebitda),
        "da": s(da),
        "pretax_income": s(pretax),
        "net_income": s(net_income),
        "cfo": s(cfo),
        "cfi": s(cfi),
        "cff": s(cff),
        "net_change_cash": s(net_change),
        "total_assets": [total_assets(i) for i in range(1, n)],
        "total_liabilities": [total_liabs(i) for i in range(1, n)],
        "dividends_paid": s(dividends),
    }

    return {"meta": meta, "periods": periods, "series": series,
            "market": market, "derived": derived}


def empty_like_sample() -> dict:
    """A blank dataset (same shape, no values) for generating a fresh template."""
    s = build_sample()
    periods = ["FY—4", "FY—3", "FY—2", "FY—1", "FY—0"]
    series = {k: [None] * len(periods) for k in s["series"]}
    market = {k: None for k in s["market"]}
    meta = dict(s["meta"])
    meta.update(
        name="<Company name>",
        ticker="<TICKER>",
        description="<One-paragraph business description>",
        industry_note="<How revenue & margins are driven in this industry>",
    )
    return {"meta": meta, "periods": periods, "series": series,
            "market": market, "derived": {"periods": periods}}


if __name__ == "__main__":  # quick integrity check
    d = build_sample()
    print("Sample built OK:", d["meta"]["name"])
    print("Periods:", d["periods"])
    print("FY2024 revenue:", d["series"]["revenue"][-1])
    print("FY2024 net income:", d["derived"]["net_income"][-1])
