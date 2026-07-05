# US Treasury Bond Analyzer

A simple, clean, beginner-friendly Excel workbook for valuing and analyzing **one
US Treasury security** — a fixed-coupon Treasury note/bond (semiannual) or a
zero-coupon Treasury bill. No VBA, no hidden formulas. Headline analytics use
Excel's own bond functions; the logic is shown in a transparent cash-flow schedule
and re-checked on an independent audit sheet.

```
pip install -r requirements.txt
python build_ustreasury.py                 # -> examples/US Treasury Bond Analyzer.xlsx
python build_ustreasury.py --blank -o "examples/US Treasury Bond Analyzer (blank).xlsx"
```

Open in Excel 365 and start on the **Cover** sheet. Type your Treasury into **Bond
Terms**; everything else updates automatically.

> For a US Treasury the main risk is **interest-rate risk**, not credit risk —
> Treasuries are the risk-free benchmark. This model reflects that focus.

---

## The twelve sheets

| # | Sheet | What it does |
|---|-------|--------------|
| 1 | **Cover** | What the model does, why interest-rate risk is the focus, supported vs unsupported securities, how to use it. |
| 2 | **Bond Terms** | The one input page (defines every named range). Security type + frequency drop-downs, with a consistency warning. |
| 3 | **Cash Flows** | Coupon + principal schedule discounted at the yield; PVs sum to the dirty price and also give duration & convexity. |
| 4 | **Price & Yield** | Accrued, clean vs dirty price, YTM, current yield, premium/discount, spread, with an interpretation box. |
| 5 | **Duration & Convexity** | Macaulay & modified duration, convexity and DV01, explained simply. |
| 6 | **Rate Shock** | Estimated clean-price impact at -100/-50/-25/+25/+50/+100 bps, by duration only and duration + convexity. |
| 7 | **Yield Curve** | Enter the 3m/2y/5y/10y/30y Treasury yields; a line chart, the bond's maturity bucket, and a normal/flat/inverted read. |
| 8 | **Risk Summary** | A Treasury-specific Low/Medium/High checklist (interest-rate, duration, reinvestment, inflation, opportunity, liquidity, curve). |
| 9 | **Recommendation** | One-page summary + hints, an **Investment Attractiveness View** (a transparent /10 score with a rate-outlook link and analyst override), and a manual Buy/Hold/Avoid call. |
| 10 | **Formula & Concept Explanations** | Every key idea in beginner language: the formula, a plain explanation, why it matters for a Treasury analyst, how to interpret it, and a simple example. |
| 11 | **Audit** | Independent re-checks (Excel bond functions, bump-and-reprice, the schedule, date/frequency/sanity tests) with Pass/Warning/Fail. |
| 12 | **Limitations** | What is out of scope and possible future upgrades. |

---

## What it computes (and how)

```
Accrued   = COUPDAYBS/COUPDAYS x periodic coupon         (Actual/Actual; 0 for a bill)
YTM       = YIELD(...)   (bill: (Face/Price)^(1/T)-1, effective annual)
Dirty     = clean + accrued
Macaulay  = DURATION(...)   Modified = MDURATION(...)     (bill: = time to maturity)
Convexity = from the cash-flow schedule (Excel has no convexity function)
DV01      = Modified duration x dirty price x 0.0001
Rate shock: price change ~ -Modified x (dy) + 0.5 x convexity x (dy)^2
```

**Supported:** fixed-coupon Treasury notes/bonds (semiannual) and zero-coupon
Treasury bills. Face = 100, prices per 100 face, day-count = **Actual/Actual** (the
Treasury convention).

### Investment Attractiveness View (Recommendation sheet)

A simple, transparent framework that answers "is this bond a good investment?"
without pretending to know your situation. It scores five categories to a total of
10 — **yield attractiveness /3, duration/rate risk /3, price sensitivity (DV01) /2,
yield-curve context /1, liquidity/simplicity /1** — and classifies **8-10 =
Attractive, 5-7 = Neutral, 0-4 = Not Attractive**, with a plain-English main reason,
a key supporting factor and a key risk. A **rate-outlook** selector (yields
rise/fall/stable) adds directional context, and the model's suggestion is fully
**overridable** by the analyst. It is explicitly framed as a structured view, not a
personalised recommendation.

**Not covered (Limitations sheet):** corporate bonds, credit spreads, callable
bonds, floaters, TIPS, STRIPS complexity, repo/futures, key-rate duration, curve
bootstrapping, scenario probabilities and portfolio-level analysis. **Future
upgrades:** TIPS, key-rate duration, curve interpolation, portfolio duration, bond
ladders, and multi-Treasury comparison.

---

## Using it with a different Treasury

Change only the yellow input cells on **Bond Terms** (and, optionally, the **Yield
Curve** and **Risk Summary** sheets). For a bill, set Security type = *Treasury
Bill* and Coupon frequency = *Zero-coupon* (coupon 0%); the model switches to
zero-coupon math (accrued 0, duration ≈ time to maturity). The consistency check on
Bond Terms flags a note/bond that isn't semiannual, or a bill that isn't zero-coupon.

---

## Verification

The workbook uses Excel's native bond functions, so correctness is verified with
the shared independent Python reference (`bond/bondmath.py`) and `tests/test_ustreasury.py`
(8/8): the note price reconciles at the YTM; a discount price implies a yield above
the coupon; modified = Macaulay/(1+y/2); DV01 by two methods agree; convexity is
positive; the bill's duration equals its time to maturity; and the stress direction
is monotonic (yields up → price down). The **Audit** sheet repeats these checks live
in Excel with stated tolerances.

Worked-example values (T-Note 4.00% 2034 at 96.50): YTM ≈ 4.48%, accrued ≈ 0.36,
dirty ≈ 96.86, Macaulay ≈ 7.52y, modified ≈ 7.36, convexity ≈ 63.9, DV01 ≈ 0.071.

This is an educational decision-support tool, **not investment advice**.
