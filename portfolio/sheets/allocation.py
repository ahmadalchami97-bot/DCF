"""
Allocation.

Compares six allocations side by side and builds a scenario-stressed recommended
allocation. The weighting rules are deliberately SIMPLE and visible -- no Solver,
no optimiser:

  * Max-Sharpe (simplified): more weight to assets with the best long-run return
    per unit of risk  ->  score = max(0, expected - risk-free) / volatility^2.
  * Min-volatility (simplified): more weight to calmer assets  ->  1 / volatility^2.
  * Scenario-stressed: start from the Max-Sharpe mix, tilt MODESTLY toward assets
    that did well in the scenario (capped, so we never chase short-term moves),
    then clamp to your min/max limits.

Portfolio risk for each allocation is computed transparently from the covariance
table on Risk & Return (so correlation genuinely matters), shown next to the
expected return so you can weigh risk against reward.
"""

from __future__ import annotations

from .. import common
from ..common import col_letter as CL
from ..config import ALLOCATIONS, ASSETS, DISCLAIMER, Defaults, Fmts

SHORT = {"smi": "SMI", "sp500": "S&P 500", "sxi_re": "SXI RE", "gold": "Gold", "ust": "US Bonds"}
LAST = 16


def build(sh, ctx):
    refs = ctx.refs
    keys = ctx.keys
    n = ctx.n
    k0, kN = keys[0], keys[-1]
    RR = lambda k, key: refs.ref(f"rr.{k}@{key}")   # noqa: E731
    IN = lambda k, key: refs.ref(f"in.{k}@{key}")   # noqa: E731
    AL = lambda k, key: refs.ref(f"al.{k}@{key}")   # noqa: E731

    common.title_block(sh, "ALLOCATION", "Compare allocations and build a scenario-stressed recommendation",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "WHAT THIS SHEET DOES:  compares your Current allocation with Equal-weight, your Custom target, a simplified "
        "Max-Sharpe and Min-volatility mix, and a Scenario-stressed recommendation.",
        "HOW THE RECOMMENDATION IS BUILT:  it starts from the Max-Sharpe mix (long-term return vs risk vs correlation), "
        "tilts modestly toward assets that did well in the scenario (capped so it never chases short-term moves), then "
        "respects your minimum/maximum weights.",
        "HOW TO READ IT:  look at expected return AND volatility together -- higher return with higher risk is not "
        "automatically better. The Sharpe ratio (return per unit of risk) helps you compare.",
    ], last_col=LAST)
    r += 1

    # ---- Step 1: building blocks ----
    r = common.section(sh, r, "Step 1 - Building blocks (used by Max-Sharpe, Min-volatility and the scenario tilt)",
                       c1=1, c2=LAST)
    hdr = r
    for c, t in enumerate(["Asset", "Volatility", "1 / Vol^2\n(min-vol)", "Sharpe score\n(max-Sharpe)",
                           "Scenario\nreturn", "Tilt\n(capped)", "Min\nweight", "Max\nweight"], 1):
        sh.put(hdr, c, t, role="colhdr" if c > 1 else "colhdr_l")
    common.cell_comment(sh, hdr, 4, "Sharpe score = max(0, expected return - risk-free) / volatility^2.\n"
                                    "Higher = better long-term return per unit of risk -> more weight in Max-Sharpe.")
    common.cell_comment(sh, hdr, 6, "Tilt = capped( sensitivity x (scenario return - average scenario return) ).\n"
                                    "Capped so the recommendation never chases short-term moves.")
    sh.row_height(hdr, 26)
    r += 1
    scen_rng = refs.range(f"rr.scen@{k0}", f"rr.scen@{kN}")
    bb_first = r
    for key, name, _ in ASSETS:
        sh.put(r, 1, name, role="label")
        sh.put(r, 2, f"={RR('vol', key)}", role="link", fmt=Fmts.PCT)
        sh.put(r, 3, f"=IFERROR(1/{RR('vol', key)}^2,0)", role="formula", fmt=Fmts.RATIO, key=f"al.invvar@{key}")
        sh.put(r, 4, f"=IFERROR(MAX(0,{RR('exp', key)}-RiskFree)/{RR('vol', key)}^2,0)",
               role="formula", fmt=Fmts.RATIO, key=f"al.score@{key}")
        sh.put(r, 5, f"={RR('scen', key)}", role="link", fmt=Fmts.PCT)
        sh.put(r, 6, f"=MEDIAN(-{Defaults.TILT_CAP},{Defaults.SCENARIO_TILT}*({RR('scen', key)}-AVERAGE({scen_rng})),{Defaults.TILT_CAP})",
               role="formula", fmt=Fmts.PCT, key=f"al.tilt@{key}")
        sh.put(r, 7, f"={IN('min_w', key)}", role="link", fmt=Fmts.PCT)
        sh.put(r, 8, f"={IN('max_w', key)}", role="link", fmt=Fmts.PCT)
        r += 1
    bb_last = r - 1
    sh.put(r, 1, "Total", role="total_l")
    sh.put(r, 3, f"=SUM({CL(3)}{bb_first}:{CL(3)}{bb_last})", role="total", fmt=Fmts.RATIO, key="al.sum_invvar")
    sh.put(r, 4, f"=SUM({CL(4)}{bb_first}:{CL(4)}{bb_last})", role="total", fmt=Fmts.RATIO, key="al.sum_score")
    sum_invvar, sum_score = refs.ref("al.sum_invvar"), refs.ref("al.sum_score")
    r += 2

    # ---- Step 2: scenario build (reserve rows; labels only for now) ----
    r = common.section(sh, r, "Step 2 - How the scenario-stressed allocation is built  "
                       "(fit to your min/max, re-total to 100%, repeat so it settles)", c1=1, c2=LAST)
    shdr = r
    for c, t in enumerate(["Asset", "Max-Sharpe\nbase", "Tilt\n(capped)", "Raw\n= base x (1+tilt)",
                           "Normalised", "Fit to\nmin/max", "Re-total\nto 100%", "Fit\nagain",
                           "Final\nweight", "Within limits?"], 1):
        sh.put(shdr, c, t, role="colhdr" if c > 1 else "colhdr_l")
    sh.row_height(shdr, 26)
    r += 1
    sb_first = r
    for key, name, _ in ASSETS:
        sh.put(r, 1, name, role="label")
        r += 1
    sb_rows = list(range(sb_first, sb_first + n))
    sb_total = sb_first + n
    sh.put(sb_total, 1, "Total", role="total_l")
    r = sb_total + 2

    # ---- Step 3: comparison (cols 2-6 now; scenario col 7 after Step 2 filled) ----
    r = common.section(sh, r, "Step 3 - Allocation comparison  (each column sums to 100%)", c1=1, c2=LAST)
    chdr = r
    sh.put(chdr, 1, "Asset", role="colhdr_l")
    for j, (akey, alabel, _note) in enumerate(ALLOCATIONS):
        sh.put(chdr, 2 + j, alabel, role="colhdr")
    r = chdr + 1
    cmp_first = r
    tgt_rng = refs.range(f"in.target_w@{k0}", f"in.target_w@{kN}")
    scen_col = 2 + [a[0] for a in ALLOCATIONS].index("scenario")
    for key, name, _ in ASSETS:
        sh.put(r, 1, name, role="label")
        sh.put(r, 2, f"={refs.ref(f'out.weight@{key}')}", role="formula", fmt=Fmts.PCT, key=f"al.w@current_{key}")
        sh.put(r, 3, f"=1/{n}", role="formula", fmt=Fmts.PCT, key=f"al.w@equal_{key}")
        sh.put(r, 4, f"=IFERROR({IN('target_w', key)}/SUM({tgt_rng}),0)", role="formula", fmt=Fmts.PCT, key=f"al.w@target_{key}")
        sh.put(r, 5, f"=IFERROR({AL('score', key)}/{sum_score},1/{n})", role="formula", fmt=Fmts.PCT, key=f"al.w@sharpe_{key}")
        sh.put(r, 6, f"=IFERROR({AL('invvar', key)}/{sum_invvar},1/{n})", role="formula", fmt=Fmts.PCT, key=f"al.w@minvol_{key}")
        r += 1
    cmp_last = r - 1
    cmp_total = r
    sh.put(cmp_total, 1, "Total", role="total_l")
    for j in range(len(ALLOCATIONS)):
        c = 2 + j
        sh.put(cmp_total, c, f"=SUM({CL(c)}{cmp_first}:{CL(c)}{cmp_last})", role="total", fmt=Fmts.PCT)
    r = cmp_total + 2

    # ---- fill Step 2 (sharpe weights now exist) ----
    raw_rng = f"{CL(4)}{sb_rows[0]}:{CL(4)}{sb_rows[-1]}"
    fit1_rng = f"{CL(6)}{sb_rows[0]}:{CL(6)}{sb_rows[-1]}"
    fit2_rng = f"{CL(8)}{sb_rows[0]}:{CL(8)}{sb_rows[-1]}"
    for i, (key, _name, _) in enumerate(ASSETS):
        rr_ = sb_rows[i]
        mn, mx = IN("min_w", key), IN("max_w", key)
        sh.put(rr_, 2, f"={refs.ref(f'al.w@sharpe_{key}')}", role="link", fmt=Fmts.PCT)
        sh.put(rr_, 3, f"={AL('tilt', key)}", role="link", fmt=Fmts.PCT)
        sh.put(rr_, 4, f"={sh.local(rr_, 2)}*(1+{sh.local(rr_, 3)})", role="formula", fmt=Fmts.PCT, key=f"al.scen_raw@{key}")
        sh.put(rr_, 5, f"=IFERROR({sh.local(rr_, 4)}/SUM({raw_rng}),0)", role="formula", fmt=Fmts.PCT, key=f"al.scen_norm@{key}")
        sh.put(rr_, 6, f"=MEDIAN({mn},{sh.local(rr_, 5)},{mx})", role="formula", fmt=Fmts.PCT)
        sh.put(rr_, 7, f"=IFERROR({sh.local(rr_, 6)}/SUM({fit1_rng}),0)", role="formula", fmt=Fmts.PCT)
        sh.put(rr_, 8, f"=MEDIAN({mn},{sh.local(rr_, 7)},{mx})", role="formula", fmt=Fmts.PCT)
        sh.put(rr_, 9, f"=IFERROR({sh.local(rr_, 8)}/SUM({fit2_rng}),0)", role="output", fmt=Fmts.PCT, key=f"al.scen_final@{key}")
        sh.put(rr_, 10, f'=IF(AND({sh.local(rr_, 9)}>={mn}-0.005,{sh.local(rr_, 9)}<={mx}+0.005),"Within","Review")',
               role="status")
    sh.put(sb_total, 9, f"=SUM({CL(9)}{sb_rows[0]}:{CL(9)}{sb_rows[-1]})", role="total", fmt=Fmts.PCT)
    common.traffic_light(sh, f"{CL(10)}{sb_rows[0]}:{CL(10)}{sb_rows[-1]}", f"{CL(10)}{sb_rows[0]}")

    # ---- now the comparison scenario column ----
    for i, (key, _name, _) in enumerate(ASSETS):
        sh.put(cmp_first + i, scen_col, f"={refs.ref(f'al.scen_final@{key}')}",
               role="output", fmt=Fmts.PCT, key=f"al.w@scenario_{key}")

    # ---- Step 4: portfolio risk & return engine ----
    r = common.section(sh, r, "Step 4 - Portfolio risk & return for each allocation  (engine - no need to edit)",
                       c1=1, c2=LAST)
    ehdr = r
    labels = ["Allocation"] + [SHORT[k] for k in keys] + ["Exp.\nreturn"] + \
             ["cw " + SHORT[k] for k in keys] + ["Variance", "Volatility", "Sharpe"]
    for c, t in enumerate(labels, 1):
        sh.put(ehdr, c, t, role="colhdr" if c > 1 else "colhdr_l")
    common.cell_comment(sh, ehdr, 2 + n + n + 2, "Volatility = SQRT( portfolio variance ), where variance is built "
                        "from the weights and the covariance table on Risk & Return. Lower correlations -> lower risk.")
    sh.row_height(ehdr, 24)
    r += 1
    sh.put(r, 1, "Expected return (by asset)", role="sublabel")
    exp_row = r
    for j, key in enumerate(keys):
        sh.put(r, 2 + j, f"={RR('exp', key)}", role="link", fmt=Fmts.PCT)
    exp_rng = f"{CL(2)}{exp_row}:{CL(1 + n)}{exp_row}"
    r += 1
    w0 = 2
    cw0 = 2 + n + 1
    for akey, alabel, _note in ALLOCATIONS:
        sh.put(r, 1, alabel, role="label_b")
        wr = f"{CL(w0)}{r}:{CL(w0 + n - 1)}{r}"
        for j, key in enumerate(keys):
            sh.put(r, w0 + j, f"={refs.ref(f'al.w@{akey}_{key}')}", role="formula", fmt=Fmts.PCT)
        sh.put(r, 2 + n, f"=SUMPRODUCT({wr},{exp_rng})", role="output", fmt=Fmts.PCT, key=f"al.ret@{akey}")
        for i, key in enumerate(keys):
            cov_row = refs.range(f"rr.cov@{i}_0", f"rr.cov@{i}_{n - 1}")
            sh.put(r, cw0 + i, f"=SUMPRODUCT({wr},{cov_row})", role="formula", fmt='0.0000')
        cwr = f"{CL(cw0)}{r}:{CL(cw0 + n - 1)}{r}"
        sh.put(r, cw0 + n, f"=SUMPRODUCT({wr},{cwr})", role="formula", fmt='0.0000', key=f"al.var@{akey}")
        sh.put(r, cw0 + n + 1, f"=SQRT({refs.ref(f'al.var@{akey}')})", role="output", fmt=Fmts.PCT, key=f"al.vol@{akey}")
        sh.put(r, cw0 + n + 2, f"=IFERROR(({refs.ref(f'al.ret@{akey}')}-RiskFree)/{refs.ref(f'al.vol@{akey}')},\"\")",
               role="formula", fmt=Fmts.RATIO, key=f"al.sharpe@{akey}")
        r += 1
    r += 2

    # ---- Step 5: recommended allocation (selectable) ----
    r = common.section(sh, r, "Step 5 - Recommended allocation", c1=1, c2=LAST)
    names = [a[1] for a in ALLOCATIONS]
    sh.put(r, 1, "Rebalance toward", role="label_b")
    sh.put(r, 3, names[-1], role="input_l", key="al.rec_name")
    common.dropdown(sh, r, 3, names)
    sh.merge(r, 3, r, 5)
    sh.put(r, 6, "Pick which allocation to rebalance toward (default: Scenario-stressed).", role="note_l")
    sh.merge(r, 6, r, LAST)
    r += 1
    sh.put(r, 1, "(selector options)", role="sublabel")
    for j, nm in enumerate(names):
        sh.put(r, 2 + j, nm, role="note_l", key=f"al.opt@{j}")
    opt_rng = refs.range("al.opt@0", f"al.opt@{len(names) - 1}")
    r += 1
    sh.put(r, 1, "Basis number", role="label")
    sh.put(r, 3, f"=IFERROR(MATCH({refs.ref('al.rec_name')},{opt_rng},0),{len(names)})",
           role="formula", fmt=Fmts.INT, key="al.rec_basis")
    common.define_name(sh, "RecBasis", r, 3)
    r += 2

    rhdr = r
    sh.put(rhdr, 1, "Asset", role="colhdr_l")
    sh.put(rhdr, 2, "Recommended weight", role="colhdr")
    sh.merge(rhdr, 2, rhdr, 4)
    r += 1
    for key, name, _ in ASSETS:
        sh.put(r, 1, name, role="label")
        choose = ",".join(refs.ref(f"al.w@{a[0]}_{key}") for a in ALLOCATIONS)
        sh.put(r, 2, f"=CHOOSE(RecBasis,{choose})", role="output", fmt=Fmts.PCT, key=f"al.rec_w@{key}")
        sh.merge(r, 2, r, 4)
        r += 1
    sh.put(r, 1, "Total", role="total_l")
    sh.put(r, 2, f"=SUM({refs.range('al.rec_w@' + k0, 'al.rec_w@' + kN)})", role="total", fmt=Fmts.PCT)
    sh.merge(r, 2, r, 4)
    r += 2

    common.explain_box(sh, r, [DISCLAIMER], last_col=LAST, title="Important")

    sh.freeze("A6")
    sh.col_width(1, 26)
    for c in range(2, LAST + 1):
        sh.col_width(c, 11)
    return sh
