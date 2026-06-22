# Institutional Forecasting Engine

A world-class, **fully-formula-driven, auditable** integrated forecasting workbook
(10 years history + 10 years forecast) built for equity research, asset
management and PE/IB use. Produces a complete three-statement forecast that feeds
directly into DCF, relative valuation and investment recommendations.

```
pip install -r requirements.txt
python build_ife.py                       # -> examples/Institutional Forecasting Engine.xlsx
python build_ife.py --blank -o template.xlsx
```

Open in Excel/LibreOffice and start on the **Dashboard**.

---

## What makes it institutional-grade

* **A fully integrated 3-statement model that reconciles WITHOUT a plug.** Cash is
  the natural residual of a *comprehensive* cash-flow statement (which captures the
  change in every non-cash balance-sheet line); equity rolls forward by
  NI − dividends; debt rolls forward by new debt − repayment. Because every line
  is wired into the cash flow, **Assets = Liabilities + Equity holds identically in
  every forecast year** (the balance check is exactly 0). Verified on every test run.
* **No circular references.** Interest is charged on *beginning* balances, so the
  classic interest⇄debt⇄cash loop never forms. No iterative calc, no macros, no VBA.
* **A real Method × Scenario engine** driven by **named ranges** (`Method`,
  `Scenario`) and dropdowns. Change either cell and the whole model re-prices:
  * *Historical Trend* — every driver uses its 5-year historical average.
  * *Manual* — every driver uses the analyst's scenario target.
  * *Hybrid* — fades from the historical average to the target over the horizon
    (so margins converge rather than expanding forever).
* **Simplicity & auditability first.** Short formulas, helper rows, no nested-IF
  spaghetti; a junior analyst can trace any forecast number back to a driver.
* **A Forecast Bridge** that explains *why* revenue, EBITDA and net income change
  each year (growth, margin, D&A, financing and tax effects), each block proven to
  sum back to the actual change.

Colour code: **blue = input · black = formula · green = key output · gray =
headers · red = error/warning.**

---

## The ten sheets

| # | Sheet | Contents |
|---|-------|----------|
| 1 | **Dashboard** | Company overview, headline 10-year CAGRs (revenue/EBITDA/EBIT/NI/FCF), forecast-quality indicators (balance integrity, health score, scenario/method) and auto-updating trend & margin charts. |
| 2 | **Historical** | 10 years of statements: blue inputs, black subtotals, reusable helper rows; a balance-check row confirms the entered statements tie. |
| 3 | **Analysis** | Growth, profitability, returns, efficiency, liquidity, leverage, the driver ratios, common-size and an indexed trend. |
| 4 | **Assumptions** | The control centre: 3/5/10-year historical averages, manual Bear/Base/Bull targets, the Method × Scenario selectors, and the resolved per-year active drivers. |
| 5 | **Forecast** | The integrated 10-year three-statement model with explicit equity and debt roll-forwards and a balance check. |
| 6 | **Bridge** | YoY effect decomposition for revenue, EBITDA and net income, each with a tie-out check. |
| 7 | **Diagnostics** | Accounting-integrity + reasonableness checks (growth, margins, cash, equity, debt, working capital, capex, tax) with PASS/WARN/FAIL and a 0–100 Forecast Health Score. |
| 8 | **Scenario** | Bear/Base/Bull run through the full driver logic via a compact engine; a professional comparison of CAGRs, margins, ROE, ROIC and Debt/EBITDA. The Base column reconciles with the Forecast sheet. |
| 9 | **Sensitivity** | Two-way live-formula grids: growth × margin (→ EBITDA, NI, FCF), growth × tax (→ NI), growth × capex (→ FCF), heat-mapped. |
| 10 | **Notes** | Structured space for the investment thesis, risks, forecast rationale, management commentary and earnings-review notes. |

---

## How the integrated model articulates (the no-plug proof)

For each forecast year *t* (interest on beginning balances → no circularity):

```
Revenue_t   = Revenue_{t-1} × (1 + growth_t)
EBITDA_t    = Revenue_t × EBITDA-margin_t ;  Gross/COGS/Opex/D&A/EBIT derived
Interest_t  = rate_t × Debt_{t-1}          (beginning balance)
NI_t        = (EBIT_t − net interest_t) × (1 − tax_t)
Working capital from DSO/DIO/DPO; Capex = capex% × revenue; PP&E rolls (capex − D&A)
CFO = NI + D&A − ΔWC ;  CFI = −Capex − ΔOther assets ;  CFF = ΔDebt − Dividends
Cash_t   = Cash_{t-1} + CFO + CFI + CFF        (no revolver plug)
Equity_t = Equity_{t-1} + NI_t − Dividends_t   (roll-forward)
Debt_t   = Debt_{t-1} + New debt_t − Repayment_t (roll-forward)
```

Since every non-cash balance-sheet movement is reflected in the cash flow,
ΔAssets ≡ ΔLiabilities + ΔEquity, so the sheet balances every year — the
"Balance check" row is identically 0. There is no balancing plug and no circular
reference; a negative cash balance (if drivers demand it) surfaces as a
**Diagnostics warning** rather than being papered over by a revolver.

---

## The Forecast Bridge

```
Revenue ΔYoY  = growth effect
EBITDA  ΔYoY  = revenue (volume) effect + margin effect
Net inc ΔYoY  = EBITDA effect + D&A effect + financing effect + tax-rate effect
```

Each block carries a check row (sum of effects − actual change = 0), proven on
every test run.

---

## Verification

```
python tests/test_ife.py        # 10/10 passing
```

The suite evaluates all ~2,900 formulas (no Excel needed) and asserts: no errors
and **no circular references**; the historical and forecast balance sheets
balance to the cent; revenue compounds off the active growth driver; the bridge
ties; the Scenario "Base" column reconciles with the main Forecast; scenario
ordering is monotonic; switching the Scenario named range re-prices the model;
the health score is 100 on the worked example; and the blank template degrades
gracefully (no errors; Diagnostics flags the missing data).

---

## Design choices & limitations

* **Beginning-balance interest** is used deliberately to keep the model
  circularity-free (an institutional norm); switch to average balances only if you
  are prepared to enable iterative calculation.
* **Intangibles are held flat** and **short-term debt is held at the last actual**
  in the forecast (long-term debt carries the roll-forward); adjust on the
  Assumptions/Forecast sheets if your company differs.
* **Navigation uses hyperlinks** (no VBA), keeping the file a portable, macro-free
  `.xlsx`. Cell-protection attributes are set per role; enable *Review → Protect
  Sheet* to lock the formulas.
* The **Scenario** sheet uses a compact engine that mirrors the main model; the
  **Sensitivity** grids use a transparent constant-growth terminal model (both
  clearly labelled). The **Forecast** sheet is always the full model.
* This is an analytical tool to support judgement, not investment advice.
