#!/usr/bin/env python3
"""
Command-line entry point for the Financial Ratio Analysis workbook.

    python build_ratios.py                          # -> examples/ratio_analysis.xlsx
    python build_ratios.py -o my.xlsx
    python build_ratios.py --blank -o template.xlsx  # empty data-entry template
"""

from __future__ import annotations

import argparse
import sys

from ratios.sample_data import build_sample, empty_like_sample
from ratios.workbook import build_workbook


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build the financial ratio analysis workbook.")
    p.add_argument("-o", "--output", default="examples/ratio_analysis.xlsx")
    p.add_argument("--blank", action="store_true", help="generate a blank input template")
    args = p.parse_args(argv)
    data = empty_like_sample() if args.blank else build_sample()
    path = build_workbook(args.output, data)
    print(f"Workbook written to: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
