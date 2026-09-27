#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
R=revisions/or-r30-quotient-memory-20260923
B=.build/ndu-r30-response
mkdir -p "$B"
if [[ ${1:-} == --refresh-source ]]; then
  pandoc "$R/RESPONSE_TO_REFEREES.md" --standalone -f markdown -t latex \
    -V documentclass=article -V fontsize=11pt -V geometry:margin=1in \
    -V linestretch=1.15 -V fontfamily=newtx -V colorlinks=false \
    -o "$R/RESPONSE_TO_REFEREES.tex"
fi
for pass in 1 2; do
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$B" \
    "$R/RESPONSE_TO_REFEREES.tex" > "$B/pass-$pass.stdout"
done
cp "$B/RESPONSE_TO_REFEREES.pdf" "$R/RESPONSE_TO_REFEREES.pdf"
cp "$B/RESPONSE_TO_REFEREES.log" "$R/results/response-build.log"
