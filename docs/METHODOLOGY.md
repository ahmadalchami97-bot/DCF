# Methodology — formula-level reference

This documents the actual calculations the workbook performs. Every formula
below is what is written into the cells (in `=A/B` form, guarded for errors).
Defaults and thresholds referenced here live in `dcf/config.py`.

Notation: `Rev_t` = revenue in period *t*; `last` = most recent reported year;
`N` = forecast horizon (default 5). Ratios are wrapped so that a non-numeric or
zero-denominator input yields `n/m` rather than an Excel error.

---

## Inputs — derived subtotals

Entered as reported (yellow); everything below is a formula on the Inputs sheet.

```
Gross profit      = Revenue − COGS
EBIT              = Gross profit − SG&A − R&D − Other operating
EBITDA            = EBIT + D&A                     (D&A entered once, in cash flow)
Pre-tax income    = EBIT − Interest expense + Interest income + Other non-operating
Net income        = Pre-tax income − Tax − Minority interest
Total assets      = Σ current assets + Σ non-current assets
Total liab. & eq. = Σ liabilities + Total equity + Minority interest
CFO               = Net income + D&A + ΔWorking capital + Other non-cash
CFI               = −Capex − Acquisitions + Other investing
CFF               = Net debt issued − Dividends − Buybacks + Other financing
Net change in cash= CFO + CFI + CFF
EPS               = Net income / shares;  Payout = Dividends / Net income
```

**Convention:** COGS and SG&A include their own depreciation (as reported);
EBITDA adds D&A back once. Capex, dividends, buybacks are entered positive.

---

## Historical analysis

Balance-sheet ratios use **period-end** balances. Selected definitions:

```
Margins:       Gross/EBITDA/EBIT/Net = the respective line ÷ Revenue
Returns:       ROE = NI/Equity;  ROA = NI/Assets
               ROIC = NOPAT / Invested capital
               NOPAT = EBIT × (1 − effective tax),  effective tax = Tax/EBT
               Invested capital = Equity + Minority + Debt − Cash − ST investments
               ROCE = EBIT / (Assets − Current liabilities)
Liquidity:     Current = CA/CL;  Quick = (CA−Inventory)/CL;  Cash = (Cash+STI)/CL
Leverage:      Net debt = Debt − Cash − ST investments
               D/E = Debt/Equity;  Net debt/EBITDA;  Coverage = EBIT/Interest
Efficiency:    DSO = AR/Rev×365;  DIO = Inv/COGS×365;  DPO = AP/COGS×365
               CCC = DSO + DIO − DPO;  turnovers = flow ÷ stock
Cash flow:     FCF = CFO − Capex;  FCF margin = FCF/Rev;  conversion = FCF/NI
```

### Interpretation labels

Centralised rules (`dcf/config.py → Thresholds`, builders in `utils.py`):

* **Trend** (margins, returns trends): compare the latest value with its trailing
  average; beyond ±`TREND_BAND` (5%) → Improving/Expanding or
  Deteriorating/Compressing, else Stable. Cost ratios invert the sense.
* **Growth**: latest growth vs prior-period growth, ±`GROWTH_ACCEL_PP` (2pp) →
  Accelerating / Stable / Decelerating.
* **Bands** (leverage, liquidity, returns): a threshold ladder, e.g. Net
  debt/EBITDA < 1.0 Conservative, < 2.5 Moderate, < 4.0 Elevated, else Stretched.

Labels are coloured green/amber/red by conditional formatting using a
sentiment-consistent vocabulary, so they update live.

---

## WACC

```
Cost of equity   Ke = Rf + β × ERP                         (CAPM)
After-tax debt   Kd(1−t) = Kd_pretax × (1 − tax)
Equity value E   = market cap if available, else book equity   (flagged)
Debt value D     = total interest-bearing debt (book proxy)
Weights          We = E/(E+D);  Wd = D/(E+D)
WACC             = We × Ke + Wd × Kd(1−t)
```

Each market input resolves as `=IF(ISNUMBER(input), input, default)` and is
tagged *input* or *fallback*. Defaults: Rf 4%, ERP 5%, β 1.0, Kd 6%, tax 25%.

---

## Assumption engine

```
Hist. revenue CAGR = (Rev_last / Rev_first)^(1/years) − 1
Blended start grwth= avg(CAGR, latest-year growth)         (fallback: long-run 3%)
Start growth (Base)= clamp(blend, −5%, +20%)
Terminal growth g  = min(2.5%, WACC − 1%)                  (kept below WACC)
Terminal margin    = trailing 3y avg EBIT margin           (fallback 12%)
D&A / capex / NWC %= trailing 3y historical intensities    (fallbacks 5/5/10%)
```

Scenario tilts (applied to Base, then clamped):

| Lever | Bull | Bear | Downside |
|---|---|---|---|
| Start growth | +3pp | −3pp | −6pp |
| Terminal growth | +0.5pp | −0.5pp | −1.0pp |
| Terminal margin | +2pp | −2pp | −5pp |

A selector cell (1–4) picks the active set via `CHOOSE()`; the Forecast/DCF read
the *active* values, so the whole model re-prices from one cell.

---

## Forecast (active scenario)

```
Growth path:   g_t = start + (g_terminal − start) × (t−1)/(N−1)     [linear fade]
Revenue:       Rev_t = Rev_{t−1} × (1 + g_t),  Rev_0 = last actual
Margin path:   m_t = m_last + (m_target − m_last) × t/N             [linear fade]
EBIT_t = Rev_t × m_t;   D&A_t = Rev_t × da%;   EBITDA_t = EBIT_t + D&A_t
NOPAT_t = EBIT_t × (1 − tax)
Capex_t = Rev_t × capex%
ΔNWC_t  = nwc% × (Rev_t − Rev_{t−1})
Unlevered FCF (FCFF_t) = NOPAT_t + D&A_t − Capex_t − ΔNWC_t
```

The forecast is driver-based: costs, capex, D&A and working capital all scale
with revenue rather than being flat assumptions. If unit volume × price are
entered on Inputs, a bottom-up revenue override can be used instead.

---

## DCF

```
Discount factor   DF_t = 1 / (1 + WACC)^t                  [end-of-year]
PV of FCFF        = Σ_t FCFF_t × DF_t
Terminal value    TV_N = FCFF_N × (1 + g) / (WACC − g)     [Gordon perpetuity]
PV of TV          = TV_N × DF_N
Enterprise value  EV = Σ PV(FCFF) + PV(TV)
Equity value      = EV − Net debt − Minority interest
Value per share   = Equity value / shares outstanding
Upside            = Value per share / current price − 1
```

Cross-checks: exit-multiple TV (`EBITDA_N × multiple`); TV as % of EV (warn
> 80%); implied exit multiple (`TV_perp / EBITDA_N`); EV / next-year EBITDA. The
`(WACC − g)` denominator is `IFERROR`-guarded and `g` is clamped below WACC.

---

## Sensitivity

* **WACC × g** and **WACC × exit multiple** — each cell re-discounts the *same*
  forecast FCFFs at the row/column rates (exact; the centre cell equals the
  headline value).
* **Start growth × terminal margin** — a clearly-labelled closed-form
  constant-growth two-stage value, because these levers move the cash flows
  themselves.

A 3-colour scale renders the gradient; the base case is boxed.

---

## Scenario

Each scenario rebuilds the full staged-fade forecast from its own
growth/margin/terminal-growth assumptions, then discounts at WACC and bridges to
value per share. The Base column reproduces the headline DCF exactly.

---

## Checks (16 diagnostics)

Balance-sheet balance, cash-flow articulation, IS-vs-CF net income, sign sanity,
key-input presence, currency/units present, WACC range, WACC > g, terminal-growth
bounds, TV concentration, positive EV/equity, gross-margin bounds, positive
revenue, growth outliers, non-negative forecast FCF, and acyclicity. Each yields
PASS / REVIEW / FAIL; the top verdict counts the flags.

---

## Conclusion

A formula-driven thesis: the stance combines the valuation read (upside vs
±15% band) with quality (ROIC vs WACC); value drivers and risks read live from
the historical labels and DCF cross-checks; the swing-assumption table links the
active WACC, g, margin and growth; upside/downside link the Bull/Downside
scenarios.
