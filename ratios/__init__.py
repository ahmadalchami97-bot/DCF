"""
Institutional Financial Ratio Analysis workbook generator.

A modular engine that builds a 15-sheet, fully-formula-driven, auditable Excel
ratio-analysis workbook. Reuses the cross-sheet cell registry and styled Sheet
wrapper from :mod:`dcf.utils`; all ratio logic, styling and content live here.
"""

from .config import APP_NAME, APP_VERSION

__all__ = ["APP_NAME", "APP_VERSION", "build"]
__version__ = APP_VERSION


def build(output_path: str, data: dict | None = None) -> str:
    from .workbook import build_workbook
    return build_workbook(output_path, data)
