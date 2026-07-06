#!/usr/bin/env python3
"""Entry point: build the Macro Market Intelligence System (core engine) workbook."""

from __future__ import annotations

import argparse
import sys

from macro.data import build_sample, empty_like_sample
from macro.workbook import build_workbook


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build the Macro Market Intelligence System (core) workbook.")
    p.add_argument("-o", "--output", default="examples/Macro Market Intelligence System.xlsx")
    p.add_argument("--blank", action="store_true", help="blank template (no sample releases/speeches)")
    args = p.parse_args(argv)
    data = empty_like_sample() if args.blank else build_sample()
    print("Workbook written to:", build_workbook(args.output, data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
