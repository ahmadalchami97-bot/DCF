"""Orchestrator for the US Treasury Bond Analyzer workbook."""

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
    "Bond Terms", "Price & Yield", "Cash Flows", "Duration & Convexity", "Rate Shock",
    "Yield Curve", "Risk Summary", "Recommendation", "Formula Explanations", "Cover",
    "Audit", "Limitations",
]
_MODULE = {
    "Cover": "cover", "Bond Terms": "terms", "Cash Flows": "cashflows", "Price & Yield": "price_yield",
    "Duration & Convexity": "duration", "Rate Shock": "rate_shock", "Yield Curve": "yield_curve",
    "Risk Summary": "risk", "Recommendation": "recommendation", "Formula Explanations": "formulas_guide",
    "Audit": "audit", "Limitations": "limitations",
}
_TABS = {"Cover": "404040", "Bond Terms": "0000FF", "Cash Flows": "2E5984", "Price & Yield": "1F7A3D",
         "Duration & Convexity": "2E5984", "Rate Shock": "C0641F", "Yield Curve": "2E5984",
         "Risk Summary": "9C6500", "Recommendation": "1F3A5F", "Formula Explanations": "6B7986",
         "Audit": "C00000", "Limitations": "6B7986"}


def assemble(data: dict | None = None):
    data = data or build_sample()
    refs = Refs()
    wb = Workbook()
    wb.remove(wb.active)
    ctx = Context(data=data, refs=refs)
    for name in SHEET_ORDER:
        ctx.sheets[name] = Sheet(wb.create_sheet(title=name), refs, styler=_styler)
    for name in BUILD_ORDER:
        importlib.import_module(f".sheets.{_MODULE[name]}", package="ustreasury").build(ctx.sheets[name], ctx)
    wb._sheets.sort(key=lambda ws: SHEET_ORDER.index(ws.title))
    wb.active = SHEET_ORDER.index("Cover")
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
    wb.properties.title = "US Treasury Bond Analyzer"
    wb.properties.creator = f"{APP_NAME} v{APP_VERSION}"
