"""
Independent bond-analytics reference (pure Python).

This mirrors, from first principles, what the workbook computes with Excel's
built-in bond functions -- so the sample numbers can be verified without Excel and
the test suite can check internal consistency. Uses the standard street
convention (discount each cash flow by (1 + y/f)^((k-1)+w), where w is the
fraction of the current coupon period remaining).

Day counts implemented: 30/360 (bases 0 and 4) exactly; actual bases (1,2,3)
via actual-day counts. Good to well within the audit tolerances.
"""

from __future__ import annotations

from datetime import date


def add_months(d: date, n: int) -> date:
    m = d.month - 1 + n
    y = d.year + m // 12
    m = m % 12 + 1
    # clamp day to month end
    dim = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28,
           31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return date(y, m, min(d.day, dim))


def days_30360(d1: date, d2: date, european: bool = False) -> int:
    dd1, dd2 = d1.day, d2.day
    if european:
        dd1 = 30 if dd1 == 31 else dd1
        dd2 = 30 if dd2 == 31 else dd2
    else:  # US NASD
        if dd1 == 31:
            dd1 = 30
        if dd2 == 31 and dd1 == 30:
            dd2 = 30
    return 360 * (d2.year - d1.year) + 30 * (d2.month - d1.month) + (dd2 - dd1)


def year_fraction(d1: date, d2: date, basis: int) -> float:
    if basis == 0:
        return days_30360(d1, d2) / 360.0
    if basis == 4:
        return days_30360(d1, d2, european=True) / 360.0
    actual = (d2 - d1).days
    if basis == 2:
        return actual / 360.0
    if basis == 3:
        return actual / 365.0
    return actual / 365.0  # basis 1 (act/act) approximated as act/365 for year fractions


def coupon_dates(settle: date, maturity: date, freq: int):
    """All coupon dates strictly after settlement, up to and including maturity."""
    step = 12 // freq
    dates = [maturity]
    d = maturity
    while True:
        d = add_months(d, -step)
        if d <= settle:
            prev = d
            break
        dates.append(d)
    dates.sort()
    ncd = dates[0]
    return prev, ncd, dates  # previous coupon (<=settle), next coupon, future coupons


def _period_days(settle, maturity, freq, basis):
    prev, ncd, _ = coupon_dates(settle, maturity, freq)
    if basis in (0, 4):
        e = days_30360(prev, ncd, european=(basis == 4))
        a = days_30360(prev, settle, european=(basis == 4))
        dsc = days_30360(settle, ncd, european=(basis == 4))
    else:
        e = (ncd - prev).days
        a = (settle - prev).days
        dsc = (ncd - settle).days
    return a, e, dsc


def accrued_interest(settle, maturity, coupon, freq, basis, face=100.0):
    a, e, _ = _period_days(settle, maturity, freq, basis)
    return (coupon / freq) * face * (a / e if e else 0)


def _pv_flows(settle, maturity, coupon, y, freq, basis, face=100.0, redemption=None):
    """Return list of (years, cashflow, pv_at_y) using the street convention."""
    redemption = face if redemption is None else redemption
    _, _, futures = coupon_dates(settle, maturity, freq)
    a, e, dsc = _period_days(settle, maturity, freq, basis)
    w = dsc / e if e else 0
    n = len(futures)
    cpn = coupon / freq * face
    out = []
    for k in range(1, n + 1):
        cf = cpn + (redemption if k == n else 0)
        t_periods = (k - 1) + w
        pv = cf / (1 + y / freq) ** t_periods
        out.append((t_periods / freq, cf, pv, t_periods))
    return out


def price_clean(settle, maturity, coupon, y, freq, basis, face=100.0, redemption=None):
    flows = _pv_flows(settle, maturity, coupon, y, freq, basis, face, redemption)
    dirty = sum(pv for _, _, pv, _ in flows)
    return dirty - accrued_interest(settle, maturity, coupon, freq, basis, face)


def solve_yield(settle, maturity, coupon, clean, freq, basis, face=100.0, redemption=None):
    lo, hi = -0.5, 2.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if price_clean(settle, maturity, coupon, mid, freq, basis, face, redemption) > clean:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def analytics(settle, maturity, coupon, clean, freq, basis, face=100.0):
    """Full analytics for a coupon bond."""
    acc = accrued_interest(settle, maturity, coupon, freq, basis, face)
    dirty = clean + acc
    y = solve_yield(settle, maturity, coupon, clean, freq, basis, face)
    flows = _pv_flows(settle, maturity, coupon, y, freq, basis, face)
    total_pv = sum(pv for _, _, pv, _ in flows)
    mac = sum(yr * pv for yr, _, pv, _ in flows) / total_pv
    mod = mac / (1 + y / freq)
    conv = (sum(cf * tp * (tp + 1) / (1 + y / freq) ** (tp + 2) for _, cf, _, tp in flows)
            / (total_pv * freq ** 2))
    dv01 = mod * dirty * 1e-4
    return dict(accrued=acc, dirty=dirty, ytm=y, macaulay=mac, modified=mod,
                convexity=conv, dv01=dv01, total_pv=total_pv)


def zero_analytics(settle, maturity, clean, basis, face=100.0):
    t = year_fraction(settle, maturity, basis)
    y = (face / clean) ** (1 / t) - 1
    mac = t
    mod = mac / (1 + y)
    conv = t * (t + 1) / (1 + y) ** 2
    dv01 = mod * clean * 1e-4
    return dict(accrued=0.0, dirty=clean, ytm=y, macaulay=mac, modified=mod,
                convexity=conv, dv01=dv01, years=t)


def yield_to_call(settle, call_date, coupon, clean, freq, basis, call_price, face=100.0):
    return solve_yield(settle, call_date, coupon, clean, freq, basis, face, redemption=call_price)


if __name__ == "__main__":
    settle, maturity = date(2025, 3, 20), date(2030, 1, 15)
    a = analytics(settle, maturity, 0.05, 98.50, 2, 0)
    print("SAMPLE BOND  ATLAS 5.0% 2030  (semiannual, 30/360, clean 98.50)")
    for k, v in a.items():
        print(f"  {k:10}: {v:.6f}")
    ytc = yield_to_call(settle, date(2028, 1, 15), 0.05, 98.50, 2, 0, 102.0)
    print(f"  {'YTC':10}: {ytc:.6f}")
    print(f"  {'YTW':10}: {min(a['ytm'], ytc):.6f}")
