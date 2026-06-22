"""Orchestrator for the Institutional Forecasting Engine workbook."""

from __future__ import annotations

import importlib

from openpyxl import Workbook

from dcf.utils import Refs, Sheet
from .common import Context
from .config import Palette, SHEET_ORDER
from .sample_data import build_sample
from .style import apply as _styler

# Dependency order: Historical defines the timeline + the actual inputs;
# Assumptions defines the drivers; the Forecast reads both; Bridge & Diagnostics
# read the Forecast; the Methodology is text; the Dashboard aggregates last.
BUILD_ORDER = [
    "Historical", "Assumptions", "Forecast", "Bridge",
    "Diagnostics", "Methodology", "Dashboard",
]
_MODULE = {
    "Dashboard": "dashboard", "Methodology": "methodology", "Historical": "historical",
    "Assumptions": "assumptions", "Forecast": "forecast", "Bridge": "bridge",
    "Diagnostics": "diagnostics",
}
_TABS = {"Dashboard": "404040", "Methodology": "5B7286", "Historical": "39506B",
         "Assumptions": "0000FF", "Forecast": "1F7A4D", "Bridge": "2E4A6B",
         "Diagnostics": "C00000"}


def assemble(data: dict | None = None):
    data = data or build_sample()
    refs = Refs()
    wb = Workbook()
    wb.remove(wb.active)
    ctx = Context(data=data, refs=refs)
    for name in SHEET_ORDER:
        ctx.sheets[name] = Sheet(wb.create_sheet(title=name), refs, styler=_styler)
    for name in BUILD_ORDER:
        importlib.import_module(f".sheets.{_MODULE[name]}", package="ife").build(
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
        ws.sheet_properties.tabColor = _TABS.get(ws.title, Palette.SUBHEADER)
        ws.sheet_view.showGridLines = False
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
        ws.oddFooter.right.text = "&A  ·  page &P of &N"
    from .config import APP_NAME, APP_VERSION
    wb.properties.title = f"{data['meta'].get('name','Company')} — Forecasting Engine"
    wb.properties.creator = f"{APP_NAME} v{APP_VERSION}"
