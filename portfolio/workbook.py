"""Orchestrator for the Portfolio Allocation Optimizer workbook."""

from __future__ import annotations

import importlib

from openpyxl import Workbook

from dcf.utils import Refs, Sheet
from .common import Context
from .config import Palette, SHEET_ORDER
from .sample_data import build_sample
from .style import apply as _styler

# Build in dependency order (Inputs -> Output -> Risk -> Allocation -> ...),
# even though sheets are displayed in reading order.
BUILD_ORDER = [
    "Scenario Inputs", "Scenario Output", "Risk & Return", "Allocation",
    "Rebalancing", "Dashboard", "Overview", "Formula Guide",
]
_MODULE = {
    "Overview": "overview", "Scenario Inputs": "scenario_inputs",
    "Scenario Output": "scenario_output", "Risk & Return": "risk_return",
    "Allocation": "allocation", "Rebalancing": "rebalancing",
    "Dashboard": "dashboard", "Formula Guide": "formula_guide",
}
_TABS = {"Overview": "404040", "Scenario Inputs": "0000FF", "Scenario Output": "1F4E79",
         "Risk & Return": "2E6CA4", "Allocation": "1F7A3D", "Rebalancing": "C0641F",
         "Dashboard": "12324F", "Formula Guide": "6B7886"}


def assemble(data: dict | None = None):
    data = data or build_sample()
    refs = Refs()
    wb = Workbook()
    wb.remove(wb.active)
    ctx = Context(data=data, refs=refs)
    for name in SHEET_ORDER:
        ctx.sheets[name] = Sheet(wb.create_sheet(title=name), refs, styler=_styler)
    for name in BUILD_ORDER:
        importlib.import_module(f".sheets.{_MODULE[name]}", package="portfolio").build(
            ctx.sheets[name], ctx)
    wb._sheets.sort(key=lambda ws: SHEET_ORDER.index(ws.title))
    wb.active = SHEET_ORDER.index("Overview")
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
        ws.sheet_properties.tabColor = _TABS.get(ws.title, Palette.SUBHEADER)
        ws.sheet_view.showGridLines = False
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
        ws.oddFooter.right.text = "&A  -  page &P of &N"
    wb.properties.title = "Portfolio Allocation Optimizer"
    wb.properties.creator = f"{APP_NAME} v{APP_VERSION}"
