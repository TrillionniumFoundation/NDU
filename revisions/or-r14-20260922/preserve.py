#!/usr/bin/env python3
"""Snapshot immutable predecessor objects, never the already modified worktree."""
from pathlib import Path
import subprocess,hashlib,json
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
BASE='808b8f0353051581134d3b8b5a7424422d4e48a8'
subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT,check=True)
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
replace={'README.md','NDU_OR_submission_checklist.md','main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','historical_supplement.pdf'}
hashes={}
for name in paths:
 data=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
 hashes[name]=hashlib.sha256(data).hexdigest()
 if name in replace:
  p=HERE/'predecessor'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
(HERE/'BASELINE_SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('Immutable baseline:',len(paths),'files; exact root snapshots:',len(replace))
