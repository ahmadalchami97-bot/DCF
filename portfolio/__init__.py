"""
Portfolio Allocation Optimizer + Scenario Analysis.

A modular engine that generates a clean, professional, EXPLAINABLE Excel workbook
to help a non-quant investor understand their current allocation, the impact of a
market scenario, the risk/return trade-off, and recommended rebalancing actions.
Live formulas throughout (no values baked in by Python); no Solver, no VBA.
Reuses dcf/utils.py.
"""

from .config import APP_NAME, APP_VERSION

__all__ = ["APP_NAME", "APP_VERSION", "build"]
__version__ = APP_VERSION


def build(output_path: str, data: dict | None = None) -> str:
    from .workbook import build_workbook
    return build_workbook(output_path, data)
