#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python revisions/or-r6-20260921/verify.py
for pass in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error main.tex > /tmp/ndu-r6-main-tex.log
done
# Import cross-document labels, not duplicate bibliography records. Compatible
# with both older and current xr packages used by TeX distributions.
python - <<'PY'
from pathlib import Path
Path('main-labels.aux').write_text(''.join(l+'\n' for l in Path('main.aux').read_text().splitlines() if l.startswith('\\newlabel')))
PY
for pass in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error electronic_companion.tex > /tmp/ndu-r6-ec-tex.log
done
python - <<'PY'
from pathlib import Path
for name in ('main','electronic_companion'):
    log=Path(name+'.log').read_text(errors='replace')
    bad=[l for l in log.splitlines() if 'Warning' in l or 'Overfull' in l]
    if bad: raise SystemExit(name+': '+'\n'.join(bad))
    assert Path(name+'.pdf').stat().st_size>10000
print('Both R6 manuscripts compile without warnings.')
PY
