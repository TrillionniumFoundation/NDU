#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python revisions/or-r14-20260922/structural_tests.py
python revisions/or-r14-20260922/study.py
python revisions/or-r14-20260922/validation.py
python revisions/or-r14-20260922/verify.py
python revisions/or-r14-20260922/tables.py
