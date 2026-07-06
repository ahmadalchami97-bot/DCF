"""Orchestrator for the Macro Market Intelligence System (core engine)."""

from __future__ import annotations

import importlib

from openpyxl import Workbook

from bond.config import Palette
from bond.style import apply as _styler
from dcf.utils import Refs, Sheet
from .common import Context
from .config import APP_NAME, APP_VERSION, SHEET_ORDER
from .data import build_sample

BUILD_ORDER = list(SHEET_ORDER)

_MODULE = {
    "Cover": "cover", "Settings": "settings", "Impact Library": "impact_library",
    "Data Tracker": "data_tracker", "Surprise Engine": "surprise_engine", "Fed Tracker": "fed_tracker",
}
_TABS = {
    "Cover": "6B7986", "Settings": "6B7986", "Impact Library": "2E5984",
    "Data Tracker": "0000FF", "Surprise Engine": "1F7A3D", "Fed Tracker": "1F3A5F",
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
        importlib.import_module(f".sheets.{_MODULE[name]}", package="macro").build(ctx.sheets[name], ctx)
    wb._sheets.sort(key=lambda ws: SHEET_ORDER.index(ws.title))
    wb.active = SHEET_ORDER.index("Cover")
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
