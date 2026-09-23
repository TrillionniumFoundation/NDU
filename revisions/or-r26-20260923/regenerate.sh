#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
R=revisions/or-r26-20260923
for spec in '3 2' '4 4' '4 8' '4 16' '8 4' '16 4'; do
 read -r horizon subdivisions <<< "$spec"
 python "$R/envelope.py" --horizon "$horizon" --grid "$subdivisions"
done
python -S "$R/replay.py"
python -S "$R/analyze.py"
