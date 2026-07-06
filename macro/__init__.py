"""
Macro Market Intelligence System (core engine, Phase 1-2).

A live-formula Excel workbook that logs macro data releases and scores them into
market signals: a Data Surprise Engine (surprise vs expectations, with per-
indicator polarity -> inflation/growth signal -> first-order asset arrows) and a
Fed hawkish/dovish composite score. Six sheets - Cover, Settings, Impact Library,
Data Tracker, Surprise Engine, Fed Tracker - built on the full 18-sheet design in
docs/MACRO_INTELLIGENCE_SYSTEM.md. No VBA; original-spec Excel functions only.
Reuses dcf/utils.py plumbing and the shared bond palette/formats.
"""

from .config import APP_NAME, APP_VERSION

__all__ = ["APP_NAME", "APP_VERSION", "build"]
__version__ = APP_VERSION


def build(output_path: str, data: dict | None = None) -> str:
    from .workbook import build_workbook
    return build_workbook(output_path, data)
