"""
Institutional Forecasting Engine.

A modular engine that generates a transparent, fully-formula-driven, auditable
integrated 3-statement forecasting workbook. Historical figures are hard-coded
inputs; the forecast begins automatically the year after the last reported year;
each forecast line is driven by exactly one assumption; and the model reconciles
without a plug and without circular references. Reuses dcf/utils.py.
"""

from .config import APP_NAME, APP_VERSION

__all__ = ["APP_NAME", "APP_VERSION", "build"]
__version__ = APP_VERSION


def build(output_path: str, data: dict | None = None) -> str:
    from .workbook import build_workbook
    return build_workbook(output_path, data)
