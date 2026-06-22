"""
Institutional Forecasting Engine.

A modular engine that generates a fully-formula-driven, auditable integrated
3-statement forecasting workbook (10y history + 10y forecast) with a
method/scenario engine, roll-forwards that reconcile without plugs, a forecast
bridge, diagnostics and sensitivity analysis. Reuses dcf/utils.py.
"""

from .config import APP_NAME, APP_VERSION

__all__ = ["APP_NAME", "APP_VERSION", "build"]
__version__ = APP_VERSION


def build(output_path: str, data: dict | None = None) -> str:
    from .workbook import build_workbook
    return build_workbook(output_path, data)
