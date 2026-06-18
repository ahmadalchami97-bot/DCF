"""
Workbook orchestrator.

Creates the sheets in *display* order but builds them in *dependency* order so
that whenever one sheet's formula references another sheet's cell, the target
cell is already registered in the cross-sheet :class:`~dcf.utils.Refs` registry.
"""

from __future__ import annotations

import importlib

from openpyxl import Workbook

from .config import SHEET_ORDER
from .sample_data import build_sample
from .sheets.common import Context
from .utils import Refs, Sheet

# Display order is config.SHEET_ORDER. Build order resolves dependencies:
# Inputs feeds everything; Historical feeds Assumptions; WACC + Assumptions feed
# Forecast; Forecast + WACC feed DCF; DCF feeds Sensitivity/Scenario; everything
# feeds Checks/Dashboard/Conclusion; Cover links to the Dashboard last.
BUILD_ORDER = [
    "Inputs",
    "Historical",
    "WACC",
    "Assumptions",
    "Forecast",
    "DCF",
    "Sensitivity",
    "Scenario",
    "Checks",
    "Dashboard",
    "Conclusion",
    "Cover",
]

_MODULE = {
    "Cover": "cover",
    "Inputs": "inputs",
    "Historical": "historical",
    "Assumptions": "assumptions",
    "WACC": "wacc",
    "Forecast": "forecast",
    "DCF": "dcf",
    "Sensitivity": "sensitivity",
    "Scenario": "scenario",
    "Checks": "checks",
    "Dashboard": "dashboard",
    "Conclusion": "conclusion",
}


def assemble(data: dict | None = None):
    """Build the workbook in memory and return ``(wb, ctx)`` (used by tests)."""
    data = data or build_sample()
    refs = Refs()
    wb = Workbook()
    wb.remove(wb.active)  # drop default sheet

    ctx = Context(data=data, refs=refs)

    # Create all sheets up front in display order, so cross-references resolve
    # regardless of build order.
    for name in SHEET_ORDER:
        ws = wb.create_sheet(title=name)
        ctx.sheets[name] = Sheet(ws, refs)

    # Build in dependency order.
    for name in BUILD_ORDER:
        module = importlib.import_module(f".sheets.{_MODULE[name]}", package="dcf")
        module.build(ctx.sheets[name], ctx)

    # Reorder to display order (be defensive).
    wb._sheets.sort(key=lambda ws: SHEET_ORDER.index(ws.title))
    wb.active = SHEET_ORDER.index("Dashboard")
    _polish(wb)
    _set_doc_properties(wb, data)
    return wb, ctx


# Tab colours group the sheets by role (structure / input / output / check).
_TAB_COLORS = {
    "Cover": "152A45", "Inputs": "C9A227", "Historical": "2E5984",
    "Assumptions": "2E5984", "WACC": "2E5984", "Forecast": "2E5984", "DCF": "1F3A5F",
    "Sensitivity": "4A789C", "Scenario": "4A789C", "Checks": "9C6500",
    "Dashboard": "1F7A3D", "Conclusion": "1F7A3D",
}


def _polish(wb):
    """Cosmetic finishing: tab colours and print/page setup."""
    from openpyxl.worksheet.properties import PageSetupProperties

    for ws in wb.worksheets:
        ws.sheet_properties.tabColor = _TAB_COLORS.get(ws.title)
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
        ws.print_options.horizontalCentered = True
        ws.sheet_view.zoomScale = 100
        ws.sheet_view.showGridLines = False
        ws.oddFooter.right.text = "&A  ·  page &P of &N"
        ws.oddFooter.left.text = "Company Analysis Engine"


def build_workbook(output_path: str, data: dict | None = None) -> str:
    wb, _ = assemble(data)
    wb.save(output_path)
    return output_path


def _set_doc_properties(wb, data):
    from .config import APP_NAME, APP_VERSION

    props = wb.properties
    props.title = f"{data['meta'].get('name','Company')} — Analysis Pack"
    props.creator = APP_NAME
    props.description = f"{APP_NAME} v{APP_VERSION}"
    props.keywords = "DCF, valuation, financial analysis"
