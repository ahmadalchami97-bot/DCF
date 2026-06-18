"""
Input schema -- the structural contract for the model's input layer.

This defines *what* an analyst can enter and how each line is treated:
  - ``input``    : a yellow cell the user fills (raw reported figure / driver)
  - ``subtotal`` : a black formula cell computed on the Inputs sheet from inputs

Downstream sheets reference these by the keys defined here, so this module is
the single source of truth for the model's vocabulary. Subtotal *formulas* are
not encoded here (they depend on cell layout); they are built in
``dcf/sheets/inputs.py`` keyed by the item ``key``.

Accounting conventions (documented on the Inputs sheet for the user):
  * COGS and SG&A are entered AS REPORTED (i.e. they already embed their share
    of depreciation & amortisation). Total D&A is entered ONCE, in the cash-flow
    block, and EBITDA is built as EBIT + D&A to avoid double counting.
  * Expenses / uses of cash are entered as POSITIVE numbers; the model applies
    the sign (e.g. capex, dividends and buybacks are positive amounts spent).
  * ``other_nonoperating`` and ``cf_*`` signed lines are entered as net cash
    impact (positive = inflow / income).
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import Fmt


@dataclass(frozen=True)
class Item:
    key: str
    label: str
    kind: str            # "input" | "subtotal"
    fmt: str = Fmt.MONEY
    required: bool = False
    note: str = ""
    indent: int = 0      # visual indent level for the label


@dataclass(frozen=True)
class Section:
    title: str
    items: tuple[Item, ...]


# --- Income statement -------------------------------------------------------
INCOME_STATEMENT = Section(
    "Income Statement",
    (
        Item("revenue", "Revenue / Net sales", "input", required=True),
        Item("cogs", "Cost of goods sold (incl. D&A)", "input", required=True),
        Item("gross_profit", "Gross profit", "subtotal"),
        Item("sga", "Selling, general & admin (SG&A)", "input"),
        Item("rd", "Research & development", "input"),
        Item("other_operating", "Other operating expense / (income)", "input"),
        Item("ebit", "EBIT (operating income)", "subtotal"),
        Item("da", "(+) Depreciation & amortisation", "subtotal",
             note="Linked from cash-flow block; added back to reach EBITDA."),
        Item("ebitda", "EBITDA", "subtotal"),
        Item("interest_expense", "Interest expense", "input"),
        Item("interest_income", "Interest & investment income", "input"),
        Item("other_nonoperating", "Other non-operating income / (expense)", "input"),
        Item("pretax_income", "Pre-tax income", "subtotal"),
        Item("tax_expense", "Income tax expense", "input"),
        Item("minority_interest", "Minority interest / (income)", "input"),
        Item("net_income", "Net income to shareholders", "subtotal"),
    ),
)

# --- Balance sheet ----------------------------------------------------------
BALANCE_SHEET = Section(
    "Balance Sheet",
    (
        Item("cash", "Cash & equivalents", "input"),
        Item("st_investments", "Short-term investments", "input"),
        Item("accounts_receivable", "Accounts receivable", "input"),
        Item("inventory", "Inventory", "input"),
        Item("other_current_assets", "Other current assets", "input"),
        Item("total_current_assets", "Total current assets", "subtotal"),
        Item("ppe_net", "Property, plant & equipment (net)", "input"),
        Item("goodwill_intangibles", "Goodwill & intangibles", "input"),
        Item("other_noncurrent_assets", "Other non-current assets", "input"),
        Item("total_noncurrent_assets", "Total non-current assets", "subtotal"),
        Item("total_assets", "TOTAL ASSETS", "subtotal"),
        Item("accounts_payable", "Accounts payable", "input"),
        Item("short_term_debt", "Short-term debt & current portion LTD", "input"),
        Item("other_current_liabilities", "Other current liabilities", "input"),
        Item("total_current_liabilities", "Total current liabilities", "subtotal"),
        Item("long_term_debt", "Long-term debt", "input"),
        Item("other_noncurrent_liabilities", "Other non-current liabilities", "input"),
        Item("total_noncurrent_liabilities", "Total non-current liabilities", "subtotal"),
        Item("total_liabilities", "TOTAL LIABILITIES", "subtotal"),
        Item("total_equity", "Total shareholders' equity", "input", required=True),
        Item("minority_equity", "Minority interest (equity)", "input"),
        Item("total_liab_equity", "TOTAL LIABILITIES & EQUITY", "subtotal"),
    ),
)

# --- Cash flow --------------------------------------------------------------
CASH_FLOW = Section(
    "Cash Flow Statement",
    (
        Item("cf_net_income", "Net income (per cash-flow statement)", "input"),
        Item("cf_da", "Depreciation & amortisation", "input",
             note="The single D&A figure; feeds EBITDA in the income statement."),
        Item("cf_wc_change", "Change in working capital (cash impact)", "input",
             note="Positive = cash released; negative = cash invested in WC."),
        Item("cf_other_operating", "Other non-cash / operating items", "input"),
        Item("cfo", "Cash flow from operations (CFO)", "subtotal"),
        Item("capex", "Capital expenditure", "input",
             note="Enter as a positive amount; the model subtracts it."),
        Item("acquisitions", "Acquisitions / (disposals), net", "input",
             note="Positive = cash spent on acquisitions."),
        Item("other_investing", "Other investing (cash impact)", "input"),
        Item("cfi", "Cash flow from investing (CFI)", "subtotal"),
        Item("debt_change", "Net debt issued / (repaid)", "input",
             note="Signed: positive = net borrowing."),
        Item("dividends_paid", "Dividends paid", "input",
             note="Enter as a positive amount returned to shareholders."),
        Item("buybacks", "Share buybacks (net)", "input",
             note="Enter as a positive amount; net of issuance."),
        Item("other_financing", "Other financing (cash impact)", "input"),
        Item("cff", "Cash flow from financing (CFF)", "subtotal"),
        Item("net_change_cash", "Net change in cash", "subtotal"),
    ),
)

# --- Per-share & shares -----------------------------------------------------
SHARE_DATA = Section(
    "Shares & Per-Share Data",
    (
        Item("shares_basic", "Weighted avg shares (basic, m)", "input", fmt=Fmt.INT),
        Item("shares_diluted", "Weighted avg shares (diluted, m)", "input", fmt=Fmt.INT),
        Item("eps_basic", "EPS (basic)", "subtotal", fmt=Fmt.PER_SHARE),
        Item("eps_diluted", "EPS (diluted)", "subtotal", fmt=Fmt.PER_SHARE),
        Item("dps", "Dividend per share", "subtotal", fmt=Fmt.PER_SHARE),
        Item("payout_ratio", "Dividend payout ratio", "subtotal", fmt=Fmt.PCT),
    ),
)

# --- Optional industry drivers ---------------------------------------------
# These are OPTIONAL. If populated, the forecast can build revenue bottom-up
# from volume x price; if blank, the model falls back to trend-based growth.
DRIVERS = Section(
    "Optional Drivers (volume / price)",
    (
        Item("driver_volume", "Volume (units, m)", "input", fmt=Fmt.FLOAT1,
             note="Optional. Units sold / delivered."),
        Item("driver_price", "Average selling price", "input", fmt=Fmt.PER_SHARE,
             note="Optional. Revenue per unit; volume x price should ~ revenue."),
        Item("driver_implied_rev", "Implied revenue (volume x price)", "subtotal",
             note="Cross-check: should approximate reported revenue."),
    ),
)

# Sections that carry per-period (time-series) data, in display order.
TIME_SERIES_SECTIONS = (
    INCOME_STATEMENT,
    BALANCE_SHEET,
    CASH_FLOW,
    SHARE_DATA,
    DRIVERS,
)


# --- Market / valuation reference inputs (single value, "latest") -----------
@dataclass(frozen=True)
class ScalarItem:
    key: str
    label: str
    kind: str
    fmt: str
    default: float | None
    source: str          # "input" | "fallback"
    note: str = ""


MARKET_INPUTS = (
    ScalarItem("mkt_share_price", "Current share price", "input", Fmt.PER_SHARE, None,
               "input", "Latest market price; leave blank if private/unknown."),
    ScalarItem("mkt_shares_out", "Shares outstanding (current, m)", "input", Fmt.INT, None,
               "input", "Current shares for market cap & per-share value."),
    ScalarItem("mkt_beta", "Equity beta", "input", Fmt.FLOAT2, 1.0,
               "fallback", "Levered beta vs market; fallback = 1.00."),
    ScalarItem("mkt_risk_free", "Risk-free rate", "input", Fmt.PCT, 0.04,
               "fallback", "Long-bond yield; fallback = 4.0%."),
    ScalarItem("mkt_erp", "Equity risk premium", "input", Fmt.PCT, 0.05,
               "fallback", "Mature-market ERP; fallback = 5.0%."),
    ScalarItem("mkt_pretax_kd", "Pre-tax cost of debt", "input", Fmt.PCT, 0.06,
               "fallback", "Marginal borrowing rate; fallback = 6.0%."),
    ScalarItem("mkt_tax_rate", "Marginal tax rate", "input", Fmt.PCT, 0.25,
               "fallback", "For after-tax cost of debt & NOPAT; fallback = 25%."),
)


def all_input_keys() -> list[str]:
    """Every time-series key that is a user input (used for missing-data checks)."""
    keys = []
    for sec in TIME_SERIES_SECTIONS:
        for it in sec.items:
            if it.kind == "input":
                keys.append(it.key)
    return keys
