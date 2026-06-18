#!/usr/bin/env python3
"""
Command-line entry point for the Company Analysis Engine.

Examples
--------
    python build_model.py                       # build the sample workbook
    python build_model.py -o my_model.xlsx       # custom output path
    python build_model.py --blank -o template.xlsx   # empty data-entry template
    python build_model.py --json mydata.json -o out.xlsx   # build from your data

The blank template has the full structure with no figures, ready for an analyst
to paste in real data. The JSON form expects the same shape as
``dcf.sample_data.build_sample()`` (see README for the schema).
"""

from __future__ import annotations

import argparse
import json
import sys

from dcf.sample_data import build_sample, empty_like_sample
from dcf.workbook import build_workbook


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build the company-analysis Excel workbook.")
    p.add_argument("-o", "--output", default="examples/sample_company.xlsx",
                   help="output .xlsx path (default: examples/sample_company.xlsx)")
    grp = p.add_mutually_exclusive_group()
    grp.add_argument("--sample", action="store_true", help="use the bundled sample (default)")
    grp.add_argument("--blank", action="store_true", help="generate a blank input template")
    grp.add_argument("--json", metavar="FILE", help="build from a JSON dataset file")
    args = p.parse_args(argv)

    if args.blank:
        data = empty_like_sample()
    elif args.json:
        with open(args.json, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    else:
        data = build_sample()

    path = build_workbook(args.output, data)
    print(f"Workbook written to: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
