#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
R=revisions/or-r22-20260923
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p "$R/results" "$R/tables"
python -u "$R/matched_cost.py" 2>&1 | tee "$R/results/matched.log"
python -u "$R/validation.py" 2>&1 | tee "$R/results/validation.log"
python -u "$R/scaling.py" 2>&1 | tee "$R/results/scaling.log"
python -S "$R/theory_checks.py"
python -S "$R/complete_dual_checks.py" 2>&1 | tee "$R/results/theory.log"
python -S "$R/replay.py" 2>&1 | tee "$R/results/replay.log"
python -S revisions/or-r19-20260923/replay.py --check 2>&1 | tee "$R/results/historical-replay.log"
python "$R/analyze.py" 2>&1 | tee "$R/results/analysis.log"
bash "$R/build.sh"
python "$R/check_package.py"
python "$R/package_metadata.py"
python "$R/check_package.py" --verify-manifest
