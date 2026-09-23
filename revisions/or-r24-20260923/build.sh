#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
R=revisions/or-r24-20260923
export SOURCE_DATE_EPOCH=1790121600
mkdir -p "$R/results"
printf '\n' > main-labels.aux
printf '\n' > ec-labels.aux
printf '\n' > cs-labels.aux
for pass in 1 2 3 4; do
  for name in main electronic_companion computational_supplement; do
    pdflatex -interaction=nonstopmode -halt-on-error "$name.tex" > "$R/results/build-$name-pass$pass.log" 2>&1 || {
      tail -80 "$R/results/build-$name-pass$pass.log"; exit 1;
    }
    case "$name" in
      main) labels=main-labels.aux;;
      electronic_companion) labels=ec-labels.aux;;
      computational_supplement) labels=cs-labels.aux;;
    esac
    grep '^\\newlabel' "$name.aux" > "$labels" || true
  done
done
for name in main electronic_companion computational_supplement; do
  cp "$name.aux" "$R/results/tex-$name.aux"
  cp "$name.log" "$R/results/tex-$name.log"
done
python - <<'PY'
from pathlib import Path
text=Path('main.tex').read_text();a=text.index(r'\begin{thebibliography}');b=text.index(r'\end{thebibliography}',a)+len(r'\end{thebibliography}')
Path('main.bbl').write_text(text[a:b]+'\n')
PY
