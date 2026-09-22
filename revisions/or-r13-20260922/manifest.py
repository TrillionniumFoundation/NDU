#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[2];here=Path(__file__).resolve().parent
paths=[root/n for n in ['main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','historical_supplement.tex','historical_supplement.pdf','README.md']]
paths+=list(here.rglob('*'));records={}
for p in sorted(set(paths)):
    if not p.is_file() or '__pycache__' in p.parts or p.name=='manifest.json' or p.suffix in ('.log','.pyc'):continue
    data=p.read_bytes();records[str(p.relative_to(root))]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
(here/'results/manifest.json').write_text(json.dumps({'files':records,'algorithm':'sha256'},indent=2)+'\n')
print('manifest files',len(records))
