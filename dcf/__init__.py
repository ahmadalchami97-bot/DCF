"""
Investment-Grade Company Analysis Engine.

A modular Python package that generates a fully-formula-driven, auditable Excel
workbook for company analysis and DCF valuation. Logic is separated into:

    config / styles / utils / schema   -- infrastructure
    sample_data                        -- a worked, internally-consistent example
    sheets/*                           -- one module per workbook sheet
    workbook                           -- the orchestrator that wires it together

See README.md for architecture, the input->output map, and a usage guide.
"""

from .config import APP_NAME, APP_VERSION

__all__ = ["APP_NAME", "APP_VERSION", "build"]
__version__ = APP_VERSION


def build(output_path: str, data: dict | None = None) -> str:
    """Build the workbook to *output_path*. Uses the sample dataset if *data* is None."""
    from .workbook import build_workbook  # local import to keep package import light

    return build_workbook(output_path, data)
