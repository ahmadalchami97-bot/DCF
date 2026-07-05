#!/usr/bin/env python3
"""Entry point: build the Government Bond Course & Calculator workbook."""

from __future__ import annotations

import argparse
import sys

from bondcourse.sample_data import build_sample, empty_like_sample
from bondcourse.workbook import build_workbook


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build the Government Bond Course & Calculator workbook.")
    p.add_argument("-o", "--output", default="examples/Government Bond Course & Calculator.xlsx")
    p.add_argument("--blank", action="store_true", help="generate a blank template (no sample bond)")
    args = p.parse_args(argv)
    data = empty_like_sample() if args.blank else build_sample()
    print("Workbook written to:", build_workbook(args.output, data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
