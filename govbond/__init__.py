"""
Government Bond Analyzer.

Generates a clean, beginner-friendly Excel workbook that values and analyzes one
government bond (fixed-coupon note/bond or zero-coupon bill), with price<->yield
both ways, cash flows, duration/DV01/convexity, rate shocks, yield-curve context,
a simple investment-attractiveness score, a recommendation page, plain-English
explanations and an independent quality-check sheet. Live Excel formulas; no VBA.
Reuses bond.bondmath and dcf/utils.py.
"""

from .config import APP_NAME, APP_VERSION

__all__ = ["APP_NAME", "APP_VERSION", "build"]
__version__ = APP_VERSION


def build(output_path: str, data: dict | None = None) -> str:
    from .workbook import build_workbook
    return build_workbook(output_path, data)
