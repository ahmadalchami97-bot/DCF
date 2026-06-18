"""
WACC build-up sheet.

Derives the discount rate step by step -- nothing is hidden in a single opaque
formula. Cost of equity is built via CAPM (Rf + beta x ERP); cost of debt is the
pre-tax rate taxed down; capital weights use market value of equity (falling back
to book equity, clearly flagged) and book debt as a proxy for market value.

Every market input resolves through an explicit fallback: ``=IF(ISNUMBER(input),
input, default)`` with a "input / fallback" tag, so a model with no market data
still produces a sensible, clearly-labelled WACC.
"""

from __future__ import annotations

from ..config import Defaults, Fmt
from . import common

L, V, S, N = 1, 2, 3, 4  # label, value, source, note columns


def build(sh, ctx: common.Context):
    refs = ctx.refs
    last = ctx.n_hist - 1
    M = lambda k: refs.ref(f"mkt.{k}")                  # noqa: E731 market input ref
    R = lambda k, p: refs.ref(f"in.{k}@{p}")            # noqa: E731
    H = lambda k, p: refs.ref(f"h.{k}@{p}")             # noqa: E731

    sh.hide_gridlines()
    sh.col_width(L, 40)
    sh.col_width(V, 15)
    sh.col_width(S, 16)
    sh.col_width(N, 56)
    r = common.title_block(sh, "WACC", "Weighted average cost of capital — built up step by step",
                           last_col=N)
    r += 1

    def driver(row, label, key, ref, default, fmt=Fmt.PCT, note=""):
        """Resolve an input-or-fallback row and register it."""
        resolved = f"=IF(ISNUMBER({ref}),{ref},{default})"
        sh.put(row, L, label, role="label")
        sh.put(row, V, resolved, role="link", fmt=fmt, key=f"wacc.{key}")
        sh.put(row, S, f'=IF(ISNUMBER({ref}),"input","fallback")', role="neutral", align="c")
        sh.put(row, N, note, role="note")
        return row + 1

    def calc(row, label, formula, key, fmt=Fmt.PCT, note="", bold=False, role="calc"):
        sh.put(row, L, label, role="label_b" if bold else "label")
        sh.put(row, V, formula, role=role, fmt=fmt, key=f"wacc.{key}", bold=bold or None)
        sh.put(row, S, "computed", role="neutral", align="c")
        sh.put(row, N, note, role="note")
        return row + 1

    # ---- Cost of equity (CAPM) -------------------------------------------
    r = common.section(sh, r, "1 · Cost of Equity — CAPM", c1=1, c2=N)
    r = driver(r, "Risk-free rate (Rf)", "rf", M("mkt_risk_free"), Defaults.RISK_FREE,
               note="Long-dated government bond yield in the reporting currency.")
    r = driver(r, "Equity risk premium (ERP)", "erp", M("mkt_erp"), Defaults.EQUITY_RISK_PREMIUM,
               note="Expected return of equities over the risk-free rate.")
    r = driver(r, "Beta (β)", "beta", M("mkt_beta"), Defaults.BETA, fmt=Fmt.FLOAT2,
               note="Levered equity beta vs the market; fallback 1.00 (market risk).")
    r = calc(r, "Cost of equity  Ke = Rf + β × ERP",
             f"={refs.ref('wacc.rf')}+{refs.ref('wacc.beta')}*{refs.ref('wacc.erp')}",
             "ke", bold=True, note="CAPM. Ke is the return equity holders require.")
    r += 1

    # ---- Cost of debt ----------------------------------------------------
    r = common.section(sh, r, "2 · Cost of Debt", c1=1, c2=N)
    r = driver(r, "Pre-tax cost of debt (Kd)", "kd_pre", M("mkt_pretax_kd"),
               Defaults.PRETAX_COST_OF_DEBT,
               note="Marginal borrowing rate. Cross-check vs implied rate below.")
    r = driver(r, "Marginal tax rate (t)", "tax", M("mkt_tax_rate"), Defaults.TAX_RATE,
               note="Used to tax-shield debt and for NOPAT in the DCF.")
    r = calc(r, "After-tax cost of debt  Kd × (1 − t)",
             f"={refs.ref('wacc.kd_pre')}*(1-{refs.ref('wacc.tax')})",
             "kd_at", bold=True, note="Interest is tax-deductible, lowering its effective cost.")
    # implied (effective) cost of debt cross-check
    implied = (f'=IFERROR({R("interest_expense", last)}/{H("_total_debt", last)},"n/a")')
    r = calc(r, "    Implied rate cross-check (int. exp / debt)", implied, "kd_implied",
             role="calc", note="Sanity check on the assumed pre-tax cost of debt.")
    r += 1

    # ---- Capital structure ----------------------------------------------
    r = common.section(sh, r, "3 · Capital Structure (market weights)", c1=1, c2=N)
    eq_val = (f'=IF(ISNUMBER({M("market_cap")}),{M("market_cap")},{R("total_equity", last)})')
    r = calc(r, "Equity value (E)", eq_val, "E", fmt=Fmt.MONEY,
             note="Market capitalisation; falls back to book equity if price/shares missing.")
    sh.put(r - 1, S, f'=IF(ISNUMBER({M("market_cap")}),"market","book (fallback)")',
           role="neutral", align="c")
    r = calc(r, "Debt value (D)", f"={H('_total_debt', last)}", "D", fmt=Fmt.MONEY,
             note="Total interest-bearing debt (book value as a proxy for market value).")
    sh.put(r - 1, S, "book", role="neutral", align="c")
    r = calc(r, "Equity weight  We = E / (E + D)",
             f"=IFERROR({refs.ref('wacc.E')}/({refs.ref('wacc.E')}+{refs.ref('wacc.D')}),1)",
             "we", note="Share of capital funded by equity.")
    r = calc(r, "Debt weight  Wd = D / (E + D)",
             f"=IFERROR({refs.ref('wacc.D')}/({refs.ref('wacc.E')}+{refs.ref('wacc.D')}),0)",
             "wd", note="Share of capital funded by debt.")
    r += 1

    # ---- WACC ------------------------------------------------------------
    r = common.section(sh, r, "4 · Weighted Average Cost of Capital", c1=1, c2=N)
    wacc_formula = (f"={refs.ref('wacc.we')}*{refs.ref('wacc.ke')}"
                    f"+{refs.ref('wacc.wd')}*{refs.ref('wacc.kd_at')}")
    sh.put(r, L, "WACC = We × Ke + Wd × Kd(1−t)", role="label_b")
    sh.put(r, V, wacc_formula, role="result", fmt=Fmt.PCT2, key="wacc.value")
    sh.put(r, N, "The blended required return used to discount the forecast cash flows.",
           role="note")
    r += 1
    # sanity read
    wv = refs.ref("wacc.value")
    sane = (f'=IF(AND({wv}>={Defaults.RISK_FREE-0.005},{wv}>=0.04,{wv}<=0.18),'
            f'"Within a reasonable range","Outside typical 4–18% range — review inputs")')
    sh.put(r, L, "Plausibility", role="label")
    sh.put(r, V, "", role="calc")
    sh.put(r, N, sane, role="note")
    common.add_label_coloring(sh, f"{sh.coord(r, N)}:{sh.coord(r, N)}", sh.coord(r, N))
    r += 2

    sh.put(r, L, "How to read this", role="label_b")
    r += 1
    for line in _NOTES:
        sh.put(r, L, "•  " + line, role="note")
        sh.merge(r, L, r, N)
        sh.row_height(r, 14)
        r += 1
    return sh


_NOTES = [
    "WACC rises with beta, the equity risk premium and leverage cost, and falls "
    "with the tax shield on debt. It is the single most important valuation input.",
    "If you have no market data, the fallback defaults give a defensible starting "
    "point; replace them with company-specific figures for a real valuation.",
    "Equity value uses market cap where available — the market's own view of equity "
    "— rather than book value, which can be stale.",
]
