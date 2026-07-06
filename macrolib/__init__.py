"""
Macro Impact Library & Global Stress Index.

A deliberately simple, practical two-sheet Excel workbook:
  1. Macro Indicator Impact Library - a professional cheat sheet of ~63 macro,
     market and geopolitical indicators and how each usually moves USD, Treasuries,
     gold, oil, equities, EM and Kuwait/GCC.
  2. Global Stress / Fear Index - a formula-driven 0-100 composite (VIX, MOVE, DXY,
     gold, oil, S&P drawdown, credit spreads, 10Y shock, geopolitics) with a
     SUMPRODUCT score, Calm..Crisis classification and an auto-written summary.

No macros; formula-driven; yellow inputs vs grey calculated cells. Reuses
dcf/utils.py and the shared bond style.
"""

from .workbook import APP_NAME

__all__ = ["APP_NAME", "build"]


def build(output_path: str, data: dict | None = None) -> str:
    from .workbook import build_workbook
    return build_workbook(output_path, data)
