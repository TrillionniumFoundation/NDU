#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 revisions/or-r7-20260921/prepare_sources.py
export SOURCE_DATE_EPOCH=1790006400
# Only newlabel records are cross-imported, avoiding duplicate bibliographies.
for p in main ec history; do touch "$p-labels.aux"; done
for pass in 1 2 3; do
  for target in main electronic_companion historical_supplement; do
    pdflatex -interaction=nonstopmode -halt-on-error "$target.tex" > "/tmp/ndu-r10-$target-build.log"
    case "$target" in main) label=main;; electronic_companion) label=ec;; *) label=history;; esac
    grep '^\\newlabel' "$target.aux" > "$label-labels.aux" || true
  done
done
if grep -E 'undefined references|Citation .* undefined|multiply defined|Overfull \\hbox' main.log electronic_companion.log historical_supplement.log; then
  echo 'Unresolved references or overfull text: inspect logs' >&2;exit 1
fi
python3 revisions/or-r10-20260921/check_package.py --pdf
