#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 revisions/or-r7-20260921/prepare_sources.py
export SOURCE_DATE_EPOCH=1789948800
for pass in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error main.tex > /tmp/ndu-r7-main-build.log
  grep '^\\newlabel' main.aux > main-labels.aux
  pdflatex -interaction=nonstopmode -halt-on-error electronic_companion.tex > /tmp/ndu-r7-ec-build.log
  grep '^\\newlabel' electronic_companion.aux > ec-labels.aux
done
if grep -E 'undefined references|Citation .* undefined|multiply defined' main.log electronic_companion.log; then
  echo 'Unresolved LaTeX references' >&2; exit 1
fi
