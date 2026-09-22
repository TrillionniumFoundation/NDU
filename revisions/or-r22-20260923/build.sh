#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
R=revisions/or-r22-20260923
export SOURCE_DATE_EPOCH=1790121600
python "$R/prepare.py"
: > main-labels.aux
: > ec-labels.aux
for pass in 1 2 3 4; do
  for target in main electronic_companion; do
    pdflatex -interaction=nonstopmode -halt-on-error "$target.tex" > "$R/results/build-$target.log"
    label=main; [ "$target" = electronic_companion ] && label=ec
    grep '^\\newlabel' "$target.aux" > "$label-labels.aux" || true
  done
done
if grep -E 'undefined references|Citation .* undefined|multiply defined|Overfull \\hbox|referenced but does not exist' main.log electronic_companion.log; then
  echo 'Unresolved reference, overfull text, or missing link target.' >&2; exit 1
fi
for target in main electronic_companion; do
  cp "$target.aux" "$R/results/tex-$target.aux"
  cp "$target.log" "$R/results/tex-$target.log"
done
# Retain the actual current inline author-year bibliography as a standalone file.
python - <<'PY'
from pathlib import Path
s=Path('main.tex').read_text();a=s.index('\\begin{thebibliography}');b=s.index('\\end{thebibliography}',a)+len('\\end{thebibliography}')
Path('main.bbl').write_text(s[a:b]+'\n')
PY
