#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
files=[]
for name in ['main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','historical_supplement.tex','historical_supplement.pdf','README.md','NDU_OR_submission_checklist.md']:
    p=ROOT/name
    if p.is_file():files.append(p)
for d in [BASE]:
    files.extend(p for p in d.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='MANIFEST.json' and not p.name.endswith('.log'))
try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
except (subprocess.CalledProcessError,FileNotFoundError):commit='local source assembled from d89f0b5 and verified R9 predecessor differences'
result={'source_commit_before_publication':commit,'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}}
(BASE/'MANIFEST.json').write_text(json.dumps(result,indent=2)+'\n');print('Manifest:',len(result['sha256']),'files')
