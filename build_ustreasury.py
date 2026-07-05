#!/usr/bin/env python3
"""Entry point: build the US Treasury Bond Analyzer workbook."""

from __future__ import annotations

import argparse
import sys

from ustreasury.sample_data import build_sample, empty_like_sample
from ustreasury.workbook import build_workbook


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build the US Treasury Bond Analyzer workbook.")
    p.add_argument("-o", "--output", default="examples/US Treasury Bond Analyzer.xlsx")
    p.add_argument("--blank", action="store_true", help="generate a blank template")
    args = p.parse_args(argv)
    data = empty_like_sample() if args.blank else build_sample()
    print("Workbook written to:", build_workbook(args.output, data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
