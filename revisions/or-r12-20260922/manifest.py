#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
files=[ROOT/'main.pdf',ROOT/'electronic_companion.pdf',ROOT/'historical_supplement.pdf',ROOT/'main.tex',ROOT/'electronic_companion.tex',ROOT/'historical_supplement.tex']
files+=list(HERE.rglob('*'))
out={}
for p in sorted(set(files)):
    if not p.is_file() or p.name=='manifest.json' or '__pycache__' in p.parts:continue
    data=p.read_bytes();out[str(p.relative_to(ROOT))]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
(HERE/'results/manifest.json').write_text(json.dumps({'files':out},indent=2))
print('Manifest covers',len(out),'files')
