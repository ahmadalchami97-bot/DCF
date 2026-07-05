"""Orchestrator for the Government Bond Course & Calculator workbook."""

from __future__ import annotations

import importlib

from openpyxl import Workbook

from bond.config import Palette
from bond.style import apply as _styler
from dcf.utils import Refs, Sheet
from .common import Context
from .config import APP_NAME, APP_VERSION, SHEET_ORDER
from .sample_data import build_sample

# Every figure is a live formula referencing named ranges, so build order does
# not affect correctness (names resolve at Excel calc time). We build in reading
# order for clarity.
BUILD_ORDER = list(SHEET_ORDER)

_MODULE = {
    "Start Here": "start_here", "Inputs": "inputs", "Cash Flows": "cashflows",
    "Price Basics": "price_basics", "Yield Basics": "yield_basics", "Price & Yield": "price_yield",
    "Duration": "duration", "DV01": "dv01", "Convexity": "convexity", "Rate Shock": "rate_shock",
    "Yield Curve": "yield_curve", "Valuation Summary": "valuation", "Is It Attractive": "attractiveness",
    "Recommendation": "recommendation", "Glossary": "glossary", "Formula Explanations": "formulas_guide",
    "Quality Check": "quality_check", "Limitations": "limitations",
}

_TABS = {
    "Start Here": "6B7986", "Inputs": "0000FF", "Cash Flows": "2E5984", "Price Basics": "1F7A3D",
    "Yield Basics": "1F7A3D", "Price & Yield": "1F7A3D", "Duration": "2E5984", "DV01": "2E5984",
    "Convexity": "2E5984", "Rate Shock": "C0641F", "Yield Curve": "2E5984", "Valuation Summary": "1F7A3D",
    "Is It Attractive": "1F3A5F", "Recommendation": "1F3A5F", "Glossary": "6B7986",
    "Formula Explanations": "6B7986", "Quality Check": "C00000", "Limitations": "6B7986",
}


def assemble(data: dict | None = None):
    data = data or build_sample()
    refs = Refs()
    wb = Workbook()
    wb.remove(wb.active)
    ctx = Context(data=data, refs=refs)
    for name in SHEET_ORDER:
        ctx.sheets[name] = Sheet(wb.create_sheet(title=name), refs, styler=_styler)
    for name in BUILD_ORDER:
        importlib.import_module(f".sheets.{_MODULE[name]}", package="bondcourse").build(ctx.sheets[name], ctx)
    wb._sheets.sort(key=lambda ws: SHEET_ORDER.index(ws.title))
    wb.active = SHEET_ORDER.index("Start Here")
    _polish(wb)
    return wb, ctx


def build_workbook(output_path: str, data: dict | None = None) -> str:
    wb, _ = assemble(data)
    wb.save(output_path)
    return output_path


def _polish(wb):
    from openpyxl.worksheet.properties import PageSetupProperties
    for ws in wb.worksheets:
        ws.sheet_properties.tabColor = _TABS.get(ws.title, Palette.HEADER)
        ws.sheet_view.showGridLines = False
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
        ws.oddFooter.right.text = "&A  -  page &P of &N"
    wb.properties.title = APP_NAME
    wb.properties.creator = f"{APP_NAME} v{APP_VERSION}"
