"""
Fixed-Rate Bond Analyzer.

Generates a clean, beginner-friendly but technically correct Excel workbook that
values and analyzes a single plain-vanilla fixed-rate bond (clean/dirty price,
accrued, YTM, duration, convexity, DV01, YTC, YTW), with an optional issuer
credit view, a risk checklist, a recommendation page and an independent audit
sheet. Live Excel formulas throughout; no VBA. Reuses dcf/utils.py.
"""

from .config import APP_NAME, APP_VERSION

__all__ = ["APP_NAME", "APP_VERSION", "build"]
__version__ = APP_VERSION


def build(output_path: str, data: dict | None = None) -> str:
    from .workbook import build_workbook
    return build_workbook(output_path, data)
