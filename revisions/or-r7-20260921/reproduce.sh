#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python accepted_exact.py
python robustness.py
python interim_participation.py
python portfolio_learning.py
python enrich_portfolio.py
python inaction.py
NDU_TABLE_OUTPUT=results/replay_tables python make_tables.py
python verify.py
