#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
R=revisions/or-r30-quotient-memory-20260923
B=.build/ndu-r30
mkdir -p "$B" "$R/results"
# Build both documents repeatedly, isolating intermediates from inherited files.
for pass in 1 2 3 4; do
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory="$B" main.tex > "$B/main-pass-$pass.stdout"
  grep '^\\newlabel' "$B/main.aux" > r30-main-labels.aux || true
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory="$B" electronic_companion.tex > "$B/ec-pass-$pass.stdout"
  grep '^\\newlabel' "$B/electronic_companion.aux" > r30-ec-labels.aux || true
done
cp "$B/main.pdf" main.pdf
cp "$B/electronic_companion.pdf" electronic_companion.pdf
cp "$B/main.log" "$R/results/main-build.log"
cp "$B/electronic_companion.log" "$R/results/electronic-companion-build.log"
if grep -E 'undefined references|undefined citations|Citation .* undefined|Reference .* undefined|multiply defined|^!' "$B/main.log" "$B/electronic_companion.log"; then
  echo 'Cross-reference or LaTeX error remains.' >&2; exit 1
fi
pdfinfo main.pdf | head -18
pdfinfo electronic_companion.pdf | head -18
