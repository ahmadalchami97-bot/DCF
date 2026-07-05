"""Orchestrator for the Government Bond Analyzer workbook."""

from __future__ import annotations

import importlib

from openpyxl import Workbook

from bond.config import Palette
from bond.style import apply as _styler
from dcf.utils import Refs, Sheet
from .common import Context
from .config import SHEET_ORDER
from .sample_data import build_sample

BUILD_ORDER = [
    "Inputs", "Price & Yield", "Cash Flows", "Valuation Summary", "Duration & DV01",
    "Rate Shock", "Yield Curve", "Investment Attractiveness", "Recommendation",
    "Explanations", "Quality Check", "Limitations",
]
_MODULE = {
    "Inputs": "inputs", "Price & Yield": "price_yield", "Cash Flows": "cashflows",
    "Valuation Summary": "valuation", "Duration & DV01": "duration", "Rate Shock": "rate_shock",
    "Yield Curve": "yield_curve", "Investment Attractiveness": "attractiveness",
    "Recommendation": "recommendation", "Explanations": "explanations",
    "Quality Check": "quality_check", "Limitations": "limitations",
}
_TABS = {"Inputs": "0000FF", "Price & Yield": "1F7A3D", "Cash Flows": "2E5984",
         "Valuation Summary": "1F7A3D", "Duration & DV01": "2E5984", "Rate Shock": "C0641F",
         "Yield Curve": "2E5984", "Investment Attractiveness": "1F3A5F", "Recommendation": "1F3A5F",
         "Explanations": "6B7986", "Quality Check": "C00000", "Limitations": "6B7986"}


def assemble(data: dict | None = None):
    data = data or build_sample()
    refs = Refs()
    wb = Workbook()
    wb.remove(wb.active)
    ctx = Context(data=data, refs=refs)
    for name in SHEET_ORDER:
        ctx.sheets[name] = Sheet(wb.create_sheet(title=name), refs, styler=_styler)
    for name in BUILD_ORDER:
        importlib.import_module(f".sheets.{_MODULE[name]}", package="govbond").build(ctx.sheets[name], ctx)
    wb._sheets.sort(key=lambda ws: SHEET_ORDER.index(ws.title))
    wb.active = SHEET_ORDER.index("Inputs")
    _polish(wb, data)
    return wb, ctx


def build_workbook(output_path: str, data: dict | None = None) -> str:
    wb, _ = assemble(data)
    wb.save(output_path)
    return output_path


def _polish(wb, data):
    from openpyxl.worksheet.properties import PageSetupProperties
    from .config import APP_NAME, APP_VERSION
    for ws in wb.worksheets:
        ws.sheet_properties.tabColor = _TABS.get(ws.title, Palette.HEADER)
        ws.sheet_view.showGridLines = False
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
        ws.oddFooter.right.text = "&A  -  page &P of &N"
    wb.properties.title = "Government Bond Analyzer"
    wb.properties.creator = f"{APP_NAME} v{APP_VERSION}"
