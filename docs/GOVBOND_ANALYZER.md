# Government Bond Analyzer

A simple, clean, beginner-friendly Excel workbook to value and analyze **one
government bond** — a fixed-coupon note/bond (semiannual or annual) or a
zero-coupon bill, especially US Treasuries. No VBA, no hidden formulas. Its
defining feature: **after every important result there is an "Explanation /
Interpretation" box** that says what the number means, why it matters, and whether
it looks high/low/risky/attractive.

```
pip install -r requirements.txt
python build_govbond.py                    # -> examples/Government Bond Analyzer.xlsx
python build_govbond.py --blank -o "examples/Government Bond Analyzer (blank).xlsx"
```

Open in Excel 365 and start on the **Inputs** sheet. Change only the yellow input
cells; everything else recalculates.

---

## The twelve sheets

| # | Sheet | What it does |
|---|-------|--------------|
| 1 | **Inputs / Bond Terms** | The only input page (defines every named range). Type/frequency drop-downs and a consistency warning. |
| 2 | **Price & Yield** | Works both ways: **Section A** yield-from-price (accrued, dirty, YTM, current yield, premium/discount); **Section B** price-from-yield (theoretical price at a yield -> cheap/fair/expensive); **Section C** a price-yield table. Interpretation box after each result. |
| 3 | **Cash Flows** | Coupon + principal schedule discounted at the yield; PVs sum to the dirty price and also give duration & convexity. |
| 4 | **Valuation Summary** | Clean/dirty, YTM, current yield, coupon, benchmark, spread, premium/discount, years, remaining coupons - each with an interpretation box. |
| 5 | **Duration & DV01** | Macaulay & modified duration, DV01 and convexity, each with a full explanation + interpretation. |
| 6 | **Rate Shock** | -100…+100 bps table: price change (duration only and duration + convexity), new price, gain/loss %, interpretation, plus a conclusion box (biggest upside/downside, main risk). |
| 7 | **Yield Curve** | Enter 3m/2y/5y/10y/30y yields -> line chart, maturity bucket, and a normal/flat/inverted read with clear explanations. |
| 8 | **Investment Attractiveness** | A transparent /10 score (yield /3, duration risk /3, DV01 /2, curve /1, **rate-outlook fit /1**) -> Attractive / Neutral / Not Attractive, with key factor/risk and an analyst override. |
| 9 | **Recommendation Summary** | One-page view: manual Buy/Hold/Avoid + the attractiveness view + all the key numbers + main positive/risk. |
| 10 | **Explanations** | 20 concepts in beginner English: formula, plain explanation, why it matters, how to interpret, example. |
| 11 | **Quality Check** | 11 independent checks (dirty identity, PV = dirty, price = reprice, duration/DV01/convexity positive, price-yield direction, zero-coupon, dates, frequency, price-vs-par sanity) with Pass/Warning/Fail. |
| 12 | **Limitations / Future Upgrades** | What is out of scope and what could come next. |

---

## What it answers

1. **What is the bond worth?** dirty/clean price and the PV of its cash flows.
2. **What is the yield?** implied YTM from the market price (or a bill's discount yield).
3. **How does price change when yield changes?** the price-yield table and rate-shock table.
4. **How sensitive is it to rates?** duration, modified duration, DV01, convexity.
5. **Is it Attractive/Neutral/Not Attractive?** the /10 score across yield, duration risk, DV01, curve and rate outlook.
6. **Buy/Hold/Avoid?** a manual analyst call, informed by the above.

**Supported:** fixed-coupon government notes/bonds (semiannual or annual) and
zero-coupon bills. Face = 100, prices per 100 face, day-count selectable
(default Actual/Actual). **Not covered (Limitations sheet):** corporate bonds,
credit analysis, floaters, TIPS, callable bonds, OAS/Z-spread, repo, futures,
key-rate duration and full portfolio analysis.

---

## Verification

The workbook uses Excel's native bond functions, so correctness is verified with
the shared Python reference `bond/bondmath.py` and `tests/test_govbond.py` (7/7):
the price reconciles at the YTM; **price↔yield works both ways** (repricing at the
implied yield returns the market price; a lower test yield gives a higher price);
the price-yield direction is correct; modified = Macaulay/(1+y/f); DV01 and
convexity are positive; and a bill's duration equals its time to maturity. The
in-workbook **Quality Check** sheet repeats these live in Excel.

Worked example (US Treasury Note 4.00% 2034 at 96.50): YTM ≈ 4.48%, dirty ≈ 96.86,
Macaulay ≈ 7.52y, modified ≈ 7.36, convexity ≈ 63.9, DV01 ≈ 0.071; at the 4.30%
benchmark the theoretical price is ≈ 97.80 (so it reads slightly **cheap**); the
attractiveness score is 6/10 → **Neutral**.

This is an educational decision-support tool, **not investment advice**.
