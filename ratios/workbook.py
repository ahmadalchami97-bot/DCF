"""Orchestrator for the ratio-analysis workbook."""

from __future__ import annotations

import importlib

from openpyxl import Workbook

from dcf.utils import Refs, Sheet
from .common import Context
from .config import Palette, SHEET_ORDER
from .sample_data import build_sample

# Built in dependency order: Home registers identity inputs; Inputs feeds every
# analysis sheet; the Dashboard and Quality Control aggregate, so they come last.
BUILD_ORDER = [
    "Home", "Inputs", "Common Size", "Profitability", "Liquidity", "Solvency",
    "Efficiency", "Growth", "Valuation", "Capital Allocation", "Quality",
    "Benchmarking", "Guide", "Quality Control", "Dashboard",
]

_MODULE = {
    "Home": "home", "Dashboard": "dashboard", "Inputs": "inputs",
    "Common Size": "common_size", "Profitability": "profitability",
    "Liquidity": "liquidity", "Solvency": "solvency", "Efficiency": "efficiency",
    "Growth": "growth", "Valuation": "valuation",
    "Capital Allocation": "capital_allocation", "Quality": "quality",
    "Benchmarking": "benchmarking", "Guide": "interpretation",
    "Quality Control": "quality_control",
}

_TAB_COLORS = {
    "Home": Palette.TITLE, "Dashboard": "1E7B34", "Inputs": "C9A227",
    "Guide": Palette.SECTION, "Quality Control": "9C1A1A",
}
_DEFAULT_TAB = Palette.SUBHEADER


def assemble(data: dict | None = None):
    data = data or build_sample()
    refs = Refs()
    wb = Workbook()
    wb.remove(wb.active)
    ctx = Context(data=data, refs=refs)
    for name in SHEET_ORDER:
        ctx.sheets[name] = Sheet(wb.create_sheet(title=name), refs)
    for name in BUILD_ORDER:
        importlib.import_module(f".sheets.{_MODULE[name]}", package="ratios").build(
            ctx.sheets[name], ctx)
    wb._sheets.sort(key=lambda ws: SHEET_ORDER.index(ws.title))
    wb.active = SHEET_ORDER.index("Dashboard")
    _polish(wb, data)
    return wb, ctx


def build_workbook(output_path: str, data: dict | None = None) -> str:
    wb, _ = assemble(data)
    wb.save(output_path)
    return output_path


def _polish(wb, data):
    from openpyxl.worksheet.properties import PageSetupProperties
    for ws in wb.worksheets:
        ws.sheet_properties.tabColor = _TAB_COLORS.get(ws.title, _DEFAULT_TAB)
        ws.sheet_view.showGridLines = False
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
        ws.oddFooter.right.text = "&A  ·  page &P of &N"
    from .config import APP_NAME, APP_VERSION
    wb.properties.title = f"{data['meta'].get('name','Company')} — Ratio Analysis"
    wb.properties.creator = f"{APP_NAME} v{APP_VERSION}"
