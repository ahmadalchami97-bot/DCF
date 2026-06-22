"""
Quality Analysis (Sheet 12): Piotroski F-Score, Altman Z-Score, Beneish M-Score,
ROIC vs WACC and economic profit.

Every score is built from explicit component helper rows (blue) and then summed /
weighted into the headline score (green) — so the user can see exactly how each
score is constructed, per the "show every step" rule.
"""

from __future__ import annotations

from dcf.config import Fmt
from ..formulas import div, q, sentence, text
from ..render import Grid

PCT, F2, MONEY = Fmt.PCT, Fmt.FLOAT2, Fmt.MONEY


def build(sh, ctx):
    g = Grid(sh, ctx, "qual")
    R, S = g.R, g.S
    li = ctx.last_hist_idx
    g.title("QUALITY ANALYSIS", "Piotroski F · Altman Z · Beneish M · economic profit")
    g.yearhead("Quality metric")

    # ---------- Altman Z-Score ----------
    g.section("Altman Z-Score  (bankruptcy/distress risk)")
    g.helper("z_x1", "X1 = working capital / assets", lambda i: div(R("working_capital", i), R("total_assets", i)), F2)
    g.helper("z_x2", "X2 = retained earnings / assets", lambda i: div(R("retained_earnings", i), R("total_assets", i)), F2)
    g.helper("z_x3", "X3 = EBIT / assets", lambda i: div(R("ebit", i), R("total_assets", i)), F2)
    g.helper("z_x4", "X4 = market cap / total liabilities", lambda i: div(R("market_cap", i), R("total_liabilities", i)), F2)
    g.helper("z_x5", "X5 = revenue / assets", lambda i: div(R("revenue", i), R("total_assets", i)), F2)
    zf = g.ratio("z", "Altman Z-Score",
                 lambda i: f'=IFERROR(1.2*{S("z_x1", i)}+1.4*{S("z_x2", i)}+3.3*{S("z_x3", i)}+0.6*{S("z_x4", i)}+1.0*{S("z_x5", i)},"")',
                 F2, ("bandc", 1.81, 2.99, ("Distress", "Grey", "Safe")), total=True, heat=True)
    g.note("Z > 2.99 = safe zone · 1.81–2.99 = grey zone · < 1.81 = distress zone.")
    g.blank()

    # ---------- Piotroski F-Score ----------
    g.section("Piotroski F-Score  (fundamental strength, 0–9)")
    g.helper("p_roa", "ROA = net income / assets", lambda i: div(R("net_income", i), R("total_assets", i)), F2)
    g.helper("p_cr", "Current ratio", lambda i: div(R("current_assets", i), R("current_liabilities", i)), F2)
    g.helper("p_gm", "Gross margin", lambda i: div(R("gross_profit", i), R("revenue", i)), F2)
    g.helper("p_ato", "Asset turnover", lambda i: div(R("revenue", i), R("total_assets", i)), F2)
    g.helper("p_lev", "LT debt / assets", lambda i: div(R("long_term_debt", i), R("total_assets", i)), F2)
    sig = [
        ("p_s1", "1. ROA > 0", lambda i: f"=({R('net_income', i)}>0)*1"),
        ("p_s2", "2. Operating cash flow > 0", lambda i: f"=({R('operating_cash_flow', i)}>0)*1"),
        ("p_s3", "3. ROA improved", lambda i: f"=({S('p_roa', i)}>{S('p_roa', i-1)})*1"),
        ("p_s4", "4. CFO > net income (accruals)", lambda i: f"=({R('operating_cash_flow', i)}>{R('net_income', i)})*1"),
        ("p_s5", "5. Lower leverage", lambda i: f"=({S('p_lev', i)}<{S('p_lev', i-1)})*1"),
        ("p_s6", "6. Higher current ratio", lambda i: f"=({S('p_cr', i)}>{S('p_cr', i-1)})*1"),
        ("p_s7", "7. No new shares", lambda i: f"=({R('shares_outstanding', i)}<={R('shares_outstanding', i-1)})*1"),
        ("p_s8", "8. Higher gross margin", lambda i: f"=({S('p_gm', i)}>{S('p_gm', i-1)})*1"),
        ("p_s9", "9. Higher asset turnover", lambda i: f"=({S('p_ato', i)}>{S('p_ato', i-1)})*1"),
    ]
    for key, label, fn in sig:
        g.helper(key, label, fn, Fmt.INT, start=1)
    g.ratio("f", "Piotroski F-Score (/9)",
            lambda i: "=SUM(" + ",".join(S(k, i) for k, _, _ in sig) + ")",
            Fmt.INT, ("bandc", 3, 7, ("Weak", "Average", "Strong")), total=True, start=1, heat=True)
    g.blank()

    # ---------- Beneish M-Score ----------
    g.section("Beneish M-Score  (earnings-manipulation risk)")
    g.helper("m_dsri", "DSRI (receivables/sales index)",
             lambda i: f'=IFERROR(({R("receivables", i)}/{R("revenue", i)})/({R("receivables", i-1)}/{R("revenue", i-1)}),"")', F2, start=1)
    g.helper("m_gmi", "GMI (gross-margin index)",
             lambda i: f'=IFERROR(({R("gross_profit", i-1)}/{R("revenue", i-1)})/({R("gross_profit", i)}/{R("revenue", i)}),"")', F2, start=1)
    g.helper("m_aqi", "AQI (asset-quality index)",
             lambda i: f'=IFERROR((1-({R("current_assets", i)}+{R("ppe", i)})/{R("total_assets", i)})/(1-({R("current_assets", i-1)}+{R("ppe", i-1)})/{R("total_assets", i-1)}),"")', F2, start=1)
    g.helper("m_sgi", "SGI (sales-growth index)",
             lambda i: f'=IFERROR({R("revenue", i)}/{R("revenue", i-1)},"")', F2, start=1)
    g.helper("m_depi", "DEPI (depreciation index)",
             lambda i: f'=IFERROR(({R("depreciation", i-1)}/({R("depreciation", i-1)}+{R("ppe", i-1)}))/({R("depreciation", i)}/({R("depreciation", i)}+{R("ppe", i)})),"")', F2, start=1)
    g.helper("m_sgai", "SGAI (SG&A index)",
             lambda i: f'=IFERROR(({R("opex", i)}/{R("revenue", i)})/({R("opex", i-1)}/{R("revenue", i-1)}),"")', F2, start=1)
    g.helper("m_lvgi", "LVGI (leverage index)",
             lambda i: f'=IFERROR(({R("total_liabilities", i)}/{R("total_assets", i)})/({R("total_liabilities", i-1)}/{R("total_assets", i-1)}),"")', F2, start=1)
    g.helper("m_tata", "TATA (total accruals / assets)",
             lambda i: f'=IFERROR(({R("net_income", i)}-{R("operating_cash_flow", i)})/{R("total_assets", i)},"")', F2, start=1)
    g.ratio("m", "Beneish M-Score",
            lambda i: (f'=IFERROR(-4.84+0.92*{S("m_dsri", i)}+0.528*{S("m_gmi", i)}+0.404*{S("m_aqi", i)}'
                       f'+0.892*{S("m_sgi", i)}+0.115*{S("m_depi", i)}-0.172*{S("m_sgai", i)}'
                       f'+4.679*{S("m_tata", i)}-0.327*{S("m_lvgi", i)},"")'),
            F2, ("bandc", -2.22, -1.78, ("Low Risk", "Watch", "Manipulation")), total=True, start=1, heat=True, reverse=True)
    g.note("M < −2.22 = unlikely manipulator · −2.22 to −1.78 = watch · > −1.78 = elevated risk.")
    g.blank()

    # ---------- ROIC vs WACC / economic profit ----------
    g.section("Value Creation  (ROIC vs WACC)")
    wacc = ctx.refs.ref("coc.wacc")
    g.ratio("roic", "ROIC", lambda i: div(R("nopat", i), R("avg_invested_capital", i)), PCT, None, start=1)
    g.ratio("wacc", "WACC", lambda i: f"={wacc}", PCT, None, arrow=False, heat=False)
    sp = g.ratio("spread", "ROIC − WACC spread", lambda i: f'=IFERROR({S("roic", i)}-{wacc},"")', PCT,
                 ("bandc", 0, 0.03, ("Value-destroying", "Roughly neutral", "Value-creating")), start=1, total=True)
    g.ratio("econ_profit", "Economic profit = spread × invested capital",
            lambda i: f'=IFERROR(({S("roic", i)}-{wacc})*{R("avg_invested_capital", i)},"")', MONEY, None, start=1)
    g.blank()

    g.section("Automated Observations")
    g.commentary(sentence(
        q("» Altman Z of "), text(S("z", li), "0.0"), q(" places the company in the "),
        ctx.refs.ref("qual.z.read"), q(" zone; Piotroski F is "), text(S("f", li), "0"),
        q("/9 ("), ctx.refs.ref("qual.f.read"), q(").")))
    g.commentary(sentence(
        q("» Beneish M of "), text(S("m", li), "0.00"), q(" implies "),
        ctx.refs.ref("qual.m.read"), q(" for earnings manipulation.")))
    g.commentary(sentence(
        q("» ROIC exceeds WACC by "), text(S("spread", li), "0.0%"), q(", generating "),
        text(S("econ_profit", li), "#,##0"), q(" of economic profit — "), ctx.refs.ref("qual.spread.read"), q(".")))

    g.chart(zf, "Altman Z & Piotroski F", zf, zf, height=7)
    g.chart(sp, "ROIC vs WACC spread", sp, sp, height=7)
    g.finalize()
    return sh
