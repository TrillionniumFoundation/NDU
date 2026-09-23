#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
R=revisions/or-r28-20260923
mkdir -p "$R/results"
for i in 1 2 3 4; do
 pdflatex -interaction=nonstopmode -halt-on-error main.tex > "$R/results/main-build-pass-$i.txt"
 grep '^\\newlabel' main.aux > r28-main-labels.aux
 pdflatex -interaction=nonstopmode -halt-on-error electronic_companion.tex > "$R/results/ec-build-pass-$i.txt"
 grep '^\\newlabel' electronic_companion.aux > r28-ec-labels.aux
done
cp main.log "$R/results/main-build.log"
cp electronic_companion.log "$R/results/ec-build.log"
