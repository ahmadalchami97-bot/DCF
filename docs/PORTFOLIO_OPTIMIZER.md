# Portfolio Allocation Optimizer + Scenario Analysis

A clean, professional, **explainable** Excel tool — *not* a black-box quant model.
It helps a non-quant investor understand four things, with every number a short,
visible formula you can follow and audit:

1. **Current allocation** — what you hold today.
2. **Scenario impact** — what a market scenario (e.g. *"Since Fed Rate Decision"*)
   did to each asset and to the whole portfolio, in your base currency.
3. **Risk / return** — the trade-off across allocation choices.
4. **Rebalancing actions** — what to buy, sell or hold, and *why*.

```
pip install -r requirements.txt
python build_portfolio.py                       # -> examples/Portfolio Allocation Optimizer.xlsx
python build_portfolio.py --blank -o "examples/Portfolio Allocation Optimizer (blank).xlsx"
```

Open in Excel/LibreOffice and start on the **Overview** sheet. Every sheet has an
amber *"How to read this sheet"* box; the **Formula Guide** explains every
calculation in plain language.

No Solver, no macros, no VBA. The only matrix-free risk calculation (portfolio
volatility) is built transparently from a visible covariance table.

---

## Asset universe

**Investable assets:** SMI, S&P 500, SXI Real Estate Funds Broad Index, Gold,
US Government Bonds.

**Market indicators (drivers / context only):** DXY, CHF/USD, USD/KWD, CHF/KWD.
These are shown to explain *why* things moved; they are **never** treated as
holdings unless you set their *Investable?* flag to *Yes*.

The worked example is a **KWD-based** investor holding Swiss and US assets.

---

## The eight sheets

| # | Sheet | What it does |
|---|-------|--------------|
| 1 | **Overview** | What the tool does, the order to use the sheets, the asset universe, the legend and the model-based disclaimer. |
| 2 | **Scenario Inputs** | The one place you type: scenario dates, each asset's start/end price and FX rate, amounts invested, target/min/max weights, the market indicators, and a small **bond return calculator**. |
| 3 | **Scenario Output** | Per-asset local return, FX effect, currency-adjusted return, market values, weight and contribution to the portfolio return. |
| 4 | **Risk & Return** | Long-term expected return and volatility per asset, the correlation matrix and the computed covariance matrix — the inputs behind the recommendation. |
| 5 | **Allocation** | Six allocations compared, and the scenario-stressed recommendation built step by step; pick which allocation to rebalance toward. |
| 6 | **Rebalancing** | Buy/Sell/Hold actions with target values and a plain-English reason for each. |
| 7 | **Dashboard** | Allocation pies, current-vs-recommended and scenario bars, a risk/return map, and a summary of what happened. |
| 8 | **Formula Guide** | Every formula in the workbook, explained simply. |

---

## The core formulas (all shown in the workbook)

```
Asset return (local)      = End price / Start price - 1
FX return                 = End FX rate / Start FX rate - 1
Currency-adjusted return  = (1 + Asset return) x (1 + FX return) - 1
Contribution              = Weight x Currency-adjusted return
Portfolio return          = Sum of all contributions
Bond return               = (End price - Start price + Coupon earned) / Start price
                            Coupon earned = Face x Coupon rate x (Holding days / 365)
```

`FX rate` means the value of 1 unit of the asset's currency in your base currency
(KWD in the example): USD assets use USD/KWD, CHF assets use CHF/KWD. The bond
calculator's *Total return* feeds the US Government Bonds local return.

---

## The six allocations compared

| Allocation | How its weights are set (simple, visible rules) |
|---|---|
| **Current** | Your amounts invested ÷ total. |
| **Equal-weight** | 1 / N for every asset. |
| **Custom target** | The target weights you type (re-based to 100%). |
| **Max-Sharpe\*** | More weight to the best long-run return per unit of risk: `score = max(0, expected − risk-free) / volatility²`. |
| **Min-volatility\*** | More weight to the calmer assets: `1 / volatility²`. |
| **Scenario-stressed** | The Max-Sharpe mix, tilted **modestly** toward scenario winners (the tilt is capped), then clamped to your min/max limits. |

\* Simplified, transparent rules — **not** a Solver optimisation. Correlation
still matters: each allocation's **volatility** is computed from the full
covariance table, so the risk figures (and the risk/return map) reflect
diversification.

**Scenario-stressed, step by step** (Allocation sheet, Step 2): start from the
Max-Sharpe weights → apply the capped scenario tilt → re-base to 100% → fit to
your min/max → re-total → fit again so it settles. A *Within limits?* check flags
any asset still near a limit.

> **The recommended allocation is model-based and should be used as a
> decision-support tool, not as a guaranteed perfect portfolio.**

---

## Rebalancing

For each asset: current value and weight, recommended weight and value, the
buy/sell amount (`Target value − Current value`), a Buy / Sell / Hold action, and
a plain-English reason — e.g. *"Reduce Gold because its weight is above target and
scenario-adjusted risk is high"* or *"Increase US Bonds because it is a calmer
asset that lowers portfolio volatility."* Gaps within 1% are left as **Hold** so
you don't trade on noise; the trades net to ~0 (a rebalance moves money between
assets, it doesn't add or remove cash).

---

## Verification

```
python tests/test_portfolio.py     # 11/11 passing
```

The suite evaluates every formula (no Excel needed) and asserts: no errors and no
circular references; the currency-adjusted and bond formulas are correct; the
portfolio return ties (sum of contributions = end value / start value − 1); every
allocation sums to 100%; the min-volatility mix really is the lowest-risk one; the
scenario-stressed recommendation respects your min/max limits; rebalancing trades
net to zero; the indicators are never treated as holdings; and the blank template
degrades gracefully.

---

## Design choices & limitations

* **Simple by design.** Allocation weights use transparent rules (inverse-variance,
  return-per-risk, a capped scenario tilt), not a Solver — so you can audit every
  weight. The scenario tilt is deliberately capped to avoid chasing short-term
  returns.
* **Correlation enters through risk.** The simplified Max-Sharpe / Min-vol *weights*
  use each asset's own risk and return; correlation is reflected in the **portfolio
  volatility** and the risk/return map, computed from the covariance table.
* **Other limits.** Two fitting rounds bring the scenario weights within ~0.3% of
  your min/max while still totalling 100%; the *Within limits?* column flags any
  residual. Adjust your limits if they are too tight.
* This is an analytical tool to support judgement, **not investment advice**.
