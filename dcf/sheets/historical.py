"""
Historical Analysis sheet.

Computes growth, margin, return, liquidity, leverage, efficiency, cash-flow and
capital-return metrics for every reported period, each as a live formula linked
to the Inputs sheet, and attaches a plain-English interpretation label (coloured
green / amber / red by conditional formatting) for the latest period.

All metrics are also registered under ``h.<key>@<period>`` so the Assumptions and
Forecast layers can build driver-based defaults from the company's own history.

Convention: balance-sheet denominators use period-END balances (noted on the
sheet) so every period is computable without a prior-year stub. ROIC uses the
company's EFFECTIVE tax rate, keeping the historical section self-contained.
"""

from __future__ import annotations

from collections import namedtuple

from ..config import Fmt, Thresholds as T
from ..utils import growth, label_bands, label_growth, label_trend, ratio
from . import common

LABEL_COL = 1
FDC = 2  # first data column

Spec = namedtuple("Spec", "key label fmt fn kind arg indent start", defaults=("", 0, 0))


def _guard(expr_true, *needed):
    """Wrap a numeric expression so it degrades to "n/m" unless all refs are numbers."""
    conds = ",".join(f"ISNUMBER({x})" for x in needed)
    return f'=IF(AND({conds}),{expr_true},"n/m")'


def build(sh, ctx: common.Context):
    n = ctx.n_hist
    last = FDC + n - 1
    note_col = FDC + n
    R = lambda k, p: ctx.refs.ref(f"in.{k}@{p}")          # noqa: E731 input ref
    H = lambda k, p: ctx.refs.ref(f"h.{k}@{p}")           # noqa: E731 historical ref

    common.setup_grid(sh, n_data_cols=n, note_col=note_col)
    r = common.title_block(sh, "HISTORICAL ANALYSIS",
                           "Ratios, margins, growth, returns & cash flow — with plain-English read",
                           last_col=note_col)
    sh.put(r, 1, common.money_units_note(ctx) +
           "  Balance-sheet ratios use period-end balances.", role="note")
    sh.merge(r, 1, r, note_col)
    r += 2

    label_anchor_rows = []  # rows carrying an interpretation label (for coloring)

    def header(row, text):
        common.section(sh, row, text, c1=1, c2=note_col)
        common.period_headers(sh, row + 1, label_col=LABEL_COL, first_data_col=FDC,
                              labels=ctx.periods, note_col=note_col,
                              note_text="Latest read")
        return row + 2

    def render(row, specs):
        for sp in specs:
            indent = "    " * sp.indent
            role = "label" if sp.indent else "label_b"
            is_helper = sp.key.startswith("_")
            sh.put(row, 1, indent + sp.label, role="sublabel" if is_helper else role)
            for p in range(n):
                if p < sp.start:
                    continue
                formula = sp.fn(R, H, p)
                if formula is None:
                    continue
                sh.put(row, FDC + p, formula, role="link", fmt=sp.fmt,
                       key=f"h.{sp.key}@{p}")
            if sp.kind != "none":
                lab = _label_formula(sh, row, sp, last)
                if lab:
                    sh.put(row, note_col, lab, role="note_c", key=f"h.lbl.{sp.key}")
                    label_anchor_rows.append(row)
            row += 1
        return row

    # ---- Growth ----------------------------------------------------------
    r = header(r, "Growth (year-on-year)")
    r = render(r, [
        Spec("rev_growth", "Revenue growth", Fmt.PCT,
             lambda R, H, p: growth(R("revenue", p), R("revenue", p - 1)), "growth", start=1),
        Spec("gross_growth", "Gross profit growth", Fmt.PCT,
             lambda R, H, p: growth(R("gross_profit", p), R("gross_profit", p - 1)), "growth", start=1),
        Spec("ebitda_growth", "EBITDA growth", Fmt.PCT,
             lambda R, H, p: growth(R("ebitda", p), R("ebitda", p - 1)), "growth", start=1),
        Spec("ebit_growth", "EBIT growth", Fmt.PCT,
             lambda R, H, p: growth(R("ebit", p), R("ebit", p - 1)), "growth", start=1),
        Spec("ni_growth", "Net income growth", Fmt.PCT,
             lambda R, H, p: growth(R("net_income", p), R("net_income", p - 1)), "growth", start=1),
        Spec("eps_growth", "Diluted EPS growth", Fmt.PCT,
             lambda R, H, p: growth(R("eps_diluted", p), R("eps_diluted", p - 1)), "growth", start=1),
    ])
    r += 1

    # ---- Margins ---------------------------------------------------------
    r = header(r, "Profitability & Margins")
    mw = ("Expanding", "Stable", "Compressing")
    r = render(r, [
        Spec("gross_margin", "Gross margin", Fmt.PCT,
             lambda R, H, p: ratio(R("gross_profit", p), R("revenue", p)), "trend", mw),
        Spec("ebitda_margin", "EBITDA margin", Fmt.PCT,
             lambda R, H, p: ratio(R("ebitda", p), R("revenue", p)), "trend", mw),
        Spec("ebit_margin", "EBIT (operating) margin", Fmt.PCT,
             lambda R, H, p: ratio(R("ebit", p), R("revenue", p)), "trend", mw),
        Spec("net_margin", "Net margin", Fmt.PCT,
             lambda R, H, p: ratio(R("net_income", p), R("revenue", p)), "trend", mw),
        Spec("sga_pct", "SG&A % of revenue", Fmt.PCT,
             lambda R, H, p: ratio(R("sga", p), R("revenue", p)), "trend_inv", indent=1),
        Spec("rd_pct", "R&D % of revenue", Fmt.PCT,
             lambda R, H, p: ratio(R("rd", p), R("revenue", p)), "trend_inv", indent=1),
        Spec("da_pct", "D&A % of revenue", Fmt.PCT,
             lambda R, H, p: ratio(R("da", p), R("revenue", p)), "none", indent=1),
        Spec("interest_burden", "Interest burden (EBT / EBIT)", Fmt.PCT,
             lambda R, H, p: ratio(R("pretax_income", p), R("ebit", p)), "trend", indent=1),
        Spec("tax_burden", "Tax burden (NI / EBT)", Fmt.PCT,
             lambda R, H, p: ratio(R("net_income", p), R("pretax_income", p)), "trend", indent=1),
        Spec("eff_tax", "Effective tax rate", Fmt.PCT,
             lambda R, H, p: ratio(R("tax_expense", p), R("pretax_income", p)), "none", indent=1),
    ])
    r += 1

    # ---- Returns ---------------------------------------------------------
    r = header(r, "Returns on Capital")
    r = render(r, [
        Spec("_nopat", "NOPAT = EBIT × (1 − effective tax)", Fmt.MONEY,
             lambda R, H, p: _guard(
                 f"{R('ebit',p)}*(1-{R('tax_expense',p)}/{R('pretax_income',p)})",
                 R("ebit", p), R("tax_expense", p), R("pretax_income", p)), "none", indent=1),
        Spec("_invcap", "Invested capital (debt + equity − cash)", Fmt.MONEY,
             lambda R, H, p: f"={R('total_equity',p)}+{R('minority_equity',p)}"
                             f"+{R('short_term_debt',p)}+{R('long_term_debt',p)}"
                             f"-{R('cash',p)}-{R('st_investments',p)}", "none", indent=1),
        Spec("roe", "Return on equity (ROE)", Fmt.PCT,
             lambda R, H, p: ratio(R("net_income", p), R("total_equity", p)), "bands",
             [(T.RETURN_WEAK, "Weak"), (T.RETURN_STRONG, "Moderate"), (None, "Strong")]),
        Spec("roa", "Return on assets (ROA)", Fmt.PCT,
             lambda R, H, p: ratio(R("net_income", p), R("total_assets", p)), "bands",
             [(0.03, "Weak"), (0.07, "Moderate"), (None, "Strong")]),
        Spec("roic", "Return on invested capital (ROIC)", Fmt.PCT,
             lambda R, H, p: ratio(H("_nopat", p), H("_invcap", p)), "bands",
             [(0.08, "Weak"), (0.12, "Moderate"), (None, "Strong")]),
        Spec("roce", "Return on capital employed (ROCE)", Fmt.PCT,
             lambda R, H, p: ratio(R("ebit", p),
                                   f"({R('total_assets',p)}-{R('total_current_liabilities',p)})"),
             "bands", [(0.08, "Weak"), (0.12, "Moderate"), (None, "Strong")]),
    ])
    r += 1

    # ---- Liquidity -------------------------------------------------------
    r = header(r, "Liquidity")
    r = render(r, [
        Spec("current_ratio", "Current ratio", Fmt.MULT2,
             lambda R, H, p: ratio(R("total_current_assets", p), R("total_current_liabilities", p)),
             "bands", [(T.CURRENT_WEAK, "Weak"), (T.CURRENT_STRONG, "Adequate"), (None, "Strong")]),
        Spec("quick_ratio", "Quick ratio (ex-inventory)", Fmt.MULT2,
             lambda R, H, p: ratio(f"({R('total_current_assets',p)}-{R('inventory',p)})",
                                   R("total_current_liabilities", p)),
             "bands", [(T.QUICK_WEAK, "Weak"), (T.QUICK_STRONG, "Adequate"), (None, "Strong")]),
        Spec("cash_ratio", "Cash ratio", Fmt.MULT2,
             lambda R, H, p: ratio(f"({R('cash',p)}+{R('st_investments',p)})",
                                   R("total_current_liabilities", p)),
             "bands", [(0.2, "Weak"), (0.5, "Adequate"), (None, "Strong")]),
    ])
    r += 1

    # ---- Leverage & solvency --------------------------------------------
    r = header(r, "Leverage & Solvency")
    r = render(r, [
        Spec("_total_debt", "Total debt", Fmt.MONEY,
             lambda R, H, p: f"={R('short_term_debt',p)}+{R('long_term_debt',p)}", "none", indent=1),
        Spec("net_debt", "Net debt (debt − cash & investments)", Fmt.MONEY,
             lambda R, H, p: f"={H('_total_debt',p)}-{R('cash',p)}-{R('st_investments',p)}",
             "none", indent=1),
        Spec("debt_to_equity", "Debt / equity", Fmt.MULT2,
             lambda R, H, p: ratio(H("_total_debt", p), R("total_equity", p)), "bands",
             [(0.5, "Conservative"), (1.0, "Moderate"), (2.0, "Elevated"), (None, "Stretched")]),
        Spec("net_debt_ebitda", "Net debt / EBITDA", Fmt.MULT,
             lambda R, H, p: ratio(H("net_debt", p), R("ebitda", p)), "bands",
             [(T.LEV_LOW, "Conservative"), (T.LEV_MODERATE, "Moderate"),
              (T.LEV_HIGH, "Elevated"), (None, "Stretched")]),
        Spec("interest_coverage", "Interest coverage (EBIT / interest)", Fmt.MULT,
             lambda R, H, p: ratio(R("ebit", p), R("interest_expense", p)), "bands",
             [(T.COVER_WEAK, "Weak"), (T.COVER_ADEQUATE, "Moderate"), (None, "Strong")]),
        Spec("ebitda_coverage", "EBITDA / interest", Fmt.MULT,
             lambda R, H, p: ratio(R("ebitda", p), R("interest_expense", p)), "bands",
             [(3.0, "Weak"), (6.0, "Moderate"), (None, "Strong")]),
    ])
    r += 1

    # ---- Efficiency / working capital -----------------------------------
    r = header(r, "Capital Efficiency & Working Capital")
    r = render(r, [
        Spec("dso", "Days sales outstanding (DSO)", Fmt.DAYS,
             lambda R, H, p: _guard(f"{R('accounts_receivable',p)}/{R('revenue',p)}*365",
                                    R("accounts_receivable", p), R("revenue", p)), "none"),
        Spec("dio", "Days inventory outstanding (DIO)", Fmt.DAYS,
             lambda R, H, p: _guard(f"{R('inventory',p)}/{R('cogs',p)}*365",
                                    R("inventory", p), R("cogs", p)), "none"),
        Spec("dpo", "Days payable outstanding (DPO)", Fmt.DAYS,
             lambda R, H, p: _guard(f"{R('accounts_payable',p)}/{R('cogs',p)}*365",
                                    R("accounts_payable", p), R("cogs", p)), "none"),
        Spec("ccc", "Cash conversion cycle (DSO+DIO−DPO)", Fmt.DAYS,
             lambda R, H, p: _guard(f"{H('dso',p)}+{H('dio',p)}-{H('dpo',p)}",
                                    H("dso", p), H("dio", p), H("dpo", p)), "trend_inv"),
        Spec("asset_turnover", "Asset turnover (rev / assets)", Fmt.MULT2,
             lambda R, H, p: ratio(R("revenue", p), R("total_assets", p)), "trend"),
        Spec("inventory_turnover", "Inventory turnover (COGS / inv)", Fmt.MULT,
             lambda R, H, p: ratio(R("cogs", p), R("inventory", p)), "trend"),
        Spec("receivables_turnover", "Receivables turnover", Fmt.MULT,
             lambda R, H, p: ratio(R("revenue", p), R("accounts_receivable", p)), "trend"),
        Spec("payables_turnover", "Payables turnover", Fmt.MULT,
             lambda R, H, p: ratio(R("cogs", p), R("accounts_payable", p)), "none"),
    ])
    r += 1

    # ---- Cash flow -------------------------------------------------------
    r = header(r, "Cash-Flow Quality")
    r = render(r, [
        Spec("cfo_margin", "CFO margin", Fmt.PCT,
             lambda R, H, p: ratio(R("cfo", p), R("revenue", p)), "trend"),
        Spec("fcf", "Free cash flow (CFO − capex)", Fmt.MONEY,
             lambda R, H, p: f"={R('cfo',p)}-{R('capex',p)}", "none"),
        Spec("fcf_margin", "FCF margin", Fmt.PCT,
             lambda R, H, p: ratio(H("fcf", p), R("revenue", p)), "bands",
             [(T.FCF_WEAK, "Weak"), (T.FCF_STRONG, "Moderate"), (None, "Strong")]),
        Spec("capex_intensity", "Capex intensity (capex / revenue)", Fmt.PCT,
             lambda R, H, p: ratio(R("capex", p), R("revenue", p)), "none"),
        Spec("fcf_conversion", "FCF conversion (FCF / net income)", Fmt.PCT,
             lambda R, H, p: ratio(H("fcf", p), R("net_income", p)), "trend"),
        Spec("cash_conversion", "Cash conversion (CFO / EBITDA)", Fmt.PCT,
             lambda R, H, p: ratio(R("cfo", p), R("ebitda", p)), "trend"),
    ])
    r += 1

    # ---- Capital returns -------------------------------------------------
    r = header(r, "Shareholder Returns")
    r = render(r, [
        Spec("div_payout", "Dividend payout ratio", Fmt.PCT,
             lambda R, H, p: ratio(R("dividends_paid", p), R("net_income", p)), "none"),
        Spec("buyback_intensity", "Buyback intensity (/ net income)", Fmt.PCT,
             lambda R, H, p: ratio(R("buybacks", p), R("net_income", p)), "none"),
        Spec("total_payout", "Total payout ratio (div + buyback)", Fmt.PCT,
             lambda R, H, p: ratio(f"({R('dividends_paid',p)}+{R('buybacks',p)})",
                                   R("net_income", p)), "none"),
    ])

    if label_anchor_rows:
        top, bot = min(label_anchor_rows), max(label_anchor_rows)
        rng = f"{sh.coord(top, note_col)}:{sh.coord(bot, note_col)}"
        common.add_label_coloring(sh, rng, sh.coord(top, note_col))

    sh.freeze("B8")
    return sh


def _label_formula(sh, row, sp: Spec, last_col: int) -> str:
    """Build the interpretation-label formula for the latest period of a row."""
    latest = sh.local(row, last_col)
    avg = f"AVERAGE({sh.local(row, FDC)}:{sh.local(row, last_col - 1)})"
    if sp.kind == "growth":
        prior = sh.local(row, last_col - 1)
        return label_growth(latest, prior, T.GROWTH_ACCEL_PP)
    if sp.kind == "trend":
        words = sp.arg or ("Improving", "Stable", "Deteriorating")
        return label_trend(latest, avg, T.TREND_BAND, up=words[0], flat=words[1],
                           down=words[2], higher_is_better=True)
    if sp.kind == "trend_inv":
        return label_trend(latest, avg, T.TREND_BAND, up="Improving", flat="Stable",
                           down="Deteriorating", higher_is_better=False)
    if sp.kind == "bands":
        bands = [(b, lab) for (b, lab) in sp.arg if b is not None]
        above = next(lab for (b, lab) in sp.arg if b is None)
        return label_bands(latest, bands, above)
    return ""
