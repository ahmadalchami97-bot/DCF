"""
Configuration for the Financial Ratio Analysis workbook.

Holds the visual language (institutional palette + the mandated 4-colour cell
scheme), the classification thresholds that drive the traffic-light reads, and
the static content for the Ratio Interpretation Guide. No analysis logic lives
here -- only constants -- so every threshold and label rule is auditable in one
place.
"""

from __future__ import annotations

APP_NAME = "Institutional Financial Ratio Analysis"
APP_VERSION = "1.0"

# Years of data the workbook holds.
HIST_YEARS = 10
FCST_YEARS = 5

SHEET_ORDER = [
    "Home", "Dashboard", "Inputs", "Common Size", "Profitability", "Liquidity",
    "Solvency", "Efficiency", "Growth", "Valuation", "Capital Allocation",
    "Quality", "Benchmarking", "Guide", "Quality Control",
]


class Palette:
    # institutional navy/slate scheme
    TITLE = "0F2942"
    HEADER = "1B3A5B"
    SUBHEADER = "2E5A88"
    SECTION = "44719C"
    BAND = "EAF0F6"
    PANEL = "F5F8FB"
    GRID = "D5DEE8"
    RULE = "AEBECD"
    TEXT = "1A2632"
    MUTED = "6A7886"
    WHITE = "FFFFFF"

    # mandated cell-type scheme
    INPUT_FILL = "FFF2CC"      # light yellow  -> user editable
    INPUT_FONT = "7F6000"
    FORMULA_FILL = "DDEBF7"    # light blue    -> protected formula / helper
    FORMULA_FONT = "1A2632"
    OUTPUT_FILL = "E2EFDA"     # light green   -> read-only result
    OUTPUT_FONT = "234D20"
    ERROR_FILL = "F8D2D2"      # light red     -> error / flag
    ERROR_FONT = "9C1A1A"

    # traffic lights (classification cells)
    GOOD = "1E7B34"
    GOOD_FILL = "D4EDDA"
    WARN = "8A6100"
    WARN_FILL = "FFF1C2"
    BAD = "9C1A1A"
    BAD_FILL = "F8D2D2"
    NEUTRAL = "5A6B7B"
    NEUTRAL_FILL = "ECEFF2"
    ACCENT = "C9A227"


# Sentiment vocabulary for conditional colouring of classification text.
GOOD_WORDS = ["Strong", "Improving", "Low Risk", "Excellent", "Healthy", "Safe",
              "Undervalued", "Value-creating", "Expanding", "Accelerating",
              "High", "Best-in-Class", "Above", "Robust", "PASS", "OK", "Conservative",
              "Reducing", "Accretive", "Cheap", "Rising", "Disciplined"]
WARN_WORDS = ["Moderate", "Stable", "Average", "Adequate", "Watch", "Grey",
              "Fair", "Neutral", "In-line", "Flat", "REVIEW", "Caution", "Decelerating"]
BAD_WORDS = ["Weak", "Deteriorating", "High Risk", "Poor", "Distress", "Overvalued",
             "Value-destroying", "Compressing", "Low", "Worst", "Below", "FAIL",
             "Elevated", "Stretched", "Manipulation", "Negative", "Diluting",
             "Dilutive", "Expensive", "Falling"]


# --- classification threshold sets (ascending bands -> 3 labels) -----------
# Each entry: (low_cut, high_cut, (label_below, label_mid, label_above))
# Used by the CHOOSE(1+(v>=lo)+(v>=hi), ...) single-formula classifier.
BANDS = {
    "current_ratio": (1.0, 2.0, ("Weak", "Adequate", "Strong")),
    "quick_ratio": (0.8, 1.2, ("Weak", "Adequate", "Strong")),
    "cash_ratio": (0.2, 0.5, ("Weak", "Adequate", "Strong")),
    "roe": (0.08, 0.15, ("Weak", "Average", "Strong")),
    "roa": (0.03, 0.07, ("Weak", "Average", "Strong")),
    "roic": (0.08, 0.12, ("Weak", "Average", "Strong")),
    "roce": (0.08, 0.12, ("Weak", "Average", "Strong")),
    "gross_margin": (0.20, 0.40, ("Low", "Average", "High")),
    "net_margin": (0.05, 0.12, ("Low", "Average", "High")),
    "operating_margin": (0.08, 0.18, ("Low", "Average", "High")),
    "fcf_margin": (0.03, 0.10, ("Weak", "Average", "Strong")),
    # leverage / solvency: higher is worse -> reversed labels
    "debt_to_equity": (0.5, 1.5, ("Low Risk", "Moderate Risk", "High Risk")),
    "debt_to_assets": (0.3, 0.6, ("Low Risk", "Moderate Risk", "High Risk")),
    "net_debt_ebitda": (1.0, 3.0, ("Low Risk", "Moderate Risk", "High Risk")),
    "interest_coverage": (3.0, 6.0, ("High Risk", "Moderate Risk", "Low Risk")),
    "debt_to_capital": (0.3, 0.6, ("Low Risk", "Moderate Risk", "High Risk")),
}

# Trend band: relative move of latest vs trailing average that counts as a change.
TREND_BAND = 0.05
# Growth-rate change (pp) that counts as accelerating/decelerating.
GROWTH_BAND_PP = 0.02

# Score-sheet thresholds.
ALTMAN_DISTRESS = 1.81
ALTMAN_SAFE = 2.99
PIOTROSKI_WEAK = 3
PIOTROSKI_STRONG = 7
BENEISH_FLAG = -1.78   # M above this => possible manipulation


# --- Ratio Interpretation Guide content ------------------------------------
# (name, formula, what it measures, strong, average, weak, investment meaning)
GUIDE = [
    ("Gross Margin", "Gross Profit / Revenue",
     "Pricing power and production efficiency.", ">40%", "20–40%", "<20%",
     "High, stable gross margins signal a durable competitive advantage."),
    ("Operating Margin", "EBIT / Revenue",
     "Core profitability after operating costs.", ">18%", "8–18%", "<8%",
     "Expanding operating margin shows operating leverage and cost control."),
    ("Net Margin", "Net Income / Revenue",
     "Bottom-line profitability.", ">12%", "5–12%", "<5%",
     "Persistent net margins indicate quality earnings."),
    ("ROE", "Net Income / Average Equity",
     "Return generated on shareholders' capital.", ">15%", "8–15%", "<8%",
     "High ROE not driven by leverage is a hallmark of quality."),
    ("ROA", "Net Income / Average Assets",
     "Efficiency of the asset base.", ">7%", "3–7%", "<3%",
     "Rising ROA shows assets are deployed more productively."),
    ("ROIC", "NOPAT / Invested Capital",
     "Return on all invested capital.", ">12%", "8–12%", "<8%",
     "ROIC above WACC is the clearest sign of value creation."),
    ("ROCE", "EBIT / Capital Employed",
     "Pre-tax return on long-term capital.", ">12%", "8–12%", "<8%",
     "Consistent ROCE indicates a capital-efficient business."),
    ("Current Ratio", "Current Assets / Current Liabilities",
     "Short-term liquidity.", ">2.0x", "1.0–2.0x", "<1.0x",
     "Below 1.0x can signal liquidity stress; very high may be inefficient."),
    ("Quick Ratio", "(Current Assets − Inventory) / Current Liabilities",
     "Liquidity excluding inventory.", ">1.2x", "0.8–1.2x", "<0.8x",
     "A stricter liquidity test for inventory-heavy firms."),
    ("Cash Ratio", "(Cash + Equivalents) / Current Liabilities",
     "Most conservative liquidity test.", ">0.5x", "0.2–0.5x", "<0.2x",
     "Shows ability to cover current liabilities from cash alone."),
    ("Debt-to-Equity", "Total Debt / Equity",
     "Reliance on debt vs equity.", "<0.5x", "0.5–1.5x", ">1.5x",
     "Higher leverage raises returns but also financial risk."),
    ("Net Debt / EBITDA", "(Debt − Cash) / EBITDA",
     "Years of EBITDA to repay net debt.", "<1.0x", "1.0–3.0x", ">3.0x",
     "A key credit metric; >3–4x is often considered stretched."),
    ("Interest Coverage", "EBIT / Interest Expense",
     "Ability to service interest.", ">6x", "3–6x", "<3x",
     "Low coverage signals vulnerability to earnings shocks."),
    ("Asset Turnover", "Revenue / Average Assets",
     "Sales generated per unit of assets.", ">1.0x", "0.5–1.0x", "<0.5x",
     "Higher turnover means a more capital-light model."),
    ("Inventory Turnover", "COGS / Average Inventory",
     "How fast inventory is sold.", ">8x", "4–8x", "<4x",
     "Falling turnover can flag obsolescence or weak demand."),
    ("Receivable Turnover", "Revenue / Average Receivables",
     "How fast receivables are collected.", ">10x", "6–10x", "<6x",
     "Declining turnover may indicate collection or channel problems."),
    ("Cash Conversion Cycle", "DSO + DIO − DPO",
     "Days cash is tied up in operations.", "<30 days", "30–90 days", ">90 days",
     "A shorter cycle frees up working capital and cash."),
    ("Revenue Growth", "Revenue_t / Revenue_t-1 − 1",
     "Top-line momentum.", ">10%", "3–10%", "<3%",
     "Sustained, profitable growth compounds shareholder value."),
    ("FCF Margin", "Free Cash Flow / Revenue",
     "Cash conversion of sales.", ">10%", "3–10%", "<3%",
     "Strong FCF funds dividends, buybacks and reinvestment."),
    ("P/E", "Price / EPS",
     "Price paid per unit of earnings.", "context", "context", "context",
     "Compare to growth (PEG) and history; not meaningful if earnings are low."),
    ("EV/EBITDA", "Enterprise Value / EBITDA",
     "Capital-structure-neutral valuation.", "context", "context", "context",
     "A core cross-company multiple; lower can mean cheaper, or lower quality."),
    ("P/B", "Price / Book Value per Share",
     "Price vs accounting net worth.", "context", "context", "context",
     "Most useful for asset-heavy or financial businesses."),
    ("FCF Yield", "Free Cash Flow / Market Cap",
     "Cash return relative to price.", ">6%", "3–6%", "<3%",
     "A high FCF yield can indicate an undervalued, cash-generative business."),
    ("Dividend Payout", "Dividends / Net Income",
     "Share of earnings paid out.", "context", "30–60%", ">100%",
     "Very high payout may be unsustainable; very low favours reinvestment."),
    ("Piotroski F-Score", "Sum of 9 fundamental signals (0–9)",
     "Fundamental strength & improvement.", "7–9", "4–6", "0–3",
     "A high F-Score flags improving, financially sound companies."),
    ("Altman Z-Score", "1.2X1+1.4X2+3.3X3+0.6X4+1.0X5",
     "Bankruptcy / distress risk.", ">2.99", "1.81–2.99", "<1.81",
     "Below 1.81 signals elevated distress risk."),
    ("Beneish M-Score", "8-variable earnings-manipulation model",
     "Likelihood of earnings manipulation.", "<−2.22", "−2.22 to −1.78", ">−1.78",
     "Above −1.78 flags a higher probability of manipulated earnings."),
    ("ROIC − WACC Spread", "ROIC − WACC",
     "Economic value creation.", ">3%", "0–3%", "<0%",
     "A positive spread means the firm earns above its cost of capital."),
]
