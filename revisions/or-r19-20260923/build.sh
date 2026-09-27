#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
R=revisions/or-r19-20260923
export SOURCE_DATE_EPOCH=1790121600
python "$R/prepare_manuscripts.py"
python "$R/flatten.py"
python "$R/legacy_labels.py"
: > main-labels.aux
: > ec-labels.aux
for pass in 1 2 3 4; do
 for target in main electronic_companion; do
  pdflatex -interaction=nonstopmode -halt-on-error "$target.tex" > "$R/results/build-$target.log"
  label=main; [ "$target" = electronic_companion ] && label=ec
  grep '^\\newlabel' "$target.aux" > "$label-labels.aux" || true
 done
done
if grep -E 'undefined references|Citation .* undefined|multiply defined|Overfull \\hbox' main.log electronic_companion.log; then
 echo 'Manuscript validation failed: unresolved references or overfull line.' >&2; exit 1
fi

for target in main electronic_companion; do
 cp "$target.aux" "$R/results/tex-$target.aux"
 cp "$target.log" "$R/results/tex-$target.log"
done
