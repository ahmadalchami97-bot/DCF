# Government Bond Course & Calculator

A simple, clean, **beginner-first** Excel workbook that teaches you government
bonds from zero *and* works as a real calculation template. It assumes you know
nothing about bonds and guides you step by step, like a short course inside
Excel. Government bonds only — a Treasury bill (zero-coupon), a fixed-coupon note,
or a fixed-coupon bond. **No VBA, no macros, no hidden formulas, no institutional
black boxes.**

Its defining feature: **for every calculation the workbook first explains the
concept in plain English** — what it means, why it matters, what the formula
does, how to read the answer, whether it is good/bad/high/low/risky, and a simple
example — *before* it shows you the number.

```
pip install -r requirements.txt
python build_bondcourse.py                    # -> examples/Government Bond Course & Calculator.xlsx
python build_bondcourse.py --blank -o "examples/Government Bond Course & Calculator (blank).xlsx"
```

Open in **Excel 365** (it uses native bond functions) and start on the **Start
Here** sheet. You only ever type on the **Inputs** sheet — the yellow cells.
Everything else recalculates automatically.

**Colour code:** 🟡 yellow = you type here · black = a formula · green = a key
answer · grey = a note / explanation.

---

## The eighteen sheets

| # | Sheet | What it teaches / does |
|---|-------|------------------------|
| 1 | **Start Here** | A beginner guide: what a bond is, what a government bond is, bill vs note vs bond, the key words (face, coupon, maturity, price, yield), the one golden rule (price and yield move opposite), an 8-step how-to, and a map of every sheet. |
| 2 | **Inputs** | The only page you type on. Bond name, issuer, currency, type, face, position size, coupon, frequency, day-count, dates, market price/yield, benchmark, rate outlook, analyst — each with a beginner note. Drop-downs + a consistency warning. Defines every named range. |
| 3 | **Cash Flows** | What money you receive and what it is worth today. A coupon + principal schedule discounted at the yield; the present values sum to the dirty price and also feed duration and convexity. |
| 4 | **Price Basics** | Clean price, dirty price and accrued interest — the price you actually pay — with a premium/discount read. |
| 5 | **Yield Basics** | Your return: yield to maturity, current yield, premium/discount, and the spread over a benchmark. |
| 6 | **Price & Yield** | A two-way calculator. **A** yield-from-price; **B** price-from-yield (type a yield → theoretical price → cheap/fair/expensive); **C** a price-yield table showing prices fall as yields rise. |
| 7 | **Duration** | Macaulay and modified duration — how sensitive the price is to rate moves — each fully explained with an example. |
| 8 | **DV01** | The same risk in **money terms**: the value change per 1 basis point, per 100 face and scaled to your position. |
| 9 | **Convexity** | Why duration is a straight-line estimate, why real prices curve, and why positive convexity helps you — with a worked +100 bps comparison. |
| 10 | **Rate Shock** | A −100…+100 bps table: price change (duration only, and duration + convexity), new price, gain/loss %, gain/loss in money, and a conclusion box (biggest upside/downside, main risk). |
| 11 | **Yield Curve** | Enter 3m/2y/5y/10y/30y yields → a line chart, your bond's maturity bucket, and a normal / flat / inverted read. |
| 12 | **Valuation Summary** | The whole bond at a glance — identity, price & yield, and risk — each block with a plain-English interpretation. |
| 13 | **Is It Attractive?** | A transparent score out of 10 (yield /3, duration /3, DV01 /2, curve /1, rate-outlook fit /1) → Attractive / Neutral / Not Attractive, with the main reason, the main risk, and an **analyst override**. |
| 14 | **Recommendation** | One page: a manual **Buy / Hold / Avoid** call (you decide) + the attractiveness view + all the key numbers + main positive/risk + your comment. |
| 15 | **Glossary** | A bond dictionary — ~40 beginner terms defined in plain language, alphabetical. |
| 16 | **Formula Explanations** | Every formula the workbook uses, shown as text, with what it does and how to read the answer. |
| 17 | **Quality Check** | 15 independent checks (dirty identity, PV = dirty, reprice = market, Macaulay two ways, duration/DV01/convexity positive, modified ≤ Macaulay, accrued in range, price-yield direction, zero-coupon, date order, frequency, price-vs-par sanity) with Pass / Warning / Fail and a summary. |
| 18 | **Limitations** | What this simple workbook does *not* try to do, the assumptions it makes, and sensible future upgrades. |

---

## How to use it (the 8 steps on Start Here)

1. **Inputs** — enter your bond in the yellow cells.
2. **Cash Flows** — see every payment and its value today.
3. **Price Basics** — clean vs dirty price (what you really pay).
4. **Yield Basics** — your return (yield to maturity).
5. **Price & Yield** — test a yield, get a price; is the bond cheap or expensive?
6. **Duration / DV01 / Convexity** — how risky is it?
7. **Rate Shock / Yield Curve** — the bigger interest-rate picture.
8. **Is It Attractive? / Recommendation** — form your own view.

## Which inputs change the answers

Everything flows from the **Inputs** sheet. The ones that move the numbers most:
the **market clean price** (drives the yield), the **coupon rate** and
**frequency**, the **settlement and maturity dates** (drive years-to-maturity and
therefore duration), the **benchmark yield** (drives the spread and the
price-from-yield test), the **yield-curve** cells on the Yield Curve sheet, and
your **rate outlook** (feeds the attractiveness score). Set **frequency =
Zero-coupon** (or type = Treasury Bill) with a **0% coupon** for a bill.

---

## The attractiveness score (transparent, out of 10)

| Category | Max | How points are earned |
|----------|-----|-----------------------|
| Yield attractiveness | 3 | 3 if YTM ≥ 4.5%, 2 if ≥ 3.5%, 1 if ≥ 2.5%, else 0 |
| Duration risk | 3 | 3 if modified ≤ 3, 2 if ≤ 7, 1 if ≤ 12, else 0 (lower = safer) |
| Price sensitivity (DV01) | 2 | 2 if DV01 ≤ 0.03, 1 if ≤ 0.08, else 0 |
| Yield-curve context | 1 | 1 if the curve is normal/upward, else 0 |
| Rate-outlook fit | 1 | Rise → short duration scores; Fall → long duration scores; Stable → yield ≥ benchmark scores |

**8–10 = Attractive · 5–7 = Neutral · 0–4 = Not Attractive.** The model view is
editable via an analyst override, and the final **Buy / Hold / Avoid** call on the
Recommendation sheet is always your manual decision. The model informs; it does
not decide.

---

## Worked example (the sample bond)

`US Treasury Note 4.000% 15-Feb-2034`, settled 20-Mar-2025, market clean price
96.50, benchmark 4.30%, outlook "Yields Stable":

| Result | Value |
|--------|-------|
| Accrued interest | 0.36 |
| Dirty price | 96.86 |
| Yield to maturity | 4.48% |
| Current yield | 4.15% |
| Spread over benchmark | +18 bps |
| Macaulay duration | 7.52 years |
| Modified duration | 7.36 |
| DV01 (per 100) | 0.071 |
| Convexity | 63.9 |
| Attractiveness | **6 / 10 → Neutral** |

At +100 bps the price falls roughly 7% (softened a little by convexity); at
−100 bps it rises a little more than 7%. The score is Neutral: a fair yield and a
positive spread, offset by intermediate duration risk.

---

## How it is built and verified

- **Live formulas only.** Every figure is an Excel formula referencing named
  ranges defined on the Inputs sheet (and a few compute sheets) — nothing is a
  baked-in value. Change an input and the whole workbook recalculates.
- **Native Excel bond functions** (`YIELD`, `PRICE`, `DURATION`, `MDURATION`,
  `COUPNUM`, `COUPDAYBS`, `YEARFRAC`, …), so the maths matches market convention.
- **Independent Python reference.** `bond/bondmath.py` recomputes the sample bond
  (price↔yield both ways, dirty identity, duration/DV01/convexity) and the tests
  assert the workbook's logic matches it. The attractiveness scoring is also
  re-derived in Python and checked to equal the Excel thresholds.
- **Reference resolver.** A test walks every formula in the built workbook and
  asserts every function and every name resolves (no `#NAME?`), and that the
  Formula Explanations column is text, not live formulas.

```
python tests/test_bondcourse.py      # 13 checks: analytics, structure, wiring, scoring, formulas
```

This is an educational, decision-support tool for a single government bond — not
investment advice.
