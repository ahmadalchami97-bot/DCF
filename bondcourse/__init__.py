"""
Government Bond Course & Calculator.

A beginner-friendly Excel workbook that teaches government bonds from zero while
also working as a real calculation template. Eighteen sheets take a complete
beginner from "what is a bond?" through cash flows, clean/dirty price, yield,
duration/DV01/convexity, rate shocks and the yield curve, to a simple
attractiveness score and a manual Buy/Hold/Avoid call - each number explained in
plain English (what it means, why it matters, what the formula does, how to read
it, and an example).

Government bonds only (fixed-coupon notes/bonds and zero-coupon bills). Every
figure is a live Excel formula; no VBA, no hidden formulas. Reuses bond.bondmath
conventions and dcf/utils.py plumbing.
"""

from .config import APP_NAME, APP_VERSION

__all__ = ["APP_NAME", "APP_VERSION", "build"]
__version__ = APP_VERSION


def build(output_path: str, data: dict | None = None) -> str:
    from .workbook import build_workbook
    return build_workbook(output_path, data)
