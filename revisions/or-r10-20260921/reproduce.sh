#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
bash revisions/or-r7-20260921/reproduce.sh
python3 revisions/or-r10-20260921/nonlinear_control.py
python3 revisions/or-r10-20260921/cached_quadratic.py
python3 revisions/or-r10-20260921/verify.py
python3 revisions/or-r10-20260921/structural_checks.py
python3 revisions/or-r10-20260921/make_tables.py
python3 revisions/or-r10-20260921/operator_diagnostics.py

# Preserve this replay under R10, without staging changes to prior scientific directories.
python3 - <<'REPLAY'
from pathlib import Path
import shutil
r=Path('revisions/or-r10-20260921/replayed_r7')
if r.exists():shutil.rmtree(r)
shutil.copytree('revisions/or-r7-20260921/results',r)
REPLAY
