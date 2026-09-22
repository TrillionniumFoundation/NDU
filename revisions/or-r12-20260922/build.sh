#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export SOURCE_DATE_EPOCH=1790035200
# Every manuscript input is already an ordinary tracked source file.
for p in main ec history; do touch "$p-labels.aux"; done
for pass in 1 2 3; do
  for target in main electronic_companion historical_supplement; do
    pdflatex -interaction=nonstopmode -halt-on-error "$target.tex" > "/tmp/ndu-r12-$target-build.log"
    case "$target" in main) label=main;; electronic_companion) label=ec;; *) label=history;; esac
    grep '^\\newlabel' "$target.aux" > "$label-labels.aux" || true
  done
done
if grep -E 'undefined references|Citation .* undefined|multiply defined|Overfull \\hbox' main.log electronic_companion.log historical_supplement.log; then
  echo 'Unresolved cross-references or overfull lines remain.' >&2;exit 1
fi
python3 revisions/or-r12-20260922/check_package.py
