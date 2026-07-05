"""
US Treasury Bond Analyzer.

Generates a clean, beginner-friendly Excel workbook that values and analyzes one
US Treasury security (fixed-coupon note/bond or zero-coupon bill): clean/dirty
price, accrued, YTM, current yield, duration, convexity, DV01, a rate-shock table,
yield-curve context, a risk checklist, a recommendation page and an independent
audit sheet. Live Excel formulas; no VBA. Reuses bond.bondmath and dcf/utils.py.
"""

from .config import APP_NAME, APP_VERSION

__all__ = ["APP_NAME", "APP_VERSION", "build"]
__version__ = APP_VERSION


def build(output_path: str, data: dict | None = None) -> str:
    from .workbook import build_workbook
    return build_workbook(output_path, data)
