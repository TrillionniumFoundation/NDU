#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
R=revisions/or-r13-20260922
mkdir -p "$R/results"
# Separate immutable training, initial validation, and prospective confirmation.
python "$R/experiment.py" train --n 1024
for start in 0 1024 2048 3072; do python "$R/experiment.py" validate --n 4096 --start "$start" --count 1024; done
python "$R/experiment.py" report
python "$R/confirmatory.py" prepare
for start in 0 2048; do python "$R/confirmatory.py" run --start "$start" --count 2048; done
python "$R/confirmatory.py" summary
python "$R/structural.py" paths
python "$R/structural.py" scale
python "$R/mechanism.py"
python "$R/verify.py"
python "$R/make_tables.py"
