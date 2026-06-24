"""
Risk & Return  (capital-market assumptions).

The long-term inputs the recommended allocation draws on: each asset's expected
return and volatility, the correlation between assets, and the resulting
covariance table. Kept as simple, visible tables -- no optimiser, no hidden math.
The covariance table is what lets portfolio risk fall when assets don't move
together; the Allocation sheet uses it to compute each portfolio's volatility.
"""

from __future__ import annotations

from .. import common
from ..config import ASSETS, Fmts

SHORT = {"smi": "SMI", "sp500": "S&P 500", "sxi_re": "SXI RE", "gold": "Gold", "ust": "US Bonds"}
LAST = 6


def build(sh, ctx):
    refs = ctx.refs
    d = ctx.data
    keys = ctx.keys

    common.title_block(sh, "RISK & RETURN", "Long-term assumptions used by the recommended allocation",
                       last_col=LAST)
    common.nav_bar(sh, 5)
    r = common.explain_box(sh, 7, [
        "WHAT TO INPUT:  a long-term (annual) expected return and a volatility for each asset, plus how the assets "
        "move together (the correlation table).  These are long-run views, separate from the one-off scenario.",
        "WHAT IT MEANS:  volatility = how much an asset bounces around (risk).  Correlation = do two assets move "
        "together (near +1), independently (0), or opposite (near -1).  Diversification works best with low correlation.",
        "Sharpe ratio = (expected return - risk-free) / volatility = return earned per unit of risk.  Higher is better.",
    ], last_col=LAST)
    r += 1

    sh.put(r, 1, "Risk-free rate (annual)", role="label_b")
    sh.put(r, 3, d.get("risk_free"), role="input", fmt=Fmts.PCT, key="rr.rf")
    common.define_name(sh, "RiskFree", r, 3)
    r += 2

    # ---- capital market assumptions ----
    r = common.section(sh, r, "Capital-Market Assumptions", c1=1, c2=LAST)
    hdr = r
    for c, t in enumerate(["Asset", "Expected\nreturn", "Volatility\n(risk)", "Scenario\nreturn", "Sharpe\nratio"], 1):
        sh.put(hdr, c, t, role="colhdr" if c > 1 else "colhdr_l")
    sh.row_height(hdr, 26)
    r += 1
    for key, name, _ in ASSETS:
        a = d["assets"][key]
        sh.put(r, 1, name, role="label")
        sh.put(r, 2, a.get("exp_return"), role="input", fmt=Fmts.PCT, key=f"rr.exp@{key}")
        sh.put(r, 3, a.get("volatility"), role="input", fmt=Fmts.PCT, key=f"rr.vol@{key}")
        sh.put(r, 4, f"={refs.ref(f'out.curradj@{key}')}", role="link", fmt=Fmts.PCT, key=f"rr.scen@{key}")
        sh.put(r, 5, f"=IFERROR(({refs.ref(f'rr.exp@{key}')}-RiskFree)/{refs.ref(f'rr.vol@{key}')},\"\")",
               role="formula", fmt=Fmts.RATIO, key=f"rr.sharpe@{key}")
        r += 1
    r += 1

    # ---- correlation matrix (inputs) ----
    r = common.section(sh, r, "Correlation Matrix  (how assets move together; 1 = same, 0 = independent, -1 = opposite)",
                       c1=1, c2=LAST)
    chdr = r
    sh.put(chdr, 1, "Correlation", role="colhdr_l")
    for j, key in enumerate(keys):
        sh.put(chdr, 2 + j, SHORT[key], role="colhdr")
    r += 1
    corr = d["correlations"]
    for i, ki in enumerate(keys):
        sh.put(r, 1, SHORT[ki], role="label_b")
        for j, kj in enumerate(keys):
            sh.put(r, 2 + j, corr[i][j], role="input_c", fmt=Fmts.RATIO, key=f"rr.corr@{i}_{j}")
        r += 1
    r += 1

    # ---- covariance matrix (computed) ----
    r = common.section(sh, r, "Covariance Matrix  (computed = volatility i x volatility j x correlation)",
                       c1=1, c2=LAST)
    cov_hdr = r
    sh.put(cov_hdr, 1, "Covariance", role="colhdr_l")
    for j, key in enumerate(keys):
        sh.put(cov_hdr, 2 + j, SHORT[key], role="colhdr")
    r += 1
    cov_first = r
    for i, ki in enumerate(keys):
        sh.put(r, 1, SHORT[ki], role="label_b")
        for j, kj in enumerate(keys):
            f = f"={refs.ref(f'rr.vol@{ki}')}*{refs.ref(f'rr.vol@{kj}')}*{refs.ref(f'rr.corr@{i}_{j}')}"
            sh.put(r, 2 + j, f, role="formula", fmt='0.0000', key=f"rr.cov@{i}_{j}")
        r += 1
    # remember covariance block location for the Allocation sheet
    ctx.data["_cov_first_row"] = cov_first
    ctx.data["_cov_first_col"] = 2

    sh.put(r + 1, 1, "The Allocation sheet multiplies these covariances by the portfolio weights to get each "
                     "portfolio's volatility (risk). Lower correlations -> more diversification -> lower risk.",
           role="note")
    sh.merge(r + 1, 1, r + 1, LAST)

    sh.freeze("A6")
    sh.col_width(1, 26)
    for c in range(2, LAST + 1):
        sh.col_width(c, 12)
    return sh
