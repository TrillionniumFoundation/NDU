#!/usr/bin/env python3
"""Convenience wrapper for regenerating the NDU experiment tables/figures.

Usage from this directory or the submission root:
    python reproducibility/scripts/run_full_ndu_all.py --outdir ndu_reproduction_outputs

The full regeneration depends on numpy, pandas, matplotlib, and seaborn and can
be computationally nontrivial. The lightweight checker in
`reproducibility/check_ndu_reproducibility.py` validates the packaged outputs
without rerunning the optimizer.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import generate_ndu_experiments as gen


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', default='ndu_reproduction_outputs')
    args = parser.parse_args()
    gen.ROOT = Path(args.outdir).resolve()
    gen.ROOT.mkdir(parents=True, exist_ok=True)
    exp1, exp2, exp3, frontier = gen.run_all_experiments()
    print('EXP1')
    print(exp1.to_string(index=False))
    print('\nEXP2')
    print(exp2.to_string(index=False))
    print('\nEXP3')
    print(exp3.to_string(index=False))
    print(f'\nWrote outputs to {gen.ROOT}')


if __name__ == '__main__':
    main()
