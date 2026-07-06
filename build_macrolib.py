#!/usr/bin/env python3
"""Entry point: build the Macro Impact Library & Global Stress Index workbook."""

from __future__ import annotations

import argparse
import sys

from macrolib.data import build_sample, empty_like_sample
from macrolib.workbook import build_workbook


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build the Macro Impact Library & Global Stress Index workbook.")
    p.add_argument("-o", "--output", default="examples/Macro Impact Library & Stress Index.xlsx")
    p.add_argument("--blank", action="store_true", help="blank stress inputs (keeps the library)")
    args = p.parse_args(argv)
    data = empty_like_sample() if args.blank else build_sample()
    print("Workbook written to:", build_workbook(args.output, data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
