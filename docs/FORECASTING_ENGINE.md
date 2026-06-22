# Institutional Forecasting Engine

A **transparent, fully-formula-driven, auditable** integrated three-statement
forecasting workbook. It was rebuilt from first principles around one rule:

> **Transparency, clarity, auditability and usability come before sophistication,
> automation and flexibility. If a forecast number must be traced through several
> layers — or a formula needs a paragraph to explain — the design is reconsidered.**

```
pip install -r requirements.txt
python build_ife.py                       # -> examples/Institutional Forecasting Engine.xlsx
python build_ife.py --blank -o "examples/Institutional Forecasting Engine (blank).xlsx"
```

Open in Excel/LibreOffice and start on the **Dashboard**; read the **Methodology**
sheet once and the whole model is self-explaining.

---

## What makes it institutional-grade

* **Historical = input, forecast = output — never mixed.** Every figure on the
  Historical sheet (including the subtotals: gross profit, EBITDA, EBIT, net
  income, total assets, total liabilities) is a hard-coded **blue input** pasted
  from the filings. Every figure on the Forecast sheet is a **formula**. The two
  are shaded differently (blue *Actual* headers vs green *Forecast* headers) so
  they can never be confused.
* **The forecast begins after the last reported year — automatically.** The model
  counts the reported years and derives `LastActual`; the forecast starts the next
  year. **Paste in another year of actuals and the whole forecast shifts forward
  on its own** — `FY2025 → FY2026` actuals moves the forecast from `FY2026…` to
  `FY2027…` with no other edits and no overlap.
* **One driver per line.** Each forecast cell is a single short formula naming the
  one assumption it uses. No scenario selector, no method engine, no resolved-
  driver layer — the assumption→output link is a single visible hop.
* **It reconciles WITHOUT a plug and WITHOUT circularity.** Cash is the residual
  of a complete cash-flow statement; equity and debt roll forward; net interest is
  charged on the **opening** net-debt balance. Because every balance-sheet move
  flows through the cash flow, **Assets = Liabilities + Equity to the cent every
  year** (the balance check is exactly 0). No iterative calc, no macros, no VBA.
* **A real audit trail.** The Historical sheet carries balance / asset-build /
  liability-build checks; the Diagnostics sheet runs accounting-integrity and
  reasonableness checks with PASS/WARN/FAIL and a 0–100 Health Score; the Bridge
  explains every change and ties exactly.

Colour code: **blue = input · black = formula · green = key output · red = warning.**

---

## The seven sheets

| # | Sheet | Contents |
|---|-------|----------|
| 1 | **Dashboard** | Company overview, the dynamic forecast window, forecast-quality indicators (Health Score, balance integrity) and headline forecast-horizon CAGRs with auto-updating trend & margin charts. |
| 2 | **Methodology** | Plain-English account of the whole model: philosophy, the dynamic timeline, the one-driver-per-line rule (every forecast formula written out in words), why it balances, how to update. |
| 3 | **Historical** | The ACTUAL layer — every figure a hard-coded input. An auto-detected timeline panel, an *Actual / spare* status row, and audit checks that confirm the pasted statements tie. |
| 4 | **Assumptions** | The drivers — one editable input per line, per forecast year, pre-filled with a base case. A "Drives" column states the exact formula each one feeds. |
| 5 | **Forecast** | The integrated three-statement model: base column pulled from the last actual via `INDEX`, then one-driver formulas per line, with a balance check. |
| 6 | **Bridge** | Exact year-over-year decomposition of revenue, EBITDA, EBIT and net income; each block ties to the actual change. |
| 7 | **Diagnostics** | Accounting integrity + reasonableness checks (growth, margins, cash, equity, debt, working capital, capex, tax) with PASS/WARN/FAIL and the Forecast Health Score. |

---

## The dynamic timeline (how the forecast start is detected)

On the Historical sheet:

```
FirstYear   = an input (e.g. 2015)                      ← the only place the start is set
count       = COUNT(revenue row across all slots)       ← how many years you have pasted
LastActual  = FirstYear + count − 1                      ← auto-detected (a named range)
Forecast    begins at LastActual + 1
```

The Forecast sheet's base column is `=INDEX(Historical!<line>, count)` — the
*count-th* (i.e. last) reported value of each line — and its year headers are
`=LastActual + 1, +2, …`. So when you paste a new column of actuals, `count` rises
by one, `LastActual` advances, the base column locks onto the new last year, and
every forecast label and formula moves forward automatically. The historical grid
ships with spare columns so there is always room to add years; empty spares are
shaded grey and tagged *“- spare -”*.

This small amount of cleverness is **isolated to the timeline layer and fully
documented on the Methodology sheet**; the forecast formulas you read every day
stay trivial.

---

## How the integrated model articulates (the no-plug proof)

For each forecast year *t* (net interest on the opening net-debt balance → no
circularity):

```
Revenue_t      = Revenue_{t-1} × (1 + growth_t)
EBITDA_t       = Revenue_t × EBITDA-margin_t
D&A_t          = Revenue_t × D&A%_t ;  EBIT_t = EBITDA_t − D&A_t
Net interest_t = net-interest-rate_t × Net debt_{t-1}      (opening balance)
Net income_t   = (EBIT_t − net interest_t) × (1 − tax_t)
NWC_t          = Revenue_t × NWC%_t
Net PP&E_t     = Net PP&E_{t-1} + Capex_t − D&A_t ;  Capex_t = Revenue_t × capex%_t
Debt_t         = Debt_{t-1} + net new debt_t
Equity_t       = Equity_{t-1} + Net income_t − Dividends_t ;  Dividends_t = payout_t × max(0, NI_t)
CFO = NI + D&A − ΔNWC ;  CFI = −Capex ;  CFF = net new debt − Dividends
Cash_t         = Cash_{t-1} + CFO + CFI + CFF              (the residual — no revolver plug)
```

`ΔAssets = ΔCash + ΔNWC + ΔNet PP&E = (NI + ΔDebt − Div) = ΔLiabilities + ΔEquity`,
so the sheet balances every year — the **Balance check** row is identically 0. A
negative cash balance (if drivers demand it) surfaces as a **Diagnostics
warning** rather than being papered over by a plug. Other assets and other
liabilities are **held flat** at the last actual (adjust on the Forecast sheet if
material).

---

## The Forecast Bridge

```
Revenue ΔYoY  = growth effect
EBITDA  ΔYoY  = revenue (volume) effect + margin effect
EBIT    ΔYoY  = revenue (volume) effect + EBITDA-margin effect + D&A effect
Net inc ΔYoY  = EBITDA effect + D&A effect + financing (net interest) effect + tax-rate effect
```

Each block carries a check row (sum of effects − actual change). The
decompositions are **exact, not approximate**, so every check is 0.

---

## Verification

```
python tests/test_ife.py        # 10/10 passing
```

The suite evaluates every formula (no Excel needed) and asserts: no errors and
**no circular references**; the pasted actuals tie (balance / asset-build /
liability-build checks are 0); the forecast balance sheet balances to the cent
every year **without a plug**; revenue compounds off its growth driver; net
interest uses the opening net-debt balance; the bridge ties; the timeline is
auto-detected; **adding a year of actuals shifts the forecast start forward**; the
Health Score is 100 on the worked example; and the blank template degrades
gracefully (no errors; Diagnostics flags the missing data).

---

## Design choices & limitations

* **Opening-balance net interest** keeps the model circularity-free (an
  institutional norm); switch to average balances only if you enable iterative
  calculation.
* **Other assets / other liabilities are held flat**; net working capital is a
  single line driven by NWC % of revenue (rather than separate DSO/DIO/DPO) — a
  deliberate simplification in favour of auditability.
* **Navigation uses hyperlinks** (no VBA), keeping the file a portable, macro-free
  `.xlsx`. Cell-protection attributes are set per role; enable *Review → Protect
  Sheet* to lock the formulas.
* This is an analytical tool to support judgement, not investment advice.
