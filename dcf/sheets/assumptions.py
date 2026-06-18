"""
Assumptions sheet -- the DCF assumption engine.

Assumptions are *derived*, not typed at random:
  * Base revenue growth blends the historical revenue CAGR with the latest year's
    growth, then is clamped to a sane band.
  * The terminal EBIT margin anchors on the recent 3-year average margin.
  * D&A, capex and working-capital intensities come from historical averages.
  * The perpetuity growth rate uses a conservative long-run default, clamped to
    stay safely below WACC so terminal value cannot blow up.

Four scenarios (Base / Bull / Bear / Downside) are built by applying explicit
tilts to growth and margin. A selector cell drives which scenario the Forecast
and DCF use, via CHOOSE(). Every row is tagged model-derived / assumption /
fallback and carries a one-line rationale.
"""

from __future__ import annotations

from openpyxl.worksheet.datavalidation import DataValidation

from ..config import DEFAULT_SCENARIO_INDEX, Defaults, Fmt, SCENARIOS
from ..utils import avg_of, cagr, choose, ratio
from . import common

L, B, BU, BE, D, SRC, NOTE = 1, 2, 3, 4, 5, 6, 7  # columns


def build(sh, ctx: common.Context):
    refs = ctx.refs
    n = ctx.n_hist
    last = n - 1
    R = lambda k, p: refs.ref(f"in.{k}@{p}")      # noqa: E731
    H = lambda k, p: refs.ref(f"h.{k}@{p}")       # noqa: E731
    A = lambda k: refs.ref(f"as.{k}")             # noqa: E731

    sh.hide_gridlines()
    sh.col_width(L, 42)
    for c in (B, BU, BE, D):
        sh.col_width(c, 13)
    sh.col_width(SRC, 18)
    sh.col_width(NOTE, 54)
    r = common.title_block(sh, "ASSUMPTIONS",
                           "DCF assumption engine — driver-based, scenario-aware, fully sourced",
                           last_col=NOTE)
    r += 1

    # ---- scenario selector ----------------------------------------------
    r = common.section(sh, r, "Scenario Selector", c1=1, c2=NOTE)
    sh.put(r, L, "Active scenario (1=Base, 2=Bull, 3=Bear, 4=Downside)", role="label_b")
    sh.put(r, B, DEFAULT_SCENARIO_INDEX, role="input", fmt=Fmt.INT, key="as.scenario_sel")
    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="4",
                        allow_blank=False, showErrorMessage=True)
    dv.error = "Enter 1 (Base), 2 (Bull), 3 (Bear) or 4 (Downside)."
    dv.prompt = "1=Base, 2=Bull, 3=Bear, 4=Downside"
    sh.ws.add_data_validation(dv)
    dv.add(sh.ws.cell(row=r, column=B))
    sh.put(r, SRC, "input", role="neutral", align="c")
    name = choose(A("scenario_sel"), [f'"{s}"' for s in SCENARIOS])
    sh.put(r, NOTE, name, role="link", align="l", key="as.scenario_name")
    sh.put(r, D, "← active scenario:", role="sublabel", align="r")
    r += 2

    # ---- derived historical anchors -------------------------------------
    r = common.section(sh, r, "Derived Historical Anchors (read-only)", c1=1, c2=NOTE)
    sh.put(r, L, "These are computed from the Historical sheet and feed the base case.",
           role="note")
    sh.merge(r, L, r, NOTE)
    r += 1

    def anchor(row, label, key, formula, fmt, note):
        sh.put(row, L, label, role="label")
        sh.put(row, B, formula, role="link", fmt=fmt, key=f"as.{key}")
        sh.put(row, SRC, "model-derived", role="neutral", align="c")
        sh.put(row, NOTE, note, role="note")
        return row + 1

    last3 = list(range(max(0, n - 3), n))
    r = anchor(r, "Historical revenue CAGR (full window)", "hist_rev_cagr",
               cagr(R("revenue", last), R("revenue", 0), str(n - 1)), Fmt.PCT,
               "Compound annual revenue growth across all reported years.")
    r = anchor(r, "Latest-year revenue growth", "last_growth",
               f"={H('rev_growth', last)}", Fmt.PCT, "Most recent year-on-year growth.")
    r = anchor(r, "Avg EBIT margin (last 3y)", "avg_ebit_margin",
               avg_of([H("ebit_margin", p) for p in last3]), Fmt.PCT,
               "Anchor for the sustainable operating margin.")
    r = anchor(r, "Avg D&A % of revenue (last 3y)", "da_pct",
               avg_of([H("da_pct", p) for p in last3]), Fmt.PCT,
               "Drives forecast depreciation & amortisation.")
    r = anchor(r, "Avg capex intensity (last 3y)", "capex_pct",
               avg_of([H("capex_intensity", p) for p in last3]), Fmt.PCT,
               "Drives forecast capital expenditure.")
    r = anchor(r, "Net working capital % of revenue", "nwc_pct",
               ratio(f"({R('accounts_receivable', last)}+{R('inventory', last)}"
                     f"-{R('accounts_payable', last)})", R("revenue", last)), Fmt.PCT,
               "Working capital scales with sales at this ratio.")
    r += 1

    # ---- scenario driver table ------------------------------------------
    r = common.section(sh, r, "Forecast Drivers by Scenario", c1=1, c2=NOTE)
    for col, txt in ((L, "Driver"), (B, "Base"), (BU, "Bull"), (BE, "Bear"),
                     (D, "Downside"), (SRC, "Source"), (NOTE, "Rationale")):
        sh.put(r, col, txt, role="colhdr" if col in (L, SRC, NOTE) else "colhdr_r")
    r += 1

    # Starting revenue growth (year 1): blend of CAGR and last-year growth, clamped.
    blend = (f"=IF(AND(ISNUMBER({A('hist_rev_cagr')}),ISNUMBER({A('last_growth')})),"
             f"({A('hist_rev_cagr')}+{A('last_growth')})/2,"
             f"IF(ISNUMBER({A('hist_rev_cagr')}),{A('hist_rev_cagr')},"
             f"IF(ISNUMBER({A('last_growth')}),{A('last_growth')},{Defaults.LONGRUN_GROWTH})))")
    sh.put(r, L, "Blended raw start growth", role="sublabel")
    sh.put(r, B, blend, role="calc", fmt=Fmt.PCT, key="as.blend_start")
    sh.put(r, NOTE, "Average of historical CAGR and latest growth (fallback to long-run).",
           role="note")
    r += 1

    base_start = f"=MAX(-0.05,MIN(0.20,{A('blend_start')}))"
    r = _scen_row(sh, r, "Revenue growth — year 1 (start)", "start_growth", base_start,
                  [Defaults.BULL_GROWTH_TILT, Defaults.BEAR_GROWTH_TILT, Defaults.DOWNSIDE_GROWTH_TILT],
                  refs, fmt=Fmt.PCT, lo=-0.30, hi=0.30, src="model-derived",
                  note="Start of the revenue path; clamped to a sane band. Bull/Bear/Downside add ±tilts.")

    base_tv = f"=MIN({Defaults.TERMINAL_GROWTH},{refs.ref('wacc.value')}-0.01)"
    r = _scen_row(sh, r, "Terminal / perpetuity growth (g)", "tv_growth", base_tv,
                  [0.005, -0.005, -0.010], refs, fmt=Fmt.PCT, lo=-0.02,
                  hi_ref=f"{refs.ref('wacc.value')}-0.01", src="assumption",
                  note="Long-run growth into perpetuity; capped at WACC−1% so TV stays finite.")

    base_margin = (f"=IF(ISNUMBER({A('avg_ebit_margin')}),MAX(0,MIN(0.60,{A('avg_ebit_margin')})),"
                   f"{Defaults.EBIT_MARGIN_FALLBACK})")
    r = _scen_row(sh, r, "Terminal EBIT margin", "target_margin", base_margin,
                  [Defaults.BULL_MARGIN_TILT, Defaults.BEAR_MARGIN_TILT, Defaults.DOWNSIDE_MARGIN_TILT],
                  refs, fmt=Fmt.PCT, lo=0.0, hi=0.60, src="model-derived",
                  note="Operating margin the business converges to by the terminal year.")
    r += 1

    # ---- scenario-invariant constants -----------------------------------
    r = common.section(sh, r, "Scenario-Invariant Drivers", c1=1, c2=NOTE)

    def const(row, label, key, formula, fmt, src, note):
        sh.put(row, L, label, role="label")
        sh.put(row, B, formula, role="link" if src != "input" else "input",
               fmt=fmt, key=f"as.{key}")
        sh.merge(row, B, row, D)
        sh.put(row, SRC, src, role="neutral", align="c")
        sh.put(row, NOTE, note, role="note")
        return row + 1

    da_used = f"=IF(ISNUMBER({A('da_pct')}),{A('da_pct')},{Defaults.DA_PCT_FALLBACK})"
    capex_used = f"=IF(ISNUMBER({A('capex_pct')}),{A('capex_pct')},{Defaults.CAPEX_PCT_FALLBACK})"
    nwc_used = f"=IF(ISNUMBER({A('nwc_pct')}),{A('nwc_pct')},{Defaults.NWC_PCT_FALLBACK})"
    r = const(r, "D&A as % of revenue", "da_pct_used", da_used, Fmt.PCT,
              "derived/fallback", "Historical average; conservative fallback if no history.")
    r = const(r, "Capex as % of revenue", "capex_pct_used", capex_used, Fmt.PCT,
              "derived/fallback", "Historical average; in steady state ≈ D&A.")
    r = const(r, "Net working capital % of revenue", "nwc_pct_used", nwc_used, Fmt.PCT,
              "derived/fallback", "ΔWC each year = this % × the change in revenue.")
    r = const(r, "Tax rate (from WACC sheet)", "tax", f"={refs.ref('wacc.tax')}", Fmt.PCT,
              "linked", "Marginal tax rate applied to EBIT to get NOPAT.")
    r = const(r, "Exit EBITDA multiple (TV cross-check)", "exit_multiple",
              str(Defaults.EXIT_EBITDA_MULTIPLE), Fmt.MULT, "fallback",
              "Generic multiple for the exit-multiple terminal-value cross-check only.")
    r = const(r, "Forecast horizon (years)", "horizon", str(ctx.n_fcst), Fmt.INT,
              "setting", "Number of explicitly forecast years before terminal value.")
    r += 1

    # ---- active (resolved) assumptions ----------------------------------
    r = common.section(sh, r, "Active Assumptions (resolved by selector)", c1=1, c2=NOTE)
    sh.put(r, L, "These are the values the Forecast & DCF actually use.", role="note")
    sh.merge(r, L, r, NOTE)
    r += 1

    def active(row, label, key, scen_key, fmt, note):
        opts = [refs.ref(f"as.{scen_key}.{s}") for s in SCENARIOS]
        sh.put(row, L, label, role="label_b")
        sh.put(row, B, choose(A("scenario_sel"), opts), role="output", fmt=fmt, key=f"as.{key}")
        sh.put(row, SRC, "active", role="neutral", align="c")
        sh.put(row, NOTE, note, role="note")
        return row + 1

    r = active(r, "Active start revenue growth", "act_start_growth", "start_growth", Fmt.PCT,
               "Year-1 revenue growth for the selected scenario.")
    r = active(r, "Active terminal growth (g)", "act_tv_growth", "tv_growth", Fmt.PCT,
               "Perpetuity growth; also the year-N revenue growth (smooth hand-off to TV).")
    r = active(r, "Active terminal EBIT margin", "act_target_margin", "target_margin", Fmt.PCT,
               "EBIT margin the forecast converges to.")
    r += 1

    # ---- methodology -----------------------------------------------------
    r = common.section(sh, r, "Methodology Notes", c1=1, c2=NOTE)
    for line in _METHOD:
        sh.put(r, L, "•  " + line, role="note")
        sh.merge(r, L, r, NOTE)
        sh.row_height(r, 26)
        r += 1
    return sh


def _scen_row(sh, row, label, key, base_formula, tilts, refs, *, fmt, lo=None, hi=None,
              hi_ref=None, src="assumption", note=""):
    """Write a Base cell + Bull/Bear/Downside = clamp(base + tilt). Registers each."""
    sh.put(row, L, label, role="label_b")
    sh.put(row, B, base_formula, role="calc", fmt=fmt, key=f"as.{key}.Base")
    base_ref = refs.ref(f"as.{key}.Base")
    cols = {"Bull": (3, tilts[0]), "Bear": (4, tilts[1]), "Downside": (5, tilts[2])}
    for scen, (col, tilt) in cols.items():
        raw = f"{base_ref}+{tilt}"
        hi_part = hi_ref if hi_ref is not None else (str(hi) if hi is not None else None)
        if lo is not None and hi_part is not None:
            formula = f"=MAX({lo},MIN({hi_part},{raw}))"
        elif hi_part is not None:
            formula = f"=MIN({hi_part},{raw})"
        elif lo is not None:
            formula = f"=MAX({lo},{raw})"
        else:
            formula = f"={raw}"
        sh.put(row, col, formula, role="calc", fmt=fmt, key=f"as.{key}.{scen}")
    sh.put(row, 6, src, role="neutral", align="c")
    sh.put(row, 7, note, role="note")
    return row + 1


_METHOD = [
    "Revenue is forecast by fading the year-1 growth rate linearly to the terminal "
    "growth rate over the horizon — a transparent mean-reversion that avoids an "
    "arbitrary flat growth assumption.",
    "Operating margin fades linearly from the last reported EBIT margin to the "
    "terminal target margin, reflecting gradual normalisation rather than a step change.",
    "Capex, D&A and working capital are tied to revenue via historical intensity "
    "ratios, so they scale with the business instead of being guessed.",
    "Scenarios change only a few economically meaningful levers (growth and margin); "
    "this keeps the bull/bear/downside cases comparable and interpretable.",
    "Where a needed figure is missing, the model falls back to a clearly-labelled "
    "conservative default rather than inventing a number.",
]
