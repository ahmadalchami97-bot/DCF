# Fixed-Rate Bond Analyzer

A clean, beginner-friendly but technically correct Excel workbook for valuing and
analyzing **one plain-vanilla fixed-rate bond**. No VBA, no hidden formulas — the
headline analytics use Excel's own bond functions and the logic is shown in a
transparent cash-flow schedule, with an independent audit sheet that re-checks
everything.

```
pip install -r requirements.txt
python build_bond.py                       # -> examples/Fixed-Rate Bond Analyzer.xlsx
python build_bond.py --blank -o "examples/Fixed-Rate Bond Analyzer (blank).xlsx"
```

Open in Excel 365 and start on the **Cover** sheet. Type your bond into **Bond
Terms**; everything else updates automatically.

---

## The twelve sheets

| # | Sheet | What it does |
|---|-------|--------------|
| 1 | **Cover** | What the model does, assumptions, supported vs unsupported bonds, how to use it. |
| 2 | **Bond Terms** | The main input page. Defines every named range the rest of the workbook reads. |
| 3 | **Cash Flows** | Coupon + principal schedule, discounted at the YTM. PVs sum to the dirty price; also yields Macaulay duration and convexity. |
| 4 | **Valuation** | Accrued interest, clean vs dirty price, YTM, current yield, premium/discount, spread, with an interpretation box. |
| 5 | **Duration & Convexity** | Macaulay & modified duration, convexity, DV01, and a yield-shock stress table (+/-25/50/100 bps). |
| 6 | **Call & YTW** | Yield to maturity, yield to call, and yield to worst, with plain-English guidance. |
| 7 | **Issuer Financial Strength** | Optional, simple credit ratios (leverage, coverage, liquidity) with divide-by-zero guards. |
| 8 | **Maturity Wall** | Debt-maturity schedule, a bar chart, and a near-term refinancing-risk read. |
| 9 | **Risks** | A structured Low/Medium/High checklist across nine risk categories. |
| 10 | **Recommendation** | One-page summary + automatic hints. The Buy/Hold/Sell/Avoid call stays a manual input. |
| 11 | **Formula Explanations** | Every calculation in plain English: formula, meaning, and how to read it. |
| 12 | **Audit** | Independent re-checks (Excel bond functions, bump-and-reprice, the schedule, logic tests) with Pass/Warning/Fail. |

---

## What it computes (and how)

Headline analytics use Excel's native, battle-tested bond functions so the numbers
are correct under the stated conventions:

```
Accrued   = COUPDAYBS/COUPDAYS x periodic coupon         (day-count based)
YTM       = YIELD(settle, maturity, coupon, clean, 100, freq, basis)   (zero: (Face/Price)^(1/T)-1)
Clean     = PRICE(settle, maturity, coupon, YTM, 100, freq, basis)     (audit reprice)
Dirty     = clean + accrued
Macaulay  = DURATION(...)   Modified = MDURATION(...)     (zero: = time to maturity)
Convexity = from the cash-flow schedule (Excel has no convexity function)
DV01      = Modified duration x dirty price x 0.0001
YTC       = YIELD(settle, CALL DATE, coupon, clean, CALL PRICE, freq, basis)
YTW       = min(YTM, YTC)   (or YTM if not callable)
```

The **Cash Flows** sheet shows the logic behind the price: each payment discounted
by `1 / (1 + YTM/frequency) ^ (periods to payment)`, using the fraction of the
first period remaining so the PVs reconcile to the dirty price to the cent.

**Supported:** annual, semiannual, quarterly and zero-coupon plain-vanilla
fixed-rate bonds; optional one-date/one-price call analysis; a simple spread vs a
government benchmark; optional simple issuer credit ratios. **Day-count bases:**
0 = US 30/360, 1 = Actual/Actual, 2 = Actual/360, 3 = Actual/365, 4 = European 30/360.

**Not supported (listed as limitations, not modelled):** monthly-coupon bonds,
floating-rate notes, amortizing/sinking-fund bonds, inflation-linked bonds,
OAS/Z-spread, full callable-bond option valuation, CDS-implied credit, and full
issuer forecasting/distressed recovery.

---

## Using it with a different bond

Change only the yellow input cells on **Bond Terms** (and, optionally, the
**Issuer Financial Strength**, **Maturity Wall** and **Risks** sheets). Everything
else — cash flows, price, yield, duration, the audit checks — recalculates. The
worked example is *Atlas Manufacturing 5.00% 2030* (semiannual, 30/360, callable).

---

## Verification

Because the workbook uses Excel's native bond functions (which a dependency-free
evaluator can't run), correctness is verified three ways:

1. **An independent Python reference** (`bond/bondmath.py`) recomputes the analytics
   from first principles (street convention). `tests/test_bond.py` (11/11) checks it
   against known cases and for internal consistency (price reconciles at the YTM;
   modified = Macaulay/(1+y/f); DV01 by two methods agree; convexity positive;
   zero-coupon duration = time to maturity; YTW logic), and confirms the workbook
   builds and wires up every named range.
2. **The in-workbook Audit sheet** re-checks each result live in Excel with a
   different method (ACCRINT, YIELD/PRICE, DURATION/MDURATION, bump-and-reprice,
   the cash-flow schedule, and logical/date/frequency tests) with stated tolerances.
3. **Worked-example values** (for the sample bond): YTM ~5.36%, accrued ~0.90,
   dirty ~99.40, Macaulay ~4.30y, modified ~4.19, convexity ~20.9, DV01 ~0.042,
   YTC ~6.24%, YTW ~5.36%.

---

## Notes & future upgrades

* Prices are quoted **per 100 face** (market convention); keep Face = 100.
* Net interest/duration use the standard street convention; results match Excel's
  `YIELD`/`PRICE`/`DURATION`.
* Future upgrades (not in this version): monthly coupons, floating-rate notes,
  amortizing bonds, inflation-linked bonds, OAS/Z-spread, full option valuation,
  CDS-implied credit, and issuer forecasting.
* This is an educational decision-support tool, **not investment advice**.
