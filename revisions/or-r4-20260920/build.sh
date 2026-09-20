#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python revisions/or-r4-20260920/execute.py
python revisions/or-r4-20260920/make_tables.py
for name in main electronic_companion; do
  pdflatex -interaction=nonstopmode -halt-on-error "$name.tex"
  pdflatex -interaction=nonstopmode -halt-on-error "$name.tex"
done
