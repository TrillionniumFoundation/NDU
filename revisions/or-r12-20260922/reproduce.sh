#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python revisions/or-r12-20260922/structural_checks.py
python revisions/or-r12-20260922/experiment.py --mode new
python revisions/or-r12-20260922/experiment.py --mode old
python revisions/or-r12-20260922/experiment.py --mode fd
python revisions/or-r12-20260922/experiment.py --mode timing
python revisions/or-r12-20260922/experiment.py --mode summary
python revisions/or-r12-20260922/verify.py
python revisions/or-r12-20260922/make_tables.py
# Replay the predecessor's complete nonlinear and cached-quadratic certificates.
python revisions/or-r10-20260921/verify.py
