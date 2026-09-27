#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
R=revisions/or-r29-price-state-20260923
mkdir -p "$R/results"
for i in 1 2 3; do
 pdflatex -interaction=nonstopmode -halt-on-error -jobname=r29_retained "$R/retained_evidence.tex" > "$R/results/retained-pass-$i.log"
done
grep '^\\newlabel{tab:' r29_retained.aux > r29-retained-labels.aux
cp r29_retained.pdf "$R/retained_evidence.pdf"
for i in 1 2 3 4; do
 pdflatex -interaction=nonstopmode -halt-on-error main.tex > "$R/results/main-pass-$i.log"
 grep '^\\newlabel' main.aux > r29-main-labels.aux
 pdflatex -interaction=nonstopmode -halt-on-error electronic_companion.tex > "$R/results/ec-pass-$i.log"
 grep '^\\newlabel' electronic_companion.aux > r29-ec-labels.aux
done
cp main.log "$R/results/main-build.log"
cp electronic_companion.log "$R/results/ec-build.log"
cp r29_retained.log "$R/results/retained-build.log"
